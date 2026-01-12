
import asyncio
import os
import logging
import time
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.utils.host_utils import detect_host
from bot.utils.url_utils import is_valid_url
from bot.downloaders.yt_dlp import download_from_yt_dlp
from bot.downloaders.gdrive import download_from_gdrive
from bot.downloaders.mega import download_from_mega
from bot.downloaders.direct import download_direct
from bot.utils.progress import progress_for_pyrogram
from bot.utils.limits import check_limits, update_usage, user_usage, DAILY_DOWNLOAD_LIMIT, DAILY_BYTE_LIMIT
from bot.utils.cache import get_from_cache, add_to_cache
from bot.utils.cleaner import periodic_cleaner

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "downloads")
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", 2))
CLEANER_INTERVAL = int(os.getenv("CLEANER_INTERVAL", 3600))
MAX_FILE_AGE = int(os.getenv("MAX_FILE_AGE", 86400))

# Create the download directory if it doesn't exist
if not os.path.isdir(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Initialize Pyrogram client
app = Client(
    "UniversalCloudDownloader",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Job queue
download_queue = asyncio.Queue()
ACTIVE_DOWNLOADS = {}
DOWNLOAD_TASKS = {}

async def worker(name):
    """A worker that processes downloads from the queue."""
    while True:
        job = await download_queue.get()
        chat_id, message_id, url = job
        
        task = asyncio.current_task()
        DOWNLOAD_TASKS[(chat_id, message_id)] = task

        try:
            message = await app.get_messages(chat_id, message_id)
            user_id = message.from_user.id
            
            # Add to active downloads
            ACTIVE_DOWNLOADS[(chat_id, message_id)] = url
            
            # Check user limits
            can_download, reason = check_limits(user_id)
            if not can_download:
                await message.reply_text(reason, quote=True)
                continue

            status_message = await message.reply_text("Processing...", quote=True)
            
            # Check cache
            cached_file_id = get_from_cache(url)
            if cached_file_id:
                await status_message.edit_text("File found in cache. Sending directly...")
                await app.send_document(chat_id, cached_file_id)
                await status_message.delete()
                continue

            host = detect_host(url)
            
            file_path = None
            if host == "yt-dlp" or host in ["terabox", "mediafire", "pixeldrain", "mixdrop", "doodstream"]:
                file_path = await download_from_yt_dlp(
                    url, DOWNLOAD_PATH, progress_for_pyrogram, status_message
                )
            elif host == "gdrive":
                file_path = await download_from_gdrive(
                    url, DOWNLOAD_PATH, status_message
                )
            elif host == "mega":
                file_path = await download_from_mega(
                    url, DOWNLOAD_PATH, progress_for_pyrogram, status_message
                )
            elif host == "direct":
                file_path = await download_direct(
                    url, DOWNLOAD_PATH, progress_for_pyrogram, status_message
                )
            else:
                await status_message.edit_text(f"Unsupported host: {host}")
                continue
                
            if file_path:
                downloaded_bytes = os.path.getsize(file_path)
                await status_message.edit_text("Uploading...")
                start_time = time.time()
                sent_message = await app.send_document(
                    chat_id,
                    file_path,
                    caption=os.path.basename(file_path),
                    progress=progress_for_pyrogram,
                    progress_args=(
                        status_message,
                        "Uploading...",
                        start_time
                    )
                )
                # Add to cache
                if sent_message.document:
                    add_to_cache(url, sent_message.document.file_id)
                
                # Update user usage
                update_usage(user_id, downloaded_bytes)
                    
                await status_message.delete()
                os.remove(file_path)
            else:
                await status_message.edit_text("Failed to download the file.")
        
        except asyncio.CancelledError:
            await message.reply_text("Download cancelled.", quote=True)
        
        finally:
            # Remove from active downloads and tasks
            if (chat_id, message_id) in ACTIVE_DOWNLOADS:
                del ACTIVE_DOWNLOADS[(chat_id, message_id)]
            if (chat_id, message_id) in DOWNLOAD_TASKS:
                del DOWNLOAD_TASKS[(chat_id, message_id)]
            download_queue.task_done()

@app.on_message(filters.command("cancel"))
async def cancel_command(client: Client, message: Message):
    """Handler for the /cancel command."""
    if message.reply_to_message:
        chat_id = message.chat.id
        message_id = message.reply_to_message.id
        
        task_to_cancel = DOWNLOAD_TASKS.get((chat_id, message_id))
        if task_to_cancel:
            task_to_cancel.cancel()
            await message.reply_text("Cancellation request sent.")
        else:
            await message.reply_text("Could not find a download to cancel for this message.")
    else:
        await message.reply_text("Please reply to the message with the download link to cancel it.")

@app.on_message(filters.command("status"))
async def status_command(client: Client, message: Message):
    """Handler for the /status command."""
    user_id = message.from_user.id
    active_user_downloads = 0
    for (chat_id, _), _ in ACTIVE_DOWNLOADS.items():
        if chat_id == user_id:
            active_user_downloads += 1
    
    await message.reply_text(f"You have {active_user_downloads} active downloads.")

@app.on_message(filters.command("queue"))
async def queue_command(client: Client, message: Message):
    """Handler for the /queue command."""
    await message.reply_text(f"There are {download_queue.qsize()} items in the queue.")

@app.on_message(filters.command("limit"))
async def limit_command(client: Client, message: Message):
    """Handler for the /limit command."""
    user_id = message.from_user.id
    usage = user_usage[user_id]
    
    # Reset usage if it's a new day
    now = time.time()
    if now - usage["timestamp"] > 86400: # 24 hours
        usage["count"] = 0
        usage["bytes"] = 0
        usage["timestamp"] = now

    def format_bytes(size):
        if not size:
            return "0B"
        power = 1024
        t_labels = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size > power and i < len(t_labels) - 1:
            size /= power
            i += 1
        return f"{size:.2f}{t_labels[i]}"

    limit_message = (
        "**Your Daily Usage**\n\n"
        f"**Downloads:** {usage['count']} / {DAILY_DOWNLOAD_LIMIT}\n"
        f"**Data Usage:** {format_bytes(usage['bytes'])} / {format_bytes(DAILY_BYTE_LIMIT)}"
    )
    await message.reply_text(limit_message)

@app.on_message(filters.text & ~filters.command(["start", "help", "status", "queue", "cancel", "limit"]))
async def message_handler(client: Client, message: Message):
    """Handler for general text messages."""
    if is_valid_url(message.text):
        job = (message.chat.id, message.id, message.text)
        await download_queue.put(job)
        await message.reply_text("Your download has been added to the queue.", quote=True)
    else:
        await message.reply_text("Please send me a valid link.")

async def main():
    """Main function to start the bot and workers."""
    # Create worker tasks
    tasks = []
    for i in range(MAX_CONCURRENT_DOWNLOADS):
        task = asyncio.create_task(worker(f"worker-{i}"))
        tasks.append(task)

    # Create and start the cleaner task
    cleaner_task = asyncio.create_task(periodic_cleaner(DOWNLOAD_PATH, CLEANER_INTERVAL, MAX_FILE_AGE))
    tasks.append(cleaner_task)
    
    logger.info(f"Starting {len(tasks)} background tasks...")
    
    # Start the bot
    await app.start()
    logger.info("Bot started.")
    
    # Wait for the bot to stop
    await asyncio.Event().wait()
    
    # Stop the background tasks
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    logger.info("Starting bot...")
    asyncio.run(main())
    logger.info("Bot stopped.")
