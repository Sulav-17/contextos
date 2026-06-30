"use client";

import { useActionState } from "react";

import { FormState, loginAction } from "@/lib/auth/actions";

const initialState: FormState = { status: "idle", message: "" };

export function LoginForm({ next = "/home" }: { next?: string }) {
  const [state, action, pending] = useActionState<FormState, FormData>(loginAction, initialState);
  return (
    <form action={action} className="grid gap-4" noValidate>
      <input type="hidden" name="next" value={next} />
      <div className="grid gap-2">
        <label htmlFor="email" className="text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          className="touch-target rounded-xl border border-[var(--border-subtle)] bg-black/20 px-3 text-[var(--text-primary)]"
        />
      </div>
      <div className="grid gap-2">
        <label htmlFor="password" className="text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          className="touch-target rounded-xl border border-[var(--border-subtle)] bg-black/20 px-3 text-[var(--text-primary)]"
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
        {pending ? "Checking session" : "Log in"}
      </button>
    </form>
  );
}
