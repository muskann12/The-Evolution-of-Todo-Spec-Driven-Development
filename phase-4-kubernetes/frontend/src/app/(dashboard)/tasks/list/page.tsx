"use client";

/**
 * Task list page - List View (Classic).
 *
 * Features:
 * - Page title "My Tasks"
 * - Filter tabs (All/Pending/Completed)
 * - Search input (filter by title/description)
 * - Sort dropdown (8 different sort options)
 * - TaskList component with current filter, search, and sort
 * - Classic list layout with Header navigation
 */

import { useState } from "react";
import Header from "@/components/Header";
import TaskList from "@/components/TaskList";
import Input from "@/components/ui/Input";
import SortSelect from "@/components/ui/SortSelect";
import type { TaskStatus, SortOption } from "@/lib/types";

export default function TaskListPage() {
  const [filter, setFilter] = useState<TaskStatus>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [sortBy, setSortBy] = useState<SortOption>("newest");

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 relative overflow-hidden">
      {/* Subtle animated gradient orbs in background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow animation-delay-400"></div>
        <div className="absolute top-1/2 right-1/4 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow animation-delay-200"></div>
      </div>

      {/* Content wrapper with relative positioning */}
      <div className="relative z-10">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div>
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-4">My Tasks</h1>

        {/* Filter Tabs */}
        <div className="flex gap-2 border-b border-purple-200 bg-white/60 backdrop-blur-sm rounded-t-lg px-2 pt-2">
          <button
            onClick={() => setFilter("all")}
            className={`px-4 py-2 font-semibold transition-all rounded-t-lg ${
              filter === "all"
                ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md"
                : "text-gray-600 hover:text-purple-600 hover:bg-purple-50"
            }`}
          >
            All Tasks
          </button>
          <button
            onClick={() => setFilter("pending")}
            className={`px-4 py-2 font-semibold transition-all rounded-t-lg ${
              filter === "pending"
                ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md"
                : "text-gray-600 hover:text-purple-600 hover:bg-purple-50"
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter("completed")}
            className={`px-4 py-2 font-semibold transition-all rounded-t-lg ${
              filter === "completed"
                ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md"
                : "text-gray-600 hover:text-purple-600 hover:bg-purple-50"
            }`}
          >
            Completed
          </button>
        </div>
      </div>

      {/* Search and Sort Controls */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-end bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-sm border border-purple-100">
        {/* Search Input */}
        <div className="flex-1 w-full">
          <Input
            label="Search Tasks"
            placeholder="Search by title or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            type="text"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="mt-1 text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent hover:from-purple-700 hover:to-blue-700 transition-all"
            >
              Clear search
            </button>
          )}
        </div>

        {/* Sort Dropdown */}
        <div className="w-full sm:w-auto">
          <SortSelect value={sortBy} onChange={setSortBy} />
        </div>
      </div>

      {/* Task List */}
      <TaskList filter={filter} searchQuery={searchQuery} sortBy={sortBy} />
          </div>
        </main>
      </div>
    </div>
  );
}
