"use client";

import { clearPrivateClientState } from "@/components/auth/client-state";
import { logoutAction } from "@/lib/auth/actions";

export function LogoutControl() {
  return (
    <form
      action={logoutAction}
      onSubmit={() => {
        void clearPrivateClientState();
      }}
    >
      <button className="touch-target rounded-lg border border-[var(--border-subtle)] px-4 text-sm text-[var(--text-secondary)]">
        Log out
      </button>
    </form>
  );
}
