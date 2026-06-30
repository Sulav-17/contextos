"use server";

import { revalidatePath } from "next/cache";

import { deleteDocument, retryDocument, uploadDocument } from "@/lib/api/documents";

export type DocumentActionState = {
  status: "idle" | "success" | "error";
  message: string;
};

export async function uploadDocumentAction(
  _state: DocumentActionState,
  formData: FormData,
): Promise<DocumentActionState> {
  try {
    const file = formData.get("file");
    if (!(file instanceof File) || file.size === 0) {
      return { status: "error", message: "Choose a PDF before uploading." };
    }
    await uploadDocument(formData);
    revalidatePath("/libraries");
    return { status: "success", message: "Upload queued for processing." };
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Upload failed.",
    };
  }
}

export async function retryDocumentAction(formData: FormData): Promise<void> {
  const documentId = String(formData.get("document_id") ?? "");
  await retryDocument(documentId);
  revalidatePath("/libraries");
}

export async function deleteDocumentAction(formData: FormData): Promise<void> {
  const documentId = String(formData.get("document_id") ?? "");
  await deleteDocument(documentId);
  revalidatePath("/libraries");
}
