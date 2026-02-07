"use client";

/**
 * Main Tasks page - Kanban Board View (Default).
 *
 * Features:
 * - Kanban board with drag-and-drop
 * - 4 columns: Ready, In Progress, Review, Done
 * - Dashboard statistics with pie chart
 * - Activity feed
 * - Modern purple/pastel design
 */

import { useState, useEffect, useMemo } from "react";
import { DragDropContext, DropResult } from "@hello-pangea/dnd";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import KanbanNavbar from "@/components/KanbanNavbar";
import KanbanColumn from "@/components/KanbanColumn";
import DashboardSidebar from "@/components/DashboardSidebar";
import DeleteConfirmation from "@/components/DeleteConfirmation";
import CreateTaskModal from "@/components/CreateTaskModal";
import { useTasks, useUpdateTask, useDeleteTask, taskKeys } from "@/hooks/useTasks";
import { getUser } from "@/lib/auth";
import { COLUMN_ORDER } from "@/config/kanban";
import type { User, Task, KanbanStatus, DashboardStats, Activity, SortOption } from "@/lib/types";

export default function TasksPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [user, setUser] = useState<User | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<string | null>(null);
  const [taskToUpdate, setTaskToUpdate] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [sortBy, setSortBy] = useState<SortOption>("newest");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Get user on mount
  useEffect(() => {
    async function loadUser() {
      const currentUser = await getUser();
      setUser(currentUser);
    }
    loadUser();
  }, []);

  // Fetch all tasks
  const { data: tasks, isLoading } = useTasks(user?.id || "", "all");

  // Mutations
  const updateMutation = useUpdateTask(user?.id || "", taskToUpdate || "");
  const deleteMutation = useDeleteTask(user?.id || "");

  // Sort tasks helper function
  function sortTasks(tasks: Task[]): Task[] {
    const sorted = [...tasks];

    switch (sortBy) {
      case "newest":
        return sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      case "oldest":
        return sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      case "priority-high":
        const priorityOrder = { High: 0, Medium: 1, Low: 2 };
        return sorted.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
      case "priority-low":
        const priorityOrderLow = { Low: 0, Medium: 1, High: 2 };
        return sorted.sort((a, b) => priorityOrderLow[a.priority] - priorityOrderLow[b.priority]);
      case "title-asc":
        return sorted.sort((a, b) => a.title.localeCompare(b.title));
      case "title-desc":
        return sorted.sort((a, b) => b.title.localeCompare(a.title));
      case "completed":
        return sorted.sort((a, b) => (b.completed ? 1 : 0) - (a.completed ? 1 : 0));
      case "pending":
        return sorted.sort((a, b) => (a.completed ? 1 : 0) - (b.completed ? 1 : 0));
      default:
        return sorted;
    }
  }

  // Map tasks to Kanban columns (based on status field)
  const tasksByColumn = useMemo(() => {
    if (!tasks) return { ready: [], in_progress: [], review: [], done: [] };

    // Filter tasks based on search query
    const filteredTasks = tasks.filter((task) => {
      if (!searchQuery) return true;

      const query = searchQuery.toLowerCase();
      const titleMatch = task.title.toLowerCase().includes(query);
      const descriptionMatch = task.description?.toLowerCase().includes(query);
      const tagsMatch = task.tags?.some(tag => tag.toLowerCase().includes(query));

      return titleMatch || descriptionMatch || tagsMatch;
    });

    const columns: Record<KanbanStatus, Task[]> = {
      ready: [],
      in_progress: [],
      review: [],
      done: [],
    };

    // Group tasks by their status field
    filteredTasks.forEach((task) => {
      const status = task.status || "ready"; // Default to ready if status is undefined
      if (columns[status]) {
        columns[status].push(task);
      } else {
        columns.ready.push(task); // Fallback to ready for invalid status
      }
    });

    // Apply sorting to each column
    columns.ready = sortTasks(columns.ready);
    columns.in_progress = sortTasks(columns.in_progress);
    columns.review = sortTasks(columns.review);
    columns.done = sortTasks(columns.done);

    return columns;
  }, [tasks, sortBy, searchQuery]);

  // Calculate stats
  const stats: DashboardStats = useMemo(() => {
    if (!tasks) return { totalProjects: 0, ready: 0, forReview: 0, inProgress: 0, completed: 0 };

    return {
      totalProjects: tasks.length,
      ready: tasksByColumn.ready.length,
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

  // Handle drag end with optimistic updates
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
    if (!task || !user) return;

    // Update task status based on destination column
    const destStatus = destination.droppableId as KanbanStatus;
    const updateData: { status: KanbanStatus; completed?: boolean } = {
      status: destStatus,
    };

    // Update completed status when moving to/from done column
    if (destStatus === "done") {
      updateData.completed = true;
    } else {
      updateData.completed = false;
    }

    // Optimistically update the task in the cache
    const queryKey = taskKeys.list(user.id, "all");
    const previousTasks = queryClient.getQueryData<Task[]>(queryKey);

    // Immediately update the cache for instant UI feedback
    queryClient.setQueryData<Task[]>(queryKey, (old) => {
      if (!old) return old;
      return old.map((t) =>
        t.id === draggableId
          ? { ...t, status: destStatus, completed: updateData.completed ?? t.completed }
          : t
      );
    });

    // Set the task to update and trigger mutation
    setTaskToUpdate(draggableId);

    // Update via API
    updateMutation.mutate(updateData, {
      onError: () => {
        // Rollback on error
        queryClient.setQueryData(queryKey, previousTasks);
      },
      onSettled: () => {
        // Refetch to ensure sync with server
        queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      },
    });
  }

  // Handle add task
  function handleAddTask(_status: KanbanStatus) {
    setIsCreateModalOpen(true);
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

  if (isLoading || !user) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-200 border-t-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 relative overflow-hidden">
      {/* Subtle animated gradient orbs in background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow animation-delay-400"></div>
        <div className="absolute top-1/2 right-1/4 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow animation-delay-200"></div>
      </div>

      {/* Content wrapper with relative positioning */}
      <div className="relative z-10 h-screen flex flex-col">
      {/* Navbar */}
      <KanbanNavbar
        sortBy={sortBy}
        onSortChange={setSortBy}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Board Area */}
        <div className="flex-1 overflow-x-auto overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
          <div className="p-4 max-w-[calc(100vw-20rem)]">
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
              <div className="flex gap-3 pb-6">
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

      {/* Create Task Modal */}
      {user && (
        <CreateTaskModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          userId={user.id}
        />
      )}
      </div>
    </div>
  );
}
