"use client";

import { useState, useRef, useCallback } from "react";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
  className?: string;
  threshold?: number;
  disabled?: boolean;
}

export function PullToRefresh({
  onRefresh,
  children,
  className,
  threshold = 80,
  disabled = false,
}: PullToRefreshProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const pullDistance = useMotionValue(0);

  // Transform for the spinner
  const spinnerOpacity = useTransform(pullDistance, [0, threshold * 0.5, threshold], [0, 0.5, 1]);
  const spinnerScale = useTransform(pullDistance, [0, threshold], [0.5, 1]);
  const spinnerRotation = useTransform(pullDistance, [0, threshold], [0, 180]);

  const handleTouchStart = useCallback(
    (e: React.TouchEvent) => {
      if (disabled || isRefreshing) return;

      const container = containerRef.current;
      if (!container) return;

      // Only activate if scrolled to top
      if (container.scrollTop !== 0) return;

      startY.current = e.touches[0].clientY;
    },
    [disabled, isRefreshing]
  );

  const handleTouchMove = useCallback(
    (e: React.TouchEvent) => {
      if (disabled || isRefreshing) return;
      if (startY.current === 0) return;

      const container = containerRef.current;
      if (!container) return;

      const currentY = e.touches[0].clientY;
      const diff = currentY - startY.current;

      // Only pull down, not up
      if (diff < 0) {
        pullDistance.set(0);
        return;
      }

      // Apply resistance
      const resistance = 0.4;
      const distance = Math.min(diff * resistance, threshold * 1.5);
      pullDistance.set(distance);
    },
    [disabled, isRefreshing, pullDistance, threshold]
  );

  const handleTouchEnd = useCallback(async () => {
    if (disabled || isRefreshing) return;

    const distance = pullDistance.get();

    if (distance >= threshold) {
      setIsRefreshing(true);
      pullDistance.set(threshold);

      try {
        await onRefresh();
      } finally {
        setIsRefreshing(false);
      }
    }

    pullDistance.set(0);
    startY.current = 0;
  }, [disabled, isRefreshing, pullDistance, threshold, onRefresh]);

  return (
    <div
      ref={containerRef}
      className={cn("relative overflow-auto", className)}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Pull indicator */}
      <motion.div
        style={{
          height: pullDistance,
          opacity: spinnerOpacity,
        }}
        className="flex items-center justify-center overflow-hidden"
      >
        <motion.div
          style={{
            scale: spinnerScale,
            rotate: isRefreshing ? undefined : spinnerRotation,
          }}
          className={cn(isRefreshing && "animate-spin-slow")}
        >
          <RefreshCw className="h-6 w-6 text-primary" />
        </motion.div>
      </motion.div>

      {/* Content */}
      <motion.div
        style={{
          y: isRefreshing ? threshold : 0,
        }}
      >
        {children}
      </motion.div>
    </div>
  );
}
