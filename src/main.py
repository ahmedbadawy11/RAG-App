from fastapi import FastAPI
from routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import settings,get_settings

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_conn = AsyncIOMotorClient(get_settings().MONGODB_URL)
    app.db_client = app.mongodb_conn[get_settings().MONGODB_DATABASE]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_conn.close()
    print("Disconnected from the MongoDB database!")

app.include_router(base.base_router)
app.include_router(data.data_router)
