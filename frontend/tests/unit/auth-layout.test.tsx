import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import AuthLayout from "@/app/(auth)/layout";

vi.mock("@/components/assistant/assistant-orb", () => ({
  AssistantOrb: () => <div>Assistant orb</div>,
}));
vi.mock("@/components/theme/theme-control", () => ({
  ThemeControl: () => <div>Theme control</div>,
}));

describe("AuthLayout", () => {
  it("marks auth routes as public-scrolling pages", () => {
    const { container } = render(
      <AuthLayout>
        <div>Auth content</div>
      </AuthLayout>,
    );

    expect(container.querySelector('[data-app-shell="auth"]')).toBeTruthy();
    expect(screen.getByText("Auth content")).toBeInTheDocument();
  });
});
