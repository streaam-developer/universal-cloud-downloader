
from bot.utils.database import cache_collection

async def get_from_cache(url: str):
    """
    Gets a file_id from the cache.

    Args:
        url: The URL to look up.

    Returns:
        The file_id if found, otherwise None.
    """
    if cache_collection is None:
        return None
        
    cached = await cache_collection.find_one({"url": url})
    if cached:
        return cached.get("file_id")
    return None

async def add_to_cache(url: str, file_id: str):
    """
    Adds a file_id to the cache.

    Args:
        url: The URL to cache.
        file_id: The file_id of the uploaded file.
    """
    if cache_collection is None:
        return

    await cache_collection.update_one(
        {"url": url},
        {"$set": {"file_id": file_id}},
        upsert=True
    )
