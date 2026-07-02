import { describe, expect, it } from "vitest";

import { primaryNavItems, secondaryNavItems } from "@/components/navigation/nav-items";

describe("navigation", () => {
  it("keeps the authenticated navigation focused on the real surfaces", () => {
    expect(primaryNavItems.map((item) => item.label)).toEqual([
      "Home",
      "Conversations",
      "Documents",
      "Memories",
    ]);
    expect(secondaryNavItems.map((item) => item.label)).toEqual(["Settings"]);
    expect(primaryNavItems.map((item) => item.label)).not.toContain("Projects");
    expect(primaryNavItems.map((item) => item.label)).not.toContain("Uploads");
    expect(secondaryNavItems.map((item) => item.label)).not.toContain("Projects");
    expect(secondaryNavItems.map((item) => item.label)).not.toContain("Uploads");
    expect(secondaryNavItems.map((item) => item.label)).not.toContain("Admin");
  });
});
