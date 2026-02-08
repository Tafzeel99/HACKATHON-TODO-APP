"use client";

import { useState } from "react";
import {
  Plus,
  FolderKanban,
  MoreHorizontal,
  Pencil,
  Trash2,
  CheckCircle2,
} from "lucide-react";
import { Project } from "@/types/project";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ProjectForm } from "@/components/projects/project-form";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

// Mock data
const MOCK_PROJECTS: Project[] = [
  {
    id: "inbox",
    user_id: "user-1",
    name: "Inbox",
    description: "Default project for uncategorized tasks",
    color: "#6b7280",
    icon: "inbox",
    is_default: true,
    position: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    task_count: 5,
  },
  {
    id: "proj-1",
    user_id: "user-1",
    name: "Work",
    description: "Work-related tasks and projects",
    color: "#6366f1",
    icon: null,
    is_default: false,
    position: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    task_count: 12,
  },
  {
    id: "proj-2",
    user_id: "user-1",
    name: "Personal",
    description: "Personal tasks and errands",
    color: "#22c55e",
    icon: null,
    is_default: false,
    position: 2,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    task_count: 8,
  },
  {
    id: "proj-3",
    user_id: "user-1",
    name: "Shopping",
    description: "Shopping lists",
    color: "#f97316",
    icon: null,
    is_default: false,
    position: 3,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    task_count: 3,
  },
];

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>(MOCK_PROJECTS);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const { toast } = useToast();

  const handleCreateProject = (data: {
    name: string;
    description?: string;
    color: string;
  }) => {
    const newProject: Project = {
      id: `proj-${Date.now()}`,
      user_id: "user-1",
      name: data.name,
      description: data.description || null,
      color: data.color,
      icon: null,
      is_default: false,
      position: projects.length,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      task_count: 0,
    };
    setProjects((prev) => [...prev, newProject]);
    toast({
      title: "Project created",
      description: `${data.name} has been created.`,
    });
  };

  const handleUpdateProject = (
    projectId: string,
    data: { name?: string; description?: string; color?: string }
  ) => {
    setProjects((prev) =>
      prev.map((p) =>
        p.id === projectId
          ? { ...p, ...data, updated_at: new Date().toISOString() }
          : p
      )
    );
    toast({
      title: "Project updated",
      description: "Your changes have been saved.",
    });
  };

  const handleDeleteProject = (projectId: string) => {
    setProjects((prev) => prev.filter((p) => p.id !== projectId));
    toast({
      title: "Project deleted",
      description: "Tasks have been moved to Inbox.",
    });
  };

  const totalTasks = projects.reduce((sum, p) => sum + p.task_count, 0);

  return (
    <div className="container mx-auto py-6 px-4 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <FolderKanban className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">Projects</h1>
            <p className="text-sm text-muted-foreground">
              {projects.length} projects, {totalTasks} tasks total
            </p>
          </div>
        </div>

        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Projects grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map((project) => (
          <div
            key={project.id}
            className={cn(
              "group relative p-5 rounded-xl border border-border bg-card",
              "hover:border-primary/30 hover:shadow-lg transition-all duration-200"
            )}
          >
            {/* Color bar */}
            <div
              className="absolute top-0 left-0 right-0 h-1 rounded-t-xl"
              style={{ backgroundColor: project.color }}
            />

            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full shrink-0"
                  style={{ backgroundColor: project.color }}
                />
                <h3 className="font-semibold text-foreground">{project.name}</h3>
                {project.is_default && (
                  <span className="px-2 py-0.5 text-xs bg-muted rounded text-muted-foreground">
                    Default
                  </span>
                )}
              </div>

              {!project.is_default && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100"
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setEditingProject(project)}>
                      <Pencil className="h-4 w-4 mr-2" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => handleDeleteProject(project.id)}
                      className="text-destructive focus:text-destructive"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>

            {/* Description */}
            {project.description && (
              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                {project.description}
              </p>
            )}

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <CheckCircle2 className="h-4 w-4" />
                <span>{project.task_count} tasks</span>
              </div>
            </div>
          </div>
        ))}

        {/* Add project card */}
        <button
          onClick={() => setShowCreateForm(true)}
          className={cn(
            "p-5 rounded-xl border-2 border-dashed border-muted",
            "hover:border-primary/50 hover:bg-primary/5 transition-colors",
            "flex flex-col items-center justify-center gap-2 min-h-[150px]"
          )}
        >
          <Plus className="h-8 w-8 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Create Project</span>
        </button>
      </div>

      {/* Create form */}
      <ProjectForm
        open={showCreateForm}
        onOpenChange={setShowCreateForm}
        onSubmit={(data) => {
          handleCreateProject(data);
          setShowCreateForm(false);
        }}
      />

      {/* Edit form */}
      {editingProject && (
        <ProjectForm
          open={!!editingProject}
          onOpenChange={(open) => !open && setEditingProject(null)}
          project={editingProject}
          onSubmit={(data) => {
            handleUpdateProject(editingProject.id, data);
            setEditingProject(null);
          }}
        />
      )}
    </div>
  );
}
