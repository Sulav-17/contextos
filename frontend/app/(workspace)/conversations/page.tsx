import { EmptyState } from "@/components/status/empty-state";

export const metadata = { title: "Conversations" };

export default function ConversationsPage() {
  return (
    <>
      <h1 className="text-3xl font-semibold">Conversations</h1>
      <div className="mt-8">
        <EmptyState title="Conversations arrive after retrieval is approved">
          Persistent conversations and citation-backed answers are out of scope for Milestone 4.
        </EmptyState>
      </div>
    </>
  );
}
