import asyncio
import logging
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import config
from handlers import commands, media

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("telegram_downloader")


async def setup_bot_commands(bot: Bot) -> None:
    """Registers command hints in Telegram menu for users."""
    bot_commands = [
        BotCommand(command="start", description="Start the bot & see instructions"),
        BotCommand(command="help", description="How to use the bot in chats & groups"),
        BotCommand(command="dl", description="Download a video link: /dl <url>"),
        BotCommand(command="ping", description="Check bot status"),
    ]
    try:
        await bot.set_my_commands(bot_commands)
        logger.info("Bot commands successfully registered with Telegram.")
    except Exception as e:
        logger.warning(f"Could not register bot commands: {e}")


async def main() -> None:
    """Main application entry point."""
    logger.info("Initializing Telegram Media Downloader Bot...")

    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        sys.exit(1)

    # Initialize bot and dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register routers
    dp.include_router(commands.router)
    dp.include_router(media.router)

    # Delete any pending updates to avoid processing stale queue on startup
    await bot.delete_webhook(drop_pending_updates=True)

    # Setup command menu hints
    await setup_bot_commands(bot)

    bot_info = await bot.get_me()
    logger.info(f"Bot @{bot_info.username} (ID: {bot_info.id}) started successfully!")
    logger.info("Listening for TikTok and Twitter/X links in private chats and groups...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot session closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
