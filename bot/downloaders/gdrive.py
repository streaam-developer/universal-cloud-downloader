
import asyncio
import os
import gdown
import time

async def download_from_gdrive(
    url: str,
    download_path: str,
    message
):
    """
    Downloads a file from a Google Drive URL using gdown.

    Args:
        url: The Google Drive URL to download from.
        download_path: The path to save the downloaded file.
        message: The Pyrogram message object to update.

    Returns:
        The path to the downloaded file, or None if the download fails.
    """
    try:
        await message.edit_text("Downloading from Google Drive...")
        
        loop = asyncio.get_event_loop()
        output_path = await loop.run_in_executor(
            None, 
            lambda: gdown.download(url, quiet=False, fuzzy=True)
        )
        
        if output_path is None:
            return None
            
        # Move the file to the download_path
        final_path = os.path.join(download_path, os.path.basename(output_path))
        os.rename(output_path, final_path)
        
        return final_path
    except Exception as e:
        await message.edit_text(f"Google Drive download failed: {e}")
        return None

