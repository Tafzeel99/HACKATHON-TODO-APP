"use client";

import { TaskItem } from "@/components/tasks/task-item";
import type { Task } from "@/types/task";

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
  onUpdate?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

export function TaskList({ tasks, isLoading, onUpdate, onDelete }: TaskListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="flex items-center gap-3 rounded-lg border p-4"
          >
            {/* Checkbox skeleton */}
            <div className="h-4 w-4 animate-pulse rounded bg-muted" />
            {/* Content skeleton */}
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
              <div className="h-3 w-1/2 animate-pulse rounded bg-muted" />
            </div>
            {/* Action buttons skeleton */}
            <div className="flex gap-1">
              <div className="h-8 w-8 animate-pulse rounded bg-muted" />
              <div className="h-8 w-8 animate-pulse rounded bg-muted" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-8 text-center">
        <p className="text-muted-foreground">
          No tasks yet. Add your first task above!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
