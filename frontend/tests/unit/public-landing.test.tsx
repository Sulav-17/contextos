import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PublicLanding } from "@/components/public/public-landing";

vi.mock("@/components/theme/theme-control", () => ({
  ThemeControl: () => <div>Theme control</div>,
}));

describe("PublicLanding", () => {
  const assign = vi.fn();

  beforeEach(() => {
    window.sessionStorage.clear();
    assign.mockReset();
    Object.defineProperty(window, "location", {
      configurable: true,
      value: { assign },
    });
  });

  it("stores anonymous prompt intent locally and routes to auth", () => {
    render(<PublicLanding />);

    fireEvent.change(screen.getByLabelText(/ask a private pdf question/i), {
      target: { value: "What does my policy say?" },
    });
    fireEvent.submit(screen.getByRole("button", { name: /continue securely/i }).closest("form")!);

    expect(window.sessionStorage.getItem("contextos.pendingPrompt")).toBe(
      "What does my policy say?",
    );
    expect(assign).toHaveBeenCalledWith("/login?next=/home&intent=chat");
  });
});

