import os
import re
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import fitz  # PyMuPDF
from docx import Document as DocxDocument

from backend.app.config import DATA_DIR
from backend.app.database.db import get_db_connection
from backend.app.rag.generator import generate_vault_answer

USER_VAULT_ROOT = DATA_DIR / "user_vault"
USER_VAULT_ROOT.mkdir(parents=True, exist_ok=True)

def sanitize_user_id(user_id: str) -> str:
    """Sanitize user_id to prevent path traversal."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "_", user_id.strip())
    return cleaned or "default_student"

def get_user_vault_dir(user_id: str) -> Path:
    """Return secure, isolated directory for a specific user."""
    safe_uid = sanitize_user_id(user_id)
    user_dir = USER_VAULT_ROOT / safe_uid
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def parse_file_content(file_path: Path, filename: str) -> str:
    """Extract readable text from PDF, DOCX, or TXT."""
    ext = file_path.suffix.lower()
    text = ""
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read().strip()
        elif ext == ".pdf":
            doc = fitz.open(str(file_path))
            pages_text = []
            for p_idx, page in enumerate(doc):
                p_txt = page.get_text("text").strip()
                if p_txt:
                    pages_text.append(f"--- Page {p_idx + 1} ---\n{p_txt}")
            doc.close()
            text = "\n\n".join(pages_text)
        elif ext in [".docx", ".doc"]:
            doc = DocxDocument(str(file_path))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            table_lines = []
            for table in doc.tables:
                for row in table.rows:
                    cells = [c.text.strip() for c in row.cells if c.text.strip()]
                    if cells:
                        table_lines.append(" | ".join(cells))
            text = "\n".join(paragraphs + table_lines)
    except Exception as e:
        print(f"[VaultService] Error extracting text from {filename}: {e}")
        text = ""

    return text.strip()

def save_vault_document(user_id: str, filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """Save an isolated personal document for the authenticated user and extract text."""
    safe_uid = sanitize_user_id(user_id)
    user_dir = get_user_vault_dir(safe_uid)

    # Sanitize filename
    clean_filename = Path(filename).name
    clean_filename = re.sub(r"[^\w\s.-]", "_", clean_filename).strip()
    if not clean_filename:
        clean_filename = f"document_{uuid.uuid4().hex[:6]}.txt"

    doc_id = f"vdoc_{uuid.uuid4().hex[:12]}"
    file_path = user_dir / f"{doc_id}_{clean_filename}"

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Extract text content
    extracted_text = parse_file_content(file_path, clean_filename)
    if not extracted_text:
        extracted_text = f"Document: {clean_filename} (Uploaded file without readable text layer)"

    now = datetime.now(timezone.utc).isoformat()
    file_size = len(file_bytes)
    ext = Path(clean_filename).suffix.lstrip(".").lower() or "txt"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_vault_documents (id, user_id, filename, file_type, file_size, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (doc_id, safe_uid, clean_filename, ext, file_size, extracted_text, now)
        )
        conn.commit()

    return {
        "id": doc_id,
        "user_id": safe_uid,
        "filename": clean_filename,
        "file_type": ext,
        "file_size": file_size,
        "created_at": now
    }

def list_vault_documents(user_id: str) -> List[Dict[str, Any]]:
    """List documents belonging strictly to the specified user."""
    safe_uid = sanitize_user_id(user_id)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, filename, file_type, file_size, created_at
            FROM user_vault_documents
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (safe_uid,)
        )
        rows = cursor.fetchall()

    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "filename": r["filename"],
            "file_type": r["file_type"],
            "file_size": r["file_size"],
            "created_at": r["created_at"]
        }
        for r in rows
    ]

def delete_vault_document(user_id: str, doc_id: str) -> bool:
    """Delete a document belonging strictly to the specified user."""
    safe_uid = sanitize_user_id(user_id)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Verify ownership
        cursor.execute("SELECT filename FROM user_vault_documents WHERE id = ? AND user_id = ?", (doc_id, safe_uid))
        row = cursor.fetchone()
        if not row:
            return False

        cursor.execute("DELETE FROM user_vault_documents WHERE id = ? AND user_id = ?", (doc_id, safe_uid))
        conn.commit()

    # Remove file from disk
    user_dir = get_user_vault_dir(safe_uid)
    for p in user_dir.glob(f"{doc_id}_*"):
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass

    return True

def query_user_vault(user_id: str, query: str) -> Dict[str, Any]:
    """
    Search and answer queries strictly grounded in the authenticated user's personal vault.
    Guarantees strict isolation: Never accesses or returns documents from other users or official college knowledge.
    """
    safe_uid = sanitize_user_id(user_id)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, filename, file_type, content, created_at
            FROM user_vault_documents
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (safe_uid,)
        )
        rows = cursor.fetchall()

    if not rows:
        return {
            "answer": "No personal documents uploaded yet. Upload your timetable, notes, or syllabus in the Personal Knowledge Vault to ask questions about them.",
            "sources": [],
            "vault_scoped": True
        }

    # Keyword scoring across user's documents
    q_words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
    matched_sections = []
    matched_sources = []
    seen_files = set()

    for r in rows:
        doc_filename = r["filename"]
        doc_content = r["content"]
        content_lower = doc_content.lower()

        # Split into readable blocks
        paragraphs = [p.strip() for p in doc_content.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [doc_content]

        scored_blocks = []
        for p in paragraphs:
            p_lower = p.lower()
            score = sum(1 for w in q_words if w in p_lower)
            if score > 0 or not q_words:
                scored_blocks.append((score, p))

        scored_blocks.sort(key=lambda x: x[0], reverse=True)
        top_blocks = scored_blocks[:4] if scored_blocks else [(0, doc_content[:600])]

        for score, block in top_blocks:
            matched_sections.append(f"DOCUMENT: {doc_filename}\n{block}")

        if doc_filename not in seen_files:
            seen_files.add(doc_filename)
            matched_sources.append({
                "title": doc_filename,
                "platform": "Personal Knowledge Vault",
                "type": "my_document",
                "url": None
            })

    vault_context = "\n\n---\n\n".join(matched_sections[:8])
    answer = generate_vault_answer(query=query, vault_context=vault_context, user_id=safe_uid)

    return {
        "answer": answer,
        "sources": matched_sources,
        "vault_scoped": True
    }
