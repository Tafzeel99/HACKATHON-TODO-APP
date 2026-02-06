import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind CSS classes with clsx.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a date string to a human-readable format.
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format a date string to include time.
 */
export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Format a relative time string (e.g., "2 hours ago").
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return "just now";
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes === 1 ? "" : "s"} ago`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours === 1 ? "" : "s"} ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays === 1 ? "" : "s"} ago`;
  }

  return formatDate(dateString);
}

/**
 * Format a date string as relative time from now (e.g., "2 hours ago", "in 3 days").
 * Handles both past and future dates.
 */
export function formatDistanceToNow(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = date.getTime() - now.getTime();
  const isPast = diffInMs < 0;
  const absDiffInSeconds = Math.abs(Math.floor(diffInMs / 1000));

  if (absDiffInSeconds < 60) {
    return isPast ? "just now" : "in a moment";
  }

  const diffInMinutes = Math.floor(absDiffInSeconds / 60);
  if (diffInMinutes < 60) {
    const unit = diffInMinutes === 1 ? "minute" : "minutes";
    return isPast ? `${diffInMinutes} ${unit} ago` : `in ${diffInMinutes} ${unit}`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    const unit = diffInHours === 1 ? "hour" : "hours";
    return isPast ? `${diffInHours} ${unit} ago` : `in ${diffInHours} ${unit}`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    const unit = diffInDays === 1 ? "day" : "days";
    return isPast ? `${diffInDays} ${unit} ago` : `in ${diffInDays} ${unit}`;
  }

  if (diffInDays < 30) {
    const diffInWeeks = Math.floor(diffInDays / 7);
    const unit = diffInWeeks === 1 ? "week" : "weeks";
    return isPast ? `${diffInWeeks} ${unit} ago` : `in ${diffInWeeks} ${unit}`;
  }

  if (diffInDays < 365) {
    const diffInMonths = Math.floor(diffInDays / 30);
    const unit = diffInMonths === 1 ? "month" : "months";
    return isPast ? `${diffInMonths} ${unit} ago` : `in ${diffInMonths} ${unit}`;
  }

  const diffInYears = Math.floor(diffInDays / 365);
  const unit = diffInYears === 1 ? "year" : "years";
  return isPast ? `${diffInYears} ${unit} ago` : `in ${diffInYears} ${unit}`;
}
