"use client";

import { useActionState, useEffect, useMemo, useState } from "react";
import {
  MessageCirclePlus,
  PanelLeft,
  Pencil,
  Save,
  Search,
  Send,
  Trash2,
  X,
} from "lucide-react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import {
  createConversationAction,
  deleteConversationAction,
  renameConversationAction,
  submitQuestionAction,
} from "@/features/conversations/actions";
import type {
  ConversationDetail,
  ConversationSummary,
  DocumentMetadata,
  UsageStatus,
} from "@/lib/api/types";

const idleChatState = { status: "idle" as const, message: "" };
const DRAFT_STORAGE_PREFIX = "contextos.conversationDraft.";

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
  const [renameState, renameAction, renamePending] = useActionState(
    renameConversationAction,
    idleChatState,
  );
  const [historyOpen, setHistoryOpen] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [query, setQuery] = useState("");
  const [question, setQuestion] = useState("");
  const [submittedMessageCount, setSubmittedMessageCount] = useState<number | null>(null);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>(
    activeConversation?.selected_document_ids ?? [],
  );
  const readyDocuments = useMemo(
    () => documents.filter((document) => document.status === "ready"),
    [documents],
  );
  const readyDocumentIds = useMemo(
    () => new Set(readyDocuments.map((document) => document.id)),
    [readyDocuments],
  );
  const selectedScopeKey = (activeConversation?.selected_document_ids ?? []).join("|");
  const filteredConversations = useMemo(
    () =>
      conversations.filter((conversation) =>
        conversation.title.toLowerCase().includes(query.trim().toLowerCase()),
      ),
    [conversations, query],
  );
  const activeConversationId = activeConversation?.id ?? "";

  useEffect(() => {
    if (!activeConversationId) {
      window.setTimeout(() => {
        setQuestion("");
        setSelectedDocumentIds([]);
      }, 0);
      return;
    }
    const draft = window.sessionStorage.getItem(`${DRAFT_STORAGE_PREFIX}${activeConversationId}`);
    const restoredSelection = (activeConversation?.selected_document_ids ?? []).filter((id) =>
      readyDocumentIds.has(id),
    );
    window.setTimeout(() => {
      setQuestion(draft ?? "");
      setSelectedDocumentIds(restoredSelection);
    }, 0);
  }, [activeConversationId, readyDocumentIds, selectedScopeKey, activeConversation]);

  useEffect(() => {
    if (!activeConversationId) {
      return;
    }
    window.sessionStorage.setItem(`${DRAFT_STORAGE_PREFIX}${activeConversationId}`, question);
  }, [activeConversationId, question]);

  useEffect(() => {
    const receivedAcceptedResponse =
      submittedMessageCount !== null &&
      activeConversation !== null &&
      activeConversation.messages.length > submittedMessageCount;
    if ((!receivedAcceptedResponse && state.status !== "success") || !activeConversationId) {
      return;
    }
    window.setTimeout(() => {
      window.sessionStorage.removeItem(`${DRAFT_STORAGE_PREFIX}${activeConversationId}`);
      setQuestion("");
      setSubmittedMessageCount(null);
    }, 0);
  }, [activeConversation, activeConversationId, state.status, submittedMessageCount]);

  function toggleDocument(documentId: string, checked: boolean) {
    setSelectedDocumentIds((current) => {
      if (checked) {
        return current.includes(documentId) ? current : [...current, documentId];
      }
      return current.filter((id) => id !== documentId);
    });
  }

  const renderConversationList = () => (
    <div className="quiet-panel surface-enter rounded-lg p-3">
      <div className="flex items-center gap-2">
        <Search aria-hidden="true" size={16} />
        <input
          aria-label="Search conversations"
          className="min-h-10 w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] px-3 text-sm"
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search"
          value={query}
        />
      </div>
      <div className="mt-3 space-y-2">
        {filteredConversations.length === 0 ? (
          <p className="text-sm text-[var(--text-muted)]">No matching conversations.</p>
        ) : (
          filteredConversations.map((conversation) => (
            <a
              className={`block rounded-lg border px-3 py-2 text-sm ${
                activeConversation?.id === conversation.id
                  ? "active-glow"
                  : "border-[var(--border-subtle)]"
              }`}
              href={`/conversations?conversation=${conversation.id}`}
              key={conversation.id}
              onClick={() => setHistoryOpen(false)}
            >
              {conversation.title}
            </a>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div className="grid gap-5 lg:grid-cols-[18rem_minmax(0,1fr)]">
      <aside className="hidden space-y-4 lg:block">
        <form action={createConversationAction}>
          <button className="touch-target inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-4 text-sm font-semibold text-[#061019]">
            <MessageCirclePlus aria-hidden="true" size={18} />
            New conversation
          </button>
        </form>
        {renderConversationList()}
        <div className="quiet-panel rounded-lg p-3 text-sm text-[var(--text-secondary)]">
          <h2 className="font-semibold">Usage</h2>
          <p className="mt-2">Today: {formatUsage(usage.daily)}</p>
          <p>Month: {formatUsage(usage.monthly)}</p>
        </div>
      </aside>

      <section className="quiet-panel surface-enter min-h-[34rem] rounded-lg p-3 md:p-5">
        <div className="mb-4 flex items-center justify-between gap-3 lg:hidden">
          <button
            className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm"
            onClick={() => setHistoryOpen(true)}
            type="button"
          >
            <PanelLeft aria-hidden="true" size={17} />
            History
          </button>
          <form action={createConversationAction}>
            <button className="touch-target inline-flex items-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-3 text-sm font-semibold text-[#061019]">
              <MessageCirclePlus aria-hidden="true" size={17} />
              New
            </button>
          </form>
        </div>
        {historyOpen ? (
          <div
            aria-label="Conversation history"
            aria-modal="true"
            className="fixed inset-0 z-50 bg-black/50 p-4 lg:hidden"
            role="dialog"
          >
            <div className="quiet-panel h-full max-w-sm rounded-lg bg-[var(--surface-raised)] p-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="font-semibold">Conversations</h2>
                <button
                  aria-label="Close conversation history"
                  className="touch-target rounded-lg border border-[var(--border-subtle)] px-3"
                  onClick={() => setHistoryOpen(false)}
                  type="button"
                >
                  <X aria-hidden="true" size={17} />
                </button>
              </div>
              {renderConversationList()}
            </div>
          </div>
        ) : null}
        {activeConversation ? (
          <div className="flex min-h-[32rem] flex-col gap-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              {isRenaming ? (
                <form action={renameAction} className="flex flex-1 flex-col gap-2 sm:flex-row">
                  <input name="conversation_id" type="hidden" value={activeConversation.id} />
                  <label className="sr-only" htmlFor="conversation-title">
                    Conversation title
                  </label>
                  <input
                    className="min-h-11 min-w-0 flex-1 rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] px-3 text-sm"
                    defaultValue={activeConversation.title}
                    id="conversation-title"
                    maxLength={120}
                    name="title"
                    required
                  />
                  <button
                    className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-3 text-sm font-semibold text-[#061019]"
                    disabled={renamePending}
                  >
                    <Save aria-hidden="true" size={17} />
                    Save
                  </button>
                  <button
                    className="touch-target inline-flex items-center justify-center rounded-lg border border-[var(--border-subtle)] px-3 text-sm"
                    onClick={() => setIsRenaming(false)}
                    type="button"
                  >
                    Cancel
                  </button>
                </form>
              ) : (
                <div className="flex min-w-0 items-center gap-2">
                  <h2 className="truncate text-xl font-semibold">{activeConversation.title}</h2>
                  <button
                    aria-label="Rename conversation"
                    className="touch-target rounded-lg border border-[var(--border-subtle)] px-3"
                    onClick={() => setIsRenaming(true)}
                    type="button"
                  >
                    <Pencil aria-hidden="true" size={16} />
                  </button>
                </div>
              )}
              <div className="flex items-center gap-2">
                {renameState.message ? (
                  <p
                    className={`text-sm ${
                      renameState.status === "error"
                        ? "text-[var(--status-danger)]"
                        : "text-[var(--text-muted)]"
                    }`}
                    role={renameState.status === "error" ? "alert" : "status"}
                  >
                    {renameState.message}
                  </p>
                ) : null}
                <form action={deleteConversationAction}>
                  <input name="conversation_id" type="hidden" value={activeConversation.id} />
                  <button className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm text-[var(--status-danger)]">
                    <Trash2 aria-hidden="true" size={17} />
                    Delete
                  </button>
                </form>
              </div>
            </div>
            <div className="flex-1 space-y-3 pb-2">
              {activeConversation.messages.length === 0 ? (
                <p className="text-sm text-[var(--text-muted)]">
                  Ask a question grounded in your ready PDFs.
                </p>
              ) : (
                activeConversation.messages.map((message) => (
                  <article
                    className={`message-bubble message-enter rounded-lg border border-[var(--border-subtle)] p-3 ${
                      message.role === "assistant"
                        ? "mr-auto max-w-3xl bg-[var(--surface-overlay)] shadow-[0_0_24px_var(--panel-glow)]"
                        : "ml-auto max-w-2xl bg-[var(--surface-inspector)]"
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
                            className="citation-card rounded-lg border border-[var(--border-subtle)] p-3 text-sm"
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
            <form
              action={formAction}
              className="composer-surface sticky bottom-0 space-y-3 border-t border-[var(--border-subtle)] pt-3"
              onSubmit={() => setSubmittedMessageCount(activeConversation.messages.length)}
            >
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
                      <label
                        className="document-chip flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 py-2 text-sm"
                        key={document.id}
                      >
                        <input
                          checked={selectedDocumentIds.includes(document.id)}
                          name="document_ids"
                          onChange={(event) => toggleDocument(document.id, event.target.checked)}
                          type="checkbox"
                          value={document.id}
                        />
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
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask from your documents"
                required
                value={question}
              />
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <AssistantOrb state={pending ? "retrieving document" : "ready"} />
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
                  {pending ? "Sending" : state.status === "error" ? "Retry" : "Send"}
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
