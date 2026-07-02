import type { ReactNode } from "react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { ThemeControl } from "@/components/theme/theme-control";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <main className="grid min-h-dvh place-items-center px-4 py-10" data-app-shell="auth">
      <a href="#auth-content" className="skip-link">
        Skip to main content
      </a>
      <section id="auth-content" className="quiet-panel w-full max-w-md rounded-lg p-6 md:p-8">
        <div className="mb-4 flex justify-end">
          <ThemeControl compact />
        </div>
        <AssistantOrb state="checking session" />
        {children}
      </section>
    </main>
  );
}
