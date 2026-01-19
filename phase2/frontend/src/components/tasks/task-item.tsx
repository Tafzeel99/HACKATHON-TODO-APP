"use client";

import { useState } from "react";
import { Check, Trash2, Edit2, X, Calendar, Repeat, Bell, AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { taskApi } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { PriorityBadge } from "./priority-badge";
import type { Task } from "@/types/task";

const tagColors = [
  "bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300",
  "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
  "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300",
  "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-300",
  "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
];

function getTagColor(tag: string): string {
  const hash = tag.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return tagColors[hash % tagColors.length];
}

function formatDueDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();

  // Compare calendar days in local timezone (not raw time difference)
  const dateDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const nowDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const daysDiff = Math.round((dateDay.getTime() - nowDay.getTime()) / (1000 * 60 * 60 * 24));

  // Check if time was set (not midnight)
  const hasTime = date.getHours() !== 0 || date.getMinutes() !== 0;
  const timeStr = hasTime ? ` at ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "";

  if (daysDiff === 0) {
    return `Today${timeStr || " at " + date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  } else if (daysDiff === 1) {
    return `Tomorrow${timeStr || " at " + date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  } else if (daysDiff === -1) {
    return `Yesterday${timeStr}`;
  } else if (daysDiff < 0) {
    return `${Math.abs(daysDiff)} days overdue${timeStr}`;
  } else if (daysDiff < 7) {
    return `${date.toLocaleDateString([], { weekday: "long" })}${timeStr}`;
  } else {
    return `${date.toLocaleDateString([], { month: "short", day: "numeric" })}${timeStr}`;
  }
}

const recurrenceLabels: Record<string, string> = {
  daily: "Daily",
  weekly: "Weekly",
  monthly: "Monthly",
};

interface TaskItemProps {
  task: Task;
  onUpdate?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [isCompleting, setIsCompleting] = useState(false);

  const handleToggleComplete = async () => {
    setIsLoading(true);
    setIsCompleting(true);
    try {
      const updatedTask = await taskApi.toggleComplete(task.id);
      onUpdate?.(updatedTask);

      let toastMessage = updatedTask.completed ? "Task completed" : "Task reopened";
      if (updatedTask.completed && task.recurrence_pattern !== "none") {
        toastMessage = "Task completed. Next occurrence created.";
      }

      toast({
        title: toastMessage,
        description: updatedTask.title,
      });
    } catch (error) {
      console.error("Failed to toggle task:", error);
      toast({
        variant: "destructive",
        title: "Failed to update task",
        description: "Please try again.",
      });
    } finally {
      setIsLoading(false);
      setTimeout(() => setIsCompleting(false), 300);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this task?")) {
      return;
    }

    setIsLoading(true);
    try {
      await taskApi.delete(task.id);
      onDelete?.(task.id);
      toast({
        title: "Task deleted",
        description: task.title,
      });
    } catch (error) {
      console.error("Failed to delete task:", error);
      toast({
        variant: "destructive",
        title: "Failed to delete task",
        description: "Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editTitle.trim()) {
      return;
    }

    setIsLoading(true);
    try {
      const updatedTask = await taskApi.update(task.id, { title: editTitle });
      onUpdate?.(updatedTask);
      setIsEditing(false);
      toast({
        title: "Task updated",
        description: updatedTask.title,
      });
    } catch (error) {
      console.error("Failed to update task:", error);
      toast({
        variant: "destructive",
        title: "Failed to update task",
        description: "Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setIsEditing(false);
  };

  return (
    <div
      className={cn(
        "group relative flex items-start gap-4 rounded-xl border bg-card p-4 transition-all duration-200",
        "hover:border-primary/20 hover:shadow-sm",
        task.completed && "bg-muted/30 border-border/50",
        task.is_overdue && !task.completed && "border-red-200 dark:border-red-900/50 bg-red-50/30 dark:bg-red-900/10",
        isLoading && "opacity-60 pointer-events-none",
        isCompleting && "animate-check"
      )}
    >
      {/* Checkbox with animation */}
      <div className="pt-0.5">
        <Checkbox
          checked={task.completed}
          onCheckedChange={handleToggleComplete}
          disabled={isLoading}
          aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
          className={cn(
            "h-5 w-5 rounded-full transition-all duration-200",
            task.completed && "bg-success border-success data-[state=checked]:bg-success"
          )}
        />
      </div>

      {isEditing ? (
        <div className="flex flex-1 items-center gap-2">
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="flex-1 h-9"
            disabled={isLoading}
            autoFocus
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSaveEdit();
              if (e.key === "Escape") handleCancelEdit();
            }}
          />
          <Button
            size="icon"
            variant="ghost"
            onClick={handleSaveEdit}
            disabled={isLoading}
            className="h-8 w-8 text-success hover:text-success hover:bg-success/10"
          >
            <Check className="h-4 w-4" />
          </Button>
          <Button
            size="icon"
            variant="ghost"
            onClick={handleCancelEdit}
            disabled={isLoading}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ) : (
        <>
          <div className="flex-1 min-w-0">
            {/* Title row with priority badge */}
            <div className="flex items-center gap-2 flex-wrap">
              <p
                className={cn(
                  "font-medium leading-tight transition-all duration-200",
                  task.completed && "text-muted-foreground line-through"
                )}
              >
                {task.title}
              </p>
              <PriorityBadge priority={task.priority} />
              {task.is_overdue && !task.completed && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300">
                  <AlertCircle className="h-3 w-3" />
                  Overdue
                </span>
              )}
            </div>

            {/* Description */}
            {task.description && (
              <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                {task.description}
              </p>
            )}

            {/* Tags */}
            {task.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {task.tags.map((tag) => (
                  <span
                    key={tag}
                    className={cn(
                      "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                      getTagColor(tag)
                    )}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Metadata row */}
            <div className="flex items-center gap-3 mt-2 flex-wrap">
              {/* Due date */}
              {task.due_date && (
                <div
                  className={cn(
                    "flex items-center gap-1 text-xs",
                    task.is_overdue && !task.completed
                      ? "text-red-600 dark:text-red-400"
                      : "text-muted-foreground"
                  )}
                >
                  <Calendar className="h-3 w-3" />
                  <span>{formatDueDate(task.due_date)}</span>
                </div>
              )}

              {/* Recurrence */}
              {task.recurrence_pattern !== "none" && (
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Repeat className="h-3 w-3" />
                  <span>{recurrenceLabels[task.recurrence_pattern]}</span>
                </div>
              )}

              {/* Reminder */}
              {task.reminder_at && !task.completed && (
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Bell className="h-3 w-3" />
                  <span>Reminder set</span>
                </div>
              )}

              {/* Completed badge */}
              {task.completed && (
                <span className="inline-flex items-center rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
                  Completed
                </span>
              )}
            </div>
          </div>

          {/* Action buttons - visible on hover */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <Button
              size="icon"
              variant="ghost"
              onClick={() => setIsEditing(true)}
              disabled={isLoading}
              aria-label="Edit task"
              className="h-8 w-8 text-muted-foreground hover:text-primary hover:bg-primary/10"
            >
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={handleDelete}
              disabled={isLoading}
              aria-label="Delete task"
              className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
