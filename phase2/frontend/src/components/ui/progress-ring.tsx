"use client";

import { cn } from "@/lib/utils";

interface ProgressRingProps {
  progress: number; // 0-100
  size?: "sm" | "md" | "lg" | "xl";
  strokeWidth?: number;
  className?: string;
  showLabel?: boolean;
  color?: "primary" | "success" | "warning" | "destructive" | "auto";
  trackColor?: string;
  animated?: boolean;
}

const SIZES = {
  sm: { size: 32, strokeWidth: 3, fontSize: "text-[10px]" },
  md: { size: 48, strokeWidth: 4, fontSize: "text-xs" },
  lg: { size: 64, strokeWidth: 5, fontSize: "text-sm" },
  xl: { size: 96, strokeWidth: 6, fontSize: "text-lg" },
};

const COLORS = {
  primary: "stroke-primary",
  success: "stroke-success",
  warning: "stroke-warning",
  destructive: "stroke-destructive",
  auto: "", // Will be determined by progress
};

function getAutoColor(progress: number): string {
  if (progress >= 80) return "stroke-success";
  if (progress >= 50) return "stroke-primary";
  if (progress >= 25) return "stroke-warning";
  return "stroke-destructive";
}

export function ProgressRing({
  progress,
  size = "md",
  strokeWidth: customStrokeWidth,
  className,
  showLabel = true,
  color = "primary",
  trackColor = "stroke-muted",
  animated = true,
}: ProgressRingProps) {
  const sizeConfig = SIZES[size];
  const strokeWidth = customStrokeWidth ?? sizeConfig.strokeWidth;
  const svgSize = sizeConfig.size;

  const radius = (svgSize - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  const strokeColor =
    color === "auto" ? getAutoColor(progress) : COLORS[color];

  return (
    <div className={cn("relative inline-flex", className)}>
      <svg
        width={svgSize}
        height={svgSize}
        viewBox={`0 0 ${svgSize} ${svgSize}`}
        className="transform -rotate-90"
      >
        {/* Track */}
        <circle
          cx={svgSize / 2}
          cy={svgSize / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          className={cn(trackColor, "opacity-20")}
        />

        {/* Progress */}
        <circle
          cx={svgSize / 2}
          cy={svgSize / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className={cn(strokeColor, animated && "transition-all duration-500 ease-out")}
        />
      </svg>

      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn("font-semibold text-foreground", sizeConfig.fontSize)}>
            {Math.round(progress)}%
          </span>
        </div>
      )}
    </div>
  );
}

// Compact version showing just the ring without percentage
export function ProgressRingCompact({
  progress,
  size = 20,
  className,
  color = "primary",
}: {
  progress: number;
  size?: number;
  className?: string;
  color?: "primary" | "success" | "warning" | "destructive" | "auto";
}) {
  const strokeWidth = Math.max(2, size / 10);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  const strokeColor =
    color === "auto" ? getAutoColor(progress) : COLORS[color];

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className={cn("transform -rotate-90", className)}
    >
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        strokeWidth={strokeWidth}
        className="stroke-muted opacity-20"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        className={cn(strokeColor, "transition-all duration-500 ease-out")}
      />
    </svg>
  );
}
