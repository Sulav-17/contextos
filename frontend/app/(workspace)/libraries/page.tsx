import { EmptyState } from "@/components/status/empty-state";

export const metadata = { title: "Libraries" };

export default function LibrariesPage() {
  return (
    <>
      <h1 className="text-3xl font-semibold">Libraries</h1>
      <div className="mt-8">
        <EmptyState title="Libraries are waiting for the document milestone">
          Private PDF storage and ingestion begin later. This page does not show sample documents.
        </EmptyState>
      </div>
    </>
  );
}
