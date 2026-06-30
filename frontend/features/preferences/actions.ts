"use server";

import { revalidatePath } from "next/cache";

import { savePreferences } from "@/lib/api/me";
import type { GreetingMode, MotionMode, ThemeMode } from "@/lib/api/types";

export type PreferencesFormState = {
  status: "idle" | "success" | "error";
  message: string;
};

export async function savePreferencesAction(
  _state: PreferencesFormState,
  formData: FormData,
): Promise<PreferencesFormState> {
  try {
    await savePreferences({
      greeting_mode: String(formData.get("greeting_mode")) as GreetingMode,
      motion_mode: String(formData.get("motion_mode")) as MotionMode,
      theme_mode: String(formData.get("theme_mode")) as ThemeMode,
      welcome_completed: formData.get("welcome_completed") === "on",
    });
    revalidatePath("/settings");
    revalidatePath("/home");
    return { status: "success", message: "Preferences saved." };
  } catch {
    return { status: "error", message: "Preferences could not be saved." };
  }
}
