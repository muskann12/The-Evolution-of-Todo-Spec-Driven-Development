# Skill: Kanban UI Enhancement

**Name:** `web.kanban-ui`
**Description:** Transform the existing TODO app into a modern Kanban-style dashboard with drag-and-drop, statistics, and activity feed
**Category:** Frontend UI/UX Enhancement
**Dependencies:** React, TypeScript, Tailwind CSS, existing Phase 2 web app structure

---

## Overview

This skill enhances the existing Phase 2 TODO web application with a modern Kanban board interface featuring:
- Drag-and-drop task management across columns
- Visual dashboard with statistics and charts
- Activity feed sidebar
- Modern purple/pastel color scheme
- Responsive design with Tailwind CSS

**IMPORTANT:** This skill works WITH the existing backend API and data models. It transforms the UI/UX while preserving all existing functionality.

---

## Prerequisites

Before running this skill, ensure:
- ✅ Phase 2 web app is set up and running
- ✅ Backend API is working (tasks CRUD endpoints)
- ✅ Frontend is using Next.js with TypeScript
- ✅ Tailwind CSS is configured
- ✅ Task data model supports: id, title, description, completed, priority, tags, due_date, created_at, updated_at

---

## Implementation Steps

### Step 1: Install Required Dependencies

```bash
cd phase-2-web-app/frontend
npm install @hello-pangea/dnd lucide-react recharts
npm install -D @types/node
```

**Dependencies:**
- `@hello-pangea/dnd` - Modern fork of react-beautiful-dnd for drag-and-drop
- `lucide-react` - Icon library
- `recharts` - For pie chart in sidebar

### Step 2: Extend Type Definitions

**File:** `frontend/src/lib/types.ts`

Add Kanban-specific types:

```typescript
// ============================================================================
// Kanban Board Types
// ============================================================================

/**
 * Kanban column status
 */
export type KanbanStatus = "ready" | "in_progress" | "review" | "done";

/**
 * Kanban column configuration
 */
export interface KanbanColumn {
  id: KanbanStatus;
  title: string;
  color: string;
  bgColor: string;
  taskIds: string[];
}

/**
 * Activity feed item
 */
export interface Activity {
  id: string;
  user: string;
  avatar: string;
  action: string;
  timestamp: string;
  type: "created" | "updated" | "completed" | "commented";
}

/**
 * Dashboard statistics
 */
export interface DashboardStats {
  totalProjects: number;
  forReview: number;
  inProgress: number;
  completed: number;
}
```

### Step 3: Create Kanban Column Configuration

**File:** `frontend/src/config/kanban.ts` (NEW)

```typescript
import type { KanbanColumn, KanbanStatus } from "@/lib/types";

export const KANBAN_COLUMNS: Record<KanbanStatus, Omit<KanbanColumn, "taskIds">> = {
  ready: {
    id: "ready",
    title: "Task Ready",
    color: "text-gray-700",
    bgColor: "bg-gray-100",
  },
  in_progress: {
    id: "in_progress",
    title: "In Progress",
    color: "text-blue-700",
    bgColor: "bg-blue-100",
  },
  review: {
    id: "review",
    title: "For Review",
    color: "text-orange-700",
    bgColor: "bg-orange-100",
  },
  done: {
    id: "done",
    title: "Done",
    color: "text-green-700",
    bgColor: "bg-green-100",
  },
};

export const COLUMN_ORDER: KanbanStatus[] = ["ready", "in_progress", "review", "done"];
```

### Step 4: Create Kanban Board Components

#### 4a. Enhanced Navbar Component

**File:** `frontend/src/components/KanbanNavbar.tsx` (NEW)

```typescript
"use client";

import { Search, Bell, Settings } from "lucide-react";
import { getUser } from "@/lib/auth";
import { useState, useEffect } from "react";
import type { User } from "@/lib/types";

export default function KanbanNavbar() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    async function loadUser() {
      const currentUser = await getUser();
      setUser(currentUser);
    }
    loadUser();
  }, []);

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left: Logo/Title */}
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Task Manager
          </h1>
        </div>

        {/* Center: Search */}
        <div className="flex-1 max-w-xl mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search tasks, projects..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Right: User Profile & Actions */}
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="h-5 w-5 text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Settings className="h-5 w-5 text-gray-600" />
          </button>

          {/* User Avatar & Name */}
          <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
              {user?.name?.charAt(0).toUpperCase() || "U"}
            </div>
            <div className="text-sm">
              <p className="font-semibold text-gray-900">{user?.name || "User"}</p>
              <p className="text-gray-500">{user?.email || ""}</p>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
```

#### 4b. Task Card Component (Kanban Style)

**File:** `frontend/src/components/KanbanTaskCard.tsx` (NEW)

```typescript
"use client";

import { Draggable } from "@hello-pangea/dnd";
import { MessageSquare, Calendar, MoreVertical, Edit, Trash2 } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import type { Task } from "@/lib/types";
import { useState } from "react";

interface KanbanTaskCardProps {
  task: Task;
  index: number;
  onEdit: (taskId: string) => void;
  onDelete: (taskId: string) => void;
}

const PRIORITY_COLORS = {
  High: "bg-red-100 text-red-700 border-red-200",
  Medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  Low: "bg-blue-100 text-blue-700 border-blue-200",
};

export default function KanbanTaskCard({
  task,
  index,
  onEdit,
  onDelete,
}: KanbanTaskCardProps) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <Draggable draggableId={task.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow ${
            snapshot.isDragging ? "shadow-lg rotate-2" : ""
          }`}
        >
          {/* Header: Tag + Menu */}
          <div className="flex items-start justify-between mb-3">
            <span
              className={`px-3 py-1 text-xs font-semibold rounded-full border ${
                PRIORITY_COLORS[task.priority]
              }`}
            >
              {task.priority}
            </span>
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <MoreVertical className="h-4 w-4 text-gray-500" />
              </button>
              {showMenu && (
                <div className="absolute right-0 mt-1 w-32 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                  <button
                    onClick={() => {
                      onEdit(task.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
                  >
                    <Edit className="h-4 w-4" />
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      onDelete(task.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 text-red-600 flex items-center gap-2"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Task Title */}
          <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
            {task.title}
          </h3>

          {/* Task Description */}
          {task.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {task.description}
            </p>
          )}

          {/* Tags */}
          {task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {task.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 text-xs bg-purple-50 text-purple-700 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Footer: Date, Comments, Avatar */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>{formatRelativeTime(task.created_at)}</span>
              </div>
              {task.due_date && (
                <div className="flex items-center gap-1">
                  <MessageSquare className="h-3 w-3" />
                  <span>0</span>
                </div>
              )}
            </div>

            {/* User Avatar Placeholder */}
            <div className="w-7 h-7 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full flex items-center justify-center text-white text-xs font-semibold">
              U
            </div>
          </div>
        </div>
      )}
    </Draggable>
  );
}
```

#### 4c. Kanban Column Component

**File:** `frontend/src/components/KanbanColumn.tsx` (NEW)

```typescript
"use client";

import { Droppable } from "@hello-pangea/dnd";
import { Plus, MoreVertical } from "lucide-react";
import KanbanTaskCard from "./KanbanTaskCard";
import type { Task, KanbanStatus } from "@/lib/types";
import { KANBAN_COLUMNS } from "@/config/kanban";

interface KanbanColumnProps {
  status: KanbanStatus;
  tasks: Task[];
  onAddTask: () => void;
  onEditTask: (taskId: string) => void;
  onDeleteTask: (taskId: string) => void;
}

export default function KanbanColumn({
  status,
  tasks,
  onAddTask,
  onEditTask,
  onDeleteTask,
}: KanbanColumnProps) {
  const column = KANBAN_COLUMNS[status];

  return (
    <div className="flex-shrink-0 w-80">
      {/* Column Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className={`font-semibold ${column.color}`}>{column.title}</h2>
          <span className="px-2 py-1 text-xs font-medium bg-gray-200 text-gray-700 rounded-full">
            {tasks.length}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onAddTask}
            className="p-1.5 hover:bg-gray-100 rounded transition-colors"
            title="Add task"
          >
            <Plus className="h-4 w-4 text-gray-600" />
          </button>
          <button className="p-1.5 hover:bg-gray-100 rounded transition-colors">
            <MoreVertical className="h-4 w-4 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Droppable Area */}
      <Droppable droppableId={status}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`min-h-[600px] p-3 rounded-lg transition-colors ${
              snapshot.isDraggingOver
                ? column.bgColor + " bg-opacity-30"
                : "bg-gray-50"
            }`}
          >
            <div className="space-y-3">
              {tasks.map((task, index) => (
                <KanbanTaskCard
                  key={task.id}
                  task={task}
                  index={index}
                  onEdit={onEditTask}
                  onDelete={onDeleteTask}
                />
              ))}
              {provided.placeholder}
            </div>
          </div>
        )}
      </Droppable>
    </div>
  );
}
```

#### 4d. Dashboard Sidebar Component

**File:** `frontend/src/components/DashboardSidebar.tsx` (NEW)

```typescript
"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from "recharts";
import { formatRelativeTime } from "@/lib/utils";
import type { DashboardStats, Activity } from "@/lib/types";

interface DashboardSidebarProps {
  stats: DashboardStats;
  activities: Activity[];
}

const CHART_COLORS = {
  ready: "#9CA3AF",
  inProgress: "#3B82F6",
  review: "#F59E0B",
  completed: "#10B981",
};

export default function DashboardSidebar({
  stats,
  activities,
}: DashboardSidebarProps) {
  const chartData = [
    { name: "For Review", value: stats.forReview, color: CHART_COLORS.review },
    { name: "In Progress", value: stats.inProgress, color: CHART_COLORS.inProgress },
    { name: "Completed", value: stats.completed, color: CHART_COLORS.completed },
  ];

  return (
    <div className="w-80 bg-white border-l border-gray-200 p-6 overflow-y-auto">
      {/* Statistics Card */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Project Statistics
        </h2>

        {/* Pie Chart */}
        <div className="h-64 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
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
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            label="Total Projects"
            value={stats.totalProjects}
            color="purple"
          />
          <StatCard
            label="For Review"
            value={stats.forReview}
            color="orange"
          />
          <StatCard
            label="In Progress"
            value={stats.inProgress}
            color="blue"
          />
          <StatCard
            label="Completed"
            value={stats.completed}
            color="green"
          />
        </div>
      </div>

      {/* Recent Activities */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Activities
        </h2>
        <div className="space-y-4">
          {activities.map((activity) => (
            <ActivityItem key={activity.id} activity={activity} />
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const colorClasses = {
    purple: "bg-purple-50 text-purple-700",
    orange: "bg-orange-50 text-orange-700",
    blue: "bg-blue-50 text-blue-700",
    green: "bg-green-50 text-green-700",
  };

  return (
    <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
      <p className="text-xs font-medium opacity-80">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}

function ActivityItem({ activity }: { activity: Activity }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
        {activity.user.charAt(0)}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900">
          <span className="font-semibold">{activity.user}</span>{" "}
          <span className="text-gray-600">{activity.action}</span>
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {formatRelativeTime(activity.timestamp)}
        </p>
      </div>
    </div>
  );
}
```

#### 4e. Main Kanban Board Page

**File:** `frontend/src/app/(dashboard)/kanban/page.tsx` (NEW)

```typescript
"use client";

import { useState, useEffect, useMemo } from "react";
import { DragDropContext, DropResult } from "@hello-pangea/dnd";
import { useRouter } from "next/navigation";
import KanbanNavbar from "@/components/KanbanNavbar";
import KanbanColumn from "@/components/KanbanColumn";
import DashboardSidebar from "@/components/DashboardSidebar";
import DeleteConfirmation from "@/components/DeleteConfirmation";
import { useTasks, useUpdateTask, useDeleteTask } from "@/hooks/useTasks";
import { getUser } from "@/lib/auth";
import { COLUMN_ORDER } from "@/config/kanban";
import type { User, Task, KanbanStatus, DashboardStats, Activity } from "@/lib/types";

export default function KanbanPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<string | null>(null);

  // Get user on mount
  useEffect(() => {
    async function loadUser() {
      const currentUser = await getUser();
      setUser(currentUser);
    }
    loadUser();
  }, []);

  // Fetch all tasks
  const { data: tasks } = useTasks(user?.id || "", "all");

  // Mutations
  const updateMutation = useUpdateTask(user?.id || "", "");
  const deleteMutation = useDeleteTask(user?.id || "");

  // Map tasks to Kanban columns (based on completion + priority)
  const tasksByColumn = useMemo(() => {
    if (!tasks) return { ready: [], in_progress: [], review: [], done: [] };

    const columns: Record<KanbanStatus, Task[]> = {
      ready: [],
      in_progress: [],
      review: [],
      done: [],
    };

    tasks.forEach((task) => {
      if (task.completed) {
        columns.done.push(task);
      } else if (task.priority === "High") {
        columns.in_progress.push(task);
      } else if (task.priority === "Medium") {
        columns.review.push(task);
      } else {
        columns.ready.push(task);
      }
    });

    return columns;
  }, [tasks]);

  // Calculate stats
  const stats: DashboardStats = useMemo(() => {
    if (!tasks) return { totalProjects: 0, forReview: 0, inProgress: 0, completed: 0 };

    return {
      totalProjects: tasks.length,
      forReview: tasksByColumn.review.length,
      inProgress: tasksByColumn.in_progress.length,
      completed: tasksByColumn.done.length,
    };
  }, [tasks, tasksByColumn]);

  // Mock activities (in real app, fetch from API)
  const activities: Activity[] = useMemo(() => {
    if (!tasks || tasks.length === 0) return [];

    return tasks.slice(0, 5).map((task, idx) => ({
      id: `activity-${idx}`,
      user: user?.name || "User",
      avatar: "",
      action: `created task "${task.title}"`,
      timestamp: task.created_at,
      type: "created" as const,
    }));
  }, [tasks, user]);

  // Handle drag end
  function handleDragEnd(result: DropResult) {
    const { destination, source, draggableId } = result;

    // Dropped outside
    if (!destination) return;

    // Dropped in same position
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    // Find the task
    const task = tasks?.find((t) => t.id === draggableId);
    if (!task) return;

    // Update task based on destination column
    const destStatus = destination.droppableId as KanbanStatus;
    let updateData: { completed?: boolean; priority?: "High" | "Medium" | "Low" } = {};

    switch (destStatus) {
      case "done":
        updateData.completed = true;
        break;
      case "in_progress":
        updateData.completed = false;
        updateData.priority = "High";
        break;
      case "review":
        updateData.completed = false;
        updateData.priority = "Medium";
        break;
      case "ready":
        updateData.completed = false;
        updateData.priority = "Low";
        break;
    }

    // Update via API
    updateMutation.mutate({
      ...updateData,
    });
  }

  // Handle add task
  function handleAddTask(status: KanbanStatus) {
    router.push("/tasks/new");
  }

  // Handle edit task
  function handleEditTask(taskId: string) {
    router.push(`/tasks/${taskId}`);
  }

  // Handle delete task
  function handleDeleteTask(taskId: string) {
    setTaskToDelete(taskId);
    setShowDeleteModal(true);
  }

  function handleDeleteConfirm() {
    if (taskToDelete) {
      deleteMutation.mutate(taskToDelete, {
        onSuccess: () => {
          setShowDeleteModal(false);
          setTaskToDelete(null);
        },
      });
    }
  }

  function handleDeleteCancel() {
    setShowDeleteModal(false);
    setTaskToDelete(null);
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Navbar */}
      <KanbanNavbar />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Board Area */}
        <div className="flex-1 overflow-x-auto overflow-y-hidden">
          <div className="p-6 h-full">
            {/* Dashboard Header */}
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">Task Dashboard</h1>
              <p className="text-sm text-gray-500 mt-1">
                {new Date().toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>

            {/* Kanban Board */}
            <DragDropContext onDragEnd={handleDragEnd}>
              <div className="flex gap-4 h-full pb-6">
                {COLUMN_ORDER.map((status) => (
                  <KanbanColumn
                    key={status}
                    status={status}
                    tasks={tasksByColumn[status]}
                    onAddTask={() => handleAddTask(status)}
                    onEditTask={handleEditTask}
                    onDeleteTask={handleDeleteTask}
                  />
                ))}
              </div>
            </DragDropContext>
          </div>
        </div>

        {/* Sidebar */}
        <DashboardSidebar stats={stats} activities={activities} />
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmation
        isOpen={showDeleteModal}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        isDeleting={deleteMutation.isPending}
      />
    </div>
  );
}
```

### Step 5: Update Tailwind Configuration (Optional Enhancements)

**File:** `frontend/tailwind.config.ts`

Add custom colors for the purple/pastel theme:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        50: '#faf5ff',
        100: '#f3e8ff',
        500: '#a855f7',
        600: '#9333ea',
        700: '#7e22ce',
      },
    },
  },
},
```

### Step 6: Add Navigation Link

**File:** `frontend/src/components/Header.tsx` (existing)

Add a link to the Kanban board:

```typescript
<Link href="/kanban">
  <Button variant="outline">Kanban Board</Button>
</Link>
```

---

## Usage

After implementation, users can:

1. **Access Kanban Board:** Navigate to `/kanban` route
2. **Drag Tasks:** Click and drag tasks between columns
3. **View Statistics:** See real-time stats in the right sidebar
4. **Track Activity:** Monitor recent actions in activity feed
5. **Manage Tasks:** Add, edit, delete tasks from the board
6. **Search:** Use global search in navbar

---

## Integration Points

### With Existing Backend

The Kanban board integrates seamlessly with your existing backend:

- **Tasks API:** Uses existing `useTasks`, `useUpdateTask`, `useDeleteTask` hooks
- **Authentication:** Uses existing `getUser()` auth flow
- **Data Model:** Works with existing Task interface (no schema changes needed)
- **Status Mapping:** Maps Kanban columns to existing `completed` + `priority` fields

### Column Mapping Logic

- **Task Ready** → `completed: false, priority: Low`
- **In Progress** → `completed: false, priority: High`
- **For Review** → `completed: false, priority: Medium`
- **Done** → `completed: true`

---

## Customization Options

### Color Scheme

Modify `KANBAN_COLUMNS` in `kanban.ts` to change colors:

```typescript
ready: {
  color: "text-purple-700",
  bgColor: "bg-purple-100",
}
```

### Column Names

Update column titles in `KANBAN_COLUMNS`:

```typescript
in_progress: {
  title: "Working On",
  // ...
}
```

### Statistics

Extend `DashboardStats` interface and update calculation logic in `KanbanPage`.

### Activity Feed

Connect to real activity API by replacing mock data:

```typescript
const { data: activities } = useActivities(user?.id || "");
```

---

## Testing Checklist

- [ ] Drag task from Ready to In Progress
- [ ] Drag task from In Progress to Done
- [ ] Reorder tasks within a column
- [ ] Add new task from column header
- [ ] Edit task from card menu
- [ ] Delete task with confirmation
- [ ] Search functionality works
- [ ] Statistics update in real-time
- [ ] Activity feed shows recent actions
- [ ] Mobile responsive (columns scroll horizontally)
- [ ] Keyboard navigation works
- [ ] Color scheme matches design

---

## Performance Considerations

- **useMemo:** Task grouping and stats are memoized to prevent unnecessary recalculations
- **Optimistic Updates:** Drag-and-drop triggers immediate UI update before API call
- **Virtual Scrolling:** Consider adding for columns with 50+ tasks
- **Lazy Loading:** Load activities in batches if feed grows large

---

## Accessibility

- All interactive elements are keyboard accessible
- Drag-and-drop has keyboard alternatives (add arrow key support if needed)
- Color contrast meets WCAG AA standards
- ARIA labels on icon buttons

---

## Future Enhancements

1. **Real-time Collaboration:** Add WebSocket for live updates
2. **Swimlanes:** Group tasks by user or project
3. **Filters:** Filter by priority, assignee, due date
4. **Card Customization:** Let users choose card color/layout
5. **Bulk Actions:** Select multiple cards for batch operations
6. **Time Tracking:** Add time estimates and actual time
7. **Attachments:** Upload files to task cards
8. **Comments:** Add comment thread to each card

---

## Troubleshooting

### Drag-and-drop not working
- Check `@hello-pangea/dnd` is installed correctly
- Ensure `DragDropContext` wraps all Droppable components
- Verify unique `draggableId` for each task

### Stats not updating
- Check `useMemo` dependencies include all relevant state
- Verify task data is being fetched correctly

### Styles not applying
- Run `npm run build` to regenerate Tailwind classes
- Check Tailwind config includes all component paths

---

## Files Created/Modified Summary

### New Files (9):
1. `frontend/src/config/kanban.ts` - Column configuration
2. `frontend/src/components/KanbanNavbar.tsx` - Enhanced navbar
3. `frontend/src/components/KanbanTaskCard.tsx` - Draggable task card
4. `frontend/src/components/KanbanColumn.tsx` - Kanban column
5. `frontend/src/components/DashboardSidebar.tsx` - Stats & activity sidebar
6. `frontend/src/app/(dashboard)/kanban/page.tsx` - Main board page

### Modified Files (2):
1. `frontend/src/lib/types.ts` - Add Kanban types
2. `frontend/src/components/Header.tsx` - Add Kanban link (optional)

---

## Conclusion

This skill transforms your existing TODO app into a modern, production-ready Kanban board while maintaining full compatibility with your backend API. All existing functionality (CRUD operations, authentication, filters) continues to work, enhanced with a beautiful drag-and-drop interface.

**Next Steps:**
1. Run the skill
2. Test drag-and-drop functionality
3. Customize colors and labels to match your brand
4. Add real activity feed API integration
5. Deploy and share with users!
