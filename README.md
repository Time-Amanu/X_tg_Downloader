# 🚀 Telegram Media Downloader Bot (TikTok & Twitter / X)

A high-performance, asynchronous Telegram bot built with **Python 3**, **aiogram 3.x**, and **yt-dlp**. It automatically detects, downloads, and sends videos from **TikTok** and **Twitter / X** directly to users or inside Telegram groups and supergroups.

---

## ✨ Features

- **Direct Messages & Group Chats**:
  - **In Private Chats**: Send any TikTok or Twitter/X link and the bot replies with the downloaded video.
  - **In Groups**: The bot automatically detects links posted by members and sends the video as a direct reply to the sender.
  - **Explicit Command**: `/dl <url>` or reply to any message containing a link with `/dl`.
- **Clean Group Experience**:
  - Automatically sends a temporary "⏳ Processing video..." message and deletes it as soon as the video is sent, preventing chat clutter.
- **Fast & Non-Blocking**:
  - Heavy download and extraction I/O runs in thread pools (`asyncio.to_thread`), preventing the bot from freezing or lagging for other users.
  - Throttled concurrency with `asyncio.Semaphore` to protect CPU, RAM, and bandwidth.
- **Direct Telegram Streaming**:
  - Sends videos with `supports_streaming=True`, correct duration, and video dimensions so users can watch immediately without waiting for full download.
- **Safe Disk Management**:
  - Every download runs inside an isolated temporary directory and is guaranteed to be deleted in a `finally` block even if the upload is aborted or an error occurs.
- **50 MB Size Limit Protection**:
  - Validates format and file size against the Telegram Bot API 50 MB limit, cleanly reporting the exact file size if exceeded.

---

## 📌 Supported Link Formats

### TikTok
- `https://www.tiktok.com/@username/video/1234567890123456789`
- `https://vt.tiktok.com/ZSxxxxxx/`
- `https://vm.tiktok.com/ZMxxxxxx/`
- `https://m.tiktok.com/v/1234567890.html`

### Twitter / X
- `https://twitter.com/username/status/1234567890123456789`
- `https://x.com/username/status/1234567890123456789`
- `https://mobile.twitter.com/...` or `https://mobile.x.com/...`

---

## 🛠️ Project Structure

```
downloader/
├── bot.py                  # Bot entry point and polling loop
├── config.py               # Environment configuration and validation
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── handlers/
│   ├── __init__.py
│   ├── commands.py         # /start, /help, /ping handlers
│   └── media.py            # Automatic URL detection and /dl command handlers
├── services/
│   ├── __init__.py
│   └── downloader.py       # Asynchronous yt-dlp wrapper and metadata extractor
├── utils/
│   ├── __init__.py
│   ├── extractors.py       # Regex extractors for TikTok and Twitter/X
│   └── helpers.py          # Caption formatting and message cleanup
└── test_extractors.py      # Smoke tests for URL extractors and captions
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python **3.10+** (Tested on Python 3.13)
- A Telegram account to create your bot via [@BotFather](https://t.me/BotFather)

### 2. Create Your Telegram Bot
1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to choose a name and username (e.g. `MyMediaDownloaderBot`).
3. Copy the **HTTP API Bot Token** provided by BotFather.
4. **Important for Groups**:
   - In BotFather, send `/setprivacy`.
   - Select your bot.
   - Choose **Disable**.
   - *Why?* By default, Telegram hides regular messages from bots in groups. Disabling privacy mode allows the bot to detect TikTok and Twitter links automatically when members chat. (If you prefer to keep privacy mode enabled, users can still trigger downloads using `/dl <link>`).

### 3. Setup Environment
Open your terminal in the project directory:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 4. Configure `.env`
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `.env` and fill in your bot token:
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
MAX_CONCURRENT_DOWNLOADS=3
MAX_FILE_SIZE_MB=50
AUTO_DOWNLOAD_IN_GROUPS=true
CLEANUP_STATUS_MESSAGES=true
```

### 5. Run the Bot
```bash
python bot.py
```

You should see:
```text
[INFO] telegram_downloader: Bot @YourBotUsername (ID: 123456789) started successfully!
[INFO] telegram_downloader: Listening for TikTok and Twitter/X links in private chats and groups...
```

---

## 💡 Usage Examples

### Direct Chat
Open a chat with your bot and send:
```text
https://vt.tiktok.com/ZS2xyzABC/
```
The bot will reply with the video and caption.

### In Groups
1. Add your bot to any Telegram group.
2. Any member posts:
```text
Check out this clip: https://x.com/OpenAI/status/1780000000000000000
```
3. The bot replies directly to that member's message with the video attached!

### Explicit Command (`/dl`)
```text
/dl https://www.tiktok.com/@user/video/123456789
```
Or reply to any existing message with `/dl`.

---

## ⚙️ Configuration Options

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | *Required* | Telegram Bot API Token from @BotFather |
| `MAX_CONCURRENT_DOWNLOADS` | `3` | Max simultaneous video downloads to avoid network saturation |
| `MAX_FILE_SIZE_MB` | `50` | Maximum file size allowed by Telegram Bot API |
| `AUTO_DOWNLOAD_IN_GROUPS` | `true` | When `true`, links posted in groups are downloaded automatically |
| `CLEANUP_STATUS_MESSAGES` | `true` | When `true`, deletes "Downloading..." messages after video upload |
| `ALLOWED_CHATS` | *(Empty)* | Optional comma-separated chat or user IDs to restrict bot access |

---

## 🧪 Testing
Run the extractor unit tests:
```bash
python test_extractors.py
```
