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

export function AssistantOrb({ state, reducedMotion = false }: AssistantOrbProps) {
  return (
    <div className="flex items-center gap-3" role="status" aria-live="polite">
      <div
        aria-hidden="true"
        className={`relative h-12 w-12 rounded-full border border-[var(--border-strong)] bg-[radial-gradient(circle_at_35%_30%,rgba(80,217,246,0.95),rgba(80,217,246,0.18)_34%,rgba(157,155,255,0.2)_62%,rgba(5,9,18,0.6))] shadow-[0_0_28px_rgba(80,217,246,0.16)] ${reducedMotion ? "" : "orb-motion"}`}
      >
        <span className="absolute left-1/2 top-1/2 h-16 w-16 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--line-context)]" />
      </div>
      <span className="text-sm font-medium text-[var(--text-secondary)]">Assistant status: {state}</span>
    </div>
  );
}
