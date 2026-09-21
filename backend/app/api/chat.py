from typing import Optional
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
    generate_smart_title
)
from backend.app.rag.retriever import campus_retriever
from backend.app.rag.generator import generate_grounded_answer, generate_general_response
from backend.app.rag.intent import classify_intent, INTENT_GENERAL

router = APIRouter(prefix="/api", tags=["Chat & Conversations"])

@router.get("/conversations")
def get_all_conversations(search: Optional[str] = Query(None, description="Search term")):
    """List conversations grouped into Today, Yesterday, and Earlier."""
    return list_conversations(search=search)

@router.post("/conversations", response_model=dict)
def start_new_conversation(req: ConversationCreate):
    """Explicitly create a new conversation."""
    return create_conversation(title=req.title or "New Conversation")

@router.get("/conversations/{conv_id}", response_model=ConversationResponse)
def get_conversation_by_id(conv_id: str):
    """Get conversation details with all historical messages."""
    conv = get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.patch("/conversations/{conv_id}")
def rename_conversation(conv_id: str, req: ConversationUpdate):
    """Rename a conversation title."""
    success = update_conversation_title(conv_id, req.title)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "title": req.title}

@router.delete("/conversations/{conv_id}")
def remove_conversation(conv_id: str):
    """Delete a conversation and its messages."""
    success = delete_conversation(conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "deleted_id": conv_id}

import re

def contextualize_followup_query(current_query: str, history: list) -> str:
    """
    Contextualize follow-up questions (e.g. 'What about Tuesday?', 'Which one is related to AI?', 'What about girls?')
    using previous conversation turns so retrieval is fully grounded and query-aware.
    """
    if not history:
        return current_query

    q_clean = current_query.strip().lower()

    # Find the last user message and assistant message from conversation history
    last_user_query = ""
    for msg in reversed(history):
        if msg.get("role") == "user":
            last_user_query = msg.get("content", "").strip()
            break

    if not last_user_query:
        return current_query

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    meals = ["breakfast", "lunch", "snacks", "dinner"]

    # Detect follow-up signals: starts with conversational inquiry or pronouns
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
        r"^how\s+to\s+(join|apply|participate)\b"
    ]
    is_followup = any(bool(re.search(p, q_clean)) for p in followup_starters) or (
        len(q_clean.split()) <= 6 and any(w in q_clean for w in [
            "which", "one", "more", "that", "it", "they", "related", "ai", "timing", "timings",
            "girls", "boys", "formal", "casual", "leave", "outpass", "cost", "fee", "eligibility"
        ] + days + meals)
    )

    if not is_followup:
        return current_query

    last_lower = last_user_query.lower()

    # 1. Clubs & Student Development context
    if any(w in last_lower for w in ["club", "clubs", "yantramanav", "drones", "acm", "pace", "pals", "idea lab"]):
        return f"{current_query} college clubs technical innovation Google Developer Club Drones Yantramanav"

    # 2. Opportunities, Hackathons & Workshops context
    if any(w in last_lower for w in ["opportunity", "opportunities", "hackathon", "workshop", "internship", "seminar"]):
        return f"{current_query} college opportunities hackathons workshops seminars placement"

    # 3. Mess Menu context
    menu_indicators = ["menu", "mess", "breakfast", "lunch", "snacks", "dinner", "food", "eat"]
    is_menu_prev = any(w in last_lower for w in menu_indicators)
    current_has_day = any(d in q_clean for d in days)
    current_has_meal = any(m in q_clean for m in meals)

    prev_meal = None
    for m in meals:
        if m in last_lower:
            prev_meal = m
            break

    prev_day = None
    for d in days:
        if d in last_lower:
            prev_day = d
            break

    if is_menu_prev:
        if current_has_day and not current_has_meal and prev_meal:
            return f"{current_query} {prev_meal} hostel mess menu"
        elif current_has_meal and not current_has_day and prev_day:
            return f"{current_query} on {prev_day} hostel mess menu"
        elif current_has_day:
            return f"{current_query} hostel mess menu"
        elif current_has_meal:
            return f"{current_query} hostel mess menu"
        return f"{current_query} hostel mess menu"

    # 4. Dress code context
    if any(w in last_lower for w in ["dress", "uniform", "wear", "attire"]):
        return f"{current_query} dress code"

    # 5. Hostel rules context
    if any(w in last_lower for w in ["hostel", "room", "warden", "leave", "card"]):
        return f"{current_query} hostel rules facilities"

    # 6. Transport context
    if any(w in last_lower for w in ["bus", "transport", "route", "boarding"]):
        return f"{current_query} bus timings"

    # 7. Academics & Exams context
    if any(w in last_lower for w in ["exam", "iat", "semester", "academic", "calendar"]):
        return f"{current_query} academic calendar examinations"

    # 8. Locations & Offices context
    if any(w in last_lower for w in ["where", "office", "location", "room", "building", "venue", "auditorium"]):
        return f"{current_query} college offices campus locations"

    return f"{current_query} {last_user_query}"

FALLBACK_MESSAGE = (
    "I couldn't find verified information about this in the available college sources. "
    "Please contact the concerned college office directly for the current information."
)

@router.post("/chat", response_model=ChatResponse)
def handle_chat_message(req: ChatRequest):
    """
    CampusIQ Chat Pipeline with Intent-Based Routing and Contextual Follow-up:
    1. Resolve or create persistent conversation and fetch previous history.
    2. Contextualize follow-up queries using conversation history.
    3. Persist user message.
    4. Determine intent:
       - GENERAL_CONVERSATION: Routed directly to Gemini for natural greetings, thanks, education.
       - COLLEGE_KNOWLEDGE_QUERY: Routed to Qdrant vector retrieval + grounded Gemini generator.
    5. Save assistant response and sources.
    6. Return ChatResponse.
    """
    query = req.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # 1. Resolve or create conversation
    conv_id = req.conversation_id
    is_new = False
    history_messages = []

    if not conv_id:
        new_conv = create_conversation(title="New Conversation")
        conv_id = new_conv["id"]
        is_new = True
    else:
        existing = get_conversation(conv_id)
        if not existing:
            new_conv = create_conversation(title="New Conversation")
            conv_id = new_conv["id"]
            is_new = True
        else:
            history_messages = existing.get("messages", [])
            if not history_messages:
                is_new = True

    # 2. Contextualize query if it is a follow-up
    retrieval_query = contextualize_followup_query(query, history_messages)

    # 3. Persist user message
    user_msg = add_message(conv_id=conv_id, role="user", content=query)

    # 4. Intent-based routing
    intent = classify_intent(retrieval_query)
    sources = []

    if intent == INTENT_GENERAL:
        # Route directly to Gemini (no college document retrieval)
        answer = generate_general_response(query)
    else:
        # College knowledge query -> Qdrant vector retrieval
        retrieved_docs = campus_retriever.retrieve(
            query=retrieval_query,
            category=req.category_filter,
            source_type=req.platform_filter
        )

        if not retrieved_docs:
            answer = FALLBACK_MESSAGE
        else:
            context_data = campus_retriever.build_context_and_sources(retrieved_docs)
            context_str = context_data["context_str"]
            potential_sources = context_data["sources"]

            conv_hist_text = ""
            if history_messages:
                recent_turns = history_messages[-2:]
                lines = []
                for m in recent_turns:
                    role_name = "Student" if m.get("role") == "user" else "CampusIQ"
                    snippet = m.get("content", "").strip()[:300]
                    lines.append(f"{role_name}: {snippet}")
                conv_hist_text = "\n".join(lines)

            answer = generate_grounded_answer(
                query=query,
                context_str=context_str,
                sources=potential_sources,
                conversation_history_text=conv_hist_text
            )

            # If the model indicates missing verified information, omit sources
            if "couldn't find verified information" in answer.lower():
                sources = []
            else:
                sources = potential_sources

    # 5. Persist assistant response
    assistant_msg = add_message(
        conv_id=conv_id,
        role="assistant",
        content=answer,
        sources=sources
    )

    # 6. Auto-generate smart title from first query
    smart_title = None
    if is_new:
        smart_title = generate_smart_title(query)
        update_conversation_title(conv_id, smart_title)

    return ChatResponse(
        conversation_id=conv_id,
        user_message_id=user_msg["id"],
        assistant_message_id=assistant_msg["id"],
        answer=answer,
        sources=sources,
        title=smart_title
    )
