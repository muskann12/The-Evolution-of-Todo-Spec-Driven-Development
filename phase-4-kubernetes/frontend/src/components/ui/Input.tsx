"use client";

/**
 * Reusable Input component with label, error states, and helper text.
 *
 * Matches the styling from LoginForm.tsx:
 * - Label with consistent styling
 * - Input with focus states
 * - Error states with red border
 * - Helper text below input
 */

import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export default function Input({
  label,
  error,
  helperText,
  className,
  id,
  ...props
}: InputProps) {
  // Generate a unique ID if not provided
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="mb-4">
      {/* Label */}
      {label && (
        <label
          htmlFor={inputId}
          className="block text-gray-700 text-sm font-semibold mb-2"
        >
          {label}
        </label>
      )}

      {/* Input */}
      <input
        id={inputId}
        className={cn(
          "w-full px-4 py-3 rounded-lg border-2 border-gray-200",
          "focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200",
          "disabled:bg-gray-100 disabled:cursor-not-allowed transition-all",
          error && "border-red-500 focus:border-red-500 focus:ring-red-200",
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
