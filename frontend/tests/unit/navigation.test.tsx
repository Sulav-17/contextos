import { describe, expect, it } from "vitest";

import { primaryNavItems, secondaryNavItems } from "@/components/navigation/nav-items";

describe("navigation", () => {
  it("keeps mobile primary navigation focused", () => {
    expect(primaryNavItems.map((item) => item.label)).toEqual([
      "Home",
      "Conversations",
      "Libraries",
      "Memories",
    ]);
    expect(secondaryNavItems.map((item) => item.label)).toContain("Projects");
    expect(secondaryNavItems.map((item) => item.label)).not.toContain("Admin");
  });
});
