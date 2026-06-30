import { SimpleAuthForm } from "@/components/auth/simple-auth-form";
import { forgotPasswordAction } from "@/lib/auth/actions";

export const metadata = { title: "Reset password" };

export default function ForgotPasswordPage() {
  return (
    <>
      <h1 className="mt-6 text-3xl font-semibold">Reset your password</h1>
      <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
        Enter your email. If the account can reset a password, ContextOS will send instructions.
      </p>
      <div className="mt-6">
        <SimpleAuthForm
          action={forgotPasswordAction}
          buttonLabel="Send reset instructions"
          fieldLabel="Email"
          fieldName="email"
          fieldType="email"
        />
      </div>
    </>
  );
}
