
import time
import math
from pyrogram.types import Message

# A lock to prevent flooding message edits
EDIT_LOCK = {}

async def progress_for_pyrogram(
    current,
    total,
    message: Message,
    ud_type: str,
    start_time: float,
    eta: int = None,
    speed: float = None,
):
    """
    Updates a Telegram message with download or upload progress.
    """
    now = time.time()
    
    # Check if we should update
    if message.id in EDIT_LOCK and (now - EDIT_LOCK[message.id]) < 2:
        return
    EDIT_LOCK[message.id] = now

    diff = now - start_time
    if diff == 0:
        return

    prop = current / total
    percent = round(prop * 100, 2)
    bar_len = 20
    filled_len = round(bar_len * prop)
    bar = "■" * filled_len + "□" * (bar_len - filled_len)

    if speed is None:
        speed = current / diff
    
    if eta is None and speed > 0:
        eta_seconds = (total - current) / speed
    else:
        eta_seconds = eta if eta is not None else 0

    def format_bytes(size):
        if not size:
            return "0B"
        power = 1024
        t_labels = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size >= power and i < len(t_labels) - 1:
            size /= power
            i += 1
        return f"{size:.2f}{t_labels[i]}"

    eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds)) if eta_seconds > 0 else "N/A"

    if "upload" in ud_type.lower():
        text = (
            f"**{ud_type}**\n"
            f"`{bar}`\n"
            f"**Progress:** {percent}%\n"
            f"**Uploaded:** {format_bytes(current)} / {format_bytes(total)}\n"
            f"**Speed:** {format_bytes(speed)}/s\n"
            f"**ETA:** {eta_str}"
        )
    else: # Default to download
        text = (
            f"**{ud_type}**\n"
            f"`{bar}`\n"
            f"**Progress:** {percent}%\n"
            f"**Downloaded:** {format_bytes(current)} / {format_bytes(total)}\n"
            f"**Speed:** {format_bytes(speed)}/s\n"
            f"**ETA:** {eta_str}"
        )
        
    try:
        await message.edit_text(text)
    except Exception as e:
        print(f"Error updating progress: {e}")
        # If the message is deleted or something goes wrong, we should stop trying to edit it
        if message.id in EDIT_LOCK:
            del EDIT_LOCK[message.id]

