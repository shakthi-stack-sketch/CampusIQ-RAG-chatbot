import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# ==========================================
# PATHS
# ==========================================
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "college_documents"
SOCIAL_MEDIA_DIR = DATA_DIR / "social_media"
VECTORSTORE_DIR = BASE_DIR / "vectorstore" / "qdrant"
CONVERSATION_DB_PATH = DATA_DIR / "campusiq_conversations.db"
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "college_logo.jpeg"

# Ensure directories exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
SOCIAL_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# CORE CREDENTIALS & MODELS
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash-lite")

# Qwen3-Embedding-8B (4096 dimensions)
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "Qwen/Qwen3-Embedding-8B")
EMBEDDING_DIMENSION = 4096
QWEN_EMBEDDING_API_URL = os.getenv("QWEN_EMBEDDING_API_URL", "")
QWEN_EMBEDDING_API_KEY = os.getenv("QWEN_EMBEDDING_API_KEY", "")

# Qdrant Vector Database
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "campusiq_college_knowledge")
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# Whisper Speech-to-Text
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

# ==========================================
# AUTHENTICATION & JWT SECURITY
# ==========================================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "campusiq-pec-super-secure-production-secret-key-2026-genlab-token")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", "30"))

# ==========================================
# VERIFIED OFFICIAL PEC SOURCES
# ==========================================
COLLEGE_NAME = "Prathyusha Engineering College"
COLLEGE_ACRONYM = "PEC"

OFFICIAL_SOURCES = {
    "linkedin": {
        "name": "Official PEC LinkedIn",
        "url": "https://www.linkedin.com/school/prathyushaenggcollege/",
    },
    "instagram": {
        "name": "Official PEC Instagram",
        "url": "https://www.instagram.com/prathyushainstitute/",
    },
    "youtube": {
        "name": "Official PEC YouTube",
        "url": "https://youtube.com/@prathyushaengineeringcollege/",
    },
    "website": {
        "name": "Official PEC Website",
        "url": "https://prathyusha.edu.in",
    },
    "documents": {
        "name": "Official College Documents",
        "url": "College Academic & Administrative Office",
    },
}
