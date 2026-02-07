"""
Pytest configuration and fixtures for backend tests.

Provides test database, client, and common fixtures for all tests.
"""
import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, create_engine, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import User, Task
from app.auth import hash_password, create_access_token


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client without authentication."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db: AsyncSession) -> dict:
    """Create a test user in the database."""
    import uuid

    user_id = str(uuid.uuid4())
    plain_password = "testpassword123"

    user = User(
        id=user_id,
        name="Test User",
        email="test@example.com",
        hashed_password=hash_password(plain_password)
    )

    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "plain_password": plain_password
    }


@pytest_asyncio.fixture(scope="function")
async def other_user(test_db: AsyncSession) -> dict:
    """Create another test user (for testing user isolation)."""
    import uuid

    user_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        name="Other User",
        email="other@example.com",
        hashed_password=hash_password("password456")
    )

    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }


@pytest_asyncio.fixture(scope="function")
async def auth_client(
    test_engine: AsyncEngine,
    test_user: dict
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with authentication."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    # Generate JWT token for test user
    token = create_access_token(data={"sub": test_user["id"], "email": test_user["email"]})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Set authorization header
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_tasks(test_db: AsyncSession, test_user: dict) -> list[dict]:
    """Create multiple test tasks for the test user."""
    import uuid
    from datetime import datetime

    tasks_data = [
        {
            "id": str(uuid.uuid4()),
            "title": "Test Task 1",
            "description": "Description 1",
            "completed": False,
            "priority": "High",
            "tags": "work,urgent",
            "status": "ready",
            "user_id": test_user["id"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Test Task 2",
            "description": "Description 2",
            "completed": True,
            "priority": "Medium",
            "tags": "personal",
            "status": "done",
            "user_id": test_user["id"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Test Task 3",
            "description": None,
            "completed": False,
            "priority": "Low",
            "tags": "",
            "status": "in_progress",
            "user_id": test_user["id"]
        }
    ]

    created_tasks = []

    for task_data in tasks_data:
        task = Task(**task_data)
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        created_tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": task.tags.split(",") if task.tags else [],
            "status": task.status,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        })

    return created_tasks


@pytest_asyncio.fixture(scope="function")
async def other_user_task(test_db: AsyncSession, other_user: dict) -> dict:
    """Create a task for the other user (for testing access control)."""
    import uuid

    task = Task(
        id=str(uuid.uuid4()),
        title="Other User's Task",
        description="This task belongs to other user",
        completed=False,
        priority="Medium",
        tags="",
        status="ready",
        user_id=other_user["id"]
    )

    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "user_id": task.user_id
    }


@pytest_asyncio.fixture(scope="function")
async def task_with_recurrence(test_db: AsyncSession, test_user: dict) -> dict:
    """Create a task with recurrence pattern."""
    import uuid

    task = Task(
        id=str(uuid.uuid4()),
        title="Daily Recurring Task",
        description="Repeats every day",
        completed=False,
        priority="Medium",
        tags="routine",
        status="ready",
        recurrence_pattern="Daily",
        recurrence_interval=1,
        user_id=test_user["id"]
    )

    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "recurrence_pattern": task.recurrence_pattern,
        "recurrence_interval": task.recurrence_interval
    }
