"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  Plus,
  Sparkles,
  ArrowRight,
  ListTodo,
  CheckCircle2,
  Clock,
  AlertCircle,
  Bot,
  TrendingUp,
  Zap,
  Activity,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { TaskForm } from "@/components/tasks/task-form";
import { TaskItem } from "@/components/tasks/task-item";
import { TodoChatKit } from "@/components/chat/TodoChatKit";
import { ActivityFeed } from "@/components/collaboration/activity-feed";
import { taskApi } from "@/lib/api";
import type { Task } from "@/types/task";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showTaskForm, setShowTaskForm] = useState(false);

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

  const handleTaskCreated = () => {
    setShowTaskForm(false);
    fetchTasks();
  };

  const handleTaskUpdate = () => {
    fetchTasks();
  };

  const handleTaskDelete = (taskId: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
  };

  // Calculate stats
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const overdueTasks = tasks.filter((t) => t.is_overdue && !t.completed).length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Get recent tasks (last 5)
  const recentTasks = tasks.slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Hero Section - Modern Futuristic */}
      <div className="relative overflow-hidden rounded-3xl gradient-primary p-8 lg:p-10">
        {/* Background effects */}
        <div className="absolute inset-0 bg-grid-white\/10" />
        <div className="absolute -right-32 -top-32 h-96 w-96 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -left-32 -bottom-32 h-96 w-96 rounded-full bg-[hsl(var(--gradient-end))]/20 blur-3xl" />

        <div className="relative z-10">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20">
                <Sparkles className="h-4 w-4 text-white" />
                <span className="text-white/90 text-sm font-medium">AI-Powered Productivity</span>
              </div>
              <h1 className="text-3xl lg:text-4xl font-bold text-white tracking-tight">
                Welcome to <span className="text-white/80">todo</span>X
              </h1>
              <p className="text-white/70 max-w-md text-base">
                Manage your tasks intelligently with natural language commands.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button
                onClick={() => setShowTaskForm(!showTaskForm)}
                size="lg"
                className="bg-white text-primary hover:bg-white/90 shadow-xl shadow-black/20 font-semibold"
              >
                <Plus className="h-5 w-5 mr-2" />
                New Task
              </Button>
              <Link href="/chat">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-white/30 text-white hover:bg-white/10 hover:border-white/50 backdrop-blur-sm"
                >
                  <Bot className="h-5 w-5 mr-2" />
                  TodoX Agent
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Task Form (Collapsible) */}
      {showTaskForm && (
        <div className="animate-fade-up">
          <div className="rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm p-6 shadow-lg">
            <h3 className="text-base font-semibold mb-4 flex items-center gap-2">
              <div className="p-2 rounded-xl bg-primary/10">
                <Plus className="h-4 w-4 text-primary" />
              </div>
              Quick Add Task
            </h3>
            <TaskForm onTaskCreated={handleTaskCreated} />
          </div>
        </div>
      )}

      {/* Stats Grid - Modern Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
        <StatCard
          title="Total Tasks"
          value={totalTasks}
          icon={<ListTodo className="h-6 w-6" />}
          color="primary"
          delay="stagger-1"
        />
        <StatCard
          title="Completed"
          value={completedTasks}
          icon={<CheckCircle2 className="h-6 w-6" />}
          color="success"
          delay="stagger-2"
        />
        <StatCard
          title="Pending"
          value={pendingTasks}
          icon={<Clock className="h-6 w-6" />}
          color="warning"
          delay="stagger-3"
        />
        <StatCard
          title="Overdue"
          value={overdueTasks}
          icon={<AlertCircle className="h-6 w-6" />}
          color="destructive"
          delay="stagger-4"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Left Column - Recent Tasks */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold flex items-center gap-3">
              <div className="p-2 rounded-xl bg-primary/10">
                <Zap className="h-5 w-5 text-primary" />
              </div>
              Recent Tasks
            </h2>
            <Link href="/tasks">
              <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-primary">
                View All
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          <div className="space-y-3">
            {isLoading ? (
              // Loading skeletons
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="rounded-2xl border border-border/50 bg-card p-5">
                  <div className="flex items-start gap-4">
                    <div className="h-6 w-6 rounded-lg bg-muted animate-pulse" />
                    <div className="flex-1 space-y-3">
                      <div className="h-5 w-3/4 bg-muted rounded-lg animate-pulse" />
                      <div className="h-4 w-1/2 bg-muted rounded-lg animate-pulse" />
                    </div>
                  </div>
                </div>
              ))
            ) : recentTasks.length === 0 ? (
              <div className="rounded-2xl border-2 border-dashed border-border/50 bg-card/50 p-10 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-muted/50 flex items-center justify-center">
                  <ListTodo className="h-8 w-8 text-muted-foreground/50" />
                </div>
                <h3 className="font-semibold text-foreground">No tasks yet</h3>
                <p className="text-sm text-muted-foreground mt-1 mb-4">
                  Create your first task or ask the TodoX Agent
                </p>
                <Button onClick={() => setShowTaskForm(true)} className="shadow-lg">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Task
                </Button>
              </div>
            ) : (
              recentTasks.map((task, index) => (
                <div key={task.id} className={cn("animate-fade-up", `stagger-${index + 1}`)}>
                  <TaskItem
                    task={task}
                    onUpdate={handleTaskUpdate}
                    onDelete={handleTaskDelete}
                  />
                </div>
              ))
            )}
          </div>

          {/* Progress Card */}
          {totalTasks > 0 && (
            <div className="relative rounded-2xl border border-border/50 bg-gradient-to-br from-card via-card to-primary/5 p-6 overflow-hidden">
              {/* Decorative glow */}
              <div className="absolute -right-10 -bottom-10 w-32 h-32 bg-primary/10 rounded-full blur-2xl" />

              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-primary/10">
                      <TrendingUp className="h-5 w-5 text-primary" />
                    </div>
                    <span className="font-semibold">Your Progress</span>
                  </div>
                  <span className="text-3xl font-bold text-gradient">{completionRate}%</span>
                </div>
                <div className="h-3 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full rounded-full gradient-primary transition-all duration-700 ease-out shadow-lg shadow-primary/30"
                    style={{ width: `${completionRate}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground mt-3">
                  <span className="font-medium text-foreground">{completedTasks}</span> of <span className="font-medium text-foreground">{totalTasks}</span> tasks completed
                </p>
              </div>
            </div>
          )}

          {/* Activity Feed Widget */}
          <div className="rounded-2xl border border-border/50 bg-card p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-xl bg-primary/10">
                <Activity className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold">Recent Activity</h3>
            </div>
            <ActivityFeed limit={5} maxHeight="250px" />
          </div>
        </div>

        {/* Right Column - TodoX Agent */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold flex items-center gap-3">
              <div className="p-2 rounded-xl bg-gradient-to-br from-primary/20 to-[hsl(var(--gradient-end))]/20">
                <Bot className="h-5 w-5 text-primary" />
              </div>
              TodoX Agent
              <span className="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded-full bg-success/10 text-success border border-success/20">
                Online
              </span>
            </h2>
            <Link href="/chat">
              <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-primary">
                Full View
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          {/* Chat Container */}
          <div className="relative rounded-2xl border border-border/50 bg-card overflow-hidden shadow-xl" style={{ height: "500px" }}>
            {/* Decorative top border */}
            <div className="absolute top-0 left-0 right-0 h-1 gradient-primary" />
            <TodoChatKit />
          </div>

          {/* Quick Commands */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-5">
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              Quick Commands
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {[
                { text: "Add a task", icon: "+" },
                { text: "Show pending", icon: "○" },
                { text: "Complete task", icon: "✓" },
                { text: "Delete task", icon: "×" },
              ].map((cmd, i) => (
                <div
                  key={cmd.text}
                  className={cn(
                    "group flex items-center gap-2 text-sm text-muted-foreground bg-background/50 rounded-xl px-4 py-3 border border-border/50",
                    "hover:border-primary/20 hover:bg-primary/5 hover:text-foreground transition-all duration-200 cursor-default",
                    "animate-fade-up",
                    `stagger-${i + 1}`
                  )}
                >
                  <span className="text-primary/70 group-hover:text-primary transition-colors">{cmd.icon}</span>
                  &quot;{cmd.text}...&quot;
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component - Modern Design
interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: "primary" | "success" | "warning" | "destructive";
  delay?: string;
}

function StatCard({ title, value, icon, color, delay }: StatCardProps) {
  const colorConfig = {
    primary: {
      bg: "bg-primary/10",
      text: "text-primary",
      border: "border-primary/20",
      glow: "shadow-primary/20",
    },
    success: {
      bg: "bg-success/10",
      text: "text-success",
      border: "border-success/20",
      glow: "shadow-success/20",
    },
    warning: {
      bg: "bg-warning/10",
      text: "text-warning",
      border: "border-warning/20",
      glow: "shadow-warning/20",
    },
    destructive: {
      bg: "bg-destructive/10",
      text: "text-destructive",
      border: "border-destructive/20",
      glow: "shadow-destructive/20",
    },
  };

  const config = colorConfig[color];

  return (
    <div className={cn("stat-card animate-fade-up", delay)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {title}
          </p>
          <p className={cn("text-3xl lg:text-4xl font-bold", config.text)}>
            {value}
          </p>
        </div>
        <div className={cn("p-3 rounded-2xl border shadow-lg", config.bg, config.border, config.glow)}>
          <div className={config.text}>{icon}</div>
        </div>
      </div>
    </div>
  );
}
