import gdown
import os
import asyncio
from bot.utils.progress import ProgressTracker

async def download_gdrive(url: str, output_path: str, progress_callback=None) -> str:
    """
    Download file from Google Drive using gdown.

    Args:
        url (str): Google Drive URL
        output_path (str): Directory to save the file
        progress_callback: Optional callback for progress updates

    Returns:
        str: Path to downloaded file
    """
    def _download():
        # gdown supports progress, but we'll wrap it
        output = os.path.join(output_path, 'gdrive_file')
        gdown.download(url, output, quiet=False)
        return output

    loop = asyncio.get_event_loop()
    filename = await loop.run_in_executor(None, _download)
    return filename