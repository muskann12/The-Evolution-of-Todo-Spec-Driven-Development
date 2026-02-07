/**
 * React Query hooks for task management.
 *
 * Provides type-safe hooks for all task operations:
 * - Fetching tasks (with caching)
 * - Creating tasks
 * - Updating tasks
 * - Deleting tasks
 * - Toggling completion (with optimistic updates)
 *
 * All hooks automatically handle:
 * - Loading states
 * - Error handling
 * - Cache invalidation
 * - Optimistic updates
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Task, TaskCreate, TaskUpdate, TaskStatus } from "@/lib/types";

// ============================================================================
// Query Keys Factory
// ============================================================================

/**
 * Centralized query keys for consistent cache management.
 * Hierarchical structure allows selective invalidation.
 */
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  list: (userId: string, filter?: TaskStatus) =>
    [...taskKeys.lists(), userId, filter] as const,
  details: () => [...taskKeys.all, "detail"] as const,
  detail: (userId: string, taskId: string) =>
    [...taskKeys.details(), userId, taskId] as const,
};

// ============================================================================
// Query Hooks
// ============================================================================

/**
 * Hook to fetch all tasks for a user.
 *
 * @param userId - User ID
 * @param filter - Optional filter: "all", "pending", or "completed"
 * @returns React Query result with tasks array
 *
 * @example
 * const { data: tasks, isLoading, error } = useTasks(user.id, 'pending');
 */
export function useTasks(userId: string, filter?: TaskStatus) {
  return useQuery({
    queryKey: taskKeys.list(userId, filter),
    queryFn: () => api.getTasks(userId, filter),
    enabled: !!userId, // Only run if userId exists
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook to fetch a single task by ID.
 *
 * @param userId - User ID
 * @param taskId - Task ID
 * @returns React Query result with task object
 *
 * @example
 * const { data: task, isLoading } = useTask(user.id, taskId);
 */
export function useTask(userId: string, taskId: string) {
  return useQuery({
    queryKey: taskKeys.detail(userId, taskId),
    queryFn: () => api.getTask(userId, taskId),
    enabled: !!userId && !!taskId, // Only run if both exist and taskId is valid
  });
}

// ============================================================================
// Mutation Hooks
// ============================================================================

/**
 * Hook to create a new task.
 *
 * Automatically invalidates task list cache on success.
 *
 * @param userId - User ID
 * @returns Mutation hook
 *
 * @example
 * const createTask = useCreateTask(user.id);
 * createTask.mutate({ title: 'New task', description: '...' });
 */
export function useCreateTask(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskCreate) => api.createTask(userId, data),
    onSuccess: () => {
      // Invalidate all task lists for this user
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}

/**
 * Hook to update an existing task.
 *
 * Automatically invalidates both the specific task and task lists on success.
 *
 * @param userId - User ID
 * @param taskId - Task ID
 * @returns Mutation hook
 *
 * @example
 * const updateTask = useUpdateTask(user.id, taskId);
 * updateTask.mutate({ title: 'Updated title' });
 */
export function useUpdateTask(userId: string, taskId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskUpdate) => api.updateTask(userId, taskId, data),
    onSuccess: () => {
      // Invalidate the specific task detail
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(userId, taskId) });
      // Invalidate all task lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}

/**
 * Hook to delete a task.
 *
 * Automatically invalidates task lists on success.
 *
 * @param userId - User ID
 * @returns Mutation hook
 *
 * @example
 * const deleteTask = useDeleteTask(user.id);
 * deleteTask.mutate(taskId);
 */
export function useDeleteTask(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => api.deleteTask(userId, taskId),
    onSuccess: () => {
      // Invalidate all task lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}

/**
 * Hook to toggle task completion status with optimistic updates.
 *
 * Provides instant UI feedback by updating the cache immediately,
 * then rolls back on error.
 *
 * @param userId - User ID
 * @param filter - Current filter (for cache key)
 * @returns Mutation hook
 *
 * @example
 * const toggleTask = useToggleTask(user.id, 'all');
 * toggleTask.mutate(taskId);
 */
export function useToggleTask(userId: string, filter?: TaskStatus) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => api.toggleTaskComplete(userId, taskId),

    // Optimistic update - run before API call
    onMutate: async (taskId) => {
      const queryKey = taskKeys.list(userId, filter);

      // Cancel any outgoing refetches (so they don't overwrite our optimistic update)
      await queryClient.cancelQueries({ queryKey });

      // Snapshot the previous value
      const previousTasks = queryClient.getQueryData<Task[]>(queryKey);

      // Optimistically update to the new value
      queryClient.setQueryData<Task[]>(queryKey, (old) =>
        old?.map((task) =>
          task.id === taskId
            ? { ...task, completed: !task.completed }
            : task
        )
      );

      // Return context with snapshot
      return { previousTasks, queryKey };
    },

    // On error, rollback to previous value
    onError: (_err, _taskId, context) => {
      if (context) {
        queryClient.setQueryData(context.queryKey, context.previousTasks);
      }
    },

    // Always refetch after error or success to ensure sync
    onSettled: (_data, _error, _taskId, context) => {
      if (context) {
        queryClient.invalidateQueries({ queryKey: context.queryKey });
      }
    },
  });
}
