"use client";

/**
 * Edit task page.
 *
 * Features:
 * - Fetches existing task by ID
 * - Pre-populates TaskForm with task data
 * - React Query mutation for update
 * - Error handling (fetch error, update error, not found)
 * - Redirect to /tasks on success
 * - Loading states
 */

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import TaskForm from "@/components/TaskForm";
import { useTask, useUpdateTask } from "@/hooks/useTasks";
import { getUser } from "@/lib/auth";
import type { User, TaskUpdate } from "@/lib/types";

export default function EditTaskPage() {
  const router = useRouter();
  const params = useParams();
  const taskId = params.id as string;

  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState("");

  // Get user on mount
  useEffect(() => {
    async function loadUser() {
      const currentUser = await getUser();
      setUser(currentUser);
    }
    loadUser();
  }, []);

  // Fetch task
  const {
    data: task,
    isLoading,
    error: fetchError,
  } = useTask(user?.id || "", taskId);

  // Update mutation
  const updateMutation = useUpdateTask(user?.id || "", taskId);

  // Submit handler
  function handleSubmit(data: TaskUpdate) {
    setError("");
    updateMutation.mutate(data, {
      onSuccess: () => {
        // Redirect to tasks list
        router.push("/tasks");
      },
      onError: (err: any) => {
        setError(err.message || "Failed to update task");
      },
    });
  }

  // Cancel handler
  function handleCancel() {
    router.push("/tasks");
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
  if (fetchError) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          Error loading task: {fetchError.message}
        </div>
      </div>
    );
  }

  // Not found
  if (!task) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="p-4 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
          Task not found
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Task Form */}
      <TaskForm
        initialData={task}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={updateMutation.isPending}
      />
    </div>
  );
}
