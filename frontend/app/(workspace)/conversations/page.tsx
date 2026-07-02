import { redirect } from "next/navigation";

import { ConversationWorkspace } from "@/features/conversations/conversation-workspace";
import { ApiClientError } from "@/lib/api/client";
import { getConversation, getConversations, getUsage } from "@/lib/api/conversations";
import { getDocuments } from "@/lib/api/documents";
import type {
  ConversationDetail,
  ConversationSummary,
  DocumentMetadata,
  UsageStatus,
} from "@/lib/api/types";

export const metadata = { title: "Conversations" };

export default async function ConversationsPage({
  searchParams,
}: {
  searchParams: Promise<{ conversation?: string }>;
}) {
  let conversations: ConversationSummary[];
  let archivedConversations: { conversations: ConversationSummary[] };
  let documents: DocumentMetadata[];
  let usage: UsageStatus;
  let params: { conversation?: string };
  try {
    [
      { conversations },
      archivedConversations,
      { documents },
      usage,
      params,
    ] = await Promise.all([
      getConversations(),
      getConversations(true),
      getDocuments(),
      getUsage(),
      searchParams,
    ]);
  } catch (error) {
    if (isAuthError(error)) {
      redirect("/login?next=/conversations");
    }
    throw error;
  }

  const requestedConversationId = params.conversation?.trim() || undefined;
  const candidateConversationIds = requestedConversationId
    ? [
        requestedConversationId,
        ...conversations
          .filter((conversation) => conversation.id !== requestedConversationId)
          .map((conversation) => conversation.id),
      ]
    : conversations.map((conversation) => conversation.id);
  let activeConversation: ConversationDetail | null = null;
  for (const conversationId of candidateConversationIds) {
    try {
      activeConversation = await getConversation(conversationId);
      break;
    } catch (error) {
      if (isAuthError(error)) {
        redirect("/login?next=/conversations");
      }
      if (!isMissingConversation(error)) {
        throw error;
      }
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
      <h1 className="shrink-0 text-3xl font-semibold">Conversations</h1>
      <div className="mt-6 min-h-0 flex-1">
        <ConversationWorkspace
          activeConversation={activeConversation}
          archivedConversations={archivedConversations.conversations}
          conversations={conversations}
          documents={documents}
          usage={usage}
        />
      </div>
    </div>
  );
}

function isAuthError(error: unknown): error is ApiClientError {
  return (
    error instanceof ApiClientError &&
    (error.status === 401 ||
      error.status === 403 ||
      error.code === "authentication_required" ||
      error.code === "invalid_authentication" ||
      error.code === "user_not_provisioned" ||
      error.code === "account_disabled")
  );
}

function isMissingConversation(error: unknown): boolean {
  return (
    error instanceof ApiClientError &&
    (error.code === "conversation_not_found" || error.status === 404)
  );
}
