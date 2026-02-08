"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Sparkles, ChevronDown, ChevronUp, Bell } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { taskApi } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { TagInput } from "./tag-input";
import { DatePicker } from "./date-picker";
import { RecurrenceSelector } from "./recurrence-selector";
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
  priority: z.enum(["low", "medium", "high"]).default("medium"),
  tags: z.array(z.string()).default([]),
  due_date: z.string().nullable().optional(),
  recurrence_pattern: z.enum(["none", "daily", "weekly", "monthly"]).default("none"),
  recurrence_end_date: z.string().nullable().optional(),
  reminder_enabled: z.boolean().default(false),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  onTaskCreated?: (task: Task) => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: "",
      description: "",
      priority: "medium",
      tags: [],
      due_date: null,
      recurrence_pattern: "none",
      recurrence_end_date: null,
      reminder_enabled: false,
    },
  });

  const dueDate = form.watch("due_date");

  useEffect(() => {
    taskApi.getTags().then((res) => setAvailableTags(res.tags)).catch(() => {});
  }, []);

  const onSubmit = async (data: TaskFormData) => {
    setIsLoading(true);

    try {
      let reminderAt: string | undefined;
      if (data.reminder_enabled && data.due_date) {
        const dueDateTime = new Date(data.due_date);
        dueDateTime.setHours(dueDateTime.getHours() - 1);
        reminderAt = dueDateTime.toISOString();
      }

      const task = await taskApi.create({
        title: data.title,
        description: data.description || undefined,
        priority: data.priority,
        tags: data.tags,
        due_date: data.due_date || undefined,
        recurrence_pattern: data.recurrence_pattern,
        recurrence_end_date: data.recurrence_end_date || undefined,
        reminder_at: reminderAt,
      });

      form.reset();
      setShowAdvanced(false);
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
    <div className="rounded-xl border bg-card p-4 shadow-sm transition-all duration-300 hover:shadow-md">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {/* Title and Add button row */}
          <div className="flex gap-3">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem className="flex-1">
                  <FormControl>
                    <div className="relative">
                      <Sparkles className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        placeholder="What needs to be done?"
                        className="pl-10 h-11 bg-background border-border/50 focus:border-primary transition-colors"
                        {...field}
                        disabled={isLoading}
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button
              type="submit"
              disabled={isLoading}
              className="h-11 px-6 gradient-primary text-white shadow-glow-sm hover:shadow-glow transition-shadow"
            >
              {isLoading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Add
                </>
              )}
            </Button>
          </div>

          {/* Priority selector - always visible */}
          <div className="flex items-center gap-4">
            <FormField
              control={form.control}
              name="priority"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center gap-2">
                    <Label className="text-sm text-muted-foreground">Priority:</Label>
                    <Select
                      value={field.value}
                      onValueChange={field.onChange}
                      disabled={isLoading}
                    >
                      <SelectTrigger className="w-[110px] h-8 text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </FormItem>
              )}
            />

            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-muted-foreground hover:text-foreground"
            >
              {showAdvanced ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-1" />
                  Less options
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-1" />
                  More options
                </>
              )}
            </Button>
          </div>

          {/* Advanced options */}
          {showAdvanced && (
            <div className="space-y-4 pt-2 border-t">
              {/* Tags */}
              <FormField
                control={form.control}
                name="tags"
                render={({ field }) => (
                  <FormItem>
                    <Label className="text-sm text-muted-foreground">Tags</Label>
                    <FormControl>
                      <TagInput
                        value={field.value}
                        onChange={field.onChange}
                        suggestions={availableTags}
                        disabled={isLoading}
                        placeholder="Add tags..."
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Due Date */}
              <FormField
                control={form.control}
                name="due_date"
                render={({ field }) => (
                  <FormItem>
                    <Label className="text-sm text-muted-foreground">Due Date</Label>
                    <FormControl>
                      <DatePicker
                        value={field.value || null}
                        onChange={field.onChange}
                        disabled={isLoading}
                        includeTime
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Recurrence - only show if due date is set */}
              {dueDate && (
                <FormField
                  control={form.control}
                  name="recurrence_pattern"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <RecurrenceSelector
                          pattern={field.value}
                          endDate={form.watch("recurrence_end_date") || null}
                          onPatternChange={field.onChange}
                          onEndDateChange={(date) =>
                            form.setValue("recurrence_end_date", date)
                          }
                          disabled={isLoading}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              {/* Reminder - only show if due date is set */}
              {dueDate && (
                <FormField
                  control={form.control}
                  name="reminder_enabled"
                  render={({ field }) => (
                    <FormItem>
                      <div className="flex items-center gap-2">
                        <Checkbox
                          id="reminder"
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          disabled={isLoading}
                        />
                        <Label
                          htmlFor="reminder"
                          className="text-sm flex items-center gap-1.5 cursor-pointer"
                        >
                          <Bell className="h-3.5 w-3.5" />
                          Remind me 1 hour before
                        </Label>
                      </div>
                    </FormItem>
                  )}
                />
              )}
            </div>
          )}
        </form>
      </Form>
    </div>
  );
}
