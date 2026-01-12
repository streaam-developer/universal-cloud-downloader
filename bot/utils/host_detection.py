import re
from urllib.parse import urlparse

def detect_host(url: str) -> str:
    """
    Detect the host platform from the URL.

    Returns:
        str: The detected host name or "unknown" if not recognized.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]

        # Define patterns for each host
        host_patterns = {
            'mega': ['mega.nz', 'mega.io'],
            'terabox': ['terabox.com', 'teraboxapp.com'],
            'mediafire': ['mediafire.com'],
            'gofile': ['gofile.io'],
            'pixeldrain': ['pixeldrain.com'],
            'mixdrop': ['mixdrop.co', 'mixdrop.to'],
            'doodstream': ['doodstream.com', 'dood.so', 'dood.cx'],
            'krakenfiles': ['krakenfiles.com'],
            'anonfiles': ['anonfiles.com'],
            'fileio': ['file.io'],
            'gdrive': ['drive.google.com', 'docs.google.com'],
            'dropbox': ['dropbox.com'],
            'onedrive': ['onedrive.live.com', '1drv.ms'],
        }

        for host, domains in host_patterns.items():
            for d in domains:
                if d in domain:
                    return host

        # Check if it's yt-dlp supported (for other hosts)
        # For simplicity, if not matched above, assume yt-dlp if it's a valid URL
        # But to be precise, we'll return "unknown" and handle yt-dlp separately
        return "unknown"

    except Exception as e:
        print(f"Error detecting host: {e}")
        return "unknown"