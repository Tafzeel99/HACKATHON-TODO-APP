"use client";

import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorFallbackProps {
  error: Error | null;
  onReset?: () => void;
  title?: string;
  description?: string;
}

export function ErrorFallback({
  error,
  onReset,
  title = "Something went wrong",
  description = "An unexpected error occurred. Please try again.",
}: ErrorFallbackProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
      <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
        <AlertCircle className="w-8 h-8 text-destructive" />
      </div>

      <h2 className="text-xl font-semibold mb-2">{title}</h2>
      <p className="text-muted-foreground mb-4 max-w-md">{description}</p>

      {error && process.env.NODE_ENV === "development" && (
        <details className="mb-4 max-w-lg">
          <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
            Error details
          </summary>
          <pre className="mt-2 p-4 bg-muted rounded-lg text-left text-xs overflow-auto max-h-40">
            {error.message}
            {error.stack && `\n\n${error.stack}`}
          </pre>
        </details>
      )}

      {onReset && (
        <Button onClick={onReset} variant="outline" className="gap-2">
          <RefreshCw className="w-4 h-4" />
          Try again
        </Button>
      )}
    </div>
  );
}

export function ErrorFallbackCompact({
  error,
  onReset,
}: ErrorFallbackProps) {
  return (
    <div className="flex items-center gap-3 p-4 bg-destructive/5 border border-destructive/20 rounded-lg">
      <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">Error loading content</p>
        {error && (
          <p className="text-xs text-muted-foreground truncate">
            {error.message}
          </p>
        )}
      </div>
      {onReset && (
        <Button onClick={onReset} variant="ghost" size="sm">
          Retry
        </Button>
      )}
    </div>
  );
}
