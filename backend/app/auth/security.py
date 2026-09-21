import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
import jwt
from fastapi import HTTPException, Header, status

from backend.app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_DAYS
from backend.app.database.db import get_db_connection

def hash_password(password: str) -> str:
    """Hash plain password using bcrypt salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve safe user dictionary by user ID from SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, profile, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        profile = {}
        if row["profile"]:
            try:
                profile = json.loads(row["profile"])
            except Exception:
                profile = {}

        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "profile": profile,
            "created_at": str(row["created_at"])
        }

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve user row (including password_hash) by email."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, password_hash, profile, created_at FROM users WHERE LOWER(email) = LOWER(?)",
            (email.strip(),)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        profile = {}
        if row["profile"]:
            try:
                profile = json.loads(row["profile"])
            except Exception:
                profile = {}

        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "password_hash": row["password_hash"],
            "profile": profile,
            "created_at": str(row["created_at"])
        }

def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract raw bearer token string from Authorization header."""
    if not authorization or not isinstance(authorization, str):
        return None
    parts = authorization.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for endpoints accessible by both Guests and Authenticated users.
    Returns safe user dict if a valid JWT is supplied; returns None for guests.
    """
    token = extract_token_from_header(authorization)
    if not token:
        return None
    
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    
    return get_user_by_id(payload["sub"])

def get_current_user_required(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    FastAPI dependency for protected personalized endpoints (Saved Answers, Vault).
    Strictly verifies JWT token; raises 401 Unauthorized if missing, expired, or invalid.
    """
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in to access this feature.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user
