import { ConversationWorkspace } from "@/features/conversations/conversation-workspace";
import { getConversation, getConversations, getUsage } from "@/lib/api/conversations";
import { getDocuments } from "@/lib/api/documents";

export const metadata = { title: "Conversations" };

export default async function ConversationsPage({
  searchParams,
}: {
  searchParams: Promise<{ conversation?: string }>;
}) {
  const [{ conversations }, { documents }, usage, params] = await Promise.all([
    getConversations(),
    getDocuments(),
    getUsage(),
    searchParams,
  ]);
  const activeId = params.conversation ?? conversations[0]?.id;
  const activeConversation = activeId ? await getConversation(activeId) : null;

  return (
    <>
      <h1 className="text-3xl font-semibold">Conversations</h1>
      <div className="mt-6">
        <ConversationWorkspace
          activeConversation={activeConversation}
          conversations={conversations}
          documents={documents}
          usage={usage}
        />
      </div>
    </>
  );
}
