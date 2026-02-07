---
Spec ID: FS-008
Feature: Task Sorting
Status: Implemented
Version: 1.0
Created: 2025-12-30
Last Updated: 2026-01-04
Authors: Development Team
Related Specs:
  - Task CRUD: @specs/features/task-crud.md
  - Task Priorities: @specs/features/task-priorities.md
  - UI Components: @specs/ui/components.md
---

# Feature Specification: Task Sorting

## Overview

The Task Sorting feature provides eight different sorting options to organize task lists according to user preferences. Users shall be able to sort tasks by creation date, priority level, title alphabetically, and completion status.

## Business Objectives

- **Flexible Organization**: Allow users to view tasks in their preferred order
- **Priority Focus**: Enable focusing on high-priority or pending tasks
- **Time Management**: Sort by dates to manage deadlines and recent activity
- **Alphabetical Reference**: Organize tasks alphabetically for easy lookup

## User Stories

### US-008-01: Sort by Creation Date
**As a** user
**I want** to sort tasks by creation date (newest or oldest first)
**So that** I can see recent tasks or long-standing tasks first

**Acceptance Criteria:**
- "Newest first" sorts by `created_at` descending
- "Oldest first" sorts by `created_at` ascending
- Default sort is "Newest first"
- Sort persists across page refreshes

### US-008-02: Sort by Priority
**As a** user
**I want** to sort tasks by priority level
**So that** I can focus on important tasks or work through easier tasks first

**Acceptance Criteria:**
- "Priority: High to Low" sorts High → Medium → Low
- "Priority: Low to High" sorts Low → Medium → High
- Tasks of same priority maintain their relative order

### US-008-03: Sort Alphabetically
**As a** user
**I want** to sort tasks alphabetically by title
**So that** I can find tasks by name quickly

**Acceptance Criteria:**
- "Title A-Z" sorts alphabetically ascending
- "Title Z-A" sorts alphabetically descending
- Case-insensitive sorting
- Special characters and numbers sort predictably

### US-008-04: Sort by Completion Status
**As a** user
**I want** to sort tasks by completion status
**So that** I can see all completed or pending tasks together

**Acceptance Criteria:**
- "Completed first" shows completed tasks at top
- "Pending first" shows uncompleted tasks at top
- Within each group, tasks maintain another sort order (by date)

## Functional Requirements

### FR-008-01: Sort Options

The system shall provide the following eight sorting options:

| Sort ID | Display Name | Sort Logic |
|---------|--------------|------------|
| 1 | Newest First | `created_at DESC` |
| 2 | Oldest First | `created_at ASC` |
| 3 | Priority: High → Low | `priority` (High=0, Medium=1, Low=2) ASC |
| 4 | Priority: Low → High | `priority` (Low=0, Medium=1, High=2) ASC |
| 5 | Title A-Z | `title ASC` (alphabetical) |
| 6 | Title Z-A | `title DESC` (reverse alphabetical) |
| 7 | Completed First | `completed DESC`, then `created_at DESC` |
| 8 | Pending First | `completed ASC`, then `created_at DESC` |

### FR-008-02: Sort Selector Component

**UI Component:** Dropdown select menu in navbar

**Visual Elements:**
- Sort icon (arrows up/down)
- Current sort option displayed
- Dropdown with all 8 options
- Checkmark next to selected option

**Behavior:**
- Click to open dropdown
- Click option to select
- Dropdown closes after selection
- Selected option updates immediately
- Task list re-renders with new sort

### FR-008-03: Sort Algorithm Implementation

**Client-Side Sorting:**

```typescript
type SortOption =
  | 'newest'
  | 'oldest'
  | 'priority-high'
  | 'priority-low'
  | 'title-asc'
  | 'title-desc'
  | 'completed'
  | 'pending';

function sortTasks(tasks: Task[], sortBy: SortOption): Task[] {
  const sorted = [...tasks]; // Create copy to avoid mutation

  switch (sortBy) {
    case 'newest':
      return sorted.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );

    case 'oldest':
      return sorted.sort((a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );

    case 'priority-high':
      const priorityOrder = { High: 0, Medium: 1, Low: 2 };
      return sorted.sort((a, b) =>
        priorityOrder[a.priority] - priorityOrder[b.priority]
      );

    case 'priority-low':
      const priorityOrderLow = { Low: 0, Medium: 1, High: 2 };
      return sorted.sort((a, b) =>
        priorityOrderLow[a.priority] - priorityOrderLow[b.priority]
      );

    case 'title-asc':
      return sorted.sort((a, b) =>
        a.title.localeCompare(b.title, undefined, { sensitivity: 'base' })
      );

    case 'title-desc':
      return sorted.sort((a, b) =>
        b.title.localeCompare(a.title, undefined, { sensitivity: 'base' })
      );

    case 'completed':
      return sorted.sort((a, b) => {
        if (a.completed === b.completed) {
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        }
        return b.completed ? 1 : -1;
      });

    case 'pending':
      return sorted.sort((a, b) => {
        if (a.completed === b.completed) {
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        }
        return a.completed ? 1 : -1;
      });

    default:
      return sorted;
  }
}
```

### FR-008-04: Sort State Management

**State Variable:**
```typescript
const [sortBy, setSortBy] = useState<SortOption>('newest');
```

**Local Storage Persistence:**
```typescript
// Save to localStorage on change
useEffect(() => {
  localStorage.setItem('task-sort-preference', sortBy);
}, [sortBy]);

// Load from localStorage on mount
useEffect(() => {
  const saved = localStorage.getItem('task-sort-preference') as SortOption;
  if (saved) setSortBy(saved);
}, []);
```

**Sort Application:**
```typescript
const sortedTasks = useMemo(() => {
  return sortTasks(tasks, sortBy);
}, [tasks, sortBy]);
```

### FR-008-05: Sort Integration with Other Features

**Kanban Board:**
- Sorting applies within each column independently
- Each column's tasks sorted by selected option
- Drag-and-drop maintains sort order until next sort change

**Search:**
- Sorting applies to filtered results
- Search + Sort work together seamlessly

**Filters:**
- Sorting applies to filtered tasks (pending/completed)
- Filter + Sort + Search all work together

## Technical Specifications

### Frontend Implementation

**Component: SortSelect**

```typescript
interface SortSelectProps {
  value: SortOption;
  onChange: (option: SortOption) => void;
}

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest First', icon: ArrowDown },
  { value: 'oldest', label: 'Oldest First', icon: ArrowUp },
  { value: 'priority-high', label: 'Priority: High → Low', icon: AlertCircle },
  { value: 'priority-low', label: 'Priority: Low → High', icon: Circle },
  { value: 'title-asc', label: 'Title A-Z', icon: SortAsc },
  { value: 'title-desc', label: 'Title Z-A', icon: SortDesc },
  { value: 'completed', label: 'Completed First', icon: CheckCircle },
  { value: 'pending', label: 'Pending First', icon: Clock },
];

function SortSelect({ value, onChange }: SortSelectProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 border rounded-lg"
      >
        <ArrowUpDown className="h-5 w-5" />
        <span>{SORT_OPTIONS.find(opt => opt.value === value)?.label}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white border rounded-lg shadow-lg z-50">
          {SORT_OPTIONS.map(option => (
            <button
              key={option.value}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
              }}
              className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center justify-between"
            >
              <span className="flex items-center gap-2">
                <option.icon className="h-4 w-4" />
                {option.label}
              </span>
              {value === option.value && <Check className="h-4 w-4 text-purple-600" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Performance Optimization

**Memoization:**
- Sort function results are memoized
- Only re-sort when tasks array or sort option changes
- Avoid sorting on every render

**Stable Sort:**
- Use stable sort algorithm (JavaScript's `.sort()` is stable in modern browsers)
- Tasks with equal sort values maintain their relative order

**Large Lists:**
- Performance tested with up to 10,000 tasks
- Sort completes in < 100ms for 1000 tasks
- Virtual scrolling for lists over 500 items (future enhancement)

## UI/UX Requirements

### Visual Design

**Sort Button:**
- Icon: Up/down arrows
- Label: Current sort option name
- Badge: Shows active sort state
- Dropdown indicator: Chevron down icon

**Dropdown Menu:**
- Width: 224px (14rem)
- Max Height: 400px (scrollable if needed)
- Background: White
- Border: 1px gray-200
- Shadow: Large dropdown shadow
- Z-index: 50 (above most content)

**Selected Option:**
- Checkmark icon on right
- Purple text color
- Subtle background highlight

### User Feedback

**Sort Change Indicator:**
- Brief loading state (spinner) for large lists
- Smooth transition animation (optional)
- Scroll to top after sort change (optional)

**Persistence Feedback:**
- Toast notification: "Sort preference saved" (optional)
- Visual indicator that sort is persisted

## Accessibility

**Keyboard Navigation:**
- `Tab`: Focus sort button
- `Enter/Space`: Open dropdown
- `Arrow Up/Down`: Navigate options
- `Enter`: Select option
- `Escape`: Close dropdown

**Screen Reader Support:**
- `aria-label="Sort tasks"`
- `aria-expanded` state on dropdown
- `aria-selected` on current option
- Announce sort change

## Performance Requirements

- **Sort Execution**: < 100ms for 1000 tasks
- **UI Update**: < 16ms (60fps) after sort
- **Storage Write**: < 10ms to localStorage

## Security Requirements

- Client-side only (no API calls)
- No user data sent to server
- Safe localStorage usage (no PII)

## Testing Requirements

### Unit Tests

- Sort by newest
- Sort by oldest
- Sort by priority (both directions)
- Sort by title (both directions)
- Sort by completion status (both directions)
- Stable sort (equal values maintain order)
- Empty task list
- Single task
- Large task list (1000+ items)

### Integration Tests

- Sort + Search combination
- Sort + Filter combination
- Sort state persistence
- Sort in Kanban view (per column)

### E2E Tests

- User selects sort option
- Task list reorders
- Sort persists on page refresh
- Sort works with search active

## Future Enhancements

- **Multi-Level Sort**: Secondary sort criteria (e.g., priority then date)
- **Custom Sort**: User-defined sort order
- **Sort by Due Date**: Sort by upcoming deadlines
- **Sort by Last Updated**: Show recently modified tasks
- **Sort Indicators**: Arrow icons showing sort direction
- **Sort Transitions**: Animated reordering

## Related Specifications

- **Task CRUD**: `@specs/features/task-crud.md`
- **Task Priorities**: `@specs/features/task-priorities.md`
- **Kanban Board**: `@specs/features/kanban-board.md`
- **UI Components**: `@specs/ui/components.md`

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-04 | Development Team | Initial specification |

---

**Specification Status:** ✅ Implemented
**Implementation Date:** 2026-01-04
**Last Reviewed:** 2026-01-06
