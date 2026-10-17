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
    PORT: int | None = int(os.getenv("PORT")) if os.getenv("PORT") and os.getenv("PORT").strip().isdigit() else None

    # Allowed usernames or numeric chat/user IDs (case-insensitive)
    # Locked to @Timelight217 by default; can be overridden via ALLOWED_USERS or ALLOWED_CHATS
    _raw_allowed = (os.getenv("ALLOWED_USERS") or os.getenv("ALLOWED_CHATS") or "Timelight217").strip()
    ALLOWED_USERS: set[str] = {
        item.strip().lstrip("@").lower()
        for item in _raw_allowed.split(",")
        if item.strip()
    }

    # Backward compatibility for numeric ALLOWED_CHATS
    ALLOWED_CHATS: set[int] = {
        int(item) for item in ALLOWED_USERS if item.lstrip("-").isdigit()
    }

    @classmethod
    def is_allowed(cls, chat_id: int, user_id: int, username: str | None = None) -> bool:
        """Returns True if the message is from an authorized user or chat."""
        if not cls.ALLOWED_USERS:
            return True
        if str(user_id) in cls.ALLOWED_USERS or str(chat_id) in cls.ALLOWED_USERS:
            return True
        if username and username.strip().lstrip("@").lower() in cls.ALLOWED_USERS:
            return True
        return False

    @classmethod
    def validate(cls) -> None:
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "your_telegram_bot_token_here":
            raise ValueError(
                "BOT_TOKEN is not set or has the placeholder value in .env file!\n"
                "Please get a bot token from @BotFather on Telegram and set it in your .env file."
            )


config = Config()
