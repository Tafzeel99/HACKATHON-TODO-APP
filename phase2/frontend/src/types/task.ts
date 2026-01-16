/**
 * Task TypeScript types matching backend Pydantic schemas.
 */

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export type TaskStatus = "all" | "pending" | "completed";
export type TaskSortField = "created" | "title";
export type SortOrder = "asc" | "desc";

export interface TaskFilters {
  status: TaskStatus;
  sort: TaskSortField;
  order: SortOrder;
}
