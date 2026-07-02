import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MobileMore } from "@/components/navigation/mobile-more";

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
  it("keeps install and logout actions accessible behind the mobile menu", () => {
    render(<MobileMore isAdmin={false} />);

    fireEvent.click(screen.getByRole("button", { name: /more/i }));

    expect(screen.getByRole("button", { name: /install app/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /log out/i })).toBeInTheDocument();
    expect(screen.getByText("More navigation")).toBeInTheDocument();
  });
});
