---
Spec ID: FS-006
Feature: Kanban Board View
Status: Implemented
Version: 1.0
Created: 2025-12-30
Last Updated: 2026-01-03
Authors: Development Team
Related Specs:
  - Task CRUD: @specs/features/task-crud.md
  - Task Status API: @specs/api/todos-endpoints.md
  - Database Schema: @specs/database/todos-table.md
  - UI Components: @specs/ui/components.md
---

# Feature Specification: Kanban Board View

## Overview

The Kanban Board View provides a visual task management interface organized into four distinct columns representing different workflow stages. Users shall be able to drag and drop tasks between columns to update their status, enabling intuitive workflow management and task progression tracking.

## Business Objectives

- **Visual Workflow Management**: Provide clear visualization of task distribution across workflow stages
- **Intuitive Status Updates**: Enable one-click status changes through drag-and-drop interaction
- **Team Collaboration**: Support multiple users viewing and managing tasks in real-time
- **Progress Tracking**: Allow quick assessment of project status and task distribution

## User Stories

### US-006-01: View Tasks by Workflow Stage
**As a** user
**I want** to see my tasks organized in columns by workflow stage
**So that** I can quickly understand the current state of my work

**Acceptance Criteria:**
- Tasks are displayed in 4 distinct columns: Ready, In Progress, For Review, Done
- Each column shows a count of tasks in that status
- Tasks are sorted within columns by creation date (newest first)
- Empty columns display a helpful empty state message

### US-006-02: Drag and Drop Task Status Updates
**As a** user
**I want** to drag tasks between columns
**So that** I can quickly update task status without opening edit forms

**Acceptance Criteria:**
- User can click and drag any task card
- Visual feedback shows the task being dragged
- Drop zones are highlighted when dragging over them
- Releasing the task in a new column updates its status immediately
- Invalid drop areas do not accept task drops
- Status update persists to the database

### US-006-03: Auto-Complete on Done Column
**As a** user
**I want** tasks moved to "Done" to be marked as completed automatically
**So that** my completion tracking is accurate without manual checkbox updates

**Acceptance Criteria:**
- Moving task to "Done" column sets `completed` field to `true`
- Moving task from "Done" to any other column sets `completed` field to `false`
- Completion status change is reflected in UI immediately
- Database update is atomic (status and completed updated together)

### US-006-04: Optimistic UI Updates
**As a** user
**I want** the UI to update immediately when I drag a task
**So that** the interface feels responsive and fast

**Acceptance Criteria:**
- UI updates before API call completes
- Task appears in new column immediately after drop
- If API call fails, task reverts to original column
- Error message displays on failed updates
- No flickering or visual glitches during updates

## Functional Requirements

### FR-006-01: Kanban Column Definition

The system shall support four workflow columns:

| Column ID | Display Name | Status Value | Color Theme | Description |
|-----------|--------------|--------------|-------------|-------------|
| 1 | Ready | `ready` | Gray (#9CA3AF) | Tasks that are ready to be started |
| 2 | In Progress | `in_progress` | Blue (#3B82F6) | Tasks currently being worked on |
| 3 | For Review | `review` | Purple (#8B5CF6) | Tasks awaiting review or approval |
| 4 | Done | `done` | Green (#10B981) | Completed tasks |

### FR-006-02: Task Card Display

Each task card in the Kanban view shall display:

- **Priority Badge**: Color-coded visual indicator (High: Red, Medium: Purple, Low: Blue)
- **Task Title**: Truncated to 2 lines maximum with ellipsis
- **Description**: First 2 lines visible, truncated with ellipsis
- **Tags**: Up to 3 tags displayed inline, with "+N" indicator for additional tags
- **Due Date**: Relative time format (e.g., "Due in 2 days", "Overdue by 1 day")
- **Creation Date**: Relative time format (e.g., "Created 3 hours ago")
- **Comment Count**: Icon with count (placeholder for future feature)
- **User Avatar**: Circular avatar with user initials

### FR-006-03: Drag and Drop Behavior

**Dragging:**
- User clicks and holds on any part of task card
- Card follows cursor with slight elevation shadow
- Card rotates 2 degrees and scales to 105% for visual feedback
- Original position shows ghost outline

**Dropping:**
- Drop zones (columns) highlight with purple border when dragging over
- Releasing mouse completes the drop
- Task animates into final position
- Status update triggered immediately

**Constraints:**
- Cannot drop tasks outside designated columns
- Cannot reorder tasks within same column (future enhancement)
- Cannot drag multiple tasks simultaneously

### FR-006-04: Status Update Logic

When a task is moved to a new column:

```
IF destination_column == source_column THEN
  // No action needed
  RETURN
END IF

status_update = {
  status: destination_column_id,
  completed: (destination_column_id == 'done')
}

// Optimistic update
UPDATE local_cache SET status_update WHERE task.id == dragged_task.id

// API call
TRY
  CALL api.updateTask(user_id, task_id, status_update)
  INVALIDATE task_cache
CATCH error
  // Rollback optimistic update
  REVERT local_cache
  SHOW error_message
END TRY
```

### FR-006-05: Column Statistics

Each column header shall display:
- Column name
- Task count in that column
- Add button (opens create task modal with pre-selected status)
- Column options menu (placeholder for future features)

## Technical Specifications

### Backend Requirements

**Database Schema Extension:**

```sql
ALTER TABLE tasks ADD COLUMN status VARCHAR(20) DEFAULT 'ready';
CREATE INDEX idx_tasks_status ON tasks(status);
```

**Allowed Status Values:**
- `ready`
- `in_progress`
- `review`
- `done`

**API Endpoint Update:**

```http
PUT /api/{user_id}/tasks/{task_id}
Content-Type: application/json

{
  "status": "in_progress",
  "completed": false
}
```

**Validation Rules:**
- Status must be one of the 4 allowed values
- User must own the task (user_id match)
- Task ID must exist

### Frontend Requirements

**Technology Stack:**
- **Drag & Drop Library**: `@hello-pangea/dnd` (React Beautiful DnD successor)
- **State Management**: React Query for cache management
- **Optimistic Updates**: React Query mutation callbacks

**Component Hierarchy:**

```
<DragDropContext onDragEnd={handleDragEnd}>
  <KanbanBoard>
    {COLUMNS.map(column =>
      <KanbanColumn
        key={column.id}
        status={column.id}
        tasks={tasksByColumn[column.id]}
      >
        <Droppable droppableId={column.id}>
          {tasks.map((task, index) =>
            <Draggable draggableId={task.id} index={index}>
              <KanbanTaskCard task={task} />
            </Draggable>
          )}
        </Droppable>
      </KanbanColumn>
    )}
  </KanbanBoard>
</DragDropContext>
```

**State Management:**

```typescript
const tasksByColumn = useMemo(() => {
  const columns = { ready: [], in_progress: [], review: [], done: [] };

  tasks.forEach(task => {
    const status = task.status || 'ready';
    columns[status].push(task);
  });

  return columns;
}, [tasks]);
```

**Optimistic Update Implementation:**

```typescript
const queryClient = useQueryClient();

function handleDragEnd(result: DropResult) {
  const { source, destination, draggableId } = result;

  if (!destination) return;

  const queryKey = taskKeys.list(userId, 'all');
  const previousTasks = queryClient.getQueryData(queryKey);

  // Optimistic update
  queryClient.setQueryData(queryKey, (old) =>
    old.map(task =>
      task.id === draggableId
        ? { ...task, status: destination.droppableId }
        : task
    )
  );

  // API call with rollback on error
  updateTask.mutate(updateData, {
    onError: () => queryClient.setQueryData(queryKey, previousTasks),
    onSettled: () => queryClient.invalidateQueries({ queryKey })
  });
}
```

## UI/UX Requirements

### Visual Design

**Column Styling:**
- Width: 256px (16rem) fixed
- Background: White with 60% opacity, backdrop blur
- Border: 1px solid gray-100
- Border Radius: 8px
- Padding: 12px

**Drag State Styling:**
- Card shadow: 2xl elevation
- Card rotation: 2deg
- Card scale: 105%
- Ring: 2px purple-500

**Drop Zone Styling:**
- Background: purple-50
- Ring: 2px purple-400

**Empty State:**
- Icon: Cloud or inbox icon
- Text: "No tasks"
- Subtext: "Drag tasks here"
- Color: Gray-400

### Responsive Behavior

- **Desktop** (≥1024px): Show all 4 columns side-by-side
- **Tablet** (768-1023px): Horizontal scroll with all columns visible
- **Mobile** (<768px): Vertical stacking, no drag-and-drop (use dropdown for status)

### Accessibility

- Keyboard navigation: Tab through cards, Enter to select, Arrow keys to move
- Screen reader: Announce drag start, destination, and drop completion
- ARIA labels: `aria-label="Kanban board"`, `role="region"`
- Focus indicators: Visible focus ring on all interactive elements

## Data Flow

### Loading Flow

```
1. User navigates to /tasks
2. Frontend requests: GET /api/{user_id}/tasks
3. Backend returns all tasks with status field
4. Frontend groups tasks by status into columns
5. Render Kanban board with tasks in respective columns
```

### Update Flow

```
1. User drags task from "Ready" to "In Progress"
2. Frontend optimistically updates UI (moves task to new column)
3. Frontend sends: PUT /api/{user_id}/tasks/{id} { status: "in_progress" }
4. Backend validates user ownership and status value
5. Backend updates task record: SET status='in_progress', updated_at=NOW()
6. Backend returns updated task
7. Frontend invalidates cache and refetches to ensure consistency
8. If error: Rollback UI to original state, show error message
```

## Performance Requirements

- **Initial Load**: < 1 second for up to 100 tasks
- **Drag Response**: < 16ms (60fps) for smooth animation
- **API Update**: < 500ms roundtrip time
- **Cache Invalidation**: < 100ms to update UI with fresh data

## Security Requirements

- User can only view and modify their own tasks
- Status transitions are validated server-side
- SQL injection prevention through parameterized queries
- XSS prevention through React's built-in escaping

## Error Handling

### Client-Side Errors

| Error | Handling |
|-------|----------|
| Network failure | Rollback optimistic update, show retry button |
| 401 Unauthorized | Redirect to login page |
| 403 Forbidden | Show "Access denied" message |
| 404 Not Found | Remove task from UI, show "Task deleted" message |
| 500 Server Error | Rollback update, show "Server error, please try again" |

### Validation Errors

- Invalid status value: Prevent drop, show error toast
- Task not found: Remove from UI silently
- User mismatch: Show "Permission denied"

## Testing Requirements

### Unit Tests

- Task grouping by status
- Drag and drop event handlers
- Optimistic update logic
- Error rollback behavior

### Integration Tests

- Full drag-and-drop flow with API mocking
- Error scenarios (network failure, 404, 403)
- Multi-column task movement
- Cache invalidation after updates

### E2E Tests

- User drags task from Ready to In Progress
- User drags task to Done (verify auto-complete)
- User drags task back from Done (verify uncomplete)
- Multiple rapid drag operations (stress test)

## Future Enhancements

- **Swimlanes**: Horizontal grouping by priority or user
- **Column Customization**: User-defined columns and status values
- **Task Reordering**: Drag to reorder within same column
- **Bulk Operations**: Multi-select and bulk status updates
- **Column Limits**: WIP limits per column
- **Animation Preferences**: Allow users to disable animations
- **Keyboard Shortcuts**: Hotkeys for moving tasks between columns

## Related Specifications

- **Task CRUD Operations**: `@specs/features/task-crud.md`
- **Task Status API**: `@specs/api/todos-endpoints.md`
- **Database Schema**: `@specs/database/todos-table.md`
- **UI Component Library**: `@specs/ui/components.md`
- **Dashboard Layout**: `@specs/ui/layouts.md`

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-03 | Development Team | Initial specification |

---

**Specification Status:** ✅ Implemented
**Implementation Date:** 2026-01-03
**Last Reviewed:** 2026-01-06
