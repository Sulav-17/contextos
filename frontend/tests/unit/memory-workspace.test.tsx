import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { MemoryWorkspace } from "@/features/memories/memory-workspace";
import type { Memory } from "@/lib/api/types";

vi.mock("@/features/memories/actions", () => ({
  approveMemoryAction: vi.fn(),
  createMemoryAction: vi.fn(() => ({ status: "idle", message: "" })),
  deleteMemoryAction: vi.fn(),
  disableMemoryAction: vi.fn(),
  enableMemoryAction: vi.fn(),
  rejectMemoryAction: vi.fn(),
  updateMemoryAction: vi.fn(() => ({ status: "idle", message: "" })),
}));

function memory(overrides: Partial<Memory>): Memory {
  return {
    id: "70000000-0000-4000-8000-000000000001",
    memory_type: "preference",
    content: "renewal preference concise",
    status: "approved",
    source_kind: "manual",
    source_conversation_id: null,
    source_conversation_title: null,
    source_message_id: null,
    created_at: "2026-07-01T12:00:00Z",
    updated_at: "2026-07-01T12:00:00Z",
    disabled_at: null,
    ...overrides,
  };
}

describe("MemoryWorkspace", () => {
  beforeEach(() => {
    Object.defineProperty(navigator, "onLine", { configurable: true, value: true });
  });

  it("renders memory lifecycle areas and provenance links", () => {
    render(
      <MemoryWorkspace
        memories={[
          memory({
            id: "70000000-0000-4000-8000-000000000001",
            status: "suggested",
            source_kind: "conversation",
            source_conversation_id: "60000000-0000-4000-8000-000000000001",
            source_conversation_title: "Deployment preferences",
          }),
          memory({ id: "70000000-0000-4000-8000-000000000002" }),
          memory({
            id: "70000000-0000-4000-8000-000000000003",
            status: "disabled",
            disabled_at: "2026-07-01T12:05:00Z",
          }),
        ]}
      />,
    );

    expect(screen.getByText("User-controlled memory")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /approve/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /reject/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /disable/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /enable/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Deployment preferences/i })).toHaveAttribute(
      "href",
      "/conversations?conversation=60000000-0000-4000-8000-000000000001",
    );
  });

  it("disables memory mutations while offline", async () => {
    Object.defineProperty(navigator, "onLine", { configurable: true, value: false });
    render(
      <MemoryWorkspace
        memories={[
          memory({
            id: "70000000-0000-4000-8000-000000000001",
            status: "suggested",
          }),
        ]}
      />,
    );
    window.dispatchEvent(new Event("offline"));

    expect(await screen.findByRole("button", { name: /save/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /approve/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /reject/i })).toBeDisabled();
  });
});
