"""Task CRUD API endpoints.

This module implements all 6 required task endpoints with JWT authentication.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
import uuid

from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse
from middleware.auth import verify_jwt
from db import get_db


router = APIRouter()


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    status: str = "all",
    current_user: str = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    List all tasks for the authenticated user.

    Query params:
        status: Filter by completion status ("all", "pending", "completed")

    Returns:
        List[TaskResponse]: Array of tasks sorted by created_at DESC
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Order by newest first
    query = query.order_by(Task.created_at.desc())

    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: str = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task for the authenticated user.

    Returns:
        TaskResponse: Created task with 201 status
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Create task with generated UUID
    task = Task(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        priority=task_data.priority,
        tags=','.join(task_data.tags) if task_data.tags else '',
        recurrence_pattern=task_data.recurrence_pattern,
        recurrence_interval=task_data.recurrence_interval
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: str,
    current_user: str = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific task by ID.

    Returns:
        TaskResponse: Task details

    Raises:
        404: Task not found or doesn't belong to user
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Query task
    query = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: str,
    task_data: TaskUpdate,
    current_user: str = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing task.

    Returns:
        TaskResponse: Updated task

    Raises:
        404: Task not found or doesn't belong to user
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Find task
    query = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.tags is not None:
        task.tags = ','.join(task_data.tags) if task_data.tags else ''
    if task_data.recurrence_pattern is not None:
        task.recurrence_pattern = task_data.recurrence_pattern
    if task_data.recurrence_interval is not None:
        task.recurrence_interval = task_data.recurrence_interval

    # Update timestamp
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return task


@router.delete("/{task_id}")
async def delete_task(
    user_id: str,
    task_id: str,
    current_user: str = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a task.

    Returns:
        dict: Success message

    Raises:
        404: Task not found or doesn't belong to user
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Find task
    query = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Delete task
    await db.delete(task)
    await db.commit()

    return {"message": "Task deleted"}


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: str,
    task_id: str,
    current_user: str = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle task completion status.

    If task is recurring and being marked complete, creates next occurrence.

    Returns:
        TaskResponse: Updated task

    Raises:
        404: Task not found or doesn't belong to user
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Find task
    query = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if task is being marked complete and is recurring
    is_becoming_complete = not task.completed  # Was incomplete, now completing
    is_recurring = task.recurrence_pattern is not None

    # Toggle completion
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    # Auto-create next occurrence if task is recurring and was just completed
    if is_becoming_complete and is_recurring:
        # Create new task with same properties but not completed
        next_task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=task.title,
            description=task.description,
            completed=False,
            priority=task.priority,
            tags=task.tags,
            recurrence_pattern=task.recurrence_pattern,
            recurrence_interval=task.recurrence_interval
        )

        db.add(next_task)
        await db.commit()

    return task
