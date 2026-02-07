"use client";

import { Search, Plus, ArrowUpDown } from "lucide-react";
import { getUser } from "@/lib/auth";
import { useState, useEffect } from "react";
import Link from "next/link";
import type { User, SortOption } from "@/lib/types";
import CreateTaskModal from "@/components/CreateTaskModal";
import UserProfileDropdown from "@/components/UserProfileDropdown";
import NotificationsDropdown from "@/components/NotificationsDropdown";

interface KanbanNavbarProps {
  sortBy?: SortOption;
  onSortChange?: (sort: SortOption) => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
}

export default function KanbanNavbar({
  sortBy = "newest",
  onSortChange,
  searchQuery = "",
  onSearchChange
}: KanbanNavbarProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    async function loadUser() {
      const currentUser = await getUser();
      setUser(currentUser);
    }
    loadUser();
  }, []);

  return (
    <nav className="bg-white/90 backdrop-blur-lg border-b border-purple-100 px-6 py-2.5 shadow-sm relative z-50">
      <div className="flex items-center justify-between">
        {/* Left: Logo/Title and New Task */}
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent hover:opacity-80 transition-opacity cursor-pointer"
          >
            Task Manager
          </Link>
          {/* New Task Button */}
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-sm rounded-lg hover:from-purple-700 hover:to-blue-700 transition shadow-lg hover:shadow-xl"
          >
            <Plus size={16} />
            <span>New Task</span>
          </button>
        </div>

        {/* Center: Spacer */}
        <div className="flex-1"></div>

        {/* Right: Search, Sort, Notifications, User Profile */}
        <div className="flex items-center gap-3">
          {/* Search Bar - Smaller */}
          <div className="relative w-48">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => onSearchChange?.(e.target.value)}
              className="w-full h-[38px] pl-9 pr-3 text-sm border border-gray-400 rounded-lg hover:border-purple-500 focus:outline-none focus:border-purple-500 transition-colors"
            />
            {searchQuery && (
              <button
                onClick={() => onSearchChange?.("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                title="Clear search"
              >
                ✕
              </button>
            )}
          </div>

          {/* Sort Dropdown - Larger (Double Size) */}
          {onSortChange && (
            <div className="flex items-center gap-2 bg-white border border-gray-400 rounded-lg px-4 h-[38px] hover:border-purple-500 transition-colors min-w-[200px]">
              <ArrowUpDown className="h-4 w-4 text-gray-500 flex-shrink-0" />
              <select
                value={sortBy}
                onChange={(e) => onSortChange(e.target.value as SortOption)}
                className="text-sm text-gray-700 font-medium bg-transparent border-none outline-none cursor-pointer w-full h-full"
              >
                <option value="newest">🆕 Newest First</option>
                <option value="oldest">📅 Oldest First</option>
                <option value="priority-high">🔴 High Priority</option>
                <option value="priority-low">🔵 Low Priority</option>
                <option value="title-asc">🔤 Title A-Z</option>
                <option value="title-desc">🔡 Title Z-A</option>
                <option value="completed">✅ Completed First</option>
                <option value="pending">⏳ Pending First</option>
              </select>
            </div>
          )}

          {/* Notifications Dropdown */}
          <NotificationsDropdown />

          {/* User Profile Dropdown */}
          {user && <UserProfileDropdown user={user} />}
        </div>
      </div>

      {/* Create Task Modal */}
      {user && (
        <CreateTaskModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          userId={user.id}
        />
      )}
    </nav>
  );
}
