#!/usr/bin/env python3
"""
Phase III - Task AI-TEST-001: Test MCP Tools User Isolation

This test verifies that all 5 MCP tools properly isolate user data:
1. add_task - Creates tasks only for specified user
2. list_tasks - Returns only tasks for specified user
3. update_task - Updates only tasks owned by specified user
4. complete_task - Completes only tasks owned by specified user
5. delete_task - Deletes only tasks owned by specified user

Security Requirement: Users must NOT be able to access or modify other users' tasks.
"""

import asyncio
import sys
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, async_session_maker
from app.models import User, Task
from app.mcp.server import (
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)
from datetime import datetime, timedelta

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"{text}")
    print("=" * 70)


def print_test(text: str):
    """Print a test description."""
    print(f"\n{text}")


def print_pass(text: str = "PASS"):
    """Print a passing test result."""
    print(f"[✓] {text}")


def print_fail(text: str):
    """Print a failing test result and exit."""
    print(f"[✗] FAIL: {text}")
    exit(1)


async def setup_test_users() -> tuple[str, str]:
    """Create two test users for isolation testing."""
    print_test("Setting up test users...")

    async with async_session_maker() as session:
        # Clean up any existing test users
        result = await session.execute(
            select(User).where(User.email == "user1@test.com")
        )
        user1 = result.scalar_one_or_none()

        result = await session.execute(
            select(User).where(User.email == "user2@test.com")
        )
        user2 = result.scalar_one_or_none()

        if user1:
            # Delete user1's tasks first
            result = await session.execute(select(Task).where(Task.user_id == user1.id))
            tasks = result.scalars().all()
            for task in tasks:
                session.delete(task)
            session.delete(user1)

        if user2:
            # Delete user2's tasks first
            result = await session.execute(select(Task).where(Task.user_id == user2.id))
            tasks = result.scalars().all()
            for task in tasks:
                session.delete(task)
            session.delete(user2)

        await session.commit()

        # Create fresh test users
        user1 = User(
            id="test-user-1",
            name="Test User 1",
            email="user1@test.com",
            hashed_password="dummy-hash-1",
            created_at=datetime.utcnow(),
        )
        user2 = User(
            id="test-user-2",
            name="Test User 2",
            email="user2@test.com",
            hashed_password="dummy-hash-2",
            created_at=datetime.utcnow(),
        )

        session.add(user1)
        session.add(user2)
        await session.commit()
        await session.refresh(user1)
        await session.refresh(user2)

        print_pass(f"Created user1: {user1.id} ({user1.email})")
        print_pass(f"Created user2: {user2.id} ({user2.email})")

        return user1.id, user2.id


async def test_add_task_isolation(user1_id: str, user2_id: str):
    """Test that add_task creates tasks only for the specified user."""
    print_header("TEST 1: add_task - User Isolation")

    print_test("Creating task for user1...")
    result1 = await add_task(
        user_id=user1_id,
        title="User1's Task",
        description="This belongs to user1",
        priority="high",
        tags=["user1"],
    )

    if not result1.get("success"):
        print_fail(f"Failed to create task for user1: {result1.get('error', 'Unknown error')}")

    print_pass("Task created for user1")

    print_test("Creating task for user2...")
    result2 = await add_task(
        user_id=user2_id,
        title="User2's Task",
        description="This belongs to user2",
        priority="medium",
        tags=["user2"],
    )

    if not result2.get("success"):
        print_fail(f"Failed to create task for user2: {result2.get('error', 'Unknown error')}")

    print_pass("Task created for user2")

    # Verify in database
    async with async_session_maker() as session:
        result = await session.execute(
            select(Task).where(Task.user_id == user1_id)
        )
        user1_tasks = result.scalars().all()

        result = await session.execute(
            select(Task).where(Task.user_id == user2_id)
        )
        user2_tasks = result.scalars().all()

        if len(user1_tasks) != 1:
            print_fail(f"Expected 1 task for user1, found {len(user1_tasks)}")

        if len(user2_tasks) != 1:
            print_fail(f"Expected 1 task for user2, found {len(user2_tasks)}")

        if user1_tasks[0].title != "User1's Task":
            print_fail(f"User1's task title mismatch")

        if user2_tasks[0].title != "User2's Task":
            print_fail(f"User2's task title mismatch")

    print_pass("Tasks correctly isolated in database")


async def test_list_tasks_isolation(user1_id: str, user2_id: str):
    """Test that list_tasks returns only tasks for the specified user."""
    print_header("TEST 2: list_tasks - User Isolation")

    print_test("Listing tasks for user1...")
    result1 = await list_tasks(user_id=user1_id)

    if not result1.get("success"):
        print_fail(f"Failed to list tasks for user1: {result1.get('error', 'Unknown error')}")

    # Verify user1 sees only their task
    user1_tasks = result1.get("data", [])
    user1_titles = [task.get("title") for task in user1_tasks]

    if "User1's Task" not in user1_titles:
        print_fail("User1 cannot see their own task")

    if "User2's Task" in user1_titles:
        print_fail("SECURITY BREACH: User1 can see User2's task!")

    print_pass("User1 sees only their own task")

    print_test("Listing tasks for user2...")
    result2 = await list_tasks(user_id=user2_id)

    if not result2.get("success"):
        print_fail(f"Failed to list tasks for user2: {result2.get('error', 'Unknown error')}")

    # Verify user2 sees only their task
    user2_tasks = result2.get("data", [])
    user2_titles = [task.get("title") for task in user2_tasks]

    if "User2's Task" not in user2_titles:
        print_fail("User2 cannot see their own task")

    if "User1's Task" in user2_titles:
        print_fail("SECURITY BREACH: User2 can see User1's task!")

    print_pass("User2 sees only their own task")


async def test_update_task_isolation(user1_id: str, user2_id: str):
    """Test that update_task cannot update tasks owned by other users."""
    print_header("TEST 3: update_task - User Isolation")

    # Get task IDs
    async with async_session_maker() as session:
        result = await session.execute(
            select(Task).where(Task.user_id == user1_id)
        )
        user1_task = result.scalar_one_or_none()

        result = await session.execute(
            select(Task).where(Task.user_id == user2_id)
        )
        user2_task = result.scalar_one_or_none()

        user1_task_id = user1_task.id
        user2_task_id = user2_task.id

    print_test("User1 attempting to update their own task...")
    result = await update_task(
        user_id=user1_id,
        task_id=user1_task_id,
        title="User1's Updated Task",
    )

    if not result.get("success"):
        print_fail(f"User1 cannot update their own task: {result.get('error', 'Unknown error')}")

    print_pass("User1 successfully updated their own task")

    print_test("User1 attempting to update User2's task (should fail)...")
    result = await update_task(
        user_id=user1_id,
        task_id=user2_task_id,
        title="HACKED!",
    )

    # This should fail or return error
    if result.get("success"):
        # Verify in database that the task was NOT updated
        async with async_session_maker() as session:
            task = await session.get(Task, user2_task_id)
            if task and task.title == "HACKED!":
                print_fail("SECURITY BREACH: User1 updated User2's task!")

    print_pass("User1 cannot update User2's task (secure)")

    # Verify user2's task is unchanged
    async with async_session_maker() as session:
        task = await session.get(Task, user2_task_id)
        if task.title != "User2's Task":
            print_fail("User2's task was modified!")

    print_pass("User2's task remains unchanged")


async def test_complete_task_isolation(user1_id: str, user2_id: str):
    """Test that complete_task cannot complete tasks owned by other users."""
    print_header("TEST 4: complete_task - User Isolation")

    # Get task IDs
    async with async_session_maker() as session:
        result = await session.execute(
            select(Task).where(Task.user_id == user1_id)
        )
        user1_task = result.scalar_one_or_none()

        result = await session.execute(
            select(Task).where(Task.user_id == user2_id)
        )
        user2_task = result.scalar_one_or_none()

        user1_task_id = user1_task.id
        user2_task_id = user2_task.id

    print_test("User2 attempting to complete their own task...")
    result = await complete_task(user_id=user2_id, task_id=user2_task_id)

    if not result.get("success"):
        print_fail(f"User2 cannot complete their own task: {result.get('error', 'Unknown error')}")

    # Verify task is completed
    async with async_session_maker() as session:
        task = await session.get(Task, user2_task_id)
        if not task.completed:
            print_fail("User2's task was not marked as completed")

    print_pass("User2 successfully completed their own task")

    print_test("User2 attempting to complete User1's task (should fail)...")
    result = await complete_task(user_id=user2_id, task_id=user1_task_id)

    # This should fail or return error
    if result.get("success"):
        # Verify in database that the task was NOT completed
        async with async_session_maker() as session:
            task = await session.get(Task, user1_task_id)
            if task and task.completed:
                print_fail("SECURITY BREACH: User2 completed User1's task!")

    print_pass("User2 cannot complete User1's task (secure)")

    # Verify user1's task is still incomplete
    async with async_session_maker() as session:
        task = await session.get(Task, user1_task_id)
        if task.completed:
            print_fail("User1's task was modified!")

    print_pass("User1's task remains incomplete")


async def test_delete_task_isolation(user1_id: str, user2_id: str):
    """Test that delete_task cannot delete tasks owned by other users."""
    print_header("TEST 5: delete_task - User Isolation")

    # Get task IDs
    async with async_session_maker() as session:
        result = await session.execute(
            select(Task).where(Task.user_id == user1_id)
        )
        user1_task = result.scalar_one_or_none()

        result = await session.execute(
            select(Task).where(Task.user_id == user2_id)
        )
        user2_task = result.scalar_one_or_none()

        user1_task_id = user1_task.id
        user2_task_id = user2_task.id

    print_test("User1 attempting to delete User2's task (should fail)...")
    result = await delete_task(user_id=user1_id, task_id=user2_task_id)

    # This should fail or return error
    if result.get("success"):
        # Verify in database that the task was NOT deleted
        async with async_session_maker() as session:
            task = await session.get(Task, user2_task_id)
            if task is None:
                print_fail("SECURITY BREACH: User1 deleted User2's task!")

    print_pass("User1 cannot delete User2's task (secure)")

    # Verify user2's task still exists
    async with async_session_maker() as session:
        task = await session.get(Task, user2_task_id)
        if task is None:
            print_fail("User2's task was deleted!")

    print_pass("User2's task still exists")

    print_test("User1 attempting to delete their own task...")
    result = await delete_task(user_id=user1_id, task_id=user1_task_id)

    if not result.get("success"):
        print_fail(f"User1 cannot delete their own task: {result.get('error', 'Unknown error')}")

    # Verify task is deleted
    async with async_session_maker() as session:
        task = await session.get(Task, user1_task_id)
        if task is not None:
            print_fail("User1's task was not deleted")

    print_pass("User1 successfully deleted their own task")


async def test_cross_user_access_patterns(user1_id: str, user2_id: str):
    """Test various cross-user access patterns to ensure complete isolation."""
    print_header("TEST 6: Cross-User Access Patterns")

    # Create multiple tasks for each user
    print_test("Creating multiple tasks for each user...")

    for i in range(3):
        await add_task(
            user_id=user1_id,
            title=f"User1 Task {i+1}",
            priority="medium",
        )
        await add_task(
            user_id=user2_id,
            title=f"User2 Task {i+1}",
            priority="low",
        )

    print_pass("Created 3 tasks for each user")

    # Test filtering by various parameters
    print_test("Testing list_tasks with filters for user1...")

    result = await list_tasks(user_id=user1_id, status="pending")
    if result.get("success"):
        task_titles = [task.get("title") for task in result.get("data", [])]
        if any("User2 Task" in title for title in task_titles):
            print_fail("SECURITY BREACH: Filter bypass - User1 sees User2's tasks!")

    print_pass("Filtered list_tasks respects user isolation")

    # Count tasks
    async with async_session_maker() as session:
        result = await session.execute(
            select(Task).where(Task.user_id == user1_id)
        )
        user1_count = len(result.scalars().all())

        result = await session.execute(
            select(Task).where(Task.user_id == user2_id)
        )
        user2_count = len(result.scalars().all())

        if user1_count != 3:
            print_fail(f"Expected 3 tasks for user1, found {user1_count}")

        if user2_count != 4:  # 3 new + 1 from earlier tests
            print_fail(f"Expected 4 tasks for user2, found {user2_count}")

    print_pass("Task counts correct for both users")


async def cleanup_test_users(user1_id: str, user2_id: str):
    """Clean up test data."""
    print_header("CLEANUP")

    async with async_session_maker() as session:
        # Delete tasks
        result = await session.execute(
            select(Task).where(Task.user_id == user1_id)
        )
        user1_tasks = result.scalars().all()

        result = await session.execute(
            select(Task).where(Task.user_id == user2_id)
        )
        user2_tasks = result.scalars().all()

        for task in user1_tasks + user2_tasks:
            session.delete(task)

        # Delete users
        user1 = await session.get(User, user1_id)
        user2 = await session.get(User, user2_id)

        if user1:
            session.delete(user1)
        if user2:
            session.delete(user2)

        await session.commit()

    print_pass("Test data cleaned up")


async def main():
    """Run all user isolation tests."""
    print_header("Phase III - User Isolation Testing (AI-TEST-001)")
    print("Testing all 5 MCP tools for proper user isolation")
    print("Security Requirement: Users must NOT access other users' data")

    try:
        # Setup
        user1_id, user2_id = await setup_test_users()

        # Run tests
        await test_add_task_isolation(user1_id, user2_id)
        await test_list_tasks_isolation(user1_id, user2_id)
        await test_update_task_isolation(user1_id, user2_id)
        await test_complete_task_isolation(user1_id, user2_id)
        await test_delete_task_isolation(user1_id, user2_id)
        await test_cross_user_access_patterns(user1_id, user2_id)

        # Cleanup
        await cleanup_test_users(user1_id, user2_id)

        # Success
        print_header("ALL TESTS PASSED ✓")
        print("\n✅ User isolation is working correctly")
        print("✅ All 5 MCP tools respect user_id boundaries")
        print("✅ No cross-user data access detected")
        print("✅ Security requirements met")

    except Exception as e:
        print_fail(f"Test suite failed with exception: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
