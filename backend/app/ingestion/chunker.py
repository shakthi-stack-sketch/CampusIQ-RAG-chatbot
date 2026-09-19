import re
from typing import List, Dict, Any

DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MEALS = ["breakfast", "lunch", "snacks", "dinner"]

def parse_mess_menu_chunks(text: str, base_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Hierarchical structure-aware chunking for the Hostel Mess Menu.
    Extracts Month, Title, Day, Meal, and Item hierarchy.
    Produces:
    1. Daily chunks (all meals for each of the 7 days)
    2. Meal-level chunks (day + specific meal for high-precision queries)
    3. Full weekly summary chunk (for holistic weekly queries)
    """
    chunks = []
    doc_title = base_meta.get("title", "Hostel Mess Menu – July 2026")
    month_match = re.search(r"(\b[A-Za-z]+\s+20\d\d\b)", text)
    month_str = month_match.group(1) if month_match else "July 2026"

    # Split by day headers: ====================\nDAY\n====================
    divider_regex = r"\n\s*={4,}\s*\n([A-Z0-9\s—–-]+)\n\s*={4,}\s*\n"
    parts = re.split(divider_regex, text)

    daily_sections: Dict[str, Dict[str, str]] = {}
    
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            sec_name = parts[i].strip().lower()
            sec_content = parts[i+1].strip() if i+1 < len(parts) else ""
            
            # Match day
            matched_day = None
            for d in DAYS_OF_WEEK:
                if d in sec_name:
                    matched_day = d
                    break
            
            if not matched_day:
                continue

            # Parse meals within this day
            # Patterns like BREAKFAST:\n- item...
            meal_pattern = r"(BREAKFAST|LUNCH|SNACKS|DINNER)\s*:\s*\n(.*?)(?=(?:BREAKFAST|LUNCH|SNACKS|DINNER)\s*:|$)"
            meal_matches = re.findall(meal_pattern, sec_content, flags=re.DOTALL | re.IGNORECASE)
            
            day_meals: Dict[str, str] = {}
            for m_name, m_items in meal_matches:
                day_meals[m_name.strip().lower()] = m_items.strip()
            
            daily_sections[matched_day] = day_meals

    # 1. Create Daily Chunks (Contains all 4 meals for the day)
    for day in DAYS_OF_WEEK:
        if day in daily_sections:
            day_meals = daily_sections[day]
            day_title = day.capitalize()
            
            body_parts = [
                f"PRATHYUSHA ENGINEERING COLLEGE",
                f"DOCUMENT: {doc_title}",
                f"CATEGORY: Hostel Mess Menu",
                f"MONTH: {month_str}",
                f"DAY: {day_title.upper()}",
                f"AVAILABLE MEALS: Breakfast, Lunch, Snacks, Dinner\n"
            ]
            
            for m in MEALS:
                if m in day_meals:
                    body_parts.append(f"{m.upper()}:\n{day_meals[m]}\n")
            
            daily_text = "\n".join(body_parts)
            daily_meta = dict(base_meta)
            daily_meta.update({
                "category": "mess_menu",
                "document_type": "official_document",
                "document_title": doc_title,
                "month": month_str,
                "day": day,
                "day_title": day_title,
                "meals": list(day_meals.keys()),
                "scope": "daily"
            })
            chunks.append({
                "content": daily_text,
                "metadata": daily_meta
            })

            # 2. Create Meal-Specific Chunks for fine-grained retrieval
            for m in MEALS:
                if m in day_meals:
                    m_title = m.capitalize()
                    meal_text = (
                        f"PRATHYUSHA ENGINEERING COLLEGE\n"
                        f"DOCUMENT: {doc_title}\n"
                        f"CATEGORY: Hostel Mess Menu\n"
                        f"MONTH: {month_str}\n"
                        f"DAY: {day_title.upper()}\n"
                        f"MEAL: {m_title.upper()}\n\n"
                        f"{day_title} {m_title} Menu Items:\n"
                        f"{day_meals[m]}"
                    )
                    meal_meta = dict(base_meta)
                    meal_meta.update({
                        "category": "mess_menu",
                        "document_type": "official_document",
                        "document_title": doc_title,
                        "month": month_str,
                        "day": day,
                        "day_title": day_title,
                        "meal": m,
                        "scope": "meal"
                    })
                    chunks.append({
                        "content": meal_text,
                        "metadata": meal_meta
                    })

    # 3. Create Full Weekly Overview Chunk
    weekly_summary_lines = [
        f"PRATHYUSHA ENGINEERING COLLEGE",
        f"DOCUMENT: {doc_title}",
        f"CATEGORY: Hostel Mess Menu",
        f"MONTH: {month_str}",
        f"SCOPE: Complete Weekly Mess Menu (Monday to Sunday)\n"
    ]
    for day in DAYS_OF_WEEK:
        if day in daily_sections:
            day_meals = daily_sections[day]
            weekly_summary_lines.append(f"=== {day.upper()} ===")
            for m in MEALS:
                if m in day_meals:
                    items_single_line = ", ".join(line.lstrip("- ").strip() for line in day_meals[m].split("\n") if line.strip())
                    weekly_summary_lines.append(f"{m.capitalize()}: {items_single_line}")
            weekly_summary_lines.append("")

    weekly_text = "\n".join(weekly_summary_lines)
    weekly_meta = dict(base_meta)
    weekly_meta.update({
        "category": "mess_menu",
        "document_type": "official_document",
        "document_title": doc_title,
        "month": month_str,
        "scope": "weekly_overview",
        "days": DAYS_OF_WEEK
    })
    chunks.append({
        "content": weekly_text,
        "metadata": weekly_meta
    })

    return chunks

def chunk_text(text: str, chunk_size: int = 750, overlap: int = 100) -> List[str]:
    """
    Split text along section boundaries while preserving headings and lists.
    Recognizes major dividers (e.g. === MONDAY ===, SECTION HEADERS) and keeps them with their content.
    """
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    # Split by section dividers: ==================== \n TITLE \n ====================
    divider_regex = r"\n\s*={4,}\s*\n([A-Z0-9\s—–-]+)\n\s*={4,}\s*\n"
    parts = re.split(divider_regex, text)
    if len(parts) > 1:
        chunks = []
        preamble = parts[0].strip()
        if preamble:
            chunks.append(preamble)
        for i in range(1, len(parts), 2):
            sec_title = parts[i].strip()
            sec_content = parts[i+1].strip() if i+1 < len(parts) else ""
            combined = f"SECTION: {sec_title}\n\n{sec_content}"
            if len(combined) <= chunk_size * 1.5:
                chunks.append(combined)
            else:
                chunks.extend(chunk_text(combined, chunk_size=chunk_size, overlap=overlap))
        return chunks

    # Split by double newlines or uppercase headers
    paragraphs = re.split(r"\n{2,}", text)
    chunks = []
    current_chunk = []
    current_len = 0
    active_header = ""

    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            continue

        is_header = bool(re.match(r"^[A-Z0-9\s—–:-]{3,60}$", para_clean)) and len(para_clean.split("\n")) == 1
        if is_header:
            active_header = para_clean

        para_to_add = f"SECTION: {active_header}\n{para_clean}" if (active_header and not is_header and not para_clean.startswith("SECTION:")) else para_clean

        if current_len + len(para_to_add) <= chunk_size:
            current_chunk.append(para_to_add)
            current_len += len(para_to_add)
        else:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [para_to_add]
            current_len = len(para_to_add)

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks

def process_and_chunk_all(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process raw document and social media items into structured, enriched chunks.
    Preserves hierarchical metadata: document title, category, day, meal, month, platform.
    """
    processed_chunks = []
    for item in raw_items:
        content = item.get("content", "").strip()
        meta = item.get("metadata", {})
        source_type = meta.get("source_type", "document")
        title = meta.get("title", meta.get("source", "College Document"))
        category = meta.get("category", "")

        # 1. Specialized hierarchical processing for Hostel Mess Menu
        if category == "mess_menu" or "mess_menu" in str(meta.get("source", "")).lower():
            menu_chunks = parse_mess_menu_chunks(content, meta)
            processed_chunks.extend(menu_chunks)
            continue

        # 2. Keep social media records intact so event/speaker/venue info stays together
        if source_type == "social_media" or len(content) < 800:
            header_prefix = f"DOCUMENT: {title}\nCATEGORY: {category.replace('_', ' ').title()}\n\n"
            final_content = content if content.startswith("DOCUMENT:") or content.startswith("TITLE:") else f"{header_prefix}{content}"
            chunk_meta = dict(meta)
            chunk_meta["document_title"] = title
            processed_chunks.append({
                "content": final_content,
                "metadata": chunk_meta
            })
        else:
            # 3. Chunk longer documents structurally
            header_prefix = f"DOCUMENT: {title}\nCATEGORY: {category.replace('_', ' ').title()}\n\n"
            text_chunks = chunk_text(content, chunk_size=750, overlap=100)
            for idx, ch in enumerate(text_chunks):
                chunk_meta = dict(meta)
                chunk_meta["chunk_index"] = idx
                chunk_meta["document_title"] = title
                chunk_content = ch if ch.startswith("DOCUMENT:") or ch.startswith("SECTION:") else f"{header_prefix}{ch}"
                processed_chunks.append({
                    "content": chunk_content,
                    "metadata": chunk_meta
                })

    print(f"[Chunker] Produced {len(processed_chunks)} final knowledge chunks with enriched metadata.")
    return processed_chunks

