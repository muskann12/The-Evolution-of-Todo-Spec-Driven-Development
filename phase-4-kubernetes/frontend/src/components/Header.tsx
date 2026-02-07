"use client";

/**
 * Header component for dashboard navigation.
 *
 * Features:
 * - App logo/title
 * - "New Task" button
 * - User name display
 * - Logout button
 * - Responsive design
 */

import { useState, useEffect } from "react";
import Link from "next/link";
import Button from "@/components/ui/Button";
import CreateTaskModal from "@/components/CreateTaskModal";
import UserProfileDropdown from "@/components/UserProfileDropdown";
import { getUser } from "@/lib/auth";
import type { User } from "@/lib/types";

export default function Header() {
  const [user, setUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Load user on mount
  useEffect(() => {
    async function loadUser() {
      const currentUser = await getUser();
      setUser(currentUser);
    }
    loadUser();
  }, []);

  return (
    <header className="bg-white/90 backdrop-blur-lg shadow-lg border-b border-purple-100 sticky top-0 z-50">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-11 flex justify-between items-center">
        {/* Left: Logo and Navigation */}
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="text-lg font-bold gradient-text hover:opacity-80 transition-opacity"
          >
            Todo App
          </Link>
          <Link href="/tasks/list">
            <Button variant="outline" size="sm" className="py-1 px-3 text-xs">
              List View
            </Button>
          </Link>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsModalOpen(true)}
            className="py-1 px-3 text-xs"
          >
            + New Task
          </Button>
        </div>

        {/* Right: User profile dropdown */}
        <div className="flex items-center gap-4">
          {user && <UserProfileDropdown user={user} />}
        </div>
      </nav>

      {/* Create Task Modal */}
      {user && (
        <CreateTaskModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          userId={user.id}
        />
      )}
    </header>
  );
}
