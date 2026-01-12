
import os
import time
from datetime import datetime, date
from bot.utils.database import users_collection

# Get limits from environment variables
DAILY_DOWNLOAD_LIMIT = int(os.getenv("DAILY_DOWNLOAD_LIMIT", 10))
DAILY_BYTE_LIMIT = int(os.getenv("DAILY_BYTE_LIMIT", 5 * 1024 * 1024 * 1024)) # 5GB

async def check_limits(user_id: int) -> (bool, str):
    """
    Checks if a user has exceeded their daily download limits.

    Args:
        user_id: The ID of the user to check.

    Returns:
        A tuple of (can_download, reason).
    """
    if users_collection is None:
        return True, "" # No limits if no database

    today = date.today().isoformat()
    
    usage = await users_collection.find_one({"user_id": user_id})

    if not usage:
        return True, ""

    # Reset usage if it's a new day
    if usage.get("date") != today:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"count": 0, "bytes": 0, "date": today}}
        )
        usage["count"] = 0
        usage["bytes"] = 0

    if usage["count"] >= DAILY_DOWNLOAD_LIMIT:
        return False, "You have reached your daily download limit."
    
    if usage["bytes"] >= DAILY_BYTE_LIMIT:
        return False, "You have reached your daily data usage limit."

    return True, ""

async def update_usage(user_id: int, downloaded_bytes: int):
    """
    Updates a user's download usage.

    Args:
        user_id: The ID of the user.
        downloaded_bytes: The number of bytes downloaded.
    """
    if users_collection is None:
        return

    today = date.today().isoformat()

    await users_collection.update_one(
        {"user_id": user_id},
        {
            "$inc": {"count": 1, "bytes": downloaded_bytes},
            "$set": {"date": today}
        },
        upsert=True
    )

async def get_user_usage(user_id: int):
    """
    Gets a user's current usage.
    """
    if users_collection is None:
        return {"count": 0, "bytes": 0}

    today = date.today().isoformat()
    usage = await users_collection.find_one({"user_id": user_id})

    if not usage or usage.get("date") != today:
        return {"count": 0, "bytes": 0}
        
    return usage
