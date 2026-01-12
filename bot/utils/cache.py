import hashlib
import os
import time
from collections import defaultdict

class DownloadCache:
    def __init__(self, cache_dir: str, max_cache_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_cache_age_hours = max_cache_age_hours
        os.makedirs(cache_dir, exist_ok=True)
        self.cache = defaultdict(dict)  # url_hash -> {file_path, timestamp}

    def _get_hash(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def is_cached(self, url: str) -> str or None:
        """Return cached file path if exists and not expired, else None."""
        hash_key = self._get_hash(url)
        cache_file = os.path.join(self.cache_dir, f"{hash_key}.cache")
        if os.path.exists(cache_file):
            mtime = os.path.getmtime(cache_file)
            if time.time() - mtime < self.max_cache_age_hours * 3600:
                return cache_file
            else:
                os.remove(cache_file)  # Remove expired cache
        return None

    def add_to_cache(self, url: str, file_path: str):
        """Add file to cache."""
        hash_key = self._get_hash(url)
        cache_file = os.path.join(self.cache_dir, f"{hash_key}.cache")
        # For simplicity, just touch the file; in real impl, copy or link
        with open(cache_file, 'w') as f:
            f.write(file_path)
        os.utime(cache_file, None)  # Update timestamp