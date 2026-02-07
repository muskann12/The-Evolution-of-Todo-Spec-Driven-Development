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
    <div className="flex-shrink-0 w-64">
      {/* Column Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className={`font-semibold ${column.color}`}>{column.title}</h2>
          <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full">
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
            className={`min-h-[500px] p-3 rounded-lg transition-all ${
              snapshot.isDraggingOver
                ? "bg-purple-50 ring-2 ring-purple-400"
                : "bg-white/60 backdrop-blur-sm border border-gray-100"
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

            {/* Empty state */}
            {tasks.length === 0 && !snapshot.isDraggingOver && (
              <div className="flex flex-col items-center justify-center h-32 text-gray-400">
                <p className="text-sm">No tasks</p>
                <p className="text-xs mt-1">Drag tasks here</p>
              </div>
            )}
          </div>
        )}
      </Droppable>
    </div>
  );
}
