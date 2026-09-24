from datetime import datetime, timezone
import re
from typing import List, Dict, Any, Optional

from backend.app.rag.embeddings import embedding_service
from backend.app.rag.vectorstore import vectorstore_manager


DAYS_ORDER = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

MEAL_TYPES = [
    "breakfast",
    "lunch",
    "snacks",
    "dinner",
]


class CampusRetriever:
    """
    Query-aware RAG retriever for CampusIQ.

    Retrieval priority:

    1. Normalize the user's question.
    2. Detect structured intent.
    3. Use exact Qdrant filtering for mess-menu questions.
    4. Never mix unrelated semantic results into exact menu queries.
    5. Use structured retrieval for dress code / transportation.
    6. Use semantic + lexical retrieval for normal questions.
    7. Preserve source metadata and provenance.
    """

    # ---------------------------------------------------------
    # TEMPORAL KEYWORDS
    # ---------------------------------------------------------

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
    # QUERY ALIASES
    # ---------------------------------------------------------

    QUERY_ALIASES = {

        # -------------------------
        # Mess / Menu
        # -------------------------

        "mess menue": "mess menu",
        "mess menuu": "mess menu",
        "hostel mess": "mess",
        "hostel food": "mess food",
        "mess food": "mess food",
        "mess meal": "mess meals",
        "mess meals": "mess meals",
        "food menu": "menu",
        "meal menu": "menu",
        "dining menu": "menu",

        # -------------------------
        # Breakfast
        # -------------------------

        "break fast": "breakfast",
        "brekfast": "breakfast",
        "brakfast": "breakfast",
        "morning food": "breakfast",
        "morning meal": "breakfast",

        # -------------------------
        # Lunch
        # -------------------------

        "afternoon food": "lunch",
        "afternoon meal": "lunch",
        "noon food": "lunch",
        "noon meal": "lunch",

        # -------------------------
        # Snacks
        # -------------------------

        "snack": "snacks",
        "evening snack": "snacks",
        "evening snacks": "snacks",
        "tea time": "snacks",
        "tea time food": "snacks",

        # -------------------------
        # Dinner
        # -------------------------

        "diner": "dinner",
        "night food": "dinner",
        "night meal": "dinner",

        # -------------------------
        # Dress Code
        # -------------------------

        "dress kode": "dress code",
        "dresscode": "dress code",
        "dress rules": "dress code",
        "clothing rules": "dress code",
        "clothes rules": "dress code",
        "what to wear": "attire",

        # -------------------------
        # Transportation
        # -------------------------

        "bus timing": "bus timings",
        "bus time": "bus timings",
        "bus timming": "bus timings",
        "bus timmings": "bus timings",
        "bus route": "bus routes",
        "college buses": "college bus",
    }

    # ---------------------------------------------------------
    # COMMON SPELLING CORRECTIONS
    # ---------------------------------------------------------

    SPELLING_ALIASES = {

        "menue": "menu",
        "menues": "menus",
        "menuu": "menu",
        "menuee": "menu",

        "messs": "mess",

        "kode": "code",

        "timming": "timing",
        "timmings": "timings",
        "timng": "timing",

        "acadmic": "academic",
        "acadamics": "academics",

        "calender": "calendar",
        "calandar": "calendar",

        "transporation": "transportation",
        "transpotation": "transportation",

        "breakfasts": "breakfast",

        "diner": "dinner",

        "snak": "snack",
        "snaks": "snacks",
        "snakcs": "snacks",

        "foood": "food",
    }

    # ---------------------------------------------------------
    # DAY ALIASES
    # ---------------------------------------------------------

    DAY_ALIASES = {

        "mon": "monday",
        "monday": "monday",

        "tue": "tuesday",
        "tues": "tuesday",
        "tuesday": "tuesday",

        "wed": "wednesday",
        "weds": "wednesday",
        "wednesday": "wednesday",

        "thu": "thursday",
        "thur": "thursday",
        "thurs": "thursday",
        "thursday": "thursday",

        "fri": "friday",
        "friday": "friday",

        "sat": "saturday",
        "saturday": "saturday",

        "sun": "sunday",
        "sunday": "sunday",
    }

    # ---------------------------------------------------------
    # CATEGORY INTENTS
    # ---------------------------------------------------------

    CATEGORY_INTENTS = {

        "dress_code": [
            "dress code",
            "dress",
            "attire",
            "uniform",
            "clothing",
            "clothes",
            "dress rules",
            "clothing rules",
            "what to wear",
            "wear to college",
            "wear in college",
            "college dress",
            "college attire",
            "allowed clothes",
            "clothes allowed",
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
            "transport schedule",
        ],
    }

    # ---------------------------------------------------------
    # STOP WORDS
    # ---------------------------------------------------------

    STOP_WORDS = {
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
        "show",
        "me",
        "could",
        "would",
        "do",
        "they",
        "does",
        "there",
        "want",
        "know",
        "college",
        "prathyusha",
    }

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(
        self,
        top_k: int = 6,
    ):
        self.top_k = top_k

    # =========================================================
    # QUERY NORMALIZATION
    # =========================================================

    def normalize_query(
        self,
        query: str,
    ) -> str:

        if not query:
            return ""

        normalized = str(
            query
        ).lower().strip()

        normalized = re.sub(
            r"[!?;,]+",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        ).strip()

        # -----------------------------------------------------
        # Day abbreviations
        # -----------------------------------------------------

        for source, target in sorted(
            self.DAY_ALIASES.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):

            if source != target:

                normalized = re.sub(
                    rf"\b{re.escape(source)}\b",
                    target,
                    normalized,
                )

        # -----------------------------------------------------
        # Phrase aliases
        # -----------------------------------------------------

        for source, target in sorted(
            self.QUERY_ALIASES.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):

            normalized = re.sub(
                rf"\b{re.escape(source)}\b",
                target,
                normalized,
            )

        # -----------------------------------------------------
        # Word-level spelling corrections
        # -----------------------------------------------------

        words = normalized.split()

        corrected_words = []

        for word in words:

            corrected_words.append(
                self.SPELLING_ALIASES.get(
                    word,
                    word,
                )
            )

        normalized = " ".join(
            corrected_words
        )

        return re.sub(
            r"\s+",
            " ",
            normalized,
        ).strip()

    # =========================================================
    # TEMPORAL INTENT
    # =========================================================

    def has_temporal_intent(
        self,
        query: str,
    ) -> bool:

        q = self.normalize_query(
            query
        )

        return any(
            re.search(
                rf"\b{re.escape(keyword)}\b",
                q,
            )
            for keyword in self.TEMPORAL_KEYWORDS
        )

    # =========================================================
    # CATEGORY DETECTION
    # =========================================================

    def detect_category_intent(
        self,
        query: str,
    ) -> Optional[str]:

        q = self.normalize_query(
            query
        )

        for category, keywords in (
            self.CATEGORY_INTENTS.items()
        ):

            for keyword in keywords:

                keyword = self.normalize_query(
                    keyword
                )

                if " " in keyword:

                    if keyword in q:
                        return category

                else:

                    if re.search(
                        rf"\b{re.escape(keyword)}\b",
                        q,
                    ):
                        return category

        return None

    # =========================================================
    # DAY DETECTION
    # =========================================================

    def _detect_day(
        self,
        query: str,
    ) -> Optional[str]:

        for day in DAYS_ORDER:

            if re.search(
                rf"\b{day}\b",
                query,
            ):
                return day

        return None

    # =========================================================
    # MEAL DETECTION
    # =========================================================

    def _detect_meal(
        self,
        query: str,
    ) -> Optional[str]:

        meal_patterns = {

            "breakfast": [
                r"\bbreakfast\b",
                r"\bmorning\s+(?:food|meal)\b",
            ],

            "lunch": [
                r"\blunch\b",
                r"\bafternoon\s+(?:food|meal)\b",
                r"\bnoon\s+(?:food|meal)\b",
            ],

            "snacks": [
                r"\bsnacks?\b",
                r"\bevening\s+snacks?\b",
                r"\btea\s+time(?:\s+food)?\b",
            ],

            "dinner": [
                r"\bdinner\b",
                r"\bnight\s+(?:food|meal)\b",
            ],
        }

        for meal, patterns in (
            meal_patterns.items()
        ):

            for pattern in patterns:

                if re.search(
                    pattern,
                    query,
                ):
                    return meal

        return None

    # =========================================================
    # MESS MENU INTENT
    # =========================================================

    def detect_mess_menu_intent(
        self,
        query: str,
    ) -> Dict[str, Any]:

        q = self.normalize_query(
            query
        )

        day = self._detect_day(
            q
        )

        meal = self._detect_meal(
            q
        )

        has_mess = bool(
            re.search(
                r"\bmess\b",
                q,
            )
        )

        has_menu = bool(
            re.search(
                r"\bmenus?\b",
                q,
            )
        )

        food_terms = [
            "food",
            "meal",
            "meals",
            "served",
            "serve",
            "serving",
            "eat",
            "eating",
            "available",
            "dish",
            "dishes",
        ]

        has_food_context = any(
            re.search(
                rf"\b{re.escape(term)}\b",
                q,
            )
            for term in food_terms
        )

        explicit_full_language = bool(
            re.search(
                r"\b(?:weekly|complete|full|entire|whole|"
                r"all\s+days|all\s+seven|seven\s+days|week)\b",
                q,
            )
        )

        # Examples:
        # "What is for Monday?"
        # "What do they serve Monday?"
        day_question = bool(
            day
            and (
                has_food_context
                or re.search(
                    r"\bwhat\s+(?:is|are)\s+(?:for|on)\b",
                    q,
                )
                or re.search(
                    r"\bwhat\s+do\s+they\s+(?:serve|have|eat)\b",
                    q,
                )
            )
        )

        # Broad menu query.
        generic_menu = bool(
            not day
            and not meal
            and (
                has_menu
                or (
                    has_mess
                    and has_food_context
                )
                or (
                    has_mess
                    and explicit_full_language
                )
            )
        )

        is_weekly = bool(
            generic_menu
            or (
                explicit_full_language
                and (
                    has_menu
                    or has_mess
                    or has_food_context
                )
                and not day
                and not meal
            )
        )

        is_menu_related = bool(
            is_weekly
            or has_mess
            or has_menu
            or meal
            or day_question
            or (
                day
                and has_food_context
            )
        )

        return {
            "is_weekly": is_weekly,
            "is_menu_related": is_menu_related,
            "day": day,
            "meal": meal,
        }

    # =========================================================
    # RESULT BUILDER
    # =========================================================

    @staticmethod
    def _result_from_point(
        point: Dict[str, Any],
        score: float,
    ) -> Dict[str, Any]:

        payload = point.get(
            "payload",
            {},
        )

        return {
            "id": point["id"],
            "score": score,
            "content": payload.get(
                "content",
                "",
            ),
            "metadata": payload,
        }

    # =========================================================
    # FULL WEEKLY MENU
    # =========================================================

    def retrieve_full_weekly_menu(
        self,
    ) -> List[Dict[str, Any]]:

        daily_points = (
            vectorstore_manager.get_by_filter(
                {
                    "category": "mess_menu",
                    "scope": "daily",
                },
                limit=100,
            )
        )

        overview_points = (
            vectorstore_manager.get_by_filter(
                {
                    "category": "mess_menu",
                    "scope": "weekly_overview",
                },
                limit=10,
            )
        )

        results = []

        # -----------------------------------------------------
        # Weekly overview
        # -----------------------------------------------------

        for point in overview_points:

            results.append(
                self._result_from_point(
                    point,
                    2.5,
                )
            )

        # -----------------------------------------------------
        # Daily documents
        # -----------------------------------------------------

        unique_days = {}

        for point in daily_points:

            payload = point.get(
                "payload",
                {},
            )

            day = str(
                payload.get(
                    "day",
                    "",
                )
            ).lower().strip()

            if (
                day in DAYS_ORDER
                and day not in unique_days
            ):

                unique_days[day] = point

        for day in DAYS_ORDER:

            point = unique_days.get(
                day
            )

            if point:

                results.append(
                    self._result_from_point(
                        point,
                        2.0,
                    )
                )

        print(
            "[Retriever] Weekly mess route: "
            f"{len(results)} chunks retrieved."
        )

        return results

    # =========================================================
    # CATEGORY RETRIEVAL
    # =========================================================

    def retrieve_category_documents(
        self,
        category: str,
        query: str,
        source_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        points = (
            vectorstore_manager.get_by_filter(
                {
                    "category": category,
                },
                limit=100,
            )
        )

        q = self.normalize_query(
            query
        )

        query_terms = [
            term.lower()
            for term in re.findall(
                r"\w+",
                q,
            )
            if (
                len(term) > 2
                and term.lower()
                not in self.STOP_WORDS
            )
        ]

        results = []

        for point in points:

            payload = point.get(
                "payload",
                {},
            )

            if (
                source_type
                and payload.get(
                    "source_type"
                )
                != source_type
            ):
                continue

            content = payload.get(
                "content",
                "",
            )

            title = payload.get(
                "title",
                "",
            )

            document_title = payload.get(
                "document_title",
                "",
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

            results.append(
                self._result_from_point(
                    point,
                    1.0
                    + lexical_matches * 0.35,
                )
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        print(
            "[Retriever] Structured category route: "
            f"{category} -> {len(results)} chunks."
        )

        return results

    # =========================================================
    # TARGETED MENU RETRIEVAL
    # =========================================================

    def retrieve_menu_targeted(
        self,
        menu_intent: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        day = menu_intent.get(
            "day"
        )

        meal = menu_intent.get(
            "meal"
        )

        # -----------------------------------------------------
        # MEAL ONLY
        #
        # Example:
        # "breakfast menu"
        #
        # Returns breakfast across available days.
        # -----------------------------------------------------

        if meal and not day:

            meal_points = (
                vectorstore_manager.get_by_filter(
                    {
                        "category": "mess_menu",
                        "meal": meal,
                        "scope": "meal",
                    },
                    limit=50,
                )
            )

            day_index = {
                day_name: index
                for index, day_name
                in enumerate(
                    DAYS_ORDER
                )
            }

            meal_points.sort(
                key=lambda point: day_index.get(
                    str(
                        point.get(
                            "payload",
                            {},
                        ).get(
                            "day",
                            "",
                        )
                    ).lower(),
                    99,
                )
            )

            results = [
                self._result_from_point(
                    point,
                    3.5,
                )
                for point in meal_points
            ]

            print(
                "[Retriever] Targeted meal route: "
                f"meal={meal}, "
                f"chunks={len(results)}"
            )

            return results

        # -----------------------------------------------------
        # DAY + MEAL
        #
        # Example:
        # "Monday snacks"
        #
        # IMPORTANT:
        # Only exact meal records are returned.
        # -----------------------------------------------------

        if day and meal:

            meal_points = (
                vectorstore_manager.get_by_filter(
                    {
                        "category": "mess_menu",
                        "day": day,
                        "meal": meal,
                        "scope": "meal",
                    },
                    limit=10,
                )
            )

            results = [
                self._result_from_point(
                    point,
                    4.0,
                )
                for point in meal_points
            ]

            print(
                "[Retriever] Targeted meal route: "
                f"day={day}, "
                f"meal={meal}, "
                f"chunks={len(results)}"
            )

            return results

        # -----------------------------------------------------
        # DAY ONLY
        #
        # Example:
        # "Monday mess menu"
        #
        # Returns complete Monday daily document.
        # -----------------------------------------------------

        if day:

            day_points = (
                vectorstore_manager.get_by_filter(
                    {
                        "category": "mess_menu",
                        "day": day,
                        "scope": "daily",
                    },
                    limit=10,
                )
            )

            results = [
                self._result_from_point(
                    point,
                    4.0,
                )
                for point in day_points
            ]

            print(
                "[Retriever] Targeted daily route: "
                f"day={day}, "
                f"chunks={len(results)}"
            )

            return results

        return []

    # =========================================================
    # MAIN RETRIEVAL
    # =========================================================

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        original_query = query

        normalized_query = (
            self.normalize_query(
                query
            )
        )

        print(
            "[Retriever] Original query: "
            f"{original_query}"
        )

        print(
            "[Retriever] Normalized query: "
            f"{normalized_query}"
        )

        # -----------------------------------------------------
        # Detect menu intent
        # -----------------------------------------------------

        menu_intent = (
            self.detect_mess_menu_intent(
                normalized_query
            )
        )

        print(
            "[Retriever] Menu intent: "
            f"{menu_intent}"
        )

        # -----------------------------------------------------
        # Detect category
        # -----------------------------------------------------

        detected_category = (
            self.detect_category_intent(
                normalized_query
            )
        )

        if category:

            detected_category = category

        print(
            "[Retriever] Detected category: "
            f"{detected_category}"
        )

        # =====================================================
        # MESS MENU ROUTING
        # =====================================================

        is_mess_query = bool(
            detected_category
            == "mess_menu"
            or menu_intent.get(
                "is_menu_related"
            )
        )

        if is_mess_query:

            # -------------------------------------------------
            # SPECIFIC DAY / MEAL
            # -------------------------------------------------

            has_specific_scope = bool(
                menu_intent.get(
                    "day"
                )
                or menu_intent.get(
                    "meal"
                )
            )

            if has_specific_scope:

                targeted_docs = (
                    self.retrieve_menu_targeted(
                        menu_intent
                    )
                )

                if targeted_docs:

                    print(
                        "[Retriever] Using exact "
                        "structured menu retrieval."
                    )

                    print(
                        "[Retriever] Final retrieval: "
                        f"{len(targeted_docs)} chunks."
                    )

                    # CRITICAL:
                    # RETURN HERE.
                    #
                    # Do NOT perform semantic search.
                    #
                    return targeted_docs

                print(
                    "[Retriever] No exact structured "
                    "menu record found."
                )

                # Accuracy-first behavior.
                # Never substitute another day/meal.
                return []

            # -------------------------------------------------
            # BROAD / FULL MENU
            # -------------------------------------------------

            if menu_intent.get(
                "is_weekly"
            ):

                weekly_docs = (
                    self.retrieve_full_weekly_menu()
                )

                if weekly_docs:

                    print(
                        "[Retriever] Using complete "
                        "mess-menu retrieval."
                    )

                    print(
                        "[Retriever] Final retrieval: "
                        f"{len(weekly_docs)} chunks."
                    )

                    return weekly_docs

                print(
                    "[Retriever] No verified weekly "
                    "menu found."
                )

                return []

            # Explicit mess_menu category but no detected
            # day/meal/full phrase.
            if detected_category == "mess_menu":

                weekly_docs = (
                    self.retrieve_full_weekly_menu()
                )

                if weekly_docs:
                    return weekly_docs

                return []

        # =====================================================
        # STRUCTURED NON-MENU CATEGORIES
        # =====================================================

        if detected_category in {
            "dress_code",
            "transportation",
        }:

            category_docs = (
                self.retrieve_category_documents(
                    category=detected_category,
                    query=normalized_query,
                    source_type=source_type,
                )
            )

            if category_docs:

                return category_docs

        # =====================================================
        # NORMAL SEMANTIC SEARCH
        # =====================================================

        query_vector = (
            embedding_service.embed_query(
                normalized_query
            )
        )

        hits = (
            vectorstore_manager.search(
                query_vector=query_vector,
                top_k=20,
                category=category,
                source_type=source_type,
            )
        )

        is_temporal = (
            self.has_temporal_intent(
                normalized_query
            )
        )

        today = datetime.now(
            timezone.utc
        )

        query_terms = [
            term.lower()
            for term in re.findall(
                r"\w+",
                normalized_query,
            )
            if (
                len(term) > 2
                and term.lower()
                not in self.STOP_WORDS
            )
        ]

        scored_docs = []

        # -----------------------------------------------------
        # Score semantic results
        # -----------------------------------------------------

        for hit in hits:

            payload = hit.get(
                "payload",
                {},
            )

            content = payload.get(
                "content",
                "",
            )

            title = payload.get(
                "title",
                "",
            )

            document_title = payload.get(
                "document_title",
                "",
            )

            content_lower = (
                content.lower()
            )

            title_lower = (
                title.lower()
            )

            document_title_lower = (
                document_title.lower()
            )

            score = float(
                hit.get(
                    "score",
                    0.0,
                )
            )

            lexical_matches = sum(
                1
                for term in query_terms
                if (
                    term in content_lower
                    or term in title_lower
                    or term in document_title_lower
                )
            )

            score += (
                lexical_matches
                * 0.40
            )

            # -------------------------------------------------
            # Temporal relevance
            # -------------------------------------------------

            if is_temporal:

                publication_date = (
                    payload.get(
                        "publication_date"
                    )
                )

                event_date = (
                    payload.get(
                        "event_date"
                    )
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
                                    "+00:00",
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

                        if (
                            days_difference
                            >= 0
                        ):

                            score += (
                                0.40
                                / (
                                    1.0
                                    + 0.03
                                    * days_difference
                                )
                            )

                    except Exception:

                        pass

            scored_docs.append(
                {
                    "id": hit["id"],
                    "score": score,
                    "content": content,
                    "metadata": payload,
                }
            )

        # -----------------------------------------------------
        # Sort
        # -----------------------------------------------------

        scored_docs.sort(
            key=lambda item: item[
                "score"
            ],
            reverse=True,
        )

        # -----------------------------------------------------
        # Final normal results
        # -----------------------------------------------------

        final_results = []

        seen_ids = set()

        for document in scored_docs:

            document_id = document[
                "id"
            ]

            if document_id in seen_ids:
                continue

            seen_ids.add(
                document_id
            )

            final_results.append(
                document
            )

            if (
                len(final_results)
                >= self.top_k
            ):
                break

        print(
            "[Retriever] Final retrieval: "
            f"{len(final_results)} chunks."
        )

        return final_results

    # =========================================================
    # CONTEXT + SOURCE PROVENANCE
    # =========================================================

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
                {},
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
                    "Official College Record",
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
                    + str(
                        source_platform
                    ).upper()
                )

            if metadata.get(
                "day_title"
            ):

                header_elements.append(
                    "DAY: "
                    + str(
                        metadata.get(
                            "day_title"
                        )
                    ).upper()
                )

            elif metadata.get(
                "day"
            ):

                header_elements.append(
                    "DAY: "
                    + str(
                        metadata.get(
                            "day"
                        )
                    ).upper()
                )

            if metadata.get(
                "meal"
            ):

                header_elements.append(
                    "MEAL: "
                    + str(
                        metadata.get(
                            "meal"
                        )
                    ).upper()
                )

            if publication_date:

                header_elements.append(
                    "PUBLISHED: "
                    + str(
                        publication_date
                    )
                )

            if event_date:

                header_elements.append(
                    "EVENT DATE: "
                    + str(
                        event_date
                    )
                )

            if department:

                header_elements.append(
                    "DEPARTMENT: "
                    + str(
                        department
                    )
                )

            header_line = (
                " | ".join(
                    header_elements
                )
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
                "\n----------------------------------------\n"
                .join(
                    context_parts
                )
            ),
            "sources": sources,
        }


# =============================================================
# GLOBAL RETRIEVER
# =============================================================

campus_retriever = CampusRetriever(
    top_k=6
)