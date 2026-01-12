
from urllib.parse import urlparse

def detect_host(url: str) -> str:
    """
    Detects the hosting platform from a given URL.

    Args:
        url: The URL to inspect.

    Returns:
        A string representing the detected host, or "unknown".
    """
    if not url:
        return "unknown"

    hostname = urlparse(url).hostname
    if not hostname:
        return "unknown"

    hostname = hostname.lower()

    if "mega.nz" in hostname or "mega.io" in hostname:
        return "mega"
    if "terabox.com" in hostname or "teraboxapp.com" in hostname:
        return "terabox"
    if "mediafire.com" in hostname:
        return "mediafire"
    if "gofile.io" in hostname:
        return "gofile"
    if "pixeldrain.com" in hostname:
        return "pixeldrain"
    if "krakenfiles.com" in hostname:
        return "krakenfiles"
    if "mixdrop.co" in hostname or "mixdrop.to" in hostname:
        return "mixdrop"
    if "doodstream.com" in hostname or "dood.watch" in hostname:
        return "doodstream"
    if "anonfiles.com" in hostname:
        return "anonfiles"
    if "file.io" in hostname:
        return "fileio"
    if "drive.google.com" in hostname:
        return "gdrive"
    if "dropbox.com" in hostname:
        return "dropbox"
    if "onedrive.live.com" in hostname:
        return "onedrive"

    # Fallback for yt-dlp supported hosts (this is a simplified check)
    # A more robust implementation might involve trying to extract info using yt-dlp
    return "yt-dlp"

