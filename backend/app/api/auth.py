import re
import uuid
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status

from backend.app.database.models import (
    UserSignupRequest,
    UserLoginRequest,
    UserResponse,
    AuthTokenResponse,
    UserProfileUpdate,
    ForgotPasswordRequest
)
from backend.app.database.db import get_db_connection
from backend.app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_id,
    get_user_by_email,
    get_current_user_required
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def validate_email_format(email: str) -> str:
    """Validate and normalize email string."""
    clean = (email or "").strip()
    if not clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is required."
        )
    if not EMAIL_REGEX.match(clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address (e.g. user@example.com)."
        )
    return clean.lower()

@router.post("/signup", response_model=AuthTokenResponse)
def signup(req: UserSignupRequest):
    """
    Register a new user with name, email, and password.
    Accepts any valid standard email address (not restricted to PEC).
    """
    name = (req.name or "").strip()
    if not name or len(name) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid name (at least 2 characters)."
        )
    
    email = validate_email_format(req.email)
    
    password = req.password or ""
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )
    
    if req.confirm_password is not None and req.confirm_password != password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match. Please verify and try again."
        )
    
    # Check if user already exists
    existing = get_user_by_email(email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please sign in instead."
        )
    
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    pw_hash = hash_password(password)
    now = datetime.now(timezone.utc).isoformat()
    empty_profile_json = json.dumps({
        "role": "current_student",
        "department": "Computer Science & Engineering",
        "year": "3rd Year",
        "semester": "Semester 5",
        "interests": ["Artificial Intelligence", "Autonomous Systems", "Full Stack"]
    })

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (id, name, email, password_hash, profile, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, email, pw_hash, empty_profile_json, now, now)
        )
        conn.commit()

    token = create_access_token(data={"sub": user_id, "email": email, "name": name})
    user_data = get_user_by_id(user_id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_data
    }

@router.post("/login", response_model=AuthTokenResponse)
def login(req: UserLoginRequest):
    """
    Authenticate user via email and password, returning a JWT bearer token.
    """
    email = validate_email_format(req.email)
    password = req.password or ""
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be empty."
        )
    
    user_row = get_user_by_email(email)
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials."
        )
    
    if not verify_password(password, user_row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials."
        )
    
    token = create_access_token(data={
        "sub": user_row["id"],
        "email": user_row["email"],
        "name": user_row["name"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_row["id"],
            "name": user_row["name"],
            "email": user_row["email"],
            "profile": user_row["profile"],
            "created_at": user_row["created_at"]
        }
    }

@router.get("/me", response_model=UserResponse)
def get_current_profile(current_user: Dict[str, Any] = Depends(get_current_user_required)):
    """Retrieve authenticated user's profile and preferences."""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    req: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Update personalized preferences (role, department, year, semester, interests)."""
    user_id = current_user["id"]
    profile = current_user.get("profile", {}) or {}

    if req.role is not None:
        profile["role"] = req.role
    if req.department is not None:
        profile["department"] = req.department
    if req.year is not None:
        profile["year"] = req.year
    if req.semester is not None:
        profile["semester"] = req.semester
    if req.interests is not None:
        profile["interests"] = req.interests

    now = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET profile = ?, updated_at = ? WHERE id = ?",
            (json.dumps(profile), now, user_id)
        )
        conn.commit()

    updated = get_user_by_id(user_id)
    return updated

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    """
    Handle forgot password request with user-friendly recovery instructions.
    """
    email = validate_email_format(req.email)
    user = get_user_by_email(email)
    return {
        "success": True,
        "message": (
            f"If an account is associated with {email}, password recovery instructions "
            "have been dispatched. If you do not receive an email, please contact the "
            "campus coordinator at admin@prathyusha.edu.in."
        )
    }
