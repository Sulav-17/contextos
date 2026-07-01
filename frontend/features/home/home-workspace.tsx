"use client";

import Link from "next/link";
import { useActionState, useEffect, useMemo, useState } from "react";
import { FileUp, Send } from "lucide-react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { PROMPT_STORAGE_KEY } from "@/components/public/public-landing";
import { quickStartConversationAction } from "@/features/conversations/actions";
import type { ConversationSummary, DocumentMetadata, UsageStatus } from "@/lib/api/types";

const idleChatState = { status: "idle" as const, message: "" };

function formatUsage(bucket: { used: number; limit: number; remaining: number }) {
  return `${bucket.used}/${bucket.limit} used, ${bucket.remaining} left`;
}

export function HomeWorkspace({
  greeting,
  conversations,
  documents,
  usage,
}: {
  greeting: string;
  conversations: ConversationSummary[];
  documents: DocumentMetadata[];
  usage: UsageStatus;
}) {
  const [state, action, pending] = useActionState(quickStartConversationAction, idleChatState);
  const [question, setQuestion] = useState("");
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const readyDocuments = useMemo(
    () => documents.filter((document) => document.status === "ready"),
    [documents],
  );
  const recentDocuments = documents.slice(0, 5);
  const recentConversations = conversations.slice(0, 5);

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

  return (
    <div className="space-y-8">
      <section className="quiet-panel surface-enter relative overflow-hidden rounded-lg p-5 md:p-7">
        <div className="ambient-orb right-12 top-8 h-24 w-24 bg-[var(--energy-primary)]" />
        <h1 className="text-3xl font-semibold">{greeting}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
          Ask from ready PDFs, inspect citations, and continue the conversation from the workspace.
        </p>
        <div className="mt-5">
          <AssistantOrb state={pending ? "retrieving document" : "ready"} />
        </div>
        <form action={action} className="mt-6 space-y-4">
          <label className="sr-only" htmlFor="home-question">
            Ask your knowledge
          </label>
          <textarea
            className="min-h-32 w-full resize-none rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] p-4 text-sm leading-6"
            id="home-question"
            maxLength={4000}
            name="question"
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask your knowledge..."
            required
            value={question}
          />
          <fieldset>
            <legend className="text-sm font-semibold text-[var(--text-secondary)]">
              Ready document scope
            </legend>
            <div className="mt-2 flex flex-wrap gap-2">
              {readyDocuments.length === 0 ? (
                <p className="text-sm text-[var(--text-muted)]">Upload a PDF to enable grounded answers.</p>
              ) : (
                readyDocuments.map((document) => (
                  <label
                    className="document-chip inline-flex touch-target items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm"
                    key={document.id}
                  >
                    <input
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
              {state.message || "Selected document excerpts may be sent to the configured AI provider."}
            </p>
            <div className="flex gap-3">
              <Link
                className="interactive-glow touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-4 text-sm font-semibold"
                href="/libraries"
              >
                <FileUp aria-hidden="true" size={17} />
                Upload
              </Link>
              <button
                className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-4 text-sm font-semibold text-[#061019] disabled:opacity-60"
                disabled={pending || readyDocuments.length === 0}
              >
                <Send aria-hidden="true" size={17} />
                {pending ? "Starting" : "Ask"}
              </button>
            </div>
          </div>
        </form>
      </section>

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="quiet-panel surface-enter rounded-lg p-4">
          <h2 className="font-semibold">Usage</h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">Today: {formatUsage(usage.daily)}</p>
          <p className="text-sm text-[var(--text-secondary)]">Month: {formatUsage(usage.monthly)}</p>
        </section>
        <section className="quiet-panel surface-enter stagger-one rounded-lg p-4">
          <h2 className="font-semibold">Recent conversations</h2>
          <div className="mt-3 space-y-2">
            {recentConversations.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)]">No conversations yet.</p>
            ) : (
              recentConversations.map((conversation) => (
                <Link
                  className="interactive-glow block rounded-lg border border-[var(--border-subtle)] px-3 py-2 text-sm transition-transform hover:-translate-y-0.5"
                  href={`/conversations?conversation=${conversation.id}`}
                  key={conversation.id}
                >
                  {conversation.title}
                </Link>
              ))
            )}
          </div>
        </section>
        <section className="quiet-panel surface-enter stagger-two rounded-lg p-4">
          <h2 className="font-semibold">Recent documents</h2>
          <div className="mt-3 space-y-2">
            {recentDocuments.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)]">No documents yet.</p>
            ) : (
              recentDocuments.map((document) => (
                <p className="text-sm text-[var(--text-secondary)]" key={document.id}>
                  {document.original_filename} - {document.status}
                </p>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
