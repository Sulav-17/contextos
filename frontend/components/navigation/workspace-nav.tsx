import Link from "next/link";

import { MobileMore } from "@/components/navigation/mobile-more";
import { primaryNavItems, secondaryNavItems } from "@/components/navigation/nav-items";

export function WorkspaceNav({ isAdmin }: { isAdmin: boolean }) {
  const desktopItems = [...primaryNavItems, ...secondaryNavItems].filter(
    (item) => !item.adminOnly || isAdmin,
  );
  return (
    <>
      <nav
        aria-label="Primary"
        className="hidden w-64 shrink-0 border-r border-[var(--border-subtle)] px-4 py-6 md:block"
      >
        <Link href="/home" className="mb-8 block text-lg font-semibold">
          ContextOS
        </Link>
        <ul className="grid gap-1">
          {desktopItems.map((item) => (
            <li key={item.href}>
              <Link
                className="touch-target flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-[var(--text-secondary)] hover:bg-white/5"
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
            className="touch-target flex flex-1 flex-col items-center justify-center gap-1 rounded-xl text-xs text-[var(--text-secondary)]"
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
