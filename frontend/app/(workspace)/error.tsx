"use client";

import Link from "next/link";

import { AssistantOrb } from "@/components/assistant/assistant-orb";

export default function WorkspaceError() {
  return (
    <main className="grid min-h-dvh place-items-center px-4 py-10">
      <section className="quiet-panel w-full max-w-lg rounded-3xl p-6 md:p-8">
        <AssistantOrb state="backend unavailable" />
        <h1 className="mt-6 text-3xl font-semibold">ContextOS is unavailable</h1>
        <p role="alert" className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
          The authenticated API boundary could not be reached or did not authorize this request.
          Try again after the backend is available.
        </p>
        <Link href="/login" className="mt-6 inline-block text-sm text-[var(--accent-intelligence)]">
          Return to login
        </Link>
      </section>
    </main>
  );
}
