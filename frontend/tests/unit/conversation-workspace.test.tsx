import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { submitQuestionAction } from "@/features/conversations/actions";
import { ConversationWorkspace } from "@/features/conversations/conversation-workspace";
import type {
  ConversationDetail,
  ConversationSummary,
  DocumentMetadata,
  UsageStatus,
} from "@/lib/api/types";

vi.mock("@/features/conversations/actions", () => ({
  createConversationAction: vi.fn(() => ({ status: "idle", message: "" })),
  deleteConversationAction: vi.fn(() => ({ status: "idle", message: "" })),
  renameConversationAction: vi.fn(() => ({ status: "idle", message: "" })),
  submitQuestionAction: vi.fn(() => new Promise(() => undefined)),
}));

function document(overrides: Partial<DocumentMetadata> = {}): DocumentMetadata {
  return {
    id: "50000000-0000-4000-8000-000000000001",
    original_filename: "research.pdf",
    mime_type: "application/pdf",
    size_bytes: 2048,
    checksum_sha256: null,
    status: "ready",
    page_count: 2,
    extracted_character_count: 400,
    failure_code: null,
    failure_reason: null,
    created_at: "2026-07-01T12:00:00Z",
    updated_at: "2026-07-01T12:00:00Z",
    processed_at: "2026-07-01T12:01:00Z",
    ...overrides,
  };
}

const usage: UsageStatus = {
  daily: { used: 19, limit: 20, remaining: 1 },
  monthly: { used: 199, limit: 200, remaining: 1 },
};

const summary: ConversationSummary = {
  id: "60000000-0000-4000-8000-000000000001",
  title: "Research",
  created_at: "2026-07-01T12:00:00Z",
  updated_at: "2026-07-01T12:00:00Z",
};

function conversation(overrides: Partial<ConversationDetail> = {}): ConversationDetail {
  return {
    ...summary,
    selected_document_ids: [],
    messages: [
      {
        id: "61000000-0000-4000-8000-000000000001",
        role: "assistant",
        content: "Based on your documents, ContextOS stores private PDFs.",
        status: "completed",
        created_at: "2026-07-01T12:00:00Z",
        citations: [
          {
            citation_index: 1,
            document_id: "50000000-0000-4000-8000-000000000001",
            document_name: "research.pdf",
            page_number: 2,
            excerpt: "ContextOS stores private PDFs.",
          },
        ],
      },
    ],
    ...overrides,
  };
}

describe("ConversationWorkspace", () => {
  beforeEach(() => {
    vi.mocked(submitQuestionAction).mockClear();
    vi.mocked(submitQuestionAction).mockImplementation(() => new Promise(() => undefined));
    window.sessionStorage.clear();
  });

  it("renders conversation controls, usage, selected-document inputs, and citations", () => {
    render(
      <ConversationWorkspace
        activeConversation={conversation()}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    expect(screen.getByRole("button", { name: /new conversation/i })).toHaveClass("touch-target");
    expect(screen.getByText("Today: 19/20")).toBeInTheDocument();
    expect(screen.getByLabelText("research.pdf")).toHaveAttribute("name", "document_ids");
    expect(screen.getByText("[1] research.pdf, page 2")).toBeInTheDocument();
    expect(screen.getByText("ContextOS stores private PDFs.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /rename conversation/i })).toBeInTheDocument();
  });

  it("renders weak-evidence and limit state text safely", () => {
    render(
      <ConversationWorkspace
        activeConversation={conversation({
          messages: [
            {
              id: "61000000-0000-4000-8000-000000000002",
              role: "assistant",
              content: "I could not find enough evidence in your documents to answer that.",
              status: "completed",
              created_at: "2026-07-01T12:00:00Z",
              citations: [],
            },
          ],
        })}
        conversations={[summary]}
        documents={[]}
        usage={{
          daily: { used: 20, limit: 20, remaining: 0 },
          monthly: { used: 200, limit: 200, remaining: 0 },
        }}
      />,
    );

    expect(screen.getByText("Today: 20/20")).toBeInTheDocument();
    expect(screen.getByText("Month: 200/200")).toBeInTheDocument();
    expect(screen.getByText(/could not find enough evidence/i)).toBeInTheDocument();
    expect(screen.getByText("No retrieval-ready PDFs.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  it("shows the thinking assistant state during question submission", async () => {
    render(
      <ConversationWorkspace
        activeConversation={conversation()}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "What evidence supports this?" },
    });

    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText("Assistant status: retrieving document")).toBeInTheDocument();
    expect(globalThis.document.querySelector(".assistant-orb")).toHaveAttribute(
      "data-state",
      "thinking",
    );
  });

  it("includes selected document ids in the submit payload", async () => {
    vi.mocked(submitQuestionAction).mockResolvedValueOnce({
      status: "success",
      message: "Answer added.",
    });

    render(
      <ConversationWorkspace
        activeConversation={conversation()}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    fireEvent.click(screen.getByLabelText("research.pdf"));
    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "What is the document about?" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => expect(submitQuestionAction).toHaveBeenCalled());
    const formData = vi.mocked(submitQuestionAction).mock.calls[0]?.[1] as FormData;
    expect(formData.get("question")).toBe("What is the document about?");
    expect(formData.getAll("document_ids")).toEqual(["50000000-0000-4000-8000-000000000001"]);
  });

  it("keeps selected documents after successful submissions", async () => {
    const selected = conversation({
      selected_document_ids: ["50000000-0000-4000-8000-000000000001"],
    });
    vi.mocked(submitQuestionAction).mockResolvedValueOnce({
      status: "success",
      message: "Answer added.",
    });
    const { rerender } = render(
      <ConversationWorkspace
        activeConversation={selected}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    expect(screen.getByLabelText("research.pdf")).toBeChecked();
    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "Summarize this document." },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    rerender(
      <ConversationWorkspace
        activeConversation={conversation({
          selected_document_ids: ["50000000-0000-4000-8000-000000000001"],
          messages: [
            ...selected.messages,
            {
              id: "61000000-0000-4000-8000-000000000098",
              role: "user",
              content: "Summarize this document.",
              status: "accepted",
              created_at: "2026-07-01T12:02:00Z",
              citations: [],
            },
            {
              id: "61000000-0000-4000-8000-000000000099",
              role: "assistant",
              content: "A grounded summary.",
              status: "completed",
              created_at: "2026-07-01T12:03:00Z",
              citations: [],
            },
          ],
        })}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );
    await waitFor(() => expect(screen.getByLabelText("Question")).toHaveValue(""));
    expect(screen.getByLabelText("research.pdf")).toBeChecked();

  });

  it("keeps selected documents after failed submissions", async () => {
    const selected = conversation({
      selected_document_ids: ["50000000-0000-4000-8000-000000000001"],
    });
    vi.mocked(submitQuestionAction).mockResolvedValueOnce({
      status: "error",
      message: "Provider unavailable.",
    });
    render(
      <ConversationWorkspace
        activeConversation={selected}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "Try again later." },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => expect(submitQuestionAction).toHaveBeenCalledTimes(1));
    expect(screen.getByLabelText("Question")).toHaveValue("Try again later.");
    expect(screen.getByLabelText("research.pdf")).toBeChecked();
  });

  it("restores selected scope across conversation refresh and allows explicit deselection", async () => {
    vi.mocked(submitQuestionAction).mockResolvedValue({
      status: "success",
      message: "Answer added.",
    });
    const selected = conversation({
      selected_document_ids: ["50000000-0000-4000-8000-000000000001"],
    });
    const { rerender } = render(
      <ConversationWorkspace
        activeConversation={selected}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    expect(screen.getByLabelText("research.pdf")).toBeChecked();
    rerender(
      <ConversationWorkspace
        activeConversation={conversation({
          selected_document_ids: ["50000000-0000-4000-8000-000000000001"],
          messages: [
            ...selected.messages,
            {
              id: "61000000-0000-4000-8000-000000000099",
              role: "assistant",
              content: "A refreshed answer.",
              status: "completed",
              created_at: "2026-07-01T12:02:00Z",
              citations: [],
            },
          ],
        })}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );
    expect(screen.getByLabelText("research.pdf")).toBeChecked();

    fireEvent.click(screen.getByLabelText("research.pdf"));
    expect(screen.getByLabelText("research.pdf")).not.toBeChecked();
    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "No selected scope." },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(submitQuestionAction).toHaveBeenCalled());
    const lastCall = vi.mocked(submitQuestionAction).mock.calls.at(-1);
    const formData = lastCall?.[1] as FormData;
    expect(formData.getAll("document_ids")).toEqual([]);
  });

  it("preserves draft text during rerender and clears it only after success", async () => {
    vi.mocked(submitQuestionAction).mockResolvedValueOnce({
      status: "error",
      message: "Provider unavailable.",
    });
    const { rerender } = render(
      <ConversationWorkspace
        activeConversation={conversation()}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "Keep this draft." },
    });
    rerender(
      <ConversationWorkspace
        activeConversation={conversation()}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );
    expect(screen.getByLabelText("Question")).toHaveValue("Keep this draft.");
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(submitQuestionAction).toHaveBeenCalledTimes(1));
    expect(screen.getByLabelText("Question")).toHaveValue("Keep this draft.");

    vi.mocked(submitQuestionAction).mockResolvedValueOnce({
      status: "success",
      message: "Answer added.",
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    rerender(
      <ConversationWorkspace
        activeConversation={conversation({
          messages: [
            ...conversation().messages,
            {
              id: "61000000-0000-4000-8000-000000000088",
              role: "user",
              content: "Keep this draft.",
              status: "accepted",
              created_at: "2026-07-01T12:02:00Z",
              citations: [],
            },
          ],
        })}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );
    await waitFor(() => expect(screen.getByLabelText("Question")).toHaveValue(""));
  });
});
