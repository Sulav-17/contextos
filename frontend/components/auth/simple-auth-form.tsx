"use client";

import { useActionState } from "react";

import type { FormState } from "@/lib/auth/actions";

type Action = (state: FormState, formData: FormData) => Promise<FormState>;

export function SimpleAuthForm({
  action,
  buttonLabel,
  fieldLabel,
  fieldName,
  fieldType,
}: {
  action: Action;
  buttonLabel: string;
  fieldLabel: string;
  fieldName: string;
  fieldType: string;
}) {
  const [state, formAction, pending] = useActionState<FormState, FormData>(action, {
    status: "idle",
    message: "",
  });
  return (
    <form action={formAction} className="grid gap-4">
      <div className="grid gap-2">
        <label htmlFor={fieldName} className="text-sm font-medium">
          {fieldLabel}
        </label>
        <input
          id={fieldName}
          name={fieldName}
          type={fieldType}
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
        {pending ? "Working" : buttonLabel}
      </button>
    </form>
  );
}
