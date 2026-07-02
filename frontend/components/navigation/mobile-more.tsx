"use client";

import * as Dialog from "@radix-ui/react-dialog";
import Link from "next/link";
import { Download, LogOut, MoreHorizontal, X } from "lucide-react";
import { useState } from "react";

import { clearPrivateClientState } from "@/components/auth/logout-control";
import { secondaryNavItems } from "@/components/navigation/nav-items";
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
      className="touch-target flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-[var(--text-secondary)] disabled:opacity-60"
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

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger className="touch-target flex flex-1 flex-col items-center justify-center gap-1 rounded-xl text-xs text-[var(--text-secondary)]">
        <MoreHorizontal aria-hidden="true" size={20} />
        More
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60" />
        <Dialog.Content className="fixed inset-x-3 bottom-3 z-50 rounded-3xl border border-[var(--border-subtle)] bg-[var(--surface-overlay)] p-4 shadow-[var(--shadow-panel)]">
          <div className="mb-4 flex items-center justify-between">
            <Dialog.Title className="text-base font-semibold">More navigation</Dialog.Title>
            <Dialog.Close className="touch-target rounded-full" aria-label="Close menu">
              <X aria-hidden="true" />
            </Dialog.Close>
          </div>
          <nav aria-label="Secondary mobile navigation" className="grid gap-2">
            {items.map((item) => (
              <Link
                className="touch-target flex items-center gap-3 rounded-xl px-3 py-2 text-sm"
                href={item.href}
                key={item.href}
                onClick={() => setOpen(false)}
              >
                <item.icon aria-hidden="true" size={18} />
                {item.label}
              </Link>
            ))}
            <InstallMenuAction onDone={() => setOpen(false)} />
            <form
              action={logoutAction}
              onSubmit={() => {
                void clearPrivateClientState();
                setOpen(false);
              }}
            >
              <button className="touch-target flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-[var(--text-secondary)]">
                <LogOut aria-hidden="true" size={18} />
                <span className="whitespace-nowrap">Log out</span>
              </button>
            </form>
          </nav>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
