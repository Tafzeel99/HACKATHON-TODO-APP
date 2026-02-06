"use client";

import { useState } from "react";
import { Check, Palette } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { TASK_COLORS } from "@/types/project";

interface TaskColorPickerProps {
  value: string | null;
  onChange: (color: string | null) => void;
  className?: string;
}

export function TaskColorPicker({
  value,
  onChange,
  className,
}: TaskColorPickerProps) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className={cn("h-8 w-8 p-0", className)}
          title="Set task color"
        >
          {value ? (
            <div
              className="h-4 w-4 rounded-full ring-2 ring-offset-2 ring-offset-background"
              style={{ backgroundColor: value }}
            />
          ) : (
            <Palette className="h-4 w-4 text-muted-foreground" />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-3" align="start">
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground">Task Color</p>
          <div className="flex flex-wrap gap-2">
            {/* No color option */}
            <button
              onClick={() => {
                onChange(null);
                setOpen(false);
              }}
              className={cn(
                "color-picker-item",
                "border-2 border-dashed border-muted-foreground/30",
                "flex items-center justify-center",
                value === null && "ring-primary"
              )}
              title="No color"
            >
              {value === null && (
                <Check className="h-4 w-4 text-muted-foreground" />
              )}
            </button>

            {/* Color options */}
            {TASK_COLORS.map((color) => (
              <button
                key={color}
                onClick={() => {
                  onChange(color);
                  setOpen(false);
                }}
                className={cn(
                  "color-picker-item",
                  value === color && "selected"
                )}
                style={{ backgroundColor: color }}
                title={color}
              >
                {value === color && (
                  <Check className="h-4 w-4 text-white drop-shadow-md" />
                )}
              </button>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Inline color indicator for task cards
export function TaskColorIndicator({
  color,
  className,
}: {
  color: string | null;
  className?: string;
}) {
  if (!color) return null;

  return (
    <div
      className={cn("task-color-indicator", className)}
      style={{ backgroundColor: color }}
    />
  );
}
