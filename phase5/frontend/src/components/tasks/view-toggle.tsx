"use client";

import { LayoutList, LayoutGrid, Kanban } from "lucide-react";
import { cn } from "@/lib/utils";

export type ViewMode = "list" | "grid" | "kanban";

interface ViewToggleProps {
  value: ViewMode;
  onChange: (value: ViewMode) => void;
  className?: string;
}

const VIEW_OPTIONS: { value: ViewMode; icon: typeof LayoutList; label: string }[] = [
  { value: "list", icon: LayoutList, label: "List" },
  { value: "grid", icon: LayoutGrid, label: "Grid" },
  { value: "kanban", icon: Kanban, label: "Kanban" },
];

export function ViewToggle({ value, onChange, className }: ViewToggleProps) {
  return (
    <div className={cn("view-toggle", className)}>
      {VIEW_OPTIONS.map((option) => {
        const Icon = option.icon;
        const isActive = value === option.value;

        return (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={cn("view-toggle-item", isActive && "active")}
            title={option.label}
            aria-pressed={isActive}
          >
            <Icon className="h-4 w-4" />
          </button>
        );
      })}
    </div>
  );
}

// Hook for persisting view preference
export function useViewPreference(key: string = "task-view"): [ViewMode, (mode: ViewMode) => void] {
  const getInitialValue = (): ViewMode => {
    if (typeof window === "undefined") return "list";
    const stored = localStorage.getItem(key);
    if (stored && ["list", "grid", "kanban"].includes(stored)) {
      return stored as ViewMode;
    }
    return "list";
  };

  const value = getInitialValue();

  const setValue = (mode: ViewMode) => {
    localStorage.setItem(key, mode);
    // Force re-render by dispatching custom event
    window.dispatchEvent(new CustomEvent("view-change", { detail: mode }));
  };

  return [value, setValue];
}
