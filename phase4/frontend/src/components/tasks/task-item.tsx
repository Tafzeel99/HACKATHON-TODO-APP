"use client";

import { useState, useRef, useEffect } from "react";
import { Check, Trash2, Edit2, X, Calendar, Repeat, Bell, AlertCircle, Pin, Archive } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { taskApi } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { PriorityBadge } from "./priority-badge";
import { TaskColorIndicator } from "./task-color-picker";
import { useConfetti } from "@/components/ui/confetti";
import type { Task } from "@/types/task";

// Minimal Tech tag colors - monochrome with accent
const tagColors = [
  "bg-primary/10 text-primary border border-primary/20",
  "bg-muted text-foreground border border-border/50",
  "bg-success/10 text-success border border-success/20",
  "bg-warning/10 text-warning border border-warning/20",
  "bg-muted text-muted-foreground border border-border/50",
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
  onPin?: (task: Task) => void;
  onArchive?: (task: Task) => void;
  enableSwipe?: boolean;
  showProjectBadge?: boolean;
}

export function TaskItem({
  task,
  onUpdate,
  onDelete,
  onPin,
  onArchive,
  enableSwipe = false,
  showProjectBadge = false,
}: TaskItemProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [isCompleting, setIsCompleting] = useState(false);
  const titleRef = useRef<HTMLParagraphElement>(null);
  const { fire: fireConfetti } = useConfetti();

  const handleToggleComplete = async () => {
    setIsLoading(true);
    setIsCompleting(true);
    try {
      const updatedTask = await taskApi.toggleComplete(task.id);
      onUpdate?.(updatedTask);

      // Fire light confetti when completing a task
      if (updatedTask.completed) {
        fireConfetti({
          particleCount: 15,
          spread: 40,
        });
      }

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

  const handleTogglePin = async () => {
    if (!onPin) return;
    setIsLoading(true);
    try {
      onPin(task);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleArchive = async () => {
    if (!onArchive) return;
    setIsLoading(true);
    try {
      onArchive(task);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle double-click to enter edit mode
  const handleTitleDoubleClick = () => {
    setIsEditing(true);
    setEditTitle(task.title);
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
        "group relative flex items-start gap-4 rounded-lg border border-border/50 bg-card p-4 transition-all duration-150",
        "hover:border-primary/25 hover:shadow-sm",
        task.completed && "bg-muted/20 border-border/30",
        task.is_overdue && !task.completed && "border-destructive/30 bg-destructive/5",
        task.pinned && "border-primary/40 bg-primary/5",
        isLoading && "opacity-60 pointer-events-none",
        isCompleting && "animate-check-bounce"
      )}
    >
      {/* Color indicator */}
      <TaskColorIndicator color={task.color} />
      {/* Checkbox - Minimal Tech style */}
      <div className="pt-0.5">
        <Checkbox
          checked={task.completed}
          onCheckedChange={handleToggleComplete}
          disabled={isLoading}
          aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
          className={cn(
            "h-5 w-5 rounded transition-all duration-150 border-2",
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
              {task.pinned && (
                <Pin className="h-3.5 w-3.5 text-primary fill-primary shrink-0" />
              )}
              <p
                ref={titleRef}
                onDoubleClick={handleTitleDoubleClick}
                className={cn(
                  "font-medium leading-tight transition-all duration-200 cursor-text",
                  task.completed && "text-muted-foreground line-through"
                )}
                title="Double-click to edit"
              >
                {task.title}
              </p>
              <PriorityBadge priority={task.priority} />
              {task.is_overdue && !task.completed && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold tracking-wide uppercase bg-destructive/10 text-destructive border border-destructive/20">
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

              {/* Completed badge - Minimal Tech */}
              {task.completed && (
                <span className="inline-flex items-center rounded px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase bg-success/10 text-success border border-success/20">
                  Done
                </span>
              )}
            </div>
          </div>

          {/* Action buttons - visible on hover */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {onPin && (
              <Button
                size="icon"
                variant="ghost"
                onClick={handleTogglePin}
                disabled={isLoading}
                aria-label={task.pinned ? "Unpin task" : "Pin task"}
                className={cn(
                  "h-8 w-8",
                  task.pinned
                    ? "text-primary hover:text-primary hover:bg-primary/10"
                    : "text-muted-foreground hover:text-primary hover:bg-primary/10"
                )}
              >
                <Pin className={cn("h-4 w-4", task.pinned && "fill-current")} />
              </Button>
            )}
            {onArchive && (
              <Button
                size="icon"
                variant="ghost"
                onClick={handleToggleArchive}
                disabled={isLoading}
                aria-label={task.archived ? "Unarchive task" : "Archive task"}
                className="h-8 w-8 text-muted-foreground hover:text-primary hover:bg-primary/10"
              >
                <Archive className="h-4 w-4" />
              </Button>
            )}
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
