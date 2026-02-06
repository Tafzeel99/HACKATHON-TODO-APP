"use client";

import { Archive, ArchiveRestore } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

interface ArchiveButtonProps {
  archived: boolean;
  onToggle: () => void;
  disabled?: boolean;
  className?: string;
  variant?: "icon" | "button";
}

export function ArchiveButton({
  archived,
  onToggle,
  disabled = false,
  className,
  variant = "icon",
}: ArchiveButtonProps) {
  if (variant === "button") {
    return (
      <Button
        variant={archived ? "default" : "outline"}
        size="sm"
        onClick={onToggle}
        disabled={disabled}
        className={cn("gap-2", className)}
      >
        {archived ? (
          <>
            <ArchiveRestore className="h-4 w-4" />
            Restore
          </>
        ) : (
          <>
            <Archive className="h-4 w-4" />
            Archive
          </>
        )}
      </Button>
    );
  }

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggle}
          disabled={disabled}
          className={cn(
            "h-8 w-8 p-0",
            archived && "text-primary",
            className
          )}
        >
          {archived ? (
            <ArchiveRestore className="h-4 w-4" />
          ) : (
            <Archive className="h-4 w-4" />
          )}
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        {archived ? "Restore from archive" : "Archive task"}
      </TooltipContent>
    </Tooltip>
  );
}

interface BulkArchiveButtonProps {
  onArchiveCompleted: () => void;
  completedCount: number;
  disabled?: boolean;
  className?: string;
}

export function BulkArchiveButton({
  onArchiveCompleted,
  completedCount,
  disabled = false,
  className,
}: BulkArchiveButtonProps) {
  if (completedCount === 0) return null;

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={onArchiveCompleted}
      disabled={disabled}
      className={cn("gap-2", className)}
    >
      <Archive className="h-4 w-4" />
      Archive {completedCount} completed
    </Button>
  );
}
