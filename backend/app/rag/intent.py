import re
from typing import Optional
from difflib import SequenceMatcher


# ============================================================
# INTENT NAMES
# ============================================================

INTENT_GENERAL = "GENERAL_CONVERSATION"
INTENT_COLLEGE = "COLLEGE_KNOWLEDGE_QUERY"


# ============================================================
# GREETINGS / GENERAL CONVERSATION
# ============================================================

GREETING_PATTERNS = [
    r"^(hi|hello|hey|hii|hiii)$",
    r"^good morning$",
    r"^good afternoon$",
    r"^good evening$",
    r"^good night$",
    r"^morning$",
    r"^afternoon$",
    r"^evening$",
]

POLITE_PATTERNS = [
    r"^thanks$",
    r"^thank you$",
    r"^thankyou$",
    r"^thanks a lot$",
    r"^thank you so much$",
    r"^ok$",
    r"^okay$",
    r"^great$",
    r"^nice$",
    r"^cool$",
]

BOT_IDENTITY_PATTERNS = [
    r"who are you",
    r"what are you",
    r"what is campusiq",
    r"tell me about yourself",
]


# ============================================================
# COLLEGE-SPECIFIC KEYWORDS
# ============================================================

COLLEGE_SPECIFIC_KEYWORDS = [
    # College
    "prathyusha",
    "prathyusha engineering college",
    "pec",
    "college",
    "campus",

    # Academics
    "academic",
    "academics",
    "academic calendar",
    "calendar",
    "semester",
    "sem",
    "exam",
    "exams",
    "iat",
    "model exam",
    "practical exam",
    "end semester",
    "end sem",
    "university",
    "course",
    "courses",
    "subject",
    "subjects",
    "lesson",
    "lessons",
    "presentation",
    "presentations",

    # Dress code
    "dress",
    "dress code",
    "dresscode",
    "dress kode",
    "uniform",
    "formal",
    "formals",
    "casual",
    "casuals",
    "leggings",
    "jeans",
    "ripped jeans",
    "salwar",
    "shawl",

    # Transport
    "bus",
    "buses",
    "bus timing",
    "bus timings",
    "bus time",
    "bus route",
    "bus routes",
    "boarding",
    "boarding time",
    "transport",
    "transportation",

    # Food
    "mess",
    "mess menu",
    "messmenu",
    "menu",
    "food",
    "breakfast",
    "lunch",
    "dinner",
    "snacks",

    # Clubs
    "club",
    "clubs",
    "google developer",
    "digital marketing",
    "gaming",
    "ar vr",
    "robotics",
    "idea lab",
    "aws",
    "acm",
    "pace",
    "pals",
    "maths",

    # Campus information
    "office",
    "admin office",
    "administration",
    "main block",
    "id card",
    "idcard",
    "bonafide",
    "scholarship",
    "certificate",
    "contact",
    "contact number",
    "email",
    "location",

    # Opportunities
    "opportunity",
    "opportunities",
    "internship",
    "internships",
    "placement",
    "placements",
    "job",
    "jobs",
    "hackathon",
    "event",
    "events",
]


# ============================================================
# QUERY NORMALIZATION
# ============================================================

QUERY_ALIASES = {
    # -------------------------
    # Dress code
    # -------------------------
    "dresscode": "dress code",
    "dress kode": "dress code",
    "dresskode": "dress code",
    "dres code": "dress code",
    "drescode": "dress code",
    "dres kode": "dress code",
    "dress cod": "dress code",
    "dresscod": "dress code",
    "dresscodde": "dress code",
    "dresscod e": "dress code",

    # -------------------------
    # Mess menu
    # -------------------------
    "messmenu": "mess menu",
    "mess menue": "mess menu",
    "messmenue": "mess menu",
    "mess mennu": "mess menu",
    "mess manu": "mess menu",
    "mess menuee": "mess menu",

    # -------------------------
    # Bus / transport
    # -------------------------
    "bustiming": "bus timing",
    "bus timming": "bus timing",
    "bus timinng": "bus timing",
    "bus timings": "bus timings",
    "bustimings": "bus timings",
    "bus time": "bus timing",
    "buss timing": "bus timing",
    "buss timings": "bus timings",
    "transportaion": "transportation",
    "transportion": "transportation",

    # -------------------------
    # Academic
    # -------------------------
    "acadmic": "academic",
    "acadamics": "academics",
    "academics": "academics",
    "acadmic calendar": "academic calendar",
    "academic calender": "academic calendar",
    "acadmic calender": "academic calendar",
    "acadamic calendar": "academic calendar",
    "acadamic calender": "academic calendar",
    "calender": "calendar",

    # -------------------------
    # Common college words
    # -------------------------
    "prathyusa": "prathyusha",
    "prathyushaa": "prathyusha",
    "prathusha": "prathyusha",
    "prathyusha engg": "prathyusha engineering",
    "collage": "college",
    "clg": "college",

    # -------------------------
    # Common question words
    # -------------------------
    "wht": "what",
    "wat": "what",
    "whats": "what is",
    "whre": "where",
    "wher": "where",
    "wen": "when",
    "hw": "how",
    "pls": "please",
    "plz": "please",
}


# ============================================================
# FUZZY TERMS
# ============================================================

FUZZY_TERMS = {
    "dress": "dress",
    "dresscode": "dress code",
    "dresskode": "dress code",
    "drescode": "dress code",
    "dres": "dress",

    "mess": "mess",
    "menue": "menu",
    "menuee": "menu",
    "manu": "menu",

    "bus": "bus",
    "buss": "bus",
    "timming": "timing",
    "timin": "timing",
    "timings": "timings",

    "acadmic": "academic",
    "acadamic": "academic",
    "acadamics": "academics",
    "calender": "calendar",

    "prathyusa": "prathyusha",
    "prathusha": "prathyusha",

    "collage": "college",
    "clg": "college",
}


# ============================================================
# NORMALIZE QUERY
# ============================================================

def normalize_query(query: str) -> str:
    """
    Cleans the user's question and fixes common spelling variations.

    Example:
        dresscode
        dress kode
        dresscodde

    all become:

        dress code
    """

    if not query:
        return ""

    # Convert to lowercase
    text = query.lower().strip()

    # Normalize apostrophes / unusual spaces
    text = text.replace("’", "'")
    text = re.sub(r"\s+", " ", text)

    # Remove unnecessary punctuation
    text = re.sub(r"[!?]+", "?", text)
    text = re.sub(r"\s*,\s*", ", ", text)

    # Apply exact aliases
    # Longer aliases first so they get priority.
    for wrong, correct in sorted(
        QUERY_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        pattern = r"\b" + re.escape(wrong) + r"\b"
        text = re.sub(pattern, correct, text)

    # Clean spaces again
    text = re.sub(r"\s+", " ", text).strip()

    # Fuzzy correction for individual words
    words = text.split()

    corrected_words = []

    for word in words:
        clean_word = re.sub(r"[^a-zA-Z0-9_-]", "", word)

        if not clean_word:
            corrected_words.append(word)
            continue

        best_match = None
        best_score = 0.0

        for wrong, correct in FUZZY_TERMS.items():
            score = SequenceMatcher(
                None,
                clean_word,
                wrong
            ).ratio()

            if score > best_score:
                best_score = score
                best_match = correct

        # Only correct when similarity is strong enough.
        if best_match and best_score >= 0.82:
            # Preserve punctuation attached to word
            prefix = ""
            suffix = ""

            if word and not word[0].isalnum():
                prefix = word[0]

            if word and not word[-1].isalnum():
                suffix = word[-1]

            corrected_words.append(
                prefix + best_match + suffix
            )
        else:
            corrected_words.append(word)

    text = " ".join(corrected_words)

    # Handle common joined phrases after fuzzy correction
    text = re.sub(
        r"\bdress\s*code\b",
        "dress code",
        text
    )

    text = re.sub(
        r"\bmess\s+menu\b",
        "mess menu",
        text
    )

    text = re.sub(
        r"\bbus\s+timing\b",
        "bus timing",
        text
    )

    text = re.sub(
        r"\bacademic\s+calendar\b",
        "academic calendar",
        text
    )

    return text.strip()


# ============================================================
# FUZZY COLLEGE TERM DETECTION
# ============================================================

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _has_fuzzy_college_term(query: str) -> bool:
    """
    Detects college-related words even when the user makes
    small spelling mistakes.
    """

    normalized = normalize_query(query)

    words = normalized.split()

    important_terms = [
        "prathyusha",
        "college",
        "campus",
        "dress",
        "menu",
        "mess",
        "bus",
        "transport",
        "academic",
        "calendar",
        "semester",
        "exam",
        "club",
        "placement",
        "internship",
        "scholarship",
        "bonafide",
        "id",
        "office",
        "event",
    ]

    for word in words:
        for term in important_terms:
            if len(word) >= 4 and len(term) >= 4:
                if _similarity(word, term) >= 0.82:
                    return True

    return False


# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_query_category(query: str) -> Optional[str]:
    """
    Detects the main CampusIQ knowledge category.

    Returns:
        dress_code
        mess_menu
        transportation
        academics
        None
    """

    normalized = normalize_query(query)

    # ----------------------------------------
    # DRESS CODE
    # ----------------------------------------

    dress_terms = [
        "dress",
        "dress code",
        "dresscode",
        "uniform",
        "formal",
        "formals",
        "casual",
        "casuals",
        "leggings",
        "ripped jeans",
        "salwar",
        "shawl",
    ]

    if any(term in normalized for term in dress_terms):
        return "dress_code"

    # ----------------------------------------
    # MESS MENU
    # ----------------------------------------

    menu_terms = [
        "mess",
        "mess menu",
        "menu",
        "breakfast",
        "lunch",
        "dinner",
        "snacks",
        "food",
    ]

    if any(term in normalized for term in menu_terms):
        return "mess_menu"

    # ----------------------------------------
    # TRANSPORTATION
    # ----------------------------------------

    transport_terms = [
        "bus",
        "bus timing",
        "bus timings",
        "bus route",
        "bus routes",
        "boarding",
        "boarding time",
        "transport",
        "transportation",
    ]

    if any(term in normalized for term in transport_terms):
        return "transportation"

    # ----------------------------------------
    # ACADEMICS
    # ----------------------------------------

    academic_terms = [
        "academic",
        "academics",
        "academic calendar",
        "calendar",
        "semester",
        "sem",
        "exam",
        "exams",
        "iat",
        "model exam",
        "practical exam",
        "end semester",
        "end sem",
        "university",
        "course",
        "courses",
        "subject",
        "subjects",
        "lesson",
        "lessons",
        "presentation",
        "presentations",
    ]

    if any(term in normalized for term in academic_terms):
        return "academics"

    return None


# ============================================================
# GENERAL EDUCATIONAL QUESTIONS
# ============================================================

GENERAL_EDUCATIONAL_PREFIXES = [
    "what is",
    "what are",
    "who is",
    "who are",
    "explain",
    "define",
    "meaning of",
    "difference between",
    "compare",
    "how does",
    "how do",
    "why does",
    "why do",
    "when was",
    "where is",
]


# ============================================================
# CLASSIFY INTENT
# ============================================================

def classify_intent(query: str) -> str:
    """
    Classifies the user's question as either:

        GENERAL_CONVERSATION

    or

        COLLEGE_KNOWLEDGE_QUERY
    """

    if not query:
        return INTENT_GENERAL

    normalized = normalize_query(query)

    if not normalized:
        return INTENT_GENERAL

    # ========================================================
    # GREETINGS
    # ========================================================

    for pattern in GREETING_PATTERNS:
        if re.fullmatch(pattern, normalized):
            return INTENT_GENERAL

    # ========================================================
    # POLITE / SHORT SOCIAL RESPONSES
    # ========================================================

    for pattern in POLITE_PATTERNS:
        if re.fullmatch(pattern, normalized):
            return INTENT_GENERAL

    # ========================================================
    # BOT IDENTITY
    # ========================================================

    for pattern in BOT_IDENTITY_PATTERNS:
        if re.search(pattern, normalized):
            return INTENT_GENERAL

    # ========================================================
    # COLLEGE CATEGORY DETECTION
    # ========================================================

    category = detect_query_category(normalized)

    if category is not None:
        return INTENT_COLLEGE

    # ========================================================
    # DIRECT COLLEGE KEYWORD DETECTION
    # ========================================================

    for keyword in COLLEGE_SPECIFIC_KEYWORDS:

        if keyword in normalized:
            return INTENT_COLLEGE

    # ========================================================
    # FUZZY COLLEGE TERM DETECTION
    # ========================================================

    if _has_fuzzy_college_term(normalized):
        return INTENT_COLLEGE

    # ========================================================
    # LOCATION / CAMPUS PHRASES
    # ========================================================

    college_phrases = [
        "in pec",
        "at pec",
        "of pec",
        "pec campus",
        "our college",
        "my college",
        "our campus",
        "my campus",
        "in prathyusha",
        "at prathyusha",
        "of prathyusha",
    ]

    for phrase in college_phrases:
        if phrase in normalized:
            return INTENT_COLLEGE

    # ========================================================
    # GENERAL EDUCATIONAL QUESTIONS
    # ========================================================

    # A question like:
    # "what is machine learning?"
    #
    # should remain general.
    for prefix in GENERAL_EDUCATIONAL_PREFIXES:
        if normalized.startswith(prefix):

            # If it also contains a college reference,
            # treat it as a college question.
            college_words = [
                "pec",
                "prathyusha",
                "college",
                "campus",
            ]

            if any(word in normalized for word in college_words):
                return INTENT_COLLEGE

            return INTENT_GENERAL

    # ========================================================
    # SHORT SOCIAL / CASUAL QUESTIONS
    # ========================================================

    casual_patterns = [
        r"^how are you$",
        r"^how r u$",
        r"^what's up$",
        r"^whats up$",
        r"^are you there$",
        r"^can you help me$",
        r"^help me$",
    ]

    for pattern in casual_patterns:
        if re.fullmatch(pattern, normalized):
            return INTENT_GENERAL

    # ========================================================
    # DEFAULT BEHAVIOR
    # ========================================================

    # Multi-word questions are usually knowledge questions.
    # This prevents CampusIQ from falling back unnecessarily.
    words = normalized.split()

    if len(words) >= 2:
        return INTENT_COLLEGE

    return INTENT_GENERAL


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_normalized_query(query: str) -> str:
    """
    Public helper for other CampusIQ modules.
    """
    return normalize_query(query)


def get_query_category(query: str) -> Optional[str]:
    """
    Public helper for other CampusIQ modules.
    """
    return detect_query_category(query)