"use client";

/**
 * Priority select component.
 *
 * Features:
 * - Dropdown for High/Medium/Low priority
 * - Color-coded options (red/yellow/blue)
 * - Label and optional error message
 * - Matches existing form styling
 */

import type { TaskPriority } from "@/lib/types";

export interface PrioritySelectProps {
  label?: string;
  value: TaskPriority;
  onChange: (value: TaskPriority) => void;
  error?: string;
}

const PRIORITY_OPTIONS: { value: TaskPriority; label: string; color: string }[] = [
  { value: "High", label: "🔴 High", color: "text-red-600" },
  { value: "Medium", label: "🟡 Medium", color: "text-yellow-600" },
  { value: "Low", label: "🔵 Low", color: "text-blue-600" },
];

export default function PrioritySelect({
  label = "Priority",
  value,
  onChange,
  error,
}: PrioritySelectProps) {
  return (
    <div className="mb-4">
      {/* Label */}
      <label className="block text-gray-700 text-sm font-bold mb-2">
        {label}
      </label>

      {/* Select */}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as TaskPriority)}
        className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
          error ? "border-red-500" : ""
        }`}
      >
        {PRIORITY_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      {/* Error Message */}
      {error && (
        <p className="text-red-500 text-xs italic mt-1">{error}</p>
      )}
    </div>
  );
}
