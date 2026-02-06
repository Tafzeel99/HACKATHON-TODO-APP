/**
 * Task TypeScript types matching backend Pydantic schemas.
 */

export type Priority = "low" | "medium" | "high";
export type RecurrencePattern = "none" | "daily" | "weekly" | "monthly";
export type BoardStatus = "todo" | "in_progress" | "done";

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
  // Organization fields
  project_id: string | null;
  pinned: boolean;
  archived: boolean;
  color: string | null;
  board_status: BoardStatus;
  position: number | null;
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
  // Organization fields
  project_id?: string;
  color?: string;
  board_status?: BoardStatus;
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
  // Organization fields
  project_id?: string;
  pinned?: boolean;
  archived?: boolean;
  color?: string;
  board_status?: BoardStatus;
  position?: number;
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
  // Organization filters
  project_id?: string;
  archived?: boolean;
  board_status?: BoardStatus;
  pinned?: boolean;
}

export interface TaskReorder {
  task_ids: string[];
  board_status?: BoardStatus;
}

export interface BulkArchive {
  task_ids?: string[];
  archive: boolean;
}

/**
 * User interface for collaboration features.
 */
export interface User {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

/**
 * Task share for collaboration.
 */
export interface TaskShare {
  id: string;
  task_id: string;
  owner_id: string;
  shared_with: User;
  permission: "view" | "edit";
  created_at: string;
}

export interface TaskShareCreate {
  user_email: string;
  permission: "view" | "edit";
}

export interface TaskShareListResponse {
  shares: TaskShare[];
  total: number;
}

/**
 * Comment interface for task discussions.
 */
export interface Comment {
  id: string;
  task_id: string;
  user: User;
  parent_id: string | null;
  content: string;
  created_at: string;
  updated_at: string;
  replies: Comment[];
}

export interface CommentCreate {
  content: string;
  parent_id?: string;
}

export interface CommentListResponse {
  comments: Comment[];
  total: number;
}

/**
 * Activity type for tracking task changes.
 */
export type ActionType =
  | "created"
  | "updated"
  | "completed"
  | "uncompleted"
  | "deleted"
  | "shared"
  | "unshared"
  | "commented"
  | "assigned"
  | "unassigned";

export interface Activity {
  id: string;
  task_id: string | null;
  user: User;
  action_type: ActionType;
  details: Record<string, unknown>;
  created_at: string;
  task_title: string | null;
}

export interface ActivityListResponse {
  activities: Activity[];
  total: number;
}

export interface UserSearchResponse {
  users: User[];
  total: number;
}
