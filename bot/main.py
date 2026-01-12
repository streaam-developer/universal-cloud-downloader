import asyncio
import os
import tempfile
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from bot.utils.host_detection import detect_host
from bot.downloaders import mega, yt_dlp, gdrive, direct
from bot.utils.progress import ProgressTracker
from bot.utils.limits import UserLimits
from bot.utils.cleaner import AutoCleaner
from bot.utils.cache import DownloadCache

# Load environment variables
load_dotenv()

# Configuration
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
TEMP_DIR = os.getenv('TEMP_DIR', './temp')
CACHE_DIR = os.getenv('CACHE_DIR', './cache')
MAX_DOWNLOADS_PER_HOUR = int(os.getenv('MAX_DOWNLOADS_PER_HOUR', 10))
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 1024))
MAX_CACHE_AGE_HOURS = int(os.getenv('MAX_CACHE_AGE_HOURS', 24))
MAX_DISK_USAGE_GB = int(os.getenv('MAX_DISK_USAGE_GB', 10))

app = Client("universal_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize utilities
user_limits = UserLimits(max_downloads_per_hour=MAX_DOWNLOADS_PER_HOUR, max_file_size_mb=MAX_FILE_SIZE_MB)
cleaner = AutoCleaner(TEMP_DIR, max_age_hours=MAX_CACHE_AGE_HOURS, max_disk_usage_gb=MAX_DISK_USAGE_GB)
cache = DownloadCache(CACHE_DIR, max_cache_age_hours=MAX_CACHE_AGE_HOURS)

# Job queue
download_queue = asyncio.Queue()

async def download_worker():
    while True:
        user_id, url, message = await download_queue.get()
        try:
            await process_download(user_id, url, message)
        except Exception as e:
            await message.reply(f"Error: {str(e)}")
        finally:
            download_queue.task_done()

async def process_download(user_id: int, url: str, message: Message):
    # Check cache
    cached_file = cache.is_cached(url)
    if cached_file:
        await message.reply("File already downloaded recently. Sending cached version.")
        await app.send_document(user_id, cached_file)
        return

    # Check limits
    if not user_limits.can_download(user_id):
        await message.reply("Download limit exceeded. Try again later.")
        return

    # Detect host
    host = detect_host(url)
    if host == "unknown":
        await message.reply("Unsupported host.")
        return

    # Create temp dir
    with tempfile.TemporaryDirectory(dir=TEMP_DIR) as temp_dir:
        progress_msg = await message.reply("Starting download...")

        def update_progress(text):
            asyncio.create_task(progress_msg.edit_text(text))

        # Select downloader
        if host == "mega":
            downloader = mega.download_mega
        elif host in ["terabox", "mediafire", "gofile", "pixeldrain", "mixdrop", "doodstream", "krakenfiles", "anonfiles", "fileio"]:
            downloader = yt_dlp.download_yt_dlp
        elif host == "gdrive":
            downloader = gdrive.download_gdrive
        elif host in ["dropbox", "onedrive"]:
            downloader = direct.download_direct
        else:
            downloader = yt_dlp.download_yt_dlp  # Fallback

        try:
            file_path = await downloader(url, temp_dir, progress_callback=None)  # Progress not implemented fully

            # Upload to Telegram
            await progress_msg.edit_text("Uploading to Telegram...")
            sent_msg = await app.send_document(user_id, file_path)

            # Cache
            cache.add_to_cache(url, file_path)

            # Record download
            user_limits.record_download(user_id)

            await progress_msg.edit_text("Download complete!")

        except Exception as e:
            await progress_msg.edit_text(f"Download failed: {str(e)}")

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("Welcome to Universal Cloud Downloader! Send me a link to download.")

@app.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = """
/start - Start the bot
/help - Show this help
/status - Show bot status
/queue - Show download queue
/cancel - Cancel current download
/limit - Show your limits
    """
    await message.reply(help_text)

@app.on_message(filters.command("status"))
async def status_command(client, message):
    queue_size = download_queue.qsize()
    await message.reply(f"Queue size: {queue_size}")

@app.on_message(filters.command("queue"))
async def queue_command(client, message):
    await message.reply(f"Current queue: {download_queue.qsize()} items")

@app.on_message(filters.command("limit"))
async def limit_command(client, message):
    user_id = message.from_user.id
    can_dl = user_limits.can_download(user_id)
    await message.reply(f"Can download: {can_dl}")

@app.on_message(filters.text)
async def handle_url(client, message):
    url = message.text.strip()
    if not url.startswith(('http://', 'https://')):
        return

    user_id = message.from_user.id
    await download_queue.put((user_id, url, message))
    await message.reply("Added to queue.")

async def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Start scheduler for cleanup
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleaner.run_cleanup, 'interval', hours=1)
    scheduler.start()

    # Start the bot
    await app.start()

    # Start download worker
    asyncio.create_task(download_worker())

    # Wait until the bot is stopped
    await idle()

    # Stop the bot and scheduler
    await app.stop()
    scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())