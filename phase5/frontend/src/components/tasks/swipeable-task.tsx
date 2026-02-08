"use client";

import { useState, useRef } from "react";
import { motion, useMotionValue, useTransform, PanInfo } from "framer-motion";
import { Check, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Task } from "@/types/task";

interface SwipeableTaskProps {
  task: Task;
  children: React.ReactNode;
  onDelete?: () => void;
  onComplete?: () => void;
  disabled?: boolean;
}

const SWIPE_THRESHOLD = 100;
const VELOCITY_THRESHOLD = 500;

export function SwipeableTask({
  task,
  children,
  onDelete,
  onComplete,
  disabled = false,
}: SwipeableTaskProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);
  const constraintsRef = useRef(null);

  const x = useMotionValue(0);

  // Transform for background visibility
  const deleteOpacity = useTransform(x, [-200, -50], [1, 0]);
  const completeOpacity = useTransform(x, [50, 200], [0, 1]);

  // Transform for icons scale
  const deleteIconScale = useTransform(x, [-150, -100], [1.2, 1]);
  const completeIconScale = useTransform(x, [100, 150], [1, 1.2]);

  const handleDragEnd = async (
    _event: MouseEvent | TouchEvent | PointerEvent,
    info: PanInfo
  ) => {
    const offset = info.offset.x;
    const velocity = info.velocity.x;

    // Delete action (swipe left)
    if (offset < -SWIPE_THRESHOLD || velocity < -VELOCITY_THRESHOLD) {
      if (onDelete) {
        setIsDeleting(true);
        // Haptic feedback if available
        if (navigator.vibrate) {
          navigator.vibrate(50);
        }
        await onDelete();
      }
    }
    // Complete action (swipe right)
    else if (offset > SWIPE_THRESHOLD || velocity > VELOCITY_THRESHOLD) {
      if (onComplete) {
        setIsCompleting(true);
        // Haptic feedback if available
        if (navigator.vibrate) {
          navigator.vibrate([30, 30, 30]);
        }
        await onComplete();
      }
    }
  };

  if (disabled) {
    return <>{children}</>;
  }

  return (
    <div ref={constraintsRef} className="relative overflow-hidden rounded-xl">
      {/* Delete background (left swipe) */}
      <motion.div
        style={{ opacity: deleteOpacity }}
        className={cn(
          "absolute inset-0 flex items-center justify-end pr-6",
          "bg-destructive rounded-xl"
        )}
      >
        <motion.div style={{ scale: deleteIconScale }}>
          <Trash2 className="h-6 w-6 text-white" />
        </motion.div>
      </motion.div>

      {/* Complete background (right swipe) */}
      <motion.div
        style={{ opacity: completeOpacity }}
        className={cn(
          "absolute inset-0 flex items-center justify-start pl-6",
          "bg-success rounded-xl"
        )}
      >
        <motion.div style={{ scale: completeIconScale }}>
          <Check className="h-6 w-6 text-white" />
        </motion.div>
      </motion.div>

      {/* Swipeable content */}
      <motion.div
        style={{ x }}
        drag="x"
        dragConstraints={constraintsRef}
        dragElastic={0.1}
        onDragEnd={handleDragEnd}
        animate={
          isDeleting
            ? { x: -400, opacity: 0 }
            : isCompleting
            ? { x: 400, opacity: 0 }
            : { x: 0 }
        }
        transition={{ type: "spring", damping: 30, stiffness: 300 }}
        className="relative bg-background rounded-xl cursor-grab active:cursor-grabbing"
      >
        {children}
      </motion.div>
    </div>
  );
}
