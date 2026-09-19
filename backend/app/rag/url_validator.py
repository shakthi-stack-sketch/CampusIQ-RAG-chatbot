import re
import urllib.request
import urllib.error
from urllib.parse import urlparse
from typing import Optional, Dict

_CACHE: Dict[str, bool] = {}

YT_VIDEO_REGEX = re.compile(
    r'^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})(?:&.*)?$'
)

LINKEDIN_REGEX = re.compile(
    r'^https?:\/\/(?:[a-z]{2,3}\.)?linkedin\.com\/(?:school|company|in|posts)\/[a-zA-Z0-9_-]+.*$'
)

COLLEGE_SITE_REGEX = re.compile(
    r'^https?:\/\/(?:[a-zA-Z0-9-]+\.)*prathyusha\.edu\.in(?:\/.*)?$'
)

def check_youtube_video_availability(video_url: str) -> bool:
    """Verify YouTube video availability via official oEmbed endpoint."""
    match = YT_VIDEO_REGEX.match(video_url)
    if not match:
        return False
    video_id = match.group(1)
    if video_url in _CACHE:
        return _CACHE[video_url]

    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        req = urllib.request.Request(oembed_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            is_valid = (resp.status == 200)
            _CACHE[video_url] = is_valid
            return is_valid
    except Exception:
        _CACHE[video_url] = False
        return False

def validate_source_url(url: Optional[str], platform: str = "") -> Optional[str]:
    """
    Validate external source URLs to ensure students never encounter broken links.
    Returns:
        Validated URL string if verified and usable; otherwise None.
    """
    if not url or not isinstance(url, str):
        return None

    cleaned_url = url.strip()
    if not cleaned_url.startswith(("http://", "https://")):
        return None

    parsed = urlparse(cleaned_url)
    netloc = parsed.netloc.lower()

    # 1. LinkedIn Handling (Preserve working school and post URLs)
    if "linkedin.com" in netloc:
        if LINKEDIN_REGEX.match(cleaned_url):
            return cleaned_url
        return None

    # 2. YouTube Handling
    if "youtube.com" in netloc or "youtu.be" in netloc:
        if "watch?v=" in cleaned_url or "youtu.be/" in cleaned_url:
            if check_youtube_video_availability(cleaned_url):
                return cleaned_url
            # Video is unavailable, private, or has invalid ID
            return None
        # Channel or handle URLs (e.g., https://youtube.com/@prathyushaengineeringcollege)
        if "/@" in cleaned_url or "/channel/" in cleaned_url:
            return cleaned_url
        return None

    # 3. Instagram Handling
    if "instagram.com" in netloc:
        # Instagram post links in current knowledge base are placeholder slugs (e.g. /p/pec_hackathon_ignite_2026)
        # which result in "Post isn't available".
        # Valid Instagram shortcodes are base64 Media IDs (e.g. C_7xyz91234) without descriptive English slugs.
        path_parts = [p for p in parsed.path.split("/") if p]
        if len(path_parts) >= 2 and path_parts[0] == "p":
            shortcode = path_parts[1]
            if "pec_" in shortcode.lower() or len(shortcode) > 15:
                return None
            return None
        return None

    # 4. Official College Website Handling
    if COLLEGE_SITE_REGEX.match(cleaned_url):
        return cleaned_url

    return None
