"use client";

import { useState } from "react";
import { Check, ChevronsUpDown, FolderOpen, Plus } from "lucide-react";
import { Project } from "@/types/project";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface ProjectSelectorProps {
  projects: Project[];
  value: string | null;
  onChange: (projectId: string | null) => void;
  onCreateNew?: () => void;
  placeholder?: string;
  className?: string;
  showAllOption?: boolean;
}

export function ProjectSelector({
  projects,
  value,
  onChange,
  onCreateNew,
  placeholder = "Select project",
  className,
  showAllOption = false,
}: ProjectSelectorProps) {
  const [open, setOpen] = useState(false);

  const selectedProject = projects.find((p) => p.id === value);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("justify-between", className)}
        >
          <div className="flex items-center gap-2">
            {selectedProject ? (
              <>
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: selectedProject.color }}
                />
                <span className="truncate">{selectedProject.name}</span>
              </>
            ) : value === null && showAllOption ? (
              <>
                <FolderOpen className="h-4 w-4 text-muted-foreground" />
                <span>All Tasks</span>
              </>
            ) : (
              <span className="text-muted-foreground">{placeholder}</span>
            )}
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Search projects..." />
          <CommandEmpty>No project found.</CommandEmpty>
          <CommandGroup>
            {showAllOption && (
              <CommandItem
                value="all-tasks"
                onSelect={() => {
                  onChange(null);
                  setOpen(false);
                }}
              >
                <FolderOpen className="mr-2 h-4 w-4" />
                All Tasks
                {value === null && (
                  <Check className="ml-auto h-4 w-4" />
                )}
              </CommandItem>
            )}
            {projects.map((project) => (
              <CommandItem
                key={project.id}
                value={project.name}
                onSelect={() => {
                  onChange(project.id);
                  setOpen(false);
                }}
              >
                <div
                  className="mr-2 w-3 h-3 rounded-full"
                  style={{ backgroundColor: project.color }}
                />
                <span className="flex-1 truncate">{project.name}</span>
                {value === project.id && (
                  <Check className="ml-auto h-4 w-4" />
                )}
              </CommandItem>
            ))}
          </CommandGroup>
          {onCreateNew && (
            <CommandGroup>
              <CommandItem
                onSelect={() => {
                  onCreateNew();
                  setOpen(false);
                }}
                className="text-muted-foreground"
              >
                <Plus className="mr-2 h-4 w-4" />
                Create new project
              </CommandItem>
            </CommandGroup>
          )}
        </Command>
      </PopoverContent>
    </Popover>
  );
}
