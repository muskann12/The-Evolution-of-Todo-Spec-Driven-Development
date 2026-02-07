"""
SQLModel database models for User and Task entities.

These models define the database schema and ORM behavior.
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

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user")


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
