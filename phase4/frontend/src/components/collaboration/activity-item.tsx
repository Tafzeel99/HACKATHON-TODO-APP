"use client";

import {
  CheckCircle2,
  Edit2,
  MessageSquare,
  Plus,
  Share2,
  Trash2,
  UserPlus,
  XCircle,
} from "lucide-react";
import { formatDistanceToNow } from "@/lib/utils";
import { UserAvatar } from "./user-avatar";
import type { Activity } from "@/types/task";

interface ActivityItemProps {
  activity: Activity;
  showTaskTitle?: boolean;
}

const actionConfig: Record<
  string,
  {
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    label: (details: Record<string, unknown>, taskTitle?: string) => string;
  }
> = {
  created: {
    icon: Plus,
    color: "text-green-500",
    label: (_, taskTitle) => `created task "${taskTitle}"`,
  },
  updated: {
    icon: Edit2,
    color: "text-blue-500",
    label: (_, taskTitle) => `updated task "${taskTitle}"`,
  },
  completed: {
    icon: CheckCircle2,
    color: "text-emerald-500",
    label: (_, taskTitle) => `completed task "${taskTitle}"`,
  },
  uncompleted: {
    icon: XCircle,
    color: "text-amber-500",
    label: (_, taskTitle) => `reopened task "${taskTitle}"`,
  },
  deleted: {
    icon: Trash2,
    color: "text-red-500",
    label: (details) => `deleted task "${details.title || "Unknown"}"`,
  },
  shared: {
    icon: Share2,
    color: "text-purple-500",
    label: (details, taskTitle) =>
      `shared task "${taskTitle}" with ${details.shared_with_email || "someone"}`,
  },
  unshared: {
    icon: Share2,
    color: "text-gray-500",
    label: (_, taskTitle) => `removed sharing for task "${taskTitle}"`,
  },
  commented: {
    icon: MessageSquare,
    color: "text-indigo-500",
    label: (details, taskTitle) =>
      `commented on task "${taskTitle}": "${
        (details.content_preview as string)?.slice(0, 50) || "..."
      }"`,
  },
  assigned: {
    icon: UserPlus,
    color: "text-cyan-500",
    label: (details, taskTitle) =>
      `assigned task "${taskTitle}" to ${details.assigned_to_email || "someone"}`,
  },
  unassigned: {
    icon: UserPlus,
    color: "text-gray-500",
    label: (_, taskTitle) => `unassigned task "${taskTitle}"`,
  },
};

export function ActivityItem({ activity, showTaskTitle = true }: ActivityItemProps) {
  const config = actionConfig[activity.action_type] || {
    icon: Edit2,
    color: "text-muted-foreground",
    label: () => `performed action on task`,
  };

  const Icon = config.icon;
  const taskTitle = showTaskTitle
    ? activity.task_title || "Unknown task"
    : undefined;

  return (
    <div className="flex items-start gap-3 py-3">
      <div className="relative">
        <UserAvatar user={activity.user} size="sm" showTooltip={false} />
        <div
          className={`absolute -bottom-1 -right-1 p-0.5 rounded-full bg-background ${config.color}`}
        >
          <Icon className="h-3 w-3" />
        </div>
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm">
          <span className="font-medium">
            {activity.user.name || activity.user.email}
          </span>{" "}
          <span className="text-muted-foreground">
            {config.label(activity.details, taskTitle)}
          </span>
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">
          {formatDistanceToNow(activity.created_at)}
        </p>
      </div>
    </div>
  );
}
