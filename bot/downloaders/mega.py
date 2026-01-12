
import asyncio
import os
import time
from typing import Callable
from mega import Mega

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 2147483648))

async def download_from_mega(
    url: str,
    download_path: str,
    progress_callback: Callable,
    message
):
    """
    Downloads a file from a MEGA URL.

    Args:
        url: The MEGA URL to download from.
        download_path: The path to save the downloaded file.
        progress_callback: A function to call with progress updates.
        message: The Pyrogram message object.

    Returns:
        The path to the downloaded file, or None if the download fails.
    """
    try:
        mega = Mega()
        loop = asyncio.get_event_loop()
        
        m = await loop.run_in_executor(None, mega.login)
        
        # Get file info to check size
        public_file_info = await loop.run_in_executor(None, m.get_public_url_info, url)
        filesize = public_file_info.get('size')
        
        if filesize and filesize > MAX_FILE_SIZE:
            await message.edit_text(f"File size ({filesize / 1024 / 1024:.2f} MB) exceeds the maximum allowed size ({MAX_FILE_SIZE / 1024 / 1024:.2f} MB).")
            return None
            
        await message.edit_text("Downloading from MEGA...")

        file_path = await loop.run_in_executor(
            None,
            lambda: m.download_url(url, download_path)
        )
        
        return file_path
        
    except Exception as e:
        await message.edit_text(f"MEGA download failed: {e}")
        return None
