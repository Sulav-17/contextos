import type { ReactNode } from "react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <main className="grid min-h-dvh place-items-center px-4 py-10">
      <a href="#auth-content" className="skip-link">
        Skip to main content
      </a>
      <section
        id="auth-content"
        className="quiet-panel w-full max-w-md rounded-3xl p-6 md:p-8"
      >
        <AssistantOrb state="checking session" />
        {children}
      </section>
    </main>
  );
}
