"use client";

import { cn } from "@/lib/utils";
import type { Priority } from "@/types/task";

interface PriorityBadgeProps {
  priority: Priority;
  size?: "sm" | "md";
  className?: string;
}

const priorityConfig: Record<
  Priority,
  { label: string; bgClass: string; textClass: string }
> = {
  low: {
    label: "Low",
    bgClass: "bg-blue-100 dark:bg-blue-900/30",
    textClass: "text-blue-700 dark:text-blue-300",
  },
  medium: {
    label: "Medium",
    bgClass: "bg-amber-100 dark:bg-amber-900/30",
    textClass: "text-amber-700 dark:text-amber-300",
  },
  high: {
    label: "High",
    bgClass: "bg-red-100 dark:bg-red-900/30",
    textClass: "text-red-700 dark:text-red-300",
  },
};

export function PriorityBadge({
  priority,
  size = "sm",
  className,
}: PriorityBadgeProps) {
  const config = priorityConfig[priority];

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full font-medium",
        config.bgClass,
        config.textClass,
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm",
        className
      )}
    >
      {config.label}
    </span>
  );
}
