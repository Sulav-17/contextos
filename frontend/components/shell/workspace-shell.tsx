import { ReactNode } from "react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { WorkspaceNav } from "@/components/navigation/workspace-nav";
import { ThemeControl } from "@/components/theme/theme-control";
import { logoutAction } from "@/lib/auth/actions";
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
      <div className="flex h-dvh overflow-hidden">
        <WorkspaceNav isAdmin={user.role === "admin"} />
        <div className="flex min-w-0 flex-1 flex-col pb-24 md:pb-0">
          <header className="flex items-center justify-between gap-3 border-b border-[var(--border-subtle)] px-4 py-4 md:px-8">
            <AssistantOrb state="ready" reducedMotion={preferences.motion_mode === "reduced"} />
            <div className="flex items-center gap-3">
              <ThemeControl compact />
              <form action={logoutAction}>
                <button className="touch-target rounded-lg border border-[var(--border-subtle)] px-4 text-sm text-[var(--text-secondary)]">
                  Log out
                </button>
              </form>
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
