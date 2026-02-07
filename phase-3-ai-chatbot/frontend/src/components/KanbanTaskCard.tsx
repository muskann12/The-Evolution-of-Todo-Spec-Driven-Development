"use client";

import { Draggable } from "@hello-pangea/dnd";
import { MessageSquare, Calendar, MoreVertical, Edit, Trash2 } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import type { Task } from "@/lib/types";
import { useState } from "react";

interface KanbanTaskCardProps {
  task: Task;
  index: number;
  onEdit: (taskId: string) => void;
  onDelete: (taskId: string) => void;
}

const PRIORITY_COLORS = {
  High: "bg-red-50 text-red-700 border-red-200",
  Medium: "bg-purple-50 text-purple-700 border-purple-200",
  Low: "bg-blue-50 text-blue-700 border-blue-200",
};

export default function KanbanTaskCard({
  task,
  index,
  onEdit,
  onDelete,
}: KanbanTaskCardProps) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <Draggable draggableId={task.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`bg-white/90 backdrop-blur-sm p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-lg hover:border-purple-200 transition-all cursor-grab active:cursor-grabbing ${
            snapshot.isDragging ? "shadow-2xl rotate-2 ring-2 ring-purple-500 scale-105" : ""
          }`}
        >
          {/* Header: Tag + Menu */}
          <div className="flex items-start justify-between mb-3">
            <span
              className={`px-3 py-1 text-xs font-semibold rounded-full border ${
                PRIORITY_COLORS[task.priority]
              }`}
            >
              {task.priority}
            </span>
            <div className="relative">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(!showMenu);
                }}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <MoreVertical className="h-4 w-4 text-gray-500" />
              </button>
              {showMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowMenu(false)}
                  />
                  <div className="absolute right-0 mt-1 w-32 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onEdit(task.id);
                        setShowMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2 rounded-t-lg"
                    >
                      <Edit className="h-4 w-4" />
                      Edit
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(task.id);
                        setShowMenu(false);
                      }}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 text-red-600 flex items-center gap-2 rounded-b-lg"
                    >
                      <Trash2 className="h-4 w-4" />
                      Delete
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Task Title */}
          <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
            {task.title}
          </h3>

          {/* Task Description */}
          {task.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {task.description}
            </p>
          )}

          {/* Tags */}
          {task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {task.tags.slice(0, 3).map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 text-xs bg-purple-50 text-purple-700 rounded"
                >
                  {tag}
                </span>
              ))}
              {task.tags.length > 3 && (
                <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                  +{task.tags.length - 3}
                </span>
              )}
            </div>
          )}

          {/* Footer: Date, Comments, Avatar */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>{formatRelativeTime(task.created_at)}</span>
              </div>
              <div className="flex items-center gap-1">
                <MessageSquare className="h-3 w-3" />
                <span>0</span>
              </div>
            </div>

            {/* User Avatar Placeholder */}
            <div className="w-7 h-7 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full flex items-center justify-center text-white text-xs font-semibold">
              {task.user_id.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>
      )}
    </Draggable>
  );
}
