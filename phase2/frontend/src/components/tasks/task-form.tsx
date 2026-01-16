"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { taskApi } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import type { Task } from "@/types/task";

const taskSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less"),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  onTaskCreated?: (task: Task) => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: "",
      description: "",
    },
  });

  const onSubmit = async (data: TaskFormData) => {
    setIsLoading(true);

    try {
      const task = await taskApi.create({
        title: data.title,
        description: data.description || undefined,
      });

      form.reset();
      onTaskCreated?.(task);
      toast({
        title: "Task created",
        description: task.title,
      });
    } catch (error) {
      console.error("Failed to create task:", error);
      toast({
        variant: "destructive",
        title: "Failed to create task",
        description: "Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="flex gap-2">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem className="flex-1">
              <FormControl>
                <Input
                  placeholder="Add a new task..."
                  {...field}
                  disabled={isLoading}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isLoading} size="icon">
          <Plus className="h-4 w-4" />
        </Button>
      </form>
    </Form>
  );
}
