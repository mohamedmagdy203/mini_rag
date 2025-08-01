from fastapi import APIRouter,Depends,FastAPI
import os
from helper.config import get_settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def welcome(settings=Depends(get_settings)):
    
    app_name=settings.app_name
    app_version=settings.app_version
    return {
        "app_name":app_name,
        "app_version":app_version,
        }
    