from typing import Optional, List, Any
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
