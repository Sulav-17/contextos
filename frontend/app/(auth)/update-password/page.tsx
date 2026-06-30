import Link from "next/link";

import { SimpleAuthForm } from "@/components/auth/simple-auth-form";
import { updatePasswordAction } from "@/lib/auth/actions";

export const metadata = { title: "Set password" };

export default function UpdatePasswordPage() {
  return (
    <>
      <h1 className="mt-6 text-3xl font-semibold">Set your password</h1>
      <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
        This page requires a valid account or recovery session from Supabase.
      </p>
      <div className="mt-6">
        <SimpleAuthForm
          action={updatePasswordAction}
          buttonLabel="Save password"
          fieldLabel="New password"
          fieldName="password"
          fieldType="password"
        />
      </div>
      <Link className="mt-5 inline-block text-sm text-[var(--accent-intelligence)]" href="/home">
        Continue to workspace
      </Link>
    </>
  );
}
