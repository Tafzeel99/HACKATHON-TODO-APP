"use client";

import { ClipboardList } from "lucide-react";
import { TaskItem } from "@/components/tasks/task-item";
import type { Task } from "@/types/task";

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
  onUpdate?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

function TaskSkeleton({ index }: { index: number }) {
  return (
    <div
      className={`flex items-start gap-4 rounded-xl border bg-card p-4 animate-fade-up stagger-${index + 1}`}
    >
      {/* Checkbox skeleton */}
      <div className="h-5 w-5 rounded-full bg-muted animate-pulse" />
      {/* Content skeleton */}
      <div className="flex-1 space-y-2">
        <div className="h-4 w-3/4 rounded bg-muted animate-pulse" />
        <div className="h-3 w-1/2 rounded bg-muted animate-pulse" />
        <div className="h-3 w-24 rounded bg-muted animate-pulse mt-3" />
      </div>
      {/* Action buttons skeleton */}
      <div className="flex gap-1">
        <div className="h-8 w-8 rounded-lg bg-muted animate-pulse" />
        <div className="h-8 w-8 rounded-lg bg-muted animate-pulse" />
      </div>
    </div>
  );
}

export function TaskList({ tasks, isLoading, onUpdate, onDelete }: TaskListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <TaskSkeleton key={i} index={i} />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed bg-muted/20 p-12 text-center animate-fade-up">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mb-4">
          <ClipboardList className="h-8 w-8 text-primary" />
        </div>
        <h3 className="text-lg font-semibold mb-1">No tasks yet</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Get started by adding your first task above. Stay organized and track your progress!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task, index) => (
        <div
          key={task.id}
          className={`animate-fade-up`}
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <TaskItem
            task={task}
            onUpdate={onUpdate}
            onDelete={onDelete}
          />
        </div>
      ))}
    </div>
  );
}
