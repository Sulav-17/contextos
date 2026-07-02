import { MemoryWorkspace } from "@/features/memories/memory-workspace";
import { getMemories } from "@/lib/api/memories";

export const metadata = { title: "Memories" };

export default async function MemoriesPage() {
  const { memories } = await getMemories();
  return (
    <>
      <h1 className="text-3xl font-semibold">Memories</h1>
      <div className="mt-8">
        <MemoryWorkspace memories={memories} />
      </div>
    </>
  );
}
