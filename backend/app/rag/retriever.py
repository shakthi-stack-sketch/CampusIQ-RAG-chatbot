from datetime import datetime, timezone
import re
from typing import List, Dict, Any, Optional

from backend.app.rag.embeddings import embedding_service
from backend.app.rag.vectorstore import vectorstore_manager


DAYS_ORDER = [
    "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday"
]

MEAL_TYPES = ["breakfast", "lunch", "snacks", "dinner"]


class CampusRetriever:
    """
    CampusIQ Query-Aware RAG Retriever.

    Retrieval strategy:
    1. Structured routing for known campus categories.
    2. Special complete-week retrieval for mess menu.
    3. Category-wide retrieval for broad questions such as
       dress code and bus timings.
    4. Semantic + lexical retrieval for normal questions.
    5. Deduplication and source provenance.
    """

    TEMPORAL_KEYWORDS = {
        "latest",
        "recent",
        "recently",
        "this week",
        "this month",
        "upcoming",
        "today",
        "yesterday",
        "newest",
        "last event",
        "current",
        "new",
    }

    # ---------------------------------------------------------
    # CATEGORY INTENT ROUTING
    # ---------------------------------------------------------

    CATEGORY_INTENTS = {
        "dress_code": [
            "dress code",
            "dress",
            "attire",
            "uniform",
            "clothing",
            "what to wear",
            "wear to college",
            "wear in college",
        ],

        "transportation": [
            "bus",
            "bus timing",
            "bus timings",
            "bus time",
            "bus route",
            "bus routes",
            "transport",
            "transportation",
            "college bus",
            "college buses",
            "boarding",
            "pickup",
            "pick up",
            "drop",
            "bus stop",
        ],
    }

    def __init__(self, top_k: int = 6):
        self.top_k = top_k

    # ---------------------------------------------------------
    # TEMPORAL INTENT
    # ---------------------------------------------------------

    def has_temporal_intent(self, query: str) -> bool:
        lower_q = query.lower()

        return any(
            re.search(rf"\b{re.escape(keyword)}\b", lower_q)
            for keyword in self.TEMPORAL_KEYWORDS
        )

    # ---------------------------------------------------------
    # STRUCTURED CATEGORY DETECTION
    # ---------------------------------------------------------

    def detect_category_intent(self, query: str) -> Optional[str]:
        """
        Detects whether a question clearly belongs to a
        structured campus category.

        Returns:
            dress_code
            transportation
            None
        """

        q = query.lower().strip()

        for category, keywords in self.CATEGORY_INTENTS.items():

            for keyword in keywords:

                # Phrase matching for multi-word keywords
                if " " in keyword:
                    if keyword in q:
                        return category

                # Word-boundary matching for single words
                else:
                    if re.search(rf"\b{re.escape(keyword)}\b", q):
                        return category

        return None

    # ---------------------------------------------------------
    # MESS MENU INTENT
    # ---------------------------------------------------------

    def detect_mess_menu_intent(
        self,
        query: str
    ) -> Dict[str, Any]:

        q_lower = query.lower()

        is_weekly = bool(
            re.search(
                r"\b(weekly|complete|full|entire|all\s+days|whole|"
                r"all\s+seven|seven\s+days|week's|week)\b.*"
                r"\b(menu|mess|food|meals|diet)\b",
                q_lower
            )
            or
            re.search(
                r"\b(menu|mess)\b.*"
                r"\b(weekly|complete|full|entire|all\s+days|whole|week)\b",
                q_lower
            )
            or "weekly mess menu" in q_lower
            or "complete weekly" in q_lower
            or "full mess menu" in q_lower
            or "entire mess menu" in q_lower
            or "whole mess menu" in q_lower
        )

        detected_day = None

        for day in DAYS_ORDER:
            if re.search(rf"\b{day}\b", q_lower):
                detected_day = day
                break

        detected_meal = None

        for meal in [
            "breakfast",
            "lunch",
            "snacks",
            "snack",
            "dinner"
        ]:
            if re.search(rf"\b{meal}\b", q_lower):
                detected_meal = (
                    "snacks" if meal == "snack" else meal
                )
                break

        is_menu_related = bool(
            is_weekly
            or "mess" in q_lower
            or "menu" in q_lower
            or (
                detected_day
                and (
                    detected_meal
                    or any(
                        word in q_lower
                        for word in [
                            "food",
                            "eat",
                            "served",
                            "serving",
                            "item",
                            "items",
                        ]
                    )
                )
            )
        )

        return {
            "is_weekly": is_weekly,
            "is_menu_related": is_menu_related,
            "day": detected_day,
            "meal": detected_meal,
        }

    # ---------------------------------------------------------
    # FULL WEEKLY MENU
    # ---------------------------------------------------------

    def retrieve_full_weekly_menu(
        self
    ) -> List[Dict[str, Any]]:

        daily_points = vectorstore_manager.get_by_filter(
            {
                "category": "mess_menu",
                "scope": "daily",
            },
            limit=25,
        )

        overview_points = vectorstore_manager.get_by_filter(
            {
                "category": "mess_menu",
                "scope": "weekly_overview",
            },
            limit=5,
        )

        day_map = {}

        for point in daily_points:

            payload = point.get("payload", {})

            day = payload.get("day", "").lower()

            if day in DAYS_ORDER and day not in day_map:
                day_map[day] = point

        ordered_results = []

        # Weekly overview first
        for point in overview_points:

            payload = point.get("payload", {})

            ordered_results.append(
                {
                    "id": point["id"],
                    "score": 2.5,
                    "content": payload.get("content", ""),
                    "metadata": payload,
                }
            )

        # Monday → Sunday
        for day in DAYS_ORDER:

            if day in day_map:

                point = day_map[day]

                payload = point.get("payload", {})

                ordered_results.append(
                    {
                        "id": point["id"],
                        "score": 2.0,
                        "content": payload.get("content", ""),
                        "metadata": payload,
                    }
                )

        print(
            f"[Retriever] Weekly mess route: "
            f"{len(ordered_results)} chunks retrieved."
        )

        return ordered_results

    # ---------------------------------------------------------
    # CATEGORY-WIDE RETRIEVAL
    # ---------------------------------------------------------

    def retrieve_category_documents(
        self,
        category: str,
        query: str,
        source_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves ALL relevant chunks from a structured category.

        This is important for questions such as:

        "What is the dress code?"

        "What are all the bus timings?"

        Instead of asking Qdrant for only the top few semantic
        matches, we retrieve the complete category so important
        routes/rules are not lost.
        """

        points = vectorstore_manager.get_by_filter(
            {
                "category": category,
            },
            limit=100,
        )

        results = []

        query_terms = [
            term.lower()
            for term in re.findall(r"\w+", query)
            if len(term) > 2
            and term.lower()
            not in {
                "what",
                "the",
                "for",
                "is",
                "are",
                "about",
                "can",
                "you",
                "how",
                "when",
                "where",
                "tell",
                "give",
                "please",
            }
        ]

        for point in points:

            payload = point.get("payload", {})

            if source_type:
                if payload.get("source_type") != source_type:
                    continue

            content = payload.get("content", "")
            title = payload.get("title", "")
            document_title = payload.get(
                "document_title",
                ""
            )

            searchable_text = (
                f"{title} "
                f"{document_title} "
                f"{content}"
            ).lower()

            lexical_matches = sum(
                1
                for term in query_terms
                if term in searchable_text
            )

            # Base score ensures every category document
            # remains available, while lexical matches
            # determine ordering.
            score = 1.0 + (
                lexical_matches * 0.35
            )

            results.append(
                {
                    "id": point["id"],
                    "score": score,
                    "content": content,
                    "metadata": payload,
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        print(
            f"[Retriever] Structured category route: "
            f"{category} → {len(results)} chunks."
        )

        return results

    # ---------------------------------------------------------
    # DAY / MEAL TARGETED MENU RETRIEVAL
    # ---------------------------------------------------------

    def retrieve_menu_targeted(
        self,
        menu_intent: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        targeted_docs = []
        seen_ids = set()

        day = menu_intent.get("day")
        meal = menu_intent.get("meal")

        if not day:
            return targeted_docs

        if meal:

            meal_hits = vectorstore_manager.get_by_filter(
                {
                    "category": "mess_menu",
                    "day": day,
                    "meal": meal,
                },
                limit=5,
            )

            for hit in meal_hits:

                if hit["id"] in seen_ids:
                    continue

                seen_ids.add(hit["id"])

                payload = hit.get("payload", {})

                targeted_docs.append(
                    {
                        "id": hit["id"],
                        "score": 3.0,
                        "content": payload.get(
                            "content",
                            ""
                        ),
                        "metadata": payload,
                    }
                )

        day_hits = vectorstore_manager.get_by_filter(
            {
                "category": "mess_menu",
                "day": day,
                "scope": "daily",
            },
            limit=5,
        )

        for hit in day_hits:

            if hit["id"] in seen_ids:
                continue

            seen_ids.add(hit["id"])

            payload = hit.get("payload", {})

            targeted_docs.append(
                {
                    "id": hit["id"],
                    "score": 2.8,
                    "content": payload.get(
                        "content",
                        ""
                    ),
                    "metadata": payload,
                }
            )

        return targeted_docs

    # ---------------------------------------------------------
    # MAIN RETRIEVAL
    # ---------------------------------------------------------

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        # -----------------------------------------------------
        # 1. MESS MENU
        # -----------------------------------------------------

        menu_intent = self.detect_mess_menu_intent(query)

        if menu_intent["is_weekly"]:

            weekly_docs = self.retrieve_full_weekly_menu()

            if weekly_docs:
                return weekly_docs

        # -----------------------------------------------------
        # 2. STRUCTURED CATEGORY ROUTING
        # -----------------------------------------------------

        detected_category = self.detect_category_intent(query)

        # Explicit category passed by caller takes priority.
        if category:
            detected_category = category

        if detected_category in {
            "dress_code",
            "transportation",
        }:

            category_docs = self.retrieve_category_documents(
                category=detected_category,
                query=query,
                source_type=source_type,
            )

            if category_docs:
                return category_docs

        # -----------------------------------------------------
        # 3. TARGETED MENU QUESTION
        # -----------------------------------------------------

        targeted_docs = self.retrieve_menu_targeted(
            menu_intent
        )

        # -----------------------------------------------------
        # 4. NORMAL SEMANTIC SEARCH
        # -----------------------------------------------------

        query_vector = embedding_service.embed_query(query)

        fetch_limit = 20

        hits = vectorstore_manager.search(
            query_vector=query_vector,
            top_k=fetch_limit,
            category=category,
            source_type=source_type,
        )

        scored_docs = []

        seen_ids = {
            doc["id"]
            for doc in targeted_docs
        }

        is_temporal = self.has_temporal_intent(query)

        today = datetime.now(timezone.utc)

        query_terms = [
            term.lower()
            for term in re.findall(
                r"\w+",
                query
            )
            if len(term) > 2
            and term.lower()
            not in {
                "what",
                "the",
                "for",
                "is",
                "are",
                "about",
                "can",
                "you",
                "how",
                "when",
                "where",
                "tell",
                "give",
            }
        ]

        for hit in hits:

            hit_id = hit["id"]

            if hit_id in seen_ids:
                continue

            payload = hit.get(
                "payload",
                {}
            )

            content = payload.get(
                "content",
                ""
            )

            title = payload.get(
                "title",
                ""
            )

            content_lower = content.lower()
            title_lower = title.lower()

            score = float(
                hit.get("score", 0)
            )

            # Lexical relevance
            term_matches = sum(
                1
                for term in query_terms
                if (
                    term in content_lower
                    or term in title_lower
                )
            )

            score += (
                term_matches * 0.40
            )

            # Menu day / meal relevance
            if (
                menu_intent.get("day")
                and payload.get("day")
                == menu_intent["day"]
            ):
                score += 1.2

            if (
                menu_intent.get("meal")
                and payload.get("meal")
                == menu_intent["meal"]
            ):
                score += 1.5

            # Temporal relevance
            if is_temporal:

                publication_date = payload.get(
                    "publication_date"
                )

                event_date = payload.get(
                    "event_date"
                )

                date_string = (
                    publication_date
                    or event_date
                )

                if date_string:

                    try:

                        document_date = (
                            datetime.fromisoformat(
                                date_string.replace(
                                    "Z",
                                    "+00:00"
                                )
                            )
                        )

                        if (
                            document_date.tzinfo
                            is None
                        ):
                            document_date = (
                                document_date.replace(
                                    tzinfo=timezone.utc
                                )
                            )

                        days_difference = (
                            today
                            - document_date
                        ).days

                        if days_difference >= 0:

                            recency_bonus = (
                                0.40
                                / (
                                    1.0
                                    + 0.03
                                    * days_difference
                                )
                            )

                            score += (
                                recency_bonus
                            )

                    except Exception:
                        pass

            scored_docs.append(
                {
                    "id": hit_id,
                    "score": score,
                    "content": content,
                    "metadata": payload,
                }
            )

        scored_docs.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        # -----------------------------------------------------
        # 5. COMBINE TARGETED + SEMANTIC RESULTS
        # -----------------------------------------------------

        combined = (
            targeted_docs
            + scored_docs
        )

        final_results = []

        retrieved_ids = set()

        for document in combined:

            document_id = document["id"]

            if document_id in retrieved_ids:
                continue

            retrieved_ids.add(
                document_id
            )

            final_results.append(
                document
            )

        limit = max(
            self.top_k,
            len(targeted_docs)
        )

        return final_results[:limit]

    # ---------------------------------------------------------
    # CONTEXT + SOURCE PROVENANCE
    # ---------------------------------------------------------

    def build_context_and_sources(
        self,
        retrieved_docs: List[
            Dict[str, Any]
        ],
    ) -> Dict[str, Any]:

        from backend.app.rag.url_validator import (
            validate_source_url
        )

        context_parts = []
        sources = []
        seen_keys = set()

        for index, item in enumerate(
            retrieved_docs,
            start=1,
        ):

            metadata = item.get(
                "metadata",
                {}
            )

            title = (
                metadata.get(
                    "document_title"
                )
                or metadata.get(
                    "title"
                )
                or metadata.get(
                    "source",
                    "Official College Record"
                )
            )

            source_type = metadata.get(
                "source_type",
                "official_document",
            )

            source_platform = metadata.get(
                "source_platform",
                "Official PEC Document",
            )

            publication_date = metadata.get(
                "publication_date",
                "",
            )

            event_date = metadata.get(
                "event_date",
                "",
            )

            raw_url = (
                metadata.get(
                    "original_url"
                )
                or metadata.get(
                    "source_url"
                )
                or ""
            )

            department = metadata.get(
                "department",
                "",
            )

            validated_url = (
                validate_source_url(
                    raw_url,
                    platform=source_platform,
                )
                if raw_url
                else None
            )

            header_elements = [
                f"[{index}] SOURCE: {title}"
            ]

            if source_platform:
                header_elements.append(
                    "PLATFORM: "
                    + source_platform.upper()
                )

            if metadata.get(
                "day_title"
            ):
                header_elements.append(
                    "DAY: "
                    + metadata.get(
                        "day_title"
                    ).upper()
                )

            if metadata.get(
                "meal"
            ):
                header_elements.append(
                    "MEAL: "
                    + metadata.get(
                        "meal"
                    ).upper()
                )

            if publication_date:
                header_elements.append(
                    "PUBLISHED: "
                    + publication_date
                )

            if event_date:
                header_elements.append(
                    "EVENT DATE: "
                    + event_date
                )

            if department:
                header_elements.append(
                    "DEPARTMENT: "
                    + department
                )

            header_line = " | ".join(
                header_elements
            )

            context_parts.append(
                f"{header_line}\n"
                f"CONTENT:\n"
                f"{item.get('content', '').strip()}\n"
            )

            source_key = (
                validated_url
                if validated_url
                else title
            )

            if source_key not in seen_keys:

                seen_keys.add(
                    source_key
                )

                sources.append(
                    {
                        "title": title,
                        "platform": source_platform,
                        "type": source_type,
                        "url": validated_url,
                        "publication_date": publication_date,
                        "event_date": event_date,
                        "department": department,
                    }
                )

        return {
            "context_str": (
                "\n"
                "----------------------------------------"
                "\n"
                .join(context_parts)
            ),
            "sources": sources,
        }


campus_retriever = CampusRetriever(
    top_k=6
)