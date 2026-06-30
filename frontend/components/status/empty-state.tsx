import { ReactNode } from "react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";

export function EmptyState({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="quiet-panel rounded-3xl p-6 md:p-8">
      <AssistantOrb state="idle" />
      <h2 className="mt-6 text-2xl font-semibold">{title}</h2>
      <div className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">{children}</div>
    </section>
  );
}
