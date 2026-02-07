# Skill: Add Data Model (Pydantic/SQLAlchemy)

## Description
Create Pydantic schemas and SQLAlchemy models for FastAPI backend data structures with validation, type hints, and database mapping.

## When to Use
- Adding a new resource/entity to the application
- Need to define request/response schemas
- Creating database tables

## Prerequisites
- FastAPI backend structure exists
- SQLAlchemy configured (if using database)
- Database connection set up (if using database)

## Workflow

### 1. Design Data Model
- What fields does this model need?
- What are the data types?
- What validations are required?
- What are the relationships to other models?
- What database constraints? (unique, not null, etc.)

### 2. Create SQLAlchemy Model (Database)
```python
# backend/models/database.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    priority = Column(String(10), default="Medium", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}')>"
```

### 3. Create Pydantic Schemas (API)
```python
# backend/schemas/todo.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# Base schema with common fields
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: str = Field(default="Medium", pattern="^(High|Medium|Low)$")

# Schema for creating new todo (request)
class TodoCreate(TodoBase):
    pass

# Schema for updating todo (request)
class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    completed: bool | None = None
    priority: str | None = Field(None, pattern="^(High|Medium|Low)$")

# Schema for todo in database (with ID and timestamps)
class TodoInDB(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

# Schema for API response
class TodoResponse(TodoInDB):
    pass
```

### 4. Create Migration (if using Alembic)
```bash
# Generate migration
alembic revision --autogenerate -m "Add todos table"

# Review migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

### 5. Create Model Tests
```python
# tests/test_models.py
def test_todo_model_creation():
    todo = Todo(
        title="Test Todo",
        description="Test Description",
        priority="High"
    )
    assert todo.title == "Test Todo"
    assert todo.completed == False  # default value

def test_todo_schema_validation():
    # Valid data
    todo_data = {"title": "Test", "description": "Desc"}
    todo = TodoCreate(**todo_data)
    assert todo.title == "Test"

    # Invalid data (title too long)
    with pytest.raises(ValidationError):
        TodoCreate(title="x" * 201)
```

### 6. Update Repository/Service Layer
```python
# backend/repositories/todo_repository.py
from sqlalchemy.orm import Session
from models.database import Todo
from schemas.todo import TodoCreate, TodoUpdate

def create_todo(db: Session, todo: TodoCreate) -> Todo:
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todo(db: Session, todo_id: int) -> Todo | None:
    return db.query(Todo).filter(Todo.id == todo_id).first()
```

## Checklist
- [ ] SQLAlchemy model defined with proper columns
- [ ] Pydantic schemas created (Create, Update, Response)
- [ ] Field validations implemented
- [ ] Type hints correct
- [ ] Database migration created and applied
- [ ] Model relationships defined (if any)
- [ ] Indexes added for performance (if needed)
- [ ] Model tests written
- [ ] Schema validation tests written
- [ ] Repository/service layer updated

## Common Patterns

### Enum Fields
```python
from enum import Enum

class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

# In Pydantic
class TodoBase(BaseModel):
    priority: Priority = Priority.MEDIUM

# In SQLAlchemy
from sqlalchemy import Enum as SQLEnum
priority = Column(SQLEnum(Priority), default=Priority.MEDIUM)
```

### Relationships (One-to-Many)
```python
# SQLAlchemy
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    todos = relationship("Todo", back_populates="user")

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="todos")

# Pydantic
class TodoResponse(TodoBase):
    id: int
    user_id: int
    user: "UserResponse | None" = None
```

### Timestamps
```python
# SQLAlchemy with auto timestamps
from sqlalchemy.sql import func

created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## Related Skills
- `web.add-api-endpoint.md` - Use models in API endpoints
- `web.setup-backend.md` - Initial backend setup
- `web.test-api.md` - Test models in API context

## References
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [FastAPI with Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
