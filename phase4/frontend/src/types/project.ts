/**
 * Project type definitions for the Todo application.
 */

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  color: string;
  icon: string | null;
  is_default: boolean;
  position: number;
  created_at: string;
  updated_at: string;
  task_count: number;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
  color?: string;
  icon?: string | null;
}

export interface ProjectUpdate {
  name?: string;
  description?: string | null;
  color?: string;
  icon?: string | null;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

export interface UserPreferences {
  user_id: string;
  accent_color: AccentColor;
  email_reminders: boolean;
  email_daily_digest: boolean;
  reminder_time: string;
  dashboard_layout: Record<string, DashboardWidget>;
  motivational_quotes: boolean;
  default_view: ViewMode;
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreferencesUpdate {
  accent_color?: AccentColor;
  email_reminders?: boolean;
  email_daily_digest?: boolean;
  reminder_time?: string;
  dashboard_layout?: Record<string, DashboardWidget>;
  motivational_quotes?: boolean;
  default_view?: ViewMode;
  timezone?: string;
}

export interface DashboardWidget {
  id: string;
  visible: boolean;
  position: { x: number; y: number; w: number; h: number };
}

export type AccentColor =
  | "indigo"
  | "purple"
  | "blue"
  | "green"
  | "orange"
  | "pink"
  | "red"
  | "teal";

export type ViewMode = "list" | "grid" | "kanban";

export type BoardStatus = "todo" | "in_progress" | "done";

export const ACCENT_COLORS: Record<AccentColor, { name: string; value: string }> = {
  indigo: { name: "Indigo", value: "#6366f1" },
  purple: { name: "Purple", value: "#8b5cf6" },
  blue: { name: "Blue", value: "#3b82f6" },
  green: { name: "Green", value: "#22c55e" },
  orange: { name: "Orange", value: "#f97316" },
  pink: { name: "Pink", value: "#ec4899" },
  red: { name: "Red", value: "#ef4444" },
  teal: { name: "Teal", value: "#14b8a6" },
};

export const TASK_COLORS = [
  "#ef4444", // Red
  "#f97316", // Orange
  "#eab308", // Yellow
  "#22c55e", // Green
  "#14b8a6", // Teal
  "#3b82f6", // Blue
  "#6366f1", // Indigo
  "#8b5cf6", // Purple
];
