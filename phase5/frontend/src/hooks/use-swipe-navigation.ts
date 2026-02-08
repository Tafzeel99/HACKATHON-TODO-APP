"use client";

import { useRef, useEffect, useCallback } from "react";

interface SwipeNavigationOptions {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  threshold?: number;
  edgeThreshold?: number;
  enabled?: boolean;
}

interface SwipeState {
  startX: number;
  startY: number;
  startTime: number;
  isTracking: boolean;
}

export function useSwipeNavigation({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  threshold = 50,
  edgeThreshold = 30,
  enabled = true,
}: SwipeNavigationOptions = {}) {
  const state = useRef<SwipeState>({
    startX: 0,
    startY: 0,
    startTime: 0,
    isTracking: false,
  });

  const handleTouchStart = useCallback(
    (e: TouchEvent) => {
      if (!enabled) return;

      const touch = e.touches[0];
      const isNearLeftEdge = touch.clientX <= edgeThreshold;
      const isNearRightEdge =
        window.innerWidth - touch.clientX <= edgeThreshold;

      // Only track edge swipes for navigation
      if (!isNearLeftEdge && !isNearRightEdge) {
        state.current.isTracking = false;
        return;
      }

      state.current = {
        startX: touch.clientX,
        startY: touch.clientY,
        startTime: Date.now(),
        isTracking: true,
      };
    },
    [enabled, edgeThreshold]
  );

  const handleTouchEnd = useCallback(
    (e: TouchEvent) => {
      if (!enabled || !state.current.isTracking) return;

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - state.current.startX;
      const deltaY = touch.clientY - state.current.startY;
      const deltaTime = Date.now() - state.current.startTime;

      // Calculate velocity
      const velocityX = Math.abs(deltaX) / deltaTime;
      const velocityY = Math.abs(deltaY) / deltaTime;

      // Check if horizontal swipe (larger than vertical)
      const isHorizontal = Math.abs(deltaX) > Math.abs(deltaY);
      const meetsThreshold =
        Math.abs(isHorizontal ? deltaX : deltaY) >= threshold;
      const meetsVelocity = (isHorizontal ? velocityX : velocityY) > 0.3;

      if (meetsThreshold || meetsVelocity) {
        if (isHorizontal) {
          if (deltaX > 0) {
            onSwipeRight?.();
          } else {
            onSwipeLeft?.();
          }
        } else {
          if (deltaY > 0) {
            onSwipeDown?.();
          } else {
            onSwipeUp?.();
          }
        }
      }

      state.current.isTracking = false;
    },
    [enabled, threshold, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown]
  );

  useEffect(() => {
    if (!enabled) return;

    document.addEventListener("touchstart", handleTouchStart, { passive: true });
    document.addEventListener("touchend", handleTouchEnd, { passive: true });

    return () => {
      document.removeEventListener("touchstart", handleTouchStart);
      document.removeEventListener("touchend", handleTouchEnd);
    };
  }, [enabled, handleTouchStart, handleTouchEnd]);
}

// Hook for opening sidebar with edge swipe
export function useSidebarSwipe(
  onOpen: () => void,
  enabled: boolean = true
) {
  useSwipeNavigation({
    onSwipeRight: onOpen,
    edgeThreshold: 20,
    threshold: 30,
    enabled,
  });
}
