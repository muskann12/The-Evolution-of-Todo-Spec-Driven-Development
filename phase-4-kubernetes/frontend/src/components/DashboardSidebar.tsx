"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from "recharts";
import { formatRelativeTime } from "@/lib/utils";
import type { DashboardStats, Activity } from "@/lib/types";

interface DashboardSidebarProps {
  stats: DashboardStats;
  activities: Activity[];
}

const CHART_COLORS = {
  ready: "#9CA3AF",
  inProgress: "#3B82F6",
  review: "#8B5CF6",
  completed: "#10B981",
};

export default function DashboardSidebar({
  stats,
  activities,
}: DashboardSidebarProps) {
  const chartData = [
    { name: "Ready", value: stats.ready, color: CHART_COLORS.ready },
    { name: "In Progress", value: stats.inProgress, color: CHART_COLORS.inProgress },
    { name: "For Review", value: stats.forReview, color: CHART_COLORS.review },
    { name: "Completed", value: stats.completed, color: CHART_COLORS.completed },
  ];

  return (
    <div className="w-72 bg-white/90 backdrop-blur-lg border-l border-purple-100 p-4 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
      {/* Statistics Card */}
      <div className="mb-6">
        <h2 className="text-base font-semibold text-gray-900 mb-3">
          Project Statistics
        </h2>

        {/* Pie Chart */}
        <div className="h-48 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={70}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-2">
          <StatCard
            label="Total Projects"
            value={stats.totalProjects}
            color="purple"
          />
          <StatCard
            label="For Review"
            value={stats.forReview}
            color="review"
          />
          <StatCard
            label="In Progress"
            value={stats.inProgress}
            color="blue"
          />
          <StatCard
            label="Completed"
            value={stats.completed}
            color="green"
          />
        </div>
      </div>

      {/* Recent Activities */}
      <div>
        <h2 className="text-base font-semibold text-gray-900 mb-3">
          Recent Activities
        </h2>
        <div className="space-y-3">
          {activities.length > 0 ? (
            activities.map((activity) => (
              <ActivityItem key={activity.id} activity={activity} />
            ))
          ) : (
            <p className="text-sm text-gray-500 text-center py-4">
              No recent activities
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const colorClasses = {
    purple: "bg-purple-50 text-purple-700",
    review: "bg-purple-50 text-purple-700",
    blue: "bg-blue-50 text-blue-700",
    green: "bg-green-50 text-green-700",
  };

  return (
    <div className={`p-2 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
      <p className="text-[10px] font-medium opacity-80 leading-tight">{label}</p>
      <p className="text-xl font-bold mt-0.5">{value}</p>
    </div>
  );
}

function ActivityItem({ activity }: { activity: Activity }) {
  return (
    <div className="flex items-start gap-2">
      <div className="w-7 h-7 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
        {activity.user.charAt(0).toUpperCase()}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-900 leading-tight">
          <span className="font-semibold">{activity.user}</span>{" "}
          <span className="text-gray-600">{activity.action}</span>
        </p>
        <p className="text-[10px] text-gray-500 mt-0.5">
          {formatRelativeTime(activity.timestamp)}
        </p>
      </div>
    </div>
  );
}
