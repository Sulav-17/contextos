import Link from "next/link";

import { SignupForm } from "@/components/auth/signup-form";
import { safeRedirectPath } from "@/lib/auth/redirects";

export const metadata = { title: "Sign up" };

export default async function SignupPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const params = await searchParams;
  const next = safeRedirectPath(params.next, "/home");
  return (
    <>
      <h1 className="mt-6 text-3xl font-semibold">Create your ContextOS account</h1>
      <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
        Join the private workspace to upload PDFs, ask grounded questions, and inspect citations.
      </p>
      <div className="mt-6">
        <SignupForm next={next} />
      </div>
      <Link
        className="mt-5 inline-block text-sm text-[var(--accent-intelligence)]"
        href={`/login?next=${encodeURIComponent(next)}`}
      >
        Already have an account?
      </Link>
    </>
  );
}

