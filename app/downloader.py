import os
import re
import tempfile
from pathlib import Path
from typing import Optional

import yt_dlp


class DownloadError(Exception):
    pass


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)[:120] or "download"


def download_media(url: str) -> tuple[str, str]:
    """Download media from a supported social URL.

    Returns:
        (downloaded_path, mime_type)
    """
    if not url:
        raise DownloadError("No URL was provided.")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": False,
        "noplaylist": True,
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(tempfile.gettempdir(), "telegram_dl_%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "restrictfilenames": False,
        "socket_timeout": 30,
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            raise DownloadError("Unable to read the provided link.")

        title = info.get("title") or "download"
        safe_title = sanitize_filename(title)
        file_path = os.path.join(tempfile.gettempdir(), f"telegram_dl_{safe_title}.%(ext)s")
        ydl.params["outtmpl"] = file_path
        ydl.download([url])

    downloaded_file = None
    for path in Path(tempfile.gettempdir()).glob(f"telegram_dl_{safe_title}.*"):
        if path.is_file() and path.stat().st_size > 0:
            downloaded_file = str(path)
            break

    if not downloaded_file:
        raise DownloadError("The link did not produce a downloadable file.")

    extension = Path(downloaded_file).suffix.lower()
    mime_type = {
        ".mp4": "video/mp4",
        ".mkv": "video/x-matroska",
        ".webm": "video/webm",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }.get(extension, "application/octet-stream")

    return downloaded_file, mime_type
