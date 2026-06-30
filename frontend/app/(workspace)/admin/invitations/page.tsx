import { redirect } from "next/navigation";

import { InvitationForm } from "@/features/invitations/invitation-form";
import { getInvitations } from "@/lib/api/invitations";
import { getMe } from "@/lib/api/me";

export const metadata = { title: "Admin invitations" };

export default async function AdminInvitationsPage() {
  const user = await getMe();
  if (user.role !== "admin") {
    redirect("/home");
  }
  const data = await getInvitations();
  return (
    <>
      <h1 className="text-3xl font-semibold">Invitation administration</h1>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
        {data.occupied_slots} of {data.beta_max_users} beta access slots are occupied.
      </p>
      <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,26rem)_1fr]">
        <InvitationForm />
        <section className="quiet-panel rounded-3xl p-6">
          <h2 className="text-xl font-semibold">Invitation states</h2>
          {data.invitations.length === 0 ? (
            <p className="mt-3 text-sm text-[var(--text-secondary)]">No invitations have been sent.</p>
          ) : (
            <ul className="mt-4 grid gap-3">
              {data.invitations.map((invite) => (
                <li key={invite.id} className="rounded-2xl border border-[var(--border-subtle)] p-4">
                  <p className="font-medium">{invite.email}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">
                    Status: {invite.status}; role: {invite.requested_role}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </>
  );
}
