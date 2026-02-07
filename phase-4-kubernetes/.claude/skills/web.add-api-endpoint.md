# Skill: Add API Endpoint (FastAPI)

## Description
Add a new REST API endpoint to the FastAPI backend with proper request/response models, validation, and error handling.

## When to Use
- User requests a new API endpoint
- Adding CRUD operations for a resource
- Extending existing API functionality

## Prerequisites
- FastAPI backend structure exists
- Pydantic models defined (or will be created)
- Router structure in place

## Workflow

### 1. Understand Requirements
- What is the endpoint purpose?
- What HTTP method? (GET, POST, PUT, PATCH, DELETE)
- What is the URL path? (e.g., `/api/todos/{id}`)
- What are the request parameters/body?
- What is the response format?
- What status codes should be returned?

### 2. Define Pydantic Models
Create or update request/response models:
```python
# models.py or schemas.py
from pydantic import BaseModel, Field

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool

    class Config:
        from_attributes = True
```

### 3. Implement Endpoint
Add endpoint to appropriate router:
```python
# routers/todos.py
from fastapi import APIRouter, HTTPException, status
from models import TodoCreate, TodoResponse

router = APIRouter(prefix="/api/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    """Create a new todo item."""
    try:
        # Business logic here
        new_todo = create_todo_service(todo)
        return new_todo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 4. Add Tests
Create API tests:
```python
# tests/test_api.py
from fastapi.testclient import TestClient

def test_create_todo(client: TestClient):
    response = client.post("/api/todos/", json={
        "title": "Test Todo",
        "description": "Test Description"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Todo"
```

### 5. Update Documentation
- Add endpoint to API documentation (if using separate docs)
- Update OpenAPI schema (FastAPI generates automatically)
- Add example requests/responses

### 6. Test Manually
```bash
# Use httpie or curl
http POST localhost:8000/api/todos/ title="New Todo" description="Description"
```

## Checklist
- [ ] Pydantic request/response models defined
- [ ] Endpoint implemented with proper HTTP method
- [ ] Input validation in place
- [ ] Error handling implemented (400, 404, 500)
- [ ] Status codes correct (200, 201, 204, etc.)
- [ ] Unit tests written and passing
- [ ] Manual testing completed
- [ ] OpenAPI docs updated (automatic)
- [ ] Code follows FastAPI best practices

## Common Patterns

### GET with Path Parameter
```python
@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
```

### PUT/PATCH Update
```python
@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: TodoUpdate):
    updated = update_todo_service(todo_id, todo)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated
```

### DELETE
```python
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    deleted = delete_todo_service(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return None
```

## Related Skills
- `web.add-model.md` - Create Pydantic models
- `web.test-api.md` - Test API endpoints
- `web.setup-backend.md` - Initial FastAPI setup

## References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
