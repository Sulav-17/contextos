"use client";

import { logoutAction } from "@/lib/auth/actions";

export async function clearPrivateClientState() {
  try {
    window.sessionStorage.clear();
    for (const key of Object.keys(window.localStorage)) {
      if (key.startsWith("contextos.")) {
        window.localStorage.removeItem(key);
      }
    }
    if ("caches" in window) {
      const names = await caches.keys();
      await Promise.all(
        names.filter((name) => name.startsWith("contextos-")).map((name) => caches.delete(name)),
      );
    }
  } catch {
    // Best-effort browser cleanup before server-side logout clears the session.
  }
}

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
