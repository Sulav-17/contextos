import "server-only";

import { apiFetch } from "@/lib/api/client";
import type {
  ConversationDetail,
  ConversationList,
  ConversationSummary,
  MessageCreateResponse,
  UsageStatus,
} from "@/lib/api/types";

export function createConversation(title = "New conversation"): Promise<ConversationSummary> {
  return apiFetch<ConversationSummary>("/api/v1/conversations", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export function getConversations(): Promise<ConversationList> {
  return apiFetch<ConversationList>("/api/v1/conversations");
}

export function getConversation(conversationId: string): Promise<ConversationDetail> {
  return apiFetch<ConversationDetail>(`/api/v1/conversations/${conversationId}`);
}

export function submitQuestion(
  conversationId: string,
  question: string,
  documentIds: string[],
): Promise<MessageCreateResponse> {
  return apiFetch<MessageCreateResponse>(`/api/v1/conversations/${conversationId}/messages`, {
    method: "POST",
    body: JSON.stringify({ question, document_ids: documentIds }),
  });
}

export function deleteConversation(conversationId: string): Promise<void> {
  return apiFetch<void>(`/api/v1/conversations/${conversationId}`, {
    method: "DELETE",
  });
}

export function getUsage(): Promise<UsageStatus> {
  return apiFetch<UsageStatus>("/api/v1/usage");
}
