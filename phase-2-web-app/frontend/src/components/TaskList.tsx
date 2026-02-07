"use client";

/**
 * Task list component with React Query integration.
 *
 * Features:
 * - Fetches tasks using React Query
 * - Filter support (all/pending/completed)
 * - Loading, error, and empty states
 * - Optimistic updates for toggle
 * - Delete confirmation modal
 * - Maps tasks to TaskItem components
 */

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import TaskItem from "@/components/TaskItem";
import DeleteConfirmation from "@/components/DeleteConfirmation";
import { useTasks, useToggleTask, useDeleteTask } from "@/hooks/useTasks";
import { getUser } from "@/lib/auth";
import { filterTasksBySearch, sortTasks } from "@/lib/utils";
import type { TaskStatus, User, SortOption } from "@/lib/types";

export interface TaskListProps {
  filter?: TaskStatus;
  searchQuery?: string;
  sortBy?: SortOption;
}

export default function TaskList({
  filter = "all",
  searchQuery = "",
  sortBy = "newest"
}: TaskListProps) {
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

  // Fetch tasks using React Query
  const { data: tasks, isLoading, error } = useTasks(user?.id || "", filter);

  // Apply client-side search and sort with memoization
  const filteredAndSortedTasks = useMemo(() => {
    if (!tasks) return [];

    // Step 1: Filter by search query
    const filtered = filterTasksBySearch(tasks, searchQuery);

    // Step 2: Sort the filtered results
    const sorted = sortTasks(filtered, sortBy);

    return sorted;
  }, [tasks, searchQuery, sortBy]);

  // Toggle mutation with optimistic updates
  const toggleMutation = useToggleTask(user?.id || "", filter);

  // Delete mutation
  const deleteMutation = useDeleteTask(user?.id || "");

  // Handle toggle completion
  function handleToggle(taskId: string) {
    toggleMutation.mutate(taskId);
  }

  // Handle delete click (show modal)
  function handleDeleteClick(taskId: string) {
    setTaskToDelete(taskId);
    setShowDeleteModal(true);
  }

  // Handle delete confirmation
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

  // Handle delete cancel
  function handleDeleteCancel() {
    setShowDeleteModal(false);
    setTaskToDelete(null);
  }

  // Loading state
  if (isLoading || !user) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Card>
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          Error loading tasks: {error.message}
        </div>
      </Card>
    );
  }

  // Empty state
  if (!filteredAndSortedTasks || filteredAndSortedTasks.length === 0) {
    const hasTasksButFiltered = tasks && tasks.length > 0 && filteredAndSortedTasks.length === 0;

    return (
      <>
        <Card className="text-center py-12" padding="lg">
          <p className="text-gray-600 text-lg mb-4">
            {hasTasksButFiltered
              ? "No tasks match your search."
              : filter === "all"
              ? "No tasks yet!"
              : `No ${filter} tasks.`}
          </p>
          {!hasTasksButFiltered && (
            <Link href="/tasks/new">
              <Button variant="primary">Create your first task</Button>
            </Link>
          )}
        </Card>

        {/* Delete Confirmation Modal */}
        <DeleteConfirmation
          isOpen={showDeleteModal}
          onClose={handleDeleteCancel}
          onConfirm={handleDeleteConfirm}
          isDeleting={deleteMutation.isPending}
        />
      </>
    );
  }

  // Tasks list
  return (
    <>
      <div className="space-y-4">
        {filteredAndSortedTasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggleComplete={handleToggle}
            onDelete={handleDeleteClick}
          />
        ))}
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmation
        isOpen={showDeleteModal}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        isDeleting={deleteMutation.isPending}
      />
    </>
  );
}
