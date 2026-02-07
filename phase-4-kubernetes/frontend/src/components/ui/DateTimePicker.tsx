"use client";

/**
 * DateTimePicker component for selecting due date and time.
 *
 * Features:
 * - HTML5 datetime-local input
 * - Optional field with clear button
 * - Converts between ISO 8601 and local datetime format
 * - Visual calendar icon
 */

import { cn } from "@/lib/utils";

export interface DateTimePickerProps {
  value: string | null; // ISO 8601 datetime string or null
  onChange: (value: string | null) => void;
  label?: string;
  error?: string;
  className?: string;
}

/**
 * Convert ISO 8601 string to datetime-local format (YYYY-MM-DDTHH:MM)
 */
function isoToDateTimeLocal(iso: string | null): string {
  if (!iso) return "";

  try {
    const date = new Date(iso);
    // Format: YYYY-MM-DDTHH:MM
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    return `${year}-${month}-${day}T${hours}:${minutes}`;
  } catch {
    return "";
  }
}

/**
 * Convert datetime-local format (YYYY-MM-DDTHH:MM) to ISO 8601 string
 */
function dateTimeLocalToIso(dateTimeLocal: string): string | null {
  if (!dateTimeLocal) return null;

  try {
    const date = new Date(dateTimeLocal);
    return date.toISOString();
  } catch {
    return null;
  }
}

export default function DateTimePicker({
  value,
  onChange,
  label = "Due Date",
  error,
  className,
}: DateTimePickerProps) {
  const localValue = isoToDateTimeLocal(value);
  const hasValue = !!value;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    const isoValue = dateTimeLocalToIso(newValue);
    onChange(isoValue);
  };

  const handleClear = () => {
    onChange(null);
  };

  return (
    <div className={cn("space-y-2", className)}>
      {/* Label */}
      <label className="block text-sm font-semibold text-gray-700">
        📅 {label}
      </label>

      {/* Input Container */}
      <div className="relative">
        <input
          type="datetime-local"
          value={localValue}
          onChange={handleChange}
          className={cn(
            "w-full px-4 py-2 border rounded-lg",
            "focus:outline-none focus:ring-2 focus:ring-blue-500",
            error
              ? "border-red-500 focus:ring-red-500"
              : "border-gray-300",
            "text-gray-700"
          )}
        />

        {/* Clear Button */}
        {hasValue && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
            title="Clear due date"
          >
            ✕
          </button>
        )}
      </div>

      {/* Helper Text */}
      {!error && !hasValue && (
        <p className="text-xs text-gray-500">
          Optional: Set a deadline for this task
        </p>
      )}

      {/* Error Message */}
      {error && (
        <p className="text-xs text-red-600">{error}</p>
      )}
    </div>
  );
}
