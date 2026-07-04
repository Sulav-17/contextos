import { ReactNode } from "react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { LogoutControl } from "@/components/auth/logout-control";
import { WorkspaceNav } from "@/components/navigation/workspace-nav";
import { InstallControl } from "@/components/pwa/install-control";
import { OfflineStatus } from "@/components/pwa/offline-status";
import { ThemeControl } from "@/components/theme/theme-control";
import type { Me, Preferences } from "@/lib/api/types";

export function WorkspaceShell({
  children,
  user,
  preferences,
}: {
  children: ReactNode;
  user: Me;
  preferences: Preferences;
}) {
  const shellClassName =
    preferences.motion_mode === "reduced"
      ? "motion-reduced h-dvh max-h-dvh min-h-0 overflow-hidden"
      : "h-dvh max-h-dvh min-h-0 overflow-hidden";

  return (
    <div className={shellClassName} data-testid="workspace-root" data-workspace-root="true">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <div className="flex h-full min-h-0 overflow-hidden" data-app-shell="workspace">
        <WorkspaceNav isAdmin={user.role === "admin"} />
        <div className="grid min-h-0 min-w-0 flex-1 grid-rows-[auto_minmax(0,1fr)] overflow-hidden pb-[calc(env(safe-area-inset-bottom)+5.75rem)] md:pb-0">
          <div className="min-w-0 flex-none">
            <OfflineStatus />
            <header className="flex min-h-16 min-w-0 items-center justify-between gap-2 overflow-x-hidden border-b border-[var(--border-subtle)] px-3 py-2 md:px-8 md:py-4">
              <AssistantOrb
                state="ready"
                reducedMotion={preferences.motion_mode === "reduced"}
              />
              <div className="flex min-w-0 items-center justify-end gap-2">
                <div className="hidden md:inline-flex">
                  <InstallControl compact />
                </div>
                <div className="hidden md:inline-flex">
                  <ThemeControl compact />
                </div>
                <div className="hidden md:inline-flex">
                  <LogoutControl />
                </div>
              </div>
            </header>
          </div>
          <main
            id="main-content"
            data-testid="workspace-main-scroll"
            tabIndex={-1}
            className="min-h-0 min-w-0 overflow-y-auto overflow-x-hidden overscroll-contain px-4 py-6 [scrollbar-gutter:stable] md:px-8"
          >
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
