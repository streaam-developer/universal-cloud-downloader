import time
from collections import defaultdict

class UserLimits:
    def __init__(self, max_downloads_per_hour: int = 10, max_file_size_mb: int = 1024):
        self.max_downloads_per_hour = max_downloads_per_hour
        self.max_file_size_mb = max_file_size_mb
        self.user_downloads = defaultdict(list)  # user_id -> list of timestamps

    def can_download(self, user_id: int) -> bool:
        now = time.time()
        # Remove old entries (older than 1 hour)
        self.user_downloads[user_id] = [t for t in self.user_downloads[user_id] if now - t < 3600]
        return len(self.user_downloads[user_id]) < self.max_downloads_per_hour

    def record_download(self, user_id: int):
        self.user_downloads[user_id].append(time.time())

    def check_file_size(self, size_bytes: int) -> bool:
        size_mb = size_bytes / (1024 * 1024)
        return size_mb <= self.max_file_size_mb