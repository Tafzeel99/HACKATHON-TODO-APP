"use client";

import { useState } from "react";
import { Check, ChevronsUpDown, Loader2, UserPlus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { UserAvatar } from "./user-avatar";
import { userApi } from "@/lib/api";
import type { User } from "@/types/task";

interface AssigneeSelectProps {
  value?: User | null;
  onChange?: (user: User | null) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function AssigneeSelect({
  value,
  onChange,
  disabled,
  placeholder = "Assign to...",
}: AssigneeSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (query: string) => {
    setSearch(query);
    if (query.length < 2) {
      setUsers([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await userApi.search(query);
      setUsers(response.users);
    } catch (error) {
      console.error("Failed to search users:", error);
      setUsers([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (user: User) => {
    onChange?.(user);
    setOpen(false);
    setSearch("");
    setUsers([]);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.(null);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "w-full justify-between",
            !value && "text-muted-foreground"
          )}
          disabled={disabled}
        >
          {value ? (
            <div className="flex items-center gap-2">
              <UserAvatar user={value} size="sm" showTooltip={false} />
              <span className="truncate">{value.name || value.email}</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <UserPlus className="h-4 w-4" />
              {placeholder}
            </div>
          )}
          <div className="flex items-center gap-1">
            {value && (
              <X
                className="h-4 w-4 opacity-50 hover:opacity-100 cursor-pointer"
                onClick={handleClear}
              />
            )}
            <ChevronsUpDown className="h-4 w-4 opacity-50" />
          </div>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder="Search users..."
            value={search}
            onValueChange={handleSearch}
          />
          <CommandList>
            {isLoading ? (
              <div className="flex items-center justify-center py-6">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            ) : search.length < 2 ? (
              <CommandEmpty>Type at least 2 characters to search</CommandEmpty>
            ) : users.length === 0 ? (
              <CommandEmpty>No users found</CommandEmpty>
            ) : (
              <CommandGroup>
                {users.map((user) => (
                  <CommandItem
                    key={user.id}
                    value={user.id}
                    onSelect={() => handleSelect(user)}
                    className="flex items-center gap-2"
                  >
                    <UserAvatar user={user} size="sm" showTooltip={false} />
                    <div className="flex-1 min-w-0">
                      <p className="truncate text-sm">
                        {user.name || user.email}
                      </p>
                      {user.name && (
                        <p className="truncate text-xs text-muted-foreground">
                          {user.email}
                        </p>
                      )}
                    </div>
                    {value?.id === user.id && (
                      <Check className="h-4 w-4 text-primary" />
                    )}
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
