"use client";

import { useState, useEffect } from "react";
import { Quote as QuoteIcon, RefreshCw } from "lucide-react";
import { getQuoteOfTheDay, getRandomQuote, Quote } from "@/lib/quotes";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface QuoteWidgetProps {
  className?: string;
  showRefresh?: boolean;
}

export function QuoteWidget({ className, showRefresh = true }: QuoteWidgetProps) {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    setQuote(getQuoteOfTheDay());
  }, []);

  const handleRefresh = () => {
    setIsAnimating(true);
    setTimeout(() => {
      setQuote(getRandomQuote());
      setIsAnimating(false);
    }, 300);
  };

  if (!quote) return null;

  return (
    <div
      className={cn(
        "relative p-6 rounded-xl bg-gradient-to-br from-primary/10 via-background to-[hsl(var(--gradient-end))]/10",
        "border border-primary/20",
        className
      )}
    >
      {/* Quote icon */}
      <div className="absolute top-4 left-4 opacity-20">
        <QuoteIcon className="h-8 w-8 text-primary" />
      </div>

      {/* Content */}
      <div
        className={cn(
          "relative pl-6",
          isAnimating && "animate-quote-fade"
        )}
      >
        <blockquote className="text-lg font-medium text-foreground leading-relaxed">
          "{quote.text}"
        </blockquote>
        <cite className="block mt-3 text-sm text-muted-foreground not-italic">
          — {quote.author}
        </cite>
      </div>

      {/* Refresh button */}
      {showRefresh && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRefresh}
          className="absolute top-2 right-2 h-8 w-8 p-0 text-muted-foreground hover:text-primary"
          title="Get new quote"
        >
          <RefreshCw
            className={cn("h-4 w-4", isAnimating && "animate-spin")}
          />
        </Button>
      )}
    </div>
  );
}

// Compact version for smaller spaces
export function QuoteWidgetCompact({ className }: { className?: string }) {
  const [quote, setQuote] = useState<Quote | null>(null);

  useEffect(() => {
    setQuote(getQuoteOfTheDay());
  }, []);

  if (!quote) return null;

  return (
    <div
      className={cn(
        "p-4 rounded-lg bg-muted/50 border border-border",
        className
      )}
    >
      <p className="text-sm text-muted-foreground italic">
        "{quote.text}"
      </p>
      <p className="mt-1 text-xs text-muted-foreground/70">
        — {quote.author}
      </p>
    </div>
  );
}
