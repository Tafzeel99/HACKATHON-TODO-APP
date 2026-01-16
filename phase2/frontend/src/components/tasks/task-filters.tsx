"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";

export type StatusFilter = "all" | "pending" | "completed";
export type SortField = "created" | "title";
export type SortOrder = "asc" | "desc";

export interface TaskFilters {
  status: StatusFilter;
  sort: SortField;
  order: SortOrder;
}

interface TaskFiltersProps {
  filters: TaskFilters;
  onFiltersChange: (filters: TaskFilters) => void;
  disabled?: boolean;
}

export function TaskFilters({
  filters,
  onFiltersChange,
  disabled = false,
}: TaskFiltersProps) {
  const handleStatusChange = (value: StatusFilter) => {
    onFiltersChange({ ...filters, status: value });
  };

  const handleSortChange = (value: SortField) => {
    onFiltersChange({ ...filters, sort: value });
  };

  const handleOrderChange = (value: SortOrder) => {
    onFiltersChange({ ...filters, order: value });
  };

  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="space-y-1.5">
        <Label htmlFor="status-filter" className="text-xs text-muted-foreground">
          Status
        </Label>
        <Select
          value={filters.status}
          onValueChange={handleStatusChange}
          disabled={disabled}
        >
          <SelectTrigger id="status-filter" className="w-[130px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tasks</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="sort-field" className="text-xs text-muted-foreground">
          Sort by
        </Label>
        <Select
          value={filters.sort}
          onValueChange={handleSortChange}
          disabled={disabled}
        >
          <SelectTrigger id="sort-field" className="w-[130px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created">Date Created</SelectItem>
            <SelectItem value="title">Title</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="sort-order" className="text-xs text-muted-foreground">
          Order
        </Label>
        <Select
          value={filters.order}
          onValueChange={handleOrderChange}
          disabled={disabled}
        >
          <SelectTrigger id="sort-order" className="w-[130px]">
            <SelectValue placeholder="Order" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Newest First</SelectItem>
            <SelectItem value="asc">Oldest First</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
