"use client";

import Link from "next/link";
import Button from "@/components/ui/Button";
import { useInView } from "@/hooks/useInView";

/**
 * Call-to-Action section for the landing page.
 * Encourages users to sign up with a compelling message.
 */
export default function CTASection() {
  const { ref, isInView } = useInView();

  return (
    <section className="py-20 px-4 bg-gradient-to-br from-purple-50 to-blue-50 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse-slow"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse-slow animation-delay-400"></div>
      </div>

      <div
        ref={ref}
        className={`max-w-4xl mx-auto text-center relative z-10 transition-all duration-700 ${
          isInView
            ? "opacity-100 translate-y-0"
            : "opacity-0 translate-y-10"
        }`}
      >
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Ready to Boost Your Productivity?
        </h2>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Join thousands of users who trust us with their tasks and experience
          the difference
        </p>
        <Link href="/signup">
          <Button variant="primary" size="lg" className="shadow-lg hover:shadow-xl transition-shadow">
            Get Started for Free
          </Button>
        </Link>
      </div>
    </section>
  );
}
