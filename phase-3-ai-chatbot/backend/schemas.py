"""Pydantic schemas for request/response validation.

This module defines schemas for API request bodies and responses.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(default="Medium")
    tags: list[str] = Field(default_factory=list)
    recurrence_pattern: Optional[str] = Field(default=None)
    recurrence_interval: int = Field(default=1, ge=1, le=365)
    due_date: Optional[datetime] = Field(default=None)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Validate that title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of the allowed values."""
        # Normalize to title case
        v = v.strip().capitalize()
        allowed = ['High', 'Medium', 'Low']
        if v not in allowed:
            raise ValueError(f'Priority must be one of: {", ".join(allowed)}')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize tags."""
        if not v:
            return []

        normalized_tags = []
        for tag in v:
            tag = tag.strip().lower()
            # Skip empty tags
            if not tag:
                continue
            # Check length
            if len(tag) > 20:
                raise ValueError('Each tag must be 1-20 characters')
            # Check format (letters, numbers, hyphens, underscores)
            if not all(c.isalnum() or c in '-_' for c in tag):
                raise ValueError('Tags can only contain letters, numbers, hyphens, and underscores')
            # Avoid duplicates
            if tag not in normalized_tags:
                normalized_tags.append(tag)

        return normalized_tags

    @field_validator('recurrence_pattern')
    @classmethod
    def validate_recurrence_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate recurrence pattern."""
        if v is None or v == "None":
            return None
        # Normalize to title case
        v = v.strip().capitalize()
        allowed = ['Daily', 'Weekly', 'Monthly']
        if v not in allowed:
            raise ValueError(f'Recurrence pattern must be one of: {", ".join(allowed)}, or None')
        return v

    @field_validator('recurrence_interval')
    @classmethod
    def validate_recurrence_interval(cls, v: int) -> int:
        """Validate recurrence interval."""
        if v < 1:
            raise ValueError('Recurrence interval must be at least 1')
        if v > 365:
            raise ValueError('Recurrence interval cannot exceed 365')
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[list[str]] = None
    recurrence_pattern: Optional[str] = None
    recurrence_interval: Optional[int] = Field(None, ge=1, le=365)
    due_date: Optional[datetime] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate that title is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority if provided."""
        if v is None:
            return None
        # Normalize to title case
        v = v.strip().capitalize()
        allowed = ['High', 'Medium', 'Low']
        if v not in allowed:
            raise ValueError(f'Priority must be one of: {", ".join(allowed)}')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate and normalize tags if provided."""
        if v is None:
            return None

        normalized_tags = []
        for tag in v:
            tag = tag.strip().lower()
            # Skip empty tags
            if not tag:
                continue
            # Check length
            if len(tag) > 20:
                raise ValueError('Each tag must be 1-20 characters')
            # Check format (letters, numbers, hyphens, underscores)
            if not all(c.isalnum() or c in '-_' for c in tag):
                raise ValueError('Tags can only contain letters, numbers, hyphens, and underscores')
            # Avoid duplicates
            if tag not in normalized_tags:
                normalized_tags.append(tag)

        return normalized_tags

    @field_validator('recurrence_pattern')
    @classmethod
    def validate_recurrence_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate recurrence pattern if provided."""
        if v is None or v == "None":
            return None
        # Normalize to title case
        v = v.strip().capitalize()
        allowed = ['Daily', 'Weekly', 'Monthly']
        if v not in allowed:
            raise ValueError(f'Recurrence pattern must be one of: {", ".join(allowed)}, or None')
        return v

    @field_validator('recurrence_interval')
    @classmethod
    def validate_recurrence_interval(cls, v: Optional[int]) -> Optional[int]:
        """Validate recurrence interval if provided."""
        if v is None:
            return None
        if v < 1:
            raise ValueError('Recurrence interval must be at least 1')
        if v > 365:
            raise ValueError('Recurrence interval cannot exceed 365')
        return v


class TaskResponse(BaseModel):
    """Schema for task responses."""

    id: str
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: list[str]
    recurrence_pattern: Optional[str]
    recurrence_interval: int
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('tags', mode='before')
    @classmethod
    def convert_tags_to_list(cls, v):
        """Convert comma-separated tags string to list."""
        if isinstance(v, str):
            if not v or v.strip() == '':
                return []
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v if v is not None else []


# Authentication Schemas

class LoginRequest(BaseModel):
    """Schema for login request."""

    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower().strip()


class SignupRequest(BaseModel):
    """Schema for signup request."""

    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower().strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserResponse(BaseModel):
    """Schema for user responses."""

    id: str
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    user: UserResponse
    token: str
