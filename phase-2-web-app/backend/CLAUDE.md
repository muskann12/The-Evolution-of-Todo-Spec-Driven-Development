# Claude Code Guide - FastAPI Backend

This document provides **FastAPI-specific guidance** for Claude Code when working on the backend of the Phase II Web Application.

**IMPORTANT:** Always read the main navigation guide first: `@../CLAUDE.md`

---

## 1. STACK

### Technology Stack

- **FastAPI** (async/await for high performance)
- **SQLModel** (ORM combining SQLAlchemy + Pydantic)
- **Neon Serverless PostgreSQL** (asyncpg driver)
- **Pydantic** (data validation and serialization)
- **PyJWT** (JWT token verification)
- **Alembic** (database migrations)
- **UV** (Python package manager)

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
│   │   └── auth.py               # Authentication endpoints
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

**Project:** Phase II - Full-Stack Web Application
**Backend Stack:** FastAPI + SQLModel + Neon PostgreSQL
**Authentication:** JWT with Better Auth Secret
**Last Updated:** 2025-12-31
**Status:** Ready for Development
