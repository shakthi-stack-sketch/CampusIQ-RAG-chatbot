from datetime import datetime, timezone
import re
from typing import List, Dict, Any, Optional

from backend.app.rag.embeddings import embedding_service
from backend.app.rag.vectorstore import vectorstore_manager

DAYS_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MEAL_TYPES = ["breakfast", "lunch", "snacks", "dinner"]

class CampusRetriever:
    """
    Query-Aware RAG Retriever for CampusIQ:
    - Dedicated full weekly mess menu routing (retrieves all 7 days Monday-Sunday in order)
    - High-precision day and meal metadata filtering
    - Multi-source retrieval (Official Documents, LinkedIn, Instagram, YouTube)
    - Hybrid scoring (Vector Cosine + Lexical Overlap + Temporal Scoring)
    - Clean deduplicated source provenance
    """

    TEMPORAL_KEYWORDS = {
        "latest", "recent", "recently", "this week", "this month",
        "upcoming", "today", "yesterday", "newest", "last event",
        "current", "new"
    }

    def __init__(self, top_k: int = 6):
        self.top_k = top_k

    def has_temporal_intent(self, query: str) -> bool:
        lower_q = query.lower()
        return any(re.search(rf"\b{re.escape(k)}\b", lower_q) for k in self.TEMPORAL_KEYWORDS)

    def detect_mess_menu_intent(self, query: str) -> Dict[str, Any]:
        """Analyze query to detect weekly overview, specific day, and specific meal intents."""
        q_lower = query.lower()

        is_weekly = bool(
            re.search(r"\b(weekly|complete|full|entire|all\s+days|whole|all\s+seven|seven\s+days|week's|week)\b.*\b(menu|mess|food|meals|diet)\b", q_lower) or
            re.search(r"\b(menu|mess)\b.*\b(weekly|complete|full|entire|all\s+days|whole|week)\b", q_lower) or
            "weekly mess menu" in q_lower or
            "complete weekly" in q_lower or
            "full mess menu" in q_lower or
            "entire mess menu" in q_lower or
            "whole mess menu" in q_lower
        )

        detected_day = None
        for d in DAYS_ORDER:
            if re.search(rf"\b{d}\b", q_lower):
                detected_day = d
                break

        detected_meal = None
        for m in ["breakfast", "lunch", "snacks", "snack", "dinner"]:
            if re.search(rf"\b{m}\b", q_lower):
                detected_meal = "snacks" if m == "snack" else m
                break

        is_menu_related = bool(
            is_weekly or
            "mess" in q_lower or
            "menu" in q_lower or
            (detected_day and (detected_meal or any(w in q_lower for w in ["food", "eat", "served", "serving", "item", "items"])))
        )

        return {
            "is_weekly": is_weekly,
            "is_menu_related": is_menu_related,
            "day": detected_day,
            "meal": detected_meal
        }

    def retrieve_full_weekly_menu(self) -> List[Dict[str, Any]]:
        """Retrieve all 7 days of the mess menu strictly ordered Monday to Sunday."""
        # 1. Fetch daily chunks
        daily_points = vectorstore_manager.get_by_filter(
            {"category": "mess_menu", "scope": "daily"},
            limit=25
        )

        # 2. Fetch weekly overview chunk
        overview_points = vectorstore_manager.get_by_filter(
            {"category": "mess_menu", "scope": "weekly_overview"},
            limit=5
        )

        # Organize daily points chronologically
        day_map = {}
        for p in daily_points:
            p_day = p.get("payload", {}).get("day", "").lower()
            if p_day in DAYS_ORDER and p_day not in day_map:
                day_map[p_day] = p

        ordered_results = []
        # Add weekly overview first if present
        for op in overview_points:
            ordered_results.append({
                "id": op["id"],
                "score": 2.5,
                "content": op.get("payload", {}).get("content", ""),
                "metadata": op.get("payload", {})
            })

        # Add all 7 days in order
        for day in DAYS_ORDER:
            if day in day_map:
                p = day_map[day]
                ordered_results.append({
                    "id": p["id"],
                    "score": 2.0,
                    "content": p.get("payload", {}).get("content", ""),
                    "metadata": p.get("payload", {})
                })

        return ordered_results

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve top relevant chunks with query-aware routing."""
        menu_intent = self.detect_mess_menu_intent(query)

        # 1. Full Weekly Mess Menu Routing: Return all 7 days
        if menu_intent["is_weekly"]:
            weekly_docs = self.retrieve_full_weekly_menu()
            if weekly_docs:
                return weekly_docs

        # 2. Day-Specific Mess Menu Routing: High-precision retrieval
        targeted_docs = []
        seen_ids = set()

        if menu_intent["day"] and menu_intent["is_menu_related"]:
            day = menu_intent["day"]
            meal = menu_intent["meal"]

            # If specific meal requested, fetch meal chunk
            if meal:
                meal_hits = vectorstore_manager.get_by_filter(
                    {"category": "mess_menu", "day": day, "meal": meal},
                    limit=2
                )
                for h in meal_hits:
                    if h["id"] not in seen_ids:
                        seen_ids.add(h["id"])
                        targeted_docs.append({
                            "id": h["id"],
                            "score": 3.0,
                            "content": h.get("payload", {}).get("content", ""),
                            "metadata": h.get("payload", {})
                        })

            # Also fetch the daily overview chunk for that day
            day_hits = vectorstore_manager.get_by_filter(
                {"category": "mess_menu", "day": day, "scope": "daily"},
                limit=2
            )
            for h in day_hits:
                if h["id"] not in seen_ids:
                    seen_ids.add(h["id"])
                    targeted_docs.append({
                        "id": h["id"],
                        "score": 2.8,
                        "content": h.get("payload", {}).get("content", ""),
                        "metadata": h.get("payload", {})
                    })

        # 3. Standard Semantic & Hybrid Vector Search
        query_vector = embedding_service.embed_query(query)
        fetch_limit = 20

        hits = vectorstore_manager.search(
            query_vector=query_vector,
            top_k=fetch_limit,
            category=category,
            source_type=source_type
        )

        scored_docs = []
        is_temporal = self.has_temporal_intent(query)
        today = datetime.now(timezone.utc)

        # Extract informative query terms
        q_terms = [t.lower() for t in re.findall(r'\w+', query) if len(t) > 2 and t.lower() not in {
            'what', 'the', 'for', 'is', 'are', 'about', 'can', 'you', 'how', 'when', 'where', 'tell', 'give'
        }]

        for hit in hits:
            hit_id = hit["id"]
            if hit_id in seen_ids:
                continue

            score = float(hit["score"])
            payload = hit.get("payload", {})
            content_lower = payload.get("content", "").lower()
            title_lower = payload.get("title", "").lower()
            doc_category = payload.get("category", "")

            # Lexical keyword overlap bonus
            term_matches = sum(1 for t in q_terms if (t in content_lower or t in title_lower))
            score += term_matches * 0.40

            # Day match bonus
            if menu_intent["day"] and payload.get("day") == menu_intent["day"]:
                score += 1.2

            # Meal match bonus
            if menu_intent["meal"] and payload.get("meal") == menu_intent["meal"]:
                score += 1.5

            # Recency bonus if temporal intent is present
            if is_temporal:
                pub_date_str = payload.get("publication_date") or payload.get("event_date")
                if pub_date_str:
                    try:
                        doc_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                        if doc_date.tzinfo is None:
                            doc_date = doc_date.replace(tzinfo=timezone.utc)
                        days_diff = (today - doc_date).days
                        if days_diff >= 0:
                            recency_bonus = 0.40 / (1.0 + 0.03 * days_diff)
                            score += recency_bonus
                    except Exception:
                        pass

            scored_docs.append({
                "id": hit_id,
                "score": score,
                "content": payload.get("content", ""),
                "metadata": payload
            })

        # Combine targeted docs with scored vector hits
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        combined = targeted_docs + scored_docs

        # Deduplicate
        final_results = []
        retrieved_ids = set()
        for doc in combined:
            if doc["id"] not in retrieved_ids:
                retrieved_ids.add(doc["id"])
                final_results.append(doc)

        limit = max(self.top_k, len(targeted_docs))
        return final_results[:limit]

    def build_context_and_sources(self, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format retrieved documents into structured context and clean provenance sources."""
        from backend.app.rag.url_validator import validate_source_url

        context_parts = []
        sources = []
        seen_keys = set()

        for idx, item in enumerate(retrieved_docs, start=1):
            meta = item.get("metadata", {})
            title = meta.get("document_title") or meta.get("title") or meta.get("source", "Official College Record")
            source_type = meta.get("source_type", "official_document")
            source_platform = meta.get("source_platform", "Official PEC Document")
            pub_date = meta.get("publication_date", "")
            event_date = meta.get("event_date", "")
            raw_url = meta.get("original_url") or meta.get("source_url") or ""
            dept = meta.get("department", "")

            # Validate URL to ensure students only get working, publicly accessible links
            validated_url = validate_source_url(raw_url, platform=source_platform) if raw_url else None

            # Format item context header
            header_elements = [f"[{idx}] SOURCE: {title}"]
            if source_platform:
                header_elements.append(f"PLATFORM: {source_platform.upper()}")
            if meta.get("day_title"):
                header_elements.append(f"DAY: {meta.get('day_title').upper()}")
            if meta.get("meal"):
                header_elements.append(f"MEAL: {meta.get('meal').upper()}")
            if pub_date:
                header_elements.append(f"PUBLISHED: {pub_date}")
            if event_date:
                header_elements.append(f"EVENT DATE: {event_date}")
            if dept:
                header_elements.append(f"DEPARTMENT: {dept}")

            header_line = " | ".join(header_elements)
            context_parts.append(f"{header_line}\nCONTENT:\n{item.get('content', '').strip()}\n")

            # Collect clean source provenance (deduplicated)
            source_key = validated_url if validated_url else title
            if source_key not in seen_keys:
                seen_keys.add(source_key)
                sources.append({
                    "title": title,
                    "platform": source_platform,
                    "type": source_type,
                    "url": validated_url,
                    "publication_date": pub_date,
                    "event_date": event_date,
                    "department": dept
                })

        return {
            "context_str": "\n----------------------------------------\n".join(context_parts),
            "sources": sources
        }

campus_retriever = CampusRetriever(top_k=6)
