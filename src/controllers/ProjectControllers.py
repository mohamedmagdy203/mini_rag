import os
from .BaseController import BaseController
from helper.config import settings, get_settings
from models import ResponseSignal

class ProjectControllers(BaseController):
    def __init__(self):
        super().__init__()
    
    def get_project_path(self,project_id:str):
        project_dir=os.path.join(
            self.files_dir,
            project_id
        )
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir