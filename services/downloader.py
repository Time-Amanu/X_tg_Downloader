import asyncio
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yt_dlp

from config import config

logger = logging.getLogger(__name__)


class VideoDownloadError(Exception):
    """Base exception for video downloader failures."""
    pass


class FileTooLargeError(VideoDownloadError):
    """Raised when the downloaded video exceeds Telegram Bot API size limit."""
    pass


class VideoNotFoundError(VideoDownloadError):
    """Raised when the video cannot be found, was deleted, or is private."""
    pass


@dataclass
class DownloadResult:
    video_path: Path
    title: str
    uploader: str
    duration: Optional[int]
    width: Optional[int]
    height: Optional[int]
    file_size: int
    temp_dir: Path

    def cleanup(self) -> None:
        """Removes the temporary directory and all downloaded files safely."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to remove temp dir {self.temp_dir}: {e}")


class DownloaderService:
    def __init__(self, max_concurrent: int = 3):
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def download_video(self, url: str, platform: str) -> DownloadResult:
        """
        Asynchronously downloads video from TikTok or Twitter/X.
        Guarantees non-blocking execution via asyncio.to_thread and limits concurrency.
        """
        async with self._semaphore:
            return await asyncio.to_thread(self._sync_download, url, platform)

    def _sync_download(self, url: str, platform: str) -> DownloadResult:
        """
        Synchronous download execution inside thread pool using yt-dlp.
        """
        temp_dir = Path(tempfile.mkdtemp(prefix="tg_dl_"))
        output_template = str(temp_dir / "%(id)s.%(ext)s")

        max_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024

        # Configure yt-dlp options
        # Note: Pre-merged MP4 is prioritized to work seamlessly even without system ffmpeg
        ydl_opts = {
            "outtmpl": output_template,
            "format": "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "max_filesize": max_bytes,
            "socket_timeout": 30,
            "retries": 3,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            },
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Extracting info for {platform} URL: {url}")
                try:
                    info = ydl.extract_info(url, download=True)
                except yt_dlp.utils.DownloadError as e:
                    err_msg = str(e).lower()
                    if "private" in err_msg or "login" in err_msg or "not found" in err_msg:
                        raise VideoNotFoundError("The video is private, deleted, or requires authentication.")
                    if "file is larger than max-filesize" in err_msg or "larger than" in err_msg:
                        raise FileTooLargeError(
                            f"The video exceeds Telegram's {config.MAX_FILE_SIZE_MB}MB file size limit."
                        )
                    raise VideoDownloadError(f"Download failed: {e}")

                if not info:
                    raise VideoNotFoundError("Could not extract video metadata.")

                # Locate the downloaded video file in the temp directory
                downloaded_files = [
                    f for f in temp_dir.iterdir()
                    if f.is_file() and f.suffix.lower() in [".mp4", ".mkv", ".webm", ".mov"]
                ]

                if not downloaded_files:
                    raise VideoDownloadError("Video file was not saved to disk after extraction.")

                # Pick the largest downloaded media file (usually the video)
                video_file = max(downloaded_files, key=lambda f: f.stat().st_size)
                file_size = video_file.stat().st_size

                if file_size > max_bytes:
                    raise FileTooLargeError(
                        f"Video file size ({file_size / (1024 * 1024):.1f} MB) exceeds "
                        f"Telegram's {config.MAX_FILE_SIZE_MB}MB limit."
                    )

                title = info.get("title") or info.get("description") or "Video"
                uploader = (
                    info.get("uploader")
                    or info.get("creator")
                    or info.get("channel")
                    or info.get("uploader_id")
                    or "Unknown"
                )
                duration = info.get("duration")
                width = info.get("width")
                height = info.get("height")

                return DownloadResult(
                    video_path=video_file,
                    title=title,
                    uploader=uploader,
                    duration=int(duration) if duration else None,
                    width=int(width) if width else None,
                    height=int(height) if height else None,
                    file_size=file_size,
                    temp_dir=temp_dir,
                )

        except Exception:
            # If an exception occurred during download, clean up temp dir immediately
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise


# Global downloader service instance
downloader_service = DownloaderService(max_concurrent=config.MAX_CONCURRENT_DOWNLOADS)
