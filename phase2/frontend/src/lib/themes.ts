/**
 * Theme configuration for accent colors.
 */

export type AccentColor =
  | "indigo"
  | "purple"
  | "blue"
  | "green"
  | "orange"
  | "pink"
  | "red"
  | "teal";

export interface ThemeColors {
  primary: string;
  primaryForeground: string;
  gradientEnd: string;
  ring: string;
}

export const THEME_COLORS: Record<AccentColor, ThemeColors> = {
  indigo: {
    primary: "239 84% 67%",
    primaryForeground: "0 0% 100%",
    gradientEnd: "262 83% 58%",
    ring: "239 84% 67%",
  },
  purple: {
    primary: "262 83% 58%",
    primaryForeground: "0 0% 100%",
    gradientEnd: "280 73% 58%",
    ring: "262 83% 58%",
  },
  blue: {
    primary: "217 91% 60%",
    primaryForeground: "0 0% 100%",
    gradientEnd: "199 89% 48%",
    ring: "217 91% 60%",
  },
  green: {
    primary: "142 71% 45%",
    primaryForeground: "0 0% 100%",
    gradientEnd: "160 84% 39%",
    ring: "142 71% 45%",
  },
  orange: {
    primary: "24 95% 53%",
    primaryForeground: "0 0% 100%",
    gradientEnd: "38 92% 50%",
    ring: "24 95% 53%",
  },
  pink: {
    primary: "330 81% 60%",
    primaryForeground: "0 0% 100%",
    gradientEnd: "350 80% 60%",
    ring: "330 81% 60%",
  },
  red: {
    primary: "0 84% 60%",
    primaryForeground: "0 0% 100%",
    gradientEnd: "350 80% 55%",
    ring: "0 84% 60%",
  },
  teal: {
    primary: "172 66% 50%",
    primaryForeground: "0 0% 100%",
    gradientEnd: "160 84% 39%",
    ring: "172 66% 50%",
  },
};

export const ACCENT_COLOR_OPTIONS: { value: AccentColor; label: string; hex: string }[] = [
  { value: "indigo", label: "Indigo", hex: "#6366f1" },
  { value: "purple", label: "Purple", hex: "#8b5cf6" },
  { value: "blue", label: "Blue", hex: "#3b82f6" },
  { value: "green", label: "Green", hex: "#22c55e" },
  { value: "orange", label: "Orange", hex: "#f97316" },
  { value: "pink", label: "Pink", hex: "#ec4899" },
  { value: "red", label: "Red", hex: "#ef4444" },
  { value: "teal", label: "Teal", hex: "#14b8a6" },
];

export function applyTheme(accentColor: AccentColor): void {
  const colors = THEME_COLORS[accentColor];
  const root = document.documentElement;

  root.style.setProperty("--primary", colors.primary);
  root.style.setProperty("--primary-foreground", colors.primaryForeground);
  root.style.setProperty("--gradient-end", colors.gradientEnd);
  root.style.setProperty("--ring", colors.ring);

  // Store in localStorage for persistence
  localStorage.setItem("accent-color", accentColor);
}

export function getStoredAccentColor(): AccentColor {
  if (typeof window === "undefined") return "indigo";
  return (localStorage.getItem("accent-color") as AccentColor) || "indigo";
}
