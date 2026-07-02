import { ConversationWorkspace } from "@/features/conversations/conversation-workspace";
import { ApiClientError } from "@/lib/api/client";
import { getConversation, getConversations, getUsage } from "@/lib/api/conversations";
import { getDocuments } from "@/lib/api/documents";

export const metadata = { title: "Conversations" };

export default async function ConversationsPage({
  searchParams,
}: {
  searchParams: Promise<{ conversation?: string }>;
}) {
  const [{ conversations }, archivedConversations, { documents }, usage, params] = await Promise.all([
    getConversations(),
    getConversations(true),
    getDocuments(),
    getUsage(),
    searchParams,
  ]);
  const activeId = params.conversation ?? conversations[0]?.id;
  let activeConversation = null;
  if (activeId) {
    try {
      activeConversation = await getConversation(activeId);
    } catch (error) {
      if (!(error instanceof ApiClientError) || error.code !== "conversation_not_found") {
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
