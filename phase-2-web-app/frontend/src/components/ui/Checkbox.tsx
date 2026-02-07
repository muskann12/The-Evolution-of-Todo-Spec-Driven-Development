"use client";

/**
 * Reusable Checkbox component.
 *
 * Client Component for interactive checkbox behavior:
 * - Blue accent when checked
 * - Proper accessibility labels
 * - Keyboard navigation support
 * - Disabled state
 */

import { cn } from "@/lib/utils";

export interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  className?: string;
  id?: string;
}

export default function Checkbox({
  checked,
  onChange,
  label,
  disabled = false,
  className,
  id,
}: CheckboxProps) {
  // Generate a unique ID if not provided
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className={cn("flex items-center", className)}>
      <input
        type="checkbox"
        id={checkboxId}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className={cn(
          "w-5 h-5 text-blue-600 rounded border-gray-300",
          "focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        )}
      />
      {label && (
        <label
          htmlFor={checkboxId}
          className={cn(
            "ml-2 text-gray-700 cursor-pointer",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          {label}
        </label>
      )}
    </div>
  );
}
