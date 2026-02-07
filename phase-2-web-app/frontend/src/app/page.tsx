"use client";

/**
 * Home/Landing page with impressive design and animations.
 *
 * Features:
 * - Modern landing page with hero, features, stats, CTA, and footer sections
 * - Smooth scroll animations
 * - Protected dashboard navigation
 * - Accessible to both authenticated and non-authenticated users
 */

import LandingNavbar from "@/components/LandingNavbar";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import StatsSection from "@/components/StatsSection";
import CTASection from "@/components/CTASection";
import Footer from "@/components/Footer";

export default function Home() {

  return (
    <div className="min-h-screen">
      <LandingNavbar />
      <HeroSection />
      <FeaturesSection />
      <StatsSection />
      <CTASection />
      <Footer />
    </div>
  );
}
