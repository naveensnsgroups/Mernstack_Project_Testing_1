import motor.motor_asyncio
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class Database:
    client: motor.motor_asyncio.AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_db():
    if not settings.mongo_uri:
        logger.error("MONGO_URI is not defined in environment variables.")
        raise RuntimeError("MONGO_URI is not defined")
    try:
        db_instance.client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
        # Extract database name from URI or default to 'HR' or 'personal_details_db'
        # In Mongoose model, collection is explicitly 'HR'. Let's use database from URI and collection 'HR'.
        # Note: Mongoose model('Employee', schema, 'HR') uses collection 'HR'.
        # In motor, db['HR'] or db.HR.
        # Let's check how db name is parsed or if we can use client.get_default_database() or parse from URI.
        # Usually URI has db name at the end e.g. ...mongodb.net/personal_details_db?...
        parsed_db_name = "personal_details_db"
        if "?" in settings.mongo_uri:
            base_part = settings.mongo_uri.split("?")[0]
        else:
            base_part = settings.mongo_uri
        parts = base_part.split("/")
        if len(parts) > 3 and parts[-1]:
            parsed_db_name = parts[-1]
            
        db_instance.db = db_instance.client[parsed_db_name]
        # Ping to test connection
        await db_instance.client.admin.command('ping')
        logger.info(f"MongoDB Connected successfully to database: {parsed_db_name}")
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {e}")
        raise e

async def close_db():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    return db_instance.db
