
import asyncio
import os
import time
from typing import Callable
import yt_dlp

from bot.utils.progress import progress_for_pyrogram

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 2147483648))

async def download_from_yt_dlp(
    url: str,
    download_path: str,
    progress_callback: Callable,
    message
):
    """
    Downloads a file from a URL using yt-dlp.

    Args:
        url: The URL to download from.
        download_path: The path to save the downloaded file.
        progress_callback: A function to call with progress updates.
        message: The Pyrogram message object.

    Returns:
        The path to the downloaded file, or None if the download fails.
    """
    start_time = time.time()

    class YtdlLogger:
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    async def progress_hook(d):
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total_bytes:
                downloaded_bytes = d.get("downloaded_bytes")
                speed = d.get("speed")
                eta = d.get("eta")
                
                await progress_callback(
                    downloaded_bytes,
                    total_bytes,
                    message,
                    "Downloading...",
                    start_time,
                    eta,
                    speed
                )

    ydl_opts = {
        "format": "best",
        "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
        "logger": YtdlLogger(),
        "progress_hooks": [progress_hook],
        "nocheckcertificate": True,
        "max_downloads": 1,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            loop = asyncio.get_event_loop()
            
            # First, extract info without downloading
            info_dict = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            
            filesize = info_dict.get('filesize') or info_dict.get('filesize_approx')
            if filesize and filesize > MAX_FILE_SIZE:
                await message.edit_text(f"File size ({filesize / 1024 / 1024:.2f} MB) exceeds the maximum allowed size ({MAX_FILE_SIZE / 1024 / 1024:.2f} MB).")
                return None
            
            # Now, download the file
            await loop.run_in_executor(None, lambda: ydl.download([url]))
            return ydl.prepare_filename(info_dict)
            
    except Exception as e:
        await message.edit_text(f"yt-dlp download failed: {e}")
        return None

