"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { ArrowRight, LockKeyhole, MessageSquareText, Quote } from "lucide-react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { ThemeControl } from "@/components/theme/theme-control";

const PROMPT_STORAGE_KEY = "contextos.pendingPrompt";

export function PublicLanding() {
  const [prompt, setPrompt] = useState("");

  function submitPrompt(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = prompt.trim().slice(0, 4000);
    if (normalized) {
      window.sessionStorage.setItem(PROMPT_STORAGE_KEY, normalized);
    }
    window.location.assign("/login?next=/home&intent=chat");
  }

  return (
    <main className="relative min-h-dvh overflow-hidden px-4 py-5 md:px-8">
      <header className="mx-auto flex max-w-6xl items-center justify-between">
        <Link className="text-lg font-semibold tracking-normal" href="/">
          ContextOS
        </Link>
        <div className="flex items-center gap-3">
          <ThemeControl compact />
          <Link
            className="touch-target inline-flex items-center rounded-lg border border-[var(--border-subtle)] px-4 text-sm text-[var(--text-secondary)]"
            href="/login?next=/home"
          >
            Log in
          </Link>
        </div>
      </header>

      <section className="mx-auto grid max-w-6xl gap-10 pb-12 pt-16 lg:grid-cols-[minmax(0,1fr)_minmax(360px,0.76fr)] lg:items-center">
        <div className="surface-enter">
          <p className="text-sm font-semibold uppercase text-[var(--accent-intelligence)]">
            Private PDF intelligence
          </p>
          <h1 className="mt-4 max-w-3xl text-5xl font-semibold leading-tight md:text-6xl">
            Ask your library and keep the answer grounded.
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-[var(--text-secondary)]">
            ContextOS turns a private PDF collection into a citation-backed workspace for
            research, decisions, and persistent conversations.
          </p>
          <div className="mt-6">
            <AssistantOrb state="ready" />
          </div>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              className="touch-target inline-flex items-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-5 font-semibold text-[#061019]"
              href="/signup?next=/home"
            >
              Create account
              <ArrowRight aria-hidden="true" size={18} />
            </Link>
            <Link
              className="touch-target inline-flex items-center rounded-lg border border-[var(--border-subtle)] px-5 font-semibold text-[var(--text-secondary)]"
              href="/login?next=/home"
            >
              Log in
            </Link>
          </div>
        </div>

        <div className="quiet-panel interactive-glow surface-enter stagger-one relative rounded-lg p-4">
          <form action="/login" className="space-y-3" onSubmit={submitPrompt}>
            <label className="text-sm font-semibold" htmlFor="public-question">
              Ask a private PDF question
            </label>
            <textarea
              className="min-h-36 w-full resize-none rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] p-4 text-sm leading-6 text-[var(--text-primary)]"
              id="public-question"
              maxLength={4000}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="What does my lease say about renewal notice?"
              value={prompt}
            />
            <button className="touch-target inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent-document)] px-4 font-semibold text-[#07111f] transition-[box-shadow,transform] hover:-translate-y-0.5 hover:shadow-[0_0_26px_var(--panel-glow)]">
              Continue securely
              <MessageSquareText aria-hidden="true" size={18} />
            </button>
            <p className="text-xs leading-5 text-[var(--text-muted)]">
              This prompt is stored only in this browser until you log in. No anonymous AI calls are
              made.
            </p>
          </form>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-4 pb-12 md:grid-cols-3">
        {[
          {
            icon: LockKeyhole,
            title: "Private by design",
            body: "Every document, conversation, and retrieval is scoped to the authenticated account.",
          },
          {
            icon: Quote,
            title: "Citations first",
            body: "Answers show source document names, pages, and excerpts so evidence stays inspectable.",
          },
          {
            icon: MessageSquareText,
            title: "Conversation memory, not long-term memory",
            body: "Current conversation history is preserved. User-approved long-term memory remains upcoming.",
          },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <article className="quiet-panel interactive-glow surface-enter stagger-two rounded-lg p-5" key={item.title}>
              <Icon aria-hidden="true" className="text-[var(--accent-intelligence)]" size={22} />
              <h2 className="mt-4 font-semibold">{item.title}</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.body}</p>
            </article>
          );
        })}
      </section>
    </main>
  );
}

export { PROMPT_STORAGE_KEY };
