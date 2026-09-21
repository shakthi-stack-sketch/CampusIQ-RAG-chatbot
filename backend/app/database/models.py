from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class MessageBase(BaseModel):
    role: str
    content: str
    sources: Optional[List[dict]] = Field(default_factory=list)

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: str

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ConversationUpdate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    id: str
    user_id: Optional[str] = "default_student"
    title: str
    created_at: str
    updated_at: str
    messages: Optional[List[MessageResponse]] = Field(default_factory=list)

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    category_filter: Optional[str] = None
    platform_filter: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    user_message_id: str
    assistant_message_id: str
    answer: str
    sources: List[dict]
    title: Optional[str] = None

class SavedAnswerCreate(BaseModel):
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    question: str
    answer: str
    sources: Optional[List[dict]] = Field(default_factory=list)

class SavedAnswerResponse(BaseModel):
    id: str
    user_id: str
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    question: str
    answer: str
    sources: List[dict] = Field(default_factory=list)
    created_at: str

class VaultDocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    created_at: str

class VaultChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class VaultChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    vault_scoped: bool = True

class PulseItem(BaseModel):
    id: str
    title: str
    caption: str
    content_type: str
    publication_date: Optional[str] = None
    event_date: Optional[str] = None
    department: Optional[str] = None
    organizer: Optional[str] = None
    venue: Optional[str] = None
    source_platform: str
    source_url: Optional[str] = None
    original_url: Optional[str] = None
    verified: bool = True

class OpportunityItem(BaseModel):
    id: str
    title: str
    category: str
    source_platform: str
    date: Optional[str] = None
    description: str
    eligibility: Optional[str] = None
    application_link: Optional[str] = None
    department: Optional[str] = None
    venue: Optional[str] = None

# ==========================================
# AUTHENTICATION & USER PROFILE MODELS
# ==========================================

class UserSignupRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    profile: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserProfileUpdate(BaseModel):
    role: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    semester: Optional[str] = None
    interests: Optional[List[str]] = None

class ForgotPasswordRequest(BaseModel):
    email: str


