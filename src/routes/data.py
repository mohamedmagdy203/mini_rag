from sys import prefix
import os
from fastapi import APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
from helper.config import settings,get_settings
from controllers import DataController
from controllers import ProjectControllers
import aiofiles
from models import ResponseSignal

data_router = APIRouter(prefix="/api/v1/data",tags=['api_v1','data'])


@data_router.post('/upload/{project_id}')
async def upload_data(project_id:str,file:UploadFile,
                    app_settings:settings=Depends(get_settings)):
    
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

    async with aiofiles.open(file_path, 'wb') as out_file:
        while chunk:=await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
            await out_file.write(chunk)
            
    return JSONResponse(
        content={
            'signal': ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            'file_id': file_id
        }
    )