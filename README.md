# Universal Cloud Downloader Telegram Bot

This is a powerful, production-grade Telegram bot that can download files from a wide variety of hosting platforms and upload them directly to Telegram.

## Features

- **Wide Range of Supported Hosts**: Download from Terabox, MEGA, MediaFire, Google Drive, and many more.
- **Concurrent Downloads**: A job queue system allows for parallel processing of multiple downloads.
- **Real-time Progress**: Get live updates on download and upload progress right in your Telegram chat.
- **File Size Limits**: Protects against abuse by enforcing a maximum file size for downloads.
- **Per-User Limits**: Set daily limits on the number of downloads and total data usage for each user.
- **Caching**: Avoids re-downloading the same file by caching previously uploaded files.
- **Automatic Cleanup**: A periodic cleaner removes old files from the download directory to save disk space.
- **Docker Support**: Comes with a multi-stage `Dockerfile` for easy deployment.
- **And much more**: Including error handling, flood protection, and a clean, modular architecture.

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

## Bot Commands

- `/start`: Show the welcome message.
- `/help`: Show the help message.
- `/status`: Check the status of your active downloads.
- `/queue`: View the number of items in the download queue.
- `/cancel`: Cancel an ongoing download by replying to the original message.
- `/limit`: View your current usage and limits.

## Setup and Deployment

### 1. Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started) (for Docker deployment)
- A Telegram account

### 2. Get Telegram API Credentials

1.  Go to [my.telegram.org](https://my.telegram.org) and log in with your Telegram account.
2.  Click on "API development tools" and create a new application.
3.  You will get your `API_ID` and `API_HASH`.

### 3. Create a Telegram Bot

1.  Open Telegram and search for the [@BotFather](https://t.me/BotFather).
2.  Send the `/newbot` command and follow the instructions to create a new bot.
3.  You will get your `BOT_TOKEN`.

### 4. Configuration

1.  Clone this repository:
    ```bash
    git clone https://github.com/your-repo/universal-cloud-downloader.git
    cd universal-cloud-downloader
    ```
2.  Create a `.env` file by copying the `.env.example`:
    ```bash
    cp .env.example .env
    ```
3.  Edit the `.env` file and fill in your credentials and desired settings:
    ```
    # Telegram API credentials
    API_ID=YOUR_API_ID
    API_HASH=YOUR_API_HASH
    BOT_TOKEN=YOUR_BOT_TOKEN

    # Bot settings
    DOWNLOAD_PATH=./downloads
    MAX_FILE_SIZE=2147483648 # 2GB in bytes
    MAX_CONCURRENT_DOWNLOADS=2
    USER_SESSION_STRING=

    # Cleaner settings
    CLEANER_INTERVAL=3600 # 1 hour
    MAX_FILE_AGE=86400 # 24 hours

    # User limits
    DAILY_DOWNLOAD_LIMIT=10
    DAILY_BYTE_LIMIT=5368709120 # 5GB
    ```

### 5. Running the Bot

#### Without Docker

1.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the bot:
    ```bash
    python -m bot.main
    ```

#### With Docker

1.  Build the Docker image:
    ```bash
    docker build -t universal-cloud-downloader .
    ```
2.  Run the bot in a Docker container:
    ```bash
    docker run -d --name ucd-bot \
        -v $(pwd)/downloads:/app/downloads \
        --env-file .env \
        universal-cloud-downloader
    ```

## Deployment on Railway, Render, etc.

You can easily deploy this bot on platforms like [Railway](https://railway.app/) or [Render](https://render.com/) using the provided `Dockerfile`.

1.  Fork this repository to your GitHub account.
2.  Create a new project on your hosting platform and connect it to your forked repository.
3.  Set the environment variables in your hosting platform's dashboard based on the `.env.example` file.
4.  The platform should automatically build and deploy the bot from the `Dockerfile`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.
