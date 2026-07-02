"use client";

import Link from "next/link";
import { useActionState, useEffect, useMemo, useRef, useState } from "react";
import { FileUp, MessageCirclePlus, Send, Sparkles } from "lucide-react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { PROMPT_STORAGE_KEY } from "@/components/public/public-landing";
import { quickStartConversationAction, createConversationAction } from "@/features/conversations/actions";
import { approveMemoryAction, rejectMemoryAction } from "@/features/memories/actions";
import type { DashboardData, DocumentMetadata } from "@/lib/api/types";
import { networkUnavailableMessage, useNetworkState } from "@/lib/pwa/network";

const idleChatState = { status: "idle" as const, message: "" };

function remainingLabel(remaining: number, limit: number) {
  return `${remaining} left of ${limit}`;
}

export function HomeWorkspace({
  dashboard,
  documents,
  greeting,
}: {
  dashboard: DashboardData;
  documents: DocumentMetadata[];
  greeting: string;
}) {
  const [state, action, pending] = useActionState(quickStartConversationAction, idleChatState);
  const [question, setQuestion] = useState("");
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [networkMessage, setNetworkMessage] = useState("");
  const submittingRef = useRef(false);
  const readyDocuments = useMemo(
    () => documents.filter((document) => document.status === "ready"),
    [documents],
  );

  useEffect(() => {
    if (!pending) {
      submittingRef.current = false;
    }
  }, [pending]);

  useEffect(() => {
    const saved = window.sessionStorage.getItem(PROMPT_STORAGE_KEY);
    if (saved) {
      window.sessionStorage.removeItem(PROMPT_STORAGE_KEY);
      window.setTimeout(() => setQuestion(saved), 0);
    }
  }, []);

  function toggleDocument(documentId: string, checked: boolean) {
    setSelectedDocumentIds((current) => {
      if (checked) {
        return current.includes(documentId) ? current : [...current, documentId];
      }
      return current.filter((id) => id !== documentId);
    });
  }

  const isNewWorkspace =
    dashboard.counts.active_documents === 0 &&
    dashboard.counts.active_conversations === 0 &&
    dashboard.counts.approved_memories === 0 &&
    dashboard.counts.pending_suggestions === 0;
  const isOffline = useNetworkState() === "offline";

  function blockOffline(event: { preventDefault: () => void }, action: string) {
    if (!isOffline) {
      return;
    }
    event.preventDefault();
    setNetworkMessage(networkUnavailableMessage(action));
  }

  return (
    <div className="space-y-8">
      <section className="quiet-panel surface-enter relative overflow-hidden rounded-lg p-5 md:p-7">
        <div className="ambient-orb right-12 top-8 h-24 w-24 bg-[var(--energy-primary)]" />
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <h1 className="text-3xl font-semibold">{greeting}</h1>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
              Home is your command center for documents, conversations, memories, and authenticated
              ContextOS workspace state.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
            <Link
              className="interactive-glow touch-target inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--border-subtle)] px-4 text-sm font-semibold"
              href="/libraries"
            >
              <FileUp aria-hidden="true" size={17} />
              Upload PDF
            </Link>
            <form action={createConversationAction} onSubmit={(event) => blockOffline(event, "Starting a conversation")}>
              <button className="touch-target inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-4 text-sm font-semibold text-[#061019] disabled:opacity-60" disabled={isOffline}>
                <MessageCirclePlus aria-hidden="true" size={17} />
                New conversation
              </button>
            </form>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          <Link className="touch-target rounded-lg border border-[var(--border-subtle)] px-4 text-sm" href="/libraries">
            Documents
          </Link>
          <Link className="touch-target rounded-lg border border-[var(--border-subtle)] px-4 text-sm" href="/conversations">
            Conversations
          </Link>
          <Link className="touch-target rounded-lg border border-[var(--border-subtle)] px-4 text-sm" href="/memories">
            Memories
          </Link>
        </div>

        <div className="mt-6">
          <AssistantOrb state={pending ? "retrieving document" : "ready"} />
        </div>
        <form
          action={action}
          className="mt-6 space-y-4"
          onSubmit={(event) => {
            if (isOffline) {
              blockOffline(event, "Quick-start chat");
              return;
            }
            if (submittingRef.current || pending || !question.trim()) {
              event.preventDefault();
              return;
            }
            submittingRef.current = true;
          }}
        >
          <label className="sr-only" htmlFor="home-question">
            Ask your knowledge
          </label>
          <textarea
            className="min-h-32 w-full resize-none rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] p-4 text-sm leading-6"
            id="home-question"
            maxLength={4000}
            name="question"
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a general question, ask from selected PDFs, or check your ContextOS workspace state."
            required
            value={question}
          />
          <fieldset>
            <legend className="text-sm font-semibold text-[var(--text-secondary)]">
              Optional document scope
            </legend>
            <div className="mt-2 flex flex-wrap gap-2">
              {readyDocuments.length === 0 ? (
                <p className="text-sm text-[var(--text-muted)]">
                  PDFs are optional for general chat. Select them when you want cited answers.
                </p>
              ) : (
                readyDocuments.map((document) => (
                  <label
                    className="document-chip inline-flex touch-target items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm"
                    key={document.id}
                  >
                    <input
                      aria-label={document.original_filename}
                      checked={selectedDocumentIds.includes(document.id)}
                      name="document_ids"
                      onChange={(event) => toggleDocument(document.id, event.target.checked)}
                      type="checkbox"
                      value={document.id}
                    />
                    <span>{document.original_filename}</span>
                  </label>
                ))
              )}
            </div>
          </fieldset>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p
              className={`text-sm ${
                state.status === "error" ? "text-[var(--status-danger)]" : "text-[var(--text-muted)]"
              }`}
              role={state.status === "error" ? "alert" : "status"}
            >
              {networkMessage ||
                state.message ||
                (selectedDocumentIds.length > 0
                  ? "Selected PDFs will be used for cited answers."
                  : "General chat works without PDFs. Saved memory only applies after approval.")}
            </p>
            <button
              className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-4 text-sm font-semibold text-[#061019] disabled:opacity-60"
              disabled={pending || isOffline || !question.trim()}
            >
              <Send aria-hidden="true" size={17} />
              {pending ? "Starting" : "Ask"}
            </button>
          </div>
        </form>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <SummaryCard label="Active documents" value={dashboard.counts.active_documents} />
        <SummaryCard label="Active conversations" value={dashboard.counts.active_conversations} />
        <SummaryCard label="Approved memories" value={dashboard.counts.approved_memories} />
        <SummaryCard label="Pending suggestions" value={dashboard.counts.pending_suggestions} />
        <SummaryCard
          label="Daily usage remaining"
          value={remainingLabel(dashboard.usage.daily.remaining, dashboard.usage.daily.limit)}
        />
        <SummaryCard
          label="Monthly usage remaining"
          value={remainingLabel(dashboard.usage.monthly.remaining, dashboard.usage.monthly.limit)}
        />
      </section>

      {isNewWorkspace ? (
        <section className="quiet-panel rounded-lg p-6">
          <div className="flex items-start gap-3">
            <Sparkles aria-hidden="true" className="mt-1" size={18} />
            <div>
              <h2 className="text-lg font-semibold">Start here</h2>
              <ol className="mt-3 space-y-2 text-sm text-[var(--text-secondary)]">
                <li>1. Upload a PDF.</li>
                <li>2. Ask a question.</li>
                <li>3. Approve useful memory.</li>
              </ol>
              <p className="mt-3 text-sm text-[var(--text-muted)]">
                PDFs are optional for general chat, selected PDFs enable cited answers, memory
                requires approval, and usage limits stay visible here.
              </p>
            </div>
          </div>
        </section>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-2">
        <RecentSection
          empty="No conversations yet."
          hrefBuilder={(item) => `/conversations?conversation=${item.id}`}
          items={dashboard.recent_conversations}
          renderMeta={(item) => (item.archived_at ? "Archived" : "Active")}
          title="Recent conversations"
        />
        <RecentSection
          empty="No documents yet."
          hrefBuilder={(item) => `/libraries#document-${item.id}`}
          items={dashboard.recent_documents}
          renderMeta={(item) => item.status}
          title="Recent documents"
        />
        <RecentSection
          empty="No approved memories yet."
          hrefBuilder={(item) => `/memories#memory-${item.id}`}
          items={dashboard.recent_memories}
          renderLabel={(item) => item.content}
          renderMeta={(item) => item.source_conversation_title ?? item.memory_type}
          title="Recent memories"
        />
        <section className="quiet-panel rounded-lg p-4">
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-semibold">Pending suggestions</h2>
            <Link className="text-sm text-[var(--text-secondary)] underline" href="/memories">
              Review all
            </Link>
          </div>
          <div className="mt-3 space-y-3">
            {dashboard.pending_suggestions.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)]">No pending suggestions.</p>
            ) : (
              dashboard.pending_suggestions.map((memory) => (
                <article
                  className="rounded-lg border border-[var(--border-subtle)] p-3"
                  key={memory.id}
                >
                  <p className="text-xs font-semibold uppercase text-[var(--text-muted)]">
                    Awaiting approval
                  </p>
                  <p className="mt-2 text-sm leading-6">{memory.content}</p>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <form action={approveMemoryAction} onSubmit={(event) => blockOffline(event, "Approving memory")}>
                      <input name="memory_id" type="hidden" value={memory.id} />
                      <button className="touch-target rounded-lg bg-[var(--accent-intelligence)] px-3 text-sm font-semibold text-[#061019] disabled:opacity-60" disabled={isOffline}>
                        Approve
                      </button>
                    </form>
                    <form action={rejectMemoryAction} onSubmit={(event) => blockOffline(event, "Rejecting memory")}>
                      <input name="memory_id" type="hidden" value={memory.id} />
                      <button className="touch-target rounded-lg border border-[var(--border-subtle)] px-3 text-sm disabled:opacity-60" disabled={isOffline}>
                        Reject
                      </button>
                    </form>
                    {memory.source_conversation_id ? (
                      <Link
                        className="text-sm underline"
                        href={`/conversations?conversation=${memory.source_conversation_id}`}
                      >
                        {memory.source_conversation_title ?? "Open source conversation"}
                      </Link>
                    ) : null}
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: number | string }) {
  return (
    <section className="quiet-panel rounded-lg p-4">
      <p className="text-sm text-[var(--text-secondary)]">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </section>
  );
}

function RecentSection<T extends { id: string }>({
  empty,
  hrefBuilder,
  items,
  renderLabel,
  renderMeta,
  title,
}: {
  empty: string;
  hrefBuilder: (item: T) => string;
  items: T[];
  renderLabel?: (item: T) => string;
  renderMeta?: (item: T) => string | null;
  title: string;
}) {
  return (
    <section className="quiet-panel rounded-lg p-4">
      <h2 className="font-semibold">{title}</h2>
      <div className="mt-3 space-y-2">
        {items.length === 0 ? (
          <p className="text-sm text-[var(--text-muted)]">{empty}</p>
        ) : (
          items.map((item) => (
            <Link
              className="interactive-glow block rounded-lg border border-[var(--border-subtle)] px-3 py-2"
              href={hrefBuilder(item)}
              key={item.id}
            >
              <p className="text-sm font-medium">{renderLabel ? renderLabel(item) : (item as { title?: string; original_filename?: string }).title ?? (item as { original_filename?: string }).original_filename}</p>
              {renderMeta ? (
                <p className="mt-1 text-xs text-[var(--text-muted)]">{renderMeta(item)}</p>
              ) : null}
            </Link>
          ))
        )}
      </div>
    </section>
  );
}
