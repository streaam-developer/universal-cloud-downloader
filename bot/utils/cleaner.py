import os
import shutil
import time
from pathlib import Path

class AutoCleaner:
    def __init__(self, temp_dir: str, max_age_hours: int = 1, max_disk_usage_gb: int = 10):
        self.temp_dir = Path(temp_dir)
        self.max_age_hours = max_age_hours
        self.max_disk_usage_gb = max_disk_usage_gb * (1024**3)  # Convert to bytes

    def cleanup_old_files(self):
        """Remove files older than max_age_hours."""
        now = time.time()
        for file_path in self.temp_dir.rglob('*'):
            if file_path.is_file():
                if now - file_path.stat().st_mtime > self.max_age_hours * 3600:
                    file_path.unlink()

    def cleanup_disk_usage(self):
        """Remove oldest files if disk usage exceeds limit."""
        files = []
        total_size = 0
        for file_path in self.temp_dir.rglob('*'):
            if file_path.is_file():
                files.append((file_path, file_path.stat().st_mtime, file_path.stat().st_size))
                total_size += file_path.stat().st_size

        if total_size > self.max_disk_usage_gb:
            # Sort by modification time (oldest first)
            files.sort(key=lambda x: x[1])
            for file_path, _, size in files:
                if total_size <= self.max_disk_usage_gb:
                    break
                file_path.unlink()
                total_size -= size

    def run_cleanup(self):
        self.cleanup_old_files()
        self.cleanup_disk_usage()