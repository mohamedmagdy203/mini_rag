from fastapi import FastAPI
from dotenv import load_dotenv
import os
load_dotenv()


from routes import base,items

app=FastAPI()

app.include_router(base.router)
app.include_router(items.router)