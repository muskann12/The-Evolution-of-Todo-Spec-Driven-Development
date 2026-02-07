"""
SQLModel database models for User, Task, Conversation, and Message entities.

These models define the database schema and ORM behavior.

Phase II: User and Task models for todo application
Phase III: Conversation and Message models for AI chatbot
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import uuid4


def generate_uuid() -> str:
    """Generate UUID string for primary keys."""
    return str(uuid4())


class User(SQLModel, table=True):
    """
    User model for authentication.

    Table: users
    """

    __tablename__ = "users"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Table: tasks

    Spec Reference: @specs/database/todos-table.md
    """

    __tablename__ = "tasks"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="Medium", max_length=10, index=True)
    status: str = Field(default="ready", max_length=20, index=True)  # Kanban column: ready, in_progress, review, done
    tags: str = Field(default="")  # Stored as comma-separated string
    recurrence_pattern: Optional[str] = Field(default=None, max_length=10)
    recurrence_interval: int = Field(default=1)
    due_date: Optional[datetime] = Field(default=None, index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: User = Relationship(back_populates="tasks")


# ============================================================================
# PHASE III: AI CHATBOT MODELS
# ============================================================================


class Conversation(SQLModel, table=True):
    """
    Conversation model for AI chatbot conversations.

    Table: conversations

    CRITICAL: Stateless Architecture
    - ALL conversation state stored in this table
    - NO in-memory conversation storage
    - Server can restart without losing conversations
    - Horizontal scaling possible (multiple servers, same database)

    Spec Reference: @specs/database/conversations-table.md
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, index=True)

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    """
    Message model for conversation messages.

    Table: messages

    CRITICAL: Stateless Architecture
    - EVERY message (user, assistant, system, tool) stored here
    - Fetched from database on EVERY request
    - NO in-memory message caching
    - Supports conversation history retrieval

    Roles:
    - "user": User messages
    - "assistant": AI assistant responses
    - "system": System prompts
    - "tool": Tool execution results

    Spec Reference: @specs/database/messages-table.md
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20, index=True)  # user, assistant, system, tool
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationship
    conversation: Conversation = Relationship(back_populates="messages")
