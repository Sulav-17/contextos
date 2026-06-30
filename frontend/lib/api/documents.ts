import "server-only";

import { apiFetch } from "@/lib/api/client";
import type { DocumentList, DocumentMetadata } from "@/lib/api/types";

export function getDocuments(): Promise<DocumentList> {
  return apiFetch<DocumentList>("/api/v1/documents");
}

export function uploadDocument(formData: FormData): Promise<DocumentMetadata> {
  return apiFetch<DocumentMetadata>("/api/v1/documents", {
    method: "POST",
    body: formData,
  });
}

export function retryDocument(documentId: string): Promise<DocumentMetadata> {
  return apiFetch<DocumentMetadata>(`/api/v1/documents/${documentId}/retry`, {
    method: "POST",
  });
}

export function deleteDocument(documentId: string): Promise<void> {
  return apiFetch<void>(`/api/v1/documents/${documentId}`, {
    method: "DELETE",
  });
}
