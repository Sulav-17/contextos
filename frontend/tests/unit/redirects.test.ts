import { describe, expect, it } from "vitest";

import { safeRedirectPath } from "@/lib/auth/redirects";

describe("safeRedirectPath", () => {
  it("allows only internal allow-listed destinations", () => {
    expect(safeRedirectPath("/settings")).toBe("/settings");
    expect(safeRedirectPath("https://evil.example")).toBe("/home");
    expect(safeRedirectPath("//evil.example")).toBe("/home");
    expect(safeRedirectPath("/unknown")).toBe("/home");
  });
});
