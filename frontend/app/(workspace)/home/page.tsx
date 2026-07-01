import { HomeWorkspace } from "@/features/home/home-workspace";
import { getConversations, getUsage } from "@/lib/api/conversations";
import { getDocuments } from "@/lib/api/documents";
import { getMe, getPreferences } from "@/lib/api/me";

export const metadata = { title: "Home" };

export default async function HomePage() {
  const [user, preferences, conversationList, documentList, usage] = await Promise.all([
    getMe(),
    getPreferences(),
    getConversations(),
    getDocuments(),
    getUsage(),
  ]);
  const greeting =
    preferences.greeting_mode === "full"
      ? "Welcome to your private knowledge space"
      : preferences.greeting_mode === "direct"
        ? "Workspace ready"
        : `Good to see you${user.display_name ? `, ${user.display_name}` : ""}`;

  return (
    <HomeWorkspace
      conversations={conversationList.conversations}
      documents={documentList.documents}
      greeting={greeting}
      usage={usage}
    />
  );
}
