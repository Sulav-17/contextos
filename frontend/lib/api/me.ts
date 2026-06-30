import "server-only";

import { apiFetch } from "@/lib/api/client";
import type { GreetingMode, Me, MotionMode, Preferences, ThemeMode } from "@/lib/api/types";

export function getMe(): Promise<Me> {
  return apiFetch<Me>("/api/v1/me");
}

export function getPreferences(): Promise<Preferences> {
  return apiFetch<Preferences>("/api/v1/me/preferences");
}

export function savePreferences(payload: {
  greeting_mode?: GreetingMode;
  motion_mode?: MotionMode;
  theme_mode?: ThemeMode;
  welcome_completed?: boolean;
}): Promise<Preferences> {
  return apiFetch<Preferences>("/api/v1/me/preferences", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
