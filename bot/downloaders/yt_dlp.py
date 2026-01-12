import yt_dlp
import os
import asyncio
from bot.utils.progress import ProgressTracker

async def download_yt_dlp(url: str, output_path: str, progress_callback=None) -> str:
    """
    Download file using yt-dlp.

    Args:
        url (str): URL to download
        output_path (str): Directory to save the file
        progress_callback: Optional callback for progress updates

    Returns:
        str: Path to downloaded file
    """
    def progress_hook(d):
        if d['status'] == 'downloading':
            if progress_callback:
                total = d.get('total_bytes', 0)
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                progress_callback(downloaded, total, speed, eta)

    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
    }

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename

    loop = asyncio.get_event_loop()
    filename = await loop.run_in_executor(None, _download)
    return filename