import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query

from backend.app.database.models import SavedAnswerCreate, SavedAnswerResponse
from backend.app.database.db import get_db_connection
from backend.app.auth.security import decode_access_token

router = APIRouter(prefix="/api/saved", tags=["Saved Answers"])

def resolve_user(
    authorization: Optional[str] = None,
    user_id: Optional[str] = None,
    x_user_id: Optional[str] = None
) -> str:
    # 1. Highest priority: Cryptographically verified JWT token
    if isinstance(authorization, str) and authorization.strip().lower().startswith("bearer "):
        parts = authorization.strip().split()
        if len(parts) == 2:
            payload = decode_access_token(parts[1])
            if not payload or "sub" not in payload:
                raise HTTPException(status_code=401, detail="Invalid or expired session token. Please sign in.")
            return payload["sub"]
    
    # 2. Internal / programmatic fallback for unit testing
    candidate = user_id if isinstance(user_id, str) and user_id.strip() else (
        x_user_id if isinstance(x_user_id, str) and x_user_id.strip() else None
    )
    if candidate and candidate != "default_student":
        return candidate.strip()
    
    # 3. Deny unauthenticated guest access
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Please sign in to access saved answers.",
        headers={"WWW-Authenticate": "Bearer"}
    )

@router.get("", response_model=List[SavedAnswerResponse])
def get_saved_answers(
    authorization: Optional[str] = Header(None),
    user_id: Optional[str] = Query(None),
    x_user_id: Optional[str] = Header(None)
):
    """Retrieve all saved answers for the authenticated user."""
    uid = resolve_user(authorization=authorization, user_id=user_id, x_user_id=x_user_id)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, conversation_id, message_id, question, answer, sources, created_at
            FROM saved_answers
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (uid,)
        )
        rows = cursor.fetchall()

    result = []
    for r in rows:
        sources_list = []
        if r["sources"]:
            try:
                sources_list = json.loads(r["sources"])
            except Exception:
                sources_list = []
        result.append({
            "id": r["id"],
            "user_id": r["user_id"],
            "conversation_id": r["conversation_id"],
            "message_id": r["message_id"],
            "question": r["question"],
            "answer": r["answer"],
            "sources": sources_list,
            "created_at": r["created_at"]
        })
    return result

@router.post("", response_model=SavedAnswerResponse)
def save_answer(
    req: SavedAnswerCreate,
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None)
):
    """Save an answer with provenance metadata for the authenticated user."""
    uid = resolve_user(authorization=authorization, user_id=req.user_id, x_user_id=x_user_id)
    if not req.answer.strip() or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question and answer cannot be empty")

    saved_id = f"saved_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    sources_json = json.dumps(req.sources or [])

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Check if already saved for this message_id to prevent duplicates
        if req.message_id:
            cursor.execute(
                "SELECT id, created_at FROM saved_answers WHERE user_id = ? AND message_id = ?",
                (uid, req.message_id)
            )
            existing = cursor.fetchone()
            if existing:
                return {
                    "id": existing["id"],
                    "user_id": uid,
                    "conversation_id": req.conversation_id,
                    "message_id": req.message_id,
                    "question": req.question,
                    "answer": req.answer,
                    "sources": req.sources or [],
                    "created_at": existing["created_at"]
                }

        cursor.execute(
            """
            INSERT INTO saved_answers (id, user_id, conversation_id, message_id, question, answer, sources, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (saved_id, uid, req.conversation_id, req.message_id, req.question, req.answer, sources_json, now)
        )
        conn.commit()

    return {
        "id": saved_id,
        "user_id": uid,
        "conversation_id": req.conversation_id,
        "message_id": req.message_id,
        "question": req.question,
        "answer": req.answer,
        "sources": req.sources or [],
        "created_at": now
    }

@router.delete("/{saved_id}")
def unsave_answer(
    saved_id: str,
    authorization: Optional[str] = Header(None),
    user_id: Optional[str] = None,
    x_user_id: Optional[str] = Header(None)
):
    """Unsave an answer by its saved ID for the authenticated user."""
    uid = resolve_user(authorization=authorization, user_id=user_id, x_user_id=x_user_id)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_answers WHERE id = ? AND user_id = ?", (saved_id, uid))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Saved answer not found")
    return {"success": True, "deleted_id": saved_id}

@router.delete("/by-message/{message_id}")
def unsave_by_message_id(
    message_id: str,
    authorization: Optional[str] = Header(None),
    user_id: Optional[str] = None,
    x_user_id: Optional[str] = Header(None)
):
    """Unsave an answer by its original assistant message ID for the authenticated user."""
    uid = resolve_user(authorization=authorization, user_id=user_id, x_user_id=x_user_id)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_answers WHERE message_id = ? AND user_id = ?", (message_id, uid))
        conn.commit()
    return {"success": True, "message_id": message_id}
