"use client";

import { useActionState } from "react";

import { signupAction, type FormState } from "@/lib/auth/actions";

const initialState: FormState = { status: "idle", message: "" };

export function SignupForm({
  next = "/home",
  actionHandler = signupAction,
}: {
  next?: string;
  actionHandler?: typeof signupAction;
}) {
  const [state, action, pending] = useActionState<FormState, FormData>(
    actionHandler,
    initialState,
  );
  return (
    <form action={action} className="grid gap-4" noValidate>
      <input type="hidden" name="next" value={next} />
      <div className="grid gap-2">
        <label htmlFor="signup-email" className="text-sm font-medium">
          Email
        </label>
        <input
          id="signup-email"
          name="email"
          type="email"
          autoComplete="email"
          required
          className="touch-target rounded-xl border border-[var(--border-subtle)] bg-black/20 px-3 text-[var(--text-primary)]"
        />
      </div>
      <div className="grid gap-2">
        <label htmlFor="signup-password" className="text-sm font-medium">
          Password
        </label>
        <input
          id="signup-password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          className="touch-target rounded-xl border border-[var(--border-subtle)] bg-black/20 px-3 text-[var(--text-primary)]"
        />
      </div>
      {state.message ? (
        <p
          role={state.status === "error" ? "alert" : "status"}
          className="text-sm text-[var(--status-warning)]"
        >
          {state.message}
        </p>
      ) : null}
      <button
        disabled={pending}
        className="touch-target rounded-xl bg-[var(--accent-memory)] px-4 font-semibold text-[#15100a] disabled:opacity-70"
      >
        {pending ? "Creating account" : "Create account"}
      </button>
    </form>
  );
}
