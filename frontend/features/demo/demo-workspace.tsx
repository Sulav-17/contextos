"use client";

import { FormEvent, useMemo, useState } from "react";
import {
  BookOpen,
  CheckCircle2,
  MessageSquareText,
  RotateCcw,
  Send,
} from "lucide-react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { ThemeControl } from "@/components/theme/theme-control";
import {
  demoAnswers,
  demoConversationEntries,
  demoDocuments,
  demoMemories,
  findPreparedAnswer,
  type DemoAnswer,
} from "@/features/demo/demo-data";

const unsupportedMessage =
  "This guided demo currently supports the provided sample questions. Choose a suggested question to see a prepared citation-backed response. No network request or live AI call was made.";

export function DemoWorkspace() {
  const [selectedAnswer, setSelectedAnswer] = useState<DemoAnswer>(demoAnswers[0]);
  const [composerValue, setComposerValue] = useState("");
  const [statusMessage, setStatusMessage] = useState("Prepared response loaded.");
  const referencedMemories = useMemo(
    () => demoMemories.filter((memory) => selectedAnswer.memoryIds.includes(memory.id)),
    [selectedAnswer],
  );

  function chooseAnswer(answer: DemoAnswer) {
    setSelectedAnswer(answer);
    setComposerValue(answer.question);
    setStatusMessage("Prepared response loaded.");
  }

  function resetDemo() {
    setSelectedAnswer(demoAnswers[0]);
    setComposerValue("");
    setStatusMessage("Demo reset to the initial prepared example.");
  }

  function submitComposer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const prepared = findPreparedAnswer(composerValue);
    if (prepared) {
      chooseAnswer(prepared);
      return;
    }
    setStatusMessage(unsupportedMessage);
  }

  return (
    <main className="min-h-dvh overflow-x-hidden px-4 py-5 md:px-8" data-app-shell="public">
      <a href="#demo-content" className="skip-link">
        Skip to demo content
      </a>
      <header className="mx-auto flex max-w-7xl items-center justify-between gap-3">
        <p className="text-lg font-semibold tracking-normal">ContextOS</p>
        <ThemeControl compact />
      </header>

      <section className="mx-auto mt-10 max-w-7xl" id="demo-content">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-4xl">
            <div className="flex flex-wrap items-center gap-3">
              <span className="rounded-full border border-[var(--accent-intelligence)] px-3 py-1 text-xs font-semibold uppercase text-[var(--accent-intelligence)]">
                Demo Mode
              </span>
              <span className="rounded-full border border-[var(--border-subtle)] px-3 py-1 text-xs font-semibold uppercase text-[var(--text-muted)]">
                Interactive Demo
              </span>
            </div>
            <h1 className="mt-4 text-4xl font-semibold leading-tight md:text-6xl">
              Explore ContextOS with fictional evidence.
            </h1>
            <p className="mt-4 max-w-3xl text-sm leading-6 text-[var(--text-secondary)] md:text-base md:leading-7">
              This guided demo uses fictional sample data and prepared responses. It does not
              access real user accounts, documents, or live AI services.
            </p>
          </div>
          <button
            className="touch-target inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--border-subtle)] px-5 text-sm font-semibold text-[var(--text-secondary)]"
            onClick={resetDemo}
            type="button"
          >
            <RotateCcw aria-hidden="true" size={17} />
            Reset demo
          </button>
        </div>

        <div className="mt-6">
          <AssistantOrb state="ready" />
        </div>

        <div className="mt-8 grid gap-5 xl:grid-cols-[18rem_minmax(0,1fr)_21rem]">
          <aside className="space-y-4">
            <section className="quiet-panel rounded-lg p-4">
              <h2 className="font-semibold">Suggested questions</h2>
              <div className="mt-3 grid gap-2">
                {demoAnswers.map((answer) => (
                  <button
                    className={`touch-target rounded-lg border px-3 py-2 text-left text-sm leading-5 ${
                      answer.id === selectedAnswer.id
                        ? "active-glow"
                        : "border-[var(--border-subtle)] text-[var(--text-secondary)] hover:bg-white/5"
                    }`}
                    key={answer.id}
                    onClick={() => chooseAnswer(answer)}
                    type="button"
                  >
                    {answer.question}
                  </button>
                ))}
              </div>
            </section>

            <section className="quiet-panel rounded-lg p-4">
              <h2 className="font-semibold">Fictional PDFs</h2>
              <div className="mt-3 space-y-3">
                {demoDocuments.map((document) => (
                  <article
                    className="rounded-lg border border-[var(--border-subtle)] p-3"
                    key={document.id}
                  >
                    <div className="flex items-start gap-2">
                      <BookOpen
                        aria-hidden="true"
                        className="mt-0.5 text-[var(--accent-document)]"
                        size={17}
                      />
                      <div className="min-w-0">
                        <h3 className="text-sm font-semibold">{document.name}</h3>
                        <p className="mt-1 text-xs text-[var(--text-muted)]">
                          {document.pages} pages / {document.status}
                        </p>
                        <p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">
                          {document.summary}
                        </p>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </aside>

          <section className="quiet-panel flex min-h-[38rem] min-w-0 flex-col rounded-lg p-4 md:p-5">
            <div className="flex flex-col gap-3 border-b border-[var(--border-subtle)] pb-4 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-[var(--text-muted)]">
                  Prepared answer
                </p>
                <h2 className="mt-1 text-xl font-semibold">{selectedAnswer.question}</h2>
              </div>
              <span className="w-fit rounded-full border border-[var(--border-subtle)] px-3 py-1 text-xs font-semibold text-[var(--text-muted)]">
                No live AI call
              </span>
            </div>

            <div
              aria-label="Demo conversation"
              className="min-h-0 flex-1 space-y-3 overflow-y-auto py-4"
              data-testid="demo-conversation"
            >
              <article className="message-bubble ml-auto w-fit max-w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] p-3 sm:max-w-2xl">
                <p className="text-xs font-semibold uppercase text-[var(--text-muted)]">user</p>
                <p className="mt-2 text-sm leading-6">{selectedAnswer.question}</p>
              </article>
              <article className="message-bubble mr-auto max-w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-overlay)] p-3 sm:max-w-3xl">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-xs font-semibold uppercase text-[var(--text-muted)]">
                    assistant
                  </p>
                  <span className="rounded-full border border-[var(--accent-document)] px-2 py-1 text-xs font-semibold text-[var(--accent-document)]">
                    Used {selectedAnswer.citations.length} fictional citations
                  </span>
                  {referencedMemories.length > 0 ? (
                    <span className="rounded-full border border-[var(--accent-memory)] px-2 py-1 text-xs font-semibold text-[var(--accent-memory)]">
                      Used {referencedMemories.length} fictional memories
                    </span>
                  ) : null}
                </div>
                <p className="mt-3 text-sm leading-6">{selectedAnswer.answer}</p>
                <div className="mt-4 space-y-2">
                  {selectedAnswer.citations.map((citation, index) => (
                    <details
                      className="citation-card rounded-lg border border-[var(--border-subtle)] p-3 text-sm"
                      key={citation.id}
                    >
                      <summary className="cursor-pointer font-semibold">
                        [{index + 1}] {citation.documentName}, page {citation.pageNumber}
                      </summary>
                      <p className="mt-2 leading-6 text-[var(--text-secondary)]">
                        {citation.excerpt}
                      </p>
                    </details>
                  ))}
                </div>
              </article>
            </div>

            <form className="composer-surface mt-auto space-y-3 border-t border-[var(--border-subtle)] pt-3" onSubmit={submitComposer}>
              <label className="sr-only" htmlFor="demo-question">
                Try a prepared sample question
              </label>
              <textarea
                className="min-h-24 w-full resize-none rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] p-3 text-sm leading-6"
                id="demo-question"
                maxLength={4000}
                onChange={(event) => setComposerValue(event.target.value)}
                placeholder="Try one of the suggested questions above"
                value={composerValue}
              />
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p
                  className={`text-sm ${
                    statusMessage === unsupportedMessage
                      ? "text-[var(--status-warning)]"
                      : "text-[var(--text-muted)]"
                  }`}
                  role="status"
                >
                  {statusMessage}
                </p>
                <button   className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-document)] px-4 text-sm font-semibold text-[#07111f]"
                type="submit">
                  <Send aria-hidden="true" size={17} />
                  Show prepared answer
                </button>
              </div>
            </form>
          </section>

          <aside className="space-y-4">
            <section className="quiet-panel rounded-lg p-4">
              <h2 className="font-semibold">Sample conversations</h2>
              <div className="mt-3 space-y-2">
                {demoConversationEntries.map((entry) => (
                  <article
                    className="rounded-lg border border-[var(--border-subtle)] p-3"
                    key={entry.id}
                  >
                    <h3 className="text-sm font-semibold">{entry.title}</h3>
                    <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                      {entry.preview}
                    </p>
                    <p className="mt-2 text-xs font-semibold uppercase text-[var(--text-muted)]">
                      {entry.sourceLabel}
                    </p>
                  </article>
                ))}
              </div>
            </section>

            <section className="quiet-panel rounded-lg p-4">
              <h2 className="font-semibold">Fictional approved memories</h2>
              <div className="mt-3 space-y-2">
                {demoMemories.map((memory) => (
                  <article
                    className={`rounded-lg border p-3 ${
                      selectedAnswer.memoryIds.includes(memory.id)
                        ? "border-[var(--accent-memory)]"
                        : "border-[var(--border-subtle)]"
                    }`}
                    key={memory.id}
                  >
                    <div className="flex items-center gap-2">
                      <CheckCircle2
                        aria-hidden="true"
                        className="text-[var(--accent-memory)]"
                        size={16}
                      />
                      <p className="text-xs font-semibold uppercase text-[var(--text-muted)]">
                        {memory.type} / approved
                      </p>
                    </div>
                    <p className="mt-2 text-sm leading-6">{memory.content}</p>
                    <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">
                      {memory.source}
                    </p>
                  </article>
                ))}
              </div>
            </section>

            <section className="quiet-panel rounded-lg p-4">
              <div className="flex items-start gap-3">
                <MessageSquareText
                  aria-hidden="true"
                  className="mt-1 text-[var(--accent-intelligence)]"
                  size={18}
                />
                <div>
                  <h2 className="font-semibold">What this demonstrates</h2>
                  <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                    Citation display, memory labeling, reset behavior, and the Quiet Orbit
                    workspace feel using deterministic fictional fixtures.
                  </p>
                </div>
              </div>
            </section>
          </aside>
        </div>
      </section>
    </main>
  );
}
