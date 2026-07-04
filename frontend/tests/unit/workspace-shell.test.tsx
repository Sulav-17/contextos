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
  function renderShell(children = <div>Workspace content</div>) {
    return render(
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
        {children}
      </WorkspaceShell>,
    );
  }

  it("keeps authenticated routes viewport constrained", () => {
    const { container, getByText } = renderShell();

    expect(container.querySelector('[data-app-shell="workspace"]')).toBeTruthy();
    expect(container.firstElementChild).toHaveClass("h-dvh", "max-h-dvh", "overflow-hidden");
    expect(container.querySelector(".flex.h-full.min-h-0.overflow-hidden")).toBeTruthy();
    expect(container.querySelector(".grid.min-h-0.min-w-0.flex-1")).toBeTruthy();
    expect(container.querySelector("main")).toHaveClass(
      "min-h-0",
      "overflow-y-auto",
      "overscroll-contain",
    );
    expect(container.querySelectorAll("header .hidden.md\\:inline-flex")).toHaveLength(3);
    expect(getByText("Theme control").parentElement).toHaveClass("hidden", "md:inline-flex");
    expect(getByText("Log out").parentElement).toHaveClass("hidden", "md:inline-flex");
    expect(getByText("Workspace content")).toBeInTheDocument();
  });

  it("keeps document height at the viewport while main content owns long scrolling", () => {
    const { getByTestId } = renderShell(<div style={{ height: "1600px" }}>Long content</div>);
    const main = getByTestId("workspace-main-scroll");

    Object.defineProperty(document.documentElement, "clientHeight", {
      configurable: true,
      value: 800,
    });
    Object.defineProperty(document.documentElement, "scrollHeight", {
      configurable: true,
      value: 800,
    });
    Object.defineProperty(document.body, "scrollHeight", {
      configurable: true,
      value: 800,
    });
    Object.defineProperty(main, "clientHeight", {
      configurable: true,
      value: 640,
    });
    Object.defineProperty(main, "scrollHeight", {
      configurable: true,
      value: 1600,
    });

    expect(document.documentElement.scrollHeight).toBe(document.documentElement.clientHeight);
    expect(document.body.scrollHeight).toBe(document.documentElement.clientHeight);
    expect(main.scrollHeight).toBeGreaterThan(main.clientHeight);
    expect(main).toHaveClass("min-h-0", "overflow-y-auto");
  });
});
