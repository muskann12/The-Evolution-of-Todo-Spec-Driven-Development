"use client";

/**
 * Reusable form component for creating and editing tasks.
 *
 * Features:
 * - Works for both create and edit modes
 * - Client-side validation
 * - Character counters
 * - Loading states
 * - Error messages
 * - Cancel and submit buttons
 */

import { useState, FormEvent, useRef, useEffect } from "react";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import PrioritySelect from "@/components/ui/PrioritySelect";
import TagInput from "@/components/ui/TagInput";
import RecurrenceSelect from "@/components/ui/RecurrenceSelect";
import DateTimePicker from "@/components/ui/DateTimePicker";
import type { Task, TaskCreate, TaskUpdate, TaskPriority, RecurrencePattern } from "@/lib/types";

export interface TaskFormProps {
  initialData?: Task;
  onSubmit: (data: TaskCreate | TaskUpdate) => void;
  onCancel: () => void;
  isSubmitting: boolean;
  isModal?: boolean;
}

export default function TaskForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting,
  isModal = false,
}: TaskFormProps) {
  // Form state
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(
    initialData?.description || ""
  );
  const [priority, setPriority] = useState<TaskPriority>(
    initialData?.priority || "Low"
  );
  const [tags, setTags] = useState<string[]>(initialData?.tags || []);
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePattern>(
    initialData?.recurrence_pattern || null
  );
  const [recurrenceInterval, setRecurrenceInterval] = useState<number>(
    initialData?.recurrence_interval || 1
  );
  const [dueDate, setDueDate] = useState<string | null>(
    initialData?.due_date || null
  );
  const [errors, setErrors] = useState<Record<string, string>>({});
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea in modal mode
  useEffect(() => {
    if (isModal && textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.max(textarea.scrollHeight, 60)}px`;
    }
  }, [description, isModal]);

  // Validation
  function validate(): boolean {
    const newErrors: Record<string, string> = {};

    // Title validation
    if (!title.trim()) {
      newErrors.title = "Title is required";
    } else if (title.length > 200) {
      newErrors.title = "Title must be 200 characters or less";
    }

    // Description validation
    if (description && description.length > 1000) {
      newErrors.description = "Description must be 1000 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  // Submit handler
  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (!validate()) return;

    const data = {
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      tags,
      recurrence_pattern: recurrencePattern,
      recurrence_interval: recurrenceInterval,
      due_date: dueDate,
    };

    onSubmit(data);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={isModal ? "space-y-4" : "bg-white/90 backdrop-blur-lg shadow-2xl rounded-2xl px-8 pt-8 pb-8 border border-purple-100"}
    >
      {/* Form Title - hide in modal mode */}
      {!isModal && (
        <h2 className="text-3xl font-bold gradient-text mb-6">
          {initialData ? "Edit Task" : "Create New Task"}
        </h2>
      )}

      {/* Title Input */}
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={errors.title}
        placeholder="Enter task title"
        disabled={isSubmitting}
        required
        maxLength={200}
      />

      {/* Description Textarea */}
      <div className="mb-4">
        <label
          htmlFor="task-description"
          className="block text-gray-700 text-sm font-semibold mb-2"
        >
          Description (Optional)
        </label>
        <textarea
          ref={textareaRef}
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details about this task..."
          disabled={isSubmitting}
          maxLength={1000}
          rows={isModal ? 2 : 4}
          className={`w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none disabled:bg-gray-100 disabled:cursor-not-allowed ${isModal ? 'resize-none overflow-hidden' : 'min-h-[100px] resize-y'} ${errors.description ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}`}
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description}</p>
        )}
        {!errors.description && (
          <p className="mt-1 text-sm text-gray-600">
            {description.length}/1000 characters
          </p>
        )}
      </div>

      {/* Priority Select */}
      <PrioritySelect
        value={priority}
        onChange={setPriority}
        error={errors.priority}
      />

      {/* Tag Input */}
      <TagInput
        value={tags}
        onChange={setTags}
        error={errors.tags}
      />

      {/* Recurrence Select */}
      <RecurrenceSelect
        pattern={recurrencePattern}
        interval={recurrenceInterval}
        onPatternChange={setRecurrencePattern}
        onIntervalChange={setRecurrenceInterval}
        error={errors.recurrence}
      />

      {/* Due Date Picker */}
      <DateTimePicker
        value={dueDate}
        onChange={setDueDate}
        label="Due Date & Time"
        error={errors.due_date}
      />

      {/* Action Buttons */}
      <div className={`flex gap-3 justify-end ${isModal ? 'mt-4 pt-4 border-t border-purple-200' : 'mt-6'}`}>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button type="submit" variant="primary" isLoading={isSubmitting}>
          {initialData ? "Update Task" : "Create Task"}
        </Button>
      </div>
    </form>
  );
}
