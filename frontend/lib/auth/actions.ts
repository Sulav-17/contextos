"use server";

import { redirect } from "next/navigation";

import { createSupabaseServerClient } from "@/lib/supabase/server";
import { safeRedirectPath } from "@/lib/auth/redirects";
import { serverEnv } from "@/lib/env/server";

export type FormState = {
  status: "idle" | "success" | "error";
  message: string;
};

export async function loginAction(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  const next = safeRedirectPath(String(formData.get("next") ?? "/home"));
  if (!email || !password) {
    return { status: "error", message: "Enter your email and password." };
  }
  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) {
    return { status: "error", message: "The email or password is not valid." };
  }
  redirect(next);
}

export async function signupAction(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  const next = safeRedirectPath(String(formData.get("next") ?? "/home"));
  if (!email || !password) {
    return { status: "error", message: "Enter your email and password." };
  }
  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: `${serverEnv.NEXT_PUBLIC_SITE_URL}/auth/confirm?next=${next}`,
    },
  });
  if (error) {
    return { status: "error", message: "The account could not be created." };
  }
  if (data.session) {
    redirect(next);
  }
  return {
    status: "success",
    message: "Account created. Check your email if this project requires confirmation.",
  };
}

export async function logoutAction(): Promise<void> {
  const supabase = await createSupabaseServerClient();
  await supabase.auth.signOut();
  redirect("/login");
}

export async function forgotPasswordAction(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email) {
    return { status: "error", message: "Enter your email address." };
  }
  const supabase = await createSupabaseServerClient();
  await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${serverEnv.NEXT_PUBLIC_SITE_URL}/auth/confirm?next=/update-password`,
  });
  return {
    status: "success",
    message: "If that account can reset a password, instructions have been sent.",
  };
}

export async function updatePasswordAction(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const password = String(formData.get("password") ?? "");
  if (password.length < 8) {
    return { status: "error", message: "Enter the new password configured for this project." };
  }
  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.auth.updateUser({ password });
  if (error) {
    return { status: "error", message: "The password could not be updated for this session." };
  }
  return { status: "success", message: "Password updated. Continue to your workspace." };
}
