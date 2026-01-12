
import aiohttp
import aiofiles
import os
import time
from typing import Callable

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 2147483648))

async def download_direct(
    url: str,
    download_path: str,
    progress_callback: Callable,
    message
):
    """
    Downloads a file from a direct URL.

    Args:
        url: The direct URL to download from.
        download_path: The path to save the downloaded file.
        progress_callback: A function to call with progress updates.
        message: The Pyrogram message object.

    Returns:
        The path to the downloaded file, or None if the download fails.
    """
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    await message.edit_text(f"HTTP Error: {response.status}")
                    return None

                total_size = int(response.headers.get('content-length', 0))
                if total_size > MAX_FILE_SIZE:
                    await message.edit_text(f"File size ({total_size / 1024 / 1024:.2f} MB) exceeds the maximum allowed size ({MAX_FILE_SIZE / 1024 / 1024:.2f} MB).")
                    return None
                
                # Get filename from headers or URL
                filename = response.headers.get('content-disposition', '').split('filename=')[-1]
                if not filename:
                    filename = os.path.basename(url.split('?')[0])
                if not filename:
                    filename = "downloaded_file"

                file_path = os.path.join(download_path, filename)
                
                downloaded_size = 0
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 1024): # 1MB chunks
                        await f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        await progress_callback(
                            downloaded_size,
                            total_size,
                            message,
                            "Downloading directly...",
                            start_time
                        )

                return file_path
    except Exception as e:
        await message.edit_text(f"Direct download failed: {e}")
        return None
