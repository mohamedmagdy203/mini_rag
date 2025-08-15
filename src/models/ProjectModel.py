from .BaseDataModel import BaseDataModel
from .db_schemas import project
from .enums.DatabaseEnum import DatabaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client:object):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECTS_NAME.value]
        
    async def create_project(self,project:project):
        result=await self.collection.insert_one(project.dict(by_alias=True,exclude_unset=True))
        project._id=result.inserted_id

        return project

    async def get_project_or_create_one(self, project_id:str):
        record=await self.collection.find_one({"_id":project_id})
        if record is None:
            projects = project(project_id=project_id)
            projects = await self.create_project(project=projects)
            return projects

        return project(**record)

    async def get_all_projects(self,page:int=1,page_size:int=10):
        
        total_doc=await self.collection.count_documents({})
        
        total_pages=total_doc//page_size
        if total_doc % page_size>0:
            total_pages+=1

        cursor=self.collection.find().skip((page-1)*page_size).limit(page_size)
        projects=[]
        async for document in cursor:
            projects.append(project(**document))
        
        return projects, total_pages
