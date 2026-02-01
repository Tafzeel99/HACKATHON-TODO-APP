"use client";

import { useState, useEffect } from "react";
import { Check, Palette } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  AccentColor,
  ACCENT_COLOR_OPTIONS,
  applyTheme,
  getStoredAccentColor,
} from "@/lib/themes";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Label } from "@/components/ui/label";

interface ThemeColorPickerProps {
  className?: string;
  onChange?: (color: AccentColor) => void;
}

export function ThemeColorPicker({ className, onChange }: ThemeColorPickerProps) {
  const [selectedColor, setSelectedColor] = useState<AccentColor>("indigo");
  const [open, setOpen] = useState(false);

  // Load stored color on mount
  useEffect(() => {
    const stored = getStoredAccentColor();
    setSelectedColor(stored);
    applyTheme(stored);
  }, []);

  const handleColorChange = (color: AccentColor) => {
    setSelectedColor(color);
    applyTheme(color);
    onChange?.(color);
    setOpen(false);
  };

  const currentOption = ACCENT_COLOR_OPTIONS.find((o) => o.value === selectedColor);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className={cn("gap-2", className)}>
          <div
            className="w-4 h-4 rounded-full"
            style={{ backgroundColor: currentOption?.hex }}
          />
          <span>{currentOption?.label || "Theme"}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-4" align="start">
        <div className="space-y-3">
          <Label className="text-sm font-medium">Accent Color</Label>
          <div className="grid grid-cols-4 gap-2">
            {ACCENT_COLOR_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => handleColorChange(option.value)}
                className={cn(
                  "w-10 h-10 rounded-lg transition-all duration-200",
                  "flex items-center justify-center",
                  "ring-2 ring-offset-2 ring-offset-background",
                  selectedColor === option.value
                    ? "ring-primary scale-105"
                    : "ring-transparent hover:scale-105"
                )}
                style={{ backgroundColor: option.hex }}
                title={option.label}
              >
                {selectedColor === option.value && (
                  <Check className="h-5 w-5 text-white drop-shadow-md" />
                )}
              </button>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Inline version for settings page
export function ThemeColorGrid({
  value,
  onChange,
  className,
}: {
  value: AccentColor;
  onChange: (color: AccentColor) => void;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-wrap gap-3", className)}>
      {ACCENT_COLOR_OPTIONS.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={cn(
            "relative w-12 h-12 rounded-xl transition-all duration-200",
            "flex items-center justify-center",
            "ring-2 ring-offset-2 ring-offset-background",
            value === option.value
              ? "ring-foreground scale-105"
              : "ring-transparent hover:scale-105"
          )}
          style={{ backgroundColor: option.hex }}
          title={option.label}
        >
          {value === option.value && (
            <Check className="h-5 w-5 text-white drop-shadow-md" />
          )}
        </button>
      ))}
    </div>
  );
}
