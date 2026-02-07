"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Menu, X } from "lucide-react";
import { isAuthenticated } from "@/lib/auth";
import { useScrollPosition } from "@/hooks/useScrollPosition";
import Button from "@/components/ui/Button";

/**
 * Landing page navbar with backdrop blur on scroll and protected dashboard link.
 * Features mobile responsive design with hamburger menu.
 */
export default function LandingNavbar() {
  const router = useRouter();
  const scrolled = useScrollPosition();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleDashboardClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    const authenticated = await isAuthenticated();
    router.push(authenticated ? "/tasks" : "/login");
    setMobileMenuOpen(false);
  };

  const handleLogoClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    const authenticated = await isAuthenticated();
    router.push(authenticated ? "/tasks" : "/");
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/80 backdrop-blur-lg shadow-md"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button
            onClick={handleLogoClick}
            className="flex items-center space-x-2 cursor-pointer"
          >
            <span className="text-2xl font-bold gradient-text">Todo App</span>
          </button>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <a
              href="#hero"
              className="text-gray-700 hover:text-blue-600 transition-colors font-medium"
            >
              Home
            </a>
            <a
              href="#features"
              className="text-gray-700 hover:text-blue-600 transition-colors font-medium"
            >
              Features
            </a>
            <button
              onClick={handleDashboardClick}
              className="text-gray-700 hover:text-blue-600 transition-colors font-medium"
            >
              Dashboard
            </button>
          </div>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Link href="/login">
              <Button variant="outline" size="md">
                Login
              </Button>
            </Link>
            <Link href="/signup">
              <Button variant="primary" size="md">
                Sign Up
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-gray-700" />
            ) : (
              <Menu className="w-6 h-6 text-gray-700" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200 shadow-lg">
          <div className="px-4 py-4 space-y-4">
            <a
              href="#hero"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-gray-700 hover:text-blue-600 transition-colors font-medium py-2"
            >
              Home
            </a>
            <a
              href="#features"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-gray-700 hover:text-blue-600 transition-colors font-medium py-2"
            >
              Features
            </a>
            <button
              onClick={handleDashboardClick}
              className="block w-full text-left text-gray-700 hover:text-blue-600 transition-colors font-medium py-2"
            >
              Dashboard
            </button>
            <div className="pt-4 space-y-2 border-t border-gray-200">
              <Link href="/login" className="block">
                <Button variant="outline" size="md" className="w-full">
                  Login
                </Button>
              </Link>
              <Link href="/signup" className="block">
                <Button variant="primary" size="md" className="w-full">
                  Sign Up
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
