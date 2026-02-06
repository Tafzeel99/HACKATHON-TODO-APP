"use client";

import { useCallback, useEffect, useRef } from "react";

interface ConfettiOptions {
  particleCount?: number;
  spread?: number;
  startVelocity?: number;
  decay?: number;
  gravity?: number;
  origin?: { x: number; y: number };
  colors?: string[];
  shapes?: ("square" | "circle")[];
  scalar?: number;
  ticks?: number;
  disableForReducedMotion?: boolean;
}

// Global flag to disable confetti (can be set from settings)
let confettiEnabled = true;

export function setConfettiEnabled(enabled: boolean) {
  confettiEnabled = enabled;
}

// Singleton pattern - load canvas-confetti only once
let confettiModule: typeof import("canvas-confetti").default | null = null;
let loadingPromise: Promise<void> | null = null;

async function loadConfetti() {
  if (confettiModule) return;
  if (loadingPromise) {
    await loadingPromise;
    return;
  }

  loadingPromise = import("canvas-confetti").then((module) => {
    confettiModule = module.default;
  });

  await loadingPromise;
}

export function useConfetti() {
  const isLoadedRef = useRef(false);

  useEffect(() => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      confettiEnabled = false;
      return;
    }

    if (!isLoadedRef.current) {
      loadConfetti();
      isLoadedRef.current = true;
    }
  }, []);

  const fire = useCallback((options?: ConfettiOptions) => {
    // Skip if disabled or not loaded
    if (!confettiEnabled || !confettiModule) return;

    // Lightweight defaults for better performance
    const defaults: ConfettiOptions = {
      particleCount: 20,  // Reduced from 50
      spread: 45,         // Reduced from 60
      startVelocity: 25,  // Reduced from 30
      decay: 0.9,         // Faster decay
      gravity: 1.2,       // Faster fall
      ticks: 150,         // Shorter animation
      origin: { x: 0.5, y: 0.6 },
      colors: ["#6366f1", "#22c55e", "#f97316"], // Reduced colors
      shapes: ["circle"], // Single shape for performance
      scalar: 0.9,
      disableForReducedMotion: true,
    };

    confettiModule({
      ...defaults,
      ...options,
    });
  }, []);

  const fireMultiple = useCallback(
    (count: number = 2, delay: number = 200) => {
      if (!confettiEnabled) return;

      for (let i = 0; i < count; i++) {
        setTimeout(() => {
          fire({
            particleCount: 15,
            origin: {
              x: 0.3 + Math.random() * 0.4,
              y: 0.5 + Math.random() * 0.2,
            },
          });
        }, i * delay);
      }
    },
    [fire]
  );

  const fireBurst = useCallback(() => {
    if (!confettiEnabled || !confettiModule) return;

    // Single burst from center - lighter
    confettiModule({
      particleCount: 25,
      spread: 70,
      origin: { x: 0.5, y: 0.5 },
      colors: ["#6366f1", "#22c55e", "#f97316"],
      ticks: 120,
    });
  }, []);

  const fireAtElement = useCallback(
    (element: HTMLElement) => {
      if (!confettiEnabled || !confettiModule) return;

      const rect = element.getBoundingClientRect();
      const x = (rect.left + rect.width / 2) / window.innerWidth;
      const y = (rect.top + rect.height / 2) / window.innerHeight;

      fire({
        origin: { x, y },
        particleCount: 15,
        spread: 35,
        startVelocity: 18,
      });
    },
    [fire]
  );

  return {
    fire,
    fireMultiple,
    fireBurst,
    fireAtElement,
  };
}

// A simple component that triggers confetti on mount
export function Confetti({
  trigger,
  type = "default",
}: {
  trigger?: boolean;
  type?: "default" | "burst" | "multiple";
}) {
  const { fire, fireBurst, fireMultiple } = useConfetti();

  useEffect(() => {
    if (trigger) {
      switch (type) {
        case "burst":
          fireBurst();
          break;
        case "multiple":
          fireMultiple();
          break;
        default:
          fire();
      }
    }
  }, [trigger, type, fire, fireBurst, fireMultiple]);

  return null;
}
