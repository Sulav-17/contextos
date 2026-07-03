import { render } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import HomePage from "@/app/(workspace)/home/page";

const { workspaceSpy, getDashboard, getDocuments, getMe, getPreferences } = vi.hoisted(() => ({
  workspaceSpy: vi.fn(),
  getDashboard: vi.fn(),
  getDocuments: vi.fn(),
  getMe: vi.fn(),
  getPreferences: vi.fn(),
}));

vi.mock("server-only", () => ({}));

vi.mock("@/features/home/home-workspace", () => ({
  HomeWorkspace: (props: Record<string, unknown>) => {
    workspaceSpy(props);
    return <div data-testid="home-workspace" />;
  },
}));

vi.mock("@/lib/api/dashboard", () => ({
  getDashboard,
}));

vi.mock("@/lib/api/documents", () => ({
  getDocuments,
}));

vi.mock("@/lib/api/me", () => ({
  getMe,
  getPreferences,
}));

const dashboard = {
  counts: {
    active_documents: 1,
    active_conversations: 0,
    approved_memories: 0,
    pending_suggestions: 0,
  },
  usage: {
    daily: { used: 0, limit: 30, remaining: 30 },
    monthly: { used: 0, limit: 200, remaining: 200 },
  },
  recent_conversations: [],
  recent_documents: [
    {
      id: "50000000-0000-4000-8000-000000000001",
      original_filename: "lease.pdf",
      status: "ready",
      created_at: "2026-07-01T12:00:00Z",
      updated_at: "2026-07-01T12:00:00Z",
    },
  ],
  recent_memories: [],
  pending_suggestions: [],
};

describe("HomePage", () => {
  beforeEach(() => {
    workspaceSpy.mockClear();
    getDashboard.mockReset();
    getDocuments.mockReset();
    getMe.mockReset();
    getPreferences.mockReset();
    getDashboard.mockResolvedValue(dashboard);
    getMe.mockResolvedValue({
      email: "user@example.test",
      id: "30000000-0000-4000-8000-000000000001",
      display_name: "Ada",
      role: "user",
      status: "active",
      memory_enabled: true,
    });
    getPreferences.mockResolvedValue({
      greeting_mode: "minimized",
      motion_mode: "system",
      theme_mode: "dark",
      welcome_completed: true,
      user_id: "30000000-0000-4000-8000-000000000001",
    });
  });

  it("uses aggregated dashboard documents without fetching the full document list", async () => {
    const element = await HomePage();
    render(element);

    expect(getDashboard).toHaveBeenCalledTimes(1);
    expect(getDocuments).not.toHaveBeenCalled();
    expect(workspaceSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        documents: dashboard.recent_documents,
        greeting: "Good to see you, Ada",
      }),
    );
  });
});
