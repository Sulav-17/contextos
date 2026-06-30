import Link from "next/link";

import { LoginForm } from "@/components/auth/login-form";
import { SignupForm } from "@/components/auth/signup-form";
import { safeRedirectPath } from "@/lib/auth/redirects";

export const metadata = { title: "Log in" };

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const params = await searchParams;
  const next = safeRedirectPath(params.next, "/home");
  return (
    <>
      <h1 className="mt-6 text-3xl font-semibold">Log in to ContextOS</h1>
      <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
        Create an account or log in with email and password. ContextOS keeps each user&apos;s
        workspace private.
      </p>
      <div className="mt-6 grid gap-8">
        <section aria-labelledby="login-heading">
          <h2 id="login-heading" className="mb-4 text-lg font-semibold">
            Existing account
          </h2>
          <LoginForm next={next} />
        </section>
        <section aria-labelledby="signup-heading">
          <h2 id="signup-heading" className="mb-4 text-lg font-semibold">
            New account
          </h2>
          <SignupForm next={next} />
        </section>
      </div>
      <Link className="mt-5 inline-block text-sm text-[var(--accent-intelligence)]" href="/forgot-password">
        Forgot password?
      </Link>
    </>
  );
}
