import re
from typing import List, Tuple

# Regex patterns for supported media URLs
TIKTOK_PATTERN = re.compile(
    r"(https?://(?:www\.|vm\.|vt\.|m\.)?tiktok\.com/(?:@[a-zA-Z0-9_.-]+/video/\d+|[a-zA-Z0-9_/-]+|v/\d+\.html)(?:\?[^\s<>\"']*)?)",
    re.IGNORECASE,
)

TWITTER_X_PATTERN = re.compile(
    r"(https?://(?:www\.|mobile\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+/status/\d+(?:\?[^\s<>\"']*)?)",
    re.IGNORECASE,
)


def _clean_url(url: str) -> str:
    """Strips sentence punctuation from URL while preserving path slashes."""
    return url.rstrip(".,!?:;)>\"'")


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

    return found


def is_supported_url(text: str) -> bool:
    """Checks if the given text contains at least one supported TikTok or Twitter/X link."""
    return bool(extract_media_urls(text))
