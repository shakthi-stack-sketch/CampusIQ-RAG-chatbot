import json
from pathlib import Path
from typing import List, Dict, Any

from backend.app.config import SOCIAL_MEDIA_DIR, OFFICIAL_SOURCES

def load_official_social_media() -> List[Dict[str, Any]]:
    """
    Load official verified social media records for Prathyusha Engineering College (PEC)
    from LinkedIn, Instagram, and YouTube.
    """
    json_path = SOCIAL_MEDIA_DIR / "official_pec_social.json"
    if not json_path.exists():
        print(f"[SocialLoader] Warning: {json_path} does not exist.")
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        knowledge_items = []
        for r in records:
            platform = r.get("source_platform", "social_media").lower()
            platform_info = OFFICIAL_SOURCES.get(platform, {})
            source_name = platform_info.get("name", f"Official PEC {platform.capitalize()}")
            channel_url = platform_info.get("url", r.get("source_url", ""))

            # Build comprehensive textual content including caption, transcript, speakers, and venue
            content_lines = [
                f"TITLE: {r.get('title', '')}",
                f"SOURCE: {source_name}",
                f"PLATFORM: {platform.upper()}",
            ]
            if r.get("publication_date"):
                content_lines.append(f"PUBLICATION DATE: {r.get('publication_date')}")
            if r.get("event_date"):
                content_lines.append(f"EVENT DATE: {r.get('event_date')}")
            if r.get("department"):
                content_lines.append(f"DEPARTMENT: {r.get('department')}")
            if r.get("organizer"):
                content_lines.append(f"ORGANIZER: {r.get('organizer')}")
            if r.get("speaker"):
                content_lines.append(f"RESOURCE PERSON / SPEAKER: {r.get('speaker')}")
            if r.get("venue"):
                content_lines.append(f"VENUE: {r.get('venue')}")
            if r.get("registration_info"):
                content_lines.append(f"REGISTRATION & ELIGIBILITY: {r.get('registration_info')}")
            if r.get("hashtags"):
                content_lines.append(f"TOPICS / TAGS: {' '.join(r.get('hashtags', []))}")

            content_lines.append(f"\nOFFICIAL ANNOUNCEMENT / CAPTION:\n{r.get('full_caption', '')}")

            if r.get("transcript"):
                content_lines.append(f"\nVERIFIED VIDEO TRANSCRIPT:\n{r.get('transcript')}")

            full_text = "\n".join(content_lines)

            knowledge_items.append({
                "content": full_text,
                "metadata": {
                    "source": source_name,
                    "title": r.get("title", ""),
                    "category": r.get("content_type", "college_announcement"),
                    "source_type": "social_media",
                    "source_platform": source_name,
                    "source_url": channel_url,
                    "original_url": r.get("original_url", channel_url),
                    "publication_date": r.get("publication_date", ""),
                    "event_date": r.get("event_date", ""),
                    "department": r.get("department", ""),
                    "speaker": r.get("speaker", ""),
                    "venue": r.get("venue", ""),
                    "verified": True
                }
            })

        print(f"[SocialLoader] Loaded {len(knowledge_items)} verified social media knowledge items.")
        return knowledge_items
    except Exception as e:
        print(f"[SocialLoader] Error loading social media knowledge: {e}")
        return []
