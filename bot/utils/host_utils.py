
from urllib.parse import urlparse

def detect_host(url: str) -> str:
    """
    Detects the hosting platform from a given URL.

    Args:
        url: The URL to inspect.

    Returns:
        A string representing the detected host, or "direct" for unknown hosts.
    """
    if not url:
        return "unknown"

    hostname = urlparse(url).hostname
    if not hostname:
        return "unknown"

    hostname = hostname.lower()

    if "mega.nz" in hostname or "mega.io" in hostname:
        return "mega"
    if "drive.google.com" in hostname:
        return "gdrive"
    if "dropbox.com" in hostname:
        return "dropbox"
    if "onedrive.live.com" in hostname:
        return "onedrive"
    if "mediafire.com" in hostname:
        return "mediafire"
    if "pixeldrain.com" in hostname:
        return "pixeldrain"
    if "mixdrop.co" in hostname or "mixdrop.to" in hostname:
        return "mixdrop"
    if "doodstream.com" in hostname or "dood.watch" in hostname:
        return "doodstream"
    if "gofile.io" in hostname:
        return "gofile"
    if "anonfiles.com" in hostname:
        return "anonfiles"
    if "file.io" in hostname:
        return "fileio"
    if "krakenfiles.com" in hostname:
        return "krakenfiles"
    if "terabox.com" in hostname or "teraboxapp.com" in hostname:
        return "terabox"
    
    # These hosts are also supported by yt-dlp, but we can be more specific
    yt_dlp_hosts = [
        "terabox.com", "teraboxapp.com", "mediafire.com", "pixeldrain.com", 
        "mixdrop.co", "mixdrop.to", "doodstream.com", "dood.watch"
    ]
    if any(host in hostname for host in yt_dlp_hosts):
        return "yt-dlp"

    # Fallback to direct download for any other link
    return "direct"
