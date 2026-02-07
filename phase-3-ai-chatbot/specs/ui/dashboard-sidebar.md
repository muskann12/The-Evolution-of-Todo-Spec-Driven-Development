---
Spec ID: UI-005
Feature: Dashboard Sidebar
Status: Implemented
Version: 1.0
Created: 2025-12-30
Last Updated: 2026-01-03
Authors: Development Team
Related Specs:
  - Kanban Board: @specs/features/kanban-board.md
  - Task CRUD: @specs/features/task-crud.md
  - UI Components: @specs/ui/components.md
---

# UI Specification: Dashboard Sidebar

## Overview

The Dashboard Sidebar is a fixed-width panel displayed on the right side of the Kanban board view. It provides real-time statistics, visual data representation via pie chart, and an activity feed showing recent task actions.

## Purpose

- **Quick Overview**: Provide at-a-glance project status
- **Visual Analytics**: Display task distribution through interactive charts
- **Activity Tracking**: Show recent task changes and updates
- **Space Efficiency**: Maximize screen space for task management

## Component Location

- **Page**: Kanban Board View (`/tasks`)
- **Position**: Fixed right sidebar
- **Width**: 288px (18rem)
- **Height**: Full viewport height minus navbar

## Layout Structure

The sidebar shall contain three main sections stacked vertically:

```
┌──────────────────────────┐
│  PROJECT STATISTICS      │
│  ┌────────────────────┐  │
│  │   [Pie Chart]      │  │
│  │                    │  │
│  └────────────────────┘  │
│                          │
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐   │
│  │  │ │  │ │  │ │  │   │
│  └──┘ └──┘ └──┘ └──┘   │
│                          │
├──────────────────────────┤
│  RECENT ACTIVITIES       │
│  ○ User created task...  │
│  ○ User updated task...  │
│  ○ User completed...     │
│                          │
└──────────────────────────┘
```

## Component Specifications

### 1. Statistics Card

**Section Title**: "Project Statistics"

**Content Elements:**
- **Pie Chart**: Visual breakdown of tasks by status (4 segments)
- **Stat Cards Grid**: 4 cards displaying counts

**Pie Chart Specifications:**

| Segment | Label | Color | Data Source |
|---------|-------|-------|-------------|
| 1 | Ready | Gray (#9CA3AF) | `stats.ready` |
| 2 | In Progress | Blue (#3B82F6) | `stats.inProgress` |
| 3 | For Review | Purple (#8B5CF6) | `stats.forReview` |
| 4 | Completed | Green (#10B981) | `stats.completed` |

**Chart Configuration:**
- **Type**: Donut chart (pie with inner radius)
- **Library**: Recharts (`recharts` npm package)
- **Inner Radius**: 50px
- **Outer Radius**: 70px
- **Padding Angle**: 5 degrees
- **Responsive**: True (fits container)
- **Legend**: Below chart, showing all 4 categories
- **Animation**: Fade in on load

**Stat Cards Grid:**

```
┌────────────┬────────────┐
│   Total    │ For Review │
│  Projects  │            │
├────────────┼────────────┤
│    In      │ Completed  │
│  Progress  │            │
└────────────┴────────────┘
```

Each card displays:
- **Label**: Category name (small, uppercase)
- **Value**: Count number (large, bold)
- **Color**: Background matching segment color

**Card Styling:**
- Padding: 8px
- Border Radius: 8px
- Font Size: Label (10px), Value (20px)
- Background Colors:
  - Total Projects: purple-50
  - For Review: purple-50
  - In Progress: blue-50
  - Completed: green-50

**Code Structure:**
```typescript
interface DashboardStats {
  totalProjects: number;
  ready: number;
  forReview: number;
  inProgress: number;
  completed: number;
}

const chartData = [
  { name: 'Ready', value: stats.ready, color: '#9CA3AF' },
  { name: 'In Progress', value: stats.inProgress, color: '#3B82F6' },
  { name: 'For Review', value: stats.forReview, color: '#8B5CF6' },
  { name: 'Completed', value: stats.completed, color: '#10B981' },
];

<ResponsiveContainer width="100%" height={200}>
  <PieChart>
    <Pie
      data={chartData}
      cx="50%"
      cy="50%"
      innerRadius={50}
      outerRadius={70}
      paddingAngle={5}
      dataKey="value"
    >
      {chartData.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={entry.color} />
      ))}
    </Pie>
    <Legend />
  </PieChart>
</ResponsiveContainer>
```

### 2. Recent Activities Section

**Section Title**: "Recent Activities"

**Purpose**: Display chronological list of recent task actions

**Activity Types:**
1. Task Created
2. Task Updated
3. Task Completed
4. Task Deleted (future)
5. Comment Added (future)

**Activity Item Structure:**

Each activity displays:
- **User Avatar**: Circular badge with user initials
- **Activity Text**: "{User} {action} {task_title}"
- **Timestamp**: Relative time (e.g., "3 hours ago")

**Example Activities:**
- "John created task 'Update documentation'"
- "Sarah completed task 'Fix login bug'"
- "Mike updated task 'Design new feature'"

**Layout per Item:**
```
┌───────────────────────────────┐
│ [JD] John created task...     │
│      3 hours ago              │
├───────────────────────────────┤
│ [SM] Sarah completed...       │
│      5 hours ago              │
└───────────────────────────────┘
```

**Styling:**
- **Avatar**: 28px circle, gradient background (purple-to-blue)
- **Text**: 12px font, gray-900 for name, gray-600 for action
- **Timestamp**: 10px font, gray-500
- **Spacing**: 12px gap between items

**Maximum Items**: Display latest 5 activities

**Empty State**: "No recent activities"

**Code Structure:**
```typescript
interface Activity {
  id: string;
  user: string;
  action: string;
  timestamp: string;
  type: 'created' | 'updated' | 'completed' | 'commented';
}

function ActivityItem({ activity }: { activity: Activity }) {
  return (
    <div className="flex items-start gap-2">
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-400 to-blue-400 flex items-center justify-center text-white text-xs font-semibold">
        {activity.user.charAt(0).toUpperCase()}
      </div>
      <div className="flex-1">
        <p className="text-xs text-gray-900">
          <span className="font-semibold">{activity.user}</span>
          <span className="text-gray-600"> {activity.action}</span>
        </p>
        <p className="text-[10px] text-gray-500">
          {formatRelativeTime(activity.timestamp)}
        </p>
      </div>
    </div>
  );
}
```

## Data Flow

### Statistics Calculation

```typescript
const stats: DashboardStats = useMemo(() => {
  if (!tasks) return { totalProjects: 0, ready: 0, forReview: 0, inProgress: 0, completed: 0 };

  // Group tasks by status
  const byStatus = {
    ready: tasks.filter(t => t.status === 'ready').length,
    in_progress: tasks.filter(t => t.status === 'in_progress').length,
    review: tasks.filter(t => t.status === 'review').length,
    done: tasks.filter(t => t.status === 'done').length,
  };

  return {
    totalProjects: tasks.length,
    ready: byStatus.ready,
    forReview: byStatus.review,
    inProgress: byStatus.in_progress,
    completed: byStatus.done,
  };
}, [tasks]);
```

### Activity Feed Generation

```typescript
const activities: Activity[] = useMemo(() => {
  if (!tasks || tasks.length === 0) return [];

  // Mock activities from latest tasks (in real app, fetch from API)
  return tasks.slice(0, 5).map((task, idx) => ({
    id: `activity-${idx}`,
    user: user?.name || 'User',
    action: `created task "${task.title}"`,
    timestamp: task.created_at,
    type: 'created' as const,
  }));
}, [tasks, user]);
```

## Styling Specifications

### Sidebar Container

```css
.dashboard-sidebar {
  width: 18rem;              /* 288px */
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border-left: 1px solid rgb(243, 232, 255);  /* purple-100 */
  padding: 1rem;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: none;     /* Hide scrollbar (Firefox) */
}

.dashboard-sidebar::-webkit-scrollbar {
  display: none;             /* Hide scrollbar (Chrome, Safari) */
}
```

### Section Headers

```css
.section-header {
  font-size: 1rem;
  font-weight: 600;
  color: rgb(17, 24, 39);    /* gray-900 */
  margin-bottom: 0.75rem;
}
```

### Responsive Behavior

- **Desktop (≥1280px)**: Fixed 288px width, always visible
- **Laptop (1024-1279px)**: Fixed 256px width, always visible
- **Tablet (<1024px)**: Hidden, show as modal/drawer on icon click
- **Mobile (<768px)**: Hidden, accessible via hamburger menu

## Performance Requirements

- **Chart Render**: < 100ms
- **Stats Update**: Real-time (updates when tasks change)
- **Activity Feed**: Updates every 30 seconds (future polling)
- **Smooth Scrolling**: 60fps for activity list scroll

## Accessibility

- **ARIA Labels**: `aria-label="Dashboard statistics"`
- **Keyboard Navigation**: Tab through interactive elements
- **Screen Reader**: Announce stat values
- **Color Blind Safe**: Chart colors distinguishable
- **Focus Indicators**: Visible focus states

## Future Enhancements

- **Real-Time Updates**: WebSocket for live activity feed
- **Customizable Widgets**: User can add/remove sidebar sections
- **Team View**: Show team member activities
- **Filters**: Filter activities by type
- **Time Range**: View activities from different time periods
- **Export**: Download statistics as PDF/CSV
- **Charts**: Additional chart types (bar, line for trends)

## Dependencies

### NPM Packages

```json
{
  "recharts": "^2.10.0"  // Pie chart visualization
}
```

### Utility Functions

- `formatRelativeTime(timestamp: string)`: Convert timestamp to "3 hours ago"
- Example: `import { formatRelativeTime } from '@/lib/utils'`

## Related Specifications

- **Kanban Board**: `@specs/features/kanban-board.md`
- **Task CRUD**: `@specs/features/task-crud.md`
- **UI Components**: `@specs/ui/components.md`
- **Dashboard Layout**: `@specs/ui/layouts.md`

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-03 | Development Team | Initial specification |

---

**Specification Status:** ✅ Implemented
**Implementation Date:** 2026-01-03
**Last Reviewed:** 2026-01-06
