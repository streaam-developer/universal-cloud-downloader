import time
from typing import Callable

class ProgressTracker:
    def __init__(self, total_size: int, update_callback: Callable[[str], None]):
        self.total_size = total_size
        self.downloaded = 0
        self.start_time = time.time()
        self.last_update = 0
        self.update_callback = update_callback

    def update(self, downloaded: int, speed: float = 0, eta: float = 0):
        self.downloaded = downloaded
        current_time = time.time()
        if current_time - self.last_update > 1:  # Update every second
            progress = (downloaded / self.total_size) * 100 if self.total_size > 0 else 0
            speed_mb = speed / (1024 * 1024) if speed else 0
            eta_str = f"{int(eta)}s" if eta else "Unknown"
            message = f"Downloading...\nProgress: {progress:.1f}% - {speed_mb:.1f}MB/s\nETA: {eta_str}"
            self.update_callback(message)
            self.last_update = current_time

    def finish(self):
        elapsed = time.time() - self.start_time
        speed = self.downloaded / elapsed / (1024 * 1024) if elapsed > 0 else 0
        message = f"Download complete!\nSize: {self.downloaded / (1024*1024):.1f}MB\nSpeed: {speed:.1f}MB/s"
        self.update_callback(message)