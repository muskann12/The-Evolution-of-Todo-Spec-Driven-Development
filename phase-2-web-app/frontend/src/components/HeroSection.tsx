"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import Button from "@/components/ui/Button";
import { isAuthenticated } from "@/lib/auth";

/**
 * Hero section with gradient background, animated elements, and call-to-action buttons.
 * Features staggered fade-in animations and a protected dashboard button.
 */
export default function HeroSection() {
  const router = useRouter();

  const handleDashboardClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    const authenticated = await isAuthenticated();
    router.push(authenticated ? "/tasks" : "/login");
  };

  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 overflow-hidden"
    >
      {/* Animated gradient orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse-slow animation-delay-400"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-pulse-slow animation-delay-200"></div>
      </div>

      {/* Hero content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 py-32 text-center">
        {/* Heading with stagger animation */}
        <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in-up">
          <span className="gradient-text">Organize Your Life,</span>
          <br />
          <span className="text-gray-900">One Task at a Time</span>
        </h1>

        {/* Subheading with delay */}
        <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto animate-fade-in-up animation-delay-200">
          A powerful, intuitive task management platform built for modern
          productivity. Stay focused, track progress, and achieve your goals.
        </p>

        {/* CTA buttons with delay */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in-up animation-delay-400">
          <Link href="/signup">
            <Button variant="primary" size="lg" className="shadow-lg hover:shadow-xl transition-shadow min-w-[200px]">
              Get Started Free
            </Button>
          </Link>
          <Button
            variant="outline"
            size="lg"
            className="min-w-[200px]"
            onClick={handleDashboardClick}
          >
            View Dashboard
          </Button>
        </div>

        {/* Additional info */}
        <p className="mt-8 text-sm text-gray-500 animate-fade-in animation-delay-600">
          No credit card required • Free forever • Get started in seconds
        </p>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <a href="#features" className="text-gray-400 hover:text-gray-600 transition-colors">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </a>
      </div>
    </section>
  );
}
