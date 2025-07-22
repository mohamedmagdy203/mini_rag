from fastapi import APIRouter
import os
router = APIRouter()

@router.get("/users")
async def get_users():
    app_name=os.getenv('APP_NAME')
    app_version=os.getenv('APP_VERSION')
    return ["user1", "user2",app_name,app_version]
