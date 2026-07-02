import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { WorkspaceNav } from "@/components/navigation/workspace-nav";

vi.mock("next/navigation", () => ({
  usePathname: () => "/libraries",
}));

vi.mock("@/components/navigation/mobile-more", () => ({
  MobileMore: () => <div>Mobile more</div>,
}));

describe("WorkspaceNav", () => {
  it("keeps Documents reachable on desktop and mobile while hiding Projects and Uploads", () => {
    const { container } = render(<WorkspaceNav isAdmin={false} />);

    const documentLinks = screen.getAllByRole("link", { name: "Documents" });
    expect(documentLinks.length).toBeGreaterThan(0);
    expect(screen.queryByRole("link", { name: "Projects" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Uploads" })).not.toBeInTheDocument();
    expect(documentLinks.some((link) => link.getAttribute("aria-current") === "page")).toBe(true);
    expect(container.querySelector('nav[aria-label="Primary"]')).toBeInTheDocument();
    expect(container.querySelector('nav[aria-label="Mobile primary"]')).toBeInTheDocument();
  });
});
