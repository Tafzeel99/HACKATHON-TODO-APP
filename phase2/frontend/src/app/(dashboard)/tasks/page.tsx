"use client";

import { useEffect, useState, useCallback } from "react";

import { TaskForm } from "@/components/tasks/task-form";
import { TaskFilters, type TaskFilters as TaskFiltersType } from "@/components/tasks/task-filters";
import { TaskList } from "@/components/tasks/task-list";
import { taskApi } from "@/lib/api";
import type { Task } from "@/types/task";

const DEFAULT_FILTERS: TaskFiltersType = {
  status: "all",
  sort: "created",
  order: "desc",
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<TaskFiltersType>(DEFAULT_FILTERS);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await taskApi.list({
        status: filters.status,
        sort: filters.sort,
        order: filters.order,
      });
      setTasks(response.tasks);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleTaskCreated = () => {
    // Refetch to ensure proper sorting/filtering
    fetchTasks();
  };

  const handleTaskUpdate = () => {
    // Refetch to ensure proper sorting/filtering after status change
    fetchTasks();
  };

  const handleTaskDelete = (taskId: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
  };

  const handleFiltersChange = (newFilters: TaskFiltersType) => {
    setFilters(newFilters);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">My Tasks</h2>
        <p className="text-muted-foreground">
          Manage your tasks and stay organized.
        </p>
      </div>

      <TaskForm onTaskCreated={handleTaskCreated} />

      <TaskFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        disabled={isLoading}
      />

      <TaskList
        tasks={tasks}
        isLoading={isLoading}
        onUpdate={handleTaskUpdate}
        onDelete={handleTaskDelete}
      />
    </div>
  );
}
