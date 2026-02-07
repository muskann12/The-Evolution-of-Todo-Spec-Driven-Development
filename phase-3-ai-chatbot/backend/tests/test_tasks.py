"""
Test suite for task CRUD endpoints.

Tests the task API endpoints defined in @specs/api/todos-endpoints.md
Covers all CRUD operations with authentication.
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_create_task_success(auth_client: AsyncClient, test_user):
    """
    Test successful task creation.

    Acceptance Criteria (FR-001):
    - POST /api/{user_id}/tasks creates task
    - Returns 201 with task data
    """
    response = await auth_client.post(
        f"/api/{test_user['id']}/tasks",
        json={
            "title": "Test Task",
            "description": "Test description",
            "priority": "High"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "Test description"
    assert data["priority"] == "High"
    assert data["completed"] == False
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_task_with_tags(auth_client: AsyncClient, test_user):
    """
    Test task creation with tags.

    Acceptance Criteria (FR-004):
    - Task can be created with multiple tags
    """
    response = await auth_client.post(
        f"/api/{test_user['id']}/tasks",
        json={
            "title": "Tagged Task",
            "tags": ["work", "urgent", "important"]
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert set(data["tags"]) == {"work", "urgent", "important"}


@pytest.mark.asyncio
async def test_create_task_with_recurrence(auth_client: AsyncClient, test_user):
    """
    Test task creation with recurrence pattern.

    Acceptance Criteria (FR-005):
    - Task can be created with recurrence
    """
    response = await auth_client.post(
        f"/api/{test_user['id']}/tasks",
        json={
            "title": "Daily Task",
            "recurrence_pattern": "Daily",
            "recurrence_interval": 1
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["recurrence_pattern"] == "Daily"
    assert data["recurrence_interval"] == 1


@pytest.mark.asyncio
async def test_create_task_without_auth(client: AsyncClient, test_user):
    """
    Test task creation fails without authentication.

    Security Requirement (SR-003):
    - All task endpoints require authentication
    """
    response = await client.post(
        f"/api/{test_user['id']}/tasks",
        json={"title": "Test Task"}
    )

    # Should return 403 Forbidden when no auth provided (FastAPI default for HTTPBearer)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_task_invalid_title(auth_client: AsyncClient, test_user):
    """
    Test task creation fails with empty title.

    Validation Rule (VR-001):
    - Title must be 1-200 characters
    """
    response = await auth_client.post(
        f"/api/{test_user['id']}/tasks",
        json={"title": ""}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_task_title_too_long(auth_client: AsyncClient, test_user):
    """
    Test task creation fails with title > 200 chars.

    Validation Rule (VR-002):
    - Title max 200 characters
    """
    long_title = "a" * 201

    response = await auth_client.post(
        f"/api/{test_user['id']}/tasks",
        json={"title": long_title}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_all_tasks(auth_client: AsyncClient, test_user, test_tasks):
    """
    Test retrieving all user's tasks.

    Acceptance Criteria (FR-002):
    - GET /api/{user_id}/tasks returns all user's tasks
    """
    response = await auth_client.get(f"/api/{test_user['id']}/tasks")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == len(test_tasks)


@pytest.mark.asyncio
async def test_get_tasks_filters_by_user(auth_client: AsyncClient, test_user, other_user, test_tasks):
    """
    Test that tasks are filtered by user_id.

    Security Requirement (SR-004):
    - Users can only see their own tasks
    """
    response = await auth_client.get(f"/api/{test_user['id']}/tasks")
    data = response.json()

    # All returned tasks should belong to test_user
    for task in data:
        assert task["user_id"] == test_user["id"]


@pytest.mark.asyncio
async def test_get_tasks_forbidden_other_user(auth_client: AsyncClient, test_user, other_user):
    """
    Test that user cannot access other user's tasks.

    Security Requirement (SR-005):
    - Requesting other user's tasks returns 403
    """
    response = await auth_client.get(f"/api/{other_user['id']}/tasks")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_single_task(auth_client: AsyncClient, test_user, test_tasks):
    """
    Test retrieving a single task by ID.

    Acceptance Criteria (FR-003):
    - GET /api/{user_id}/tasks/{id} returns task
    """
    task_id = test_tasks[0]["id"]

    response = await auth_client.get(
        f"/api/{test_user['id']}/tasks/{task_id}"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == test_tasks[0]["title"]


@pytest.mark.asyncio
async def test_get_task_not_found(auth_client: AsyncClient, test_user):
    """
    Test getting non-existent task returns 404.

    Error Handling (EH-001):
    - Non-existent task ID returns 404
    """
    fake_id = "nonexistent-task-id"

    response = await auth_client.get(
        f"/api/{test_user['id']}/tasks/{fake_id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_task_success(auth_client: AsyncClient, test_user, test_tasks):
    """
    Test successful task update.

    Acceptance Criteria (FR-006):
    - PUT /api/{user_id}/tasks/{id} updates task
    """
    task_id = test_tasks[0]["id"]

    response = await auth_client.put(
        f"/api/{test_user['id']}/tasks/{task_id}",
        json={
            "title": "Updated Title",
            "description": "Updated description",
            "priority": "Low"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["priority"] == "Low"


@pytest.mark.asyncio
async def test_update_task_partial(auth_client: AsyncClient, test_user, test_tasks):
    """
    Test partial task update (only some fields).

    Acceptance Criteria (FR-007):
    - Can update only specific fields
    """
    task_id = test_tasks[0]["id"]
    original_description = test_tasks[0]["description"]

    response = await auth_client.put(
        f"/api/{test_user['id']}/tasks/{task_id}",
        json={"title": "Only Title Updated"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["title"] == "Only Title Updated"
    assert data["description"] == original_description  # Unchanged


@pytest.mark.asyncio
async def test_update_task_forbidden_other_user(auth_client: AsyncClient, test_user, other_user_task):
    """
    Test that user cannot update other user's task.

    Security Requirement (SR-006):
    - Updating other user's task returns 403 or 404
    """
    response = await auth_client.put(
        f"/api/{test_user['id']}/tasks/{other_user_task['id']}",
        json={"title": "Hacked"}
    )

    # Should be 404 (task not found for this user) or 403 (forbidden)
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]


@pytest.mark.asyncio
async def test_delete_task_success(auth_client: AsyncClient, test_user, test_tasks):
    """
    Test successful task deletion.

    Acceptance Criteria (FR-008):
    - DELETE /api/{user_id}/tasks/{id} deletes task
    - Returns 204 No Content
    """
    task_id = test_tasks[0]["id"]

    response = await auth_client.delete(
        f"/api/{test_user['id']}/tasks/{task_id}"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify task is deleted
    get_response = await auth_client.get(
        f"/api/{test_user['id']}/tasks/{task_id}"
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_task_forbidden_other_user(auth_client: AsyncClient, test_user, other_user_task):
    """
    Test that user cannot delete other user's task.

    Security Requirement (SR-007):
    - Deleting other user's task returns 403 or 404
    """
    response = await auth_client.delete(
        f"/api/{test_user['id']}/tasks/{other_user_task['id']}"
    )

    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]


@pytest.mark.asyncio
async def test_toggle_task_completion(auth_client: AsyncClient, test_user, test_tasks):
    """
    Test toggling task completion status.

    Acceptance Criteria (FR-009):
    - PATCH /api/{user_id}/tasks/{id}/complete toggles completed
    """
    task_id = test_tasks[0]["id"]
    original_status = test_tasks[0]["completed"]

    response = await auth_client.patch(
        f"/api/{test_user['id']}/tasks/{task_id}/complete"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should be toggled
    assert data["completed"] == (not original_status)

    # Toggle again
    response2 = await auth_client.patch(
        f"/api/{test_user['id']}/tasks/{task_id}/complete"
    )

    data2 = response2.json()
    assert data2["completed"] == original_status  # Back to original


@pytest.mark.asyncio
async def test_task_timestamps_updated(auth_client: AsyncClient, test_user, test_tasks):
    """
    Test that updated_at timestamp changes on update.

    Data Requirement (DR-002):
    - updated_at should change when task is modified
    """
    task_id = test_tasks[0]["id"]
    original_updated_at = test_tasks[0]["updated_at"]

    # Wait a moment to ensure timestamp difference
    import asyncio
    await asyncio.sleep(0.1)

    response = await auth_client.put(
        f"/api/{test_user['id']}/tasks/{task_id}",
        json={"title": "Updated"}
    )

    data = response.json()

    # updated_at should have changed
    assert data["updated_at"] != original_updated_at
