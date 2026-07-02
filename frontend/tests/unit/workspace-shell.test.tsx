import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { WorkspaceShell } from "@/components/shell/workspace-shell";

vi.mock("@/components/assistant/assistant-orb", () => ({
  AssistantOrb: () => <div>Assistant orb</div>,
}));
vi.mock("@/components/navigation/workspace-nav", () => ({
  WorkspaceNav: () => <nav>Workspace nav</nav>,
}));
vi.mock("@/components/theme/theme-control", () => ({
  ThemeControl: () => <div>Theme control</div>,
}));
vi.mock("@/components/auth/logout-control", () => ({
  LogoutControl: () => <button type="button">Log out</button>,
}));
vi.mock("@/components/pwa/install-control", () => ({
  InstallControl: () => <button type="button">Install</button>,
}));
vi.mock("@/components/pwa/offline-status", () => ({
  OfflineStatus: () => <div>Offline status</div>,
}));

describe("WorkspaceShell", () => {
  it("keeps authenticated routes viewport constrained", () => {
    const { container, getByText } = render(
      <WorkspaceShell
        preferences={{
          greeting_mode: "full",
          motion_mode: "system",
          theme_mode: "dark",
          welcome_completed: true,
          user_id: "30000000-0000-4000-8000-000000000001",
        }}
        user={{
          email: "user@example.test",
          id: "30000000-0000-4000-8000-000000000001",
          display_name: null,
          role: "user",
          status: "active",
          memory_enabled: true,
        }}
      >
        <div>Workspace content</div>
      </WorkspaceShell>,
    );

    expect(container.querySelector('[data-app-shell="workspace"]')).toBeTruthy();
    expect(container.querySelector(".flex.h-dvh.overflow-hidden")).toBeTruthy();
    expect(container.querySelector("main")).toHaveClass("overflow-y-auto");
    expect(container.querySelectorAll("header .hidden.md\\:inline-flex")).toHaveLength(3);
    expect(getByText("Theme control").parentElement).toHaveClass("hidden", "md:inline-flex");
    expect(getByText("Log out").parentElement).toHaveClass("hidden", "md:inline-flex");
    expect(getByText("Workspace content")).toBeInTheDocument();
  });
});
