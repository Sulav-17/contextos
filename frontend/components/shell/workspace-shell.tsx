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
  return (
    <div className={preferences.motion_mode === "reduced" ? "motion-reduced" : ""}>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <div className="flex h-dvh overflow-hidden" data-app-shell="workspace">
        <WorkspaceNav isAdmin={user.role === "admin"} />
        <div className="flex min-w-0 flex-1 flex-col pb-[calc(env(safe-area-inset-bottom)+5.75rem)] md:pb-0">
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
              <ThemeControl compact />
              <div className="hidden md:inline-flex">
                <LogoutControl />
              </div>
            </div>
          </header>
          <main
            id="main-content"
            tabIndex={-1}
            className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden px-4 py-6 md:px-8"
          >
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
