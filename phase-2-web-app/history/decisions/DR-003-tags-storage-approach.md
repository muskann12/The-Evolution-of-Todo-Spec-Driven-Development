# Decision Record: Tags Storage Approach

**ID:** DR-003
**Date:** December 30, 2025
**Status:** ✅ Implemented
**Decider:** Development Team

---

## Context and Problem Statement

Tasks need to support multiple tags for organization and filtering:
- Users want to categorize tasks with labels (e.g., "work", "urgent", "documentation")
- Tags should be searchable and filterable
- Need efficient storage and retrieval
- MVP timeline constraints

**Requirements:**
1. Support multiple tags per task
2. Easy to query tasks by tag
3. Simple to implement for MVP
4. Minimal database schema changes
5. Future scalability path clear

---

## Decision Drivers

- **MVP Speed**: Quick implementation
- **Simplicity**: Minimal schema complexity
- **Query Performance**: Fast tag-based searches
- **Flexibility**: Easy to add/remove tags
- **Future-proof**: Can migrate if needed

---

## Considered Options

### Option 1: Comma-Separated String in tasks Table (Chosen)

**Approach:**
- Store tags as comma-separated string in `tasks.tags` column
- Parse on read, join on write
- Example: `"work,urgent,documentation"`

**Schema:**
```sql
CREATE TABLE tasks (
    ...
    tags TEXT DEFAULT '',
    ...
);
```

**Pros:**
- ✅ Extremely simple to implement
- ✅ No additional tables needed
- ✅ Easy to understand and debug
- ✅ Sufficient for MVP scale (< 1000 tasks)
- ✅ Can migrate to junction table later
- ✅ Direct string matching for simple queries

**Cons:**
- ⚠️ Not normalized (violates 1NF)
- ⚠️ Harder to query efficiently for complex tag filters
- ⚠️ Cannot enforce tag uniqueness across users
- ⚠️ String parsing overhead on every read

---

### Option 2: Tags Table with Junction Table

**Approach:**
- Separate `tags` table with unique tag names
- `task_tags` junction table for many-to-many relationship
- Fully normalized database design

**Schema:**
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    user_id UUID REFERENCES users(id)
);

CREATE TABLE task_tags (
    task_id UUID REFERENCES tasks(id),
    tag_id UUID REFERENCES tags(id),
    PRIMARY KEY (task_id, tag_id)
);
```

**Pros:**
- ✅ Fully normalized (proper relational design)
- ✅ Efficient queries with indexes
- ✅ Tag autocomplete/suggestions easy
- ✅ Can track tag usage statistics
- ✅ No duplicate tag strings

**Cons:**
- ❌ More complex schema (3 tables instead of 1)
- ❌ Requires JOINs for every task query
- ❌ More API endpoints needed (tag CRUD)
- ❌ Higher implementation time
- ❌ Over-engineered for MVP

---

### Option 3: JSON Array in tasks Table

**Approach:**
- Store tags as JSON array in `tasks.tags` column
- PostgreSQL JSON functions for querying

**Schema:**
```sql
CREATE TABLE tasks (
    ...
    tags JSONB DEFAULT '[]',
    ...
);
```

**Pros:**
- ✅ Better than comma-separated (native array type)
- ✅ Can use PostgreSQL JSON operators
- ✅ No string parsing needed

**Cons:**
- ❌ Database-specific (PostgreSQL JSONB)
- ❌ Still not fully normalized
- ❌ More complex queries than simple strings
- ❌ Harder to debug and maintain

---

## Decision Outcome

**Chosen option:** Comma-Separated String (Option 1)

### Rationale

1. **MVP Principle**
   - Simplest possible implementation
   - "Do the simplest thing that could possibly work"
   - Can always migrate later

2. **Sufficient Performance**
   - For MVP scale (< 100 tasks per user)
   - String parsing is negligible overhead
   - Frontend does filtering anyway

3. **Easy Implementation**
   - No migration scripts needed
   - Simple API response transformation
   - Straightforward frontend display

4. **Clear Migration Path**
   - Can migrate to junction table in Phase 3
   - Migration script straightforward:
     1. Create new tables
     2. Parse existing tags
     3. Insert into new schema
     4. Switch code to new format

### Implementation

**Backend (Python):**
```python
# Store tags
task.tags = ",".join(tags_list)  # ["work", "urgent"] → "work,urgent"

# Retrieve tags
tags_list = task.tags.split(",") if task.tags else []  # "work,urgent" → ["work", "urgent"]
```

**Frontend (TypeScript):**
```typescript
// Display tags
const tags = task.tags ? task.tags.split(',') : [];

// Save tags
const tagsString = tags.join(',');  // ['work', 'urgent'] → 'work,urgent'
```

**API Response:**
```json
{
  "id": "task-123",
  "title": "Complete docs",
  "tags": ["work", "urgent", "documentation"],
  ...
}
```

---

## Constraints & Validations

### Tag Naming Rules
1. Max 20 characters per tag
2. Lowercase only (normalized on save)
3. No commas (delimiter conflict)
4. No leading/trailing spaces
5. Alphanumeric and hyphens only

**Validation Regex:** `^[a-z0-9-]{1,20}$`

### Maximum Tags
- Limit: 10 tags per task
- Reason: UI display constraints, performance
- Validation: Frontend and backend

---

## Migration Plan (Future)

**When to Migrate:**
- User reports slow tag queries
- Need tag statistics/analytics
- Want tag autocomplete from all users
- Scale exceeds 1000 tasks per user

**Migration Steps:**
1. Create `tags` and `task_tags` tables
2. Write migration script:
   ```python
   for task in all_tasks:
       tags = task.tags.split(',')
       for tag_name in tags:
           tag = get_or_create_tag(tag_name, task.user_id)
           create_task_tag(task.id, tag.id)
   ```
3. Deploy new API version with junction table queries
4. Remove old `tasks.tags` column (after validation)

**Estimated Migration Time:** 4-6 hours

---

## Testing

**Test Cases (Implemented Jan 2, 2026):**
1. ✅ Create task with tags → Stored correctly
2. ✅ Update task tags → Updated correctly
3. ✅ Empty tags → Handled gracefully
4. ✅ Special characters in tags → Rejected with validation error
5. ✅ Too many tags (> 10) → Validation error
6. ✅ Tag parsing/joining → Reversible transformations

**Edge Cases:**
- ✅ Empty string → Returns empty array
- ✅ Single tag → Correctly parsed
- ✅ Whitespace handling → Trimmed
- ✅ Duplicate tags → Prevented by frontend

---

## Related Decisions

- **DR-001**: Technology Stack (PostgreSQL chosen)
- **DR-002**: Authentication Strategy (per-user tags)
- D-003: Database Field for Tags

---

## Consequences

**Positive:**
- Faster MVP development (saved 4-6 hours)
- Simpler codebase to maintain
- Easy to understand for new developers
- Flexible for quick changes

**Negative:**
- Not ideal database design (denormalized)
- Slightly slower for complex tag queries
- Need migration if scale increases

**Neutral:**
- Acceptable trade-off for MVP
- Migration path well-documented
- Technical debt acknowledged and managed

---

## Review

**Performance Metrics (Jan 7, 2026):**
- Parse time: < 1ms per task
- Query time: < 50ms for 100 tasks
- No user complaints about speed

**Decision Validation:**
- ✅ MVP completed on time
- ✅ Tags feature working well
- ✅ No performance issues
- ✅ Users satisfied with tag functionality

**Next Review:** After reaching 500 users or 10,000 total tasks

---

**Decision Type:** Data Model
**Impact Level:** Medium (can be migrated)
**Reversibility:** High (migration path clear)
**Status:** Working well, no immediate need to migrate

---

*This decision record follows SpecKit Plus v2.0 format*
