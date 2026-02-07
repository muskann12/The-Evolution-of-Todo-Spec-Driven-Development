"""
Task CRUD router for managing todo items.

Spec Reference: @specs/features/task-crud.md
API Reference: @specs/api/todos-endpoints.md
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from datetime import datetime

from app.database import get_session
from app.models import User, Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, MessageResponse
from app.auth import get_current_user, verify_user_access


router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new task.

    Spec Reference: @specs/features/task-crud.md - FR-001

    Args:
        user_id: User ID from URL path
        task_data: Task creation data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Created task data

    Raises:
        403: User ID mismatch
    """
    # Verify user can access this resource
    verify_user_access(user_id, current_user)

    # Convert tags list to comma-separated string
    tags_str = ",".join(task_data.tags) if task_data.tags else ""

    # Create task
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority or "Medium",
        tags=tags_str,
        recurrence_pattern=task_data.recurrence_pattern,
        recurrence_interval=task_data.recurrence_interval or 1,
        due_date=task_data.due_date,
        user_id=current_user.id,
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return TaskResponse.from_orm(new_task)


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    List all user's tasks.

    Spec Reference: @specs/features/task-crud.md - FR-002

    Args:
        user_id: User ID from URL path
        current_user: Current authenticated user
        session: Database session

    Returns:
        List of tasks ordered by created_at (newest first)

    Raises:
        403: User ID mismatch
    """
    # Verify user can access this resource
    verify_user_access(user_id, current_user)

    # Query tasks for this user
    statement = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    result = await session.execute(statement)
    tasks = result.scalars().all()

    return [TaskResponse.from_orm(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: str = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a single task by ID.

    Spec Reference: @specs/features/task-crud.md - FR-003

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        current_user: Current authenticated user
        session: Database session

    Returns:
        Task data

    Raises:
        403: User ID mismatch
        404: Task not found
    """
    # Verify user can access this resource
    verify_user_access(user_id, current_user)

    # Query task
    statement = select(Task).where(
        Task.id == task_id, Task.user_id == current_user.id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    return TaskResponse.from_orm(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update an existing task.

    Spec Reference: @specs/features/task-crud.md - FR-004

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        task_data: Task update data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated task data

    Raises:
        403: User ID mismatch
        404: Task not found
    """
    # Verify user can access this resource
    verify_user_access(user_id, current_user)

    # Query task
    statement = select(Task).where(
        Task.id == task_id, Task.user_id == current_user.id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.status is not None:
        task.status = task_data.status
    if task_data.tags is not None:
        task.tags = ",".join(task_data.tags)
    if task_data.recurrence_pattern is not None:
        task.recurrence_pattern = task_data.recurrence_pattern
    if task_data.recurrence_interval is not None:
        task.recurrence_interval = task_data.recurrence_interval
    if task_data.due_date is not None:
        task.due_date = task_data.due_date

    # Update timestamp
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskResponse.from_orm(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a task permanently.

    Spec Reference: @specs/features/task-crud.md - FR-005

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        current_user: Current authenticated user
        session: Database session

    Returns:
        204 No Content on success

    Raises:
        403: User ID mismatch
        404: Task not found
    """
    # Verify user can access this resource
    verify_user_access(user_id, current_user)

    # Query task
    statement = select(Task).where(
        Task.id == task_id, Task.user_id == current_user.id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    # Delete task
    await session.delete(task)
    await session.commit()

    return None


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Toggle task completion status.

    Spec Reference: @specs/features/task-crud.md

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated task data

    Raises:
        403: User ID mismatch
        404: Task not found
    """
    # Verify user can access this resource
    verify_user_access(user_id, current_user)

    # Query task
    statement = select(Task).where(
        Task.id == task_id, Task.user_id == current_user.id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    # Toggle completed status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskResponse.from_orm(task)
