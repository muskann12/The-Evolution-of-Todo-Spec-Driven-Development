/**
 * Reusable Card component for containing content.
 *
 * Server Component - no client-side interactivity.
 * Matches the LoginForm card styling:
 * - White background
 * - Shadow for elevation
 * - Rounded corners
 * - Customizable padding
 */

import { cn } from "@/lib/utils";

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: "sm" | "md" | "lg";
}

export default function Card({ children, className, padding = "md" }: CardProps) {
  // Padding variants
  const paddingClasses = {
    sm: "p-4",
    md: "px-8 pt-6 pb-8", // Default - matches LoginForm
    lg: "p-12",
  };

  return (
    <div
      className={cn(
        "bg-white shadow-md rounded-lg",
        paddingClasses[padding],
        className
      )}
    >
      {children}
    </div>
  );
}
