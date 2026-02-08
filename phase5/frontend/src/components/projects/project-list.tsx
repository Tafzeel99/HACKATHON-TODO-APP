"use client";

import { useState } from "react";
import { Plus, FolderOpen, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { Project } from "@/types/project";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ProjectForm } from "./project-form";

interface ProjectListProps {
  projects: Project[];
  selectedProjectId: string | null;
  onSelectProject: (projectId: string | null) => void;
  onCreateProject: (project: { name: string; description?: string; color: string; icon?: string }) => void;
  onUpdateProject: (projectId: string, data: { name?: string; description?: string; color?: string; icon?: string }) => void;
  onDeleteProject: (projectId: string) => void;
  isLoading?: boolean;
}

export function ProjectList({
  projects,
  selectedProjectId,
  onSelectProject,
  onCreateProject,
  onUpdateProject,
  onDeleteProject,
  isLoading = false,
}: ProjectListProps) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-2 p-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-10 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {/* All Tasks option */}
      <button
        onClick={() => onSelectProject(null)}
        className={cn(
          "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
          selectedProjectId === null
            ? "bg-primary/10 text-primary font-medium"
            : "text-muted-foreground hover:bg-muted hover:text-foreground"
        )}
      >
        <FolderOpen className="h-4 w-4" />
        <span className="flex-1 text-left">All Tasks</span>
      </button>

      {/* Project items */}
      {projects.map((project) => (
        <div
          key={project.id}
          className={cn(
            "group flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer",
            selectedProjectId === project.id
              ? "bg-primary/10 text-primary font-medium"
              : "text-muted-foreground hover:bg-muted hover:text-foreground"
          )}
          onClick={() => onSelectProject(project.id)}
        >
          {/* Color dot or icon */}
          <div
            className="w-3 h-3 rounded-full shrink-0"
            style={{ backgroundColor: project.color }}
          />

          {/* Project name */}
          <span className="flex-1 truncate">{project.name}</span>

          {/* Task count */}
          <span className="text-xs text-muted-foreground">
            {project.task_count}
          </span>

          {/* Actions menu */}
          {!project.is_default && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingProject(project);
                  }}
                >
                  <Pencil className="h-4 w-4 mr-2" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteProject(project.id);
                  }}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      ))}

      {/* Add project button */}
      <button
        onClick={() => setShowCreateForm(true)}
        className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
      >
        <Plus className="h-4 w-4" />
        <span>Add Project</span>
      </button>

      {/* Create project form */}
      <ProjectForm
        open={showCreateForm}
        onOpenChange={setShowCreateForm}
        onSubmit={(data) => {
          onCreateProject(data);
          setShowCreateForm(false);
        }}
      />

      {/* Edit project form */}
      {editingProject && (
        <ProjectForm
          open={!!editingProject}
          onOpenChange={(open) => !open && setEditingProject(null)}
          project={editingProject}
          onSubmit={(data) => {
            onUpdateProject(editingProject.id, data);
            setEditingProject(null);
          }}
        />
      )}
    </div>
  );
}
