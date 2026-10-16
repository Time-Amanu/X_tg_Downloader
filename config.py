import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / ".env")


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
    MAX_CONCURRENT_DOWNLOADS: int = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "3"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    AUTO_DOWNLOAD_IN_GROUPS: bool = os.getenv("AUTO_DOWNLOAD_IN_GROUPS", "true").lower() in ("true", "1", "yes")
    CLEANUP_STATUS_MESSAGES: bool = os.getenv("CLEANUP_STATUS_MESSAGES", "true").lower() in ("true", "1", "yes")

    # Allowed chats/users filter (comma separated). Empty means all users/chats allowed.
    _raw_allowed = os.getenv("ALLOWED_CHATS", "").strip()
    ALLOWED_CHATS: set[int] = {
        int(chat_id.strip())
        for chat_id in _raw_allowed.split(",")
        if chat_id.strip().lstrip("-").isdigit()
    }

    @classmethod
    def validate(cls) -> None:
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "your_telegram_bot_token_here":
            raise ValueError(
                "BOT_TOKEN is not set or has the placeholder value in .env file!\n"
                "Please get a bot token from @BotFather on Telegram and set it in your .env file."
            )


config = Config()
