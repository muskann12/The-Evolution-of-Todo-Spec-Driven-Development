"use client";

/**
 * Sort select component for task list.
 *
 * Features:
 * - Dropdown with all sort options
 * - Icon prefix for visual clarity
 * - Matches existing form component styling
 * - Descriptive labels for each option
 */

import type { SortOption } from "@/lib/types";

export interface SortSelectProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
  className?: string;
}

const SORT_OPTIONS: { value: SortOption; label: string; icon: string }[] = [
  { value: "newest", label: "Newest First", icon: "🆕" },
  { value: "oldest", label: "Oldest First", icon: "📅" },
  { value: "priority-high", label: "Priority (High to Low)", icon: "🔴" },
  { value: "priority-low", label: "Priority (Low to High)", icon: "🔵" },
  { value: "title-asc", label: "Title (A-Z)", icon: "🔤" },
  { value: "title-desc", label: "Title (Z-A)", icon: "🔡" },
  { value: "completed", label: "Completed First", icon: "✅" },
  { value: "pending", label: "Pending First", icon: "⏳" },
];

export default function SortSelect({
  value,
  onChange,
  className = "",
}: SortSelectProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Label */}
      <label className="text-sm font-medium text-gray-700 whitespace-nowrap">
        Sort by:
      </label>

      {/* Select Dropdown */}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as SortOption)}
        className="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
      >
        {SORT_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.icon} {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
