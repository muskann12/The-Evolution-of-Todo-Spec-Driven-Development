"use client";

/**
 * Edit Profile Page
 *
 * Allows users to edit their profile information:
 * - Name
 * - Email
 * - Password (change password)
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getUser } from "@/lib/auth";
import { User as UserIcon, Lock, Camera } from "lucide-react";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import KanbanNavbar from "@/components/KanbanNavbar";
import type { User } from "@/lib/types";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState("");

  // Load user data on mount
  useEffect(() => {
    async function loadUser() {
      const currentUser = await getUser();
      if (currentUser) {
        setUser(currentUser);
        setName(currentUser.name || "");
        setEmail(currentUser.email || "");
      } else {
        router.push("/login");
      }
    }
    loadUser();
  }, [router]);

  // Validation
  function validate(): boolean {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Email is invalid";
    }

    // Password validation (if user wants to change password)
    if (newPassword || confirmPassword) {
      if (!currentPassword) {
        newErrors.currentPassword = "Current password is required to change password";
      }
      if (newPassword.length < 6) {
        newErrors.newPassword = "New password must be at least 6 characters";
      }
      if (newPassword !== confirmPassword) {
        newErrors.confirmPassword = "Passwords do not match";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  // Handle save
  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSuccessMessage("");

    if (!validate()) return;

    setIsLoading(true);

    try {
      // TODO: Implement API call to update user profile
      // For now, just show success message
      console.log("Updating profile:", { name, email });

      setSuccessMessage("Profile updated successfully!");

      // Clear password fields
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (error) {
      setErrors({ general: "Failed to update profile" });
    } finally {
      setIsLoading(false);
    }
  }

  if (!user) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 relative overflow-hidden">
      {/* Subtle animated gradient orbs in background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow animation-delay-400"></div>
        <div className="absolute top-1/2 right-1/4 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow animation-delay-200"></div>
      </div>

      {/* Content wrapper with relative positioning */}
      <div className="relative z-10 h-screen flex flex-col">
        <KanbanNavbar />

        <div className="flex-1 overflow-y-auto py-8 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Page Header with Avatar */}
          <div className="bg-white/90 backdrop-blur-lg rounded-2xl shadow-2xl p-8 mb-6 border border-purple-100">
            <div className="flex items-center gap-6">
              {/* Profile Avatar */}
              <div className="relative group">
                <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                  {user?.name?.charAt(0).toUpperCase() || "U"}
                </div>
                <button
                  type="button"
                  className="absolute bottom-0 right-0 bg-white rounded-full p-2 shadow-lg border-2 border-purple-500 hover:bg-purple-50 transition-colors"
                >
                  <Camera className="h-4 w-4 text-purple-600" />
                </button>
              </div>

              {/* Header Text */}
              <div className="flex-1">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Edit Profile
                </h1>
                <p className="text-gray-600 mt-1">
                  Manage your account settings and preferences
                </p>
              </div>
            </div>
          </div>

          {/* Success Message */}
          {successMessage && (
            <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 rounded-lg text-green-800 shadow-sm animate-in fade-in slide-in-from-top-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                {successMessage}
              </div>
            </div>
          )}

          {/* Error Message */}
          {errors.general && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg text-red-800 shadow-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                {errors.general}
              </div>
            </div>
          )}

          {/* Profile Form */}
          <form onSubmit={handleSave} className="space-y-6">
            {/* Personal Information Card */}
            <div className="bg-white/90 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-purple-100">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                  <UserIcon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    Personal Information
                  </h2>
                  <p className="text-sm text-gray-500">Update your basic details</p>
                </div>
              </div>

              <div className="space-y-4">
                <Input
                  label="Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  error={errors.name}
                  placeholder="Enter your name"
                  disabled={isLoading}
                  required
                />

                <Input
                  label="Email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={errors.email}
                  placeholder="Enter your email"
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            {/* Change Password Card */}
            <div className="bg-white/90 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-purple-100">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-orange-500 rounded-lg flex items-center justify-center">
                  <Lock className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    Change Password
                  </h2>
                  <p className="text-sm text-gray-500">Update your password to keep your account secure</p>
                </div>
              </div>

              <div className="bg-purple-50 border-l-4 border-purple-500 p-4 rounded-lg mb-6">
                <p className="text-sm text-purple-800">
                  💡 Leave password fields blank if you don't want to change your password
                </p>
              </div>

              <div className="space-y-4">
                <Input
                  label="Current Password"
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  error={errors.currentPassword}
                  placeholder="Enter current password"
                  disabled={isLoading}
                />

                <Input
                  label="New Password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  error={errors.newPassword}
                  placeholder="Enter new password (min. 6 characters)"
                  disabled={isLoading}
                />

                <Input
                  label="Confirm New Password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  error={errors.confirmPassword}
                  placeholder="Confirm new password"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 justify-end bg-white/90 backdrop-blur-lg rounded-2xl shadow-2xl p-6 border border-purple-100">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={isLoading}
                className="min-w-[120px]"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                isLoading={isLoading}
                className="min-w-[120px] bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              >
                Save Changes
              </Button>
            </div>
          </form>
          </div>
        </div>
      </div>
    </div>
  );
}
