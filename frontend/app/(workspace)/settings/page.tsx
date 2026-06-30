import { PreferencesForm } from "@/features/preferences/preferences-form";
import { getPreferences } from "@/lib/api/me";

export const metadata = { title: "Settings" };

export default async function SettingsPage() {
  const preferences = await getPreferences();
  return (
    <>
      <h1 className="text-3xl font-semibold">Settings</h1>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
        These preferences are stored through FastAPI under your authenticated application user.
      </p>
      <div className="mt-8 max-w-2xl">
        <PreferencesForm preferences={preferences} />
      </div>
    </>
  );
}
