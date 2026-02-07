"use client";

/**
 * Modal component for creating new tasks.
 *
 * Wraps the TaskForm component in a Modal dialog for in-place task creation
 * without navigating to a new page.
 */

import Modal from "@/components/ui/Modal";
import TaskForm from "@/components/TaskForm";
import { useCreateTask } from "@/hooks/useTasks";
import type { TaskCreate, TaskUpdate } from "@/lib/types";

interface CreateTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
}

export default function CreateTaskModal({
  isOpen,
  onClose,
  userId,
}: CreateTaskModalProps) {
  const createMutation = useCreateTask(userId);

  function handleSubmit(data: TaskCreate | TaskUpdate) {
    createMutation.mutate(data as TaskCreate, {
      onSuccess: () => {
        onClose(); // Close modal on success
        // React Query will auto-invalidate and refresh tasks
      },
      // Errors handled by mutation internally
    });
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Task"
      size="lg"
    >
      <div className="max-h-[70vh] overflow-y-auto px-1">
        <TaskForm
          onSubmit={handleSubmit}
          onCancel={onClose}
          isSubmitting={createMutation.isPending}
          isModal={true}
        />
      </div>
    </Modal>
  );
}
