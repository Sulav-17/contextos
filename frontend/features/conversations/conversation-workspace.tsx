"use client";

import { useActionState, useEffect, useMemo, useRef, useState } from "react";
import {
  Archive,
  ChevronRight,
  MessageCirclePlus,
  PanelLeft,
  PanelRight,
  Pencil,
  RotateCcw,
  Save,
  Search,
  Send,
  Trash2,
  X,
} from "lucide-react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import {
  createConversationAction,
  archiveConversationAction,
  deleteConversationAction,
  renameConversationAction,
  submitQuestionAction,
  unarchiveConversationAction,
} from "@/features/conversations/actions";
import type {
  ConversationDetail,
  ConversationMessage,
  ConversationSummary,
  DocumentMetadata,
  UsageStatus,
} from "@/lib/api/types";
import { networkUnavailableMessage, useNetworkState } from "@/lib/pwa/network";

const idleChatState = { status: "idle" as const, message: "" };
const DRAFT_STORAGE_PREFIX = "contextos.conversationDraft.";

function formatUsage(bucket: { used: number; limit: number }): string {
  return `${bucket.used}/${bucket.limit}`;
}

function sourceBadge(message: ConversationMessage): string {
  if (message.source_mode === "memory_suggestion_created") {
    return "Memory suggestion created";
  }
  if (message.source_mode === "contextos") {
    return "ContextOS data";
  }
  if (message.source_mode === "general") {
    return "General answer";
  }
  if (message.source_mode === "memory") {
    return "Used saved memory";
  }
  if (message.source_mode === "documents") {
    const count = new Set(message.citations.map((citation) => citation.document_id)).size;
    return `Used ${count} ${count === 1 ? "document" : "documents"}`;
  }
  if (message.source_mode === "documents_and_memory") {
    const count = new Set(message.citations.map((citation) => citation.document_id)).size;
    return `Used memory + ${count} ${count === 1 ? "document" : "documents"}`;
  }
  return "Not enough evidence";
}

export function ConversationWorkspace({
  conversations,
  archivedConversations,
  activeConversation,
  documents,
  usage,
}: {
  conversations: ConversationSummary[];
  archivedConversations: ConversationSummary[];
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
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [networkMessage, setNetworkMessage] = useState("");
  const [historyFilter, setHistoryFilter] = useState<"active" | "archived">("active");
  const [query, setQuery] = useState("");
  const [question, setQuestion] = useState("");
  const historyRef = useRef<HTMLDivElement | null>(null);
  const isNearBottomRef = useRef(true);
  const submittingRef = useRef(false);
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
    () => {
      const source = historyFilter === "active" ? conversations : archivedConversations;
      return source.filter((conversation) =>
        conversation.title.toLowerCase().includes(query.trim().toLowerCase()),
      );
    },
    [archivedConversations, conversations, historyFilter, query],
  );
  const activeConversationId = activeConversation?.id ?? "";
  const helperText =
    selectedDocumentIds.length > 0
      ? "Answers will be grounded in the selected PDFs."
      : "General chat works without PDFs. Select documents when you want cited answers.";
  const latestAssistantMessage = [...(activeConversation?.messages ?? [])]
    .reverse()
    .find((message) => message.role === "assistant");
  const networkState = useNetworkState();
  const isOffline = networkState === "offline";

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
    if (!pending) {
      submittingRef.current = false;
    }
  }, [pending]);

  useEffect(() => {
    const history = historyRef.current;
    if (!history) {
      return;
    }
    history.scrollTop = history.scrollHeight;
    isNearBottomRef.current = true;
  }, [activeConversationId]);

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

  useEffect(() => {
    const history = historyRef.current;
    if (!history || !isNearBottomRef.current) {
      return;
    }
    history.scrollTop = history.scrollHeight;
  }, [activeConversation?.messages.length, pending]);

  function updateNearBottom() {
    const history = historyRef.current;
    if (!history) {
      return;
    }
    const remaining = history.scrollHeight - history.scrollTop - history.clientHeight;
    isNearBottomRef.current = remaining <= 96;
  }

  function toggleDocument(documentId: string, checked: boolean) {
    setSelectedDocumentIds((current) => {
      if (checked) {
        return current.includes(documentId) ? current : [...current, documentId];
      }
      return current.filter((id) => id !== documentId);
    });
  }

  function blockOffline(event: { preventDefault: () => void }, action: string) {
    if (!isOffline) {
      return;
    }
    event.preventDefault();
    setNetworkMessage(networkUnavailableMessage(action));
  }

  const renderConversationList = () => (
    <div className="quiet-panel surface-enter flex min-h-0 flex-col rounded-lg p-3">
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
      <div className="mt-3 grid grid-cols-2 gap-2">
        <button
          className={`touch-target rounded-lg border px-3 text-sm ${
            historyFilter === "active" ? "active-glow" : "border-[var(--border-subtle)]"
          }`}
          onClick={() => setHistoryFilter("active")}
          type="button"
        >
          Active
        </button>
        <button
          className={`touch-target rounded-lg border px-3 text-sm ${
            historyFilter === "archived" ? "active-glow" : "border-[var(--border-subtle)]"
          }`}
          onClick={() => setHistoryFilter("archived")}
          type="button"
        >
          Archived
        </button>
      </div>
      <div className="mt-3 min-h-0 space-y-2 overflow-y-auto overflow-x-hidden pr-1">
        {filteredConversations.length === 0 ? (
          <p className="text-sm text-[var(--text-muted)]">
            No matching {historyFilter} conversations.
          </p>
        ) : (
          filteredConversations.map((conversation) => (
            <a
              aria-label={conversation.title}
              className={`line-clamp-2 block rounded-lg border px-3 py-2 text-sm leading-5 ${
                activeConversation?.id === conversation.id
                  ? "active-glow"
                  : "border-[var(--border-subtle)]"
              }`}
              href={`/conversations?conversation=${conversation.id}`}
              key={conversation.id}
              onClick={() => setHistoryOpen(false)}
              title={conversation.title}
            >
              {conversation.title}
            </a>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div className="grid min-h-0 gap-5 xl:grid-cols-[18rem_minmax(0,1fr)_22rem]">
      <aside className="hidden min-h-0 space-y-4 lg:flex lg:flex-col">
        <form action={createConversationAction} onSubmit={(event) => blockOffline(event, "Starting a conversation")}>
          <button className="touch-target inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-4 text-sm font-semibold text-[#061019] disabled:opacity-60" disabled={isOffline}>
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

      <section className="quiet-panel surface-enter flex min-h-0 flex-col overflow-hidden rounded-lg p-3 md:p-5">
        <div className="mb-4 grid gap-3 lg:hidden">
          <div className="flex min-w-0 items-center justify-between gap-2">
            {isRenaming ? (
              <form
                action={renameAction}
                className="flex min-w-0 flex-1 flex-wrap items-center gap-2"
                onSubmit={(event) => blockOffline(event, "Renaming a conversation")}
              >
                <input name="conversation_id" type="hidden" value={activeConversation!.id} />
                <label className="sr-only" htmlFor="conversation-title-mobile">
                  Conversation title
                </label>
                <input
                  className="min-h-11 min-w-0 flex-1 rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] px-3 text-sm"
                  defaultValue={activeConversation!.title}
                  id="conversation-title-mobile"
                  maxLength={120}
                  name="title"
                  required
                />
                <button
                  className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-3 text-sm font-semibold text-[#061019]"
                  disabled={renamePending || isOffline}
                >
                  <Save aria-hidden="true" size={17} />
                  Save
                </button>
                <button
                  className="touch-target inline-flex items-center justify-center rounded-lg border border-[var(--border-subtle)] px-3 text-sm whitespace-nowrap"
                  onClick={() => setIsRenaming(false)}
                  type="button"
                >
                  Cancel
                </button>
              </form>
            ) : (
              <div className="flex min-w-0 items-center gap-2">
                <h2 className="min-w-0 truncate text-lg font-semibold" title={activeConversation!.title}>
                  {activeConversation!.title}
                </h2>
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
          </div>
          <div className="grid min-w-0 grid-cols-3 gap-2">
            <button
              className="touch-target inline-flex w-full items-center justify-center gap-2 rounded-lg border border-[var(--border-subtle)] px-2 text-sm whitespace-nowrap"
              onClick={() => setHistoryOpen(true)}
              type="button"
            >
              <PanelLeft aria-hidden="true" size={17} />
              History
            </button>
            <button
              className="touch-target inline-flex w-full items-center justify-center gap-2 rounded-lg border border-[var(--border-subtle)] px-2 text-sm whitespace-nowrap xl:hidden"
              onClick={() => setInspectorOpen(true)}
              type="button"
            >
              <PanelRight aria-hidden="true" size={17} />
              Context
            </button>
            <form
              action={createConversationAction}
              onSubmit={(event) => blockOffline(event, "Starting a conversation")}
            >
              <button
                className="touch-target inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-2 text-sm font-semibold whitespace-nowrap text-[#061019] disabled:opacity-60"
                disabled={isOffline}
              >
                <MessageCirclePlus aria-hidden="true" size={17} />
                New
              </button>
            </form>
          </div>
          <div className="flex flex-wrap gap-2">
            {activeConversation!.archived_at ? (
              <form
                action={unarchiveConversationAction}
                onSubmit={(event) => blockOffline(event, "Restoring a conversation")}
              >
                <input name="conversation_id" type="hidden" value={activeConversation!.id} />
                <button className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm whitespace-nowrap disabled:opacity-60" disabled={isOffline}>
                  <RotateCcw aria-hidden="true" size={17} />
                  Restore
                </button>
              </form>
            ) : (
              <form
                action={archiveConversationAction}
                onSubmit={(event) => blockOffline(event, "Archiving a conversation")}
              >
                <input name="conversation_id" type="hidden" value={activeConversation!.id} />
                <button className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm whitespace-nowrap disabled:opacity-60" disabled={isOffline}>
                  <Archive aria-hidden="true" size={17} />
                  Archive
                </button>
              </form>
            )}
            <form
              action={deleteConversationAction}
              onSubmit={(event) => blockOffline(event, "Deleting a conversation")}
            >
              <input name="conversation_id" type="hidden" value={activeConversation!.id} />
              <button
                className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm whitespace-nowrap text-[var(--status-danger)] disabled:opacity-60"
                onClick={(event) => {
                  if (!window.confirm("Delete this conversation?")) {
                    event.preventDefault();
                  }
                }}
                disabled={isOffline}
              >
                <Trash2 aria-hidden="true" size={17} />
                Delete
              </button>
            </form>
          </div>
        </div>
        {historyOpen ? (
          <div
            aria-label="Conversation history"
            aria-modal="true"
            className="fixed inset-0 z-50 bg-black/50 p-4 lg:hidden"
            role="dialog"
            onKeyDown={(event) => {
              if (event.key === "Escape") {
                setHistoryOpen(false);
              }
            }}
          >
            <div className="quiet-panel flex h-full max-w-sm flex-col overflow-hidden rounded-lg bg-[var(--surface-raised)] p-4">
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
        {inspectorOpen && latestAssistantMessage ? (
          <div
            aria-label="Context inspector"
            aria-modal="true"
            className="fixed inset-0 z-50 bg-black/50 p-4 xl:hidden"
            role="dialog"
            onKeyDown={(event) => {
              if (event.key === "Escape") {
                setInspectorOpen(false);
              }
            }}
          >
            <div className="quiet-panel ml-auto flex h-full max-w-sm flex-col overflow-hidden rounded-lg bg-[var(--surface-raised)] p-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="font-semibold">Context inspector</h2>
                <button
                  aria-label="Close context inspector"
                  className="touch-target rounded-lg border border-[var(--border-subtle)] px-3"
                  onClick={() => setInspectorOpen(false)}
                  type="button"
                >
                  <X aria-hidden="true" size={17} />
                </button>
              </div>
              <ContextInspector message={latestAssistantMessage} />
            </div>
          </div>
        ) : null}
        {activeConversation ? (
          <div className="flex min-h-0 flex-1 flex-col gap-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              {isRenaming ? (
                <form action={renameAction} className="flex flex-1 flex-col gap-2 sm:flex-row" onSubmit={(event) => blockOffline(event, "Renaming a conversation")}>
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
                    disabled={renamePending || isOffline}
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
                  <h2 className="text-xl font-semibold" title={activeConversation.title}>
                    {activeConversation.title}
                  </h2>
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
                <form action={deleteConversationAction} onSubmit={(event) => blockOffline(event, "Deleting a conversation")}>
                  <input name="conversation_id" type="hidden" value={activeConversation.id} />
                  <button
                    className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm text-[var(--status-danger)]"
                    onClick={(event) => {
                      if (!window.confirm("Delete this conversation?")) {
                        event.preventDefault();
                      }
                    }}
                  >
                    <Trash2 aria-hidden="true" size={17} />
                    Delete
                  </button>
                </form>
                {activeConversation.archived_at ? (
                  <form action={unarchiveConversationAction} onSubmit={(event) => blockOffline(event, "Restoring a conversation")}>
                    <input name="conversation_id" type="hidden" value={activeConversation.id} />
                    <button className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm disabled:opacity-60" disabled={isOffline}>
                      <RotateCcw aria-hidden="true" size={17} />
                      Restore
                    </button>
                  </form>
                ) : (
                  <form action={archiveConversationAction} onSubmit={(event) => blockOffline(event, "Archiving a conversation")}>
                    <input name="conversation_id" type="hidden" value={activeConversation.id} />
                    <button className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm disabled:opacity-60" disabled={isOffline}>
                      <Archive aria-hidden="true" size={17} />
                      Archive
                    </button>
                  </form>
                )}
                <button
                  className="touch-target hidden items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm xl:inline-flex"
                  onClick={() => setInspectorOpen(true)}
                  type="button"
                >
                  <PanelRight aria-hidden="true" size={17} />
                  Context inspector
                </button>
              </div>
            </div>
            <div
              className="min-h-0 flex-1 space-y-3 overflow-y-auto overflow-x-hidden pb-36 pr-1 md:pb-40"
              data-testid="conversation-history"
              onScroll={updateNearBottom}
              ref={historyRef}
            >
              {activeConversation.messages.length === 0 ? (
                <p className="text-sm text-[var(--text-muted)]">
                  Ask anything, use saved memory, or select PDFs for cited answers.
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
                    {message.role === "assistant" ? (
                      <div className="mt-2 flex flex-wrap items-center gap-2">
                        <span
                          className={`rounded-full border px-2 py-1 text-xs font-semibold ${
                            message.source_mode === "memory_suggestion_created"
                              ? "border-[var(--status-warning)] text-[var(--status-warning)]"
                              : "border-[var(--border-subtle)] text-[var(--text-muted)]"
                          }`}
                        >
                          {sourceBadge(message)}
                        </span>
                        {message.source_mode === "memory_suggestion_created" ? (
                          <a
                            className="rounded-full border border-[var(--border-subtle)] px-2 py-1 text-xs font-semibold underline"
                            href="/memories"
                          >
                            Review in Memories
                          </a>
                        ) : null}
                      </div>
                    ) : null}
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
                    {message.memory_references.length > 0 ? (
                      <div className="mt-3 space-y-2">
                        <p className="text-xs font-semibold uppercase text-[var(--text-muted)]">
                          Used saved memory
                        </p>
                        {message.memory_references.map((memory) => (
                          <details
                            className="rounded-lg border border-[var(--accent-intelligence)]/60 p-3 text-sm"
                            key={memory.id}
                          >
                            <summary className="cursor-pointer font-semibold">
                              Remembered {memory.memory_type}
                            </summary>
                            <p className="mt-2 leading-6 text-[var(--text-secondary)]">
                              {memory.content}
                            </p>
                            {memory.source_conversation_id ? (
                              <a
                                className="mt-2 inline-flex items-center gap-1 text-xs underline"
                                href={`/conversations?conversation=${memory.source_conversation_id}`}
                              >
                                <ChevronRight aria-hidden="true" size={13} />
                                {memory.source_conversation_title ?? "Source conversation"}
                              </a>
                            ) : null}
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
              className="composer-surface mt-auto shrink-0 space-y-3 border-t border-[var(--border-subtle)] pt-3"
              onSubmit={(event) => {
                if (isOffline) {
                  blockOffline(event, "Sending chat");
                  return;
                }
                if (submittingRef.current || pending || !question.trim()) {
                  event.preventDefault();
                  return;
                }
                submittingRef.current = true;
                setSubmittedMessageCount(activeConversation.messages.length);
              }}
            >
              <input name="conversation_id" type="hidden" value={activeConversation.id} />
              <fieldset className="rounded-lg border border-[var(--border-subtle)] p-3">
                <legend className="px-1 text-sm font-semibold text-[var(--text-secondary)]">
                  Optional document scope
                </legend>
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  {readyDocuments.length === 0 ? (
                    <p className="text-sm text-[var(--text-muted)]">
                      No retrieval-ready PDFs. Document selection is optional.
                    </p>
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
                placeholder="Ask a general question, use ContextOS data, or ask from selected documents"
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
                  {networkMessage ||
                    state.message ||
                    helperText}
                </p>
                <button
                  className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-document)] px-4 text-sm font-semibold text-[#07111f] disabled:opacity-60"
                  disabled={pending || isOffline || !question.trim()}
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
              <h2 className="text-xl font-semibold">No conversations yet</h2>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                Start a conversation to chat generally, ask from selected documents, or use
                authenticated ContextOS workspace data.
              </p>
            </div>
          </div>
        )}
      </section>
      <aside className="hidden min-h-0 xl:block">
        {latestAssistantMessage ? (
          <div className="quiet-panel h-full overflow-y-auto rounded-lg p-4">
            <h2 className="text-sm font-semibold text-[var(--text-secondary)]">
              Context inspector
            </h2>
            <div className="mt-3">
              <ContextInspector message={latestAssistantMessage} />
            </div>
          </div>
        ) : null}
      </aside>
    </div>
  );
}

function ContextInspector({ message }: { message: ConversationMessage }) {
  if (message.source_mode === "contextos") {
    return (
      <div className="space-y-3 text-sm">
        <p className="rounded-full border border-[var(--border-subtle)] px-2 py-1 font-semibold">
          ContextOS data
        </p>
        <p className="text-[var(--text-secondary)]">
          Authenticated workspace metadata was used.
        </p>
      </div>
    );
  }
  if (message.source_mode === "memory_suggestion_created") {
    return (
      <div className="space-y-3 text-sm">
        <p className="rounded-full border border-[var(--status-warning)] px-2 py-1 font-semibold">
          Awaiting approval
        </p>
        <p className="text-[var(--text-secondary)]">
          Memory suggestion created. Review it before it can influence answers.
        </p>
        <a className="inline-flex items-center gap-1 underline" href="/memories">
          <ChevronRight aria-hidden="true" size={13} />
          Review action
        </a>
      </div>
    );
  }
  if (message.source_mode === "insufficient_evidence") {
    return (
      <div className="space-y-3 text-sm">
        <p className="rounded-full border border-[var(--border-subtle)] px-2 py-1 font-semibold">
          Not enough evidence
        </p>
        <p className="text-[var(--text-secondary)]">No reliable source found.</p>
      </div>
    );
  }
  if (message.source_mode === "general") {
    return (
      <div className="space-y-3 text-sm">
        <p className="rounded-full border border-[var(--border-subtle)] px-2 py-1 font-semibold">
          General answer
        </p>
        <p className="text-[var(--text-secondary)]">
          No documents or saved memories were used.
        </p>
      </div>
    );
  }
  return (
    <div className="space-y-4 text-sm">
      {message.citations.length > 0 ? (
        <section>
          <h3 className="font-semibold">Documents</h3>
          <p className="mt-1 text-[var(--text-secondary)]">
            Citation count: {message.citations.length}
          </p>
          <div className="mt-2 space-y-2">
            {message.citations.map((citation) => (
              <div className="rounded-lg border border-[var(--border-subtle)] p-2" key={citation.citation_index}>
                <p className="font-medium">{citation.document_name}</p>
                <p className="text-[var(--text-muted)]">Page {citation.page_number}</p>
              </div>
            ))}
          </div>
        </section>
      ) : null}
      {message.memory_references.length > 0 ? (
        <section>
          <h3 className="font-semibold">Used saved memory</h3>
          <div className="mt-2 space-y-2">
            {message.memory_references.map((memory) => (
              <div className="rounded-lg border border-[var(--border-subtle)] p-2" key={memory.id}>
                <p className="font-medium">{memory.memory_type}</p>
                <p className="mt-1 text-[var(--text-secondary)]">{memory.content}</p>
                {memory.source_conversation_id ? (
                  <a
                    className="mt-2 inline-flex items-center gap-1 text-xs underline"
                    href={`/conversations?conversation=${memory.source_conversation_id}`}
                  >
                    <ChevronRight aria-hidden="true" size={13} />
                    {memory.source_conversation_title ?? "Source conversation"}
                  </a>
                ) : null}
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
