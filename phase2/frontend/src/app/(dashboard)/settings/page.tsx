"use client";

import { useState, useEffect } from "react";
import {
  Settings,
  User,
  Bell,
  Palette,
  Shield,
  Save,
  Check,
  Clock,
  Mail,
  Quote,
  LayoutGrid,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { ThemeColorGrid } from "@/components/theme-color-picker";
import { ViewToggle, ViewMode } from "@/components/tasks/view-toggle";
import { AccentColor, applyTheme, getStoredAccentColor } from "@/lib/themes";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl gradient-primary shadow-glow-sm">
          <Settings className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">
            <span className="text-gradient">Settings</span>
          </h1>
          <p className="text-sm text-muted-foreground">
            Manage your preferences and account
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            <SettingsTab
              icon={<User className="h-4 w-4" />}
              label="Profile"
              active={activeTab === "profile"}
              onClick={() => setActiveTab("profile")}
            />
            <SettingsTab
              icon={<Bell className="h-4 w-4" />}
              label="Notifications"
              active={activeTab === "notifications"}
              onClick={() => setActiveTab("notifications")}
            />
            <SettingsTab
              icon={<Palette className="h-4 w-4" />}
              label="Appearance"
              active={activeTab === "appearance"}
              onClick={() => setActiveTab("appearance")}
            />
            <SettingsTab
              icon={<Shield className="h-4 w-4" />}
              label="Privacy"
              active={activeTab === "privacy"}
              onClick={() => setActiveTab("privacy")}
            />
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3 rounded-xl border bg-card p-6">
          {activeTab === "profile" && <ProfileSettings />}
          {activeTab === "notifications" && <NotificationSettings />}
          {activeTab === "appearance" && <AppearanceSettings />}
          {activeTab === "privacy" && <PrivacySettings />}
        </div>
      </div>
    </div>
  );
}

function SettingsTab({
  icon,
  label,
  active,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
        active
          ? "bg-primary text-primary-foreground"
          : "text-muted-foreground hover:bg-muted hover:text-foreground"
      )}
    >
      {icon}
      {label}
    </button>
  );
}

function ProfileSettings() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const handleSave = () => {
    toast({
      title: "Settings saved",
      description: "Your profile has been updated.",
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold">Profile Settings</h3>
        <p className="text-sm text-muted-foreground">
          Update your personal information
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="name">Display Name</Label>
          <Input
            id="name"
            placeholder="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
      </div>

      <Button onClick={handleSave} className="gap-2">
        <Save className="h-4 w-4" />
        Save Changes
      </Button>
    </div>
  );
}

function NotificationSettings() {
  const [emailReminders, setEmailReminders] = useState(true);
  const [overdueAlerts, setOverdueAlerts] = useState(true);
  const [dailyDigest, setDailyDigest] = useState(false);
  const [digestTime, setDigestTime] = useState("09:00");

  const handleSave = () => {
    // In real implementation, call API to save preferences
    toast({
      title: "Settings saved",
      description: "Your notification preferences have been updated.",
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold">Notification Settings</h3>
        <p className="text-sm text-muted-foreground">
          Configure how you receive notifications
        </p>
      </div>

      <div className="space-y-4">
        <ToggleOption
          icon={<Mail className="h-4 w-4 text-muted-foreground" />}
          title="Email Reminders"
          description="Receive email notifications about upcoming task deadlines"
          enabled={emailReminders}
          onToggle={() => setEmailReminders(!emailReminders)}
        />
        <ToggleOption
          icon={<Bell className="h-4 w-4 text-muted-foreground" />}
          title="Overdue Alerts"
          description="Get notified when tasks become overdue"
          enabled={overdueAlerts}
          onToggle={() => setOverdueAlerts(!overdueAlerts)}
        />
        <ToggleOption
          icon={<Clock className="h-4 w-4 text-muted-foreground" />}
          title="Daily Digest"
          description="Receive a daily summary of your tasks via email"
          enabled={dailyDigest}
          onToggle={() => setDailyDigest(!dailyDigest)}
        />

        {dailyDigest && (
          <div className="ml-4 pl-4 border-l-2 border-primary/20 space-y-2">
            <Label htmlFor="digestTime" className="text-sm">
              Digest Time
            </Label>
            <Input
              id="digestTime"
              type="time"
              value={digestTime}
              onChange={(e) => setDigestTime(e.target.value)}
              className="w-32"
            />
            <p className="text-xs text-muted-foreground">
              We'll send your daily digest at this time
            </p>
          </div>
        )}
      </div>

      <Button onClick={handleSave} className="gap-2">
        <Save className="h-4 w-4" />
        Save Changes
      </Button>
    </div>
  );
}

function AppearanceSettings() {
  const [accentColor, setAccentColor] = useState<AccentColor>("indigo");
  const [defaultView, setDefaultView] = useState<ViewMode>("list");
  const [showQuotes, setShowQuotes] = useState(true);

  useEffect(() => {
    const stored = getStoredAccentColor();
    setAccentColor(stored);
  }, []);

  const handleColorChange = (color: AccentColor) => {
    setAccentColor(color);
    applyTheme(color);
    toast({
      title: "Theme updated",
      description: `Accent color changed to ${color}.`,
    });
  };

  const handleSave = () => {
    // In real implementation, call API to save preferences
    localStorage.setItem("default-view", defaultView);
    localStorage.setItem("show-quotes", String(showQuotes));
    toast({
      title: "Settings saved",
      description: "Your appearance preferences have been updated.",
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold">Appearance Settings</h3>
        <p className="text-sm text-muted-foreground">
          Customize the look and feel of the app
        </p>
      </div>

      <div className="p-4 rounded-lg bg-muted/50 border">
        <p className="text-sm text-muted-foreground">
          Use the theme toggle in the header to switch between light and dark mode.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-medium mb-3">Accent Color</h4>
          <ThemeColorGrid value={accentColor} onChange={handleColorChange} />
        </div>

        <div>
          <h4 className="text-sm font-medium mb-3">Default Task View</h4>
          <div className="flex items-center gap-4">
            <ViewToggle value={defaultView} onChange={setDefaultView} />
            <span className="text-sm text-muted-foreground capitalize">
              {defaultView} view
            </span>
          </div>
        </div>

        <ToggleOption
          icon={<Quote className="h-4 w-4 text-muted-foreground" />}
          title="Motivational Quotes"
          description="Show inspirational quotes on the dashboard"
          enabled={showQuotes}
          onToggle={() => setShowQuotes(!showQuotes)}
        />
      </div>

      <Button onClick={handleSave} className="gap-2">
        <Save className="h-4 w-4" />
        Save Changes
      </Button>
    </div>
  );
}

function PrivacySettings() {
  const [shareAnalytics, setShareAnalytics] = useState(false);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold">Privacy Settings</h3>
        <p className="text-sm text-muted-foreground">
          Control your data and privacy preferences
        </p>
      </div>

      <div className="space-y-4">
        <ToggleOption
          title="Share Analytics"
          description="Help us improve by sharing anonymous usage data"
          enabled={shareAnalytics}
          onToggle={() => setShareAnalytics(!shareAnalytics)}
        />
      </div>

      <div className="pt-4 border-t">
        <h4 className="text-sm font-medium mb-2">Data Management</h4>
        <div className="flex gap-3">
          <Button variant="outline" size="sm">
            Export Data
          </Button>
          <Button variant="destructive" size="sm">
            Delete Account
          </Button>
        </div>
      </div>
    </div>
  );
}

function ToggleOption({
  icon,
  title,
  description,
  enabled,
  onToggle,
}: {
  icon?: React.ReactNode;
  title: string;
  description: string;
  enabled: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/30 transition-colors">
      <div className="flex items-start gap-3">
        {icon && <div className="mt-0.5">{icon}</div>}
        <div>
          <p className="text-sm font-medium">{title}</p>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      </div>
      <button
        onClick={onToggle}
        className={cn(
          "relative h-6 w-11 rounded-full transition-colors shrink-0",
          enabled ? "bg-primary" : "bg-muted"
        )}
      >
        <span
          className={cn(
            "absolute top-1 left-1 h-4 w-4 rounded-full bg-white transition-transform",
            enabled && "translate-x-5"
          )}
        />
      </button>
    </div>
  );
}
