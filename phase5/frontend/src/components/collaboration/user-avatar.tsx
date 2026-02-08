"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

interface UserAvatarProps {
  user: {
    id: string;
    email: string;
    name?: string | null;
  };
  size?: "sm" | "md" | "lg";
  showTooltip?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: "h-6 w-6 text-xs",
  md: "h-8 w-8 text-sm",
  lg: "h-10 w-10 text-base",
};

function getInitials(name: string | null | undefined, email: string): string {
  if (name) {
    const parts = name.trim().split(" ");
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

function getAvatarColor(id: string): string {
  const colors = [
    "bg-red-500",
    "bg-orange-500",
    "bg-amber-500",
    "bg-yellow-500",
    "bg-lime-500",
    "bg-green-500",
    "bg-emerald-500",
    "bg-teal-500",
    "bg-cyan-500",
    "bg-sky-500",
    "bg-blue-500",
    "bg-indigo-500",
    "bg-violet-500",
    "bg-purple-500",
    "bg-fuchsia-500",
    "bg-pink-500",
  ];

  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

export function UserAvatar({
  user,
  size = "md",
  showTooltip = true,
  className,
}: UserAvatarProps) {
  const initials = getInitials(user.name, user.email);
  const bgColor = getAvatarColor(user.id);

  const avatar = (
    <Avatar className={cn(sizeClasses[size], className)}>
      <AvatarImage src={undefined} alt={user.name || user.email} />
      <AvatarFallback className={cn(bgColor, "text-white font-medium")}>
        {initials}
      </AvatarFallback>
    </Avatar>
  );

  if (!showTooltip) {
    return avatar;
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{avatar}</TooltipTrigger>
        <TooltipContent>
          <p className="font-medium">{user.name || "Unknown"}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

interface UserAvatarGroupProps {
  users: Array<{
    id: string;
    email: string;
    name?: string | null;
  }>;
  max?: number;
  size?: "sm" | "md" | "lg";
}

export function UserAvatarGroup({
  users,
  max = 3,
  size = "sm",
}: UserAvatarGroupProps) {
  const visibleUsers = users.slice(0, max);
  const remainingCount = users.length - max;

  return (
    <div className="flex -space-x-2">
      {visibleUsers.map((user) => (
        <UserAvatar
          key={user.id}
          user={user}
          size={size}
          className="ring-2 ring-background"
        />
      ))}
      {remainingCount > 0 && (
        <div
          className={cn(
            sizeClasses[size],
            "flex items-center justify-center rounded-full bg-muted ring-2 ring-background"
          )}
        >
          <span className="text-muted-foreground">+{remainingCount}</span>
        </div>
      )}
    </div>
  );
}
