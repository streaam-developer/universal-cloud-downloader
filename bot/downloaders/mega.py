import asyncio
import os
from mega import Mega
from bot.utils.progress import ProgressTracker

async def download_mega(url: str, output_path: str, progress_callback=None) -> str:
    """
    Download file from MEGA using mega.py.

    Args:
        url (str): MEGA URL
        output_path (str): Path to save the file
        progress_callback: Optional callback for progress updates

    Returns:
        str: Path to downloaded file
    """
    def _download():
        mega = Mega()
        m = mega.login()  # Anonymous login
        file = m.find(url)
        if not file:
            raise ValueError("File not found or invalid URL")
        m.download(file, output_path)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _download)
    return output_path