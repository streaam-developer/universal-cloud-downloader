import aiohttp
import aiofiles
import os
import asyncio
from bot.utils.progress import ProgressTracker

async def download_direct(url: str, output_path: str, progress_callback=None) -> str:
    """
    Download file directly using aiohttp.

    Args:
        url (str): Direct URL
        output_path (str): Directory to save the file
        progress_callback: Optional callback for progress updates

    Returns:
        str: Path to downloaded file
    """
    filename = os.path.basename(url.split('?')[0]) or 'downloaded_file'
    filepath = os.path.join(output_path, filename)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError(f"Failed to download: {response.status}")

            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0

            async with aiofiles.open(filepath, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size, 0, 0)  # Speed and ETA not calculated here

    return filepath