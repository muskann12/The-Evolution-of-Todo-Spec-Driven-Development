# Feature Specification: Task Priorities

**Feature:** Task Priority Management
**Priority:** P1 (High - MVP)
**Status:** Specification Phase
**Last Updated:** 2025-12-31

---

## 1. Overview

### Feature Description
Users can assign priority levels to tasks to indicate importance and urgency. Tasks can be filtered and sorted by priority.

### User Story
**As a** user
**I want to** assign priority levels to my tasks
**So that** I can focus on the most important work first

### Success Criteria
- [ ] Users can set task priority (High, Medium, Low)
- [ ] Default priority is "Medium" for new tasks
- [ ] Visual indicators show priority level
- [ ] Users can filter tasks by priority
- [ ] Users can sort tasks by priority

---

## 2. Requirements

### 2.1 Priority Levels (FR-010)

**Requirement:** Support three priority levels

**Priority Levels:**
- **High** (🔴) - Urgent/Important
- **Medium** (🟡) - Normal priority (default)
- **Low** (🔵) - Nice to have

**Acceptance Criteria:**
- AC1: Priority must be one of: "High", "Medium", "Low"
- AC2: Priority is case-insensitive on input
- AC3: Priority is stored as normalized string
- AC4: Invalid priority returns error
- AC5: Blank priority defaults to "Medium"

**Validation:**
```python
def validate_priority(priority: str | None) -> tuple[bool, str | None, str]:
    """
    Validate and normalize priority.

    Returns:
        (is_valid, normalized_priority, error_message)
    """
    if priority is None:
        return (True, "Medium", "")

    normalized = priority.strip().capitalize()

    if normalized not in ["High", "Medium", "Low"]:
        return (False, None, "Error: Priority must be High, Medium, or Low.")

    return (True, normalized, "")
```

### 2.2 Visual Indicators (FR-011)

**Requirement:** Clear visual indication of priority

**Visual Design:**
```
🔴 High    - Red indicator + bold text
🟡 Medium  - Yellow indicator + normal text
🔵 Low     - Blue indicator + gray text
```

**Acceptance Criteria:**
- AC1: Each priority has unique color
- AC2: Icon/indicator visible in list view
- AC3: Priority shown in detail view
- AC4: Color-blind friendly design

### 2.3 Set Priority (FR-012)

**Requirement:** Users can set/change task priority

**Acceptance Criteria:**
- AC1: Priority can be set during task creation
- AC2: Priority can be changed after creation
- AC3: Priority dropdown shows all three options
- AC4: Current priority is pre-selected
- AC5: Priority change updates `updated_at` timestamp

**UI Component:**
```tsx
<Select value={priority} onChange={setPriority}>
  <option value="High">🔴 High</option>
  <option value="Medium">🟡 Medium</option>
  <option value="Low">🔵 Low</option>
</Select>
```

---

## 3. User Flows

### 3.1 Set Priority on Create
```
1. User clicks "New Task"
2. User fills title, description
3. User selects priority from dropdown (default: Medium)
4. User clicks "Create"
5. Task created with selected priority
```

### 3.2 Change Priority
```
1. User clicks on task
2. User clicks "Edit"
3. User selects new priority from dropdown
4. User clicks "Save"
5. Priority updated, visual indicator changes
```

---

## 4. API Specification

### Request/Response

**Create with Priority:**
```json
POST /api/{user_id}/tasks
{
  "title": "Important task",
  "priority": "High"
}
```

**Update Priority:**
```json
PUT /api/{user_id}/tasks/{id}
{
  "priority": "Low"
}
```

---

## 5. Database Schema

```sql
ALTER TABLE tasks
ADD COLUMN priority VARCHAR(10) DEFAULT 'Medium'
CHECK (priority IN ('High', 'Medium', 'Low'));

CREATE INDEX idx_tasks_priority ON tasks(priority);
```

---

## 6. Testing Requirements

- [ ] Set priority on task creation
- [ ] Update priority on existing task
- [ ] Invalid priority returns error
- [ ] Default priority is "Medium"
- [ ] Visual indicators display correctly
- [ ] Filter by priority works
- [ ] Sort by priority works

---

## Related Specifications

- `@specs/features/task-crud.md` - Core CRUD operations
- `@specs/api/todos-endpoints.md` - API endpoints
- `@specs/ui/components.md` - UI components

---

**Document Type:** Feature Specification (WHAT)
**Lifecycle Stage:** Specify
**Status:** Ready for Implementation
**Priority:** P1 (High)
