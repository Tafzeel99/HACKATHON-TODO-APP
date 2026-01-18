"use client";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { Calendar, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DatePickerProps {
  value: string | null;
  onChange: (date: string | null) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  includeTime?: boolean;
  min?: string;
}

export function DatePicker({
  value,
  onChange,
  placeholder = "Select date",
  disabled = false,
  className,
  includeTime = false,
  min,
}: DatePickerProps) {
  const inputType = includeTime ? "datetime-local" : "date";

  const formatValue = (val: string | null): string => {
    if (!val) return "";
    const date = new Date(val);
    if (includeTime) {
      return date.toISOString().slice(0, 16);
    }
    return date.toISOString().slice(0, 10);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    if (newValue) {
      onChange(new Date(newValue).toISOString());
    } else {
      onChange(null);
    }
  };

  const handleClear = () => {
    onChange(null);
  };

  return (
    <div className={cn("relative", className)}>
      <div className="relative">
        <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
        <Input
          type={inputType}
          value={formatValue(value)}
          onChange={handleChange}
          disabled={disabled}
          className="pl-10 pr-8"
          min={min}
          placeholder={placeholder}
        />
        {value && !disabled && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={handleClear}
            className="absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6 text-muted-foreground hover:text-foreground"
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
    </div>
  );
}
