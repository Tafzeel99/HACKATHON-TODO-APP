"use client";

import { useState, useRef, useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  suggestions?: string[];
  maxTags?: number;
  maxLength?: number;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

const tagColors = [
  "bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300",
  "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
  "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300",
  "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-300",
  "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
];

function getTagColor(tag: string): string {
  const hash = tag.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return tagColors[hash % tagColors.length];
}

export function TagInput({
  value,
  onChange,
  suggestions = [],
  maxTags = 10,
  maxLength = 30,
  placeholder = "Add tag...",
  disabled = false,
  className,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const filteredSuggestions = suggestions.filter(
    (s) =>
      s.toLowerCase().includes(inputValue.toLowerCase()) &&
      !value.includes(s.toLowerCase())
  );

  const addTag = (tag: string) => {
    const normalizedTag = tag.trim().toLowerCase();
    if (
      normalizedTag &&
      normalizedTag.length <= maxLength &&
      value.length < maxTags &&
      !value.includes(normalizedTag)
    ) {
      onChange([...value, normalizedTag]);
      setInputValue("");
      setShowSuggestions(false);
    }
  };

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && inputValue) {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1]);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <div className="flex flex-wrap gap-1.5 p-2 rounded-md border bg-background min-h-[42px]">
        {value.map((tag) => (
          <span
            key={tag}
            className={cn(
              "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
              getTagColor(tag)
            )}
          >
            {tag}
            {!disabled && (
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="hover:opacity-70"
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </span>
        ))}
        {value.length < maxTags && !disabled && (
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onKeyDown={handleKeyDown}
            placeholder={value.length === 0 ? placeholder : ""}
            className="flex-1 min-w-[80px] bg-transparent outline-none text-sm"
            maxLength={maxLength}
          />
        )}
      </div>

      {showSuggestions && filteredSuggestions.length > 0 && (
        <div className="absolute z-10 mt-1 w-full rounded-md border bg-popover shadow-lg">
          <ul className="py-1 max-h-40 overflow-auto">
            {filteredSuggestions.map((suggestion) => (
              <li key={suggestion}>
                <button
                  type="button"
                  onClick={() => addTag(suggestion)}
                  className="w-full px-3 py-1.5 text-left text-sm hover:bg-accent"
                >
                  {suggestion}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {value.length >= maxTags && (
        <p className="text-xs text-muted-foreground mt-1">
          Maximum {maxTags} tags allowed
        </p>
      )}
    </div>
  );
}
