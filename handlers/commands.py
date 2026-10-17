import logging
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode

from config import config

router = Router(name="commands_router")
logger = logging.getLogger(__name__)


def is_chat_allowed(chat_id: int, user_id: int, username: str | None = None) -> bool:
    """Checks if chat, user ID, or username is allowed."""
    return config.is_allowed(chat_id, user_id, username)


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Handles the /start command."""
    user = message.from_user
    if not is_chat_allowed(message.chat.id, user.id if user else 0, user.username if user else None):
        return

    text = (
        "👋 <b>Welcome to Media Downloader Bot!</b>\n\n"
        "I can download and send high-quality videos from <b>TikTok</b>, <b>Twitter / X</b>, and <b>YouTube Shorts</b>.\n\n"
        "🚀 <b>Features:</b>\n"
        "• <b>Direct Chat</b>: Simply send me any TikTok, Twitter/X, or YouTube Shorts link.\n"
        "• <b>Groups & Channels</b>: Add me to any group and I will automatically fetch videos whenever someone posts a link!\n"
        "• Fast streaming playback support.\n\n"
        "📌 <b>Supported Links:</b>\n"
        "• TikTok (<code>tiktok.com</code>, <code>vt.tiktok.com</code>, <code>vm.tiktok.com</code>)\n"
        "• Twitter / X (<code>x.com/.../status/...</code>, <code>twitter.com/.../status/...</code>)\n"
        "• YouTube Shorts (<code>youtube.com/shorts/...</code>)\n\n"
        "💡 <i>Try sending a link now, or use /help for more options!</i>"
    )
    await message.reply(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Handles the /help command."""
    user = message.from_user
    if not is_chat_allowed(message.chat.id, user.id if user else 0, user.username if user else None):
        return

    text = (
        "📖 <b>How to Use This Bot:</b>\n\n"
        "1️⃣ <b>Direct Messages:</b>\n"
        "Just paste a video link into the chat. The bot will download and send it to you.\n\n"
        "2️⃣ <b>In Telegram Groups:</b>\n"
        "• Add this bot to your group.\n"
        "• By default, when anyone posts a supported link, the bot replies with the video.\n"
        "• You can also use <code>/dl &lt;link&gt;</code> to download explicitly.\n"
        "• <i>Note:</i> In @BotFather, make sure Group Privacy Mode is disabled (<code>/setprivacy -&gt; Disable</code>) "
        "if you want the bot to automatically detect links without using commands.\n\n"
        "⚡ <b>Commands:</b>\n"
        "• /start - Start the bot\n"
        "• /help - Show this guide\n"
        "• /ping - Test bot responsiveness\n"
        "• /dl &lt;link&gt; - Download a specific link"
    )
    await message.reply(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.message(Command("ping"))
async def handle_ping(message: Message) -> None:
    """Health check ping command."""
    user = message.from_user
    if not is_chat_allowed(message.chat.id, user.id if user else 0, user.username if user else None):
        return
    await message.reply("🏓 <b>Pong!</b> Bot is running and ready.", parse_mode=ParseMode.HTML)
