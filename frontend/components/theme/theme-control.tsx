"use client";

import { Moon, Monitor, Sun } from "lucide-react";

import { AppearanceMode, useTheme } from "@/components/theme/theme-provider";

const options: { value: AppearanceMode; label: string; icon: typeof Monitor }[] = [
  { value: "system", label: "System", icon: Monitor },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "light", label: "Light", icon: Sun },
];

export function ThemeControl({ compact = false }: { compact?: boolean }) {
  const { mode, setMode } = useTheme();
  return (
    <fieldset
      aria-label="Appearance"
      className="inline-flex rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-overlay)] p-1"
    >
      {options.map((option) => {
        const Icon = option.icon;
        return (
          <button
            aria-pressed={mode === option.value}
            className={`touch-target inline-flex items-center justify-center gap-2 rounded-md px-3 text-sm ${
              mode === option.value
                ? "bg-[var(--accent-intelligence)] text-[#061019]"
                : "text-[var(--text-secondary)]"
            }`}
            key={option.value}
            onClick={() => setMode(option.value)}
            title={option.label}
            type="button"
          >
            <Icon aria-hidden="true" size={16} />
            {compact ? <span className="sr-only">{option.label}</span> : option.label}
          </button>
        );
      })}
    </fieldset>
  );
}

