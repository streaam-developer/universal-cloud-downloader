
import os
import time
from collections import defaultdict

# In-memory storage for user limits.
# For a production environment, consider a more persistent storage like Redis.
user_usage = defaultdict(lambda: {"count": 0, "bytes": 0, "timestamp": time.time()})

# Get limits from environment variables
DAILY_DOWNLOAD_LIMIT = int(os.getenv("DAILY_DOWNLOAD_LIMIT", 10))
DAILY_BYTE_LIMIT = int(os.getenv("DAILY_BYTE_LIMIT", 5 * 1024 * 1024 * 1024)) # 5GB

def check_limits(user_id: int) -> (bool, str):
    """
    Checks if a user has exceeded their daily download limits.

    Args:
        user_id: The ID of the user to check.

    Returns:
        A tuple of (can_download, reason).
    """
    now = time.time()
    usage = user_usage[user_id]

    # Reset usage if it's a new day
    if now - usage["timestamp"] > 86400: # 24 hours
        usage["count"] = 0
        usage["bytes"] = 0
        usage["timestamp"] = now

    if usage["count"] >= DAILY_DOWNLOAD_LIMIT:
        return False, "You have reached your daily download limit."
    
    if usage["bytes"] >= DAILY_BYTE_LIMIT:
        return False, "You have reached your daily data usage limit."

    return True, ""

def update_usage(user_id: int, downloaded_bytes: int):
    """
    Updates a user's download usage.

    Args:
        user_id: The ID of the user.
        downloaded_bytes: The number of bytes downloaded.
    """
    user_usage[user_id]["count"] += 1
    user_usage[user_id]["bytes"] += downloaded_bytes
