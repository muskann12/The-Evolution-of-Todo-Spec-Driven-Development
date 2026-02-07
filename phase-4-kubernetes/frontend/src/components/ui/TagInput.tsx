"use client";

/**
 * Tag input component.
 *
 * Features:
 * - Add tags by typing and pressing Enter or comma
 * - Display tags as removable pills/badges
 * - Validation (1-20 chars, letters/numbers/hyphens/underscores)
 * - Duplicate prevention
 * - Label and error message
 */

import { useState, KeyboardEvent } from "react";

export interface TagInputProps {
  label?: string;
  value: string[];
  onChange: (tags: string[]) => void;
  error?: string;
  placeholder?: string;
}

export default function TagInput({
  label = "Tags",
  value,
  onChange,
  error,
  placeholder = "Type a tag and press Enter",
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [inputError, setInputError] = useState("");

  // Add tag
  function addTag(tag: string) {
    tag = tag.trim().toLowerCase();

    // Skip empty
    if (!tag) return;

    // Check if already exists
    if (value.includes(tag)) {
      setInputError("Tag already added");
      return;
    }

    // Validate length
    if (tag.length > 20) {
      setInputError("Tag must be 1-20 characters");
      return;
    }

    // Validate format (letters, numbers, hyphens, underscores)
    if (!/^[a-z0-9_-]+$/.test(tag)) {
      setInputError("Tags can only contain letters, numbers, hyphens, and underscores");
      return;
    }

    // Add tag
    onChange([...value, tag]);
    setInputValue("");
    setInputError("");
  }

  // Remove tag
  function removeTag(tagToRemove: string) {
    onChange(value.filter((tag) => tag !== tagToRemove));
  }

  // Handle key press
  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
      // Remove last tag on backspace if input is empty
      removeTag(value[value.length - 1]);
    }
  }

  return (
    <div className="mb-4">
      {/* Label */}
      <label className="block text-gray-700 text-sm font-bold mb-2">
        {label}
      </label>

      {/* Tag Pills */}
      {value.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {value.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
            >
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="text-blue-600 hover:text-blue-800 font-bold"
                aria-label={`Remove ${tag}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Input */}
      <input
        type="text"
        value={inputValue}
        onChange={(e) => {
          setInputValue(e.target.value);
          setInputError("");
        }}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
          error || inputError ? "border-red-500" : ""
        }`}
      />

      {/* Error Message */}
      {(error || inputError) && (
        <p className="text-red-500 text-xs italic mt-1">{error || inputError}</p>
      )}

      {/* Helper Text */}
      <p className="text-gray-500 text-xs mt-1">
        Press Enter or comma to add a tag. Click × to remove.
      </p>
    </div>
  );
}
