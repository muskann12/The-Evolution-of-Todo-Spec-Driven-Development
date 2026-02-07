# Skill: MCP Server Development

## Description
Build Model Context Protocol (MCP) servers using the Official MCP SDK for Python. Create stateless, secure tools that AI agents can call to interact with your TODO application backend.

## When to Use
- Building AI agent tools for backend operations
- Exposing database operations to AI models
- Creating reusable, testable tool implementations
- Implementing secure, user-isolated tool execution
- Integrating backend services with AI agents

## Prerequisites
- Python 3.10+
- Official MCP SDK installed
- Database models and CRUD operations defined
- Understanding of async/await patterns
- FastAPI or similar async framework

---

## Core Concepts

### What is MCP?
Model Context Protocol (MCP) is a standard for exposing tools and resources to AI models. An MCP server:
- Registers tools that AI agents can discover and call
- Handles tool execution with parameters
- Returns structured results to the AI
- Maintains security and user isolation

### MCP Tools Architecture
```
AI Agent (OpenAI) <-> MCP Client <-> MCP Server <-> Database
                                    (Your Tools)
```

### Key Principles
1. **Stateless**: Tools don't maintain state between calls
2. **User Isolation**: Every tool filters by user_id
3. **Structured Returns**: Always return JSON-serializable dicts
4. **Type Safety**: Use type hints for all parameters
5. **Error Handling**: Graceful errors with clear messages

---

## Setup

### 1. Install Official MCP SDK

```bash
# Install with UV
uv add mcp

# Or with pip
pip install mcp

# For development
uv add --dev pytest pytest-asyncio httpx
```

### 2. Project Structure

```
backend/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py              # MCP server initialization
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tasks.py           # Task-related tools
│   │   ├── search.py          # Search tools
│   │   └── analytics.py       # Analytics tools
│   ├── context.py             # Database context management
│   └── schemas.py             # Tool input/output schemas
├── tests/
│   └── mcp/
│       ├── test_task_tools.py
│       └── test_search_tools.py
└── main.py                    # FastAPI app with MCP integration
```

### 3. Dependencies

```python
# requirements.txt
mcp>=1.0.0
pydantic>=2.0.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
python-dotenv>=1.0.0
```

---

## Implementation

### 1. Server Initialization

```python
# mcp_server/server.py
from mcp import McpServer
from mcp.types import Tool, TextContent
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp_server = McpServer(name="todo-manager-server")

@mcp_server.tool()
async def example_tool(
    user_id: int,
    param: str
) -> Dict[str, Any]:
    """
    Example tool implementation.

    Args:
        user_id: User ID for authorization (ALWAYS REQUIRED FIRST)
        param: Tool parameter

    Returns:
        Dict with success status and result
    """
    return {
        "success": True,
        "result": f"Executed with {param}"
    }

# Export for use in other modules
__all__ = ["mcp_server"]
```

### 2. Database Context Management

```python
# mcp_server/context.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
import os

# Database engine (singleton)
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session for tool execution.

    Usage:
        async with get_db_session() as db:
            result = await crud_operation(db, user_id, ...)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database (create tables if needed)"""
    from app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Close database connections"""
    await engine.dispose()
```

### 3. Tool Schemas

```python
# mcp_server/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class ToolResponse(BaseModel):
    """Standard tool response format"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None

class TaskData(BaseModel):
    """Task data for responses"""
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    tags: List[str] = []
    due_date: Optional[str] = None
    created_at: str
    updated_at: str

class CreateTaskInput(BaseModel):
    """Input validation for create_task"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[str] = None
    recurrence: str = Field("none", pattern="^(none|daily|weekly|monthly)$")

    @validator("tags")
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return [tag.strip().lower() for tag in v if tag.strip()]

class UpdateTaskInput(BaseModel):
    """Input validation for update_task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, pattern="^(ready|in_progress|review|done)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    tags: Optional[List[str]] = None
    due_date: Optional[str] = None
```

### 4. Task Management Tools

```python
# mcp_server/tools/tasks.py
from mcp_server.server import mcp_server
from mcp_server.context import get_db_session
from mcp_server.schemas import ToolResponse, TaskData, CreateTaskInput, UpdateTaskInput
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import select
from app.models import Todo
import logging

logger = logging.getLogger(__name__)

@mcp_server.tool()
async def create_task(
    user_id: int,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    recurrence: str = "none"
) -> Dict[str, Any]:
    """
    Create a new TODO task.

    Args:
        user_id: User ID (required for authorization)
        title: Task title (required, max 200 chars)
        description: Task description (optional, max 2000 chars)
        priority: Priority level: low, medium, or high (default: medium)
        tags: List of tags for categorization (optional, max 10)
        due_date: Due date in ISO format YYYY-MM-DD (optional)
        recurrence: Recurrence pattern: none, daily, weekly, monthly (default: none)

    Returns:
        Dict with success status and created task data

    Example:
        {
            "success": true,
            "message": "Task created successfully",
            "data": {
                "id": 123,
                "title": "Finish report",
                "priority": "high",
                ...
            }
        }
    """
    try:
        # Validate input
        input_data = CreateTaskInput(
            title=title,
            description=description,
            priority=priority,
            tags=tags or [],
            due_date=due_date,
            recurrence=recurrence
        )

        async with get_db_session() as db:
            # Create task
            task = Todo(
                user_id=user_id,  # CRITICAL: Always set user_id
                title=input_data.title,
                description=input_data.description,
                priority=input_data.priority,
                tags=input_data.tags,
                due_date=datetime.fromisoformat(input_data.due_date) if input_data.due_date else None,
                recurrence=input_data.recurrence,
                status="ready",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(task)
            await db.flush()  # Get the ID
            await db.refresh(task)

            logger.info(f"Created task {task.id} for user {user_id}")

            return {
                "success": True,
                "message": f"Task '{task.title}' created successfully",
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence": task.recurrence,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }

    except ValueError as e:
        logger.warning(f"Validation error in create_task: {e}")
        return {
            "success": False,
            "error": "validation_error",
            "message": str(e)
        }
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        return {
            "success": False,
            "error": "internal_error",
            "message": "Failed to create task. Please try again."
        }

@mcp_server.tool()
async def get_tasks(
    user_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Retrieve TODO tasks with optional filters.

    Args:
        user_id: User ID (required for authorization)
        status: Filter by status (ready, in_progress, review, done)
        priority: Filter by priority (low, medium, high)
        tags: Filter by tags (returns tasks with ANY of these tags)
        limit: Maximum number of tasks to return (default: 20, max: 100)
        offset: Number of tasks to skip (for pagination)

    Returns:
        Dict with success status and list of tasks

    Example:
        {
            "success": true,
            "message": "Retrieved 5 tasks",
            "data": {
                "tasks": [...],
                "total": 5,
                "limit": 20,
                "offset": 0
            }
        }
    """
    try:
        # Validate limit
        limit = min(max(1, limit), 100)  # Between 1 and 100

        async with get_db_session() as db:
            # Build query with user_id filter (CRITICAL)
            query = select(Todo).where(Todo.user_id == user_id)

            # Apply filters
            if status:
                query = query.where(Todo.status == status)

            if priority:
                query = query.where(Todo.priority == priority)

            if tags:
                # Filter tasks that have any of the specified tags
                from sqlalchemy import func
                query = query.where(
                    func.array_overlap(Todo.tags, tags)
                )

            # Count total (before pagination)
            from sqlalchemy import func as sql_func
            count_query = select(sql_func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0

            # Apply pagination
            query = query.offset(offset).limit(limit)

            # Order by created_at descending
            query = query.order_by(Todo.created_at.desc())

            # Execute query
            result = await db.execute(query)
            tasks = result.scalars().all()

            logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")

            return {
                "success": True,
                "message": f"Retrieved {len(tasks)} task(s)",
                "data": {
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "status": task.status,
                            "priority": task.priority,
                            "tags": task.tags,
                            "due_date": task.due_date.isoformat() if task.due_date else None,
                            "recurrence": task.recurrence,
                            "created_at": task.created_at.isoformat(),
                            "updated_at": task.updated_at.isoformat()
                        }
                        for task in tasks
                    ],
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }
            }

    except Exception as e:
        logger.error(f"Error retrieving tasks: {e}", exc_info=True)
        return {
            "success": False,
            "error": "internal_error",
            "message": "Failed to retrieve tasks. Please try again."
        }

@mcp_server.tool()
async def update_task(
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing TODO task.

    Args:
        user_id: User ID (required for authorization)
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)
        priority: New priority (optional)
        tags: New tags list (optional, replaces existing)
        due_date: New due date in ISO format (optional)

    Returns:
        Dict with success status and updated task data

    Example:
        {
            "success": true,
            "message": "Task updated successfully",
            "data": {...}
        }
    """
    try:
        async with get_db_session() as db:
            # Get task with user_id filter (CRITICAL)
            query = select(Todo).where(
                Todo.id == task_id,
                Todo.user_id == user_id  # Ensure user owns this task
            )
            result = await db.execute(query)
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"Task {task_id} not found for user {user_id}")
                return {
                    "success": False,
                    "error": "not_found",
                    "message": f"Task {task_id} not found or you don't have permission to update it"
                }

            # Update fields if provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.status = status
            if priority is not None:
                task.priority = priority
            if tags is not None:
                task.tags = tags
            if due_date is not None:
                task.due_date = datetime.fromisoformat(due_date) if due_date else None

            task.updated_at = datetime.utcnow()

            await db.flush()
            await db.refresh(task)

            logger.info(f"Updated task {task_id} for user {user_id}")

            return {
                "success": True,
                "message": f"Task '{task.title}' updated successfully",
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }

    except ValueError as e:
        logger.warning(f"Validation error in update_task: {e}")
        return {
            "success": False,
            "error": "validation_error",
            "message": str(e)
        }
    except Exception as e:
        logger.error(f"Error updating task: {e}", exc_info=True)
        return {
            "success": False,
            "error": "internal_error",
            "message": "Failed to update task. Please try again."
        }

@mcp_server.tool()
async def delete_task(
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """
    Delete a TODO task permanently.

    Args:
        user_id: User ID (required for authorization)
        task_id: ID of the task to delete

    Returns:
        Dict with success status

    Example:
        {
            "success": true,
            "message": "Task deleted successfully"
        }
    """
    try:
        async with get_db_session() as db:
            # Get task with user_id filter (CRITICAL)
            query = select(Todo).where(
                Todo.id == task_id,
                Todo.user_id == user_id  # Ensure user owns this task
            )
            result = await db.execute(query)
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"Task {task_id} not found for user {user_id}")
                return {
                    "success": False,
                    "error": "not_found",
                    "message": f"Task {task_id} not found or you don't have permission to delete it"
                }

            task_title = task.title
            await db.delete(task)

            logger.info(f"Deleted task {task_id} for user {user_id}")

            return {
                "success": True,
                "message": f"Task '{task_title}' deleted successfully"
            }

    except Exception as e:
        logger.error(f"Error deleting task: {e}", exc_info=True)
        return {
            "success": False,
            "error": "internal_error",
            "message": "Failed to delete task. Please try again."
        }
```

### 5. Search Tools

```python
# mcp_server/tools/search.py
from mcp_server.server import mcp_server
from mcp_server.context import get_db_session
from typing import Dict, Any, Optional, List
from sqlalchemy import select, or_, func
from app.models import Todo
import logging

logger = logging.getLogger(__name__)

@mcp_server.tool()
async def search_tasks(
    user_id: int,
    query: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search TODO tasks by keyword in title or description.

    Args:
        user_id: User ID (required for authorization)
        query: Search query (searches in title and description)
        limit: Maximum number of results (default: 20, max: 50)

    Returns:
        Dict with success status and matching tasks

    Example:
        {
            "success": true,
            "message": "Found 3 matching tasks",
            "data": {
                "query": "report",
                "tasks": [...],
                "count": 3
            }
        }
    """
    try:
        if not query or len(query.strip()) < 2:
            return {
                "success": False,
                "error": "validation_error",
                "message": "Search query must be at least 2 characters"
            }

        # Validate limit
        limit = min(max(1, limit), 50)

        async with get_db_session() as db:
            # Build search query with user_id filter (CRITICAL)
            search_pattern = f"%{query.strip().lower()}%"

            query_stmt = select(Todo).where(
                Todo.user_id == user_id,  # User isolation
                or_(
                    func.lower(Todo.title).like(search_pattern),
                    func.lower(Todo.description).like(search_pattern)
                )
            ).limit(limit).order_by(Todo.updated_at.desc())

            result = await db.execute(query_stmt)
            tasks = result.scalars().all()

            logger.info(f"Search '{query}' found {len(tasks)} tasks for user {user_id}")

            return {
                "success": True,
                "message": f"Found {len(tasks)} matching task(s)",
                "data": {
                    "query": query,
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "status": task.status,
                            "priority": task.priority,
                            "tags": task.tags
                        }
                        for task in tasks
                    ],
                    "count": len(tasks)
                }
            }

    except Exception as e:
        logger.error(f"Error searching tasks: {e}", exc_info=True)
        return {
            "success": False,
            "error": "internal_error",
            "message": "Search failed. Please try again."
        }
```

### 6. Analytics Tools

```python
# mcp_server/tools/analytics.py
from mcp_server.server import mcp_server
from mcp_server.context import get_db_session
from typing import Dict, Any, Optional
from sqlalchemy import select, func
from app.models import Todo
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@mcp_server.tool()
async def get_task_analytics(
    user_id: int,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get analytics and insights about tasks.

    Args:
        user_id: User ID (required for authorization)
        days: Number of days to analyze (default: 30, max: 365)

    Returns:
        Dict with analytics data

    Example:
        {
            "success": true,
            "data": {
                "total_tasks": 45,
                "by_status": {...},
                "by_priority": {...},
                "completion_rate": 0.67,
                ...
            }
        }
    """
    try:
        # Validate days
        days = min(max(1, days), 365)
        date_from = datetime.utcnow() - timedelta(days=days)

        async with get_db_session() as db:
            # Get all tasks for user (CRITICAL: user_id filter)
            base_query = select(Todo).where(
                Todo.user_id == user_id,
                Todo.created_at >= date_from
            )

            result = await db.execute(base_query)
            tasks = result.scalars().all()

            # Calculate analytics
            total = len(tasks)

            # By status
            by_status = {}
            for status in ["ready", "in_progress", "review", "done"]:
                count = sum(1 for t in tasks if t.status == status)
                by_status[status] = count

            # By priority
            by_priority = {}
            for priority in ["low", "medium", "high"]:
                count = sum(1 for t in tasks if t.priority == priority)
                by_priority[priority] = count

            # Completion rate
            completed = by_status.get("done", 0)
            completion_rate = completed / total if total > 0 else 0

            # Most used tags
            tag_counts = {}
            for task in tasks:
                for tag in task.tags or []:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            top_tags = sorted(
                tag_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            # Overdue tasks
            now = datetime.utcnow()
            overdue = sum(
                1 for t in tasks
                if t.due_date and t.due_date < now and t.status != "done"
            )

            logger.info(f"Generated analytics for user {user_id}: {total} tasks")

            return {
                "success": True,
                "data": {
                    "period_days": days,
                    "total_tasks": total,
                    "by_status": by_status,
                    "by_priority": by_priority,
                    "completion_rate": round(completion_rate, 2),
                    "completed_tasks": completed,
                    "overdue_tasks": overdue,
                    "top_tags": [
                        {"tag": tag, "count": count}
                        for tag, count in top_tags
                    ]
                }
            }

    except Exception as e:
        logger.error(f"Error generating analytics: {e}", exc_info=True)
        return {
            "success": False,
            "error": "internal_error",
            "message": "Failed to generate analytics. Please try again."
        }
```

### 7. FastAPI Integration

```python
# main.py (FastAPI integration)
from fastapi import FastAPI, Depends
from mcp_server.server import mcp_server
from mcp_server.context import init_db, close_db
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="TODO Manager with MCP")

@app.on_event("startup")
async def startup():
    """Initialize database and MCP server on startup"""
    logger.info("Starting TODO Manager with MCP server")
    await init_db()
    logger.info("MCP server ready with tools:")
    for tool in mcp_server.list_tools():
        logger.info(f"  - {tool.name}")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down TODO Manager")
    await close_db()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mcp_tools": len(mcp_server.list_tools())}

@app.get("/mcp/tools")
async def list_mcp_tools():
    """List all available MCP tools"""
    tools = mcp_server.list_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema
            }
            for tool in tools
        ]
    }

@app.post("/mcp/execute")
async def execute_mcp_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    user_id: int  # From authentication middleware
) -> Dict[str, Any]:
    """
    Execute an MCP tool directly (for testing/debugging).

    In production, this would be called by the AI agent via MCP protocol.
    """
    try:
        # Ensure user_id is in parameters
        parameters["user_id"] = user_id

        # Execute tool
        result = await mcp_server.call_tool(tool_name, parameters)

        return result

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {
            "success": False,
            "error": "execution_error",
            "message": str(e)
        }
```

---

## Testing

### 1. Unit Tests for Tools

```python
# tests/mcp/test_task_tools.py
import pytest
from mcp_server.server import mcp_server
from mcp_server.context import get_db_session
from app.models import Todo, User
from datetime import datetime

@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash="hashed"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.mark.asyncio
async def test_create_task_success(test_user):
    """Test creating a task successfully"""
    result = await mcp_server.call_tool(
        "create_task",
        {
            "user_id": test_user.id,
            "title": "Test Task",
            "description": "Test description",
            "priority": "high"
        }
    )

    assert result["success"] is True
    assert "Task 'Test Task' created successfully" in result["message"]
    assert result["data"]["title"] == "Test Task"
    assert result["data"]["priority"] == "high"
    assert result["data"]["id"] is not None

@pytest.mark.asyncio
async def test_create_task_validation_error():
    """Test validation error on create"""
    result = await mcp_server.call_tool(
        "create_task",
        {
            "user_id": 1,
            "title": "",  # Empty title (invalid)
            "priority": "high"
        }
    )

    assert result["success"] is False
    assert result["error"] == "validation_error"

@pytest.mark.asyncio
async def test_get_tasks_user_isolation(test_user, db_session):
    """Test that users can only see their own tasks"""
    # Create task for test_user
    task1 = Todo(
        user_id=test_user.id,
        title="User 1 Task",
        status="ready",
        priority="medium"
    )
    db_session.add(task1)

    # Create task for another user
    task2 = Todo(
        user_id=999,  # Different user
        title="User 2 Task",
        status="ready",
        priority="medium"
    )
    db_session.add(task2)
    await db_session.commit()

    # Get tasks for test_user
    result = await mcp_server.call_tool(
        "get_tasks",
        {"user_id": test_user.id}
    )

    assert result["success"] is True
    assert len(result["data"]["tasks"]) == 1
    assert result["data"]["tasks"][0]["title"] == "User 1 Task"

@pytest.mark.asyncio
async def test_update_task_not_found(test_user):
    """Test updating non-existent task"""
    result = await mcp_server.call_tool(
        "update_task",
        {
            "user_id": test_user.id,
            "task_id": 99999,  # Non-existent
            "title": "Updated"
        }
    )

    assert result["success"] is False
    assert result["error"] == "not_found"

@pytest.mark.asyncio
async def test_delete_task_success(test_user, db_session):
    """Test deleting a task"""
    # Create task
    task = Todo(
        user_id=test_user.id,
        title="To Delete",
        status="ready",
        priority="low"
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Delete task
    result = await mcp_server.call_tool(
        "delete_task",
        {
            "user_id": test_user.id,
            "task_id": task.id
        }
    )

    assert result["success"] is True
    assert "deleted successfully" in result["message"]

@pytest.mark.asyncio
async def test_search_tasks(test_user, db_session):
    """Test searching tasks"""
    # Create tasks
    tasks = [
        Todo(user_id=test_user.id, title="Python Tutorial", status="ready", priority="medium"),
        Todo(user_id=test_user.id, title="JavaScript Guide", status="ready", priority="medium"),
        Todo(user_id=test_user.id, title="Learn Python", status="ready", priority="high")
    ]
    for task in tasks:
        db_session.add(task)
    await db_session.commit()

    # Search for "Python"
    result = await mcp_server.call_tool(
        "search_tasks",
        {
            "user_id": test_user.id,
            "query": "Python"
        }
    )

    assert result["success"] is True
    assert result["data"]["count"] == 2
    assert all("python" in task["title"].lower() for task in result["data"]["tasks"])

@pytest.mark.asyncio
async def test_analytics(test_user, db_session):
    """Test task analytics"""
    # Create various tasks
    tasks = [
        Todo(user_id=test_user.id, title="Task 1", status="done", priority="high"),
        Todo(user_id=test_user.id, title="Task 2", status="in_progress", priority="medium"),
        Todo(user_id=test_user.id, title="Task 3", status="ready", priority="low"),
        Todo(user_id=test_user.id, title="Task 4", status="done", priority="high"),
    ]
    for task in tasks:
        db_session.add(task)
    await db_session.commit()

    # Get analytics
    result = await mcp_server.call_tool(
        "get_task_analytics",
        {
            "user_id": test_user.id,
            "days": 30
        }
    )

    assert result["success"] is True
    assert result["data"]["total_tasks"] == 4
    assert result["data"]["by_status"]["done"] == 2
    assert result["data"]["completion_rate"] == 0.5
```

### 2. Integration Tests

```python
# tests/mcp/test_integration.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow: create, update, search, delete"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Health check
        response = await client.get("/health")
        assert response.status_code == 200

        # List tools
        response = await client.get("/mcp/tools")
        assert response.status_code == 200
        tools = response.json()["tools"]
        assert len(tools) > 0

        # Execute create_task
        response = await client.post(
            "/mcp/execute",
            json={
                "tool_name": "create_task",
                "parameters": {
                    "title": "Integration Test Task",
                    "priority": "high"
                },
                "user_id": 1
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        task_id = result["data"]["id"]

        # Update task
        response = await client.post(
            "/mcp/execute",
            json={
                "tool_name": "update_task",
                "parameters": {
                    "task_id": task_id,
                    "status": "done"
                },
                "user_id": 1
            }
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Search for task
        response = await client.post(
            "/mcp/execute",
            json={
                "tool_name": "search_tasks",
                "parameters": {
                    "query": "Integration"
                },
                "user_id": 1
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["count"] >= 1
```

---

## Best Practices

### 1. Always Filter by user_id

```python
# ✅ CORRECT: Always filter by user_id
query = select(Todo).where(
    Todo.id == task_id,
    Todo.user_id == user_id  # CRITICAL
)

# ❌ WRONG: Missing user_id filter (security vulnerability!)
query = select(Todo).where(Todo.id == task_id)
```

### 2. Keep Tools Stateless

```python
# ✅ CORRECT: Stateless tool
@mcp_server.tool()
async def create_task(user_id: int, title: str) -> Dict:
    async with get_db_session() as db:
        # All state in database
        task = Todo(user_id=user_id, title=title)
        db.add(task)
        return {"success": True, "data": {...}}

# ❌ WRONG: Stateful (global variable)
_task_cache = {}  # Don't do this!

@mcp_server.tool()
async def create_task(user_id: int, title: str) -> Dict:
    _task_cache[user_id] = title  # State outside database
    ...
```

### 3. Return Structured JSON

```python
# ✅ CORRECT: Return dict with consistent structure
return {
    "success": True,
    "message": "Task created",
    "data": {"id": 1, "title": "Task"}
}

# ❌ WRONG: Return arbitrary objects
return task  # SQLAlchemy object (not JSON-serializable)
```

### 4. Use Type Hints

```python
# ✅ CORRECT: Full type hints
@mcp_server.tool()
async def create_task(
    user_id: int,
    title: str,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    ...

# ❌ WRONG: No type hints
@mcp_server.tool()
async def create_task(user_id, title, tags=None):
    ...
```

### 5. Handle Errors Gracefully

```python
# ✅ CORRECT: Try-except with user-friendly messages
try:
    task = await get_task(task_id, user_id)
    if not task:
        return {
            "success": False,
            "error": "not_found",
            "message": "Task not found"
        }
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    return {
        "success": False,
        "error": "internal_error",
        "message": "Operation failed. Please try again."
    }

# ❌ WRONG: Let exceptions propagate
task = await get_task(task_id, user_id)  # Can raise!
```

### 6. Write Clear Docstrings

```python
# ✅ CORRECT: Complete docstring
@mcp_server.tool()
async def create_task(
    user_id: int,
    title: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a new TODO task.

    Args:
        user_id: User ID for authorization
        title: Task title (max 200 chars)
        priority: Priority level (low/medium/high)

    Returns:
        Dict with success status and task data
    """
    ...

# ❌ WRONG: No docstring or vague
@mcp_server.tool()
async def create_task(user_id: int, title: str) -> Dict:
    """Creates a task"""  # Too vague
    ...
```

---

## Common Pitfalls

### 1. Missing user_id Filter
```python
# 🚨 SECURITY ISSUE: Any user can access any task!
task = await db.get(Todo, task_id)  # Missing user check

# ✅ FIXED:
query = select(Todo).where(Todo.id == task_id, Todo.user_id == user_id)
task = (await db.execute(query)).scalar_one_or_none()
```

### 2. Not Handling None Results
```python
# 🐛 BUG: Will crash if task not found
task = await db.get(Todo, task_id)
return {"title": task.title}  # task might be None!

# ✅ FIXED:
task = await db.get(Todo, task_id)
if not task:
    return {"success": False, "error": "not_found"}
return {"success": True, "data": {"title": task.title}}
```

### 3. Returning Non-JSON Objects
```python
# 🐛 BUG: SQLAlchemy objects aren't JSON-serializable
return task  # Todo object

# ✅ FIXED:
return {
    "id": task.id,
    "title": task.title,
    ...
}
```

### 4. No Transaction Management
```python
# 🐛 BUG: Changes not committed
task = Todo(user_id=user_id, title=title)
db.add(task)
# Missing: await db.commit()

# ✅ FIXED: Use context manager
async with get_db_session() as db:
    task = Todo(user_id=user_id, title=title)
    db.add(task)
    # Auto-commits on context exit
```

---

## Deployment Checklist

- [ ] All tools have user_id as first parameter
- [ ] All database queries filter by user_id
- [ ] All tools return Dict[str, Any]
- [ ] All tools have type hints
- [ ] All tools have docstrings
- [ ] Error handling implemented in all tools
- [ ] Input validation using Pydantic
- [ ] Logging configured for debugging
- [ ] Tests written (unit + integration)
- [ ] Database connection pooling configured
- [ ] Environment variables set (.env)

---

## Resources

- [Official MCP SDK Documentation](https://modelcontextprotocol.io/docs)
- [MCP Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)

---

**Last Updated:** 2026-01-12
**Skill Version:** 1.0.0
**Recommended For:** Phase 3 AI Chatbot - MCP Server Development
