"use client";

import { ClipboardList } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { TaskItem } from "@/components/tasks/task-item";
import { TaskSkeleton } from "@/components/skeletons";
import type { Task } from "@/types/task";

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
  onUpdate?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

const listVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 30,
    },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: {
      duration: 0.2,
    },
  },
};

export function TaskList({ tasks, isLoading, onUpdate, onDelete }: TaskListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <TaskSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col items-center justify-center rounded-xl border border-dashed bg-muted/20 p-12 text-center"
      >
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mb-4">
          <ClipboardList className="h-8 w-8 text-primary" />
        </div>
        <h3 className="text-lg font-semibold mb-1">No tasks yet</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Get started by adding your first task above. Stay organized and track your progress!
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="space-y-3"
      variants={listVariants}
      initial="hidden"
      animate="visible"
    >
      <AnimatePresence mode="popLayout">
        {tasks.map((task) => (
          <motion.div
            key={task.id}
            variants={itemVariants}
            layout
            exit="exit"
          >
            <TaskItem
              task={task}
              onUpdate={onUpdate}
              onDelete={onDelete}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </motion.div>
  );
}
