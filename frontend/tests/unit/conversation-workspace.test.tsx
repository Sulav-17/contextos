import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ConversationWorkspace } from "@/features/conversations/conversation-workspace";
import type {
  ConversationDetail,
  ConversationSummary,
  DocumentMetadata,
  UsageStatus,
} from "@/lib/api/types";

vi.mock("@/features/conversations/actions", () => ({
  createConversationAction: vi.fn(),
  deleteConversationAction: vi.fn(),
  submitQuestionAction: vi.fn(),
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
});
