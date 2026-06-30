"use client";

import { useActionState } from "react";

import { AssistantOrb } from "@/components/assistant/assistant-orb";
import { savePreferencesAction } from "@/features/preferences/actions";
import type { Preferences } from "@/lib/api/types";
import type { PreferencesFormState } from "@/features/preferences/actions";

export function PreferencesForm({ preferences }: { preferences: Preferences }) {
  const [state, action, pending] = useActionState<PreferencesFormState, FormData>(savePreferencesAction, {
    status: "idle",
    message: "",
  });
  return (
    <form action={action} className="quiet-panel grid gap-6 rounded-3xl p-6">
      <AssistantOrb state={pending ? "saving preference" : state.status === "success" ? "success" : "ready"} />
      <fieldset className="grid gap-3">
        <legend className="font-semibold">Greeting</legend>
        {(["full", "minimized", "direct"] as const).map((mode) => (
          <label key={mode} className="flex min-h-11 items-center gap-3">
            <input name="greeting_mode" type="radio" value={mode} defaultChecked={preferences.greeting_mode === mode} />
            {mode === "full" ? "Full welcome" : mode === "minimized" ? "Minimized greeting" : "Direct workspace entry"}
          </label>
        ))}
      </fieldset>
      <fieldset className="grid gap-3">
        <legend className="font-semibold">Motion</legend>
        {(["system", "reduced"] as const).map((mode) => (
          <label key={mode} className="flex min-h-11 items-center gap-3">
            <input name="motion_mode" type="radio" value={mode} defaultChecked={preferences.motion_mode === mode} />
            {mode === "system" ? "Follow system" : "Reduced motion"}
          </label>
        ))}
      </fieldset>
      <fieldset className="grid gap-3">
        <legend className="font-semibold">Theme</legend>
        {(["dark", "system"] as const).map((mode) => (
          <label key={mode} className="flex min-h-11 items-center gap-3">
            <input name="theme_mode" type="radio" value={mode} defaultChecked={preferences.theme_mode === mode} />
            {mode === "dark" ? "Dark Quiet Orbit" : "Follow system when available"}
          </label>
        ))}
      </fieldset>
      <label className="flex min-h-11 items-center gap-3">
        <input name="welcome_completed" type="checkbox" defaultChecked={preferences.welcome_completed} />
        Welcome completed
      </label>
      {state.message ? (
        <p role={state.status === "error" ? "alert" : "status"} className="text-sm text-[var(--status-warning)]">
          {state.message}
        </p>
      ) : null}
      <button
        disabled={pending}
        className="touch-target rounded-xl bg-[var(--accent-intelligence)] px-4 font-semibold text-[#051018] disabled:opacity-70"
      >
        {pending ? "Saving preference" : "Save preferences"}
      </button>
    </form>
  );
}
