"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Plus,
  CheckCircle2,
  Circle,
  AlertCircle,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { taskApi } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import type { Task } from "@/types/task";
import { cn } from "@/lib/utils";

const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

export default function CalendarPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTasks, setSelectedTasks] = useState<Task[]>([]);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await taskApi.list({
        status: "all",
        sort: "due_date",
        order: "asc",
      });
      setTasks(response.tasks);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Get calendar data for current month
  const calendarData = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // First day of month
    const firstDay = new Date(year, month, 1);
    const startingDay = firstDay.getDay();

    // Last day of month
    const lastDay = new Date(year, month + 1, 0);
    const totalDays = lastDay.getDate();

    // Previous month days to show
    const prevMonthLastDay = new Date(year, month, 0).getDate();

    // Build calendar grid
    const days: { date: Date; isCurrentMonth: boolean; isToday: boolean; tasks: Task[] }[] = [];

    // Previous month days
    for (let i = startingDay - 1; i >= 0; i--) {
      const date = new Date(year, month - 1, prevMonthLastDay - i);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        tasks: getTasksForDate(date),
      });
    }

    // Current month days
    const today = new Date();
    for (let i = 1; i <= totalDays; i++) {
      const date = new Date(year, month, i);
      const isToday =
        date.getDate() === today.getDate() &&
        date.getMonth() === today.getMonth() &&
        date.getFullYear() === today.getFullYear();
      days.push({
        date,
        isCurrentMonth: true,
        isToday,
        tasks: getTasksForDate(date),
      });
    }

    // Next month days to fill grid (always show 6 rows)
    const remainingDays = 42 - days.length;
    for (let i = 1; i <= remainingDays; i++) {
      const date = new Date(year, month + 1, i);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        tasks: getTasksForDate(date),
      });
    }

    return days;
  }, [currentDate, tasks]);

  function getTasksForDate(date: Date): Task[] {
    const dateStr = date.toISOString().split("T")[0];
    return tasks.filter((task) => {
      if (!task.due_date) return false;
      return task.due_date.startsWith(dateStr);
    });
  }

  const navigateMonth = (direction: "prev" | "next") => {
    setCurrentDate((prev) => {
      const newDate = new Date(prev);
      if (direction === "prev") {
        newDate.setMonth(newDate.getMonth() - 1);
      } else {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    });
    setSelectedDate(null);
    setSelectedTasks([]);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(null);
    setSelectedTasks([]);
  };

  const handleDateClick = (date: Date, dayTasks: Task[]) => {
    setSelectedDate(date);
    setSelectedTasks(dayTasks);
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      await taskApi.toggleComplete(task.id);
      fetchTasks();
      toast({
        title: task.completed ? "Task reopened" : "Task completed",
        description: task.title,
      });
    } catch (error) {
      console.error("Failed to toggle task:", error);
      toast({
        variant: "destructive",
        title: "Failed to update task",
        description: "Please try again.",
      });
    }
  };

  // Stats for current month
  const monthStats = useMemo(() => {
    const monthTasks = calendarData
      .filter((d) => d.isCurrentMonth)
      .flatMap((d) => d.tasks);

    const uniqueTasks = [...new Map(monthTasks.map((t) => [t.id, t])).values()];
    const completed = uniqueTasks.filter((t) => t.completed).length;
    const overdue = uniqueTasks.filter((t) => t.is_overdue && !t.completed).length;

    return {
      total: uniqueTasks.length,
      completed,
      pending: uniqueTasks.length - completed,
      overdue,
    };
  }, [calendarData]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-muted animate-pulse" />
          <div className="space-y-2">
            <div className="h-6 w-32 bg-muted animate-pulse rounded" />
            <div className="h-4 w-48 bg-muted animate-pulse rounded" />
          </div>
        </div>
        <div className="h-96 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl gradient-primary shadow-glow-sm">
            <CalendarIcon className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">
              <span className="text-gradient">Calendar</span>
            </h1>
            <p className="text-sm text-muted-foreground">
              View and manage tasks by due date
            </p>
          </div>
        </div>

        {/* Month Stats */}
        <div className="flex items-center gap-3">
          <StatBadge
            icon={<CheckCircle2 className="h-3 w-3" />}
            value={monthStats.completed}
            label="Done"
            color="success"
          />
          <StatBadge
            icon={<Circle className="h-3 w-3" />}
            value={monthStats.pending}
            label="Pending"
            color="warning"
          />
          {monthStats.overdue > 0 && (
            <StatBadge
              icon={<AlertCircle className="h-3 w-3" />}
              value={monthStats.overdue}
              label="Overdue"
              color="destructive"
            />
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar */}
        <div className="lg:col-span-2 rounded-xl border bg-card p-4">
          {/* Calendar Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Button variant="outline" size="icon" onClick={() => navigateMonth("prev")}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h2 className="text-lg font-semibold min-w-[180px] text-center">
                {MONTHS[currentDate.getMonth()]} {currentDate.getFullYear()}
              </h2>
              <Button variant="outline" size="icon" onClick={() => navigateMonth("next")}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <Button variant="outline" size="sm" onClick={goToToday}>
              Today
            </Button>
          </div>

          {/* Day Headers */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {DAYS.map((day) => (
              <div
                key={day}
                className="text-center text-xs font-medium text-muted-foreground py-2"
              >
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1">
            {calendarData.map((day, i) => (
              <CalendarDay
                key={i}
                date={day.date}
                isCurrentMonth={day.isCurrentMonth}
                isToday={day.isToday}
                isSelected={
                  selectedDate?.toDateString() === day.date.toDateString()
                }
                tasks={day.tasks}
                onClick={() => handleDateClick(day.date, day.tasks)}
              />
            ))}
          </div>

          {/* Legend */}
          <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <div className="h-2 w-2 rounded-full bg-success" />
              Completed
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <div className="h-2 w-2 rounded-full bg-warning" />
              Pending
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <div className="h-2 w-2 rounded-full bg-destructive" />
              Overdue
            </div>
          </div>
        </div>

        {/* Selected Day Panel */}
        <div className="rounded-xl border bg-card p-4">
          {selectedDate ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-semibold">
                    {selectedDate.toLocaleDateString("en-US", {
                      weekday: "long",
                      month: "short",
                      day: "numeric",
                    })}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    {selectedTasks.length} task{selectedTasks.length !== 1 ? "s" : ""}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    setSelectedDate(null);
                    setSelectedTasks([]);
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {selectedTasks.length === 0 ? (
                <div className="text-center py-8">
                  <CalendarIcon className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">No tasks due on this day</p>
                  <p className="text-xs text-muted-foreground/70 mt-1">
                    Tasks with due dates will appear here
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {selectedTasks.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onToggle={() => handleToggleComplete(task)}
                    />
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <CalendarIcon className="h-16 w-16 text-muted-foreground/20 mx-auto mb-4" />
              <h3 className="font-medium text-muted-foreground">Select a Date</h3>
              <p className="text-sm text-muted-foreground/70 mt-1">
                Click on a date to view tasks
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Upcoming Tasks */}
      <div className="rounded-xl border bg-card p-5">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <CalendarIcon className="h-4 w-4 text-primary" />
          Upcoming Tasks (Next 7 Days)
        </h3>
        <UpcomingTasks tasks={tasks} onToggle={handleToggleComplete} />
      </div>
    </div>
  );
}

// Calendar Day Component
interface CalendarDayProps {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  isSelected: boolean;
  tasks: Task[];
  onClick: () => void;
}

function CalendarDay({ date, isCurrentMonth, isToday, isSelected, tasks, onClick }: CalendarDayProps) {
  const completedCount = tasks.filter((t) => t.completed).length;
  const overdueCount = tasks.filter((t) => t.is_overdue && !t.completed).length;
  const pendingCount = tasks.length - completedCount - overdueCount;

  return (
    <button
      onClick={onClick}
      className={cn(
        "relative aspect-square p-1 rounded-lg transition-all duration-200 hover:bg-muted",
        !isCurrentMonth && "opacity-40",
        isToday && "ring-2 ring-primary ring-offset-2 ring-offset-background",
        isSelected && "bg-primary/10 hover:bg-primary/20"
      )}
    >
      <span
        className={cn(
          "block text-sm font-medium",
          isToday && "text-primary font-bold"
        )}
      >
        {date.getDate()}
      </span>

      {/* Task indicators */}
      {tasks.length > 0 && (
        <div className="absolute bottom-1 left-1/2 -translate-x-1/2 flex items-center gap-0.5">
          {overdueCount > 0 && <div className="h-1.5 w-1.5 rounded-full bg-destructive" />}
          {pendingCount > 0 && <div className="h-1.5 w-1.5 rounded-full bg-warning" />}
          {completedCount > 0 && <div className="h-1.5 w-1.5 rounded-full bg-success" />}
        </div>
      )}
    </button>
  );
}

// Task Card Component
function TaskCard({ task, onToggle }: { task: Task; onToggle: () => void }) {
  return (
    <div
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg border transition-all",
        task.completed && "bg-muted/30 border-border/50",
        task.is_overdue && !task.completed && "border-destructive/30 bg-destructive/5"
      )}
    >
      <button
        onClick={onToggle}
        className={cn(
          "mt-0.5 h-5 w-5 rounded-full border-2 flex items-center justify-center transition-colors",
          task.completed
            ? "bg-success border-success text-white"
            : "border-muted-foreground/30 hover:border-primary"
        )}
      >
        {task.completed && <CheckCircle2 className="h-3 w-3" />}
      </button>
      <div className="flex-1 min-w-0">
        <p
          className={cn(
            "text-sm font-medium truncate",
            task.completed && "line-through text-muted-foreground"
          )}
        >
          {task.title}
        </p>
        <div className="flex items-center gap-2 mt-1">
          <span
            className={cn(
              "text-xs px-1.5 py-0.5 rounded-full",
              task.priority === "high" && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
              task.priority === "medium" && "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
              task.priority === "low" && "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
            )}
          >
            {task.priority}
          </span>
          {task.is_overdue && !task.completed && (
            <span className="text-xs text-destructive flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              Overdue
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// Stat Badge Component
function StatBadge({
  icon,
  value,
  label,
  color,
}: {
  icon: React.ReactNode;
  value: number;
  label: string;
  color: "success" | "warning" | "destructive";
}) {
  const colorClasses = {
    success: "bg-success/10 text-success border-success/20",
    warning: "bg-warning/10 text-warning border-warning/20",
    destructive: "bg-destructive/10 text-destructive border-destructive/20",
  };

  return (
    <div className={cn("flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs", colorClasses[color])}>
      {icon}
      <span className="font-semibold">{value}</span>
      <span className="hidden sm:inline opacity-70">{label}</span>
    </div>
  );
}

// Upcoming Tasks Component
function UpcomingTasks({ tasks, onToggle }: { tasks: Task[]; onToggle: (task: Task) => void }) {
  const upcomingTasks = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const weekFromNow = new Date(today);
    weekFromNow.setDate(weekFromNow.getDate() + 7);

    return tasks
      .filter((task) => {
        if (!task.due_date || task.completed) return false;
        const dueDate = new Date(task.due_date);
        return dueDate >= today && dueDate <= weekFromNow;
      })
      .sort((a, b) => new Date(a.due_date!).getTime() - new Date(b.due_date!).getTime())
      .slice(0, 10);
  }, [tasks]);

  if (upcomingTasks.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-8">
        No upcoming tasks in the next 7 days. Great job staying ahead!
      </p>
    );
  }

  // Group by date
  const groupedTasks: Record<string, Task[]> = {};
  upcomingTasks.forEach((task) => {
    const dateKey = new Date(task.due_date!).toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
    if (!groupedTasks[dateKey]) groupedTasks[dateKey] = [];
    groupedTasks[dateKey].push(task);
  });

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Object.entries(groupedTasks).map(([date, dateTasks]) => (
        <div key={date} className="space-y-2">
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
            {date}
          </h4>
          {dateTasks.map((task) => (
            <div
              key={task.id}
              className={cn(
                "flex items-center gap-2 p-2 rounded-lg border text-sm",
                task.is_overdue && "border-destructive/30 bg-destructive/5"
              )}
            >
              <button
                onClick={() => onToggle(task)}
                className="h-4 w-4 rounded-full border-2 border-muted-foreground/30 hover:border-primary transition-colors flex-shrink-0"
              />
              <span className="truncate flex-1">{task.title}</span>
              {task.is_overdue && <AlertCircle className="h-3 w-3 text-destructive flex-shrink-0" />}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
