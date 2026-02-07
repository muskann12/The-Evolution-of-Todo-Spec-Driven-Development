# API Specification: Todo Endpoints

**API Group:** Task Management Endpoints
**Base Path:** `/api/{user_id}/tasks`
**Authentication:** Required (JWT Bearer token)
**Last Updated:** 2026-01-03

---

## Overview

This document specifies all API endpoints for task (todo) management operations. All endpoints require JWT authentication and enforce user authorization.

**Base URL:**
- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

---

## Authentication

All endpoints require JWT token in Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Authorization Rules:**
- User ID from JWT token must match `{user_id}` in URL
- Mismatch returns `403 Forbidden`
- Missing/invalid token returns `401 Unauthorized`

---

## Endpoints

### 1. List Tasks

**GET** `/api/{user_id}/tasks`

Get all tasks for authenticated user.

**Request:**
```http
GET /api/user123/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "task-uuid-1",
    "title": "Complete project",
    "description": "Finish Phase II",
    "completed": false,
    "priority": "High",
    "status": "in_progress",
    "tags": ["work", "urgent"],
    "recurrence_pattern": null,
    "recurrence_interval": 1,
    "due_date": "2026-01-10T17:00:00Z",
    "user_id": "user123",
    "created_at": "2025-12-31T12:00:00Z",
    "updated_at": "2025-12-31T12:00:00Z"
  },
  ...
]
```

**Error Responses:**
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - User ID mismatch

---

### 2. Create Task

**POST** `/api/{user_id}/tasks`

Create a new task.

**Request:**
```http
POST /api/user123/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Write documentation",
  "description": "Complete API specs",
  "priority": "High",
  "status": "ready",
  "tags": ["documentation"],
  "due_date": "2026-01-15T17:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": "new-task-uuid",
  "title": "Write documentation",
  "description": "Complete API specs",
  "completed": false,
  "priority": "High",
  "status": "ready",
  "tags": ["documentation"],
  "recurrence_pattern": null,
  "recurrence_interval": 1,
  "due_date": "2026-01-15T17:00:00Z",
  "user_id": "user123",
  "created_at": "2025-12-31T13:00:00Z",
  "updated_at": "2025-12-31T13:00:00Z"
}
```

**Validation:**
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters
- `priority`: Optional, one of "High", "Medium", "Low" (default: "Medium")
- `status`: Optional, one of "ready", "in_progress", "review", "done" (default: "ready")
- `tags`: Optional, array of strings (each 1-20 chars)
- `recurrence_pattern`: Optional, one of "Daily", "Weekly", "Monthly", null
- `recurrence_interval`: Optional, positive integer (default: 1)
- `due_date`: Optional, ISO 8601 datetime string

**Error Responses:**
- `400 Bad Request` - Validation failed
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - User ID mismatch

---

### 3. Get Single Task

**GET** `/api/{user_id}/tasks/{id}`

Get a specific task by ID.

**Request:**
```http
GET /api/user123/tasks/task-uuid-1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "task-uuid-1",
  "title": "Complete project",
  "description": "Finish Phase II",
  "completed": false,
  "priority": "High",
  "status": "in_progress",
  "tags": ["work", "urgent"],
  "recurrence_pattern": null,
  "recurrence_interval": 1,
  "due_date": "2026-01-10T17:00:00Z",
  "user_id": "user123",
  "created_at": "2025-12-31T12:00:00Z",
  "updated_at": "2025-12-31T12:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Task belongs to different user
- `404 Not Found` - Task doesn't exist

---

### 4. Update Task

**PUT** `/api/{user_id}/tasks/{id}`

Update an existing task.

**Request:**
```http
PUT /api/user123/tasks/task-uuid-1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Updated title",
  "completed": true,
  "priority": "Medium",
  "status": "done"
}
```

**Response (200 OK):**
```json
{
  "id": "task-uuid-1",
  "title": "Updated title",
  "description": "Finish Phase II",
  "completed": true,
  "priority": "Medium",
  "status": "done",
  "tags": ["work", "urgent"],
  "recurrence_pattern": null,
  "recurrence_interval": 1,
  "due_date": "2026-01-10T17:00:00Z",
  "user_id": "user123",
  "created_at": "2025-12-31T12:00:00Z",
  "updated_at": "2025-12-31T14:00:00Z"
}
```

**Partial Updates:**
Only fields provided in request are updated. Omitted fields remain unchanged.

**Special Behavior:**
When `status` is set to "done", the `completed` field is automatically set to `true`.
When `status` is set to any other value ("ready", "in_progress", "review"), the `completed` field is automatically set to `false`.

**Error Responses:**
- `400 Bad Request` - Validation failed
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Task belongs to different user
- `404 Not Found` - Task doesn't exist

---

### 5. Delete Task

**DELETE** `/api/{user_id}/tasks/{id}`

Delete a task permanently.

**Request:**
```http
DELETE /api/user123/tasks/task-uuid-1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
```

**Response (204 No Content):**
```
(No response body)
```

**Error Responses:**
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Task belongs to different user
- `404 Not Found` - Task doesn't exist

---

### 6. Toggle Task Completion

**PATCH** `/api/{user_id}/tasks/{id}/complete`

Toggle task completion status.

**Request:**
```http
PATCH /api/user123/tasks/task-uuid-1/complete HTTP/1.1
Host: localhost:8000
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "task-uuid-1",
  "title": "Complete project",
  "completed": true,
  "updated_at": "2025-12-31T15:00:00Z",
  ...
}
```

**Behavior:**
- If `completed: false` → set to `true`
- If `completed: true` → set to `false`
- Updates `updated_at` timestamp

**Error Responses:**
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Task belongs to different user
- `404 Not Found` - Task doesn't exist

---

## Common Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Not allowed to access resource |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server error |

---

## Data Models

### Task Response Model

```typescript
interface TaskResponse {
  id: string
  title: string
  description: string | null
  completed: boolean
  priority: "High" | "Medium" | "Low"
  status: "ready" | "in_progress" | "review" | "done"
  tags: string[]
  recurrence_pattern: "Daily" | "Weekly" | "Monthly" | null
  recurrence_interval: number
  due_date: string | null  // ISO 8601 timestamp
  user_id: string
  created_at: string  // ISO 8601 timestamp
  updated_at: string  // ISO 8601 timestamp
}
```

### Task Create Model

```typescript
interface TaskCreate {
  title: string
  description?: string
  priority?: "High" | "Medium" | "Low"
  status?: "ready" | "in_progress" | "review" | "done"
  tags?: string[]
  recurrence_pattern?: "Daily" | "Weekly" | "Monthly" | null
  recurrence_interval?: number
  due_date?: string | null  // ISO 8601 timestamp
}
```

### Task Update Model

```typescript
interface TaskUpdate {
  title?: string
  description?: string
  completed?: boolean
  priority?: "High" | "Medium" | "Low"
  status?: "ready" | "in_progress" | "review" | "done"
  tags?: string[]
  recurrence_pattern?: "Daily" | "Weekly" | "Monthly" | null
  recurrence_interval?: number
  due_date?: string | null  // ISO 8601 timestamp
}
```

---

## Related Specifications

- `@specs/features/task-crud.md` - Feature requirements
- `@specs/features/kanban-board.md` - Kanban board feature (status field)
- `@specs/features/task-priorities.md` - Priority system
- `@specs/features/task-tags.md` - Tag system
- `@specs/features/task-recurrence.md` - Recurrence patterns
- `@specs/database/todos-table.md` - Database schema
- `@backend/CLAUDE.md` - Backend implementation guide

---

**Document Type:** API Specification
**Status:** ✅ Implemented
**Priority:** P0 (Critical)
