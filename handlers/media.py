import html
import logging
from typing import Optional

from aiogram import Bot, Router, F
from aiogram.enums import ChatAction, ChatType, ParseMode
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from config import config
from services.downloader import (
    FileTooLargeError,
    VideoDownloadError,
    VideoNotFoundError,
    downloader_service,
)
from utils.extractors import extract_media_urls
from utils.helpers import format_video_caption, human_readable_size, safe_delete_message

router = Router(name="media_router")
logger = logging.getLogger(__name__)


def is_chat_allowed(chat_id: int, user_id: int, username: str | None = None) -> bool:
    """Checks if chat, user ID, or username is allowed."""
    return config.is_allowed(chat_id, user_id, username)


async def process_and_send_video(
    message: Message,
    bot: Bot,
    url: str,
    platform: str,
) -> None:
    """
    Downloads and uploads a video to Telegram, managing status messages and cleanup.
    """
    status_msg: Optional[Message] = None
    result = None

    try:
        # Send initial status message
        platform_name = "TikTok" if platform == "tiktok" else "Twitter / X"
        status_msg = await message.reply(
            f"⏳ <b>Downloading {platform_name} video...</b>\n<i>Please wait a moment.</i>",
            parse_mode=ParseMode.HTML,
        )

        # Notify Telegram client with upload_video action
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

        # Execute download asynchronously
        result = await downloader_service.download_video(url=url, platform=platform)

        # Update chat action during actual file upload
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

        caption = format_video_caption(
            platform=platform,
            title=result.title,
            uploader=result.uploader,
            source_url=url,
        )

        # Send video file to user/group
        video_input = FSInputFile(str(result.video_path))
        await message.reply_video(
            video=video_input,
            caption=caption,
            parse_mode=ParseMode.HTML,
            duration=result.duration,
            width=result.width,
            height=result.height,
            supports_streaming=True,
        )

        # Clean up the status message if configured
        if config.CLEANUP_STATUS_MESSAGES and status_msg:
            await safe_delete_message(bot, message.chat.id, status_msg.message_id)

    except FileTooLargeError as e:
        error_text = (
            f"⚠️ <b>Video too large for Telegram!</b>\n\n"
            f"{html.escape(str(e))}\n"
            f"Telegram Bot API limits file uploads to 50 MB."
        )
        if status_msg:
            await status_msg.edit_text(error_text, parse_mode=ParseMode.HTML)
        else:
            await message.reply(error_text, parse_mode=ParseMode.HTML)

    except VideoNotFoundError as e:
        error_text = (
            f"❌ <b>Video Not Found</b>\n\n"
            f"{html.escape(str(e))}"
        )
        if status_msg:
            await status_msg.edit_text(error_text, parse_mode=ParseMode.HTML)
        else:
            await message.reply(error_text, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.exception(f"Unexpected error while downloading {url}: {e}")
        error_text = (
            f"❌ <b>Download Error</b>\n\n"
            f"Could not download the requested video.\n"
            f"<i>Details: {html.escape(str(e)[:150])}</i>"
        )
        if status_msg:
            await status_msg.edit_text(error_text, parse_mode=ParseMode.HTML)
        else:
            await message.reply(error_text, parse_mode=ParseMode.HTML)

    finally:
        # Guarantee removal of temporary files
        if result:
            result.cleanup()


@router.message(Command("dl"))
async def handle_dl_command(message: Message, bot: Bot) -> None:
    """
    Explicit /dl <url> command handler.
    Can be used in both direct messages and groups.
    Also supports replying to a message containing a link with '/dl'.
    """
    user = message.from_user
    if not is_chat_allowed(message.chat.id, user.id if user else 0, user.username if user else None):
        return

    text_to_check = message.text or ""

    # Check if command has arguments
    urls = extract_media_urls(text_to_check)

    # If no URL in command text, check if replying to a message with a URL
    if not urls and message.reply_to_message:
        replied_text = message.reply_to_message.text or message.reply_to_message.caption or ""
        urls = extract_media_urls(replied_text)

    if not urls:
        await message.reply(
            "ℹ️ <b>Usage:</b> <code>/dl &lt;url&gt;</code>\n"
            "Or reply to any message containing a TikTok or Twitter/X link with <code>/dl</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Process first found URL
    platform, url = urls[0]
    await process_and_send_video(message, bot, url, platform)


@router.message(F.text)
async def handle_text_urls(message: Message, bot: Bot) -> None:
    """
    Detects TikTok and Twitter/X URLs in standard text messages.
    Works in direct messages and in groups (if AUTO_DOWNLOAD_IN_GROUPS is enabled).
    """
    user = message.from_user
    if not is_chat_allowed(message.chat.id, user.id if user else 0, user.username if user else None):
        return

    # Ignore bot commands in this handler (handled by command routers)
    if message.text and message.text.startswith("/"):
        return

    is_group = message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)

    # In groups, check if auto-download is enabled
    if is_group and not config.AUTO_DOWNLOAD_IN_GROUPS:
        return

    urls = extract_media_urls(message.text or "")
    if not urls:
        return

    # Process the first detected link
    platform, url = urls[0]
    await process_and_send_video(message, bot, url, platform)
