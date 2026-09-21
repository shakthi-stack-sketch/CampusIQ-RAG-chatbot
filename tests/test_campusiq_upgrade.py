# Setup database and configurations
from backend.app.database.db import init_db
from backend.app.rag.vectorstore import vectorstore_manager
from backend.app.rag.retriever import campus_retriever
from backend.app.rag.generator import generate_grounded_answer, generate_vault_answer
from backend.app.rag.intent import classify_intent, INTENT_COLLEGE, INTENT_GENERAL
from backend.app.api.chat import contextualize_followup_query
from backend.app.api.pulse import load_verified_social_items, get_campus_pulse, get_verified_opportunities, get_verified_locations
from backend.app.services.vault_service import (
    save_vault_document,
    list_vault_documents,
    delete_vault_document,
    query_user_vault
)
from backend.app.api.saved import save_answer, get_saved_answers, unsave_answer, unsave_by_message_id
from backend.app.database.models import SavedAnswerCreate

def setup_test_environment():
    init_db()

# ==================================================
# 1. VECTORSTORE & INDEXING TESTS
# ==================================================

def test_vectorstore_indexed():
    """Verify that Qdrant vectorstore is active and contains college vectors."""
    count = vectorstore_manager.get_collection_count()
    assert count > 0, f"Qdrant collection should contain vectors, found {count}"

def test_mess_menu_all_days_indexed():
    """Verify all 7 days of the mess menu are indexed in Qdrant."""
    val = vectorstore_manager.validate_mess_menu_indexing()
    assert val["all_days_indexed"] is True, f"Missing days in mess menu indexing: {val['days_validation']}"

# ==================================================
# 2. MESS MENU RETRIEVAL TESTS (ALL 7 DAYS)
# ==================================================

def test_monday_breakfast_retrieval():
    docs = campus_retriever.retrieve("What is the Monday breakfast menu?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "idli" in text or "vada curry" in text

def test_tuesday_lunch_retrieval():
    docs = campus_retriever.retrieve("What is served for Tuesday lunch?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "biryani" in text or "sambar rice" in text or "kurma" in text

def test_wednesday_dinner_retrieval():
    docs = campus_retriever.retrieve("What is for dinner on Wednesday?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "idli" in text or "chicken kurma" in text or "veg kurma" in text

def test_thursday_retrieval():
    docs = campus_retriever.retrieve("What is the food menu on Thursday?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "dosa" in text or "bonda" in text or "vatha kulambu" in text

def test_friday_snacks_retrieval():
    docs = campus_retriever.retrieve("What are the snacks on Friday?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "bun butter jam" in text or "tea" in text

def test_saturday_dinner_retrieval():
    docs = campus_retriever.retrieve("What is for dinner on Saturday?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "pongal" in text or "sambar" in text or "chutney" in text

def test_sunday_breakfast_retrieval():
    docs = campus_retriever.retrieve("What is the breakfast on Sunday?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "poori" in text or "potato masala" in text or "boiled egg" in text

def test_full_weekly_menu_retrieval():
    docs = campus_retriever.retrieve("Show me the complete weekly mess menu from Monday to Sunday")
    assert len(docs) > 0
    days_found = set()
    for d in docs:
        day = d["metadata"].get("day")
        if day:
            days_found.add(day.lower())
    # Full weekly menu routing must contain all 7 days
    assert len(days_found) == 7 or any("complete weekly" in d["content"].lower() for d in docs)

# ==================================================
# 3. ACADEMIC, DRESS CODE & HOSTEL GROUNDING
# ==================================================

def test_academic_iat_count():
    docs = campus_retriever.retrieve("How many IATs are conducted per semester?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "three internal assessment tests" in text or "iat" in text

def test_dress_code_norms():
    docs = campus_retriever.retrieve("What is the formal dress code for students from Monday to Wednesday?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "formal" in text and ("salwar" in text or "tuck" in text)

def test_hostel_leave_card_colors():
    docs = campus_retriever.retrieve("What are the hostel leave card colors for boys and girls?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "pink card" in text and "yellow card" in text

def test_clubs_retrieval():
    docs = campus_retriever.retrieve("What clubs are available at PEC?")
    assert len(docs) > 0
    text = "\n".join(d["content"] for d in docs).lower()
    assert "google developer club" in text or "drones club" in text or "yantramanav" in text

# ==================================================
# 4. CONVERSATIONAL SEARCH & FOLLOW-UP (FIND THIS FOR ME)
# ==================================================

def test_followup_contextualization_clubs_ai():
    history = [
        {"role": "user", "content": "What clubs are available?"},
        {"role": "assistant", "content": "The college offers Google Developer Club, Drones Club, Yantramanav..."}
    ]
    query = "Which one is related to AI?"
    rewritten = contextualize_followup_query(query, history)
    assert "club" in rewritten.lower() or "innovation" in rewritten.lower()

    # Now verify Qdrant retrieves relevant docs with the rewritten query
    docs = campus_retriever.retrieve(rewritten)
    assert len(docs) > 0
    assert any("club" in d["metadata"].get("category", "").lower() or "club" in d["content"].lower() for d in docs)

def test_followup_contextualization_menu():
    history = [
        {"role": "user", "content": "What is the mess menu on Wednesday?"},
        {"role": "assistant", "content": "Wednesday breakfast is Pongal..."}
    ]
    query = "What about Thursday?"
    rewritten = contextualize_followup_query(query, history)
    assert "thursday" in rewritten.lower()
    assert "mess menu" in rewritten.lower()

# ==================================================
# 5. ANTI-HALLUCINATION & ZERO-FABRICATION TESTS
# ==================================================

def test_anti_hallucination_fake_event():
    """Asking about a completely fake event must NOT invent dates or answers."""
    query = "When is the PEC Interstellar Robotics Championship on Mars scheduled in 2099?"
    docs = campus_retriever.retrieve(query)
    ctx = campus_retriever.build_context_and_sources(docs)["context_str"]
    ans = generate_grounded_answer(query, ctx, [])
    ans_lower = ans.lower()
    assert "couldn't find verified information" in ans_lower or "not found" in ans_lower or "no verified" in ans_lower
    assert "2099" not in ans
    assert "mars" not in ans_lower or "couldn't find" in ans_lower

def test_anti_hallucination_fake_fee():
    """Asking about a fake fee must NOT invent currency amounts."""
    query = "What is the annual fee of 500000 rupees for the Secret Quantum Supercomputing Lab?"
    docs = campus_retriever.retrieve(query)
    ctx = campus_retriever.build_context_and_sources(docs)["context_str"]
    ans = generate_grounded_answer(query, ctx, [])
    ans_lower = ans.lower()
    assert "couldn't find verified information" in ans_lower or "not found" in ans_lower
    assert "500000" not in ans

def test_anti_hallucination_fake_office():
    """Asking about a fake room number/office must NOT invent locations."""
    query = "Where is room 909 located in Block Z on the 9th floor?"
    docs = campus_retriever.retrieve(query)
    ctx = campus_retriever.build_context_and_sources(docs)["context_str"]
    ans = generate_grounded_answer(query, ctx, [])
    ans_lower = ans.lower()
    assert "couldn't find verified information" in ans_lower or "not found" in ans_lower
    assert "block z" not in ans_lower or "couldn't find" in ans_lower

def test_anti_hallucination_fake_staff():
    """Asking about a fake staff member must NOT invent a biography or phone number."""
    query = "Who is Professor Johnathan Alexander Smith in the Mechanical department and what is his phone number?"
    docs = campus_retriever.retrieve(query)
    ctx = campus_retriever.build_context_and_sources(docs)["context_str"]
    ans = generate_grounded_answer(query, ctx, [])
    ans_lower = ans.lower()
    assert "couldn't find verified information" in ans_lower or "not found" in ans_lower

def test_anti_hallucination_fake_opportunity():
    """Asking about a non-existent opportunity must NOT invent application links."""
    query = "Provide the direct registration link for the NASA Mars Exploration Internship at PEC."
    docs = campus_retriever.retrieve(query)
    ctx = campus_retriever.build_context_and_sources(docs)["context_str"]
    ans = generate_grounded_answer(query, ctx, [])
    ans_lower = ans.lower()
    assert "couldn't find verified information" in ans_lower or "not found" in ans_lower
    assert "http://nasa" not in ans_lower and "https://nasa" not in ans_lower

# ==================================================
# 6. SAVED ANSWERS CRUD TESTS
# ==================================================

def test_saved_answers_lifecycle():
    user_id = "test_student_user_1"
    req = SavedAnswerCreate(
        user_id=user_id,
        conversation_id="conv_test_123",
        message_id="msg_test_456",
        question="What is the dress code on Monday?",
        answer="Students must wear formal attire from Monday to Wednesday.",
        sources=[{"title": "dress_code.txt", "platform": "Official PEC Document"}]
    )

    # 1. Save
    saved = save_answer(req)
    assert saved["id"] is not None
    assert saved["question"] == req.question

    # 2. Retrieve
    user_saved = get_saved_answers(user_id=user_id)
    assert len(user_saved) >= 1
    assert any(item["message_id"] == "msg_test_456" for item in user_saved)

    # 3. Unsave by message ID
    unsave_by_message_id(message_id="msg_test_456", user_id=user_id)
    updated_saved = get_saved_answers(user_id=user_id)
    assert not any(item["message_id"] == "msg_test_456" for item in updated_saved)

# ==================================================
# 7. PERSONAL KNOWLEDGE VAULT ISOLATION TESTS
# ==================================================

def test_vault_document_isolation():
    user_a = "student_user_alice"
    user_b = "student_user_bob"

    # Alice uploads her private timetable
    alice_timetable = (
        "ALICE'S PERSONAL TIMETABLE - FALL 2026\n"
        "Monday 9am: Advanced Distributed Systems in Lab 3\n"
        "Tuesday 2pm: Quantum Cryptography Project Meeting with Team Beta"
    )
    doc_a = save_vault_document(
        user_id=user_a,
        filename="alice_timetable.txt",
        file_bytes=alice_timetable.encode("utf-8")
    )
    assert doc_a["id"] is not None

    # Alice queries her vault -> gets her timetable
    res_a = query_user_vault(user_id=user_a, query="What class do I have on Monday at 9am?")
    assert "distributed systems" in res_a["answer"].lower() or "lab 3" in res_a["answer"].lower()

    # Bob queries his vault -> MUST NOT get Alice's timetable!
    res_b = query_user_vault(user_id=user_b, query="What class do I have on Monday at 9am?")
    assert "distributed systems" not in res_b["answer"].lower()
    assert "no personal documents" in res_b["answer"].lower()

    # Bob lists documents -> Bob sees 0 documents
    b_docs = list_vault_documents(user_id=user_b)
    assert len(b_docs) == 0

    # General College RAG -> MUST NOT retrieve Alice's personal timetable
    college_docs = campus_retriever.retrieve("What class is on Monday at 9am in Lab 3?")
    assert not any("Team Beta" in d.get("content", "") for d in college_docs)
    assert not any("ALICE'S PERSONAL TIMETABLE" in d.get("content", "") for d in college_docs)

    # Cleanup
    delete_vault_document(user_id=user_a, doc_id=doc_a["id"])

# ==================================================
# 8. CAMPUS PULSE & OPPORTUNITY FINDER TESTS
# ==================================================

def test_campus_pulse_items():
    items = get_campus_pulse()
    assert len(items) > 0
    for item in items:
        assert item.title is not None and len(item.title) > 0
        assert item.source_platform is not None
        assert item.verified is True
        # Ensure no fake dates
        if item.event_date:
            assert item.event_date.startswith("2026")
        if item.publication_date:
            assert item.publication_date.startswith("2026")

def test_verified_opportunities_items():
    opps = get_verified_opportunities()
    assert len(opps) > 0
    for op in opps:
        assert op.title is not None and len(op.title) > 0
        assert op.category in {"workshops", "hackathons", "seminars", "training", "competitions", "general"}
        # Check that application links, if present, are valid URLs
        if op.application_link:
            assert op.application_link.startswith("http")

def test_verified_locations_items():
    locs = get_verified_locations()
    assert len(locs) >= 5
    loc_names = [l["name"] for l in locs]
    assert any("Admissions" in name for name in loc_names)
    assert any("Placement" in name for name in loc_names)
    assert any("Hostel" in name for name in loc_names)
