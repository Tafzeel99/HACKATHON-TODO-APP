"use client";

import { useState, useEffect } from "react";
import {
  Filter,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  AlertCircle,
  X,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { SearchInput } from "./search-input";
import { TagInput } from "./tag-input";
import { DatePicker } from "./date-picker";
import { taskApi } from "@/lib/api";
import type { TaskFilters as TaskFiltersType, Priority, TaskSortField } from "@/types/task";

interface TaskFiltersProps {
  filters: TaskFiltersType;
  onFiltersChange: (filters: TaskFiltersType) => void;
  disabled?: boolean;
}

export function TaskFilters({
  filters,
  onFiltersChange,
  disabled = false,
}: TaskFiltersProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  useEffect(() => {
    taskApi.getTags().then((res) => setAvailableTags(res.tags)).catch(() => {});
  }, []);

  const handleChange = <K extends keyof TaskFiltersType>(
    key: K,
    value: TaskFiltersType[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const handleClearFilters = () => {
    onFiltersChange({
      status: "all",
      sort: "created",
      order: "desc",
      priority: "all",
      tags: [],
      search: "",
      due_before: undefined,
      due_after: undefined,
      overdue_only: false,
    });
  };

  const hasActiveFilters =
    filters.priority !== "all" ||
    (filters.tags && filters.tags.length > 0) ||
    filters.search ||
    filters.due_before ||
    filters.due_after ||
    filters.overdue_only;

  return (
    <div className="space-y-3">
      {/* Main filters row */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Search */}
        <SearchInput
          value={filters.search || ""}
          onChange={(value) => handleChange("search", value || undefined)}
          disabled={disabled}
          className="w-[200px]"
        />

        {/* Status Filter */}
        <Select
          value={filters.status}
          onValueChange={(value) => handleChange("status", value as TaskFiltersType["status"])}
          disabled={disabled}
        >
          <SelectTrigger className="w-[130px] h-9 text-sm bg-background border-border/50">
            <Filter className="h-3.5 w-3.5 mr-2 text-muted-foreground" />
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tasks</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>

        {/* Priority Filter */}
        <Select
          value={filters.priority || "all"}
          onValueChange={(value) =>
            handleChange("priority", value as Priority | "all")
          }
          disabled={disabled}
        >
          <SelectTrigger className="w-[120px] h-9 text-sm bg-background border-border/50">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priority</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>

        {/* Sort By */}
        <Select
          value={filters.sort}
          onValueChange={(value) => handleChange("sort", value as TaskSortField)}
          disabled={disabled}
        >
          <SelectTrigger className="w-[130px] h-9 text-sm bg-background border-border/50">
            <ArrowUpDown className="h-3.5 w-3.5 mr-2 text-muted-foreground" />
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created">Date Created</SelectItem>
            <SelectItem value="title">Title</SelectItem>
            <SelectItem value="priority">Priority</SelectItem>
            <SelectItem value="due_date">Due Date</SelectItem>
          </SelectContent>
        </Select>

        {/* Order */}
        <Select
          value={filters.order}
          onValueChange={(value) =>
            handleChange("order", value as TaskFiltersType["order"])
          }
          disabled={disabled}
        >
          <SelectTrigger className="w-[110px] h-9 text-sm bg-background border-border/50">
            {filters.order === "desc" ? (
              <ArrowDown className="h-3.5 w-3.5 mr-2 text-muted-foreground" />
            ) : (
              <ArrowUp className="h-3.5 w-3.5 mr-2 text-muted-foreground" />
            )}
            <SelectValue placeholder="Order" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Newest</SelectItem>
            <SelectItem value="asc">Oldest</SelectItem>
          </SelectContent>
        </Select>

        {/* Toggle advanced filters */}
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-muted-foreground hover:text-foreground"
        >
          {showAdvanced ? (
            <>
              <ChevronUp className="h-4 w-4 mr-1" />
              Less
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4 mr-1" />
              More
            </>
          )}
        </Button>

        {/* Clear filters button */}
        {hasActiveFilters && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleClearFilters}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4 mr-1" />
            Clear filters
          </Button>
        )}
      </div>

      {/* Advanced filters */}
      {showAdvanced && (
        <div className="flex flex-wrap items-end gap-4 pt-3 border-t">
          {/* Tags filter */}
          <div className="space-y-1.5 min-w-[200px]">
            <Label className="text-xs text-muted-foreground">Tags</Label>
            <TagInput
              value={filters.tags || []}
              onChange={(tags) => handleChange("tags", tags)}
              suggestions={availableTags}
              disabled={disabled}
              placeholder="Filter by tags..."
            />
          </div>

          {/* Due date range */}
          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Due After</Label>
            <DatePicker
              value={filters.due_after || null}
              onChange={(date) => handleChange("due_after", date || undefined)}
              disabled={disabled}
              className="w-[160px]"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Due Before</Label>
            <DatePicker
              value={filters.due_before || null}
              onChange={(date) => handleChange("due_before", date || undefined)}
              disabled={disabled}
              className="w-[160px]"
            />
          </div>

          {/* Overdue only toggle */}
          <div className="flex items-center gap-2 h-9">
            <Checkbox
              id="overdue-only"
              checked={filters.overdue_only || false}
              onCheckedChange={(checked) =>
                handleChange("overdue_only", checked as boolean)
              }
              disabled={disabled}
            />
            <Label
              htmlFor="overdue-only"
              className="text-sm flex items-center gap-1.5 cursor-pointer"
            >
              <AlertCircle className="h-3.5 w-3.5 text-red-500" />
              Overdue only
            </Label>
          </div>
        </div>
      )}
    </div>
  );
}
