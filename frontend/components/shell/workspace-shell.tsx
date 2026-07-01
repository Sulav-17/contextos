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
      <div className="flex min-h-dvh">
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
          <div className="grid min-h-0 flex-1 grid-cols-1 xl:grid-cols-[minmax(0,1fr)_340px]">
            <main id="main-content" tabIndex={-1} className="min-w-0 px-4 py-6 md:px-8">
              {children}
            </main>
            <aside
              aria-label="Context inspector"
              className="hidden border-l border-[var(--border-subtle)] bg-[var(--surface-inspector)] p-6 xl:block"
            >
              <h2 className="text-sm font-semibold text-[var(--text-secondary)]">
                Context inspector
              </h2>
              <p className="mt-3 text-sm leading-6 text-[var(--text-muted)]">
                Source details, selected documents, and citation evidence stay visible while you
                work through grounded conversations.
              </p>
            </aside>
          </div>
        </div>
      </div>
    </div>
  );
}
