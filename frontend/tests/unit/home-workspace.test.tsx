import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PROMPT_STORAGE_KEY } from "@/components/public/public-landing";
import { quickStartConversationAction } from "@/features/conversations/actions";
import { HomeWorkspace } from "@/features/home/home-workspace";
import type { DashboardData, DocumentMetadata } from "@/lib/api/types";

vi.mock("@/features/conversations/actions", () => ({
  createConversationAction: vi.fn(),
  quickStartConversationAction: vi.fn(() => new Promise(() => undefined)),
}));
vi.mock("@/features/memories/actions", () => ({
  approveMemoryAction: vi.fn(),
  rejectMemoryAction: vi.fn(),
}));

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

const dashboard: DashboardData = {
  counts: {
    active_documents: 1,
    active_conversations: 1,
    approved_memories: 1,
    pending_suggestions: 1,
  },
  usage: {
    daily: { used: 2, limit: 20, remaining: 18 },
    monthly: { used: 14, limit: 200, remaining: 186 },
  },
  recent_conversations: [
    {
      id: "60000000-0000-4000-8000-000000000001",
      title: "Lease review",
      updated_at: "2026-07-01T12:00:00Z",
      archived_at: null,
    },
  ],
  recent_documents: [
    {
      id: "50000000-0000-4000-8000-000000000001",
      original_filename: "lease.pdf",
      status: "ready",
      created_at: "2026-07-01T12:00:00Z",
      updated_at: "2026-07-01T12:00:00Z",
    },
  ],
  recent_memories: [
    {
      id: "70000000-0000-4000-8000-000000000001",
      memory_type: "preference",
      content: "Keep lease answers concise.",
      status: "approved",
      source_conversation_id: null,
      source_conversation_title: null,
      updated_at: "2026-07-01T12:00:00Z",
    },
  ],
  pending_suggestions: [
    {
      id: "70000000-0000-4000-8000-000000000002",
      memory_type: "preference",
      content: "Remember the lease renewal schedule.",
      status: "suggested",
      source_conversation_id: "60000000-0000-4000-8000-000000000001",
      source_conversation_title: "Lease review",
      updated_at: "2026-07-01T12:00:00Z",
    },
  ],
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
        dashboard={dashboard}
        documents={[document]}
        greeting="Workspace ready"
      />,
    );

    expect(await screen.findByDisplayValue("Restored public prompt")).toBeInTheDocument();
    expect(screen.getByLabelText("lease.pdf")).toHaveAttribute("name", "document_ids");
    expect(screen.getAllByText("Lease review").length).toBeGreaterThan(0);
    expect(screen.getByText("Daily usage remaining")).toBeInTheDocument();
    expect(screen.getByText("18 left of 20")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /upload pdf/i })).toHaveAttribute("href", "/libraries");
    expect(screen.getByText("Remember the lease renewal schedule.")).toBeInTheDocument();
  });

  it("shows the thinking assistant state during quick-start submission", async () => {
    render(
      <HomeWorkspace
        dashboard={dashboard}
        documents={[document]}
        greeting="Workspace ready"
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
        dashboard={dashboard}
        documents={[document]}
        greeting="Workspace ready"
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

  it("allows quick-start without PDFs and guards duplicate starts", async () => {
    render(
      <HomeWorkspace
        dashboard={{
          ...dashboard,
          counts: {
            active_documents: 0,
            active_conversations: 0,
            approved_memories: 0,
            pending_suggestions: 0,
          },
          recent_conversations: [],
          recent_documents: [],
          recent_memories: [],
          pending_suggestions: [],
        }}
        documents={[]}
        greeting="Workspace ready"
      />,
    );

    expect(screen.getByText("Start here")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Ask your knowledge"), {
      target: { value: "Remember that I prefer concise deployment notes." },
    });
    const button = screen.getByRole("button", { name: /ask/i });
    expect(button).toBeEnabled();
    fireEvent.click(button);
    fireEvent.click(button);

    await waitFor(() => expect(quickStartConversationAction).toHaveBeenCalledTimes(1));
    const formData = vi.mocked(quickStartConversationAction).mock.calls[0]?.[1] as FormData;
    expect(formData.getAll("document_ids")).toEqual([]);
  });
});
