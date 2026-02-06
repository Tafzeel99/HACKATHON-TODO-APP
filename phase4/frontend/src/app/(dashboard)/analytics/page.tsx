"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  Circle,
  AlertCircle,
  Calendar,
  Tag,
  Zap,
  Target,
  Clock,
  Award,
} from "lucide-react";

import { taskApi } from "@/lib/api";
import type { Task } from "@/types/task";
import { cn } from "@/lib/utils";

export default function AnalyticsPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await taskApi.list({
        status: "all",
        sort: "created",
        order: "desc",
      });
      setTasks(response.tasks);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Calculate analytics
  const analytics = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter((t) => t.completed).length;
    const pending = total - completed;
    const overdue = tasks.filter((t) => t.is_overdue && !t.completed).length;
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;

    // Priority breakdown
    const byPriority = {
      high: tasks.filter((t) => t.priority === "high").length,
      medium: tasks.filter((t) => t.priority === "medium").length,
      low: tasks.filter((t) => t.priority === "low").length,
    };

    // Tags breakdown
    const tagCounts: Record<string, number> = {};
    tasks.forEach((t) => {
      t.tags.forEach((tag) => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });
    const topTags = Object.entries(tagCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    // Weekly activity (last 7 days)
    const weeklyData: { day: string; completed: number; created: number }[] = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split("T")[0];
      const dayName = date.toLocaleDateString("en-US", { weekday: "short" });

      const createdOnDay = tasks.filter((t) => t.created_at.startsWith(dateStr)).length;
      const completedOnDay = tasks.filter(
        (t) => t.completed && t.updated_at.startsWith(dateStr)
      ).length;

      weeklyData.push({ day: dayName, completed: completedOnDay, created: createdOnDay });
    }

    // Productivity score (simple algorithm)
    const productivityScore = Math.min(
      100,
      Math.round(
        completionRate * 0.5 +
          (overdue === 0 ? 30 : Math.max(0, 30 - overdue * 5)) +
          (total > 0 ? 20 : 0)
      )
    );

    // Tasks with due dates
    const withDueDate = tasks.filter((t) => t.due_date).length;
    const dueDateUsage = total > 0 ? Math.round((withDueDate / total) * 100) : 0;

    return {
      total,
      completed,
      pending,
      overdue,
      completionRate,
      byPriority,
      topTags,
      weeklyData,
      productivityScore,
      dueDateUsage,
    };
  }, [tasks]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-muted animate-pulse" />
          <div className="space-y-2">
            <div className="h-6 w-32 bg-muted animate-pulse rounded" />
            <div className="h-4 w-48 bg-muted animate-pulse rounded" />
          </div>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl gradient-primary shadow-glow-sm">
            <BarChart3 className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">
              <span className="text-gradient">Analytics</span>
            </h1>
            <p className="text-sm text-muted-foreground">
              Track your productivity and task insights
            </p>
          </div>
        </div>

        {/* Productivity Score Badge */}
        <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-gradient-to-r from-primary/10 to-purple-500/10 border border-primary/20">
          <Award className="h-5 w-5 text-primary" />
          <div>
            <p className="text-xs text-muted-foreground">Productivity Score</p>
            <p className="text-xl font-bold text-primary">{analytics.productivityScore}/100</p>
          </div>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Tasks"
          value={analytics.total}
          icon={<Target className="h-5 w-5" />}
          color="primary"
          subtitle="All time"
        />
        <StatCard
          title="Completed"
          value={analytics.completed}
          icon={<CheckCircle2 className="h-5 w-5" />}
          color="success"
          subtitle={`${analytics.completionRate}% rate`}
          trend={analytics.completionRate >= 50 ? "up" : "down"}
        />
        <StatCard
          title="Pending"
          value={analytics.pending}
          icon={<Circle className="h-5 w-5" />}
          color="warning"
          subtitle="To complete"
        />
        <StatCard
          title="Overdue"
          value={analytics.overdue}
          icon={<AlertCircle className="h-5 w-5" />}
          color="destructive"
          subtitle={analytics.overdue === 0 ? "Great job!" : "Need attention"}
          trend={analytics.overdue === 0 ? "up" : "down"}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Completion Donut Chart */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Zap className="h-4 w-4 text-primary" />
            Completion Rate
          </h3>
          <div className="flex items-center justify-center gap-8">
            <DonutChart
              completed={analytics.completed}
              pending={analytics.pending}
              overdue={analytics.overdue}
            />
            <div className="space-y-3">
              <LegendItem color="bg-success" label="Completed" value={analytics.completed} />
              <LegendItem color="bg-warning" label="Pending" value={analytics.pending - analytics.overdue} />
              <LegendItem color="bg-destructive" label="Overdue" value={analytics.overdue} />
            </div>
          </div>
        </div>

        {/* Priority Distribution */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" />
            Priority Distribution
          </h3>
          <div className="space-y-4">
            <PriorityBar
              label="High Priority"
              value={analytics.byPriority.high}
              total={analytics.total}
              color="bg-red-500"
            />
            <PriorityBar
              label="Medium Priority"
              value={analytics.byPriority.medium}
              total={analytics.total}
              color="bg-amber-500"
            />
            <PriorityBar
              label="Low Priority"
              value={analytics.byPriority.low}
              total={analytics.total}
              color="bg-green-500"
            />
          </div>
        </div>
      </div>

      {/* Weekly Activity */}
      <div className="rounded-xl border bg-card p-5">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Calendar className="h-4 w-4 text-primary" />
          Weekly Activity
        </h3>
        <div className="flex items-end justify-between gap-2 h-40">
          {analytics.weeklyData.map((day, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-2">
              <div className="w-full flex flex-col items-center gap-1 flex-1 justify-end">
                {/* Completed bar */}
                <div
                  className="w-full max-w-8 rounded-t bg-success transition-all duration-500"
                  style={{
                    height: `${Math.max(4, day.completed * 20)}px`,
                  }}
                />
                {/* Created bar */}
                <div
                  className="w-full max-w-8 rounded-b bg-primary/30 transition-all duration-500"
                  style={{
                    height: `${Math.max(4, day.created * 20)}px`,
                  }}
                />
              </div>
              <span className="text-xs text-muted-foreground">{day.day}</span>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t">
          <div className="flex items-center gap-2 text-xs">
            <div className="h-3 w-3 rounded bg-success" />
            <span className="text-muted-foreground">Completed</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="h-3 w-3 rounded bg-primary/30" />
            <span className="text-muted-foreground">Created</span>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Tags */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Tag className="h-4 w-4 text-primary" />
            Top Tags
          </h3>
          {analytics.topTags.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No tags used yet. Add tags to your tasks for better organization.
            </p>
          ) : (
            <div className="space-y-3">
              {analytics.topTags.map(([tag, count], i) => (
                <div key={tag} className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground w-4">{i + 1}</span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">{tag}</span>
                      <span className="text-xs text-muted-foreground">{count} tasks</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full rounded-full bg-primary transition-all duration-500"
                        style={{
                          width: `${(count / (analytics.topTags[0]?.[1] || 1)) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Insights */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Zap className="h-4 w-4 text-primary" />
            Insights
          </h3>
          <div className="space-y-3">
            <InsightItem
              icon={<Clock className="h-4 w-4" />}
              title="Due Date Usage"
              value={`${analytics.dueDateUsage}%`}
              description="of tasks have due dates"
              positive={analytics.dueDateUsage >= 50}
            />
            <InsightItem
              icon={<CheckCircle2 className="h-4 w-4" />}
              title="Completion Rate"
              value={`${analytics.completionRate}%`}
              description="tasks completed"
              positive={analytics.completionRate >= 50}
            />
            <InsightItem
              icon={<AlertCircle className="h-4 w-4" />}
              title="Overdue Tasks"
              value={analytics.overdue.toString()}
              description={analytics.overdue === 0 ? "You're on track!" : "tasks need attention"}
              positive={analytics.overdue === 0}
            />
            <InsightItem
              icon={<Target className="h-4 w-4" />}
              title="High Priority"
              value={analytics.byPriority.high.toString()}
              description="important tasks"
              positive={true}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: "primary" | "success" | "warning" | "destructive";
  subtitle: string;
  trend?: "up" | "down";
}

function StatCard({ title, value, icon, color, subtitle, trend }: StatCardProps) {
  const colorClasses = {
    primary: "text-primary bg-primary/10 border-primary/20",
    success: "text-success bg-success/10 border-success/20",
    warning: "text-warning bg-warning/10 border-warning/20",
    destructive: "text-destructive bg-destructive/10 border-destructive/20",
  };

  return (
    <div className="rounded-xl border bg-card p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className={cn("p-2 rounded-lg border", colorClasses[color])}>
          {icon}
        </div>
        {trend && (
          <div className={cn("text-xs flex items-center gap-1", trend === "up" ? "text-success" : "text-destructive")}>
            {trend === "up" ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
          </div>
        )}
      </div>
      <p className={cn("text-3xl font-bold mt-3", `text-${color}`)}>{value}</p>
      <p className="text-xs text-muted-foreground mt-1">{title}</p>
      <p className="text-[10px] text-muted-foreground/70">{subtitle}</p>
    </div>
  );
}

// Donut Chart Component
function DonutChart({ completed, pending, overdue }: { completed: number; pending: number; overdue: number }) {
  const total = completed + pending;
  if (total === 0) {
    return (
      <div className="relative w-32 h-32">
        <svg className="w-32 h-32 transform -rotate-90">
          <circle cx="64" cy="64" r="56" fill="none" stroke="currentColor" strokeWidth="16" className="text-muted" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-muted-foreground">0%</span>
        </div>
      </div>
    );
  }

  const completedPct = (completed / total) * 100;
  const pendingPct = ((pending - overdue) / total) * 100;
  const overduePct = (overdue / total) * 100;

  const circumference = 2 * Math.PI * 56;
  const completedDash = (completedPct / 100) * circumference;
  const pendingDash = (pendingPct / 100) * circumference;
  const overdueDash = (overduePct / 100) * circumference;

  return (
    <div className="relative w-32 h-32">
      <svg className="w-32 h-32 transform -rotate-90">
        {/* Completed */}
        <circle
          cx="64"
          cy="64"
          r="56"
          fill="none"
          stroke="hsl(var(--success))"
          strokeWidth="16"
          strokeDasharray={`${completedDash} ${circumference}`}
          strokeDashoffset="0"
          className="transition-all duration-500"
        />
        {/* Pending */}
        <circle
          cx="64"
          cy="64"
          r="56"
          fill="none"
          stroke="hsl(var(--warning))"
          strokeWidth="16"
          strokeDasharray={`${pendingDash} ${circumference}`}
          strokeDashoffset={-completedDash}
          className="transition-all duration-500"
        />
        {/* Overdue */}
        <circle
          cx="64"
          cy="64"
          r="56"
          fill="none"
          stroke="hsl(var(--destructive))"
          strokeWidth="16"
          strokeDasharray={`${overdueDash} ${circumference}`}
          strokeDashoffset={-(completedDash + pendingDash)}
          className="transition-all duration-500"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold">{Math.round(completedPct)}%</span>
      </div>
    </div>
  );
}

// Legend Item
function LegendItem({ color, label, value }: { color: string; label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className={cn("h-3 w-3 rounded-full", color)} />
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-medium ml-auto">{value}</span>
    </div>
  );
}

// Priority Bar
function PriorityBar({ label, value, total, color }: { label: string; value: number; total: number; color: string }) {
  const percentage = total > 0 ? (value / total) * 100 : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm">{label}</span>
        <span className="text-sm text-muted-foreground">{value} ({Math.round(percentage)}%)</span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-500", color)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// Insight Item
function InsightItem({
  icon,
  title,
  value,
  description,
  positive,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
  description: string;
  positive: boolean;
}) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
      <div className={cn("p-2 rounded-lg", positive ? "bg-success/10 text-success" : "bg-warning/10 text-warning")}>
        {icon}
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      <span className={cn("text-lg font-bold", positive ? "text-success" : "text-warning")}>{value}</span>
    </div>
  );
}
