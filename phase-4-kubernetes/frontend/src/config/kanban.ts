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
