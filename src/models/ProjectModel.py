from .BaseDataModel import BaseDataModel
from .db_schemas import project
from .enums.DatabaseEnum import DatabaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client:object):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECTS_NAME.value]
        
    @classmethod
    async def create_instance(cls, db_client:object):
        instance=cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collection=await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_PROJECTS_NAME.value not in all_collection:
            self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECTS_NAME.value]
            indexes=project.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index.get("unique", False), background=True)


    async def create_project(self, project:project):
        result=await self.collection.insert_one(project.dict(by_alias=True,exclude_unset=True))
        project.id = str(result.inserted_id)
        return project

        
    async def get_project_or_create_one(self, project_id: str):

        record = await self.collection.find_one({
            "project_id": project_id
        })

        if record is None:
            Project = project(project_id=project_id)
            Project = await self.create_project(project=Project)

            return Project

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
