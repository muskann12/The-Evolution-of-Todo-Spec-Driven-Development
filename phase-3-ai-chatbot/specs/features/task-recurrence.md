# Feature Specification: Recurring Tasks

**Feature:** Recurring Task Management
**Priority:** P2 (Medium - Post-MVP)
**Status:** Specification Phase (Future Enhancement)
**Last Updated:** 2025-12-31

---

## 1. Overview

### Feature Description
Users can set tasks to recur automatically on a schedule (daily, weekly, monthly). When a recurring task is completed, a new instance is automatically created for the next occurrence.

### User Story
**As a** user
**I want to** create recurring tasks
**So that** I don't have to manually recreate repetitive tasks

### Success Criteria
- [ ] Users can set recurrence pattern (Daily, Weekly, Monthly)
- [ ] Users can set recurrence interval (every N days/weeks/months)
- [ ] Completing a recurring task creates next occurrence
- [ ] Users can view upcoming occurrences
- [ ] Users can stop recurrence
- [ ] Recurrence indicator visible in UI

---

## 2. Requirements

### 2.1 Recurrence Patterns (FR-030)

**Requirement:** Support standard recurrence patterns

**Patterns:**
- **None** - Task does not recur (default)
- **Daily** - Recurs every N days
- **Weekly** - Recurs every N weeks
- **Monthly** - Recurs every N months

**Acceptance Criteria:**
- AC1: Recurrence pattern must be None, Daily, Weekly, or Monthly
- AC2: Default pattern is None
- AC3: Recurrence interval must be positive integer (default: 1)
- AC4: Pattern stored in database
- AC5: Invalid pattern returns error

### 2.2 Auto-Create Next Occurrence (FR-031)

**Requirement:** Automatically create next task when recurring task completed

**Acceptance Criteria:**
- AC1: When recurring task marked complete, create new task
- AC2: New task has same title, description, priority, tags
- AC3: New task has `completed: false`
- AC4: New task has new UUID
- AC5: New task has `created_at` set to current time
- AC6: Original task remains complete
- AC7: User notified: "Task completed! Next occurrence created."

**Example:**
```
Task: "Daily standup meeting"
Recurrence: Daily (interval: 1)

User completes task on 2025-12-31
→ New task created for 2026-01-01
  - Same title, description, priority, tags
  - completed: false
  - created_at: 2026-01-01 00:00:00
```

### 2.3 Visual Indicators (FR-032)

**Requirement:** Show recurrence status in UI

**Indicators:**
- 🔁D - Daily recurrence
- 🔁W - Weekly recurrence
- 🔁M - Monthly recurrence
- 🔁 - Custom recurrence

**Acceptance Criteria:**
- AC1: Recurring tasks show recurrence icon
- AC2: Icon includes pattern letter
- AC3: Tooltip shows full recurrence info
- AC4: Non-recurring tasks have no icon

---

## 3. User Flows

### 3.1 Create Recurring Task
```
1. User creates new task
2. User enables "Recurring task" checkbox
3. User selects pattern (Daily/Weekly/Monthly)
4. User sets interval (default: 1)
5. User clicks "Create"
6. Task created with recurrence settings
7. Recurrence indicator shown
```

### 3.2 Complete Recurring Task
```
1. User marks recurring task as complete
2. Backend detects task has recurrence
3. Backend creates new task instance
4. New task inherits properties
5. New task set to incomplete
6. Original task remains complete
7. Frontend shows success message
8. Frontend displays new task in list
```

### 3.3 Stop Recurrence
```
1. User edits recurring task
2. User sets recurrence to "None"
3. User clicks "Save"
4. Task recurrence removed
5. No new occurrences created
6. Recurrence indicator removed
```

---

## 4. API Specification

**Create Recurring Task:**
```json
POST /api/{user_id}/tasks
{
  "title": "Daily standup meeting",
  "recurrence_pattern": "Daily",
  "recurrence_interval": 1
}
```

**Complete Recurring Task:**
```json
PATCH /api/{user_id}/tasks/{id}/complete

Response:
{
  "message": "Task completed! Next occurrence created.",
  "completed_task": {...},
  "next_task": {
    "id": "new-uuid",
    "title": "Daily standup meeting",
    "completed": false,
    ...
  }
}
```

---

## 5. Database Schema

```sql
ALTER TABLE tasks
ADD COLUMN recurrence_pattern VARCHAR(10) DEFAULT NULL
CHECK (recurrence_pattern IN (NULL, 'Daily', 'Weekly', 'Monthly'));

ALTER TABLE tasks
ADD COLUMN recurrence_interval INTEGER DEFAULT 1;

ALTER TABLE tasks
ADD COLUMN next_occurrence TIMESTAMP DEFAULT NULL;
```

---

## 6. Implementation Notes

**Future Enhancement:**
This feature is marked as P2 (Post-MVP). Implement after core CRUD, priorities, and tags are complete and tested.

**Complexity:**
- Moderate backend logic
- Date arithmetic
- Task cloning logic
- UI for recurrence settings

---

## 7. Testing Requirements

- [ ] Create task with daily recurrence
- [ ] Create task with weekly recurrence
- [ ] Create task with monthly recurrence
- [ ] Complete recurring task creates next occurrence
- [ ] Next task has correct properties
- [ ] Stop recurrence works
- [ ] Invalid pattern rejected
- [ ] Visual indicators display correctly

---

## Related Specifications

- `@specs/features/task-crud.md` - Core CRUD operations
- `@specs/api/todos-endpoints.md` - API endpoints
- `@specs/database/todos-table.md` - Database schema

---

**Document Type:** Feature Specification (WHAT)
**Lifecycle Stage:** Specify
**Status:** Future Enhancement (Post-MVP)
**Priority:** P2 (Medium)
