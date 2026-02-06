"use client";

import { CheckCircle2, Circle, ListTodo, AlertCircle } from "lucide-react";
import { Task } from "@/types/task";

interface TaskStatsProps {
  tasks: Task[];
  isLoading?: boolean;
}

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  colorClass: string;
  delay?: string;
}

function StatCard({ title, value, icon, colorClass, delay }: StatCardProps) {
  return (
    <div
      className={`stat-card animate-fade-up ${delay || ""}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className={`text-3xl font-bold mt-1 ${colorClass}`}>
            {value}
          </p>
        </div>
        <div className={`p-3 rounded-xl ${colorClass} bg-current/10`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function StatCardSkeleton() {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between">
        <div>
          <div className="h-4 w-16 bg-muted animate-pulse rounded" />
          <div className="h-8 w-12 bg-muted animate-pulse rounded mt-2" />
        </div>
        <div className="h-12 w-12 bg-muted animate-pulse rounded-xl" />
      </div>
    </div>
  );
}

export function TaskStats({ tasks, isLoading }: TaskStatsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>
    );
  }

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((task) => task.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const overdueTasks = tasks.filter((task) => task.is_overdue && !task.completed).length;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <StatCard
        title="Total Tasks"
        value={totalTasks}
        icon={<ListTodo className="h-6 w-6 text-primary" />}
        colorClass="text-primary"
        delay="stagger-1"
      />
      <StatCard
        title="Pending"
        value={pendingTasks}
        icon={<Circle className="h-6 w-6 text-warning" />}
        colorClass="text-warning"
        delay="stagger-2"
      />
      <StatCard
        title="Overdue"
        value={overdueTasks}
        icon={<AlertCircle className="h-6 w-6 text-destructive" />}
        colorClass="text-destructive"
        delay="stagger-3"
      />
      <StatCard
        title="Completed"
        value={completedTasks}
        icon={<CheckCircle2 className="h-6 w-6 text-success" />}
        colorClass="text-success"
        delay="stagger-4"
      />
    </div>
  );
}
