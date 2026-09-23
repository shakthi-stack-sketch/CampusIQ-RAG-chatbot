from typing import Optional
import re

from fastapi import APIRouter, HTTPException, Query

from backend.app.database.models import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
)

from backend.app.services.conversation_service import (
    create_conversation,
    get_conversation,
    list_conversations,
    update_conversation_title,
    delete_conversation,
    add_message,
    generate_smart_title,
)

from backend.app.rag.retriever import campus_retriever

from backend.app.rag.generator import (
    generate_grounded_answer,
    generate_general_response,
)

from backend.app.rag.intent import (
    classify_intent,
    normalize_query,
    detect_query_category,
    INTENT_GENERAL,
)


router = APIRouter(
    prefix="/api",
    tags=["Chat & Conversations"]
)


# ============================================================
# CONVERSATIONS
# ============================================================

@router.get("/conversations")
def get_all_conversations(
    search: Optional[str] = Query(
        None,
        description="Search term"
    )
):
    """
    List conversations grouped into
    Today, Yesterday, and Earlier.
    """
    return list_conversations(search=search)


@router.post("/conversations", response_model=dict)
def start_new_conversation(req: ConversationCreate):
    """
    Explicitly create a new conversation.
    """
    return create_conversation(
        title=req.title or "New Conversation"
    )


@router.get(
    "/conversations/{conv_id}",
    response_model=ConversationResponse
)
def get_conversation_by_id(conv_id: str):
    """
    Get conversation details with all historical messages.
    """
    conv = get_conversation(conv_id)

    if not conv:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conv


@router.patch("/conversations/{conv_id}")
def rename_conversation(
    conv_id: str,
    req: ConversationUpdate
):
    """
    Rename a conversation title.
    """
    success = update_conversation_title(
        conv_id,
        req.title
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {
        "success": True,
        "title": req.title
    }


@router.delete("/conversations/{conv_id}")
def remove_conversation(conv_id: str):
    """
    Delete a conversation and its messages.
    """
    success = delete_conversation(conv_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {
        "success": True,
        "deleted_id": conv_id
    }


# ============================================================
# FOLLOW-UP QUERY CONTEXT
# ============================================================

def contextualize_followup_query(
    current_query: str,
    history: list
) -> str:
    """
    Contextualize follow-up questions using previous
    conversation turns.

    Examples:

        User:
        What is the dress code?

        User:
        What about Thursday?

    becomes approximately:

        What about Thursday? dress code
    """

    if not history:
        return current_query

    q_clean = current_query.strip().lower()

    # --------------------------------------------------------
    # Find last user message
    # --------------------------------------------------------

    last_user_query = ""

    for msg in reversed(history):
        if msg.get("role") == "user":
            last_user_query = msg.get(
                "content",
                ""
            ).strip()
            break

    if not last_user_query:
        return current_query

    # --------------------------------------------------------
    # Common campus entities
    # --------------------------------------------------------

    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    meals = [
        "breakfast",
        "lunch",
        "snacks",
        "dinner",
    ]

    # --------------------------------------------------------
    # Detect follow-up language
    # --------------------------------------------------------

    followup_starters = [
        r"^(what|how)\s+about\b",
        r"^and\s+(what|how|for|on|about|which|where|when)\b",
        r"^what\s+(is|for|on)\s+(it|that)\b",
        r"^which\s+(one|ones|of\s+them|of\s+these|club|event|domain|department)\b",
        r"^(is|are)\s+there\s+(any|more)\b",
        r"^tell\s+me\s+more\b",
        r"^can\s+you\s+elaborate\b",
        r"^who\s+(can\s+join|is\s+in\s+charge|is\s+the\s+speaker)\b",
        r"^where\s+is\s+(that|it|this)\b",
        r"^when\s+is\s+(that|it|this)\b",
        r"^how\s+to\s+(join|apply|participate)\b",
    ]

    is_followup = any(
        bool(re.search(pattern, q_clean))
        for pattern in followup_starters
    )

    if not is_followup:

        short_followup_words = [
            "which",
            "one",
            "more",
            "that",
            "it",
            "they",
            "related",
            "ai",
            "timing",
            "timings",
            "girls",
            "boys",
            "formal",
            "casual",
            "leave",
            "outpass",
            "cost",
            "fee",
            "eligibility",
        ]

        if len(q_clean.split()) <= 6:

            if any(
                word in q_clean
                for word in short_followup_words + days + meals
            ):
                is_followup = True

    if not is_followup:
        return current_query

    last_lower = last_user_query.lower()

    # ========================================================
    # CLUBS
    # ========================================================

    if any(
        word in last_lower
        for word in [
            "club",
            "clubs",
            "yantramanav",
            "drones",
            "acm",
            "pace",
            "pals",
            "idea lab",
        ]
    ):
        return (
            f"{current_query} "
            "college clubs technical innovation "
            "Google Developer Club Drones Yantramanav"
        )

    # ========================================================
    # OPPORTUNITIES
    # ========================================================

    if any(
        word in last_lower
        for word in [
            "opportunity",
            "opportunities",
            "hackathon",
            "workshop",
            "internship",
            "seminar",
        ]
    ):
        return (
            f"{current_query} "
            "college opportunities hackathons "
            "workshops seminars placement"
        )

    # ========================================================
    # MESS MENU
    # ========================================================

    menu_indicators = [
        "menu",
        "mess",
        "breakfast",
        "lunch",
        "snacks",
        "dinner",
        "food",
        "eat",
    ]

    is_menu_previous = any(
        word in last_lower
        for word in menu_indicators
    )

    current_has_day = any(
        day in q_clean
        for day in days
    )

    current_has_meal = any(
        meal in q_clean
        for meal in meals
    )

    previous_meal = None

    for meal in meals:
        if meal in last_lower:
            previous_meal = meal
            break

    previous_day = None

    for day in days:
        if day in last_lower:
            previous_day = day
            break

    if is_menu_previous:

        if (
            current_has_day
            and not current_has_meal
            and previous_meal
        ):
            return (
                f"{current_query} "
                f"{previous_meal} hostel mess menu"
            )

        elif (
            current_has_meal
            and not current_has_day
            and previous_day
        ):
            return (
                f"{current_query} "
                f"on {previous_day} hostel mess menu"
            )

        elif current_has_day:
            return (
                f"{current_query} "
                "hostel mess menu"
            )

        elif current_has_meal:
            return (
                f"{current_query} "
                "hostel mess menu"
            )

        return (
            f"{current_query} "
            "hostel mess menu"
        )

    # ========================================================
    # DRESS CODE
    # ========================================================

    if any(
        word in last_lower
        for word in [
            "dress",
            "dress code",
            "dresscode",
            "uniform",
            "wear",
            "attire",
            "formal",
            "casual",
        ]
    ):
        return (
            f"{current_query} "
            "dress code"
        )

    # ========================================================
    # HOSTEL
    # ========================================================

    if any(
        word in last_lower
        for word in [
            "hostel",
            "room",
            "warden",
            "leave",
            "card",
        ]
    ):
        return (
            f"{current_query} "
            "hostel rules facilities"
        )

    # ========================================================
    # TRANSPORT
    # ========================================================

    if any(
        word in last_lower
        for word in [
            "bus",
            "transport",
            "route",
            "boarding",
        ]
    ):
        return (
            f"{current_query} "
            "bus timings"
        )

    # ========================================================
    # ACADEMICS
    # ========================================================

    if any(
        word in last_lower
        for word in [
            "exam",
            "iat",
            "semester",
            "academic",
            "calendar",
        ]
    ):
        return (
            f"{current_query} "
            "academic calendar examinations"
        )

    # ========================================================
    # CAMPUS LOCATIONS
    # ========================================================

    if any(
        word in last_lower
        for word in [
            "where",
            "office",
            "location",
            "room",
            "building",
            "venue",
            "auditorium",
        ]
    ):
        return (
            f"{current_query} "
            "college offices campus locations"
        )

    # ========================================================
    # FINAL FOLLOW-UP FALLBACK
    # ========================================================

    return (
        f"{current_query} "
        f"{last_user_query}"
    )


# ============================================================
# FALLBACK
# ============================================================

FALLBACK_MESSAGE = (
    "I couldn't find verified information about this in "
    "the available college sources. Please contact the "
    "concerned college office directly for the current "
    "information."
)


# ============================================================
# MAIN CHAT ENDPOINT
# ============================================================

@router.post(
    "/chat",
    response_model=ChatResponse
)
def handle_chat_message(req: ChatRequest):
    """
    CampusIQ main chat pipeline.

    Pipeline:

    1. Resolve/create conversation.
    2. Load conversation history.
    3. Contextualize follow-up query.
    4. Normalize spelling and wording.
    5. Detect user intent.
    6. Detect college knowledge category.
    7. Retrieve verified evidence from Qdrant.
    8. Generate grounded answer with Gemini.
    9. Save assistant response.
    10. Return answer and sources.
    """

    # ========================================================
    # 1. VALIDATE USER QUESTION
    # ========================================================

    original_query = req.message.strip()

    if not original_query:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # ========================================================
    # 2. RESOLVE / CREATE CONVERSATION
    # ========================================================

    conv_id = req.conversation_id

    is_new = False

    history_messages = []

    if not conv_id:

        new_conv = create_conversation(
            title="New Conversation"
        )

        conv_id = new_conv["id"]

        is_new = True

    else:

        existing = get_conversation(conv_id)

        if not existing:

            new_conv = create_conversation(
                title="New Conversation"
            )

            conv_id = new_conv["id"]

            is_new = True

        else:

            history_messages = existing.get(
                "messages",
                []
            )

            if not history_messages:
                is_new = True

    # ========================================================
    # 3. CONTEXTUALIZE FOLLOW-UP
    # ========================================================

    contextual_query = contextualize_followup_query(
        original_query,
        history_messages
    )

    # ========================================================
    # 4. NORMALIZE QUERY
    #
    # Examples:
    #
    # dresscode
    # dress kode
    # drescode
    #
    #        ↓
    #
    # dress code
    # ========================================================

    normalized_query = normalize_query(
        contextual_query
    )

    # ========================================================
    # 5. DETECT INTENT
    # ========================================================

    intent = classify_intent(
        normalized_query
    )

    # ========================================================
    # 6. DETECT CATEGORY
    #
    # Example:
    #
    # "what is the dress kode of PEC?"
    #
    #        ↓
    #
    # dress_code
    # ========================================================

    detected_category = detect_query_category(
        normalized_query
    )

    # ========================================================
    # 7. PERSIST ORIGINAL USER MESSAGE
    #
    # Important:
    # Store exactly what the user typed.
    # ========================================================

    user_msg = add_message(
        conv_id=conv_id,
        role="user",
        content=original_query
    )

    # ========================================================
    # 8. INITIALIZE RESPONSE DATA
    # ========================================================

    sources = []

    # ========================================================
    # 9. GENERAL CONVERSATION
    # ========================================================

    if intent == INTENT_GENERAL:

        answer = generate_general_response(
            original_query
        )

    # ========================================================
    # 10. COLLEGE KNOWLEDGE QUERY
    # ========================================================

    else:

        # ----------------------------------------------------
        # Respect an explicitly supplied category filter.
        #
        # Otherwise use our newly detected category.
        # ----------------------------------------------------

        retrieval_category = (
            req.category_filter
            if req.category_filter
            else detected_category
        )

        # ----------------------------------------------------
        # Debug information
        # ----------------------------------------------------

        print(
            "\n[CampusIQ Query Understanding]"
        )

        print(
            f"Original query      : {original_query}"
        )

        print(
            f"Contextual query    : {contextual_query}"
        )

        print(
            f"Normalized query    : {normalized_query}"
        )

        print(
            f"Detected intent     : {intent}"
        )

        print(
            f"Detected category   : {detected_category}"
        )

        print(
            f"Retrieval category  : {retrieval_category}"
        )

        # ----------------------------------------------------
        # Qdrant retrieval
        # ----------------------------------------------------

        retrieved_docs = campus_retriever.retrieve(
            query=normalized_query,
            category=retrieval_category,
            source_type=req.platform_filter
        )

        # ----------------------------------------------------
        # No verified documents
        # ----------------------------------------------------

        if not retrieved_docs:

            answer = FALLBACK_MESSAGE

        # ----------------------------------------------------
        # Verified documents found
        # ----------------------------------------------------

        else:

            context_data = (
                campus_retriever
                .build_context_and_sources(
                    retrieved_docs
                )
            )

            context_str = context_data[
                "context_str"
            ]

            potential_sources = context_data[
                "sources"
            ]

            # =================================================
            # CONVERSATION HISTORY FOR GEMINI
            # =================================================

            conv_hist_text = ""

            if history_messages:

                # Keep recent conversation context.
                recent_turns = history_messages[-4:]

                lines = []

                for message in recent_turns:

                    role_name = (
                        "Student"
                        if message.get("role") == "user"
                        else "CampusIQ"
                    )

                    snippet = (
                        message.get(
                            "content",
                            ""
                        )
                        .strip()
                    )

                    # Avoid sending excessively large history.
                    snippet = snippet[:500]

                    lines.append(
                        f"{role_name}: {snippet}"
                    )

                conv_hist_text = "\n".join(
                    lines
                )

            # =================================================
            # GROUNDED GEMINI ANSWER
            # =================================================

            answer = generate_grounded_answer(
                query=original_query,
                context_str=context_str,
                sources=potential_sources,
                conversation_history_text=conv_hist_text
            )

            # =================================================
            # SOURCE SAFETY
            # =================================================

            if (
                "couldn't find verified information"
                in answer.lower()
            ):

                sources = []

            else:

                sources = potential_sources

    # ========================================================
    # 11. SAVE ASSISTANT MESSAGE
    # ========================================================

    assistant_msg = add_message(
        conv_id=conv_id,
        role="assistant",
        content=answer,
        sources=sources
    )

    # ========================================================
    # 12. GENERATE SMART TITLE
    # ========================================================

    smart_title = None

    if is_new:

        smart_title = generate_smart_title(
            original_query
        )

        update_conversation_title(
            conv_id,
            smart_title
        )

    # ========================================================
    # 13. RETURN RESPONSE
    # ========================================================

    return ChatResponse(
        conversation_id=conv_id,
        user_message_id=user_msg["id"],
        assistant_message_id=assistant_msg["id"],
        answer=answer,
        sources=sources,
        title=smart_title
    )