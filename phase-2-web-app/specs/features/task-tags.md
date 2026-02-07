# Feature Specification: Task Tags

**Feature:** Task Tag Management
**Priority:** P1 (High - MVP)
**Status:** Specification Phase
**Last Updated:** 2025-12-31

---

## 1. Overview

### Feature Description
Users can add tags to tasks to categorize and organize them. Tags enable filtering and grouping of related tasks.

### User Story
**As a** user
**I want to** add tags to my tasks
**So that** I can categorize and find related tasks easily

### Success Criteria
- [ ] Users can add multiple tags to tasks
- [ ] Users can remove tags from tasks
- [ ] Tags are case-insensitive and normalized
- [ ] Users can filter tasks by tags
- [ ] Duplicate tags are automatically removed

---

## 2. Requirements

### 2.1 Tag Format (FR-020)

**Requirement:** Tags follow specific format rules

**Tag Rules:**
- Length: 1-20 characters
- Characters: Letters, numbers, hyphens, underscores
- Case: Normalized to lowercase
- Duplicates: Automatically removed
- Separator: Comma-separated list

**Acceptance Criteria:**
- AC1: Each tag is 1-20 characters
- AC2: Tags normalized to lowercase
- AC3: Duplicate tags removed
- AC4: Empty tags ignored
- AC5: Tags stored as comma-separated string in database

**Validation:**
```python
def validate_tags(tags: list[str] | None) -> tuple[bool, list[str], str]:
    """
    Validate and normalize tags.

    Returns:
        (is_valid, normalized_tags, error_message)
    """
    if tags is None or len(tags) == 0:
        return (True, [], "")

    normalized_tags = []
    for tag in tags:
        tag = tag.strip().lower()

        if len(tag) == 0:
            continue  # Skip empty tags

        if len(tag) > 20:
            return (False, [], "Error: Each tag must be 1-20 characters.")

        if tag not in normalized_tags:
            normalized_tags.append(tag)

    return (True, normalized_tags, "")
```

### 2.2 Add/Remove Tags (FR-021)

**Requirement:** Users can manage task tags

**Acceptance Criteria:**
- AC1: Tags can be added during task creation
- AC2: Tags can be added/removed after creation
- AC3: Multiple tags can be added at once
- AC4: Tags update `updated_at` timestamp
- AC5: Removing all tags results in empty tag list

**UI Component:**
```tsx
<TagInput
  tags={tags}
  onAdd={addTag}
  onRemove={removeTag}
  placeholder="Add tags (comma-separated)"
/>
```

### 2.3 Tag Display (FR-022)

**Requirement:** Tags shown clearly in UI

**Visual Design:**
```
Task: Complete documentation
Tags: [documentation] [urgent] [phase-2]
```

**Acceptance Criteria:**
- AC1: Tags displayed as pills/badges
- AC2: Each tag has remove button (in edit mode)
- AC3: Tags wrapped to multiple lines if needed
- AC4: Color-coded or styled distinctly

---

## 3. User Flows

### 3.1 Add Tags on Create
```
1. User creates new task
2. User enters tags in tag input (comma-separated)
   Example: "documentation, urgent, phase-2"
3. Tags normalized and deduplicated
4. Task created with tags
5. Tags displayed as pills
```

### 3.2 Add Tags to Existing Task
```
1. User edits task
2. User adds new tags to tag input
3. User clicks "Save"
4. New tags added to existing tags
5. Tags displayed in UI
```

### 3.3 Remove Tag
```
1. User edits task
2. User clicks X on tag pill
3. Tag removed from list
4. User clicks "Save"
5. Tag removed from task
```

---

## 4. API Specification

**Create with Tags:**
```json
POST /api/{user_id}/tasks
{
  "title": "Write documentation",
  "tags": ["documentation", "urgent", "phase-2"]
}
```

**Update Tags:**
```json
PUT /api/{user_id}/tasks/{id}
{
  "tags": ["documentation", "phase-2"]
}
```

**Response:**
```json
{
  "id": "task-uuid",
  "title": "Write documentation",
  "tags": ["documentation", "phase-2"],
  ...
}
```

---

## 5. Database Schema

```sql
-- Tags stored as comma-separated string
ALTER TABLE tasks
ADD COLUMN tags TEXT DEFAULT '';

-- Example data
-- tags: "documentation,urgent,phase-2"
```

**Storage Format:**
```
Frontend: ["documentation", "urgent", "phase-2"]
         ↓ (join)
Database: "documentation,urgent,phase-2"
         ↓ (split)
Frontend: ["documentation", "urgent", "phase-2"]
```

---

## 6. Testing Requirements

- [ ] Add tags on task creation
- [ ] Add tags to existing task
- [ ] Remove tags from task
- [ ] Tags normalized to lowercase
- [ ] Duplicate tags removed
- [ ] Empty tags ignored
- [ ] Tags > 20 chars rejected
- [ ] Display tags correctly
- [ ] Filter by tags works

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
