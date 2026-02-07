"use client";

/**
 * User Profile Dropdown Component
 *
 * Displays a dropdown menu when user clicks on their avatar/profile.
 *
 * Menu Options:
 * - Edit Profile (navigate to /profile)
 * - Switch Account (logout and redirect to login)
 * - Logout (sign out)
 */

import { useState, useRef, useEffect } from "react";
import { User, Users, LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/auth";

interface UserProfileDropdownProps {
  user: {
    name: string;
    email: string;
    id: string;
  };
}

export default function UserProfileDropdown({ user }: UserProfileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  function handleEditProfile() {
    setIsOpen(false);
    router.push("/profile");
  }

  function handleSwitchAccount() {
    setIsOpen(false);
    logout();
    router.push("/login");
  }

  function handleLogout() {
    setIsOpen(false);
    logout();
    router.push("/login");
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Avatar Button - Only Avatar, No Text */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative pl-4 border-l border-purple-200 hover:bg-purple-50 transition-colors rounded-r-lg p-2"
      >
        {/* User Avatar */}
        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold shadow-md hover:shadow-lg transition-shadow cursor-pointer">
          {user.name?.charAt(0).toUpperCase() || "U"}
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white/95 backdrop-blur-lg rounded-lg shadow-xl border border-purple-200 py-2 z-[100] animate-in fade-in slide-in-from-top-2 duration-200">
          {/* User Info Section */}
          <div className="px-4 py-3 border-b border-purple-200">
            <div className="flex items-center gap-3">
              {/* Avatar in Dropdown */}
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {user.name?.charAt(0).toUpperCase() || "U"}
              </div>
              {/* User Details */}
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 truncate">
                  {user.name || "User"}
                </p>
                <p className="text-gray-500 text-sm truncate">
                  {user.email || ""}
                </p>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          {/* Edit Profile */}
          <button
            onClick={handleEditProfile}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700 transition-colors"
          >
            <User className="h-4 w-4 text-purple-500" />
            <span className="font-medium">Edit Profile</span>
          </button>

          {/* Switch Account */}
          <button
            onClick={handleSwitchAccount}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700 transition-colors"
          >
            <Users className="h-4 w-4 text-purple-500" />
            <span className="font-medium">Switch Account</span>
          </button>

          {/* Divider */}
          <div className="border-t border-purple-200 my-2"></div>

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      )}
    </div>
  );
}
