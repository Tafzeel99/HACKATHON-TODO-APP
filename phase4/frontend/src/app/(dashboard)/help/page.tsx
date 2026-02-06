"use client";

import { useState } from "react";
import {
  HelpCircle,
  MessageSquare,
  Book,
  Keyboard,
  ChevronDown,
  ChevronRight,
  Bot,
  ListTodo,
  Calendar,
  BarChart3,
  ExternalLink,
} from "lucide-react";

import { Button } from "@/components/ui/button";

const faqs = [
  {
    question: "How do I create a new task?",
    answer:
      "You can create a task in multiple ways: Click the 'New Task' button on the dashboard, use the quick add form, or simply tell the TodoX Agent 'Add a task to [your task description]'.",
  },
  {
    question: "How does the TodoX Agent work?",
    answer:
      "The TodoX Agent uses natural language processing to understand your commands. You can ask it to add, update, complete, or delete tasks. Try phrases like 'Show my pending tasks' or 'Mark task 3 as done'.",
  },
  {
    question: "Can I set due dates and reminders?",
    answer:
      "Yes! When creating or editing a task, you can set a due date. You can also enable browser notifications to receive reminders. Look for the bell icon on the Tasks page to enable notifications.",
  },
  {
    question: "What are task priorities?",
    answer:
      "Tasks can be set to Low, Medium, or High priority. High priority tasks are highlighted and can be filtered for focus. This helps you tackle important tasks first.",
  },
  {
    question: "How do recurring tasks work?",
    answer:
      "You can set tasks to repeat daily, weekly, or monthly. When you complete a recurring task, a new instance is automatically created for the next occurrence.",
  },
  {
    question: "Can I organize tasks with tags?",
    answer:
      "Absolutely! Add tags to your tasks for better organization. You can then filter tasks by tags to focus on specific projects or categories.",
  },
];

const features = [
  {
    icon: <ListTodo className="h-5 w-5" />,
    title: "Task Management",
    description: "Create, edit, complete, and delete tasks with ease",
  },
  {
    icon: <Bot className="h-5 w-5" />,
    title: "TodoX Agent",
    description: "Manage tasks using natural language commands",
  },
  {
    icon: <Calendar className="h-5 w-5" />,
    title: "Calendar View",
    description: "Visualize tasks on a calendar by due date",
  },
  {
    icon: <BarChart3 className="h-5 w-5" />,
    title: "Analytics",
    description: "Track productivity and completion rates",
  },
];

const shortcuts = [
  { keys: ["N"], description: "New task (when on tasks page)" },
  { keys: ["?"], description: "Open help" },
  { keys: ["D"], description: "Toggle dark mode" },
  { keys: ["Esc"], description: "Close dialogs" },
];

export default function HelpPage() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl gradient-primary shadow-glow-sm">
          <HelpCircle className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">
            <span className="text-gradient">Help Center</span>
          </h1>
          <p className="text-sm text-muted-foreground">
            Get help and learn how to use todoX
          </p>
        </div>
      </div>

      {/* Quick Start */}
      <div className="rounded-xl border bg-gradient-to-br from-primary/5 to-purple-500/5 p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Book className="h-5 w-5 text-primary" />
          Quick Start Guide
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((feature, i) => (
            <div
              key={i}
              className="p-4 rounded-lg bg-card border hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-primary/10 text-primary">
                  {feature.icon}
                </div>
              </div>
              <h3 className="font-medium text-sm">{feature.title}</h3>
              <p className="text-xs text-muted-foreground mt-1">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* TodoX Agent Guide */}
      <div className="rounded-xl border bg-card p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary" />
          TodoX Agent Commands
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <CommandExample
            command="Add a task to buy groceries"
            description="Creates a new task"
          />
          <CommandExample
            command="Show me all my tasks"
            description="Lists all tasks"
          />
          <CommandExample
            command="Mark task 3 as done"
            description="Completes a task"
          />
          <CommandExample
            command="Delete task 5"
            description="Removes a task"
          />
          <CommandExample
            command="What's pending?"
            description="Shows incomplete tasks"
          />
          <CommandExample
            command="Update task 2 title to Call mom"
            description="Edits a task"
          />
        </div>
      </div>

      {/* FAQ */}
      <div className="rounded-xl border bg-card p-6">
        <h2 className="text-lg font-semibold mb-4">Frequently Asked Questions</h2>
        <div className="space-y-2">
          {faqs.map((faq, i) => (
            <FAQItem key={i} question={faq.question} answer={faq.answer} />
          ))}
        </div>
      </div>

      {/* Keyboard Shortcuts */}
      <div className="rounded-xl border bg-card p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Keyboard className="h-5 w-5 text-primary" />
          Keyboard Shortcuts
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {shortcuts.map((shortcut, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/30"
            >
              <span className="text-sm text-muted-foreground">
                {shortcut.description}
              </span>
              <div className="flex items-center gap-1">
                {shortcut.keys.map((key, j) => (
                  <kbd
                    key={j}
                    className="px-2 py-1 text-xs font-mono bg-background border rounded shadow-sm"
                  >
                    {key}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground mt-4">
          More keyboard shortcuts coming soon!
        </p>
      </div>

      {/* Support */}
      <div className="rounded-xl border bg-card p-6 text-center">
        <h2 className="text-lg font-semibold mb-2">Need More Help?</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Check out our documentation or reach out to support
        </p>
        <div className="flex items-center justify-center gap-3">
          <Button variant="outline" className="gap-2">
            <Book className="h-4 w-4" />
            Documentation
            <ExternalLink className="h-3 w-3" />
          </Button>
          <Button className="gap-2 gradient-primary">
            <MessageSquare className="h-4 w-4" />
            Contact Support
          </Button>
        </div>
      </div>
    </div>
  );
}

function CommandExample({
  command,
  description,
}: {
  command: string;
  description: string;
}) {
  return (
    <div className="p-3 rounded-lg bg-muted/30 border">
      <code className="text-sm text-primary">&quot;{command}&quot;</code>
      <p className="text-xs text-muted-foreground mt-1">{description}</p>
    </div>
  );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
      >
        <span className="text-sm font-medium">{question}</span>
        {isOpen ? (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        )}
      </button>
      {isOpen && (
        <div className="px-4 pb-4">
          <p className="text-sm text-muted-foreground">{answer}</p>
        </div>
      )}
    </div>
  );
}
