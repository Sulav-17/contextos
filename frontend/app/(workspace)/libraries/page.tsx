import { DocumentLibrary } from "@/features/documents/document-library";
import { getDocuments } from "@/lib/api/documents";

export const metadata = { title: "Libraries" };

export default async function LibrariesPage() {
  const { documents } = await getDocuments();

  return (
    <>
      <h1 className="text-3xl font-semibold">Libraries</h1>
      <div className="mt-6">
        <DocumentLibrary documents={documents} maxSizeMb={10} maxDocuments={10} />
      </div>
    </>
  );
}
