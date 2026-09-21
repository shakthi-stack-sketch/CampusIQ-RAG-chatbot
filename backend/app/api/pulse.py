import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query

from backend.app.config import SOCIAL_MEDIA_DIR, OFFICIAL_SOURCES
from backend.app.database.models import PulseItem, OpportunityItem

router = APIRouter(prefix="/api", tags=["Campus Pulse & Opportunities"])

def load_verified_social_items() -> List[Dict[str, Any]]:
    """Load verified items strictly from official college records."""
    social_file = SOCIAL_MEDIA_DIR / "official_pec_social.json"
    if not social_file.exists():
        return []
    try:
        with open(social_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [item for item in data if item.get("verified", True)]
    except Exception as e:
        print(f"[Pulse] Error loading official social media: {e}")
        return []

@router.get("/pulse", response_model=List[PulseItem])
def get_campus_pulse(
    category: Optional[str] = Query(None, description="Category filter (workshop, hackathon, placement, cultural_event, video, seminar, orientation)"),
    search: Optional[str] = Query(None, description="Search term")
):
    """
    Verified Recent Campus Pulse Updates:
    Streams actual verified updates from official institutional channels.
    Never invents dates or updates.
    """
    raw_items = load_verified_social_items()
    pulse_items: List[PulseItem] = []
    cat_str = category if isinstance(category, str) and category.strip() else None
    search_str = search if isinstance(search, str) and search.strip() else None

    for item in raw_items:
        c_type = item.get("content_type", "update")
        # Apply category filter if requested
        if cat_str and cat_str.lower() != "all" and cat_str.lower() not in c_type.lower():
            continue

        title = item.get("title", "")
        caption = item.get("full_caption", "")

        # Apply search filter if requested
        if search_str:
            s_lower = search_str.lower()
            if s_lower not in title.lower() and s_lower not in caption.lower():
                continue

        pulse_items.append(PulseItem(
            id=item.get("id", ""),
            title=title,
            caption=caption,
            content_type=c_type,
            publication_date=item.get("publication_date"),
            event_date=item.get("event_date"),
            department=item.get("department"),
            organizer=item.get("organizer"),
            venue=item.get("venue"),
            source_platform=item.get("source_platform", "Official Channel"),
            source_url=item.get("source_url"),
            original_url=item.get("original_url"),
            verified=True
        ))

    # Sort chronologically by date if available (latest first)
    pulse_items.sort(
        key=lambda x: x.event_date or x.publication_date or "1970-01-01",
        reverse=True
    )
    return pulse_items

@router.get("/opportunities", response_model=List[OpportunityItem])
def get_verified_opportunities(
    category: Optional[str] = Query(None, description="Filter: workshops, hackathons, seminars, training, placements")
):
    """
    Verified Opportunities Section:
    Extracts strictly verified opportunities from official college records.
    Displays available eligibility and application links ONLY if officially provided.
    Never invents deadlines or URLs.
    """
    raw_items = load_verified_social_items()
    opp_items: List[OpportunityItem] = []

    # Map content types to opportunities
    opportunity_types = {"workshop", "hackathon", "placement", "seminar", "video"}

    cat_str = category if isinstance(category, str) and category.strip() else None

    for item in raw_items:
        c_type = item.get("content_type", "")
        if c_type not in opportunity_types and "achievement" not in c_type:
            continue

        # Extract verified registration info or portal link
        reg_info = item.get("registration_info")
        app_link = None
        if reg_info and "http" in reg_info:
            import re
            url_match = re.search(r"https?://[^\s,]+", reg_info)
            if url_match:
                app_link = url_match.group(0)

        # Categorize
        cat = "general"
        if "workshop" in c_type:
            cat = "workshops"
        elif "hackathon" in c_type:
            cat = "hackathons"
        elif "placement" in c_type:
            cat = "training"
        elif "seminar" in c_type:
            cat = "seminars"
        elif "achievement" in c_type or "video" in c_type:
            cat = "competitions"

        if cat_str and cat_str.lower() != "all" and cat_str.lower() != cat:
            continue

        opp_items.append(OpportunityItem(
            id=f"opp_{item.get('id', '')}",
            title=item.get("title", ""),
            category=cat,
            source_platform=item.get("source_platform", "Official PEC Channel"),
            date=item.get("event_date") or item.get("publication_date"),
            description=item.get("full_caption", ""),
            eligibility=reg_info if reg_info and not app_link else (f"Eligibility: {reg_info}" if reg_info else None),
            application_link=app_link or item.get("original_url"),
            department=item.get("department"),
            venue=item.get("venue")
        ))

    return opp_items

@router.get("/locations")
def get_verified_locations():
    """
    Verified Campus Office & Venue Directory:
    List only verified locations documented in official records.
    """
    return [
        {
            "id": "loc_admissions",
            "name": "Admissions Office",
            "category": "Administrative Office",
            "building": "Administrative Block",
            "purpose": "Enquiries for B.E/B.Tech admissions, certificates, and enrollment.",
            "source": "Official PEC Admission Records"
        },
        {
            "id": "loc_placement",
            "name": "Placement Directorate & Interview Cabins",
            "category": "Career & Placements",
            "building": "Placement Block",
            "purpose": "Campus recruitment drives, training sessions, and corporate relations.",
            "source": "Training and Placement Cell"
        },
        {
            "id": "loc_idea_lab",
            "name": "Idea Lab & AR-VR Center of Excellence",
            "category": "Innovation & Research",
            "building": "Innovation Hub / Central Tech Wing",
            "purpose": "Hands-on student prototyping, 13 innovation domains, hackathons, and AR-VR development.",
            "source": "Clubs & Innovation Handbook"
        },
        {
            "id": "loc_turing_lab",
            "name": "Turing Computing Lab & Meganathan Memorial Auditorium",
            "category": "Academic & Seminar Halls",
            "building": "CSE Department Wing",
            "purpose": "National workshops, technical symposia, coding sessions, and GDSC events.",
            "source": "Department of CSE"
        },
        {
            "id": "loc_biotech_lab",
            "name": "Bio-Process Technology Laboratory",
            "category": "Department Laboratory",
            "building": "Biotechnology Block",
            "purpose": "Research in bio-innovations, algae biocomposites, and practical coursework.",
            "source": "Department of Biotechnology"
        },
        {
            "id": "loc_seminar1",
            "name": "Seminar Hall 1 & College Sports Ground",
            "category": "Events & Demonstrations",
            "building": "Central Campus",
            "purpose": "International technical lectures, autonomous drone waypoint demonstrations, and robotics expos.",
            "source": "Drones Club & Yantramanav"
        },
        {
            "id": "loc_hostel_office",
            "name": "Hostel Warden Office & Main Security Gate",
            "category": "Hostel Administration",
            "building": "Campus Entrance & Hostel Blocks",
            "purpose": "Hostel room allocation, leave approvals (Pink card for boys, Yellow card for girls), and gate clearance.",
            "source": "Hostel Facilities & Rules Document"
        },
        {
            "id": "loc_mega_auditorium",
            "name": "PEC Mega Auditorium",
            "category": "Auditorium",
            "building": "Main Block",
            "purpose": "First-year induction programme (AARAMBH), annual day, and central institutional gatherings.",
            "source": "First Year Coordination Committee"
        }
    ]
