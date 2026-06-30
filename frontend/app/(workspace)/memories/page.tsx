import { EmptyState } from "@/components/status/empty-state";

export const metadata = { title: "Memories" };

export default function MemoriesPage() {
  return (
    <>
      <h1 className="text-3xl font-semibold">Memories</h1>
      <div className="mt-8">
        <EmptyState title="No memory candidates are used or shown">
          Long-term memory requires explicit approval in a later milestone. Unapproved memories are
          not used in answers.
        </EmptyState>
      </div>
    </>
  );
}
