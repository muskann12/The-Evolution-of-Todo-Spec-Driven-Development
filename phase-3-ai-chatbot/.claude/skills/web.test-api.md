# Skill: Test API Endpoints

## Description
Write comprehensive tests for FastAPI endpoints including unit tests, integration tests, and API contract testing.

## When to Use
- After creating a new API endpoint
- When modifying existing endpoint behavior
- Before deploying changes to production
- As part of TDD workflow

## Prerequisites
- FastAPI backend with endpoints implemented
- pytest and pytest-asyncio installed
- TestClient from fastapi.testclient available

## Workflow

### 1. Setup Test Environment
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### 2. Write Endpoint Tests

**Test POST (Create)**
```python
# tests/test_todos_api.py
def test_create_todo_success(client):
    response = client.post("/api/todos/", json={
        "title": "Test Todo",
        "description": "Test Description",
        "priority": "High"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["priority"] == "High"
    assert "id" in data

def test_create_todo_invalid_data(client):
    # Missing required field
    response = client.post("/api/todos/", json={
        "description": "No title"
    })
    assert response.status_code == 422

    # Title too long
    response = client.post("/api/todos/", json={
        "title": "x" * 201
    })
    assert response.status_code == 422
```

**Test GET (Read)**
```python
def test_get_todo_success(client, db):
    # Create a todo first
    todo = create_test_todo(db)

    response = client.get(f"/api/todos/{todo.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo.id
    assert data["title"] == todo.title

def test_get_todo_not_found(client):
    response = client.get("/api/todos/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_list_todos(client, db):
    # Create multiple todos
    for i in range(3):
        create_test_todo(db, title=f"Todo {i}")

    response = client.get("/api/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
```

**Test PUT/PATCH (Update)**
```python
def test_update_todo_success(client, db):
    todo = create_test_todo(db)

    response = client.put(f"/api/todos/{todo.id}", json={
        "title": "Updated Title",
        "completed": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] == True

def test_update_todo_partial(client, db):
    todo = create_test_todo(db)

    response = client.patch(f"/api/todos/{todo.id}", json={
        "completed": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] == True
    assert data["title"] == todo.title  # unchanged
```

**Test DELETE**
```python
def test_delete_todo_success(client, db):
    todo = create_test_todo(db)

    response = client.delete(f"/api/todos/{todo.id}")
    assert response.status_code == 204

    # Verify it's deleted
    response = client.get(f"/api/todos/{todo.id}")
    assert response.status_code == 404

def test_delete_todo_not_found(client):
    response = client.delete("/api/todos/99999")
    assert response.status_code == 404
```

### 3. Test Query Parameters and Filters
```python
def test_filter_todos_by_priority(client, db):
    create_test_todo(db, priority="High")
    create_test_todo(db, priority="Low")

    response = client.get("/api/todos/?priority=High")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "High"

def test_search_todos(client, db):
    create_test_todo(db, title="Buy groceries")
    create_test_todo(db, title="Read book")

    response = client.get("/api/todos/?search=groceries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "groceries" in data[0]["title"]
```

### 4. Test Authentication (if applicable)
```python
def test_endpoint_requires_auth(client):
    response = client.get("/api/todos/")
    assert response.status_code == 401

def test_endpoint_with_valid_token(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/todos/", headers=headers)
    assert response.status_code == 200
```

### 5. Run Tests
```bash
# Run all tests
pytest tests/test_todos_api.py -v

# Run with coverage
pytest tests/test_todos_api.py --cov=backend --cov-report=html

# Run specific test
pytest tests/test_todos_api.py::test_create_todo_success -v
```

## Checklist
- [ ] Test fixtures set up (db, client)
- [ ] POST endpoint tests (success + validation errors)
- [ ] GET endpoint tests (single + list)
- [ ] PUT/PATCH endpoint tests
- [ ] DELETE endpoint tests
- [ ] Query parameter tests
- [ ] Filter/search tests
- [ ] Authentication tests (if applicable)
- [ ] Error case tests (404, 400, 422, 500)
- [ ] Edge case tests
- [ ] All tests passing
- [ ] Test coverage > 80%

## Test Helpers
```python
# tests/helpers.py
from models.database import Todo

def create_test_todo(db, **kwargs):
    """Helper to create a test todo with default values."""
    defaults = {
        "title": "Test Todo",
        "description": "Test Description",
        "priority": "Medium",
        "completed": False
    }
    defaults.update(kwargs)

    todo = Todo(**defaults)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

def assert_todo_response(response_data, expected_data):
    """Helper to assert todo response matches expected data."""
    for key, value in expected_data.items():
        assert response_data[key] == value
```

## Common Patterns

### Parameterized Tests
```python
import pytest

@pytest.mark.parametrize("priority,expected_count", [
    ("High", 2),
    ("Medium", 3),
    ("Low", 1),
])
def test_filter_by_priority(client, db, priority, expected_count):
    # Setup todos with different priorities
    for _ in range(2):
        create_test_todo(db, priority="High")
    for _ in range(3):
        create_test_todo(db, priority="Medium")
    create_test_todo(db, priority="Low")

    response = client.get(f"/api/todos/?priority={priority}")
    assert len(response.json()) == expected_count
```

### Async Tests
```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/todos/")
        assert response.status_code == 200
```

## Related Skills
- `web.add-api-endpoint.md` - Create endpoints to test
- `web.add-model.md` - Models used in tests
- `web.e2e-test.md` - End-to-end testing

## References
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
