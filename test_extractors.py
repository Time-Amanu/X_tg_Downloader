"""
Smoke test suite for URL extraction and caption formatting.
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from utils.extractors import extract_media_urls
from utils.helpers import format_video_caption, human_readable_size


def test_url_extraction():
    test_cases = [
        # TikTok tests
        ("Check out this tiktok https://www.tiktok.com/@mrbeast/video/7200000000000000000 it is funny", [
            ("tiktok", "https://www.tiktok.com/@mrbeast/video/7200000000000000000")
        ]),
        ("Short link: https://vt.tiktok.com/ZS2xyzABC/!", [
            ("tiktok", "https://vt.tiktok.com/ZS2xyzABC/")
        ]),
        ("Long TikTok with tracking query: https://www.tiktok.com/@mrbeast/video/7200000000000000000?is_from_webapp=1&sender_device=pc&_t=8a123", [
            ("tiktok", "https://www.tiktok.com/@mrbeast/video/7200000000000000000")
        ]),
        ("TikTok Photo mode: https://www.tiktok.com/@creator/photo/7300000000000000000", [
            ("tiktok", "https://www.tiktok.com/@creator/photo/7300000000000000000")
        ]),
        ("VM link: https://vm.tiktok.com/ZM8rxyzABC/?k=1", [
            ("tiktok", "https://vm.tiktok.com/ZM8rxyzABC/?k=1")
        ]),

        # Twitter / X tests
        ("Look at this tweet https://twitter.com/elonmusk/status/1780000000000000000 right now", [
            ("twitter", "https://twitter.com/elonmusk/status/1780000000000000000")
        ]),
        ("X link with tracking query: https://x.com/OpenAI/status/1780000000000000000?s=20&t=xyz123", [
            ("twitter", "https://x.com/OpenAI/status/1780000000000000000")
        ]),

        # YouTube Shorts tests
        ("Watch this short https://www.youtube.com/shorts/dQw4w9WgXcQ so good", [
            ("youtube", "https://www.youtube.com/shorts/dQw4w9WgXcQ")
        ]),
        ("Short with tracking params: https://youtube.com/shorts/abcdef12345?feature=share&si=test", [
            ("youtube", "https://youtube.com/shorts/abcdef12345")
        ]),

        # Multiple links in single message
        ("Both: https://vt.tiktok.com/ZS2xyz/ and https://x.com/user/status/123456789 and https://youtube.com/shorts/xyz123", [
            ("tiktok", "https://vt.tiktok.com/ZS2xyz/"),
            ("twitter", "https://x.com/user/status/123456789"),
            ("youtube", "https://youtube.com/shorts/xyz123")
        ]),

        # Non-matching text
        ("Just a normal message with https://google.com and https://youtube.com/watch?v=123", []),
    ]

    for text, expected in test_cases:
        actual = extract_media_urls(text)
        assert actual == expected, f"Failed for '{text}': got {actual}, expected {expected}"

    print("✅ All extractor tests passed!")


def test_helpers():
    assert human_readable_size(1024) == "1.0 KB"
    assert human_readable_size(15 * 1024 * 1024) == "15.0 MB"
    assert human_readable_size(0) == "Unknown size"

    caption = format_video_caption(
        platform="tiktok",
        title="Epic Cat Jump",
        uploader="CatLover",
        source_url="https://vt.tiktok.com/xyz",
    )
    assert "Epic Cat Jump" in caption
    assert "CatLover" in caption
    assert "TikTok" in caption

    yt_caption = format_video_caption(
        platform="youtube",
        title="Epic Tech Short",
        uploader="TechChannel",
        source_url="https://www.youtube.com/shorts/123",
    )
    assert "Epic Tech Short" in yt_caption
    assert "YouTube Shorts" in yt_caption
    assert "🔴" in yt_caption

    print("✅ All helper tests passed!")


if __name__ == "__main__":
    test_url_extraction()
    test_helpers()
