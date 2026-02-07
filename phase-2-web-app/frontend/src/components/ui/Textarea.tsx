"use client";

/**
 * Reusable Textarea component for multi-line text input.
 *
 * Same pattern as Input component but for text areas:
 * - Label with consistent styling
 * - Textarea with focus states
 * - Error states with red border
 * - Helper text below textarea
 * - Resizable vertically
 */

import { cn } from "@/lib/utils";

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export default function Textarea({
  label,
  error,
  helperText,
  className,
  id,
  ...props
}: TextareaProps) {
  // Generate a unique ID if not provided
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="mb-4">
      {/* Label */}
      {label && (
        <label
          htmlFor={textareaId}
          className="block text-gray-700 text-sm font-bold mb-2"
        >
          {label}
        </label>
      )}

      {/* Textarea */}
      <textarea
        id={textareaId}
        className={cn(
          "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight",
          "focus:outline-none focus:ring-2 focus:ring-blue-500",
          "disabled:bg-gray-100 disabled:cursor-not-allowed",
          "min-h-[100px] resize-y",
          error && "border-red-500",
          className
        )}
        {...props}
      />

      {/* Error Message */}
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}

      {/* Helper Text */}
      {helperText && !error && (
        <p className="mt-1 text-sm text-gray-600">{helperText}</p>
      )}
    </div>
  );
}
