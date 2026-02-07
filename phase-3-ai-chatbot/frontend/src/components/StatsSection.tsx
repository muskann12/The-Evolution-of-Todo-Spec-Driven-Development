"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Users, Zap, Star } from "lucide-react";
import { useInView } from "@/hooks/useInView";

/**
 * Custom hook for animating numbers from 0 to target value.
 */
function useCounter(end: number, duration: number, shouldStart: boolean) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!shouldStart) return;

    let startTime: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);

      if (progress < 1) {
        setCount(Math.floor(end * progress));
        requestAnimationFrame(animate);
      } else {
        setCount(end);
      }
    };

    requestAnimationFrame(animate);
  }, [end, duration, shouldStart]);

  return count;
}

/**
 * Stats section with animated counters and gradient background.
 * Counters animate when section scrolls into view.
 */
export default function StatsSection() {
  const { ref, isInView } = useInView();

  const stats = [
    {
      icon: CheckCircle2,
      value: 10000,
      suffix: "+",
      label: "Tasks Completed",
    },
    {
      icon: Users,
      value: 500,
      suffix: "+",
      label: "Active Users",
    },
    {
      icon: Zap,
      value: 99.9,
      suffix: "%",
      label: "Uptime",
      decimals: true,
    },
    {
      icon: Star,
      value: 4.8,
      suffix: "★",
      label: "User Rating",
      decimals: true,
    },
  ];

  return (
    <section className="py-20 px-4 bg-gradient-to-r from-purple-600 to-blue-600">
      <div ref={ref} className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            const count = useCounter(
              stat.value,
              2000,
              isInView
            );

            return (
              <div
                key={stat.label}
                className={`text-center transition-all duration-700 ${
                  isInView
                    ? "opacity-100 translate-y-0"
                    : "opacity-0 translate-y-10"
                }`}
                style={{
                  transitionDelay: isInView ? `${index * 100}ms` : "0ms",
                }}
              >
                {/* Icon */}
                <div className="flex justify-center mb-4">
                  <Icon className="w-12 h-12 text-white/90" />
                </div>

                {/* Animated counter */}
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">
                  {stat.decimals ? count.toFixed(1) : count.toLocaleString()}
                  {stat.suffix}
                </div>

                {/* Label */}
                <div className="text-white/80 text-sm md:text-base font-medium">
                  {stat.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
