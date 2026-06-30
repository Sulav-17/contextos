"use client";

import * as Dialog from "@radix-ui/react-dialog";
import Link from "next/link";
import { MoreHorizontal, X } from "lucide-react";

import { secondaryNavItems } from "@/components/navigation/nav-items";

export function MobileMore({ isAdmin }: { isAdmin: boolean }) {
  const items = secondaryNavItems.filter((item) => !item.adminOnly || isAdmin);
  return (
    <Dialog.Root>
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
              <Dialog.Close asChild key={item.href}>
                <Link className="touch-target flex items-center gap-3 rounded-xl px-3 py-2 text-sm" href={item.href}>
                  <item.icon aria-hidden="true" size={18} />
                  {item.label}
                </Link>
              </Dialog.Close>
            ))}
          </nav>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
