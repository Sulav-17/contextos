"use client";

import { useActionState } from "react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { createInvitationAction } from "@/features/invitations/actions";
import type { InvitationFormState } from "@/features/invitations/actions";

export function InvitationForm() {
  const [state, action, pending] = useActionState<InvitationFormState, FormData>(createInvitationAction, {
    status: "idle",
    message: "",
  });
  return (
    <form action={action} className="quiet-panel grid gap-4 rounded-3xl p-6">
      <AssistantOrb
        state={pending ? "sending invitation" : state.status === "error" ? "error" : state.status === "success" ? "success" : "ready"}
      />
      <div className="grid gap-2">
        <label htmlFor="invite-email" className="text-sm font-medium">
          Invite email
        </label>
        <input
          id="invite-email"
          name="email"
          type="email"
          required
          className="touch-target rounded-xl border border-[var(--border-subtle)] bg-black/20 px-3"
        />
      </div>
      {state.message ? (
        <p role={state.status === "error" ? "alert" : "status"} className="text-sm text-[var(--status-warning)]">
          {state.message}
        </p>
      ) : null}
      <button
        disabled={pending}
        className="touch-target rounded-xl bg-[var(--accent-intelligence)] px-4 font-semibold text-[#051018] disabled:opacity-70"
      >
        {pending ? "Sending invitation" : "Send invitation"}
      </button>
    </form>
  );
}
