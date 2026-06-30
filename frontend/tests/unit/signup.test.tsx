import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { SignupForm } from "@/components/auth/signup-form";
import { signupAction, type FormState } from "@/lib/auth/actions";

const signUp = vi.fn();

vi.mock("server-only", () => ({}));

vi.mock("@/lib/supabase/server", () => ({
  createSupabaseServerClient: vi.fn(async () => ({
    auth: { signUp },
  })),
}));

vi.mock("next/navigation", () => ({
  redirect: vi.fn(),
}));

describe("signup", () => {
  beforeEach(() => {
    signUp.mockReset();
  });

  it("submits email/password signup to Supabase", async () => {
    signUp.mockResolvedValue({ data: { session: null }, error: null });
    const formData = new FormData();
    formData.set("email", "New.User@Example.TEST");
    formData.set("password", "safe-password");
    formData.set("next", "/settings");

    const result = await signupAction({ status: "idle", message: "" }, formData);

    expect(signUp).toHaveBeenCalledWith({
      email: "New.User@Example.TEST",
      password: "safe-password",
      options: {
        emailRedirectTo: "http://localhost:3000/auth/confirm?next=/settings",
      },
    });
    expect(result).toEqual({
      status: "success",
      message: "Account created. Check your email if this project requires confirmation.",
    });
  });

  it("returns a safe signup error without provider detail", async () => {
    signUp.mockResolvedValue({
      data: { session: null },
      error: { message: "provider internal detail" },
    });
    const formData = new FormData();
    formData.set("email", "new@example.test");
    formData.set("password", "safe-password");

    const result = await signupAction({ status: "idle", message: "" }, formData);

    expect(result).toEqual({
      status: "error",
      message: "The account could not be created.",
    });
  });

  it("displays safe signup errors", async () => {
    const actionHandler = async (): Promise<FormState> => ({
      status: "error",
      message: "The account could not be created.",
    });
    render(<SignupForm actionHandler={actionHandler} />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "new@example.test" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "safe-password" },
    });
    fireEvent.submit(screen.getByRole("button", { name: "Create account" }).closest("form")!);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("The account could not be created.");
    });
  });
});
