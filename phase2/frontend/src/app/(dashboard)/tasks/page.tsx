"use client";

import { useEffect, useState, useCallback } from "react";
import { Bell } from "lucide-react";

import { TaskForm } from "@/components/tasks/task-form";
import { TaskFilters } from "@/components/tasks/task-filters";
import { TaskList } from "@/components/tasks/task-list";
import { TaskStats } from "@/components/tasks/task-stats";
import { Button } from "@/components/ui/button";
import { taskApi } from "@/lib/api";
import { useNotifications } from "@/hooks/use-notifications";
import { toast } from "@/hooks/use-toast";
import type { Task, TaskFilters as TaskFiltersType } from "@/types/task";

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

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">
            <span className="text-gradient">My Tasks</span>
          </h2>
          <p className="text-muted-foreground">
            Manage your tasks and stay organized. Track your progress below.
          </p>
        </div>

        {/* Notification toggle */}
        {isSupported && permission !== "granted" && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleEnableNotifications}
            className="flex items-center gap-2"
          >
            <Bell className="h-4 w-4" />
            Enable Reminders
          </Button>
        )}
        {isSupported && permission === "granted" && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Bell className="h-4 w-4 text-success" />
            Reminders active
          </div>
        )}
      </div>

      {/* Stats Section */}
      <TaskStats tasks={allTasks} isLoading={isLoading && allTasks.length === 0} />

      {/* Task Creation */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Add New Task</h3>
        <TaskForm onTaskCreated={handleTaskCreated} />
      </div>

      {/* Task List Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h3 className="text-lg font-semibold">Task List</h3>
          <TaskFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
            disabled={isLoading}
          />
        </div>

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
