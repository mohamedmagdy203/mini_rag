from .BaseController import BaseController
from models import ResponseSignal
from fastapi import UploadFile
import random
import string
from .ProjectControllers import ProjectControllers
import re
import os

class DataController(BaseController):

    def __init__(self) -> None:
        super().__init__()
        self.size_scale=1048576
        
    def validate_upload_file(self,file:UploadFile):
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False,ResponseSignal.FILE_SIZE_EXCEEDED.value
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False,ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        return True,ResponseSignal.FILE_VALIDATED_SUCCESS.value
    
    def generate_unique_filepath(self,orig_filename:str,project_id:str):
        random_key=self.generate_random_string()
        project_path=ProjectControllers().get_project_path(project_id=project_id)

        cleaned_file_name=self.get_clean_file_name(
            orig_filename=orig_filename
            )
        
        new_file_path=os.path.join(
            project_path,
            random_key + '_' + cleaned_file_name
        )
        while os.path.exists(new_file_path):
            random_key=self.generate_random_string()
            new_file_path=os.path.join(
                project_path,
                random_key + '_' + cleaned_file_name
            )
        return new_file_path,random_key + "_" +cleaned_file_name

    def get_clean_file_name(self,orig_filename:str):

        cleaned_file_name=re.sub(r'[^\w.]', '', orig_filename.strip())
        cleaned_file_name=cleaned_file_name.replace(' ', '_')
        return cleaned_file_name
