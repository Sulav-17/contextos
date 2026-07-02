"use client";

import Link from "next/link";
import { Download, LogOut, MoreHorizontal, X } from "lucide-react";
import { useEffect, useState } from "react";

import { clearPrivateClientState } from "@/components/auth/client-state";
import { secondaryNavItems } from "@/components/navigation/nav-items";
import { ThemeControl } from "@/components/theme/theme-control";
import { logoutAction } from "@/lib/auth/actions";
import { useInstallPrompt } from "@/lib/pwa/install";

function InstallMenuAction({ onDone }: { onDone: () => void }) {
  const { promptInstall, state } = useInstallPrompt();
  const label =
    state === "ios-guidance"
      ? "Add to Home Screen"
      : state === "installed"
        ? "Installed"
        : "Install app";
  const disabled = state === "checking" || state === "installed" || state === "unavailable";

  return (
    <button
      className="touch-target flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-[var(--text-secondary)] disabled:opacity-60"
      disabled={disabled}
      onClick={() => {
        void promptInstall();
        onDone();
      }}
      type="button"
    >
      <Download aria-hidden="true" size={18} />
      <span className="whitespace-nowrap">{label}</span>
    </button>
  );
}

export function MobileMore({ isAdmin }: { isAdmin: boolean }) {
  const [open, setOpen] = useState(false);
  const items = secondaryNavItems.filter((item) => !item.adminOnly || isAdmin);

  useEffect(() => {
    if (!open) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open]);

  return (
    <>
      <button
        aria-expanded={open}
        aria-label="Open more menu"
        className="touch-target flex flex-1 flex-col items-center justify-center gap-1 rounded-xl text-xs text-[var(--text-secondary)]"
        onClick={() => setOpen(true)}
        type="button"
      >
        <MoreHorizontal aria-hidden="true" size={20} />
        <span>More</span>
      </button>

      {open ? (
        <>
          <button
            aria-label="Close more menu"
            className="fixed inset-0 z-40 cursor-default bg-black/60"
            data-testid="mobile-more-overlay"
            onClick={() => setOpen(false)}
            type="button"
          />
          <div
            aria-label="More navigation"
            aria-modal="true"
            className="fixed inset-x-3 bottom-[calc(env(safe-area-inset-bottom)+0.75rem)] z-50 max-h-[calc(100dvh-1.5rem)] w-[calc(100vw-1.5rem)] max-w-[28rem] overflow-y-auto rounded-3xl border border-[var(--border-subtle)] bg-[var(--surface-overlay)] p-4 shadow-[var(--shadow-panel)]"
            role="dialog"
          >
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold">More navigation</h2>
              <button
                aria-label="Close menu"
                className="touch-target rounded-full"
                onClick={() => setOpen(false)}
                type="button"
              >
                <X aria-hidden="true" />
              </button>
            </div>
            <nav aria-label="Secondary mobile navigation" className="grid gap-2">
              {items.map((item) => (
                <Link
                  className="touch-target flex items-center gap-3 rounded-xl px-3 py-3 text-sm"
                  href={item.href}
                  key={item.href}
                  onClick={() => setOpen(false)}
                >
                  <item.icon aria-hidden="true" size={18} />
                  {item.label}
                </Link>
              ))}
              <div className="rounded-xl px-3 py-3">
                <p className="mb-2 text-xs font-semibold uppercase text-[var(--text-muted)]">
                  Appearance
                </p>
                <ThemeControl compact />
              </div>
              <InstallMenuAction onDone={() => setOpen(false)} />
              <form
                action={logoutAction}
                onSubmit={() => {
                  void clearPrivateClientState();
                  setOpen(false);
                }}
              >
                <button className="touch-target flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-[var(--text-secondary)]">
                  <LogOut aria-hidden="true" size={18} />
                  <span className="whitespace-nowrap">Log out</span>
                </button>
              </form>
            </nav>
          </div>
        </>
      ) : null}
    </>
  );
}
