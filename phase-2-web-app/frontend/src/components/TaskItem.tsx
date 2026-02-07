"use client";

/**
 * Individual task card component.
 *
 * Features:
 * - Checkbox for completion toggle
 * - Task title and description
 * - Created/updated timestamps
 * - Edit and Delete buttons
 * - Visual feedback for completed tasks (line-through, gray)
 * - Hover effects
 */

import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Checkbox from "@/components/ui/Checkbox";
import Button from "@/components/ui/Button";
import { formatDate, cn } from "@/lib/utils";
import type { Task } from "@/lib/types";

/**
 * Check if a task is overdue.
 */
function isOverdue(dueDate: string | null, completed: boolean): boolean {
  if (!dueDate || completed) return false;
  return new Date(dueDate) < new Date();
}

/**
 * Format due date for display.
 */
function formatDueDate(dueDate: string | null): string {
  if (!dueDate) return "";

  const date = new Date(dueDate);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  // If overdue
  if (diffMs < 0) {
    const absDays = Math.abs(diffDays);
    if (absDays === 0) return "Overdue (today)";
    if (absDays === 1) return "Overdue (1 day ago)";
    return `Overdue (${absDays} days ago)`;
  }

  // If due soon
  if (diffDays === 0) {
    if (diffHours <= 1) return "Due in less than 1 hour";
    return `Due in ${diffHours} hours`;
  }
  if (diffDays === 1) return "Due tomorrow";
  if (diffDays < 7) return `Due in ${diffDays} days`;

  // Otherwise show formatted date
  return `Due ${date.toLocaleDateString()} ${date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  })}`;
}

export interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: string) => void;
  onDelete: (taskId: string) => void;
}

export default function TaskItem({
  task,
  onToggleComplete,
  onDelete,
}: TaskItemProps) {
  const router = useRouter();
  const taskOverdue = isOverdue(task.due_date, task.completed);
  const dueDateText = formatDueDate(task.due_date);

  return (
    <Card className="bg-white/90 backdrop-blur-sm hover:shadow-lg hover:border-purple-200 transition-all duration-200" padding="sm">
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <div className="pt-1">
          <Checkbox
            checked={task.completed}
            onChange={() => onToggleComplete(task.id)}
            id={`task-${task.id}`}
          />
        </div>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3
            className={cn(
              "text-lg font-semibold break-words",
              task.completed && "line-through text-gray-500"
            )}
          >
            {task.title}
          </h3>

          {/* Description */}
          {task.description && (
            <p
              className={cn(
                "mt-1 text-gray-600 break-words",
                task.completed && "text-gray-400"
              )}
            >
              {task.description}
            </p>
          )}

          {/* Priority, Recurrence, and Tags */}
          <div className="flex flex-wrap items-center gap-2 mt-2">
            {/* Priority Badge */}
            <span
              className={cn(
                "inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold border",
                task.priority === "High" && "bg-red-50 text-red-700 border-red-200",
                task.priority === "Medium" && "bg-purple-50 text-purple-700 border-purple-200",
                task.priority === "Low" && "bg-blue-50 text-blue-700 border-blue-200"
              )}
            >
              {task.priority === "High" && "🔴"}
              {task.priority === "Medium" && "🟡"}
              {task.priority === "Low" && "🔵"}
              {" "}
              {task.priority}
            </span>

            {/* Recurrence Indicator */}
            {task.recurrence_pattern && (
              <span
                className="inline-flex items-center px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-semibold"
                title={`Repeats every ${task.recurrence_interval} ${task.recurrence_pattern.toLowerCase()}${task.recurrence_interval > 1 ? 's' : ''}`}
              >
                {task.recurrence_pattern === "Daily" && "🔁D"}
                {task.recurrence_pattern === "Weekly" && "🔁W"}
                {task.recurrence_pattern === "Monthly" && "🔁M"}
                {task.recurrence_interval > 1 && ` ×${task.recurrence_interval}`}
              </span>
            )}

            {/* Tag Badges */}
            {task.tags && task.tags.length > 0 && task.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
              >
                {tag}
              </span>
            ))}

            {/* Due Date Badge */}
            {task.due_date && (
              <span
                className={cn(
                  "inline-flex items-center px-2 py-1 rounded text-xs font-semibold",
                  taskOverdue
                    ? "bg-red-100 text-red-800"
                    : "bg-green-100 text-green-800"
                )}
                title={task.due_date}
              >
                {taskOverdue ? "⚠️" : "📅"} {dueDateText}
              </span>
            )}
          </div>

          {/* Timestamps */}
          <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-500">
            <span>Created: {formatDate(task.created_at)}</span>
            {task.updated_at !== task.created_at && (
              <span>Updated: {formatDate(task.updated_at)}</span>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 flex-shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push(`/tasks/${task.id}`)}
          >
            Edit
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => onDelete(task.id)}
          >
            Delete
          </Button>
        </div>
      </div>
    </Card>
  );
}
