"use client";

/**
 * Delete confirmation modal component.
 *
 * Shows a warning dialog before deleting a task:
 * - Warning message
 * - Cancel button (secondary)
 * - Delete button (destructive)
 * - Loading state during deletion
 */

import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";

export interface DeleteConfirmationProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isDeleting: boolean;
}

export default function DeleteConfirmation({
  isOpen,
  onClose,
  onConfirm,
  isDeleting,
}: DeleteConfirmationProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Delete Task">
      {/* Warning Message */}
      <p className="text-gray-600 mb-6">
        Are you sure you want to delete this task? This action cannot be
        undone.
      </p>

      {/* Action Buttons */}
      <div className="flex gap-3 justify-end">
        <Button variant="outline" onClick={onClose} disabled={isDeleting}>
          Cancel
        </Button>
        <Button
          variant="destructive"
          onClick={onConfirm}
          isLoading={isDeleting}
        >
          {isDeleting ? "Deleting..." : "Delete"}
        </Button>
      </div>
    </Modal>
  );
}
