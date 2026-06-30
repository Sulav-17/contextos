import type { ReactNode } from "react";
import { redirect } from "next/navigation";

import { WorkspaceShell } from "@/components/shell/workspace-shell";
import { ApiClientError } from "@/lib/api/client";
import { getMe, getPreferences } from "@/lib/api/me";
import type { Me, Preferences } from "@/lib/api/types";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export default async function ProtectedLayout({ children }: { children: ReactNode }) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) {
    redirect("/login");
  }
  let user: Me;
  let preferences: Preferences;
  try {
    [user, preferences] = await Promise.all([getMe(), getPreferences()]);
  } catch (error) {
    if (error instanceof ApiClientError && error.status === 401) {
      redirect("/login");
    }
    throw error;
  }

  return (
    <WorkspaceShell user={user} preferences={preferences}>
      {children}
    </WorkspaceShell>
  );
}
