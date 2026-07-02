"use client";

import { useActionState, useState } from "react";
import type { ReactNode } from "react";
import { Check, Link2, Pencil, Plus, RotateCcw, Save, Trash2, X } from "lucide-react";

import {
  approveMemoryAction,
  createMemoryAction,
  deleteMemoryAction,
  disableMemoryAction,
  enableMemoryAction,
  type MemoryActionState,
  rejectMemoryAction,
  updateMemoryAction,
} from "@/features/memories/actions";
import type { Memory, MemoryType } from "@/lib/api/types";

const idleState = { status: "idle" as const, message: "" };
const memoryTypes: MemoryType[] = [
  "identity",
  "background",
  "goal",
  "preference",
  "project",
  "decision",
  "constraint",
  "other",
];

export function MemoryWorkspace({ memories }: { memories: Memory[] }) {
  const [createState, createAction, createPending] = useActionState(createMemoryAction, idleState);
  const [editState, editAction, editPending] = useActionState(updateMemoryAction, idleState);
  const [editingId, setEditingId] = useState<string | null>(null);
  const suggestions = memories.filter((memory) => memory.status === "suggested");
  const approved = memories.filter((memory) => memory.status === "approved");
  const disabled = memories.filter((memory) => memory.status === "disabled");

  return (
    <div className="space-y-6">
      <section className="quiet-panel rounded-lg p-4">
        <h2 className="text-lg font-semibold">User-controlled memory</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">
          Saved memories are separate from document citations. ContextOS may use approved active
          memories as remembered information, but document evidence still wins when the two
          conflict.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <SummaryCard label="Approved memories" value={approved.length} />
        <SummaryCard label="Pending suggestions" value={suggestions.length} />
        <SummaryCard label="Disabled memories" value={disabled.length} />
      </section>

      <section className="quiet-panel rounded-lg p-4">
        <h2 className="font-semibold">Create memory</h2>
        <form action={createAction} className="mt-3 grid gap-3 md:grid-cols-[12rem_1fr_auto]">
          <label className="sr-only" htmlFor="memory-type">
            Memory type
          </label>
          <select
            className="min-h-11 rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] px-3 text-sm"
            id="memory-type"
            name="memory_type"
          >
            {memoryTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
          <label className="sr-only" htmlFor="memory-content">
            Memory content
          </label>
          <input
            className="min-h-11 rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] px-3 text-sm"
            id="memory-content"
            maxLength={1200}
            name="content"
            placeholder="What should ContextOS remember?"
            required
          />
          <button
            className="touch-target inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-4 text-sm font-semibold text-[#061019]"
            disabled={createPending}
          >
            <Plus aria-hidden="true" size={17} />
            Save
          </button>
        </form>
        {createState.message ? (
          <p
            className={`mt-2 text-sm ${
              createState.status === "error"
                ? "text-[var(--status-danger)]"
                : "text-[var(--text-muted)]"
            }`}
            role={createState.status === "error" ? "alert" : "status"}
          >
            {createState.message}
          </p>
        ) : null}
      </section>

      <MemorySection
        actionState={editState}
        editingId={editingId}
        editPending={editPending}
        memories={suggestions}
        onCancel={() => setEditingId(null)}
        onEdit={setEditingId}
        title="Suggested"
        updateAction={editAction}
      />
      <MemorySection
        actionState={editState}
        editingId={editingId}
        editPending={editPending}
        memories={approved}
        onCancel={() => setEditingId(null)}
        onEdit={setEditingId}
        title="Approved"
        updateAction={editAction}
      />
      <MemorySection
        actionState={editState}
        editingId={editingId}
        editPending={editPending}
        memories={disabled}
        onCancel={() => setEditingId(null)}
        onEdit={setEditingId}
        title="Disabled"
        updateAction={editAction}
      />
    </div>
  );
}

function MemorySection({
  actionState,
  editingId,
  editPending,
  memories,
  onCancel,
  onEdit,
  title,
  updateAction,
}: {
  actionState: MemoryActionState;
  editingId: string | null;
  editPending: boolean;
  memories: Memory[];
  onCancel: () => void;
  onEdit: (memoryId: string) => void;
  title: string;
  updateAction: (payload: FormData) => void;
}) {
  return (
    <section className="quiet-panel rounded-lg p-4">
      <h2 className="font-semibold">{title}</h2>
      <div className="mt-3 space-y-3">
        {memories.length === 0 ? (
          <p className="text-sm text-[var(--text-muted)]">No {title.toLowerCase()} memories.</p>
        ) : (
          memories.map((memory) => (
            <article
              className="rounded-lg border border-[var(--border-subtle)] p-3"
              id={`memory-${memory.id}`}
              key={memory.id}
            >
              {editingId === memory.id ? (
                <form action={updateAction} className="grid gap-3">
                  <input name="memory_id" type="hidden" value={memory.id} />
                  <select
                    className="min-h-11 rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] px-3 text-sm"
                    defaultValue={memory.memory_type}
                    name="memory_type"
                  >
                    {memoryTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                  <textarea
                    className="min-h-24 rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-inspector)] p-3 text-sm"
                    defaultValue={memory.content}
                    maxLength={1200}
                    name="content"
                    required
                  />
                  <div className="flex flex-wrap gap-2">
                    <button
                      className="touch-target inline-flex items-center gap-2 rounded-lg bg-[var(--accent-intelligence)] px-3 text-sm font-semibold text-[#061019]"
                      disabled={editPending}
                    >
                      <Save aria-hidden="true" size={16} />
                      Save
                    </button>
                    <button
                      className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm"
                      onClick={onCancel}
                      type="button"
                    >
                      <X aria-hidden="true" size={16} />
                      Cancel
                    </button>
                  </div>
                  {actionState.message ? (
                    <p className="text-sm text-[var(--text-muted)]">{actionState.message}</p>
                  ) : null}
                </form>
              ) : (
                <>
                  <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                    <div>
                      <p className="text-xs font-semibold uppercase text-[var(--text-muted)]">
                        {memory.memory_type} / {memory.status}
                      </p>
                      <p className="mt-2 text-sm leading-6">{memory.content}</p>
                      <p className="mt-2 text-xs text-[var(--text-muted)]">
                        Source: {memory.source_kind}
                        {memory.source_conversation_id ? (
                          <>
                            {" "}
                            <a
                              className="inline-flex items-center gap-1 underline"
                              href={`/conversations?conversation=${memory.source_conversation_id}`}
                            >
                              <Link2 aria-hidden="true" size={13} />
                              {memory.source_conversation_title ?? "Deleted conversation"}
                            </a>
                          </>
                        ) : null}
                      </p>
                    </div>
                    <MemoryActions memory={memory} onEdit={onEdit} />
                  </div>
                </>
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}

function MemoryActions({
  memory,
  onEdit,
}: {
  memory: Memory;
  onEdit: (memoryId: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {memory.status === "suggested" ? (
        <>
          <MemoryForm action={approveMemoryAction} icon={<Check size={16} />} label="Approve" memory={memory} />
          <MemoryForm action={rejectMemoryAction} icon={<X size={16} />} label="Reject" memory={memory} />
        </>
      ) : null}
      {memory.status === "approved" ? (
        <MemoryForm action={disableMemoryAction} icon={<X size={16} />} label="Disable" memory={memory} />
      ) : null}
      {memory.status === "disabled" ? (
        <MemoryForm action={enableMemoryAction} icon={<RotateCcw size={16} />} label="Enable" memory={memory} />
      ) : null}
      <button
        className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm"
        onClick={() => onEdit(memory.id)}
        type="button"
      >
        <Pencil aria-hidden="true" size={16} />
        Edit
      </button>
      <MemoryForm action={deleteMemoryAction} icon={<Trash2 size={16} />} label="Delete" memory={memory} />
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: number }) {
  return (
    <section className="quiet-panel rounded-lg p-4">
      <p className="text-sm text-[var(--text-secondary)]">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </section>
  );
}

function MemoryForm({
  action,
  icon,
  label,
  memory,
}: {
  action: (formData: FormData) => void;
  icon: ReactNode;
  label: string;
  memory: Memory;
}) {
  return (
    <form action={action}>
      <input name="memory_id" type="hidden" value={memory.id} />
      <button
        className="touch-target inline-flex items-center gap-2 rounded-lg border border-[var(--border-subtle)] px-3 text-sm"
        onClick={(event) => {
          if (label === "Delete" && !window.confirm("Delete this memory?")) {
            event.preventDefault();
          }
        }}
      >
        {icon}
        {label}
      </button>
    </form>
  );
}
