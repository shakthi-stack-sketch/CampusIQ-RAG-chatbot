import re

# Intent Types
INTENT_GENERAL = "GENERAL_CONVERSATION"
INTENT_COLLEGE = "COLLEGE_KNOWLEDGE_QUERY"

# Regex patterns for fast, high-confidence conversational classification
GREETING_PATTERNS = [
    r"^(hi|hello|hey|heyy|heya|howdy|greetings)\b",
    r"^good\s+(morning|afternoon|evening|day|night)\b",
    r"^how\s+are\s+you\b",
    r"^how('s|s|\s+is)\s+it\s+going\b",
    r"^what('s|s|\s+is)\s+up\b",
    r"^nice\s+to\s+meet\s+you\b",
]

POLITE_PATTERNS = [
    r"^(thanks|thank\s+you|thank\s+u|thx|tysm|many\s+thanks|appreciate\s+it)\b",
    r"^(bye|goodbye|see\s+you|cya|take\s+care|have\s+a\s+(good|nice|great)\s+day)\b",
    r"^(ok|okay|cool|great|awesome|understood|got\s+it|alright)\b",
]

BOT_IDENTITY_PATTERNS = [
    r"^who\s+are\s+you\b",
    r"^what\s+is\s+your\s+name\b",
    r"^what\s+can\s+you\s+do\b",
    r"^what\s+are\s+you\b",
    r"^tell\s+me\s+about\s+yourself\b",
    r"^help(\s+me)?$",
    r"^tell\s+me\s+a\s+joke\b",
]

COLLEGE_SPECIFIC_KEYWORDS = {
    "prathyusha", "pec", "college", "campus", "hostel", "mess", "menu",
    "breakfast", "lunch", "dinner", "snacks", "snack", "food", "meals", "meal",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "dress", "code", "formal", "casual", "shawl", "jeans", "tuck", "tucked", "salwar",
    "iat", "internal", "assessment", "exam", "examination", "semester", "syllabus",
    "calendar", "bus", "transport", "route", "boarding", "timing", "timings",
    "fee", "fees", "admission", "admissions", "bonafide", "leave", "card", "pink card",
    "yellow card", "outpass", "warden", "hod", "principal", "faculty", "mentor",
    "club", "clubs", "yantramanav", "drones", "ar-vr", "idea lab", "hackathon",
    "workshop", "placement", "placements", "recruiter", "package",
    "biotechnology", "cse", "ece", "mech", "freshers", "pongal", "culturals",
    "rules", "regulations", "facility", "facilities", "canteen", "library",
    "reopening", "working day", "working days", "holiday", "holidays"
}

def classify_intent(query: str) -> str:
    """
    Classifies a user query into:
    - GENERAL_CONVERSATION: Greetings, thanks, identity, general educational questions (Python, ML, etc.)
    - COLLEGE_KNOWLEDGE_QUERY: Inquiries about Prathyusha Engineering College rules, hostel, timings, academics, events.
    """
    q_clean = query.strip().lower()
    if not q_clean:
        return INTENT_GENERAL

    # 1. Direct match on greetings
    for pat in GREETING_PATTERNS:
        if re.search(pat, q_clean):
            # If the user says "Good morning, what is the hostel menu?", that's a college query!
            if any(k in q_clean for k in COLLEGE_SPECIFIC_KEYWORDS):
                return INTENT_COLLEGE
            return INTENT_GENERAL

    # 2. Direct match on polite/gratitude/closing
    for pat in POLITE_PATTERNS:
        if re.search(pat, q_clean):
            if any(k in q_clean for k in COLLEGE_SPECIFIC_KEYWORDS):
                return INTENT_COLLEGE
            return INTENT_GENERAL

    # 3. Direct match on bot identity / joke / help
    for pat in BOT_IDENTITY_PATTERNS:
        if re.search(pat, q_clean):
            return INTENT_GENERAL

    # 4. Check for general coding / science / AI educational questions
    general_educational_starts = [
        "what is python", "explain python", "how does python",
        "what is machine learning", "explain machine learning",
        "what is ai", "explain ai", "what is an algorithm",
        "what is javascript", "what is java", "what is c++",
        "what is data structure", "how to write a program",
        "tell me about python", "tell me about machine learning"
    ]
    if any(q_clean.startswith(prefix) for prefix in general_educational_starts):
        return INTENT_GENERAL

    # 5. Check for college-specific keywords
    words = re.findall(r"\w+", q_clean)
    if any(w in COLLEGE_SPECIFIC_KEYWORDS for w in words):
        return INTENT_COLLEGE

    # 6. Default handling: If query asks "how many semesters", "when are tests", "where is", "rules", etc.
    college_phrases = ["semester", "semesters", "exam", "exams", "test", "tests", "rules", "timing", "timings"]
    if any(p in q_clean for p in college_phrases):
        return INTENT_COLLEGE

    # If short and no college terms (e.g. "hey there", "howdy friend") -> general
    if len(words) <= 3 and not any(w in COLLEGE_SPECIFIC_KEYWORDS for w in words):
        return INTENT_GENERAL

    # Default to College Query for multi-word queries so RAG can inspect knowledge
    return INTENT_COLLEGE
