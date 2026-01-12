
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Get the database URI from environment variables
DATABASE_URI = os.getenv('DATABASE_URI')

# Initialize the MongoDB client
if DATABASE_URI:
    client = AsyncIOMotorClient(DATABASE_URI)

    # Get the database name from the URI, default to "UniversalDownloader"
    db_name = DATABASE_URI.split('/')[-1].split('?')[0] or "UniversalDownloader"
    db = client[db_name]

    # Create collections
    users_collection = db["users"]
    cache_collection = db["cache"]

    # Create indexes for faster queries
    async def create_indexes():
        await users_collection.create_index("user_id", unique=True)
        await cache_collection.create_index("url", unique=True)

else:
    # If no DATABASE_URI is provided, set db to None
    db = None
    users_collection = None
    cache_collection = None
    
    async def create_indexes():
        pass # No-op if no database
