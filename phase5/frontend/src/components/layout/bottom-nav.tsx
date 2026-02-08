"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Home, CheckSquare, Calendar, Settings, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  icon: typeof Home;
  label: string;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/", icon: Home, label: "Home" },
  { href: "/tasks", icon: CheckSquare, label: "Tasks" },
  { href: "/calendar", icon: Calendar, label: "Calendar" },
  { href: "/analytics", icon: BarChart3, label: "Analytics" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="bottom-nav md:hidden">
      <div className="flex items-center justify-around h-16">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn("bottom-nav-item", isActive && "active")}
            >
              <Icon className={cn("h-5 w-5", isActive && "text-primary")} />
              <span className={cn("text-xs mt-1", isActive && "text-primary font-medium")}>
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
