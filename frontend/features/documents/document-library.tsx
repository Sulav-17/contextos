"use client";

import { useActionState, useEffect, useMemo, useState } from "react";
import { Download, MessageCirclePlus, RefreshCw, Trash2, Upload } from "lucide-react";
import { useRouter } from "next/navigation";

import { createScopedConversationAction } from "@/features/conversations/actions";
import {
  deleteDocumentAction,
  retryDocumentAction,
  uploadDocumentAction,
} from "@/features/documents/actions";
import type { DocumentMetadata } from "@/lib/api/types";

const idleDocumentActionState = { status: "idle" as const, message: "" };

function formatBytes(size: number): string {
  if (size < 1024 * 1024) {
    return `${Math.round(size / 1024)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
}

function statusLabel(document: DocumentMetadata): string {
  if (document.status === "failed") {
    return document.failure_reason ?? "Processing failed.";
  }
  if (document.status === "ready") {
    return "Ready";
  }
  return document.status.charAt(0).toUpperCase() + document.status.slice(1);
}

export function DocumentLibrary({
  documents,
  maxSizeMb,
  maxDocuments,
}: {
  documents: DocumentMetadata[];
  maxSizeMb: number;
  maxDocuments: number;
}) {
  const router = useRouter();
  const [state, formAction, pending] = useActionState(
    uploadDocumentAction,
    idleDocumentActionState,
  );
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const hasActiveProcessing = documents.some((document) =>
    ["queued", "processing"].includes(document.status),
  );
  const readyDocuments = useMemo(
    () => documents.filter((document) => document.status === "ready"),
    [documents],
  );

  useEffect(() => {
    if (!hasActiveProcessing) {
      return;
    }
    const interval = window.setInterval(() => router.refresh(), 3500);
    return () => window.clearInterval(interval);
  }, [hasActiveProcessing, router]);

  return (
    <div className="space-y-6">
      <form action={formAction} className="quiet-panel rounded-lg border-dashed p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Private PDFs</h2>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
              PDF only. Up to {maxSizeMb} MB each, {maxDocuments} documents during beta.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              accept="application/pdf,.pdf"
              aria-label="Choose PDF"
              className="touch-target max-w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-overlay)] px-3 py-2 text-sm"
              name="file"
              required
              type="file"
            />
            <button
              className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-document)] px-4 text-sm font-semibold text-[#07111f] disabled:cursor-not-allowed disabled:opacity-60"
              disabled={pending}
              type="submit"
            >
              <Upload aria-hidden="true" size={18} />
              {pending ? "Uploading" : "Upload"}
            </button>
          </div>
        </div>
        <p
          className={`mt-3 text-sm ${
            state.status === "error" ? "text-[var(--status-danger)]" : "text-[var(--text-muted)]"
          }`}
          role={state.status === "error" ? "alert" : "status"}
        >
          {state.message ||
            "General chat works without PDFs. Select documents when you want cited answers."}
        </p>
      </form>

      {readyDocuments.length > 1 ? (
        <section className="quiet-panel rounded-lg p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="font-semibold">Start a scoped conversation</h2>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                Select one or more ready documents, then start a conversation with that scope.
              </p>
            </div>
            <form action={createScopedConversationAction}>
              {selectedIds.map((documentId) => (
                <input key={documentId} name="document_ids" type="hidden" value={documentId} />
              ))}
              <button
                className="touch-target inline-flex items-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-4 text-sm font-semibold text-[#061019] disabled:opacity-60"
                disabled={selectedIds.length === 0}
              >
                <MessageCirclePlus aria-hidden="true" size={17} />
                Start with selected documents
              </button>
            </form>
          </div>
        </section>
      ) : null}

      {documents.length === 0 ? (
        <div className="quiet-panel rounded-lg p-6">
          <h2 className="text-lg font-semibold">No documents yet</h2>
          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            Upload a PDF to build your library, ask cited questions from selected documents, and
            keep general chat available even without documents.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((document) => (
            <article className="quiet-panel rounded-lg p-4" id={`document-${document.id}`} key={document.id}>
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-3">
                    {document.status === "ready" ? (
                      <label className="document-chip inline-flex touch-target items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm">
                        <input
                          checked={selectedIds.includes(document.id)}
                          onChange={(event) =>
                            setSelectedIds((current) =>
                              event.target.checked
                                ? current.includes(document.id)
                                  ? current
                                  : [...current, document.id]
                                : current.filter((id) => id !== document.id),
                            )
                          }
                          type="checkbox"
                        />
                        <span>Select</span>
                      </label>
                    ) : null}
                    <h2 className="truncate text-base font-semibold">{document.original_filename}</h2>
                  </div>
                  <dl className="mt-2 flex flex-wrap gap-x-4 gap-y-2 text-sm text-[var(--text-secondary)]">
                    <div>
                      <dt className="sr-only">Size</dt>
                      <dd>{formatBytes(document.size_bytes)}</dd>
                    </div>
                    <div>
                      <dt className="sr-only">Pages</dt>
                      <dd>{document.page_count ?? "Unknown"} pages</dd>
                    </div>
                    <div>
                      <dt className="sr-only">Created</dt>
                      <dd>{formatDate(document.created_at)}</dd>
                    </div>
                  </dl>
                  <p
                    className={`mt-2 text-sm ${
                      document.status === "failed"
                        ? "text-[var(--status-danger)]"
                        : "text-[var(--text-muted)]"
                    }`}
                  >
                    {statusLabel(document)}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {document.status === "ready" ? (
                    <form action={createScopedConversationAction}>
                      <input name="document_ids" type="hidden" value={document.id} />
                      <button className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-3 text-sm font-semibold text-[#061019]">
                        <MessageCirclePlus aria-hidden="true" size={17} />
                        Ask about this document
                      </button>
                    </form>
                  ) : null}
                  <a
                    aria-disabled={document.status === "deleted"}
                    className="touch-target inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm text-[var(--text-secondary)]"
                    href={`/libraries/${document.id}/download`}
                  >
                    <Download aria-hidden="true" size={17} />
                    Download
                  </a>
                  {document.status === "failed" ? (
                    <form action={retryDocumentAction}>
                      <input name="document_id" type="hidden" value={document.id} />
                      <button className="touch-target inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm text-[var(--text-secondary)]">
                        <RefreshCw aria-hidden="true" size={17} />
                        Retry
                      </button>
                    </form>
                  ) : null}
                  <form
                    action={deleteDocumentAction}
                    onSubmit={(event) => {
                      if (!window.confirm("Delete this document and its extracted chunks?")) {
                        event.preventDefault();
                      }
                    }}
                  >
                    <input name="document_id" type="hidden" value={document.id} />
                    <button className="touch-target inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm text-[var(--status-danger)]">
                      <Trash2 aria-hidden="true" size={17} />
                      Delete
                    </button>
                  </form>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
