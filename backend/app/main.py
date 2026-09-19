import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import ASSETS_DIR, LOGO_PATH
from backend.app.database.db import init_db
from backend.app.api.chat import router as chat_router
from backend.app.api.voice import router as voice_router
from backend.app.api.knowledge import router as knowledge_router
from backend.app.rag.vectorstore import vectorstore_manager
from backend.app.api.knowledge import sync_knowledge_base

app = FastAPI(
    title="CampusIQ API",
    description="Production-grade AI-powered College Knowledge Assistant for Prathyusha Engineering College",
    version="2.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(knowledge_router)

@app.on_event("startup")
def startup_event():
    """Initialize database tables and verify vectorstore indexing on launch."""
    print("[CampusIQ] Initializing SQLite Conversation Database...")
    init_db()

    count = vectorstore_manager.get_collection_count()
    print(f"[CampusIQ] Current Qdrant Vector Count: {count}")
    if count == 0:
        print("[CampusIQ] Vectorstore is empty. Triggering initial knowledge base sync...")
        try:
            res = sync_knowledge_base()
            print(f"[CampusIQ] Initial sync complete: {res}")
        except Exception as e:
            print(f"[CampusIQ] Initial knowledge sync error: {e}")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "CampusIQ",
        "college": "Prathyusha Engineering College",
        "version": "2.0.0",
        "vectors_indexed": vectorstore_manager.get_collection_count(),
        "logo_available": LOGO_PATH.exists()
    }

# Mount compiled React frontend if present
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
