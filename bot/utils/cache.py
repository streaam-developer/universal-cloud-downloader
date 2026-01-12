
# A simple in-memory cache
# For a production environment, you might want to use a more persistent cache like Redis.
url_cache = {}

def get_from_cache(url: str):
    """
    Gets a file_id from the cache.

    Args:
        url: The URL to look up.

    Returns:
        The file_id if found, otherwise None.
    """
    return url_cache.get(url)

def add_to_cache(url: str, file_id: str):
    """
    Adds a file_id to the cache.

    Args:
        url: The URL to cache.
        file_id: The file_id of the uploaded file.
    """
    url_cache[url] = file_id

