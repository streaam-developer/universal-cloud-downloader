
import os
import time
import asyncio
import logging

logger = logging.getLogger(__name__)

async def periodic_cleaner(path, interval, max_age):
    """
    Periodically cleans a directory of old files.

    Args:
        path: The directory to clean.
        interval: The interval in seconds between cleanups.
        max_age: The maximum age of a file in seconds before it is deleted.
    """
    while True:
        try:
            logger.info(f"Running cleaner on {path}...")
            now = time.time()
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > max_age:
                        os.remove(file_path)
                        logger.info(f"Removed old file: {file_path}")
        except Exception as e:
            logger.error(f"Error in cleaner: {e}")
            
        await asyncio.sleep(interval)
