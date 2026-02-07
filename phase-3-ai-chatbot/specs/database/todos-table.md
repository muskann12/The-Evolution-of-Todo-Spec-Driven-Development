# Database Table Specification: tasks

**Table Name:** `tasks`
**Purpose:** Store user todo items with priorities, tags, recurrence, and Kanban status
**Last Updated:** 2026-01-07
**Implementation Status:** ✅ Fully Implemented

---

## Table Definition

```sql
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'Medium'
        CHECK (priority IN ('High', 'Medium', 'Low')),
    status VARCHAR(20) DEFAULT 'ready'
        CHECK (status IN ('ready', 'in_progress', 'review', 'done')),
    tags TEXT DEFAULT '',
    recurrence_pattern VARCHAR(20)
        CHECK (recurrence_pattern IN ('Daily', 'Weekly', 'Monthly', NULL)),
    recurrence_interval INTEGER DEFAULT 1,
    due_date TIMESTAMP,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_status ON tasks(status);
```

---

## Columns

### id
- **Type:** VARCHAR
- **Constraints:** PRIMARY KEY
- **Description:** Unique task identifier (UUID format)
- **Example:** `"task-550e8400-e29b-41d4-a716-446655440000"`

### title
- **Type:** VARCHAR(200)
- **Constraints:** NOT NULL
- **Description:** Task title/summary
- **Validation:** 1-200 characters
- **Example:** `"Complete project documentation"`

### description
- **Type:** VARCHAR(1000)
- **Constraints:** NULL allowed
- **Description:** Optional detailed description
- **Validation:** Max 1000 characters
- **Example:** `"Write comprehensive docs for Phase II including API specs and architecture"`

### completed
- **Type:** BOOLEAN
- **Constraints:** DEFAULT FALSE
- **Description:** Task completion status
- **Values:** `true` (completed), `false` (incomplete)

### priority
- **Type:** VARCHAR(10)
- **Constraints:** DEFAULT 'Medium', CHECK constraint
- **Description:** Task priority level
- **Values:** `"High"`, `"Medium"`, `"Low"`

### status
- **Type:** VARCHAR(20)
- **Constraints:** DEFAULT 'ready', CHECK constraint
- **Description:** Kanban board status for task workflow
- **Values:** `"ready"`, `"in_progress"`, `"review"`, `"done"`
- **Business Rule:** When status is set to `"done"`, the `completed` field shall be automatically set to `true`

### tags
- **Type:** TEXT
- **Constraints:** DEFAULT ''
- **Description:** Comma-separated tag list
- **Format:** `"tag1,tag2,tag3"`
- **Example:** `"documentation,urgent,phase-2"`

### recurrence_pattern
- **Type:** VARCHAR(20)
- **Constraints:** CHECK constraint, NULL allowed
- **Description:** Pattern for recurring tasks
- **Values:** `"Daily"`, `"Weekly"`, `"Monthly"`, or `NULL` (non-recurring)
- **Default:** `NULL` (task does not recur)
- **Example:** `"Weekly"` (task repeats every week)

### recurrence_interval
- **Type:** INTEGER
- **Constraints:** DEFAULT 1
- **Description:** Interval multiplier for recurrence pattern
- **Values:** Positive integers (1, 2, 3, ...)
- **Example:** `2` (with "Weekly" pattern = every 2 weeks)

### due_date
- **Type:** TIMESTAMP
- **Constraints:** NULL allowed
- **Description:** Optional deadline for task completion (UTC)
- **Format:** ISO 8601 datetime
- **Example:** `"2026-01-15T17:00:00Z"`

### user_id
- **Type:** VARCHAR
- **Constraints:** FOREIGN KEY → users(id), NOT NULL
- **Description:** Owner of the task
- **Example:** `"user-550e8400-e29b-41d4-a716-446655440000"`

### created_at
- **Type:** TIMESTAMP
- **Constraints:** DEFAULT CURRENT_TIMESTAMP
- **Description:** Task creation timestamp (UTC)
- **Example:** `"2025-12-31T12:00:00Z"`

### updated_at
- **Type:** TIMESTAMP
- **Constraints:** DEFAULT CURRENT_TIMESTAMP
- **Description:** Last update timestamp (UTC)
- **Example:** `"2025-12-31T14:30:00Z"`

---

## Indexes

### Primary Key
```sql
PRIMARY KEY (id)
```

### User ID Index
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

**Purpose:** Fast query of user's tasks

### Completed Index
```sql
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

**Purpose:** Filter by completion status

### Priority Index
```sql
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

**Purpose:** Sort/filter by priority

### Status Index
```sql
CREATE INDEX idx_tasks_status ON tasks(status);
```

**Purpose:** Filter tasks by Kanban status (used in board view)

---

## Relationships

### tasks → users (Many-to-One)

Each task belongs to one user.

```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

**Cascade Behavior:** Deleting a user deletes all their tasks.

---

## Sample Data

```sql
INSERT INTO tasks (
    id, title, description, completed, priority, status, tags,
    recurrence_pattern, recurrence_interval, due_date,
    user_id, created_at, updated_at
)
VALUES (
    'task-1',
    'Write documentation',
    'Complete API specs for Phase II',
    false,
    'High',
    'in_progress',
    'documentation,urgent',
    NULL,
    1,
    '2026-01-10 17:00:00',
    'user-1',
    '2026-01-03 12:00:00',
    '2026-01-03 12:00:00'
);
```

---

## SQLModel Definition

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Task model for todo items."""

    __tablename__ = "tasks"

    id: str = Field(primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default="Medium")
    status: str = Field(default="ready")
    tags: str = Field(default="")
    recurrence_pattern: Optional[str] = Field(default=None)
    recurrence_interval: int = Field(default=1)
    due_date: Optional[datetime] = Field(default=None)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Queries

### Get All User Tasks
```python
async def get_user_tasks(session: AsyncSession, user_id: str) -> list[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()
```

### Create Task
```python
async def create_task(
    session: AsyncSession,
    task_data: TaskCreate,
    user_id: str
) -> Task:
    task = Task(
        id=str(uuid.uuid4()),
        **task_data.model_dump(),
        user_id=user_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

### Update Task
```python
async def update_task(
    session: AsyncSession,
    task_id: str,
    user_id: str,
    updates: TaskUpdate
) -> Task | None:
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        return None

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

---

## Related Specifications

- `@specs/features/task-crud.md` - Task CRUD feature spec
- `@specs/features/kanban-board.md` - Kanban board with status field
- `@specs/features/task-priorities.md` - Priority system
- `@specs/features/task-tags.md` - Tag system
- `@specs/features/task-recurrence.md` - Recurrence patterns
- `@specs/api/todos-endpoints.md` - Tasks API endpoints
- `@specs/database/schema.md` - Complete schema

---

**Document Type:** Database Table Specification
**Status:** ✅ Implemented
**Priority:** P0 (Critical)
