import { render } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import ConversationsPage from "@/app/(workspace)/conversations/page";
import { ApiClientError } from "@/lib/api/client";

const { workspaceSpy, redirect, getConversation, getConversations, getDocuments, getUsage } =
  vi.hoisted(() => ({
    workspaceSpy: vi.fn(),
    redirect: vi.fn((path: string) => {
      throw new Error(`REDIRECT:${path}`);
    }),
    getConversation: vi.fn(),
    getConversations: vi.fn(),
    getDocuments: vi.fn(),
    getUsage: vi.fn(),
  }));

vi.mock("server-only", () => ({}));
vi.mock("next/navigation", () => ({
  redirect,
}));

vi.mock("@/features/conversations/conversation-workspace", () => ({
  ConversationWorkspace: (props: Record<string, unknown>) => {
    workspaceSpy(props);
    return <div data-testid="conversation-workspace" />;
  },
}));

vi.mock("@/lib/api/conversations", () => ({
  getConversation,
  getConversations,
  getUsage,
}));

vi.mock("@/lib/api/documents", () => ({
  getDocuments,
}));

type ConversationSummary = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
};

type ConversationDetail = ConversationSummary & {
  messages: Array<Record<string, unknown>>;
  selected_document_ids: string[];
};

function summary(id: string, title = "Conversation"): ConversationSummary {
  return {
    id,
    title,
    created_at: "2026-07-01T12:00:00Z",
    updated_at: "2026-07-01T12:00:00Z",
    archived_at: null,
  };
}

function detail(id: string, title = "Conversation"): ConversationDetail {
  return {
    ...summary(id, title),
    messages: [],
    selected_document_ids: [],
  };
}

describe("ConversationsPage", () => {
  beforeEach(() => {
    workspaceSpy.mockClear();
    redirect.mockClear();
    getConversation.mockReset();
    getConversations.mockReset();
    getDocuments.mockReset();
    getUsage.mockReset();
    vi.mocked(getConversations).mockResolvedValue({ conversations: [] });
    vi.mocked(getDocuments).mockResolvedValue({ documents: [] });
    vi.mocked(getUsage).mockResolvedValue({
      daily: { used: 0, limit: 20, remaining: 20 },
      monthly: { used: 0, limit: 200, remaining: 200 },
    });
  });

  it("renders the empty conversations state when no conversations exist", async () => {
    vi.mocked(getConversations).mockResolvedValueOnce({ conversations: [] });
    vi.mocked(getConversations).mockResolvedValueOnce({ conversations: [] });
    vi.mocked(getConversation).mockRejectedValue(
      new ApiClientError("conversation_not_found", "Conversation not found.", 404),
    );

    const element = await ConversationsPage({
      searchParams: Promise.resolve({}),
    });

    render(element);

    expect(workspaceSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        activeConversation: null,
        conversations: [],
      }),
    );
  });

  it("keeps the empty state when the final conversation is deleted", async () => {
    vi.mocked(getConversations).mockResolvedValueOnce({ conversations: [] });
    vi.mocked(getConversations).mockResolvedValueOnce({ conversations: [] });
    vi.mocked(getConversation).mockRejectedValue(
      new ApiClientError("conversation_not_found", "Conversation not found.", 404),
    );

    const element = await ConversationsPage({
      searchParams: Promise.resolve({ conversation: "60000000-0000-4000-8000-000000000001" }),
    });

    render(element);

    expect(workspaceSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        activeConversation: null,
        conversations: [],
      }),
    );
  });

  it("selects a remaining conversation when the current one is missing", async () => {
    const remaining = detail("60000000-0000-4000-8000-000000000002", "Remaining");
    vi.mocked(getConversations).mockResolvedValueOnce({
      conversations: [summary("60000000-0000-4000-8000-000000000002", "Remaining")],
    });
    vi.mocked(getConversations).mockResolvedValueOnce({ conversations: [] });
    vi.mocked(getConversation).mockImplementation(async (conversationId: string) => {
      if (conversationId === "60000000-0000-4000-8000-000000000001") {
        throw new ApiClientError("conversation_not_found", "Conversation not found.", 404);
      }
      if (conversationId === remaining.id) {
        return remaining;
      }
      throw new ApiClientError("conversation_not_found", "Conversation not found.", 404);
    });

    const element = await ConversationsPage({
      searchParams: Promise.resolve({ conversation: "60000000-0000-4000-8000-000000000001" }),
    });

    render(element);

    expect(workspaceSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        activeConversation: expect.objectContaining({ id: remaining.id }),
      }),
    );
  });

  it("redirects to login when the conversations API reports auth failure", async () => {
    vi.mocked(getConversations).mockRejectedValue(
      new ApiClientError("authentication_required", "Authentication is required.", 401),
    );

    await expect(
      ConversationsPage({
        searchParams: Promise.resolve({}),
      }),
    ).rejects.toThrow("REDIRECT:/login?next=/conversations");

    expect(redirect).toHaveBeenCalledWith("/login?next=/conversations");
  });

  it("surfaces real backend failures instead of emptying the workspace", async () => {
    vi.mocked(getConversations).mockRejectedValue(
      new ApiClientError("backend_unavailable", "ContextOS is unavailable.", 503),
    );

    await expect(
      ConversationsPage({
        searchParams: Promise.resolve({}),
      }),
    ).rejects.toMatchObject({
      code: "backend_unavailable",
      status: 503,
    });
  });
});
