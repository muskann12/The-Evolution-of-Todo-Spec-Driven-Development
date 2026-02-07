"""
Pydantic schemas for request/response validation.

These schemas define the API contract between frontend and backend.
Spec Reference: @specs/api/todos-endpoints.md
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# ============================================================================
# User Schemas
# ============================================================================


class UserCreate(BaseModel):
    """Schema for user signup request."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses (no password)."""

    id: str
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Task Schemas
# ============================================================================


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Spec Reference: @specs/features/task-crud.md - FR-001
    """

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field("Medium", pattern="^(High|Medium|Low)$")
    status: Optional[str] = Field("ready", pattern="^(ready|in_progress|review|done)$")
    tags: Optional[List[str]] = Field(default_factory=list)
    recurrence_pattern: Optional[str] = Field(
        None, pattern="^(Daily|Weekly|Monthly|None)?$"
    )
    recurrence_interval: Optional[int] = Field(1, gt=0)
    due_date: Optional[datetime] = None

    @validator("recurrence_pattern", pre=True)
    def validate_recurrence_pattern(cls, v):
        """Convert empty string or 'None' to None."""
        if v == "" or v == "None":
            return None
        return v


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.

    Spec Reference: @specs/features/task-crud.md - FR-004
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(High|Medium|Low)$")
    status: Optional[str] = Field(None, pattern="^(ready|in_progress|review|done)$")
    tags: Optional[List[str]] = None
    recurrence_pattern: Optional[str] = Field(
        None, pattern="^(Daily|Weekly|Monthly|None)?$"
    )
    recurrence_interval: Optional[int] = Field(None, gt=0)
    due_date: Optional[datetime] = None

    @validator("recurrence_pattern", pre=True)
    def validate_recurrence_pattern(cls, v):
        """Convert empty string or 'None' to None."""
        if v == "" or v == "None":
            return None
        return v


class TaskResponse(BaseModel):
    """
    Schema for task data in responses.

    Spec Reference: @specs/features/task-crud.md - API Responses
    """

    id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    status: str  # Kanban column status
    tags: List[str]  # Converted from comma-separated string
    recurrence_pattern: Optional[str]
    recurrence_interval: int
    due_date: Optional[datetime]
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @validator("tags", pre=True)
    def parse_tags(cls, v):
        """Convert comma-separated string to list."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v or []


# ============================================================================
# Authentication Schemas
# ============================================================================


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded JWT token payload."""

    user_id: str
    email: str


# ============================================================================
# Generic Response Schemas
# ============================================================================


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str


# ============================================================================
# Phase III: Chat Schemas
# ============================================================================


class ChatMessageRequest(BaseModel):
    """
    Schema for chat message request.

    Phase III: AI Chatbot - Conversational task management.
    """

    conversation_id: Optional[int] = None
    message: str = Field(..., min_length=1, max_length=5000)


class ChatMessageResponse(BaseModel):
    """
    Schema for chat message response.

    Phase III: AI Chatbot - Contains AI assistant's response.
    """

    conversation_id: int
    response: str


class ConversationResponse(BaseModel):
    """
    Schema for conversation metadata.

    Phase III: AI Chatbot - List conversations for a user.
    """

    id: int
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """
    Schema for list of conversations.

    Phase III: AI Chatbot - User's conversation history.
    """

    conversations: List[ConversationResponse]
    total: int
