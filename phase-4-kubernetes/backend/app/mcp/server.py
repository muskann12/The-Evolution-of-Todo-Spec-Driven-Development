"""
Phase III: MCP (Model Context Protocol) Server

This module implements stateless MCP tools for AI agent interaction with the TODO application.

CRITICAL REQUIREMENTS:
1. Stateless: Tools MUST NOT maintain state between calls
2. user_id First: EVERY tool MUST accept user_id as first parameter
3. Database Filter: EVERY database query MUST filter by user_id
4. Return JSON: Tools MUST return Dict[str, Any], never arbitrary objects
5. Type Hints: All parameters MUST have type hints
6. Clear Descriptions: Docstrings MUST explain WHEN to use the tool
7. Error Handling: Tools MUST handle errors gracefully and return structured errors

MCP Tools:
1. add_task(user_id, title, description, priority, tags, due_date) - Create new task
2. list_tasks(user_id, status, priority, tags, limit) - Retrieve tasks with filters
3. update_task(user_id, task_id, title, description, status, priority) - Update existing task
4. complete_task(user_id, task_id) - Mark task as completed
5. delete_task(user_id, task_id) - Delete task permanently

Author: Claude Code
Date: 2026-01-13
Version: 1.0.0
"""

from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
from datetime import datetime

# MCP SDK imports
from mcp.server import Server
from mcp.types import Tool

# Database imports
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import async_session_maker

# Model imports (for future tool implementations)
from app.models import Task


# Initialize MCP Server
# This server provides stateless tools for the AI agent to manage TODO tasks
mcp_server = Server(name="todo-assistant")


# Database session context manager for MCP tools
@asynccontextmanager
async def get_db_session():
    """
    Get async database session for MCP tools.

    This context manager provides database access for MCP tools while maintaining
    stateless architecture. Each tool call gets a fresh session.

    Yields:
        AsyncSession: SQLModel async database session

    Example:
        async with get_db_session() as db:
            task = Task(user_id=user_id, title="Example")
            db.add(task)
            await db.commit()
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Tool registration dictionary
# Maps tool names to their handler functions
_tool_handlers: Dict[str, callable] = {}


def tool(name: str, description: str, input_schema: Dict[str, Any]):
    """
    Decorator for registering MCP tools.

    This decorator registers a function as an MCP tool that can be called by the AI agent.

    Args:
        name: Tool name (must match function name)
        description: Clear description of when agent should use this tool
        input_schema: JSON Schema describing tool parameters

    Returns:
        Decorator function that registers the tool

    Example:
        @tool(
            name="add_task",
            description="Create a new TODO task when user wants to add a task",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["user_id", "title"]
            }
        )
        async def add_task(user_id: str, title: str, description: str = None):
            ...
    """
    def decorator(func: callable):
        # Register tool with MCP server
        tool_obj = Tool(
            name=name,
            description=description,
            inputSchema=input_schema
        )

        # Store handler function
        _tool_handlers[name] = func

        # Return original function (allows normal calling)
        return func

    return decorator


# ============================================================================
# MCP TOOL IMPLEMENTATIONS
# ============================================================================

# Tool 1: add_task - Create a new TODO task
@tool(
    name="add_task",
    description=(
        "Create a new TODO task. Use when user wants to add/create a task. "
        "Extract details from user's message (title, priority, due date, tags)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID from JWT authentication (ALWAYS required first)"
            },
            "title": {
                "type": "string",
                "description": "Task title (required, max 200 characters)"
            },
            "description": {
                "type": "string",
                "description": "Task description (optional, max 1000 characters)"
            },
            "priority": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "Task priority (default: Medium)"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of tags"
            },
            "due_date": {
                "type": "string",
                "description": "Optional due date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            }
        },
        "required": ["user_id", "title"]
    }
)
async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: str = "Medium",
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new TODO task.

    This tool creates a new task for the authenticated user. It validates all inputs
    and ensures user isolation by setting the user_id.

    Args:
        user_id: User ID from JWT authentication (ALWAYS first parameter)
        title: Task title (required, max 200 characters)
        description: Task description (optional, max 1000 characters)
        priority: Task priority - "Low", "Medium", or "High" (default: "Medium")
        tags: Optional list of tags to categorize the task
        due_date: Optional due date in ISO 8601 format

    Returns:
        Dict with success status and task data:
        - On success: {"success": True, "data": {"id": str, "title": str, ...}}
        - On failure: {"success": False, "error": str}

    Examples:
        User: "Create a task to buy groceries"
        Agent calls: add_task(user_id="123", title="Buy groceries")

        User: "Add a high priority task for client meeting tomorrow"
        Agent calls: add_task(
            user_id="123",
            title="Client meeting",
            priority="High",
            due_date="2026-01-14"
        )
    """
    try:
        # Validate title length
        if not title or len(title) > 200:
            return {
                "success": False,
                "error": "Title is required and must be 200 characters or less"
            }

        # Validate description length
        if description and len(description) > 1000:
            return {
                "success": False,
                "error": "Description must be 1000 characters or less"
            }

        # Validate priority
        if priority not in ["Low", "Medium", "High"]:
            return {
                "success": False,
                "error": "Priority must be one of: Low, Medium, High"
            }

        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                # Try parsing ISO 8601 format
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid due_date format. Use ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
                }

        # Create task with database session
        async with get_db_session() as db:
            # Create new task
            task = Task(
                user_id=user_id,  # ✅ CRITICAL: User isolation
                title=title,
                description=description,
                priority=priority,
                tags=",".join(tags) if tags else "",
                due_date=parsed_due_date,
                completed=False,
                status="ready"  # Default Kanban status
            )

            db.add(task)
            await db.commit()
            await db.refresh(task)

            # Return success with task data
            return {
                "success": True,
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "tags": task.tags.split(",") if task.tags else [],
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.completed,
                    "status": task.status,
                    "created_at": task.created_at.isoformat()
                }
            }

    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }


# Tool 2: list_tasks - Retrieve tasks with filters
@tool(
    name="list_tasks",
    description=(
        "Retrieve tasks with optional filters. Use when user wants to see/list their tasks. "
        "Supports filtering by status (completed/incomplete), priority, and tags."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID from JWT authentication (ALWAYS required first)"
            },
            "status": {
                "type": "string",
                "enum": ["pending", "completed"],
                "description": "Filter by completion status (optional)"
            },
            "priority": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "Filter by priority (optional)"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by tags (optional)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of tasks to return (default: 20)"
            }
        },
        "required": ["user_id"]
    }
)
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Retrieve tasks with optional filters.

    This tool retrieves tasks for the authenticated user with optional filtering by
    completion status, priority, and tags. Results are limited to prevent excessive data.

    Args:
        user_id: User ID from JWT authentication (ALWAYS first parameter)
        status: Filter by status - "pending" (incomplete) or "completed" (optional)
        priority: Filter by priority - "Low", "Medium", or "High" (optional)
        tags: Filter by tags - tasks containing ANY of these tags (optional)
        limit: Maximum number of tasks to return (default: 20, max: 100)

    Returns:
        Dict with success status and array of tasks:
        - On success: {"success": True, "data": [{"id": str, "title": str, ...}, ...]}
        - On failure: {"success": False, "error": str}

    Examples:
        User: "Show me my tasks"
        Agent calls: list_tasks(user_id="123")

        User: "List my high priority tasks"
        Agent calls: list_tasks(user_id="123", priority="High")

        User: "Show completed tasks"
        Agent calls: list_tasks(user_id="123", status="completed")
    """
    try:
        # Validate limit
        if limit < 1 or limit > 100:
            return {
                "success": False,
                "error": "Limit must be between 1 and 100"
            }

        # Validate priority if provided
        if priority and priority not in ["Low", "Medium", "High"]:
            return {
                "success": False,
                "error": "Priority must be one of: Low, Medium, High"
            }

        # Validate status if provided
        if status and status not in ["pending", "completed"]:
            return {
                "success": False,
                "error": "Status must be one of: pending, completed"
            }

        # Retrieve tasks with database session
        async with get_db_session() as db:
            from sqlmodel import select, or_

            # Start with user filter
            statement = select(Task).where(Task.user_id == user_id)  # ✅ CRITICAL: User isolation

            # Apply status filter
            if status:
                statement = statement.where(
                    Task.completed == (status == "completed")
                )

            # Apply priority filter
            if priority:
                statement = statement.where(Task.priority == priority)

            # Apply tags filter (tasks containing ANY of the specified tags)
            if tags:
                tag_conditions = [Task.tags.contains(tag) for tag in tags]
                statement = statement.where(or_(*tag_conditions))

            # Apply limit
            statement = statement.limit(limit)

            # Execute query
            result = await db.execute(statement)
            tasks = result.scalars().all()

            # Return success with tasks data
            return {
                "success": True,
                "data": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority,
                        "tags": task.tags.split(",") if task.tags else [],
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "completed": task.completed,
                        "status": task.status,
                        "created_at": task.created_at.isoformat()
                    }
                    for task in tasks
                ],
                "count": len(tasks)
            }

    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Failed to retrieve tasks: {str(e)}"
        }


# Tool 3: update_task - Update existing task
@tool(
    name="update_task",
    description=(
        "Update an existing task. Use when user wants to modify task details. "
        "Only provided fields will be updated, others remain unchanged."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID from JWT authentication (ALWAYS required first)"
            },
            "task_id": {
                "type": "string",
                "description": "Task ID to update (required)"
            },
            "title": {
                "type": "string",
                "description": "New task title (optional, max 200 characters)"
            },
            "description": {
                "type": "string",
                "description": "New task description (optional, max 1000 characters)"
            },
            "status": {
                "type": "string",
                "enum": ["ready", "in_progress", "done"],
                "description": "New Kanban status (optional)"
            },
            "priority": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "New task priority (optional)"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "New list of tags (optional)"
            },
            "due_date": {
                "type": "string",
                "description": "New due date in ISO 8601 format (optional)"
            }
        },
        "required": ["user_id", "task_id"]
    }
)
async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task.

    This tool updates only the provided fields of an existing task. All other fields
    remain unchanged. Ensures user isolation by filtering by both user_id and task_id.

    Args:
        user_id: User ID from JWT authentication (ALWAYS first parameter)
        task_id: Task ID to update (required)
        title: New task title (optional, max 200 characters)
        description: New task description (optional, max 1000 characters)
        status: New Kanban status - "ready", "in_progress", or "done" (optional)
        priority: New task priority - "Low", "Medium", or "High" (optional)
        tags: New list of tags (optional)
        due_date: New due date in ISO 8601 format (optional)

    Returns:
        Dict with success status and updated task data:
        - On success: {"success": True, "data": {"id": str, "title": str, ...}}
        - On failure: {"success": False, "error": str}

    Examples:
        User: "Change the priority of task 5 to high"
        Agent calls: update_task(user_id="123", task_id="5", priority="High")

        User: "Update the title of my first task to 'Buy organic groceries'"
        Agent calls: update_task(user_id="123", task_id="1", title="Buy organic groceries")
    """
    try:
        # Validate at least one field to update
        if all(v is None for v in [title, description, status, priority, tags, due_date]):
            return {
                "success": False,
                "error": "At least one field must be provided to update"
            }

        # Validate title length if provided
        if title is not None and (not title or len(title) > 200):
            return {
                "success": False,
                "error": "Title must be between 1 and 200 characters"
            }

        # Validate description length if provided
        if description is not None and len(description) > 1000:
            return {
                "success": False,
                "error": "Description must be 1000 characters or less"
            }

        # Validate priority if provided
        if priority is not None and priority not in ["Low", "Medium", "High"]:
            return {
                "success": False,
                "error": "Priority must be one of: Low, Medium, High"
            }

        # Validate status if provided
        if status is not None and status not in ["ready", "in_progress", "done"]:
            return {
                "success": False,
                "error": "Status must be one of: ready, in_progress, done"
            }

        # Parse due_date if provided
        parsed_due_date = None
        if due_date is not None:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "error": "Invalid due_date format. Use ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
                }

        # Update task with database session
        async with get_db_session() as db:
            from sqlmodel import select

            # Find task with user_id filtering
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # ✅ CRITICAL: User isolation
            )
            result = await db.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or access denied"
                }

            # Update provided fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.status = status
                # Update completed flag if status is "done"
                if status == "done":
                    task.completed = True
            if priority is not None:
                task.priority = priority
            if tags is not None:
                task.tags = ",".join(tags)
            if parsed_due_date is not None:
                task.due_date = parsed_due_date

            # Update timestamp
            task.updated_at = datetime.utcnow()

            db.add(task)
            await db.commit()
            await db.refresh(task)

            # Return success with updated task data
            return {
                "success": True,
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "tags": task.tags.split(",") if task.tags else [],
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.completed,
                    "status": task.status,
                    "updated_at": task.updated_at.isoformat()
                }
            }

    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }


# Tool 4: complete_task - Mark task as completed
@tool(
    name="complete_task",
    description=(
        "Mark a task as completed. Use when user wants to complete/finish a task. "
        "Sets the completed flag to True and status to 'done'."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID from JWT authentication (ALWAYS required first)"
            },
            "task_id": {
                "type": "string",
                "description": "Task ID to mark as completed (required)"
            }
        },
        "required": ["user_id", "task_id"]
    }
)
async def complete_task(
    user_id: str,
    task_id: str
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    This tool marks a task as completed by setting the completed flag to True and
    status to "done". Ensures user isolation by filtering by both user_id and task_id.

    Args:
        user_id: User ID from JWT authentication (ALWAYS first parameter)
        task_id: Task ID to mark as completed (required)

    Returns:
        Dict with success status and updated task data:
        - On success: {"success": True, "data": {"id": str, "title": str, "completed": True, ...}}
        - On failure: {"success": False, "error": str}

    Examples:
        User: "Mark task 3 as done"
        Agent calls: complete_task(user_id="123", task_id="3")

        User: "Complete the groceries task"
        Agent calls: complete_task(user_id="123", task_id="groceries-id")
    """
    try:
        # Complete task with database session
        async with get_db_session() as db:
            from sqlmodel import select

            # Find task with user_id filtering
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # ✅ CRITICAL: User isolation
            )
            result = await db.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or access denied"
                }

            # Mark as completed
            task.completed = True
            task.status = "done"
            task.updated_at = datetime.utcnow()

            db.add(task)
            await db.commit()
            await db.refresh(task)

            # Return success with updated task data
            return {
                "success": True,
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "status": task.status,
                    "updated_at": task.updated_at.isoformat()
                },
                "message": f"Task '{task.title}' marked as completed"
            }

    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}"
        }


# Tool 5: delete_task - Delete task permanently
@tool(
    name="delete_task",
    description=(
        "Delete a task permanently. Use when user explicitly wants to delete/remove a task. "
        "This action is irreversible. Consider confirming with user before deletion."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID from JWT authentication (ALWAYS required first)"
            },
            "task_id": {
                "type": "string",
                "description": "Task ID to delete permanently (required)"
            }
        },
        "required": ["user_id", "task_id"]
    }
)
async def delete_task(
    user_id: str,
    task_id: str
) -> Dict[str, Any]:
    """
    Delete a task permanently.

    This tool permanently deletes a task from the database. This action is irreversible.
    The agent should consider confirming with the user before calling this tool.
    Ensures user isolation by filtering by both user_id and task_id.

    Args:
        user_id: User ID from JWT authentication (ALWAYS first parameter)
        task_id: Task ID to delete permanently (required)

    Returns:
        Dict with success status and deleted task info:
        - On success: {"success": True, "data": {"id": str, "title": str, "deleted": True}}
        - On failure: {"success": False, "error": str}

    Examples:
        User: "Delete task 7"
        Agent calls: delete_task(user_id="123", task_id="7")

        User: "Remove the groceries task"
        Agent calls: delete_task(user_id="123", task_id="groceries-id")

    Security:
        - CRITICAL: Only deletes tasks owned by the authenticated user
        - Returns error if task not found or user doesn't have access
        - Permanent deletion - cannot be undone
    """
    try:
        # Delete task with database session
        async with get_db_session() as db:
            from sqlmodel import select

            # Find task with user_id filtering
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # ✅ CRITICAL: User isolation
            )
            result = await db.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or access denied"
                }

            # Store task info before deletion
            task_info = {
                "id": task.id,
                "title": task.title,
                "deleted": True
            }

            # Delete task permanently
            await db.delete(task)
            await db.commit()

            # Return success with deleted task info
            return {
                "success": True,
                "data": task_info,
                "message": f"Task '{task.title}' has been permanently deleted"
            }

    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }


# ============================================================================
# ALL 5 MCP TOOLS IMPLEMENTED
# ============================================================================
# 1. add_task - Create new task
# 2. list_tasks - Retrieve tasks with filters
# 3. update_task - Update existing task
# 4. complete_task - Mark task as completed
# 5. delete_task - Delete task permanently
#
# All tools follow critical requirements:
# - user_id ALWAYS first parameter
# - ALL database queries filter by user_id
# - Return Dict[str, Any] with structured responses
# - Complete type hints and docstrings
# - Comprehensive error handling
# - Stateless (no global state)
# ============================================================================


# Export server instance and utilities
__all__ = [
    "mcp_server",
    "get_db_session",
    "tool",
    "_tool_handlers",
    "add_task",
    "list_tasks",
    "update_task",
    "complete_task",
    "delete_task",
]
