"use client";

import { useActionState } from "react";
import { MessageCirclePlus, Send, Trash2 } from "lucide-react";

import {
  createConversationAction,
  deleteConversationAction,
  submitQuestionAction,
} from "@/features/conversations/actions";
import type {
  ConversationDetail,
  ConversationSummary,
  DocumentMetadata,
  UsageStatus,
} from "@/lib/api/types";

const idleChatState = { status: "idle" as const, message: "" };

function formatUsage(bucket: { used: number; limit: number }): string {
  return `${bucket.used}/${bucket.limit}`;
}

export function ConversationWorkspace({
  conversations,
  activeConversation,
  documents,
  usage,
}: {
  conversations: ConversationSummary[];
  activeConversation: ConversationDetail | null;
  documents: DocumentMetadata[];
  usage: UsageStatus;
}) {
  const [state, formAction, pending] = useActionState(submitQuestionAction, idleChatState);
  const readyDocuments = documents.filter((document) => document.status === "ready");

  return (
    <div className="grid gap-5 lg:grid-cols-[18rem_minmax(0,1fr)]">
      <aside className="space-y-4">
        <form action={createConversationAction}>
          <button className="touch-target inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-4 text-sm font-semibold text-[#061019]">
            <MessageCirclePlus aria-hidden="true" size={18} />
            New conversation
          </button>
        </form>
        <div className="quiet-panel rounded-lg p-3">
          <h2 className="text-sm font-semibold text-[var(--text-secondary)]">Conversations</h2>
          <div className="mt-3 space-y-2">
            {conversations.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)]">No conversations yet.</p>
            ) : (
              conversations.map((conversation) => (
                <a
                  className={`block rounded-lg border px-3 py-2 text-sm ${
                    activeConversation?.id === conversation.id
                      ? "border-[var(--border-strong)] bg-[var(--surface-overlay)]"
                      : "border-[var(--border-subtle)]"
                  }`}
                  href={`/conversations?conversation=${conversation.id}`}
                  key={conversation.id}
                >
                  {conversation.title}
                </a>
              ))
            )}
          </div>
        </div>
        <div className="quiet-panel rounded-lg p-3 text-sm text-[var(--text-secondary)]">
          <h2 className="font-semibold">Usage</h2>
          <p className="mt-2">Today: {formatUsage(usage.daily)}</p>
          <p>Month: {formatUsage(usage.monthly)}</p>
        </div>
      </aside>

      <section className="quiet-panel min-h-[34rem] rounded-lg p-4">
        {activeConversation ? (
          <div className="flex min-h-[32rem] flex-col gap-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-xl font-semibold">{activeConversation.title}</h2>
              <form action={deleteConversationAction}>
                <input name="conversation_id" type="hidden" value={activeConversation.id} />
                <button className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm text-[var(--status-danger)]">
                  <Trash2 aria-hidden="true" size={17} />
                  Delete
                </button>
              </form>
            </div>
            <div className="flex-1 space-y-3">
              {activeConversation.messages.length === 0 ? (
                <p className="text-sm text-[var(--text-muted)]">
                  Ask a question grounded in your ready PDFs.
                </p>
              ) : (
                activeConversation.messages.map((message) => (
                  <article
                    className={`rounded-lg border border-[var(--border-subtle)] p-3 ${
                      message.role === "assistant" ? "bg-[var(--surface-overlay)]" : ""
                    }`}
                    key={message.id}
                  >
                    <p className="text-xs font-semibold uppercase text-[var(--text-muted)]">
                      {message.role}
                    </p>
                    <p className="mt-2 whitespace-pre-wrap text-sm leading-6">{message.content}</p>
                    {message.citations.length > 0 ? (
                      <div className="mt-3 space-y-2">
                        {message.citations.map((citation) => (
                          <details
                            className="rounded-lg border border-[var(--border-subtle)] p-3 text-sm"
                            key={citation.citation_index}
                          >
                            <summary className="cursor-pointer font-semibold">
                              [{citation.citation_index}] {citation.document_name}, page{" "}
                              {citation.page_number}
                            </summary>
                            <p className="mt-2 leading-6 text-[var(--text-secondary)]">
                              {citation.excerpt}
                            </p>
                          </details>
                        ))}
                      </div>
                    ) : null}
                  </article>
                ))
              )}
            </div>
            <form action={formAction} className="space-y-3">
              <input name="conversation_id" type="hidden" value={activeConversation.id} />
              <fieldset className="rounded-lg border border-[var(--border-subtle)] p-3">
                <legend className="px-1 text-sm font-semibold text-[var(--text-secondary)]">
                  Document scope
                </legend>
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  {readyDocuments.length === 0 ? (
                    <p className="text-sm text-[var(--text-muted)]">No retrieval-ready PDFs.</p>
                  ) : (
                    readyDocuments.map((document) => (
                      <label className="flex items-center gap-2 text-sm" key={document.id}>
                        <input name="document_ids" type="checkbox" value={document.id} />
                        <span className="truncate">{document.original_filename}</span>
                      </label>
                    ))
                  )}
                </div>
              </fieldset>
              <label className="sr-only" htmlFor="question">
                Question
              </label>
              <textarea
                className="min-h-28 w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] p-3 text-sm"
                id="question"
                name="question"
                placeholder="Ask from your documents"
                required
              />
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p
                  className={`text-sm ${
                    state.status === "error"
                      ? "text-[var(--status-danger)]"
                      : "text-[var(--text-muted)]"
                  }`}
                  role={state.status === "error" ? "alert" : "status"}
                >
                  {state.message ||
                    "Document excerpts may be sent to the configured AI provider."}
                </p>
                <button
                  className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-document)] px-4 text-sm font-semibold text-[#07111f] disabled:opacity-60"
                  disabled={pending || readyDocuments.length === 0}
                >
                  <Send aria-hidden="true" size={17} />
                  {pending ? "Sending" : "Send"}
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="flex min-h-[30rem] items-center justify-center text-center">
            <div>
              <h2 className="text-xl font-semibold">Start a grounded conversation</h2>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                Create a conversation to ask citation-backed questions across ready PDFs.
              </p>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
