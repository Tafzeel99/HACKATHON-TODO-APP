"use client";

import { Repeat } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DatePicker } from "./date-picker";
import { Label } from "@/components/ui/label";
import type { RecurrencePattern } from "@/types/task";

interface RecurrenceSelectorProps {
  pattern: RecurrencePattern;
  endDate: string | null;
  onPatternChange: (pattern: RecurrencePattern) => void;
  onEndDateChange: (date: string | null) => void;
  disabled?: boolean;
}

const recurrenceOptions: { value: RecurrencePattern; label: string }[] = [
  { value: "none", label: "Does not repeat" },
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
];

export function RecurrenceSelector({
  pattern,
  endDate,
  onPatternChange,
  onEndDateChange,
  disabled = false,
}: RecurrenceSelectorProps) {
  return (
    <div className="space-y-3">
      <div className="space-y-1.5">
        <Label className="text-sm text-muted-foreground">Repeat</Label>
        <Select
          value={pattern}
          onValueChange={(value) => onPatternChange(value as RecurrencePattern)}
          disabled={disabled}
        >
          <SelectTrigger className="w-full">
            <Repeat className="h-4 w-4 mr-2 text-muted-foreground" />
            <SelectValue placeholder="Select recurrence" />
          </SelectTrigger>
          <SelectContent>
            {recurrenceOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {pattern !== "none" && (
        <div className="space-y-1.5">
          <Label className="text-sm text-muted-foreground">
            Ends on (optional)
          </Label>
          <DatePicker
            value={endDate}
            onChange={onEndDateChange}
            placeholder="No end date"
            disabled={disabled}
            min={new Date().toISOString().slice(0, 10)}
          />
        </div>
      )}
    </div>
  );
}
