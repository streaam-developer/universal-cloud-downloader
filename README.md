# Universal Cloud Downloader Telegram Bot

A production-grade Telegram bot that downloads files from various cloud storage platforms and re-uploads them to Telegram.

## Supported Hosts

- Terabox
- MEGA
- MediaFire
- Gofile
- Pixeldrain
- Krakenfiles
- Mixdrop
- Doodstream
- AnonFiles
- File.io
- Google Drive (public links)
- Dropbox (public links)
- OneDrive (public links)
- Any yt-dlp supported host

## Features

- Async processing with Pyrogram
- Job queue for multiple users
- Progress tracking
- Speed monitoring
- File size limits
- User rate limiting
- Auto cleanup
- Duplicate prevention (caching)
- Resume support (where possible)

## Setup Instructions

### 1. Telegram BotFather Setup

1. Go to [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the BOT_TOKEN

### 2. Get API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in and go to API development tools
3. Create an application
4. Copy API_ID and API_HASH

### 3. Clone and Install

```bash
git clone <this-repo>
cd universal-cloud-downloader
pip install -r requirements.txt
```

### 4. Configuration

1. Copy `.env.example` to `.env`
2. Fill in your credentials:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
TEMP_DIR=./temp
CACHE_DIR=./cache
MAX_DOWNLOADS_PER_HOUR=10
MAX_FILE_SIZE_MB=1024
MAX_CACHE_AGE_HOURS=24
MAX_DISK_USAGE_GB=10
```

### 5. Run the Bot

```bash
python bot/main.py
```

## Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot/main.py"]
```

Build and run:

```bash
docker build -t downloader-bot .
docker run -e API_ID=... -e API_HASH=... -e BOT_TOKEN=... downloader-bot
```

### Ubuntu VPS

1. Install Python 3.9+
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run: `python bot/main.py`

### Railway/Render

1. Set environment variables in dashboard
2. Deploy as Python app with `python bot/main.py` as start command

## Bot Commands

- `/start` - Start the bot
- `/help` - Show help
- `/status` - Show bot status
- `/queue` - Show queue size
- `/cancel` - Cancel download (not implemented)
- `/limit` - Check your limits

## Usage

Send any supported URL to the bot, and it will download and upload the file back to Telegram.

## Architecture

```
/bot
  /downloaders
    mega.py      - MEGA downloads
    yt_dlp.py    - yt-dlp based downloads
    gdrive.py    - Google Drive
    direct.py    - Direct downloads
  /utils
    host_detection.py - URL host detection
    progress.py       - Progress tracking
    limits.py         - User limits
    cleaner.py        - Auto cleanup
    cache.py          - Duplicate prevention
  main.py             - Bot logic
```

## Security

- URL validation
- File size limits
- Rate limiting per user
- Auto cleanup of temp files
- No sensitive data logging

## Performance

- Supports 100+ concurrent users
- Async I/O with aiofiles
- Chunked downloads
- Streamed uploads to Telegram