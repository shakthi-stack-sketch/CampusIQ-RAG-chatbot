import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from backend.app.database.db import get_db_connection

def generate_smart_title(query: str) -> str:
    """Generate a clean, concise 3-5 word conversation title from user query."""
    q = query.strip()
    # Simple rule-based title extraction
    clean = q.rstrip("?.,!").strip()
    words = clean.split()
    
    # Remove common question filler prefixes
    lower_clean = clean.lower()
    prefixes = [
        "what is the", "what are the", "where can i find", "where can i get",
        "how do i", "how to", "tell me about the", "tell me about",
        "can you tell me", "is there any", "are there any", "when is the",
        "when are the", "which", "what"
    ]
    for p in sorted(prefixes, key=len, reverse=True):
        if lower_clean.startswith(p):
            clean = clean[len(p):].strip()
            break
            
    # Capitalize title words
    clean_words = clean.split()
    if clean_words:
        title = " ".join(clean_words[:5]).title()
    else:
        title = " ".join(words[:4]).title() if words else "Campus Inquiry"
        
    return title or "College Inquiry"

def create_conversation(title: str = "New Conversation", user_id: str = "default_student") -> Dict[str, Any]:
    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (conv_id, user_id, title, now, now)
        )
        conn.commit()
        
    return {
        "id": conv_id,
        "user_id": user_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
        "messages": []
    }

def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
        conv = cursor.fetchone()
        if not conv:
            return None
            
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
            (conv_id,)
        )
        msg_rows = cursor.fetchall()
        
        messages = []
        for m in msg_rows:
            sources = []
            if m["sources"]:
                try:
                    sources = json.loads(m["sources"])
                except Exception:
                    sources = []
            messages.append({
                "id": m["id"],
                "conversation_id": m["conversation_id"],
                "role": m["role"],
                "content": m["content"],
                "sources": sources,
                "created_at": m["created_at"]
            })
            
        return {
            "id": conv["id"],
            "user_id": conv["user_id"],
            "title": conv["title"],
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"],
            "messages": messages
        }

def list_conversations(search: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """List all conversations grouped into TODAY, YESTERDAY, EARLIER."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if search and search.strip():
            term = f"%{search.strip()}%"
            cursor.execute("""
                SELECT DISTINCT c.* FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.title LIKE ? OR m.content LIKE ?
                ORDER BY c.updated_at DESC
            """, (term, term))
        else:
            cursor.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
            
        rows = cursor.fetchall()
        
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    yesterday_start = today_start - timedelta(days=1)
    
    grouped: Dict[str, List[Dict[str, Any]]] = {
        "today": [],
        "yesterday": [],
        "earlier": []
    }
    
    for row in rows:
        conv_data = {
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
        
        try:
            # Parse ISO or SQLite timestamp
            ts_str = row["updated_at"].replace("Z", "+00:00")
            if " " in ts_str and "+" not in ts_str and "T" not in ts_str:
                conv_time = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
            else:
                conv_time = datetime.fromisoformat(ts_str)
                if conv_time.tzinfo is None:
                    conv_time = conv_time.replace(tzinfo=timezone.utc)
        except Exception:
            conv_time = now
            
        if conv_time >= today_start:
            grouped["today"].append(conv_data)
        elif conv_time >= yesterday_start:
            grouped["yesterday"].append(conv_data)
        else:
            grouped["earlier"].append(conv_data)
            
    return grouped

def update_conversation_title(conv_id: str, new_title: str) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
            (new_title.strip(), now, conv_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_conversation(conv_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        conn.commit()
        return cursor.rowcount > 0

def add_message(conv_id: str, role: str, content: str, sources: Optional[List[dict]] = None) -> Dict[str, Any]:
    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    sources_json = json.dumps(sources or [])
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (msg_id, conv_id, role, content, sources_json, now)
        )
        cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id))
        conn.commit()
        
    return {
        "id": msg_id,
        "conversation_id": conv_id,
        "role": role,
        "content": content,
        "sources": sources or [],
        "created_at": now
    }
