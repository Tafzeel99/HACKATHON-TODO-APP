"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Bell,
  ListTodo,
  Plus,
  Filter,
  CheckCircle2,
  Circle,
  AlertCircle,
  TrendingUp,
} from "lucide-react";

import { TaskForm } from "@/components/tasks/task-form";
import { TaskFilters } from "@/components/tasks/task-filters";
import { TaskList } from "@/components/tasks/task-list";
import { Button } from "@/components/ui/button";
import { taskApi } from "@/lib/api";
import { useNotifications } from "@/hooks/use-notifications";
import { toast } from "@/hooks/use-toast";
import type { Task, TaskFilters as TaskFiltersType } from "@/types/task";
import { cn } from "@/lib/utils";

const DEFAULT_FILTERS: TaskFiltersType = {
  status: "all",
  sort: "created",
  order: "desc",
  priority: "all",
  tags: [],
  search: "",
  overdue_only: false,
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [allTasks, setAllTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<TaskFiltersType>(DEFAULT_FILTERS);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const {
    permission,
    isSupported,
    requestPermission,
    scheduleTaskReminders,
  } = useNotifications();

  // Fetch all tasks for stats (unfiltered)
  const fetchAllTasks = useCallback(async () => {
    try {
      const response = await taskApi.list({
        status: "all",
        sort: "created",
        order: "desc",
      });
      setAllTasks(response.tasks);
      // Schedule reminders for tasks with reminder_at
      scheduleTaskReminders(response.tasks);
    } catch (error) {
      console.error("Failed to fetch all tasks:", error);
    }
  }, [scheduleTaskReminders]);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await taskApi.list(filters);
      setTasks(response.tasks);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTasks();
    fetchAllTasks();
  }, [fetchTasks, fetchAllTasks]);

  const handleEnableNotifications = async () => {
    const granted = await requestPermission();
    if (granted) {
      toast({
        title: "Notifications enabled",
        description: "You will receive reminders for your tasks.",
      });
      // Re-schedule reminders now that we have permission
      scheduleTaskReminders(allTasks);
    } else {
      toast({
        variant: "destructive",
        title: "Notifications blocked",
        description: "Please enable notifications in your browser settings.",
      });
    }
  };

  const handleTaskCreated = () => {
    setShowAddForm(false);
    fetchTasks();
    fetchAllTasks();
  };

  const handleTaskUpdate = () => {
    fetchTasks();
    fetchAllTasks();
  };

  const handleTaskDelete = (taskId: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
    setAllTasks((prev) => prev.filter((task) => task.id !== taskId));
  };

  const handleFiltersChange = (newFilters: TaskFiltersType) => {
    setFilters(newFilters);
  };

  // Calculate stats
  const totalTasks = allTasks.length;
  const completedTasks = allTasks.filter((t) => t.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const overdueTasks = allTasks.filter((t) => t.is_overdue && !t.completed).length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl gradient-primary shadow-glow-sm">
            <ListTodo className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">
              <span className="text-gradient">My Tasks</span>
            </h1>
            <p className="text-sm text-muted-foreground">
              Organize and track your progress
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Notification toggle */}
          {isSupported && permission !== "granted" && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleEnableNotifications}
              className="gap-2"
            >
              <Bell className="h-4 w-4" />
              <span className="hidden sm:inline">Enable Reminders</span>
            </Button>
          )}
          {isSupported && permission === "granted" && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-success/10 text-success px-3 py-1.5 rounded-full">
              <Bell className="h-3 w-3" />
              Active
            </div>
          )}

          <Button
            onClick={() => setShowAddForm(!showAddForm)}
            className="gap-2 gradient-primary"
          >
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">New Task</span>
          </Button>
        </div>
      </div>

      {/* Stats Strip */}
      <div className="grid grid-cols-4 gap-3">
        <MiniStat
          label="Total"
          value={totalTasks}
          icon={<ListTodo className="h-4 w-4" />}
          color="primary"
        />
        <MiniStat
          label="Pending"
          value={pendingTasks}
          icon={<Circle className="h-4 w-4" />}
          color="warning"
        />
        <MiniStat
          label="Done"
          value={completedTasks}
          icon={<CheckCircle2 className="h-4 w-4" />}
          color="success"
        />
        <MiniStat
          label="Overdue"
          value={overdueTasks}
          icon={<AlertCircle className="h-4 w-4" />}
          color="destructive"
        />
      </div>

      {/* Progress Bar */}
      {totalTasks > 0 && (
        <div className="rounded-xl border bg-card p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-sm">
              <TrendingUp className="h-4 w-4 text-primary" />
              <span className="font-medium">Overall Progress</span>
            </div>
            <span className="text-lg font-bold text-primary">{completionRate}%</span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full rounded-full gradient-primary transition-all duration-500"
              style={{ width: `${completionRate}%` }}
            />
          </div>
        </div>
      )}

      {/* Add Task Form (Collapsible) */}
      {showAddForm && (
        <div className="animate-fade-up rounded-xl border bg-card p-4 shadow-sm">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Plus className="h-4 w-4 text-primary" />
            Create New Task
          </h3>
          <TaskForm onTaskCreated={handleTaskCreated} />
        </div>
      )}

      {/* Task List Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h3 className="text-lg font-semibold">All Tasks</h3>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="gap-2"
            >
              <Filter className="h-4 w-4" />
              Filters
            </Button>
          </div>
        </div>

        {/* Filters (Collapsible) */}
        {showFilters && (
          <div className="animate-fade-up rounded-xl border bg-muted/30 p-4">
            <TaskFilters
              filters={filters}
              onFiltersChange={handleFiltersChange}
              disabled={isLoading}
            />
          </div>
        )}

        {/* Task List */}
        <TaskList
          tasks={tasks}
          isLoading={isLoading}
          onUpdate={handleTaskUpdate}
          onDelete={handleTaskDelete}
        />
      </div>
    </div>
  );
}

// Mini Stat Component
interface MiniStatProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: "primary" | "success" | "warning" | "destructive";
}

function MiniStat({ label, value, icon, color }: MiniStatProps) {
  const colorClasses = {
    primary: "text-primary",
    success: "text-success",
    warning: "text-warning",
    destructive: "text-destructive",
  };

  return (
    <div className="rounded-xl border bg-card p-3 text-center hover:shadow-sm transition-shadow">
      <div className={cn("flex justify-center mb-1", colorClasses[color])}>
        {icon}
      </div>
      <p className={cn("text-xl font-bold", colorClasses[color])}>{value}</p>
      <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{label}</p>
    </div>
  );
}
