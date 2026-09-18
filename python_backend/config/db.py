import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_db():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI is not defined in environment variables.", file=sys.stderr)
        sys.exit(1)

    try:
        db_instance.client = AsyncIOMotorClient(mongo_uri)
        db_name = mongo_uri.split("/")[-1].split("?")[0] or "personal_details_db"
        db_instance.db = db_instance.client[db_name]
        
        await db_instance.client.admin.command('ping')
        print(f"MongoDB Atlas Connected: {db_instance.client.address}")
    except Exception as error:
        print(f"MongoDB Connection Error: {error}", file=sys.stderr)
        sys.exit(1)

async def close_db():
    if db_instance.client:
        db_instance.client.close()
        print("MongoDB connection closed.")

def get_db():
    return db_instance.db
