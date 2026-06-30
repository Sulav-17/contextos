import Link from "next/link";

export const metadata = { title: "Authentication error" };

export default function AuthErrorPage() {
  return (
    <main className="grid min-h-dvh place-items-center px-4 py-10">
      <section className="quiet-panel w-full max-w-md rounded-3xl p-6 md:p-8">
        <h1 className="text-3xl font-semibold">This authentication link could not be used</h1>
        <p role="alert" className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
          The link may be expired, already used, or not allowed for this site. Request a new link
          or contact your ContextOS administrator.
        </p>
        <Link className="mt-6 inline-block text-sm text-[var(--accent-intelligence)]" href="/login">
          Return to login
        </Link>
      </section>
    </main>
  );
}
