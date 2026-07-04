"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { MobileMore } from "@/components/navigation/mobile-more";
import { primaryNavItems, secondaryNavItems } from "@/components/navigation/nav-items";

export function WorkspaceNav({ isAdmin }: { isAdmin: boolean }) {
  const pathname = usePathname();
  const desktopItems = [...primaryNavItems, ...secondaryNavItems].filter(
    (item) => !item.adminOnly || isAdmin,
  );
  return (
    <>
      <nav
        aria-label="Primary"
        className="hidden h-full w-64 shrink-0 overflow-y-auto overflow-x-hidden border-r border-[var(--border-subtle)] px-4 py-6 [scrollbar-gutter:stable] md:block"
      >
        <Link href="/home" className="mb-8 block text-lg font-semibold">
          ContextOS
        </Link>
        <ul className="grid gap-1">
          {desktopItems.map((item) => (
            <li key={item.href}>
              <Link
                aria-current={pathname === item.href ? "page" : undefined}
                className={`touch-target flex items-center gap-3 rounded-xl px-3 py-2 text-sm ${
                  pathname === item.href
                    ? "active-glow"
                    : "text-[var(--text-secondary)] hover:bg-white/5"
                }`}
                href={item.href}
              >
                <item.icon aria-hidden="true" size={18} />
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      <nav
        aria-label="Mobile primary"
        className="fixed inset-x-0 bottom-0 z-30 flex border-t border-[var(--border-subtle)] bg-[var(--surface-overlay)] px-2 pb-[calc(env(safe-area-inset-bottom)+0.25rem)] pt-2 md:hidden"
      >
        {primaryNavItems.map((item) => (
          <Link
            key={item.href}
            aria-current={pathname === item.href ? "page" : undefined}
            className={`touch-target flex flex-1 flex-col items-center justify-center gap-1 rounded-xl text-xs ${
              pathname === item.href ? "active-glow" : "text-[var(--text-secondary)]"
            }`}
            href={item.href}
          >
            <item.icon aria-hidden="true" size={20} />
            {item.label}
          </Link>
        ))}
        <MobileMore isAdmin={isAdmin} />
      </nav>
    </>
  );
}
