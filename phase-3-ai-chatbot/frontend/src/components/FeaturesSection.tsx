"use client";

import { Kanban, Zap, Repeat, Tag, BarChart3, Shield } from "lucide-react";
import { useInView } from "@/hooks/useInView";

/**
 * Features section showcasing the key capabilities of the todo app.
 * Features animate in when scrolled into view.
 */
export default function FeaturesSection() {
  const { ref, isInView } = useInView();

  const features = [
    {
      icon: Kanban,
      title: "Kanban Boards",
      description: "Visualize your workflow with intuitive drag-and-drop boards",
      color: "text-purple-600",
      bgColor: "bg-purple-100",
    },
    {
      icon: Zap,
      title: "Smart Priorities",
      description: "Focus on what matters most with intelligent prioritization",
      color: "text-yellow-600",
      bgColor: "bg-yellow-100",
    },
    {
      icon: Repeat,
      title: "Recurring Tasks",
      description: "Automate repetitive tasks with flexible recurrence patterns",
      color: "text-blue-600",
      bgColor: "bg-blue-100",
    },
    {
      icon: Tag,
      title: "Rich Tagging",
      description: "Organize tasks with custom tags and categories",
      color: "text-green-600",
      bgColor: "bg-green-100",
    },
    {
      icon: BarChart3,
      title: "Analytics Dashboard",
      description: "Track your productivity with beautiful charts and insights",
      color: "text-indigo-600",
      bgColor: "bg-indigo-100",
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Your data is safe with enterprise-grade security",
      color: "text-red-600",
      bgColor: "bg-red-100",
    },
  ];

  return (
    <section id="features" className="py-20 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        {/* Section heading */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Everything You Need to Stay Productive
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Powerful features designed to help you accomplish more, every single day
          </p>
        </div>

        {/* Feature cards grid */}
        <div
          ref={ref}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className={`group p-6 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-2 ${
                  isInView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
                }`}
                style={{
                  transitionDelay: isInView ? `${index * 100}ms` : "0ms",
                }}
              >
                {/* Icon */}
                <div
                  className={`${feature.bgColor} ${feature.color} w-14 h-14 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                >
                  <Icon className="w-7 h-7" />
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-gray-600">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
