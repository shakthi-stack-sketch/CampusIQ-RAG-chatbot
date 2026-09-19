import sqlite3
import json
from contextlib import contextmanager
from backend.app.config import CONVERSATION_DB_PATH

def init_db():
    """Initialize SQLite tables for persistent conversation history."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Conversations Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'default_student',
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)
        
        # Performance Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conv_id ON messages(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_updated ON conversations(updated_at DESC)")
        conn.commit()

@contextmanager
def get_db_connection():
    """Context manager for SQLite connections with row factory."""
    conn = sqlite3.connect(str(CONVERSATION_DB_PATH))
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()
