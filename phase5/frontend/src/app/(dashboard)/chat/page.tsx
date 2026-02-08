"use client";

import { Bot, Lightbulb, Zap, Target, Clock, Sparkles } from "lucide-react";
import { TodoChatKit } from "@/components/chat/TodoChatKit";

export default function ChatPage() {
  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl gradient-primary shadow-lg shadow-primary/30">
            <Bot className="h-7 w-7 text-white" />
            {/* Status indicator */}
            <div className="absolute -bottom-1 -right-1 h-4 w-4 rounded-full bg-success border-2 border-background shadow-lg">
              <div className="absolute inset-0 rounded-full bg-success animate-ping opacity-50" />
            </div>
          </div>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <span className="text-gradient">TodoX Agent</span>
            </h1>
            <p className="text-sm text-muted-foreground">
              Manage your tasks using natural language
            </p>
          </div>
        </div>

        {/* Quick Tips - Desktop */}
        <div className="hidden lg:flex items-center gap-2">
          <QuickTip icon={<Zap className="h-3 w-3" />} text="Add tasks" />
          <QuickTip icon={<Target className="h-3 w-3" />} text="Complete tasks" />
          <QuickTip icon={<Clock className="h-3 w-3" />} text="Check pending" />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Container */}
        <div className="lg:col-span-3 relative rounded-2xl border border-border/50 bg-card overflow-hidden shadow-xl">
          {/* Decorative top gradient */}
          <div className="absolute top-0 left-0 right-0 h-1 gradient-primary" />
          <TodoChatKit />
        </div>

        {/* Side Panel - Tips & Commands */}
        <div className="hidden lg:flex flex-col gap-4">
          {/* Commands Card */}
          <div className="rounded-2xl border border-border/50 bg-card p-5 space-y-4">
            <h3 className="font-semibold flex items-center gap-2 text-sm">
              <div className="p-1.5 rounded-lg bg-primary/10">
                <Lightbulb className="h-4 w-4 text-primary" />
              </div>
              Available Commands
            </h3>
            <div className="space-y-2">
              <CommandItem
                title="Add Task"
                example="Add a task to buy groceries"
              />
              <CommandItem
                title="View Tasks"
                example="Show me all my tasks"
              />
              <CommandItem
                title="Complete Task"
                example="Mark task 3 as done"
              />
              <CommandItem
                title="Update Task"
                example="Change task 1 title to..."
              />
              <CommandItem
                title="Delete Task"
                example="Delete task 2"
              />
              <CommandItem
                title="Filter Tasks"
                example="Show pending tasks only"
              />
            </div>
          </div>

          {/* Tips Card */}
          <div className="relative overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/5 via-card to-[hsl(var(--gradient-end))]/5 p-5 space-y-4 flex-1">
            {/* Decorative glow */}
            <div className="absolute -right-10 -top-10 w-32 h-32 bg-primary/10 rounded-full blur-3xl" />

            <h3 className="font-semibold flex items-center gap-2 text-sm relative">
              <div className="p-1.5 rounded-lg bg-primary/10">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              Pro Tips
            </h3>
            <ul className="text-xs text-muted-foreground space-y-3 relative">
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5 font-bold">•</span>
                <span>Be specific with task descriptions for better organization</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5 font-bold">•</span>
                <span>Use task IDs when referencing specific tasks</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5 font-bold">•</span>
                <span>Ask &quot;What&apos;s pending?&quot; for a quick status check</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5 font-bold">•</span>
                <span>The AI remembers context within the conversation</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Mobile Tips - Collapsible */}
      <div className="lg:hidden rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-3">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide">
          <QuickTip icon={<Zap className="h-3 w-3" />} text="Add tasks" />
          <QuickTip icon={<Target className="h-3 w-3" />} text="Complete" />
          <QuickTip icon={<Clock className="h-3 w-3" />} text="View pending" />
          <QuickTip icon={<Lightbulb className="h-3 w-3" />} text="Update" />
        </div>
      </div>
    </div>
  );
}

function QuickTip({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-muted/50 border border-border/50 text-xs font-medium whitespace-nowrap hover:bg-primary/5 hover:border-primary/20 transition-all duration-200">
      <span className="text-primary">{icon}</span>
      {text}
    </div>
  );
}

function CommandItem({ title, example }: { title: string; example: string }) {
  return (
    <div className="p-3 rounded-xl bg-muted/30 border border-border/30 hover:bg-primary/5 hover:border-primary/20 transition-all duration-200">
      <p className="text-xs font-semibold">{title}</p>
      <p className="text-[11px] text-muted-foreground mt-1 truncate">
        &quot;{example}&quot;
      </p>
    </div>
  );
}
