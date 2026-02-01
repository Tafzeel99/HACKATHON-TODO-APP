"use client";

import { useDroppable } from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { Task, BoardStatus } from "@/types/task";
import { KanbanCard } from "./kanban-card";
import { cn } from "@/lib/utils";

interface KanbanColumnProps {
  id: BoardStatus;
  title: string;
  color: string;
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
  onTaskComplete?: (task: Task) => void;
  onTaskDelete?: (task: Task) => void;
}

export function KanbanColumn({
  id,
  title,
  color,
  tasks,
  onTaskClick,
  onTaskComplete,
  onTaskDelete,
}: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id,
  });

  return (
    <div
      ref={setNodeRef}
      className={cn(
        "flex flex-col bg-muted/30 rounded-xl transition-all duration-200",
        isOver && "kanban-column-over"
      )}
    >
      {/* Column Header */}
      <div className="flex items-center gap-2 p-4 pb-2">
        <div className={cn("w-3 h-3 rounded-full", color)} />
        <h3 className="font-semibold text-foreground">{title}</h3>
        <span className="ml-auto text-sm text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
          {tasks.length}
        </span>
      </div>

      {/* Tasks Container */}
      <div className="flex-1 p-2 pt-0 overflow-y-auto">
        <SortableContext
          items={tasks.map((t) => t.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-2 min-h-[100px]">
            {tasks.length === 0 ? (
              <div className="flex items-center justify-center h-24 text-muted-foreground text-sm border-2 border-dashed border-muted rounded-lg">
                Drop tasks here
              </div>
            ) : (
              tasks.map((task) => (
                <KanbanCard
                  key={task.id}
                  task={task}
                  onClick={() => onTaskClick?.(task)}
                  onComplete={() => onTaskComplete?.(task)}
                  onDelete={() => onTaskDelete?.(task)}
                />
              ))
            )}
          </div>
        </SortableContext>
      </div>
    </div>
  );
}
