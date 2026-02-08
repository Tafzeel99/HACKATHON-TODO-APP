"use client";

import { useState, useEffect } from "react";
import { Check } from "lucide-react";
import { Project, TASK_COLORS } from "@/types/project";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface ProjectFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  project?: Project;
  onSubmit: (data: {
    name: string;
    description?: string;
    color: string;
    icon?: string;
  }) => void;
}

const PROJECT_COLORS = [
  "#6366f1", // Indigo
  "#8b5cf6", // Purple
  "#3b82f6", // Blue
  "#06b6d4", // Cyan
  "#14b8a6", // Teal
  "#22c55e", // Green
  "#eab308", // Yellow
  "#f97316", // Orange
  "#ef4444", // Red
  "#ec4899", // Pink
  "#6b7280", // Gray
  "#1f2937", // Dark
];

export function ProjectForm({
  open,
  onOpenChange,
  project,
  onSubmit,
}: ProjectFormProps) {
  const [name, setName] = useState(project?.name || "");
  const [description, setDescription] = useState(project?.description || "");
  const [color, setColor] = useState(project?.color || PROJECT_COLORS[0]);

  // Reset form when project changes
  useEffect(() => {
    if (project) {
      setName(project.name);
      setDescription(project.description || "");
      setColor(project.color);
    } else {
      setName("");
      setDescription("");
      setColor(PROJECT_COLORS[0]);
    }
  }, [project, open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    onSubmit({
      name: name.trim(),
      description: description.trim() || undefined,
      color,
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {project ? "Edit Project" : "Create Project"}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Project name"
              maxLength={100}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description"
              rows={2}
              maxLength={500}
            />
          </div>

          <div className="space-y-2">
            <Label>Color</Label>
            <div className="flex flex-wrap gap-2">
              {PROJECT_COLORS.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setColor(c)}
                  className={cn(
                    "w-8 h-8 rounded-full transition-all duration-200",
                    "ring-2 ring-offset-2 ring-offset-background",
                    color === c ? "ring-primary scale-110" : "ring-transparent hover:scale-105"
                  )}
                  style={{ backgroundColor: c }}
                >
                  {color === c && (
                    <Check className="h-4 w-4 text-white mx-auto" />
                  )}
                </button>
              ))}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={!name.trim()}>
              {project ? "Save Changes" : "Create Project"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
