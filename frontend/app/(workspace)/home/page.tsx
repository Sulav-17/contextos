import { EmptyState } from "@/components/status/empty-state";
import { getMe, getPreferences } from "@/lib/api/me";

export const metadata = { title: "Home" };

export default async function HomePage() {
  const [user, preferences] = await Promise.all([getMe(), getPreferences()]);
  const greeting =
    preferences.greeting_mode === "full"
      ? "Welcome to your private knowledge space"
      : preferences.greeting_mode === "direct"
        ? "Workspace ready"
        : `Good to see you${user.display_name ? `, ${user.display_name}` : ""}`;

  return (
    <>
      <h1 className="text-3xl font-semibold">{greeting}</h1>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
        ContextOS is ready for the next approved milestone. Documents, conversations, retrieval,
        and memory are intentionally not implemented yet.
      </p>
      <div className="mt-8">
        <EmptyState title="Your knowledge space is ready">
          No documents, conversations, citations, uploads, or approved memories are shown because
          those features begin in later milestones.
        </EmptyState>
      </div>
    </>
  );
}
