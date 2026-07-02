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
  archiveConversationAction: vi.fn(() => ({ status: "idle", message: "" })),
  createConversationAction: vi.fn(() => ({ status: "idle", message: "" })),
  deleteConversationAction: vi.fn(() => ({ status: "idle", message: "" })),
  renameConversationAction: vi.fn(() => ({ status: "idle", message: "" })),
  submitQuestionAction: vi.fn(() => new Promise(() => undefined)),
  unarchiveConversationAction: vi.fn(() => ({ status: "idle", message: "" })),
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
  archived_at: null,
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
        memory_references: [],
        source_mode: "documents",
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
    Object.defineProperty(navigator, "onLine", { configurable: true, value: true });
  });

  it("renders conversation controls, usage, selected-document inputs, and citations", () => {
    render(
      <ConversationWorkspace
        activeConversation={conversation()}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    expect(screen.getByRole("button", { name: /new conversation/i })).toHaveClass("touch-target");
    expect(screen.getByText("Today: 19/20")).toBeInTheDocument();
    expect(screen.getByLabelText("research.pdf")).toHaveAttribute("name", "document_ids");
    expect(screen.getByText("Used 1 document")).toBeInTheDocument();
    expect(screen.getByText("[1] research.pdf, page 2")).toBeInTheDocument();
    expect(screen.getByText("ContextOS stores private PDFs.")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /rename conversation/i }).length).toBeGreaterThan(
      1,
    );
  });

  it("uses a mobile-safe conversation toolbar and preserves desktop controls", () => {
    const { container } = render(
      <ConversationWorkspace
        activeConversation={conversation()}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    expect(screen.getByRole("button", { name: /history/i })).toHaveClass("whitespace-nowrap");
    expect(screen.getByRole("button", { name: /^context$/i })).toHaveClass("whitespace-nowrap");
    expect(screen.getByRole("button", { name: /^new$/i })).toHaveClass("whitespace-nowrap");
    expect(screen.getByRole("button", { name: /context inspector/i })).toHaveClass(
      "xl:inline-flex",
    );
    expect(container.querySelector(".lg\\:hidden")).toBeTruthy();
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
              memory_references: [],
              source_mode: "insufficient_evidence",
              citations: [],
            },
          ],
        })}
        archivedConversations={[]}
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
    expect(screen.getByText(/Document selection is optional/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  it("enables non-empty chat with zero PDFs and shows dynamic helper text", async () => {
    vi.mocked(submitQuestionAction).mockResolvedValueOnce({
      status: "success",
      message: "Answer added.",
    });
    render(
      <ConversationWorkspace
        activeConversation={conversation({ messages: [] })}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[]}
        usage={usage}
      />,
    );

    expect(screen.getAllByText(/Ask anything, use saved memory/i).length).toBeGreaterThan(0);
    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "What is a PWA?" },
    });
    expect(screen.getByRole("button", { name: /send/i })).toBeEnabled();
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => expect(submitQuestionAction).toHaveBeenCalledTimes(1));
    const formData = vi.mocked(submitQuestionAction).mock.calls[0]?.[1] as FormData;
    expect(formData.getAll("document_ids")).toEqual([]);
  });

  it("renders memory suggestion and memory badges distinctly", () => {
    render(
      <ConversationWorkspace
        activeConversation={conversation({
          messages: [
            {
              id: "61000000-0000-4000-8000-000000000010",
              role: "assistant",
              content: "Memory suggestion created. Awaiting approval before it can influence answers.",
              status: "completed",
              created_at: "2026-07-01T12:00:00Z",
              memory_references: [],
              source_mode: "memory_suggestion_created",
              citations: [],
            },
            {
              id: "61000000-0000-4000-8000-000000000011",
              role: "assistant",
              content: "Remembered information: deployment target browser install",
              status: "completed",
              created_at: "2026-07-01T12:01:00Z",
              memory_references: [
                {
                  id: "70000000-0000-4000-8000-000000000001",
                  memory_type: "preference",
                  content: "deployment target browser install",
                  source_conversation_id: null,
                  source_conversation_title: null,
                },
              ],
              source_mode: "memory",
              citations: [],
            },
          ],
        })}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[]}
        usage={usage}
      />,
    );

    expect(screen.getByText("Memory suggestion created")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /review in memories/i })).toHaveAttribute(
      "href",
      "/memories",
    );
    expect(screen.getAllByText("Used saved memory")[0]).toBeInTheDocument();
  });

  it("renders the ContextOS data badge and inspector state", () => {
    render(
      <ConversationWorkspace
        activeConversation={conversation({
          messages: [
            {
              id: "61000000-0000-4000-8000-000000000012",
              role: "assistant",
              content: "You have 2 conversations.",
              status: "completed",
              created_at: "2026-07-01T12:02:00Z",
              memory_references: [],
              source_mode: "contextos",
              citations: [],
            },
          ],
        })}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[]}
        usage={usage}
      />,
    );

    expect(screen.getAllByText("ContextOS data")[0]).toBeInTheDocument();
    expect(screen.getByText("Authenticated workspace metadata was used.")).toBeInTheDocument();
  });

  it("shows the thinking assistant state during question submission", async () => {
    render(
      <ConversationWorkspace
        activeConversation={conversation()}
        archivedConversations={[]}
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
    expect(globalThis.document.querySelector('.assistant-orb[data-state="thinking"]')).toBeTruthy();
    expect(globalThis.document.querySelector('.assistant-orb[data-state="thinking"]')).toHaveAttribute(
      "data-state",
      "thinking",
    );
  });

  it("guards against duplicate submit clicks while pending", async () => {
    render(
      <ConversationWorkspace
        activeConversation={conversation()}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "What evidence supports this?" },
    });
    const button = screen.getByRole("button", { name: /send/i });
    fireEvent.click(button);
    fireEvent.click(button);

    await waitFor(() => expect(submitQuestionAction).toHaveBeenCalledTimes(1));
  });

  it("includes selected document ids in the submit payload", async () => {
    vi.mocked(submitQuestionAction).mockResolvedValueOnce({
      status: "success",
      message: "Answer added.",
    });

    render(
      <ConversationWorkspace
        activeConversation={conversation()}
        archivedConversations={[]}
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
        archivedConversations={[]}
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
              memory_references: [],
              source_mode: "general",
              citations: [],
            },
            {
              id: "61000000-0000-4000-8000-000000000099",
              role: "assistant",
              content: "A grounded summary.",
              status: "completed",
              created_at: "2026-07-01T12:03:00Z",
              memory_references: [],
              source_mode: "general",
              citations: [],
            },
          ],
        })}
        archivedConversations={[]}
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
        archivedConversations={[]}
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
        archivedConversations={[]}
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
              memory_references: [],
              source_mode: "general",
              citations: [],
            },
          ],
        })}
        archivedConversations={[]}
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
        archivedConversations={[]}
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
        archivedConversations={[]}
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
              memory_references: [],
              source_mode: "general",
              citations: [],
            },
          ],
        })}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );
    await waitFor(() => expect(screen.getByLabelText("Question")).toHaveValue(""));
  });

  it("disables chat send while offline and preserves composer text", async () => {
    Object.defineProperty(navigator, "onLine", { configurable: true, value: false });
    render(
      <ConversationWorkspace
        activeConversation={conversation()}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );
    window.dispatchEvent(new Event("offline"));
    await waitFor(() => expect(screen.getByLabelText("Question")).toHaveValue(""));

    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "Keep this offline draft." },
    });

    const send = await screen.findByRole("button", { name: /send/i });
    expect(send).toBeDisabled();
    expect(screen.getByLabelText("Question")).toHaveValue("Keep this offline draft.");
    expect(submitQuestionAction).not.toHaveBeenCalled();
  });

  it("scrolls to the newest message when the user is already near the bottom", async () => {
    const firstConversation = conversation({
      messages: [
        {
          id: "61000000-0000-4000-8000-000000000020",
          role: "assistant",
          content: "First answer",
          status: "completed",
          created_at: "2026-07-01T12:00:00Z",
          memory_references: [],
          source_mode: "general",
          citations: [],
        },
      ],
    });
    const { rerender } = render(
      <ConversationWorkspace
        activeConversation={firstConversation}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    const history = screen.getByTestId("conversation-history");
    Object.defineProperty(history, "scrollHeight", { configurable: true, value: 400 });
    Object.defineProperty(history, "clientHeight", { configurable: true, value: 200 });
    Object.defineProperty(history, "scrollTop", { configurable: true, writable: true, value: 160 });
    fireEvent.scroll(history);

    rerender(
      <ConversationWorkspace
        activeConversation={conversation({
          messages: [
            ...firstConversation.messages,
            {
              id: "61000000-0000-4000-8000-000000000021",
              role: "assistant",
              content: "Newest answer",
              status: "completed",
              created_at: "2026-07-01T12:01:00Z",
              memory_references: [],
              source_mode: "general",
              citations: [],
            },
          ],
        })}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    await waitFor(() => expect((history as HTMLDivElement).scrollTop).toBe(400));
  });

  it("does not force-scroll when the user has moved up in history", async () => {
    const firstConversation = conversation({
      messages: [
        {
          id: "61000000-0000-4000-8000-000000000030",
          role: "assistant",
          content: "First answer",
          status: "completed",
          created_at: "2026-07-01T12:00:00Z",
          memory_references: [],
          source_mode: "general",
          citations: [],
        },
      ],
    });
    const { rerender } = render(
      <ConversationWorkspace
        activeConversation={firstConversation}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    const history = screen.getByTestId("conversation-history");
    Object.defineProperty(history, "scrollHeight", { configurable: true, value: 400 });
    Object.defineProperty(history, "clientHeight", { configurable: true, value: 200 });
    Object.defineProperty(history, "scrollTop", { configurable: true, writable: true, value: 0 });
    fireEvent.scroll(history);

    rerender(
      <ConversationWorkspace
        activeConversation={conversation({
          messages: [
            ...firstConversation.messages,
            {
              id: "61000000-0000-4000-8000-000000000031",
              role: "assistant",
              content: "Newest answer",
              status: "completed",
              created_at: "2026-07-01T12:01:00Z",
              memory_references: [],
              source_mode: "general",
              citations: [],
            },
          ],
        })}
        archivedConversations={[]}
        conversations={[summary]}
        documents={[document()]}
        usage={usage}
      />,
    );

    await waitFor(() => expect((history as HTMLDivElement).scrollTop).toBe(0));
  });
});
