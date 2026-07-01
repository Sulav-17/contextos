export type AssistantState =
  | "idle"
  | "checking session"
  | "ready"
  | "saving preference"
  | "sending invitation"
  | "success"
  | "error"
  | "backend unavailable"
  | "retrieving document"
  | "memory review";

type AssistantOrbProps = {
  state: AssistantState;
  reducedMotion?: boolean;
};

function visualStateFor(state: AssistantState): "idle" | "ready" | "thinking" | "error" {
  if (state === "error" || state === "backend unavailable") {
    return "error";
  }
  if (
    state === "checking session" ||
    state === "saving preference" ||
    state === "sending invitation" ||
    state === "retrieving document"
  ) {
    return "thinking";
  }
  if (state === "ready" || state === "success") {
    return "ready";
  }
  return "idle";
}

export function AssistantOrb({ state, reducedMotion = false }: AssistantOrbProps) {
  const visualState = visualStateFor(state);
  return (
    <div className="flex items-center gap-3" role="status" aria-live="polite">
      <div
        aria-hidden="true"
        className="assistant-orb"
        data-reduced-motion={reducedMotion ? "true" : "false"}
        data-state={visualState}
      >
        <span className="orb-ring orb-ring-outer" />
        <span className="orb-ring orb-ring-inner" />
        <span className="orb-core" />
        <span className="orb-particle" />
      </div>
      <span className="text-sm font-medium text-[var(--text-secondary)]">
        Assistant status: {state}
      </span>
    </div>
  );
}
