"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface FloatingActionButtonProps {
  onClick: () => void;
  className?: string;
}

export function FloatingActionButton({
  onClick,
  className,
}: FloatingActionButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn("fab", className)}
      aria-label="Add new task"
    >
      <Plus className="h-6 w-6" />
    </button>
  );
}

// Expandable FAB with multiple actions
interface FabAction {
  icon: typeof Plus;
  label: string;
  onClick: () => void;
  color?: string;
}

interface ExpandableFabProps {
  actions: FabAction[];
  className?: string;
}

export function ExpandableFab({ actions, className }: ExpandableFabProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={cn("fixed bottom-20 right-4 z-40", className)}>
      {/* Action buttons */}
      <AnimatePresence>
        {isOpen && (
          <div className="absolute bottom-16 right-0 space-y-3">
            {actions.map((action, index) => {
              const Icon = action.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20, scale: 0.8 }}
                  animate={{
                    opacity: 1,
                    y: 0,
                    scale: 1,
                    transition: { delay: index * 0.05 },
                  }}
                  exit={{
                    opacity: 0,
                    y: 10,
                    scale: 0.8,
                    transition: { delay: (actions.length - index) * 0.03 },
                  }}
                  className="flex items-center gap-2 justify-end"
                >
                  <span className="px-3 py-1.5 text-sm bg-card rounded-lg shadow-lg border border-border whitespace-nowrap">
                    {action.label}
                  </span>
                  <button
                    onClick={() => {
                      action.onClick();
                      setIsOpen(false);
                    }}
                    className={cn(
                      "h-12 w-12 rounded-full shadow-lg flex items-center justify-center",
                      "text-white transition-transform hover:scale-105 active:scale-95",
                      action.color || "bg-primary"
                    )}
                  >
                    <Icon className="h-5 w-5" />
                  </button>
                </motion.div>
              );
            })}
          </div>
        )}
      </AnimatePresence>

      {/* Main FAB */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "fab",
          isOpen && "bg-muted text-foreground shadow-none"
        )}
        aria-label={isOpen ? "Close menu" : "Open menu"}
        aria-expanded={isOpen}
      >
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.2 }}
        >
          {isOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Plus className="h-6 w-6" />
          )}
        </motion.div>
      </button>

      {/* Backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background/60 backdrop-blur-sm -z-10"
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
