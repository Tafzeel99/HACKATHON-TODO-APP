"use client";

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Calendar, Pin, MoreHorizontal, Check, Trash2 } from "lucide-react";
import { Task } from "@/types/task";
import { PriorityBadge } from "./priority-badge";
import { TaskColorIndicator } from "./task-color-picker";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface KanbanCardProps {
  task: Task;
  onClick?: () => void;
  onComplete?: () => void;
  onDelete?: () => void;
  isDragging?: boolean;
}

export function KanbanCard({
  task,
  onClick,
  onComplete,
  onDelete,
  isDragging = false,
}: KanbanCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const isBeingDragged = isDragging || isSortableDragging;

  // Format due date
  const formatDueDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return "Today";
    }
    if (date.toDateString() === tomorrow.toDateString()) {
      return "Tomorrow";
    }
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={cn(
        "relative bg-card rounded-lg p-3 cursor-grab active:cursor-grabbing",
        "border border-border shadow-sm transition-all duration-200",
        "hover:shadow-md hover:border-primary/20",
        isBeingDragged && "kanban-card-dragging opacity-90",
        task.completed && "opacity-60"
      )}
      onClick={(e) => {
        if ((e.target as HTMLElement).closest("button")) return;
        onClick?.();
      }}
    >
      {/* Color indicator */}
      <TaskColorIndicator color={task.color} />

      {/* Card content */}
      <div className="space-y-2">
        {/* Title row */}
        <div className="flex items-start gap-2">
          <h4
            className={cn(
              "flex-1 font-medium text-sm text-foreground line-clamp-2",
              task.completed && "line-through text-muted-foreground"
            )}
          >
            {task.title}
          </h4>

          {task.pinned && (
            <Pin className="h-3.5 w-3.5 text-primary fill-primary shrink-0" />
          )}

          {/* Actions menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 hover:opacity-100 focus:opacity-100"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={onComplete}>
                <Check className="h-4 w-4 mr-2" />
                {task.completed ? "Mark incomplete" : "Mark complete"}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={onDelete}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Meta row */}
        <div className="flex items-center gap-2 flex-wrap">
          <PriorityBadge priority={task.priority} size="sm" />

          {task.due_date && (
            <div
              className={cn(
                "flex items-center gap-1 text-xs",
                task.is_overdue
                  ? "text-destructive"
                  : "text-muted-foreground"
              )}
            >
              <Calendar className="h-3 w-3" />
              <span>{formatDueDate(task.due_date)}</span>
            </div>
          )}

          {task.tags.length > 0 && (
            <div className="flex items-center gap-1">
              {task.tags.slice(0, 2).map((tag) => (
                <span
                  key={tag}
                  className="px-1.5 py-0.5 text-[10px] bg-muted rounded text-muted-foreground"
                >
                  {tag}
                </span>
              ))}
              {task.tags.length > 2 && (
                <span className="text-[10px] text-muted-foreground">
                  +{task.tags.length - 2}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
