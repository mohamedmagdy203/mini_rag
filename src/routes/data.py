from sys import prefix
import os
from fastapi import APIRouter,Depends,UploadFile,status,Request,requests
from fastapi.responses import JSONResponse
from helper.config import settings,get_settings
from controllers import DataController,ProcessController,ProjectControllers
import aiofiles
from models import ResponseSignal
from models.db_schemas.data_chunk import DataChunk
from models.db_schemas.asset import Asset
from .schemas.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnums import AssetTypeEnums
from bson import ObjectId

data_router = APIRouter(prefix="/api/v1/data",tags=['api_v1','data'])


@data_router.post('/upload/{project_id}')
async def upload_data(request:Request,project_id:str,file:UploadFile,
                    app_settings:settings=Depends(get_settings)):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project=await project_model.get_project_or_create_one(project_id=project_id)

    data_controller = DataController()
    is_valid,result_signal = data_controller.validate_upload_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": result_signal}
        )
    
    project_dir_path = ProjectControllers().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_filename=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk:=await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(chunk)

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": ResponseSignal.FILE_UPLOAD_FAILED.value, "details": str(e)}
        )
        
    # store the assets into the database
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    asset_resource=Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnums.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )
    
    asset_record=await asset_model.create_asset(asset=asset_resource)
    

    return JSONResponse(
        content={
            'signal': ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            'file_id': str(asset_record.id),
            'project_id': str(project.id),
        }
    )
    
    
@data_router.post('/process/{project_id}')
async def process_endpoint(requests: Request, project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    file_chunk_size = process_request.chunk_size
    file_chunk_overlap = process_request.chunk_overlap
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client=requests.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=file_chunk_size,
        chunk_overlap=file_chunk_overlap
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'signal': ResponseSignal.PROCESSING_FAILED.value}
        )

    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = await ChunkModel.create_instance(db_client=requests.app.db_client)

    if do_reset:
        await chunk_model.delete_chunk_by_project_id(project_id=project.id)

    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
            'signal': ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            'file_id': file_id,
            'project_id': str(project.id),
        }
    )
