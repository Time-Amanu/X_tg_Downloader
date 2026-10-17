from __future__ import annotations

import html
import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)


def human_readable_size(size_bytes: Optional[int]) -> str:
    """Converts a byte count into a human-friendly string (e.g. 14.2 MB)."""
    if not size_bytes or size_bytes <= 0:
        return "Unknown size"

    units = ["B", "KB", "MB", "GB"]
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    return f"{size:.1f} {units[unit_index]}"


def format_video_caption(
    platform: str,
    title: Optional[str] = None,
    uploader: Optional[str] = None,
    source_url: Optional[str] = None,
    max_length: int = 1000,
) -> str:
    """
    Builds a clean, styled HTML caption for Telegram video messages.
    Ensures HTML tags are never severed by truncation. Telegram limit is 1024 characters.
    """
    if platform.lower() == "tiktok":
        platform_label = "TikTok"
        icon = "🎵"
    elif platform.lower() in ("youtube", "youtube_shorts"):
        platform_label = "YouTube Shorts"
        icon = "🔴"
    else:
        platform_label = "Twitter / X"
        icon = "🐦"

    # Clean and strip bloated query params from link for clean embedding
    clean_link = source_url.strip() if source_url else ""
    if clean_link and any(d in clean_link.lower() for d in ("tiktok.com", "twitter.com", "x.com", "youtube.com")):
        clean_link = clean_link.split("?")[0]

    link_line = f"{icon} <a href=\"{html.escape(clean_link)}\">{platform_label}</a>" if clean_link else f"{icon} {platform_label}"
    
    # Safe uploader string
    safe_uploader = html.escape(uploader.strip()[:60]) if uploader else None
    uploader_line = f"👤 <i>{safe_uploader}</i>" if safe_uploader else ""

    # Calculate safe space for title to ensure total caption never exceeds max_length
    fixed_length = len(link_line) + (len(uploader_line) + 2 if uploader_line else 0) + 15
    title_budget = max(50, max_length - fixed_length)

    lines = []
    if title:
        raw_title = title.strip()
        if len(raw_title) > title_budget:
            raw_title = raw_title[: title_budget - 3] + "..."
        lines.append(f"<b>{html.escape(raw_title)}</b>\n")

    if uploader_line:
        lines.append(uploader_line)

    lines.append(link_line)

    return "\n".join(lines)


async def safe_delete_message(bot: Bot, chat_id: int, message_id: int) -> None:
    """Safely attempts to delete a message without raising unhandled exceptions."""
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.debug(f"Could not delete message {message_id} in chat {chat_id}: {e}")
