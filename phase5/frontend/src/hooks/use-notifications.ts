"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { Task } from "@/types/task";

interface NotificationState {
  permission: NotificationPermission | "default";
  isSupported: boolean;
}

export function useNotifications() {
  const [state, setState] = useState<NotificationState>({
    permission: "default",
    isSupported: false,
  });
  const scheduledNotifications = useRef<Map<string, NodeJS.Timeout>>(new Map());

  useEffect(() => {
    const isSupported =
      typeof window !== "undefined" && "Notification" in window;

    setState({
      permission: isSupported ? Notification.permission : "default",
      isSupported,
    });
  }, []);

  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!state.isSupported) {
      return false;
    }

    if (Notification.permission === "granted") {
      setState((prev) => ({ ...prev, permission: "granted" }));
      return true;
    }

    if (Notification.permission === "denied") {
      setState((prev) => ({ ...prev, permission: "denied" }));
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      setState((prev) => ({ ...prev, permission }));
      return permission === "granted";
    } catch {
      return false;
    }
  }, [state.isSupported]);

  const showNotification = useCallback(
    (title: string, options?: NotificationOptions) => {
      if (!state.isSupported || state.permission !== "granted") {
        return null;
      }

      try {
        const notification = new Notification(title, {
          icon: "/favicon.ico",
          badge: "/favicon.ico",
          ...options,
        });

        notification.onclick = () => {
          window.focus();
          notification.close();
        };

        return notification;
      } catch {
        return null;
      }
    },
    [state.isSupported, state.permission]
  );

  const scheduleTaskReminder = useCallback(
    (task: Task) => {
      if (!task.reminder_at || task.completed) {
        return;
      }

      // Cancel existing reminder for this task
      const existing = scheduledNotifications.current.get(task.id);
      if (existing) {
        clearTimeout(existing);
        scheduledNotifications.current.delete(task.id);
      }

      const reminderTime = new Date(task.reminder_at).getTime();
      const now = Date.now();
      const delay = reminderTime - now;

      // Only schedule if the reminder is in the future
      if (delay > 0) {
        const timeout = setTimeout(() => {
          showNotification(`Task Reminder: ${task.title}`, {
            body: task.due_date
              ? `Due: ${new Date(task.due_date).toLocaleString()}`
              : "Task reminder",
            tag: `task-reminder-${task.id}`,
            requireInteraction: true,
          });
          scheduledNotifications.current.delete(task.id);
        }, delay);

        scheduledNotifications.current.set(task.id, timeout);
      }
    },
    [showNotification]
  );

  const cancelTaskReminder = useCallback((taskId: string) => {
    const existing = scheduledNotifications.current.get(taskId);
    if (existing) {
      clearTimeout(existing);
      scheduledNotifications.current.delete(taskId);
    }
  }, []);

  const scheduleTaskReminders = useCallback(
    (tasks: Task[]) => {
      // Cancel all existing reminders
      scheduledNotifications.current.forEach((timeout) => clearTimeout(timeout));
      scheduledNotifications.current.clear();

      // Schedule new reminders
      tasks.forEach((task) => {
        if (task.reminder_at && !task.completed) {
          scheduleTaskReminder(task);
        }
      });
    },
    [scheduleTaskReminder]
  );

  // Cleanup on unmount
  useEffect(() => {
    const notifications = scheduledNotifications.current;
    return () => {
      notifications.forEach((timeout) => clearTimeout(timeout));
      notifications.clear();
    };
  }, []);

  return {
    permission: state.permission,
    isSupported: state.isSupported,
    requestPermission,
    showNotification,
    scheduleTaskReminder,
    scheduleTaskReminders,
    cancelTaskReminder,
  };
}
