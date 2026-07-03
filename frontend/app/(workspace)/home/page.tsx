import { HomeWorkspace } from "@/features/home/home-workspace";
import { getDashboard } from "@/lib/api/dashboard";
import { getMe, getPreferences } from "@/lib/api/me";

export const metadata = { title: "Home" };

export default async function HomePage() {
  const [user, preferences, dashboard] = await Promise.all([
    getMe(),
    getPreferences(),
    getDashboard(),
  ]);
  const greeting =
    preferences.greeting_mode === "full"
      ? "Welcome to your private knowledge space"
      : preferences.greeting_mode === "direct"
        ? "Workspace ready"
        : `Good to see you${user.display_name ? `, ${user.display_name}` : ""}`;

  return (
    <HomeWorkspace
      dashboard={dashboard}
      documents={dashboard.recent_documents}
      greeting={greeting}
    />
  );
}
