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
    Telegram caption limit is 1024 characters.
    """
    platform_label = "TikTok" if platform.lower() == "tiktok" else "Twitter / X"
    icon = "🎵" if platform.lower() == "tiktok" else "🐦"

    lines = []

    # Title / description
    if title:
        clean_title = html.escape(title.strip())
        if len(clean_title) > 250:
            clean_title = clean_title[:247] + "..."
        lines.append(f"<b>{clean_title}</b>\n")

    # Author
    if uploader:
        lines.append(f"👤 <i>{html.escape(uploader)}</i>")

    # Source platform and link
    if source_url:
        lines.append(f"{icon} <a href=\"{html.escape(source_url)}\">{platform_label}</a>")
    else:
        lines.append(f"{icon} {platform_label}")

    caption = "\n".join(lines)
    if len(caption) > max_length:
        caption = caption[: max_length - 3] + "..."

    return caption


async def safe_delete_message(bot: Bot, chat_id: int, message_id: int) -> None:
    """Safely attempts to delete a message without raising unhandled exceptions."""
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.debug(f"Could not delete message {message_id} in chat {chat_id}: {e}")
