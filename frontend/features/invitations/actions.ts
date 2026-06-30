"use server";

import { revalidatePath } from "next/cache";

import { ApiClientError } from "@/lib/api/client";
import { createInvitation } from "@/lib/api/invitations";

export type InvitationFormState = {
  status: "idle" | "success" | "error";
  message: string;
};

export async function createInvitationAction(
  _state: InvitationFormState,
  formData: FormData,
): Promise<InvitationFormState> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email) {
    return { status: "error", message: "Enter an email address." };
  }
  try {
    await createInvitation(email);
    revalidatePath("/admin/invitations");
    return { status: "success", message: "Invitation sent." };
  } catch (error) {
    if (error instanceof ApiClientError) {
      if (error.code === "invitation_duplicate") {
        return { status: "error", message: "That user already has access or an active invitation." };
      }
      if (error.code === "beta_capacity_reached") {
        return { status: "error", message: "The beta capacity has been reached." };
      }
      if (error.code === "provider_unavailable") {
        return { status: "error", message: "The invitation provider is unavailable." };
      }
    }
    return { status: "error", message: "Invitation could not be sent." };
  }
}
