# Claude Code Guide - FastAPI Backend

This document provides **FastAPI-specific guidance** for Claude Code when working on the backend of the Phase II-III Web Application (including AI Chatbot).

**IMPORTANT:** Always read the main navigation guide first: `@../CLAUDE.md`

---

## 1. STACK

### Technology Stack

**Phase II:**
- **FastAPI** (async/await for high performance)
- **SQLModel** (ORM combining SQLAlchemy + Pydantic)
- **Neon Serverless PostgreSQL** (asyncpg driver)
- **Pydantic** (data validation and serialization)
- **PyJWT** (JWT token verification)
- **Alembic** (database migrations)
- **UV** (Python package manager)

**Phase III (AI Chatbot):**
- **OpenAI Agents SDK** (AI agent orchestration and tool calling)
- **Official MCP SDK (Python)** (Stateless tool server implementation)
- **AsyncOpenAI Client** (Async Python client for OpenAI API)
- **Stateless Conversation Architecture** (All state persisted to PostgreSQL)

### Version Requirements

```toml
# pyproject.toml
[project]
name = "todo-backend"
version = "0.1.0"
requires-python = ">=3.13"

dependencies = [
    "fastapi>=0.109.0",
    "sqlmodel>=0.0.14",
    "asyncpg>=0.29.0",
    "pydantic>=2.5.0",
    "pyjwt>=2.8.0",
    "uvicorn[standard]>=0.27.0",
    "alembic>=1.13.0",
    "python-dotenv>=1.0.0",
]
```

### Development Environment

- **Python**: 3.13 or higher
- **Package Manager**: UV (mandatory)
- **Port**: http://localhost:8000 (development)
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Database**: Neon Serverless PostgreSQL

---

## 2. PROJECT STRUCTURE

### Folder Organization

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Environment configuration
│   ├── database.py                # Database connection & session
│   ├── models.py                  # SQLModel database models
│   ├── schemas.py                 # Pydantic request/response schemas
│   │
│   ├── routers/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── tasks.py              # Task CRUD endpoints
│   │   ├── auth.py               # Authentication endpoints
│   │   └── chat.py               # Chat endpoint (Phase III)
│   │
│   ├── middleware/                # Middleware components
│   │   ├── __init__.py
│   │   ├── auth.py               # JWT verification
│   │   └── cors.py               # CORS configuration
│   │
│   ├── dependencies/              # FastAPI dependencies
│   │   ├── __init__.py
│   │   ├── database.py           # Database session dependency
│   │   └── auth.py               # Auth dependencies
│   │
│   ├── mcp/                       # MCP Tools (Phase III)
│   │   ├── __init__.py
│   │   └── server.py             # MCP tool implementations
│   │
│   ├── ai/                        # AI Integration (Phase III)
│   │   ├── __init__.py
│   │   ├── agent.py              # OpenAI Agent integration
│   │   └── prompts.py            # System prompts for AI
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── logging.py            # Logging configuration
│       └── exceptions.py         # Custom exceptions
│
├── alembic/                       # Database migrations
│   ├── versions/                 # Migration files
│   ├── env.py                    # Alembic environment
│   └── script.py.mako            # Migration template
│
├── tests/                         # Backend tests
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── conftest.py               # Pytest configuration
│
├── .env                           # Environment variables (gitignored)
├── .env.example                   # Example environment file
├── alembic.ini                    # Alembic configuration
├── pyproject.toml                 # UV project configuration
├── CLAUDE.md                      # This file
└── README.md                      # Backend documentation
```

### Key Files

#### `main.py` - FastAPI App Entry Point

```python
"""
FastAPI application entry point with CORS and lifespan management.

[Task]: T-001
[Spec]: @../specs/api/main-api.md
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import tasks, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    # Close database connections if needed


app = FastAPI(
    title="Todo API",
    description="Task management API with authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Todo API is running"}
```

#### `models.py` - SQLModel Database Models

```python
"""
SQLModel database models.

[Task]: T-002
[Spec]: @../specs/database/schema.md
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model for authentication."""

    __tablename__ = "users"

    id: str = Field(primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    """Task model for todo items."""

    __tablename__ = "tasks"

    id: str = Field(primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default="Medium")  # High, Medium, Low
    tags: str = Field(default="")  # Comma-separated tags
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### `schemas.py` - Pydantic Request/Response Models

```python
"""
Pydantic schemas for request/response validation.

[Task]: T-003
[Spec]: @../specs/api/todos-endpoints.md
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(default="Medium")
    tags: list[str] = Field(default_factory=list)

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of the allowed values."""
        allowed = ['High', 'Medium', 'Low']
        if v not in allowed:
            raise ValueError(f'Priority must be one of {allowed}')
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[list[str]] = None


class TaskResponse(BaseModel):
    """Schema for task responses."""

    id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: list[str]
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

#### `database.py` - Database Connection

```python
"""
Database connection and session management.

[Task]: T-004
[Spec]: @../specs/database/connection.md
"""
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """
    Initialize database tables.

    Creates all tables defined in SQLModel models.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """
    Dependency for getting database sessions.

    Yields:
        AsyncSession: Database session
    """
    async with async_session() as session:
        yield session
```

#### `config.py` - Environment Configuration

```python
"""
Application configuration from environment variables.

[Task]: T-005
[Spec]: @../specs/config/environment.md
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database
    DATABASE_URL: str

    # Authentication
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: list[str]

    # Application
    DEBUG: bool = False

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


settings = Settings()
```

---

## 3. API CONVENTIONS

### Standard API Patterns

All API endpoints **MUST** follow these conventions:

#### 1. All Routes Under `/api/`

```python
# ✅ GOOD
@router.get("/api/{user_id}/tasks")

# ❌ BAD
@router.get("/tasks")
```

#### 2. Return JSON Responses

```python
# ✅ GOOD - Pydantic model automatically serialized to JSON
@router.get("/api/{user_id}/tasks", response_model=list[TaskResponse])
async def get_tasks(user_id: str):
    return tasks

# ❌ BAD - Plain dict without validation
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str):
    return {"tasks": tasks}
```

#### 3. Use Pydantic Models for Validation

```python
# ✅ GOOD - Request body validated
@router.post("/api/{user_id}/tasks", response_model=TaskResponse)
async def create_task(
    user_id: str,
    task: TaskCreate,  # Pydantic validation
):
    ...

# ❌ BAD - No validation
@router.post("/api/{user_id}/tasks")
async def create_task(user_id: str, data: dict):
    ...
```

#### 4. Handle Errors with HTTPException

```python
from fastapi import HTTPException

# ✅ GOOD - Proper error handling
if not task:
    raise HTTPException(
        status_code=404,
        detail=f"Task with ID {task_id} not found"
    )

# ❌ BAD - Generic exception
if not task:
    raise Exception("Task not found")
```

#### 5. Use Proper HTTP Status Codes

```python
# 200 OK - Successful GET, PUT, PATCH, DELETE
@router.get("/api/{user_id}/tasks/{id}", status_code=200)

# 201 Created - Successful POST
@router.post("/api/{user_id}/tasks", status_code=201)

# 204 No Content - Successful DELETE with no response body
@router.delete("/api/{user_id}/tasks/{id}", status_code=204)

# 400 Bad Request - Invalid input
raise HTTPException(status_code=400, detail="Invalid data")

# 401 Unauthorized - Missing/invalid token
raise HTTPException(status_code=401, detail="Unauthorized")

# 403 Forbidden - User not allowed to access resource
raise HTTPException(status_code=403, detail="Forbidden")

# 404 Not Found - Resource doesn't exist
raise HTTPException(status_code=404, detail="Task not found")
```

---

## 4. DATABASE

### SQLModel Operations

#### Use SQLModel for All Database Operations

```python
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Task


# ✅ GOOD - Async SQLModel operations
async def get_tasks(session: AsyncSession, user_id: str) -> list[Task]:
    """Get all tasks for a user."""
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()


async def create_task(
    session: AsyncSession,
    task_data: TaskCreate,
    user_id: str
) -> Task:
    """Create a new task."""
    task = Task(
        id=str(uuid.uuid4()),
        **task_data.model_dump(),
        user_id=user_id
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

### Async Operations with asyncpg

All database operations **MUST** be async:

```python
# ✅ GOOD - Async operations
async def get_task(session: AsyncSession, task_id: str) -> Task | None:
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# ❌ BAD - Sync operations
def get_task(session: Session, task_id: str) -> Task | None:
    return session.query(Task).filter(Task.id == task_id).first()
```

### Connection String from Environment

```python
# .env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Neon PostgreSQL example
DATABASE_URL=postgresql+asyncpg://user:password@ep-cool-smoke-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Connection Pooling

Connection pooling is managed automatically by SQLAlchemy:

```python
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,          # Default: 5 connections
    max_overflow=10,      # Allow up to 10 extra connections
    pool_pre_ping=True,   # Verify connections before using
)
```

### Security: Filter by user_id

**CRITICAL:** All queries **MUST** filter by `user_id` for security:

```python
# ✅ GOOD - Filters by user_id
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id  # REQUIRED for security
)

# ❌ BAD - No user_id filter (security vulnerability!)
statement = select(Task).where(Task.id == task_id)
```

---

## 5. AUTHENTICATION & AUTHORIZATION

### JWT Token Verification

Every API endpoint **MUST** require and verify JWT tokens:

#### Auth Dependency

```python
# app/dependencies/auth.py
"""
Authentication dependencies.

[Task]: T-006
[Spec]: @../specs/api/auth-endpoints.md
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.config import settings


security = HTTPBearer()


async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify JWT token and return payload.

    Args:
        credentials: HTTP Bearer token

    Returns:
        dict: Token payload containing user_id in 'sub' claim

    Raises:
        HTTPException: 401 if token invalid/missing/expired
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user_id(payload: dict = Depends(verify_jwt)) -> str:
    """
    Extract user_id from JWT payload.

    Args:
        payload: Verified JWT payload

    Returns:
        str: User ID from 'sub' claim
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    return user_id
```

#### Using Auth in Endpoints

```python
from app.dependencies.auth import get_current_user_id

@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all tasks for a user.

    Requires JWT token in Authorization header.
    User can only access their own tasks.
    """
    # Verify user_id matches token
    if user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Cannot access other users' tasks"
        )

    # Fetch tasks
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    tasks = result.scalars().all()

    return tasks
```

### Authorization Rules

**CRITICAL:** Users can ONLY access their own tasks:

```python
# ✅ GOOD - Verifies user owns the resource
if user_id != current_user_id:
    raise HTTPException(status_code=403, detail="Forbidden")

# ✅ GOOD - Filters by user_id in query
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == current_user_id
)

# ❌ BAD - No user_id verification
# Allows users to access other users' tasks!
```

### Required Headers

All authenticated endpoints require:

```http
Authorization: Bearer <jwt_token>
```

### Error Responses

```python
# 401 Unauthorized - Missing/invalid token
raise HTTPException(
    status_code=401,
    detail="Unauthorized: Invalid or missing token"
)

# 403 Forbidden - User_id mismatch
raise HTTPException(
    status_code=403,
    detail="Forbidden: Cannot access other users' resources"
)
```

---

## 6. API ENDPOINTS

### All 6 Required Endpoints

#### 1. GET `/api/{user_id}/tasks` - List User's Tasks

```python
@router.get("/api/{user_id}/tasks", response_model=list[TaskResponse])
async def get_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> list[Task]:
    """
    Get all tasks for a user.

    [Task]: T-007
    [Spec]: @../specs/api/todos-endpoints.md §1

    Args:
        user_id: User ID from URL
        current_user_id: User ID from JWT token
        session: Database session

    Returns:
        list[Task]: List of user's tasks

    Raises:
        HTTPException: 403 if user_id mismatch
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()
```

#### 2. POST `/api/{user_id}/tasks` - Create Task

```python
@router.post(
    "/api/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=201
)
async def create_task(
    user_id: str,
    task: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> Task:
    """
    Create a new task.

    [Task]: T-008
    [Spec]: @../specs/api/todos-endpoints.md §2
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    new_task = Task(
        id=str(uuid.uuid4()),
        **task.model_dump(),
        user_id=user_id,
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return new_task
```

#### 3. GET `/api/{user_id}/tasks/{id}` - Get Single Task

```python
@router.get("/api/{user_id}/tasks/{id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> Task:
    """
    Get a single task by ID.

    [Task]: T-009
    [Spec]: @../specs/api/todos-endpoints.md §3
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(
        Task.id == id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

#### 4. PUT `/api/{user_id}/tasks/{id}` - Update Task

```python
@router.put("/api/{user_id}/tasks/{id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    id: str,
    task_update: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> Task:
    """
    Update an existing task.

    [Task]: T-010
    [Spec]: @../specs/api/todos-endpoints.md §4
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(
        Task.id == id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task
```

#### 5. DELETE `/api/{user_id}/tasks/{id}` - Delete Task

```python
@router.delete("/api/{user_id}/tasks/{id}", status_code=204)
async def delete_task(
    user_id: str,
    id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Delete a task.

    [Task]: T-011
    [Spec]: @../specs/api/todos-endpoints.md §5
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(
        Task.id == id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()
```

#### 6. PATCH `/api/{user_id}/tasks/{id}/complete` - Toggle Completion

```python
@router.patch("/api/{user_id}/tasks/{id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> Task:
    """
    Toggle task completion status.

    [Task]: T-012
    [Spec]: @../specs/api/todos-endpoints.md §6
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(
        Task.id == id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task
```

---

## 7. ENVIRONMENT VARIABLES

### Required Environment Variables

Create a `.env` file in the backend directory:

```bash
# .env

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Neon PostgreSQL example
# DATABASE_URL=postgresql+asyncpg://user:password@ep-cool-smoke-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# Authentication (shared with frontend)
BETTER_AUTH_SECRET=your-secret-key-here

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,https://yourfrontend.com

# Optional
DEBUG=false
```

### Example Environment File

```bash
# .env.example

# Database - Neon Serverless PostgreSQL
DATABASE_URL=postgresql+asyncpg://username:password@hostname:5432/database

# Authentication - Must match frontend Better Auth secret
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# CORS - Allowed frontend origins (comma-separated)
CORS_ORIGINS=http://localhost:3000

# Debug mode (development only)
DEBUG=true
```

---

## 8. RUNNING THE SERVER

### Development

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Using UV (recommended)
uv run uvicorn app.main:app --reload --port 8000

# With specific host
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
# Production server (no reload, optimized)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using UV
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 9. CODE QUALITY

### Python 3.13+ with Type Hints

```python
# ✅ GOOD - Full type hints
async def get_tasks(
    session: AsyncSession,
    user_id: str
) -> list[Task]:
    """Get all tasks for a user."""
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()

# ❌ BAD - No type hints
async def get_tasks(session, user_id):
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()
```

### Google-Style Docstrings

```python
def create_task(session: AsyncSession, task_data: TaskCreate, user_id: str) -> Task:
    """
    Create a new task for a user.

    Args:
        session: Database session
        task_data: Task data to create
        user_id: User ID who owns the task

    Returns:
        Task: Created task object

    Raises:
        HTTPException: 400 if validation fails

    Example:
        >>> task = await create_task(session, task_data, "user123")
        >>> print(task.id)
        "task-uuid-here"
    """
    ...
```

### Async/Await for All I/O

```python
# ✅ GOOD - Async I/O operations
async def get_task(session: AsyncSession, task_id: str) -> Task | None:
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# ❌ BAD - Blocking I/O
def get_task(session: Session, task_id: str) -> Task | None:
    return session.query(Task).filter(Task.id == task_id).first()
```

### No Print Statements - Use Logging

```python
import logging

logger = logging.getLogger(__name__)

# ✅ GOOD - Use logging
logger.info(f"Task created: {task.id}")
logger.error(f"Failed to create task: {error}")
logger.debug(f"Processing task data: {task_data}")

# ❌ BAD - Print statements
print(f"Task created: {task.id}")
```

### Custom Exceptions

```python
# app/utils/exceptions.py

class TaskNotFoundError(Exception):
    """Raised when a task is not found."""
    pass


class UnauthorizedError(Exception):
    """Raised when user is not authorized."""
    pass


# Usage
try:
    task = await get_task(session, task_id)
    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")
except TaskNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

---

## 10. QUALITY CHECKLIST

Before submitting backend code, verify:

- [ ] All functions have type hints
- [ ] All I/O operations are async/await
- [ ] JWT authentication required on all endpoints
- [ ] User_id verification implemented
- [ ] All queries filter by user_id
- [ ] Pydantic models for request/response
- [ ] HTTPException for error handling
- [ ] Proper HTTP status codes used
- [ ] Google-style docstrings
- [ ] No print statements (use logging)
- [ ] Environment variables in config.py
- [ ] Database session properly managed
- [ ] Tests written and passing

---

## 11. QUICK REFERENCE

### Common Imports

```python
# FastAPI
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

# SQLModel
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession

# Pydantic
from pydantic import BaseModel, Field, field_validator

# Authentication
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# Standard library
from datetime import datetime
from typing import Optional
import uuid
import logging
```

### Common Commands

```bash
# Development
uv run uvicorn app.main:app --reload        # Start dev server

# Database migrations
alembic revision --autogenerate -m "msg"    # Create migration
alembic upgrade head                         # Apply migrations
alembic downgrade -1                         # Rollback one migration

# Testing
uv run pytest                                # Run all tests
uv run pytest -v                             # Verbose output
uv run pytest tests/unit                     # Unit tests only

# Dependencies
uv add package-name                          # Add dependency
uv sync                                      # Install dependencies
uv tree                                      # Show dependency tree
```

---

## 12. PHASE III: CHATBOT ARCHITECTURE

### Overview

Phase III adds an AI-powered chatbot that allows users to manage tasks through natural language conversations. The architecture is **completely stateless** - all conversation state is persisted to the PostgreSQL database.

### Stateless Request Cycle

Every chat request follows this 9-step cycle:

```
1. Receive chat request (message + optional conversation_id)
   ↓
2. Verify JWT and extract user_id
   ↓
3. Get or create conversation (from database)
   ↓
4. Fetch conversation history from database (last 20 messages)
   ↓
5. Build message array (history + new user message)
   ↓
6. Store user message in database
   ↓
7. Run OpenAI Agent with MCP tools
   - Agent analyzes message
   - Agent calls MCP tools if needed (add_task, list_tasks, etc.)
   - Agent generates natural language response
   ↓
8. Store assistant response in database
   ↓
9. Return response to client
```

**CRITICAL:** NO in-memory state. Everything fetched from and persisted to database on every request.

### Why Stateless Architecture?

**Benefits:**
- Server can restart without losing conversations
- Horizontal scaling (multiple servers, same database)
- Load balancers can route requests to any server
- No memory leaks from long-running conversations
- Cloud-native deployment ready

**Required Patterns:**
- ✅ Fetch conversation history from database on every request
- ✅ Store every message (user and assistant) in database
- ✅ All user_id filtering in database queries
- ❌ NO global dictionaries storing conversations
- ❌ NO in-memory session management
- ❌ NO caching conversation state

### Request Flow Example

```python
# POST /api/chat/message
# Request: {"message": "Create a task to buy groceries", "conversation_id": 123}

async def send_chat_message(
    request: ChatMessageRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    # Step 1-2: JWT verified, user_id extracted (by dependency)

    # Step 3: Get or create conversation
    conversation = await get_or_create_conversation(
        session, current_user_id, request.conversation_id
    )

    # Step 4: Fetch last 20 messages from database
    messages = await get_conversation_messages(
        session, conversation.id, limit=20
    )

    # Step 5: Build message array for AI
    message_array = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[{"role": m.role, "content": m.content} for m in messages],
        {"role": "user", "content": request.message}
    ]

    # Step 6: Store user message
    await store_message(
        session, conversation.id, "user", request.message
    )

    # Step 7: Run OpenAI Agent
    response = await run_agent(message_array, current_user_id)

    # Step 8: Store assistant response
    await store_message(
        session, conversation.id, "assistant", response
    )

    # Step 9: Return response
    return ChatMessageResponse(
        conversation_id=conversation.id,
        response=response
    )
```

---

## 13. MCP TOOLS IMPLEMENTATION

### Overview

MCP (Model Context Protocol) tools are Python functions that the AI agent can call to perform actions. Phase III requires 5 MCP tools for task management.

### Tool Requirements

**CRITICAL Requirements for ALL tools:**
1. **user_id ALWAYS first parameter** - Security critical
2. **Filter ALL database queries by user_id** - Prevents data leakage
3. **Return Dict[str, Any]** - Structured JSON response
4. **Include type hints** - For OpenAI function calling
5. **Clear docstring** - Explains when agent should use tool
6. **Handle errors gracefully** - Return structured error responses
7. **Completely stateless** - No global variables or caching

### Tool Implementation Pattern

```python
# app/mcp/server.py
from typing import Dict, Any, Optional, List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models import Task


# MCP Tool Server (using official MCP SDK)
from mcp.server import MCPServer

mcp_server = MCPServer()


@mcp_server.tool()
async def tool_name(
    user_id: str,        # ✅ ALWAYS first parameter
    param1: str,
    param2: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tool description explaining when agent should use it.

    Args:
        user_id: User ID (from JWT authentication)
        param1: Description of parameter
        param2: Optional parameter description

    Returns:
        Dict with 'success' boolean and 'data' or 'error'
    """
    try:
        async with get_session() as session:
            # Database operation
            # ALWAYS filter by user_id
            statement = select(Task).where(
                Task.user_id == user_id,  # ✅ CRITICAL: User isolation
                # ... other filters
            )
            result = await session.execute(statement)
            items = result.scalars().all()

            return {
                "success": True,
                "data": [item.dict() for item in items]
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### Tool 1: add_task

```python
@mcp_server.tool()
async def add_task(
    user_id: str,                    # ✅ ALWAYS first
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",        # "low", "medium", "high"
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None   # ISO 8601 format
) -> Dict[str, Any]:
    """
    Create a new TODO task. Use when user wants to add a task.

    Examples:
    - "Create a task to buy groceries"
    - "Add high priority task for client meeting"
    - "Remind me to call mom tomorrow"

    Args:
        user_id: User ID (from JWT)
        title: Task title (required)
        description: Optional task description
        priority: Task priority (low/medium/high)
        tags: Optional list of tags
        due_date: Optional due date (ISO 8601)

    Returns:
        Dict with success status and created task data
    """
    try:
        async with get_session() as session:
            task = Task(
                id=str(uuid.uuid4()),
                user_id=user_id,      # ✅ CRITICAL: User isolation
                title=title,
                description=description,
                priority=priority,
                tags=",".join(tags) if tags else "",
                due_date=datetime.fromisoformat(due_date) if due_date else None,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "success": True,
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }
```

### Tool 2: list_tasks

```python
@mcp_server.tool()
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,    # "pending", "completed"
    priority: Optional[str] = None,  # "low", "medium", "high"
    tags: Optional[List[str]] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Retrieve tasks with optional filters.

    Examples:
    - "Show me my tasks"
    - "List high priority tasks"
    - "Show completed tasks"

    Args:
        user_id: User ID (from JWT)
        status: Filter by status (pending/completed)
        priority: Filter by priority (low/medium/high)
        tags: Filter by tags
        limit: Maximum number of tasks to return

    Returns:
        Dict with success status and list of tasks
    """
    try:
        async with get_session() as session:
            statement = select(Task).where(
                Task.user_id == user_id  # ✅ CRITICAL: User isolation
            )

            # Apply filters
            if status:
                statement = statement.where(
                    Task.completed == (status == "completed")
                )
            if priority:
                statement = statement.where(Task.priority == priority)
            if tags:
                # Filter by tags (comma-separated in DB)
                for tag in tags:
                    statement = statement.where(Task.tags.contains(tag))

            statement = statement.limit(limit)

            result = await session.execute(statement)
            tasks = result.scalars().all()

            return {
                "success": True,
                "data": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "priority": task.priority,
                        "tags": task.tags.split(",") if task.tags else [],
                    }
                    for task in tasks
                ]
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}"
        }
```

### Tool 3: update_task

```python
@mcp_server.tool()
async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,     # "pending", "completed"
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task. Only provided fields are updated.

    Examples:
    - "Change task 5 priority to high"
    - "Update the title of my first task"

    Args:
        user_id: User ID (from JWT)
        task_id: Task ID to update
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)
        priority: New priority (optional)

    Returns:
        Dict with success status and updated task data
    """
    try:
        async with get_session() as session:
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # ✅ CRITICAL: User isolation
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or access denied"
                }

            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.completed = (status == "completed")
            if priority is not None:
                task.priority = priority

            task.updated_at = datetime.utcnow()

            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "success": True,
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "priority": task.priority,
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }
```

### Tool 4: complete_task

```python
@mcp_server.tool()
async def complete_task(
    user_id: str,
    task_id: str
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Examples:
    - "Mark task 3 as done"
    - "Complete the groceries task"

    Args:
        user_id: User ID (from JWT)
        task_id: Task ID to complete

    Returns:
        Dict with success status and updated task data
    """
    try:
        async with get_session() as session:
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # ✅ CRITICAL: User isolation
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or access denied"
                }

            task.completed = True
            task.updated_at = datetime.utcnow()

            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "success": True,
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}"
        }
```

### Tool 5: delete_task

```python
@mcp_server.tool()
async def delete_task(
    user_id: str,
    task_id: str
) -> Dict[str, Any]:
    """
    Delete a task permanently. Use with caution.

    Examples:
    - "Delete task 7"
    - "Remove the groceries task"

    Args:
        user_id: User ID (from JWT)
        task_id: Task ID to delete

    Returns:
        Dict with success status
    """
    try:
        async with get_session() as session:
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # ✅ CRITICAL: User isolation
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or access denied"
                }

            await session.delete(task)
            await session.commit()

            return {
                "success": True,
                "data": {
                    "id": task_id,
                    "deleted": True
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }
```

### MCP Tool Server Registration

```python
# app/mcp/server.py

# Export all tools for agent integration
def get_mcp_tools():
    """Get all registered MCP tools for OpenAI agent."""
    return [
        add_task,
        list_tasks,
        update_task,
        complete_task,
        delete_task,
    ]
```

---

## 14. OPENAI AGENT INTEGRATION

### Overview

The OpenAI Agent orchestrates conversations and calls MCP tools when needed. It uses the OpenAI Agents SDK with AsyncOpenAI client.

### Agent Setup

```python
# app/ai/agent.py
from openai import AsyncOpenAI
from typing import List, Dict, Any

from app.config import settings
from app.mcp.server import get_mcp_tools
from app.ai.prompts import TODO_ASSISTANT_SYSTEM_PROMPT


class TodoAgent:
    """OpenAI agent for todo task management."""

    def __init__(self):
        """Initialize OpenAI client and register MCP tools."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # or "gpt-4o-mini" for cost savings
        self.tools = self._register_tools()

    def _register_tools(self) -> List[Dict[str, Any]]:
        """
        Register MCP tools as OpenAI functions.

        Returns:
            List of tool definitions in OpenAI format
        """
        mcp_tools = get_mcp_tools()

        # Convert MCP tools to OpenAI function format
        tools = []
        for tool in mcp_tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.__name__,
                    "description": tool.__doc__,
                    "parameters": self._get_tool_parameters(tool)
                }
            })

        return tools

    def _get_tool_parameters(self, tool) -> Dict[str, Any]:
        """
        Extract parameter schema from tool function signature.

        Args:
            tool: MCP tool function

        Returns:
            OpenAI parameters schema
        """
        # Extract from function annotations
        import inspect
        sig = inspect.signature(tool)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == "user_id":
                continue  # Skip user_id (provided automatically)

            param_type = param.annotation
            if param_type == str:
                properties[param_name] = {"type": "string"}
            elif param_type == int:
                properties[param_name] = {"type": "integer"}
            elif param_type == bool:
                properties[param_name] = {"type": "boolean"}
            elif param_type == List[str]:
                properties[param_name] = {
                    "type": "array",
                    "items": {"type": "string"}
                }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    async def run(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        max_iterations: int = 5
    ) -> str:
        """
        Run agent with conversation messages.

        Args:
            messages: Conversation history with new user message
            user_id: User ID for MCP tool calls
            max_iterations: Maximum tool calling iterations

        Returns:
            Assistant's response text
        """
        current_messages = messages.copy()
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                tools=self.tools,
                tool_choice="auto"
            )

            message = response.choices[0].message
            current_messages.append(message.dict())

            # Check if agent wants to call tools
            if message.tool_calls:
                # Execute tool calls
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Add user_id to tool arguments
                    tool_args["user_id"] = user_id

                    # Execute tool
                    tool_result = await self._execute_tool(
                        tool_name, tool_args
                    )

                    # Add tool result to messages
                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })

                # Continue loop to get final response
                continue

            # No more tool calls - return final response
            return message.content

        # Max iterations reached
        return "I apologize, but I couldn't complete your request. Please try again."

    async def _execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute MCP tool by name.

        Args:
            tool_name: Tool function name
            tool_args: Tool arguments including user_id

        Returns:
            Tool execution result
        """
        from app.mcp.server import (
            add_task,
            list_tasks,
            update_task,
            complete_task,
            delete_task,
        )

        tools_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "update_task": update_task,
            "complete_task": complete_task,
            "delete_task": delete_task,
        }

        tool = tools_map.get(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        try:
            result = await tool(**tool_args)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }


# Singleton instance
_agent_instance = None

def get_agent() -> TodoAgent:
    """Get singleton agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TodoAgent()
    return _agent_instance
```

### System Prompt

```python
# app/ai/prompts.py

TODO_ASSISTANT_SYSTEM_PROMPT = """
You are a helpful TODO task assistant. You help users manage their tasks through natural language conversations.

Available MCP Tools:
1. add_task(user_id, title, description, priority, tags, due_date) - Create new task
2. list_tasks(user_id, status, priority, tags, limit) - Retrieve tasks with filters
3. update_task(user_id, task_id, title, description, status, priority) - Update existing task
4. complete_task(user_id, task_id) - Mark task as completed
5. delete_task(user_id, task_id) - Delete task permanently

Personality:
- Friendly and helpful
- Concise and action-oriented
- Professional but not robotic
- Encouraging for task completion

Response Format:
- Confirm what was done
- Show relevant details (task title, priority, etc.)
- Offer next steps if appropriate
- Use emojis sparingly (✅ ❌ 🎯 📅)

Tool Calling Guidelines:
- ALWAYS call tools to perform actions (don't just describe what would happen)
- When user asks to create/update/delete tasks, use the appropriate tool
- When user asks to see tasks, use list_tasks with appropriate filters
- After tool execution, confirm the action and show results

Examples:
User: "Create a task to buy groceries"
Assistant: [Calls add_task] "✅ I've created a task titled 'Buy groceries'. Would you like to set a due date or priority?"

User: "Show me my high priority tasks"
Assistant: [Calls list_tasks with priority="high"] "Here are your high priority tasks: ..."

User: "Mark task 3 as done"
Assistant: [Calls complete_task] "✅ Great! I've marked the task as completed. Keep up the good work!"
"""
```

---

## 15. CONVERSATION MODELS

### Database Models

Add these models to `app/models.py`:

```python
# app/models.py (additions to existing file)

class Conversation(SQLModel, table=True):
    """Conversation model for chat history."""

    __tablename__ = "conversations"

    id: int = Field(primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


class Message(SQLModel, table=True):
    """Message model for conversation messages."""

    __tablename__ = "messages"

    id: int = Field(primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # "user", "assistant", "system"
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Index for efficient queries
    __table_args__ = (
        {"indexes": [("conversation_id", "created_at")]},
    )
```

### Database Helpers

```python
# app/routers/chat.py (helper functions)

async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: Optional[int] = None
) -> Conversation:
    """
    Get existing conversation or create new one.

    Args:
        session: Database session
        user_id: User ID
        conversation_id: Optional conversation ID

    Returns:
        Conversation object
    """
    if conversation_id:
        # Get existing conversation
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id  # ✅ User isolation
        )
        result = await session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        return conversation
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            title="New Conversation"
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        return conversation


async def get_conversation_messages(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 20
) -> List[Message]:
    """
    Get last N messages from conversation.

    Args:
        session: Database session
        conversation_id: Conversation ID
        limit: Maximum messages to fetch

    Returns:
        List of messages in chronological order
    """
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.desc()
    ).limit(limit)

    result = await session.execute(statement)
    messages = result.scalars().all()

    # Reverse to get chronological order
    return list(reversed(messages))


async def store_message(
    session: AsyncSession,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    Store a message in the database.

    Args:
        session: Database session
        conversation_id: Conversation ID
        role: Message role ("user" or "assistant")
        content: Message content

    Returns:
        Created message object
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)

    return message
```

---

## 16. CHAT ENDPOINT

### Pydantic Schemas

```python
# app/schemas.py (additions)

class ChatMessageRequest(BaseModel):
    """Schema for chat message request."""

    conversation_id: Optional[int] = None
    message: str = Field(min_length=1, max_length=5000)


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""

    conversation_id: int
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
```

### Chat Router Implementation

```python
# app/routers/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.schemas import ChatMessageRequest, ChatMessageResponse
from app.ai.agent import get_agent
from app.ai.prompts import TODO_ASSISTANT_SYSTEM_PROMPT

router = APIRouter()


@router.post("/api/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Process chat message with stateless architecture.

    Stateless Cycle:
    1. Verify JWT and extract user_id (handled by dependency)
    2. Get or create conversation (from DB)
    3. Fetch conversation history (from DB)
    4. Store user message (to DB)
    5. Build message array for AI
    6. Run OpenAI Agent with MCP tools
    7. Store assistant response (to DB)
    8. Return response to client

    All state in PostgreSQL - server maintains NO memory.

    [Task]: T-CHAT-001
    [Spec]: @../speckit.specify §5.9 Feature 9 - Conversational Task Creation

    Args:
        request: Chat message request with message and optional conversation_id
        current_user_id: User ID from JWT token
        session: Database session

    Returns:
        ChatMessageResponse with conversation_id and AI response

    Raises:
        HTTPException: 401 if unauthorized, 404 if conversation not found
    """

    # STEP 2: Get or create conversation (stateless - from DB)
    conversation = await get_or_create_conversation(
        session, current_user_id, request.conversation_id
    )

    # STEP 3: Fetch conversation history (stateless - last 20 messages from DB)
    messages_history = await get_conversation_messages(
        session, conversation.id, limit=20
    )

    # STEP 4: Store user message (to DB)
    await store_message(
        session, conversation.id, "user", request.message
    )

    # STEP 5: Build message array for AI
    message_array = [
        {"role": "system", "content": TODO_ASSISTANT_SYSTEM_PROMPT}
    ]

    # Add history
    for msg in messages_history:
        message_array.append({
            "role": msg.role,
            "content": msg.content
        })

    # Add new user message
    message_array.append({
        "role": "user",
        "content": request.message
    })

    # STEP 6: Run OpenAI Agent with MCP tools
    agent = get_agent()
    try:
        response_text = await agent.run(
            messages=message_array,
            user_id=current_user_id
        )
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="AI service is currently unavailable"
        )

    # STEP 7: Store assistant response (to DB)
    await store_message(
        session, conversation.id, "assistant", response_text
    )

    # STEP 8: Return response to client
    return ChatMessageResponse(
        conversation_id=conversation.id,
        response=response_text
    )


# Register router in main.py
# app.include_router(chat.router, prefix="/api", tags=["chat"])
```

---

## 17. ENVIRONMENT VARIABLES (PHASE III)

### Updated Environment Variables

Add these to your `.env` file:

```bash
# .env

# Database (existing)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Authentication (existing)
BETTER_AUTH_SECRET=your-secret-key-here

# CORS (existing)
CORS_ORIGINS=http://localhost:3000,https://yourfrontend.com

# Phase III: OpenAI Integration
OPENAI_API_KEY=sk-proj-...your-openai-api-key-here

# Optional: MCP Server URL (if running separately)
# MCP_SERVER_URL=http://localhost:5000

# Optional: AI Model Selection
# OPENAI_MODEL=gpt-4o  # or gpt-4o-mini for cost savings

# Optional
DEBUG=false
```

### Updated Example File

```bash
# .env.example

# Database - Neon Serverless PostgreSQL
DATABASE_URL=postgresql+asyncpg://username:password@hostname:5432/database

# Authentication - Must match frontend Better Auth secret
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# CORS - Allowed frontend origins (comma-separated)
CORS_ORIGINS=http://localhost:3000

# Phase III: OpenAI API Key (required for chatbot)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# AI Model (optional, defaults to gpt-4o)
OPENAI_MODEL=gpt-4o-mini

# Debug mode (development only)
DEBUG=true
```

### Configuration Class Updates

```python
# app/config.py (additions)

class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database (existing)
    DATABASE_URL: str

    # Authentication (existing)
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # CORS (existing)
    CORS_ORIGINS: list[str]

    # Phase III: OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"

    # Optional: MCP Server
    MCP_SERVER_URL: Optional[str] = None

    # Application (existing)
    DEBUG: bool = False

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }
```

---

## 18. RUNNING THE SERVER (PHASE III)

### Development (Unchanged)

Phase III uses the same uvicorn command as Phase II:

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Using UV (recommended)
uv run uvicorn app.main:app --reload --port 8000

# With specific host
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Phase III Testing

```bash
# Test MCP tools
uv run pytest tests/test_mcp_tools.py -v

# Test AI agent
uv run pytest tests/test_ai_agent.py -v

# Test chat endpoint
uv run pytest tests/test_chat_endpoints.py -v

# Test user isolation (CRITICAL)
uv run pytest tests/test_user_isolation.py -v

# Test stateless architecture
uv run pytest tests/test_stateless.py -v

# Run all Phase III tests
uv run pytest tests/test_mcp*.py tests/test_ai*.py tests/test_chat*.py -v
```

### API Documentation

Phase III endpoints are automatically included in OpenAPI docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

Look for the "chat" tag in the API documentation.

---

## 19. CRITICAL CHATBOT REQUIREMENTS

### Stateless Architecture (NON-NEGOTIABLE)

**FORBIDDEN Patterns:**
```python
# ❌ WRONG - Global dictionary storing conversations
conversations_cache = {}

# ❌ WRONG - In-memory session management
user_sessions = {}

# ❌ WRONG - Caching conversation state
conversation_state = None
```

**REQUIRED Patterns:**
```python
# ✅ CORRECT - Fetch from database on every request
conversation = await get_or_create_conversation(session, user_id, conversation_id)

# ✅ CORRECT - Store to database immediately
await store_message(session, conversation.id, "user", message)

# ✅ CORRECT - All queries filter by user_id
statement = select(Task).where(Task.user_id == user_id)
```

### User Isolation (SECURITY CRITICAL)

**EVERY MCP tool MUST filter by user_id:**

```python
# ✅ CORRECT - Filters by user_id
@mcp_server.tool()
async def add_task(user_id: str, title: str) -> Dict[str, Any]:
    async with get_session() as session:
        task = Task(
            user_id=user_id,  # ✅ CRITICAL: User isolation
            title=title
        )
        session.add(task)
        await session.commit()
        return {"success": True, "data": {"id": task.id}}

# ❌ WRONG - No user_id filtering (SECURITY VULNERABILITY!)
@mcp_server.tool()
async def add_task(title: str) -> Dict[str, Any]:
    task = Task(title=title)  # ❌ No user_id!
    # This allows cross-user data leakage!
```

**Verification Checklist:**
- [ ] ALL MCP tools accept user_id as FIRST parameter
- [ ] ALL database queries filter by user_id
- [ ] Conversation queries filter by user_id
- [ ] Message queries filter by conversation_id (which is already user-filtered)
- [ ] No global variables storing user data
- [ ] No in-memory caching of conversations

### Error Handling

**Tool Execution Errors:**
```python
try:
    result = await tool(**tool_args)
    return result
except Exception as e:
    logger.error(f"Tool execution failed: {e}")
    return {
        "success": False,
        "error": f"Tool execution failed: {str(e)}"
    }
```

**OpenAI API Errors:**
```python
try:
    response = await client.chat.completions.create(...)
except openai.RateLimitError:
    raise HTTPException(
        status_code=429,
        detail="AI service rate limit reached. Please try again later."
    )
except openai.APIError as e:
    logger.error(f"OpenAI API error: {e}")
    raise HTTPException(
        status_code=500,
        detail="AI service is currently unavailable"
    )
```

**User-Friendly Error Messages:**
```python
# ✅ GOOD - User-friendly
raise HTTPException(
    status_code=500,
    detail="AI service is currently unavailable. Please try again."
)

# ❌ BAD - Technical details exposed
raise HTTPException(
    status_code=500,
    detail=f"OpenAI API error: {technical_error_message}"
)
```

### Testing Requirements

**Required Tests:**
1. **MCP Tools Tests** - Test each tool with valid inputs, user isolation, errors
2. **AI Agent Tests** - Test agent can call tools, handle multi-turn, recover from errors
3. **Chat Endpoint Tests** - Test stateless architecture, authentication, message persistence
4. **User Isolation Tests** - Verify User A cannot access User B's tasks/conversations
5. **Stateless Tests** - Restart server between requests, verify state persists

---

## 20. PHASE III QUALITY CHECKLIST

Before submitting Phase III backend code, verify:

**MCP Tools:**
- [ ] All tools accept user_id as FIRST parameter
- [ ] All tools filter database queries by user_id
- [ ] All tools return Dict[str, Any] with success/error
- [ ] All tools have type hints for all parameters
- [ ] All tools have clear docstrings
- [ ] All tools handle errors gracefully
- [ ] All tools are completely stateless

**OpenAI Agent:**
- [ ] Agent initialized with OpenAI API key
- [ ] Agent registers all 5 MCP tools
- [ ] Agent handles multi-turn tool calling (max 5 iterations)
- [ ] Agent passes user_id to all tool calls
- [ ] Agent handles OpenAI API errors gracefully

**Chat Endpoint:**
- [ ] JWT authentication required
- [ ] Stateless architecture (fetch from DB every request)
- [ ] User message stored to database
- [ ] Assistant response stored to database
- [ ] Conversation history fetched from database (last 20 messages)
- [ ] User isolation (conversation_id validation)
- [ ] Error handling for AI failures

**Database Models:**
- [ ] Conversation model with user_id foreign key
- [ ] Message model with conversation_id foreign key
- [ ] Indexes on user_id and conversation_id
- [ ] created_at and updated_at timestamps
- [ ] Alembic migration created and applied

**Environment:**
- [ ] OPENAI_API_KEY configured
- [ ] OpenAI model selection configured (gpt-4o or gpt-4o-mini)
- [ ] All existing Phase II env vars still work

**Testing:**
- [ ] MCP tools tests written and passing
- [ ] AI agent tests written and passing
- [ ] Chat endpoint tests written and passing
- [ ] User isolation tests written and passing
- [ ] Stateless architecture tests written and passing

---

**Project:** Phase II-III - Full-Stack Web Application with AI Chatbot
**Backend Stack:** FastAPI + SQLModel + Neon PostgreSQL + OpenAI Agents SDK + MCP
**Authentication:** JWT with Better Auth Secret
**Last Updated:** 2026-01-12
**Status:** Phase III - AI Chatbot Development
