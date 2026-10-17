import re
from typing import List, Tuple

# Regex patterns for supported media URLs
TIKTOK_PATTERN = re.compile(
    r"(https?://(?:www\.|vm\.|vt\.|m\.)?tiktok\.com/(?:@[a-zA-Z0-9_.-]+/(?:video|photo)/\d+|[a-zA-Z0-9_/-]+|v/\d+\.html)(?:\?[^\s<>\"']*)?)",
    re.IGNORECASE,
)

TWITTER_X_PATTERN = re.compile(
    r"(https?://(?:www\.|mobile\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+/status/\d+(?:\?[^\s<>\"']*)?)",
    re.IGNORECASE,
)

YOUTUBE_SHORTS_PATTERN = re.compile(
    r"(https?://(?:www\.|m\.)?youtube\.com/shorts/[a-zA-Z0-9_-]+(?:\?[^\s<>\"']*)?)",
    re.IGNORECASE,
)


def _clean_url(url: str) -> str:
    """Strips sentence punctuation and bloat tracking query parameters from URL."""
    cleaned = url.rstrip(".,!?:;)>\"'")
    # Remove tracking query bloat from standard TikTok video and photo URLs
    if "tiktok.com" in cleaned.lower() and ("/video/" in cleaned.lower() or "/photo/" in cleaned.lower()):
        cleaned = re.sub(r"(\.tiktok\.com/@[^/?#]+/(?:video|photo)/\d+)(?:\?[^\s#]*)?", r"\1", cleaned)
    # Remove tracking query bloat from standard Twitter / X status URLs
    elif ("twitter.com" in cleaned.lower() or "x.com" in cleaned.lower()) and "/status/" in cleaned.lower():
        cleaned = re.sub(r"((?:twitter|x)\.com/[^/?#]+/status/\d+)(?:\?[^\s#]*)?", r"\1", cleaned)
    # Remove tracking query bloat from YouTube Shorts URLs
    elif "youtube.com" in cleaned.lower() and "/shorts/" in cleaned.lower():
        cleaned = re.sub(r"(youtube\.com/shorts/[a-zA-Z0-9_-]+)(?:\?[^\s#]*)?", r"\1", cleaned)
        if not cleaned.startswith("http"):
            cleaned = "https://" + cleaned
    return cleaned


def extract_media_urls(text: str) -> List[Tuple[str, str]]:
    """
    Extracts all supported media URLs from a text string.
    Returns a list of tuples: (platform, clean_url)
    e.g. [("tiktok", "https://vt.tiktok.com/..."), ("twitter", "https://x.com/...")]
    """
    if not text:
        return []

    found: List[Tuple[str, str]] = []
    seen: set[str] = set()

    # Search for TikTok URLs
    for match in TIKTOK_PATTERN.finditer(text):
        url = _clean_url(match.group(1))
        if url not in seen:
            seen.add(url)
            found.append(("tiktok", url))

    # Search for Twitter / X URLs
    for match in TWITTER_X_PATTERN.finditer(text):
        url = _clean_url(match.group(1))
        if url not in seen:
            seen.add(url)
            found.append(("twitter", url))

    # Search for YouTube Shorts URLs
    for match in YOUTUBE_SHORTS_PATTERN.finditer(text):
        url = _clean_url(match.group(1))
        if url not in seen:
            seen.add(url)
            found.append(("youtube", url))

    return found


def is_supported_url(text: str) -> bool:
    """Checks if the given text contains at least one supported TikTok or Twitter/X link."""
    return bool(extract_media_urls(text))
