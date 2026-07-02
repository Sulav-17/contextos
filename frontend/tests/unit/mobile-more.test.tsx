import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MobileMore } from "@/components/navigation/mobile-more";

vi.mock("@/components/theme/theme-control", () => ({
  ThemeControl: () => <div>Theme controls</div>,
}));
vi.mock("@/lib/auth/actions", () => ({
  logoutAction: vi.fn(),
}));
vi.mock("@/lib/pwa/install", () => ({
  useInstallPrompt: () => ({
    promptInstall: vi.fn(),
    state: "available",
  }),
}));

describe("MobileMore", () => {
  it("opens a mobile menu with secondary navigation and actions", () => {
    render(<MobileMore isAdmin={false} />);

    fireEvent.click(screen.getByRole("button", { name: "Open more menu" }));

    expect(screen.getByRole("dialog", { name: "More navigation" })).toHaveClass(
      "fixed",
      "bottom-[calc(env(safe-area-inset-bottom)+0.75rem)]",
      "max-h-[calc(100dvh-1.5rem)]",
      "overflow-y-auto",
      "z-50",
    );
    expect(screen.getByTestId("mobile-more-overlay")).toHaveClass("z-40");
    expect(screen.queryByRole("link", { name: "Projects" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Uploads" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Settings" })).toBeInTheDocument();
    expect(screen.getByText("Theme controls")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /install app/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /log out/i })).toBeInTheDocument();
  });

  it("places logout inside More and closes on outside click", () => {
    render(<MobileMore isAdmin={false} />);

    expect(screen.queryByRole("button", { name: /log out/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open more menu" }));
    expect(screen.getByRole("button", { name: /log out/i })).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("mobile-more-overlay"));

    expect(screen.queryByRole("dialog", { name: "More navigation" })).not.toBeInTheDocument();
  });

  it("closes on Escape", () => {
    render(<MobileMore isAdmin={false} />);

    fireEvent.click(screen.getByRole("button", { name: "Open more menu" }));
    expect(screen.getByRole("dialog", { name: "More navigation" })).toBeInTheDocument();

    fireEvent.keyDown(document, { key: "Escape" });

    expect(screen.queryByRole("dialog", { name: "More navigation" })).not.toBeInTheDocument();
  });
});
