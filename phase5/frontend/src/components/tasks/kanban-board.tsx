"use client";

import { useState, useCallback } from "react";
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragEndEvent,
  DragOverEvent,
} from "@dnd-kit/core";
import { sortableKeyboardCoordinates } from "@dnd-kit/sortable";
import { Task, BoardStatus } from "@/types/task";
import { KanbanColumn } from "./kanban-column";
import { KanbanCard } from "./kanban-card";

interface KanbanBoardProps {
  tasks: Task[];
  onTaskMove: (taskId: string, newStatus: BoardStatus, newIndex: number) => void;
  onTaskClick?: (task: Task) => void;
  onTaskComplete?: (task: Task) => void;
  onTaskDelete?: (task: Task) => void;
  isLoading?: boolean;
}

const COLUMNS: { id: BoardStatus; title: string; color: string }[] = [
  { id: "todo", title: "To Do", color: "bg-slate-500" },
  { id: "in_progress", title: "In Progress", color: "bg-blue-500" },
  { id: "done", title: "Done", color: "bg-green-500" },
];

export function KanbanBoard({
  tasks,
  onTaskMove,
  onTaskClick,
  onTaskComplete,
  onTaskDelete,
  isLoading = false,
}: KanbanBoardProps) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Group tasks by board status
  const tasksByColumn = COLUMNS.reduce(
    (acc, column) => {
      acc[column.id] = tasks
        .filter((task) => task.board_status === column.id)
        .sort((a, b) => (a.position ?? 0) - (b.position ?? 0));
      return acc;
    },
    {} as Record<BoardStatus, Task[]>
  );

  const handleDragStart = useCallback((event: DragStartEvent) => {
    const { active } = event;
    const task = tasks.find((t) => t.id === active.id);
    if (task) {
      setActiveTask(task);
    }
  }, [tasks]);

  const handleDragOver = useCallback((event: DragOverEvent) => {
    // Optional: Add visual feedback when dragging over columns
  }, []);

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      setActiveTask(null);

      if (!over) return;

      const taskId = active.id as string;
      const overId = over.id as string;

      // Determine the target column
      let targetColumn: BoardStatus;
      let targetIndex: number;

      // Check if dropped on a column
      if (COLUMNS.some((col) => col.id === overId)) {
        targetColumn = overId as BoardStatus;
        targetIndex = tasksByColumn[targetColumn].length;
      } else {
        // Dropped on a task - find its column
        const overTask = tasks.find((t) => t.id === overId);
        if (!overTask) return;

        targetColumn = overTask.board_status;
        targetIndex = tasksByColumn[targetColumn].findIndex(
          (t) => t.id === overId
        );
      }

      // Get the dragged task
      const draggedTask = tasks.find((t) => t.id === taskId);
      if (!draggedTask) return;

      // Check if actually moved
      if (
        draggedTask.board_status === targetColumn &&
        draggedTask.position === targetIndex
      ) {
        return;
      }

      onTaskMove(taskId, targetColumn, targetIndex);
    },
    [tasks, tasksByColumn, onTaskMove]
  );

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
        {COLUMNS.map((column) => (
          <div
            key={column.id}
            className="bg-muted/30 rounded-xl p-4 min-h-[400px] animate-pulse"
          >
            <div className="h-6 w-24 bg-muted rounded mb-4" />
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 bg-muted rounded-lg" />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 min-h-[500px]">
        {COLUMNS.map((column) => (
          <KanbanColumn
            key={column.id}
            id={column.id}
            title={column.title}
            color={column.color}
            tasks={tasksByColumn[column.id]}
            onTaskClick={onTaskClick}
            onTaskComplete={onTaskComplete}
            onTaskDelete={onTaskDelete}
          />
        ))}
      </div>

      <DragOverlay>
        {activeTask && (
          <KanbanCard
            task={activeTask}
            isDragging
          />
        )}
      </DragOverlay>
    </DndContext>
  );
}
