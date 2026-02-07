"""SQLModel database models for Users and Tasks.

This module defines the database schema using SQLModel.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    """
    User model for authentication.

    This table is managed by Better Auth.
    """

    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: list["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Each task belongs to a user and tracks completion status.
    """

    __tablename__ = "tasks"

    # Primary key (UUID string)
    id: Optional[str] = Field(default=None, primary_key=True)

    # Foreign key to users
    user_id: str = Field(foreign_key="users.id", index=True)

    # Task data
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="Medium", max_length=10)  # High, Medium, Low
    tags: str = Field(default="", max_length=500)  # Comma-separated tags

    # Recurrence fields
    recurrence_pattern: Optional[str] = Field(default=None, max_length=10)  # None, Daily, Weekly, Monthly
    recurrence_interval: int = Field(default=1)  # How often (e.g., every 2 days)

    # Deadline field
    due_date: Optional[datetime] = Field(default=None, index=True)  # Optional deadline with date and time

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: User = Relationship(back_populates="tasks")
