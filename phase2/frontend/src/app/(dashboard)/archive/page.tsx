"use client";

import { useState, useEffect } from "react";
import { Archive, ArchiveRestore, Search, Trash2 } from "lucide-react";
import { Task } from "@/types/task";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";

// Mock data for demonstration
const MOCK_ARCHIVED_TASKS: Task[] = [
  {
    id: "archived-1",
    user_id: "user-1",
    title: "Old project research",
    description: "Research completed last month",
    completed: true,
    created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    priority: "medium",
    tags: ["research", "completed"],
    due_date: null,
    recurrence_pattern: "none",
    recurrence_end_date: null,
    parent_task_id: null,
    reminder_at: null,
    is_overdue: false,
    project_id: null,
    pinned: false,
    archived: true,
    color: "#6366f1",
    board_status: "done",
    position: 0,
  },
  {
    id: "archived-2",
    user_id: "user-1",
    title: "Q4 planning documents",
    description: "Completed Q4 planning",
    completed: true,
    created_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
    priority: "high",
    tags: ["planning", "quarterly"],
    due_date: null,
    recurrence_pattern: "none",
    recurrence_end_date: null,
    parent_task_id: null,
    reminder_at: null,
    is_overdue: false,
    project_id: null,
    pinned: false,
    archived: true,
    color: "#22c55e",
    board_status: "done",
    position: 1,
  },
];

export default function ArchivePage() {
  const [tasks, setTasks] = useState<Task[]>(MOCK_ARCHIVED_TASKS);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const filteredTasks = tasks.filter(
    (task) =>
      task.title.toLowerCase().includes(search.toLowerCase()) ||
      task.description?.toLowerCase().includes(search.toLowerCase()) ||
      task.tags.some((tag) => tag.toLowerCase().includes(search.toLowerCase()))
  );

  const handleRestore = async (taskId: string) => {
    // In real implementation, call API
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
    toast({
      title: "Task restored",
      description: "The task has been moved back to your task list.",
    });
  };

  const handleDelete = async (taskId: string) => {
    // In real implementation, call API
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
    toast({
      title: "Task deleted",
      description: "The task has been permanently deleted.",
      variant: "destructive",
    });
  };

  const handleDeleteAll = async () => {
    // In real implementation, call API
    setTasks([]);
    toast({
      title: "Archive cleared",
      description: "All archived tasks have been permanently deleted.",
      variant: "destructive",
    });
  };

  return (
    <div className="container mx-auto py-6 px-4 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-muted">
            <Archive className="h-6 w-6 text-muted-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">Archive</h1>
            <p className="text-sm text-muted-foreground">
              {tasks.length} archived task{tasks.length !== 1 ? "s" : ""}
            </p>
          </div>
        </div>

        {tasks.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleDeleteAll}
            className="text-destructive hover:text-destructive"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete All
          </Button>
        )}
      </div>

      {/* Search */}
      {tasks.length > 0 && (
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search archived tasks..."
            className="pl-10"
          />
        </div>
      )}

      {/* Task list */}
      {filteredTasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Archive className="h-16 w-16 text-muted-foreground/30 mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">
            {search ? "No matching tasks" : "Archive is empty"}
          </h3>
          <p className="text-sm text-muted-foreground max-w-md">
            {search
              ? "Try a different search term"
              : "Completed tasks that you archive will appear here. You can restore them at any time."}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className="relative flex items-start gap-4 p-4 rounded-xl border border-border bg-card hover:border-primary/20 transition-colors"
            >
              {/* Color indicator */}
              {task.color && (
                <div
                  className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
                  style={{ backgroundColor: task.color }}
                />
              )}

              {/* Content */}
              <div className="flex-1 min-w-0 pl-2">
                <h3 className="font-medium text-foreground line-through opacity-70">
                  {task.title}
                </h3>
                {task.description && (
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                    {task.description}
                  </p>
                )}
                <div className="flex items-center gap-2 mt-2">
                  {task.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 text-xs bg-muted rounded text-muted-foreground"
                    >
                      {tag}
                    </span>
                  ))}
                  <span className="text-xs text-muted-foreground">
                    Archived {new Date(task.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRestore(task.id)}
                  title="Restore task"
                >
                  <ArchiveRestore className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(task.id)}
                  className="text-destructive hover:text-destructive"
                  title="Delete permanently"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
