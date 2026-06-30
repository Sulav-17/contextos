import "server-only";

import { apiFetch } from "@/lib/api/client";
import type { Invitation, InvitationList } from "@/lib/api/types";

export function getInvitations(): Promise<InvitationList> {
  return apiFetch<InvitationList>("/api/v1/admin/invitations");
}

export function createInvitation(email: string): Promise<Invitation> {
  return apiFetch<Invitation>("/api/v1/admin/invitations", {
    method: "POST",
    body: JSON.stringify({ email, role: "user" }),
  });
}
