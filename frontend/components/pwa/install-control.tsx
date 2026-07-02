"use client";

import { Download } from "lucide-react";

import { useInstallPrompt } from "@/lib/pwa/install";

export function InstallControl({ compact = false }: { compact?: boolean }) {
  const { promptInstall, state } = useInstallPrompt();
  const unavailable = state === "checking" || state === "unavailable" || state === "installed";
  const label =
    state === "installed"
      ? "Installed"
      : state === "ios-guidance"
        ? "Add to Home Screen from Share"
        : "Install app";

  return (
    <button
      aria-label={label}
      className="touch-target inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm text-[var(--text-secondary)] disabled:opacity-60"
      data-testid="install-control"
      disabled={unavailable}
      onClick={promptInstall}
      title={state === "ios-guidance" ? "Use Safari Share, then Add to Home Screen." : label}
      type="button"
    >
      <Download aria-hidden="true" size={16} />
      {compact ? <span className="sr-only">{label}</span> : <span>{label}</span>}
    </button>
  );
}
