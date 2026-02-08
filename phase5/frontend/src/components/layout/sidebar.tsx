"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ListTodo,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Calendar,
  BarChart3,
  HelpCircle,
  Bot,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface NavItem {
  title: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
  isAgent?: boolean;
}

const mainNavItems: NavItem[] = [
  {
    title: "Dashboard",
    href: "/",
    icon: <LayoutDashboard className="h-5 w-5" />,
  },
  {
    title: "My Tasks",
    href: "/tasks",
    icon: <ListTodo className="h-5 w-5" />,
  },
  {
    title: "TodoX Agent",
    href: "/chat",
    icon: <Bot className="h-5 w-5" />,
    badge: "AI",
    isAgent: true,
  },
];

const secondaryNavItems: NavItem[] = [
  {
    title: "Analytics",
    href: "/analytics",
    icon: <BarChart3 className="h-5 w-5" />,
  },
  {
    title: "Calendar",
    href: "/calendar",
    icon: <Calendar className="h-5 w-5" />,
  },
];

const bottomNavItems: NavItem[] = [
  {
    title: "Settings",
    href: "/settings",
    icon: <Settings className="h-5 w-5" />,
  },
  {
    title: "Help",
    href: "/help",
    icon: <HelpCircle className="h-5 w-5" />,
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const NavLink = ({ item }: { item: NavItem }) => {
    const isActive = pathname === item.href ||
      (item.href !== "/" && pathname?.startsWith(item.href));

    return (
      <Link href={item.href}>
        <div
          className={cn(
            "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
            isActive
              ? "bg-gradient-to-r from-primary to-[hsl(var(--gradient-end))] text-white shadow-lg shadow-primary/25"
              : "text-muted-foreground hover:bg-muted hover:text-foreground",
            item.isAgent && !isActive && "hover:bg-primary/5",
            isCollapsed && "justify-center px-2"
          )}
        >
          <div className={cn(
            "flex-shrink-0 transition-transform duration-200",
            !isActive && "group-hover:scale-110",
            item.isAgent && !isActive && "text-primary"
          )}>
            {item.icon}
          </div>
          {!isCollapsed && (
            <>
              <span className="flex-1">{item.title}</span>
              {item.badge && (
                <span className={cn(
                  "flex h-5 items-center rounded-full px-2 text-[10px] font-bold",
                  isActive
                    ? "bg-white/20 text-white"
                    : "bg-gradient-to-r from-violet-500 to-purple-500 text-white"
                )}>
                  {item.badge}
                </span>
              )}
            </>
          )}
        </div>
      </Link>
    );
  };

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-border/50 bg-card/50 backdrop-blur-xl transition-all duration-300",
        isCollapsed ? "w-[72px]" : "w-[260px]",
        className
      )}
    >
      {/* Collapse Toggle */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-6 z-10 h-6 w-6 rounded-full border border-border/50 bg-background shadow-lg hover:bg-muted hover:shadow-xl transition-all"
      >
        {isCollapsed ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronLeft className="h-3 w-3" />
        )}
      </Button>

      {/* Logo Section */}
      <div className={cn(
        "flex h-16 items-center border-b border-border/50 px-4",
        isCollapsed && "justify-center px-2"
      )}>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl gradient-primary shadow-lg shadow-primary/30">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="text-lg font-bold text-gradient">todoX</span>
              <span className="text-[10px] text-muted-foreground font-medium">AI-Powered Tasks</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 space-y-1 p-3">
        <div className="space-y-1">
          {!isCollapsed && (
            <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Main
            </p>
          )}
          {mainNavItems.map((item) => (
            <NavLink key={item.href} item={item} />
          ))}
        </div>

        <div className="my-4 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div className="space-y-1">
          {!isCollapsed && (
            <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Features
            </p>
          )}
          {secondaryNavItems.map((item) => (
            <NavLink key={item.href} item={item} />
          ))}
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="border-t border-border/50 p-3 space-y-1">
        {bottomNavItems.map((item) => (
          <NavLink key={item.href} item={item} />
        ))}
      </div>

      {/* Agent Promo Card (when expanded) */}
      {!isCollapsed && (
        <div className="p-3">
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/10 via-purple-500/10 to-pink-500/10 p-4 border border-primary/20">
            {/* Decorative elements */}
            <div className="absolute -right-8 -top-8 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="absolute -left-4 -bottom-4 w-16 h-16 bg-[hsl(var(--gradient-end))]/10 rounded-full blur-xl" />

            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <div className="p-1.5 rounded-lg bg-primary/10">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <span className="text-xs font-semibold">TodoX Agent</span>
              </div>
              <p className="text-[11px] text-muted-foreground mb-3 leading-relaxed">
                Manage tasks with natural language commands
              </p>
              <Link href="/chat">
                <Button size="sm" className="w-full h-9 text-xs font-semibold gradient-primary shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all">
                  <Zap className="h-3.5 w-3.5 mr-1.5" />
                  Try Now
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
