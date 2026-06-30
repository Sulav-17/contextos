import Link from "next/link";

export const metadata = { title: "Account access" };

export default function InviteAcceptPage() {
  return (
    <>
      <h1 className="mt-6 text-3xl font-semibold">Access ContextOS</h1>
      <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
        Create an account from the login page, or open a valid account email link on this device.
        ContextOS validates account links through Supabase before continuing.
      </p>
      <Link className="mt-6 inline-block text-sm text-[var(--accent-intelligence)]" href="/login">
        Go to login
      </Link>
    </>
  );
}
