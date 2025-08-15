from typing import List
from pydantic_settings import BaseSettings,SettingsConfigDict

class settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    FILE_MAX_SIZE: int
    FILE_ALLOWED_EXTENSIONS:str
    FILE_DEFAULT_CHUNK_SIZE: int
    MONGODB_URL:str
    MONGODB_DATABASE:str

    class Config:
        env_file = ".env"
        
            
def get_settings():
    return settings()

