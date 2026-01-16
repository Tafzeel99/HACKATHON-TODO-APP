"use client";

import { useState } from "react";
import { Check, Trash2, Edit2, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { taskApi } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import type { Task } from "@/types/task";

interface TaskItemProps {
  task: Task;
  onUpdate?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);

  const handleToggleComplete = async () => {
    setIsLoading(true);
    try {
      const updatedTask = await taskApi.toggleComplete(task.id);
      onUpdate?.(updatedTask);
      toast({
        title: updatedTask.completed ? "Task completed" : "Task reopened",
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
        "flex items-center gap-3 rounded-lg border p-4 transition-colors",
        task.completed && "bg-muted/50",
        isLoading && "opacity-50"
      )}
    >
      <Checkbox
        checked={task.completed}
        onCheckedChange={handleToggleComplete}
        disabled={isLoading}
        aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
      />

      {isEditing ? (
        <div className="flex flex-1 items-center gap-2">
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="flex-1"
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
          >
            <Check className="h-4 w-4" />
          </Button>
          <Button
            size="icon"
            variant="ghost"
            onClick={handleCancelEdit}
            disabled={isLoading}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ) : (
        <>
          <div className="flex-1">
            <p
              className={cn(
                "font-medium",
                task.completed && "text-muted-foreground line-through"
              )}
            >
              {task.title}
            </p>
            {task.description && (
              <p className="mt-1 text-sm text-muted-foreground">
                {task.description}
              </p>
            )}
          </div>

          <div className="flex items-center gap-1">
            <Button
              size="icon"
              variant="ghost"
              onClick={() => setIsEditing(true)}
              disabled={isLoading}
              aria-label="Edit task"
            >
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={handleDelete}
              disabled={isLoading}
              aria-label="Delete task"
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
