"use client";

import { cn } from "@/lib/utils";
import type { Priority } from "@/types/task";

interface PriorityBadgeProps {
  priority: Priority;
  size?: "sm" | "md";
  className?: string;
}

// Minimal Tech priority config - clean with border accents
const priorityConfig: Record<
  Priority,
  { label: string; classes: string }
> = {
  low: {
    label: "Low",
    classes: "bg-muted/50 text-muted-foreground border border-border/50",
  },
  medium: {
    label: "Medium",
    classes: "bg-warning/10 text-warning border border-warning/25",
  },
  high: {
    label: "High",
    classes: "bg-destructive/10 text-destructive border border-destructive/25",
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
        "inline-flex items-center rounded font-semibold tracking-wide uppercase",
        config.classes,
        size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-1 text-xs",
        className
      )}
    >
      {config.label}
    </span>
  );
}
