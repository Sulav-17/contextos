"use client";

import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from "react";

export type AppearanceMode = "system" | "dark" | "light";

type ThemeContextValue = {
  mode: AppearanceMode;
  setMode: (mode: AppearanceMode) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);
const STORAGE_KEY = "contextos.appearance";

function isAppearanceMode(value: string | null): value is AppearanceMode {
  return value === "system" || value === "dark" || value === "light";
}

function applyTheme(mode: AppearanceMode): void {
  const darkQuery = window.matchMedia("(prefers-color-scheme: dark)");
  const resolved = mode === "system" ? (darkQuery.matches ? "dark" : "light") : mode;
  document.documentElement.dataset.theme = resolved;
  document.documentElement.dataset.appearance = mode;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<AppearanceMode>(() => {
    if (typeof window === "undefined") {
      return "system";
    }
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return isAppearanceMode(stored) ? stored : "system";
  });

  useEffect(() => {
    applyTheme(mode);
    window.localStorage.setItem(STORAGE_KEY, mode);
    const query = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = () => {
      if (mode === "system") {
        applyTheme("system");
      }
    };
    query.addEventListener("change", listener);
    return () => query.removeEventListener("change", listener);
  }, [mode]);

  const value = useMemo(
    () => ({
      mode,
      setMode: setModeState,
    }),
    [mode],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const value = useContext(ThemeContext);
  if (!value) {
    throw new Error("useTheme must be used inside ThemeProvider");
  }
  return value;
}
