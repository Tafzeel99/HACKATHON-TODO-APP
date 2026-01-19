/**
 * Task TypeScript types matching backend Pydantic schemas.
 */

export type Priority = "low" | "medium" | "high";
export type RecurrencePattern = "none" | "daily" | "weekly" | "monthly";

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  priority: Priority;
  tags: string[];
  due_date: string | null;
  recurrence_pattern: RecurrencePattern;
  recurrence_end_date: string | null;
  parent_task_id: string | null;
  reminder_at: string | null;
  is_overdue: boolean;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: Priority;
  tags?: string[];
  due_date?: string;
  recurrence_pattern?: RecurrencePattern;
  recurrence_end_date?: string;
  reminder_at?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: Priority;
  tags?: string[];
  due_date?: string;
  recurrence_pattern?: RecurrencePattern;
  recurrence_end_date?: string;
  reminder_at?: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export interface TagsResponse {
  tags: string[];
}

export type TaskStatus = "all" | "pending" | "completed";
export type TaskSortField = "created" | "title" | "priority" | "due_date";
export type SortOrder = "asc" | "desc";

export interface TaskFilters {
  status: TaskStatus;
  sort: TaskSortField;
  order: SortOrder;
  priority?: Priority | "all";
  tags?: string[];
  search?: string;
  due_before?: string;
  due_after?: string;
  overdue_only?: boolean;
}
