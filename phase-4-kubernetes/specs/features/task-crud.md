# Feature Specification: Task CRUD Operations

**Feature:** Core Task Management (Create, Read, Update, Delete)
**Priority:** P0 (Critical - MVP)
**Status:** Specification Phase
**Last Updated:** 2025-12-31

---

## 1. Overview

### Feature Description
Users can perform all CRUD (Create, Read, Update, Delete) operations on their personal tasks. This is the core functionality of the todo application.

### User Story
**As a** registered user
**I want to** create, view, update, and delete my tasks
**So that** I can manage my todo list effectively

### Success Criteria
- [ ] Users can create new tasks with title and optional description
- [ ] Users can view all their tasks in a list
- [ ] Users can view details of a single task
- [ ] Users can update task title, description, and completion status
- [ ] Users can delete tasks they no longer need
- [ ] All operations require authentication
- [ ] Users can only access their own tasks

---

## 2. Requirements

### 2.1 Create Task (FR-001)

**Requirement:** Users must be able to create new tasks

**Acceptance Criteria:**
- AC1: User must provide a title (required, 1-200 characters)
- AC2: User can optionally provide a description (0-1000 characters)
- AC3: Task is created with default values:
  - `completed`: false
  - `priority`: "Medium"
  - `tags`: []
  - `recurrence_pattern`: null
  - `recurrence_interval`: 1
  - `due_date`: null
  - `created_at`: current timestamp
  - `updated_at`: current timestamp
- AC4: Task is assigned a unique ID (UUID)
- AC5: Task is associated with the authenticated user's ID
- AC6: User receives confirmation of successful creation
- AC7: User is redirected to task list after creation

**Input Validation:**
```typescript
interface TaskCreate {
  title: string                    // Required, 1-200 chars
  description?: string             // Optional, max 1000 chars
  priority?: string                // Optional, default "Medium" (High/Medium/Low)
  tags?: string[]                  // Optional, default []
  recurrence_pattern?: string      // Optional, default null (Daily/Weekly/Monthly/null)
  recurrence_interval?: number     // Optional, default 1 (positive integer)
  due_date?: string | null         // Optional, default null (ISO 8601 datetime)
}
```

**Error Cases:**
- Empty title → `"Error: Title cannot be empty."`
- Title > 200 chars → `"Error: Title exceeds 200 character limit."`
- Description > 1000 chars → `"Error: Description exceeds 1000 character limit."`
- Not authenticated → `401 Unauthorized`

### 2.2 Read Tasks (FR-002)

**Requirement:** Users must be able to view all their tasks

**Acceptance Criteria:**
- AC1: User sees a list of all their tasks
- AC2: Each task displays:
  - Title
  - Description (if present)
  - Completion status (✅ or ⬜)
  - Priority indicator
  - Tags (if present)
- AC3: Tasks are ordered by created_at (newest first)
- AC4: Empty state shown when user has no tasks
- AC5: Only authenticated user's tasks are displayed
- AC6: User cannot see other users' tasks

**Display Format:**
```
┌─────────────────────────────────────────────┐
│ ⬜ High: Complete project documentation     │
│    Write comprehensive docs for Phase II    │
│    Tags: documentation, urgent               │
│    Created: 2025-12-31 12:00 PM             │
└─────────────────────────────────────────────┘
```

**Error Cases:**
- Not authenticated → `401 Unauthorized`
- Invalid user_id → `403 Forbidden`

### 2.3 Read Single Task (FR-003)

**Requirement:** Users must be able to view details of a specific task

**Acceptance Criteria:**
- AC1: User can click on a task to view full details
- AC2: Detail view shows all task properties
- AC3: User can edit or delete from detail view
- AC4: 404 error if task doesn't exist
- AC5: 403 error if task belongs to different user

**Error Cases:**
- Task not found → `404 Not Found`
- Task belongs to different user → `403 Forbidden`
- Not authenticated → `401 Unauthorized`

### 2.4 Update Task (FR-004)

**Requirement:** Users must be able to update existing tasks

**Acceptance Criteria:**
- AC1: User can update task title
- AC2: User can update task description
- AC3: User can toggle completion status
- AC4: User can update priority
- AC5: User can update tags
- AC6: `updated_at` timestamp is automatically updated
- AC7: User receives confirmation of successful update
- AC8: Validation rules same as create

**Input Validation:**
```typescript
interface TaskUpdate {
  title?: string                   // Optional, 1-200 chars if provided
  description?: string             // Optional, max 1000 chars if provided
  completed?: boolean              // Optional
  priority?: string                // Optional, High/Medium/Low
  tags?: string[]                  // Optional
  recurrence_pattern?: string      // Optional, Daily/Weekly/Monthly/null
  recurrence_interval?: number     // Optional, positive integer
  due_date?: string | null         // Optional, ISO 8601 datetime
}
```

**Error Cases:**
- Empty title → `"Error: Title cannot be empty."`
- Title > 200 chars → `"Error: Title exceeds 200 character limit."`
- Description > 1000 chars → `"Error: Description exceeds 1000 character limit."`
- Task not found → `404 Not Found`
- Task belongs to different user → `403 Forbidden`
- Not authenticated → `401 Unauthorized`

### 2.5 Delete Task (FR-005)

**Requirement:** Users must be able to delete tasks

**Acceptance Criteria:**
- AC1: User can delete a task permanently
- AC2: User is asked to confirm deletion
- AC3: Task is removed from database
- AC4: User receives confirmation of deletion
- AC5: User cannot undo deletion (permanent)
- AC6: Task ID is never reused

**Confirmation Dialog:**
```
"Are you sure you want to delete this task?
This action cannot be undone."

[Cancel] [Delete]
```

**Error Cases:**
- Task not found → `404 Not Found`
- Task belongs to different user → `403 Forbidden`
- Not authenticated → `401 Unauthorized`

---

## 3. User Flows

### 3.1 Create Task Flow

```
1. User clicks "New Task" button
2. User fills out task form:
   - Enters title (required)
   - Enters description (optional)
   - Selects priority (optional, default Medium)
   - Adds tags (optional)
3. User clicks "Create" button
4. Frontend validates input
5. Frontend sends POST request to backend
6. Backend validates JWT token
7. Backend validates request data
8. Backend creates task in database
9. Backend returns created task
10. Frontend shows success message
11. Frontend redirects to task list
```

### 3.2 View Tasks Flow

```
1. User navigates to /tasks page
2. Frontend requests user's tasks from backend
3. Backend verifies authentication
4. Backend queries database for user's tasks
5. Backend returns task list
6. Frontend displays tasks
7. User sees all their tasks
```

### 3.3 Update Task Flow

```
1. User clicks on task to view details
2. User clicks "Edit" button
3. Form pre-filled with current values
4. User modifies fields
5. User clicks "Save" button
6. Frontend validates input
7. Frontend sends PUT request to backend
8. Backend validates JWT token
9. Backend validates request data
10. Backend updates task in database
11. Backend returns updated task
12. Frontend shows success message
13. Frontend updates UI with new values
```

### 3.4 Delete Task Flow

```
1. User clicks "Delete" button on task
2. Confirmation dialog appears
3. User confirms deletion
4. Frontend sends DELETE request to backend
5. Backend validates JWT token
6. Backend verifies task ownership
7. Backend deletes task from database
8. Backend returns 204 No Content
9. Frontend removes task from UI
10. Frontend shows success message
```

---

## 4. API Endpoints

### 4.1 Create Task
```
POST /api/{user_id}/tasks
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request Body:
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "priority": "High",
  "tags": ["documentation", "urgent"],
  "recurrence_pattern": "Weekly",
  "recurrence_interval": 1,
  "due_date": "2025-12-31T17:00:00Z"
}

Response (201 Created):
{
  "id": "task-uuid",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "completed": false,
  "priority": "High",
  "tags": ["documentation", "urgent"],
  "recurrence_pattern": "Weekly",
  "recurrence_interval": 1,
  "due_date": "2025-12-31T17:00:00Z",
  "user_id": "user-uuid",
  "created_at": "2025-12-31T12:00:00Z",
  "updated_at": "2025-12-31T12:00:00Z"
}
```

### 4.2 List Tasks
```
GET /api/{user_id}/tasks
Authorization: Bearer <jwt_token>

Response (200 OK):
[
  {
    "id": "task-uuid",
    "title": "Complete project documentation",
    ...
  },
  ...
]
```

### 4.3 Get Single Task
```
GET /api/{user_id}/tasks/{id}
Authorization: Bearer <jwt_token>

Response (200 OK):
{
  "id": "task-uuid",
  "title": "Complete project documentation",
  ...
}
```

### 4.4 Update Task
```
PUT /api/{user_id}/tasks/{id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request Body:
{
  "title": "Updated title",
  "completed": true
}

Response (200 OK):
{
  "id": "task-uuid",
  "title": "Updated title",
  "completed": true,
  ...
}
```

### 4.5 Delete Task
```
DELETE /api/{user_id}/tasks/{id}
Authorization: Bearer <jwt_token>

Response (204 No Content)
```

---

## 5. Database Schema

```sql
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'Medium',
    tags TEXT DEFAULT '',
    recurrence_pattern VARCHAR(10) DEFAULT NULL,
    recurrence_interval INTEGER DEFAULT 1,
    due_date TIMESTAMP DEFAULT NULL,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
```

---

## 6. UI Components

### Components Needed
- `TaskList.tsx` - Display list of tasks
- `TaskItem.tsx` - Individual task card
- `TaskForm.tsx` - Create/edit task form
- `TaskDetail.tsx` - Task detail view
- `DeleteConfirmation.tsx` - Confirm delete dialog

See: `@specs/ui/components.md` for detailed component specs

---

## 7. Testing Requirements

### Unit Tests
- [ ] Task creation with valid data
- [ ] Task creation with invalid data (title too long, etc.)
- [ ] Task list retrieval
- [ ] Task update
- [ ] Task deletion
- [ ] Validation functions

### Integration Tests
- [ ] End-to-end task creation flow
- [ ] End-to-end task update flow
- [ ] End-to-end task deletion flow
- [ ] Authentication required for all operations
- [ ] Users cannot access other users' tasks

---

## 8. Security Considerations

- ✅ All endpoints require JWT authentication
- ✅ User ID from token must match URL user ID
- ✅ All database queries filter by user_id
- ✅ Input validation on frontend AND backend
- ✅ SQL injection prevented by ORM
- ✅ XSS prevented by proper escaping

---

## 9. Performance Requirements

- Task list loads in < 500ms
- Task creation completes in < 200ms
- Task updates complete in < 200ms
- Task deletion completes in < 200ms
- UI updates immediately (optimistic updates)

---

## 10. Related Specifications

- `@specs/api/todos-endpoints.md` - API endpoint details
- `@specs/database/todos-table.md` - Database schema
- `@specs/ui/components.md` - UI component specs
- `@specs/features/user-authentication.md` - Authentication

---

## 11. Implementation Tasks

See implementation plan in separate task breakdown document.

---

**Document Type:** Feature Specification (WHAT)
**Lifecycle Stage:** Specify
**Status:** Ready for Implementation
**Priority:** P0 (Critical)
