import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PROMPT_STORAGE_KEY } from "@/components/public/public-landing";
import { quickStartConversationAction } from "@/features/conversations/actions";
import { HomeWorkspace } from "@/features/home/home-workspace";
import type { ConversationSummary, DocumentMetadata, UsageStatus } from "@/lib/api/types";

vi.mock("@/features/conversations/actions", () => ({
  quickStartConversationAction: vi.fn(() => new Promise(() => undefined)),
}));

const conversation: ConversationSummary = {
  id: "60000000-0000-4000-8000-000000000001",
  title: "Lease review",
  created_at: "2026-07-01T12:00:00Z",
  updated_at: "2026-07-01T12:00:00Z",
};

const document: DocumentMetadata = {
  id: "50000000-0000-4000-8000-000000000001",
  original_filename: "lease.pdf",
  mime_type: "application/pdf",
  size_bytes: 2048,
  checksum_sha256: null,
  status: "ready",
  page_count: 3,
  extracted_character_count: 700,
  failure_code: null,
  failure_reason: null,
  created_at: "2026-07-01T12:00:00Z",
  updated_at: "2026-07-01T12:00:00Z",
  processed_at: "2026-07-01T12:01:00Z",
};

const usage: UsageStatus = {
  daily: { used: 2, limit: 20, remaining: 18 },
  monthly: { used: 14, limit: 200, remaining: 186 },
};

describe("HomeWorkspace", () => {
  beforeEach(() => {
    vi.mocked(quickStartConversationAction).mockClear();
    vi.mocked(quickStartConversationAction).mockImplementation(() => new Promise(() => undefined));
    window.sessionStorage.clear();
  });

  it("renders quick-start inputs, recent data, usage, upload shortcut, and restored prompt", async () => {
    window.sessionStorage.setItem(PROMPT_STORAGE_KEY, "Restored public prompt");

    render(
      <HomeWorkspace
        conversations={[conversation]}
        documents={[document]}
        greeting="Workspace ready"
        usage={usage}
      />,
    );

    expect(await screen.findByDisplayValue("Restored public prompt")).toBeInTheDocument();
    expect(screen.getByLabelText("lease.pdf")).toHaveAttribute("name", "document_ids");
    expect(screen.getByText("Lease review")).toBeInTheDocument();
    expect(screen.getByText("lease.pdf - ready")).toBeInTheDocument();
    expect(screen.getByText("Today: 2/20 used, 18 left")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /upload/i })).toHaveAttribute("href", "/libraries");
  });

  it("shows the thinking assistant state during quick-start submission", async () => {
    render(
      <HomeWorkspace
        conversations={[conversation]}
        documents={[document]}
        greeting="Workspace ready"
        usage={usage}
      />,
    );

    fireEvent.change(screen.getByLabelText("Ask your knowledge"), {
      target: { value: "What does the lease say?" },
    });

    fireEvent.click(screen.getByRole("button", { name: /ask/i }));

    expect(await screen.findByText("Assistant status: retrieving document")).toBeInTheDocument();
    expect(globalThis.document.querySelector(".assistant-orb")).toHaveAttribute(
      "data-state",
      "thinking",
    );
  });

  it("sends selected document ids in the quick-start request payload", async () => {
    vi.mocked(quickStartConversationAction).mockResolvedValueOnce({
      status: "error",
      message: "Conversation could not start.",
    });
    render(
      <HomeWorkspace
        conversations={[conversation]}
        documents={[document]}
        greeting="Workspace ready"
        usage={usage}
      />,
    );

    fireEvent.click(screen.getByLabelText("lease.pdf"));
    fireEvent.change(screen.getByLabelText("Ask your knowledge"), {
      target: { value: "What is this document about?" },
    });
    fireEvent.click(screen.getByRole("button", { name: /ask/i }));

    await waitFor(() => expect(quickStartConversationAction).toHaveBeenCalled());
    const formData = vi.mocked(quickStartConversationAction).mock.calls[0]?.[1] as FormData;
    expect(formData.get("question")).toBe("What is this document about?");
    expect(formData.getAll("document_ids")).toEqual(["50000000-0000-4000-8000-000000000001"]);
    expect(screen.getByLabelText("lease.pdf")).toBeChecked();
    expect(screen.getByLabelText("Ask your knowledge")).toHaveValue("What is this document about?");
  });
});
