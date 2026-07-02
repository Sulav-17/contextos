import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DocumentLibrary } from "@/features/documents/document-library";
import type { DocumentMetadata } from "@/lib/api/types";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

vi.mock("@/features/documents/actions", () => ({
  deleteDocumentAction: vi.fn(),
  retryDocumentAction: vi.fn(),
  uploadDocumentAction: vi.fn(),
}));
vi.mock("@/features/conversations/actions", () => ({
  createScopedConversationAction: vi.fn(),
}));

function document(overrides: Partial<DocumentMetadata> = {}): DocumentMetadata {
  return {
    id: "50000000-0000-4000-8000-000000000001",
    original_filename: "research.pdf",
    mime_type: "application/pdf",
    size_bytes: 2048,
    checksum_sha256: null,
    status: "ready",
    page_count: 3,
    extracted_character_count: 1200,
    failure_code: null,
    failure_reason: null,
    created_at: "2026-06-30T12:00:00Z",
    updated_at: "2026-06-30T12:00:00Z",
    processed_at: "2026-06-30T12:01:00Z",
    ...overrides,
  };
}

describe("DocumentLibrary", () => {
  beforeEach(() => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    Object.defineProperty(navigator, "onLine", { configurable: true, value: true });
  });

  it("renders an empty library with upload controls", () => {
    render(<DocumentLibrary documents={[]} maxDocuments={10} maxSizeMb={10} />);

    expect(screen.getByRole("heading", { name: "Private PDFs" })).toBeInTheDocument();
    expect(screen.getByLabelText("Choose PDF")).toHaveAttribute("accept", "application/pdf,.pdf");
    expect(screen.getByRole("heading", { name: "No documents yet" })).toBeInTheDocument();
  });

  it("renders document status and touch-friendly actions", () => {
    render(
      <DocumentLibrary
        documents={[document({ status: "failed", failure_reason: "No extractable text." })]}
        maxDocuments={10}
        maxSizeMb={10}
      />,
    );

    expect(screen.getByText("research.pdf")).toBeInTheDocument();
    expect(screen.getByText("No extractable text.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /download/i })).toHaveAttribute(
      "href",
      "/libraries/50000000-0000-4000-8000-000000000001/download",
    );
    expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /delete/i })).toBeInTheDocument();
  });

  it("renders ask-about-document workflow for ready documents", () => {
    render(<DocumentLibrary documents={[document()]} maxDocuments={10} maxSizeMb={10} />);

    expect(screen.getByRole("button", { name: /ask about this document/i })).toBeInTheDocument();
    expect(screen.getByRole("checkbox")).toBeInTheDocument();
  });

  it("does not render client-visible owner identifiers", () => {
    render(
      <DocumentLibrary
        documents={[document({ id: "50000000-0000-4000-8000-000000000099" })]}
        maxDocuments={10}
        maxSizeMb={10}
      />,
    );

    expect(screen.queryByText(/user_id/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/owner/i)).not.toBeInTheDocument();
  });

  it("confirms before deleting", () => {
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(false);
    render(<DocumentLibrary documents={[document()]} maxDocuments={10} maxSizeMb={10} />);

    fireEvent.click(screen.getByRole("button", { name: /delete/i }));

    expect(confirm).toHaveBeenCalledWith("Delete this document and its extracted chunks?");
  });

  it("disables upload and retry actions while offline", async () => {
    Object.defineProperty(navigator, "onLine", { configurable: true, value: false });
    render(
      <DocumentLibrary
        documents={[document({ status: "failed", failure_reason: "Interrupted upload." })]}
        maxDocuments={10}
        maxSizeMb={10}
      />,
    );
    window.dispatchEvent(new Event("offline"));

    expect(await screen.findByRole("button", { name: /upload/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /retry/i })).toBeDisabled();
    expect(screen.getByLabelText("Choose PDF")).toBeDisabled();
  });
});
