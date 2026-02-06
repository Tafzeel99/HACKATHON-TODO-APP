"use client";

import { useEffect, useState } from "react";
import { Activity as ActivityIcon, Loader2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ActivityItem } from "./activity-item";
import { ActivityFeedSkeleton } from "@/components/skeletons";
import { activityApi } from "@/lib/api";
import type { Activity } from "@/types/task";

interface ActivityFeedProps {
  taskId?: string;
  limit?: number;
  maxHeight?: string;
  showTaskTitle?: boolean;
}

export function ActivityFeed({
  taskId,
  limit = 20,
  maxHeight = "400px",
  showTaskTitle = true,
}: ActivityFeedProps) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchActivities = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = taskId
          ? await activityApi.getTaskActivities(taskId, limit)
          : await activityApi.getActivities(limit);
        setActivities(response.activities);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load activities");
      } finally {
        setIsLoading(false);
      }
    };

    fetchActivities();
  }, [taskId, limit]);

  if (isLoading) {
    return <ActivityFeedSkeleton count={5} />;
  }

  if (error) {
    return (
      <div className="text-center py-8 text-sm text-muted-foreground">
        <p>{error}</p>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-sm text-muted-foreground">
        <ActivityIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No activity yet</p>
      </div>
    );
  }

  return (
    <ScrollArea style={{ maxHeight }}>
      <div className="space-y-0 divide-y">
        {activities.map((activity) => (
          <ActivityItem
            key={activity.id}
            activity={activity}
            showTaskTitle={showTaskTitle}
          />
        ))}
      </div>
    </ScrollArea>
  );
}

interface TaskActivityFeedProps {
  taskId: string;
  limit?: number;
  maxHeight?: string;
}

export function TaskActivityFeed({
  taskId,
  limit = 20,
  maxHeight = "300px",
}: TaskActivityFeedProps) {
  return (
    <ActivityFeed
      taskId={taskId}
      limit={limit}
      maxHeight={maxHeight}
      showTaskTitle={false}
    />
  );
}
