"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut, Sparkles, Github, Linkedin, Instagram, Menu, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { Sidebar } from "@/components/layout/sidebar";
import { ErrorBoundary } from "@/components/error-boundary";
import { isAuthenticated, signout } from "@/lib/auth";
import { cn } from "@/lib/utils";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Check authentication on mount
    if (!isAuthenticated()) {
      router.replace("/login");
    } else {
      setIsLoading(false);
    }
  }, [router]);

  const handleLogout = async () => {
    await signout();
    router.replace("/login");
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          {/* Modern loading spinner */}
          <div className="relative">
            <div className="h-16 w-16 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-primary animate-pulse" />
            </div>
          </div>
          <p className="text-sm text-muted-foreground animate-pulse">Loading your workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* Desktop Sidebar */}
      <Sidebar className="hidden lg:flex fixed left-0 top-0 bottom-0 z-40" />

      {/* Mobile Sidebar Overlay */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-background/80 backdrop-blur-sm z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <div
        className={cn(
          "lg:hidden fixed left-0 top-0 bottom-0 z-50 transition-transform duration-300",
          isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <Sidebar />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:ml-[260px] min-h-screen">
        {/* Top Header */}
        <header className="sticky top-0 z-30 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
          <div className="flex h-16 items-center justify-between px-4 lg:px-6">
            {/* Mobile Menu Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden"
            >
              {isMobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>

            {/* Welcome Text (Desktop) */}
            <div className="hidden lg:block">
              <p className="text-sm text-muted-foreground">
                Welcome back! Let&apos;s get things done.
              </p>
            </div>

            {/* Spacer for mobile */}
            <div className="lg:hidden flex-1" />

            {/* Actions */}
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="gap-2 text-muted-foreground hover:text-foreground"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-4 lg:p-8 animate-fade-in">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </main>

        {/* Footer */}
        <footer className="border-t border-border/50 bg-card/30 backdrop-blur-sm">
          <div className="px-4 lg:px-6 py-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              {/* Left - Brand */}
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl gradient-primary shadow-lg shadow-primary/20">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-bold text-gradient">todoX</span>
              </div>

              {/* Center - Copyright */}
              <p className="text-xs text-muted-foreground">
                © 2026 Built by Tafzeel® with ❤️
              </p>

              {/* Right - Social Links */}
              <div className="flex items-center gap-1">
                <a
                  href="https://linkedin.com/in/tafzeel-ahmed-khan-379510366"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-9 w-9 items-center justify-center rounded-xl hover:bg-muted transition-colors"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
                </a>
                <a
                  href="https://github.com/Tafzeel99"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-9 w-9 items-center justify-center rounded-xl hover:bg-muted transition-colors"
                  aria-label="GitHub"
                >
                  <Github className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
                </a>
                <a
                  href="https://www.instagram.com/tafzeel._.here/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-9 w-9 items-center justify-center rounded-xl hover:bg-muted transition-colors"
                  aria-label="Instagram"
                >
                  <Instagram className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
