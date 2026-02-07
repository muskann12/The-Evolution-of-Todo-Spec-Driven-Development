"use client";

/**
 * Recurrence select component.
 *
 * Features:
 * - Dropdown for None/Daily/Weekly/Monthly
 * - Interval input (every X days/weeks/months)
 * - Visual icons for patterns
 * - Label and optional error message
 */

import type { RecurrencePattern } from "@/lib/types";

export interface RecurrenceSelectProps {
  label?: string;
  pattern: RecurrencePattern;
  interval: number;
  onPatternChange: (pattern: RecurrencePattern) => void;
  onIntervalChange: (interval: number) => void;
  error?: string;
}

const PATTERN_OPTIONS: { value: RecurrencePattern; label: string; icon: string }[] = [
  { value: null, label: "None", icon: "" },
  { value: "Daily", label: "Daily", icon: "🔁D" },
  { value: "Weekly", label: "Weekly", icon: "🔁W" },
  { value: "Monthly", label: "Monthly", icon: "🔁M" },
];

export default function RecurrenceSelect({
  label = "Recurrence",
  pattern,
  interval,
  onPatternChange,
  onIntervalChange,
  error,
}: RecurrenceSelectProps) {
  return (
    <div className="mb-4">
      {/* Label */}
      <label className="block text-gray-700 text-sm font-bold mb-2">
        {label}
      </label>

      <div className="flex gap-2">
        {/* Pattern Select */}
        <select
          value={pattern || "None"}
          onChange={(e) => {
            const value = e.target.value === "None" ? null : (e.target.value as RecurrencePattern);
            onPatternChange(value);
          }}
          className={`shadow appearance-none border rounded flex-1 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
            error ? "border-red-500" : ""
          }`}
        >
          {PATTERN_OPTIONS.map((option) => (
            <option key={option.label} value={option.value || "None"}>
              {option.icon && `${option.icon} `}{option.label}
            </option>
          ))}
        </select>

        {/* Interval Input (only show if pattern is selected) */}
        {pattern && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Every</span>
            <input
              type="number"
              min="1"
              max="365"
              value={interval}
              onChange={(e) => onIntervalChange(Math.max(1, Math.min(365, parseInt(e.target.value) || 1)))}
              className="shadow appearance-none border rounded w-20 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
            <span className="text-sm text-gray-600">
              {pattern === "Daily" && (interval === 1 ? "day" : "days")}
              {pattern === "Weekly" && (interval === 1 ? "week" : "weeks")}
              {pattern === "Monthly" && (interval === 1 ? "month" : "months")}
            </span>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <p className="text-red-500 text-xs italic mt-1">{error}</p>
      )}

      {/* Helper Text */}
      {pattern && (
        <p className="text-gray-500 text-xs mt-1">
          When completed, a new task will be created automatically.
        </p>
      )}
    </div>
  );
}
