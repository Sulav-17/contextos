import { beforeEach, describe, expect, it, vi } from "vitest";

import ProjectsPage from "@/app/(workspace)/projects/page";
import UploadsPage from "@/app/(workspace)/uploads/page";

const { redirect } = vi.hoisted(() => ({
  redirect: vi.fn((path: string) => {
    throw new Error(`REDIRECT:${path}`);
  }),
}));

vi.mock("next/navigation", () => ({
  redirect,
}));

describe("legacy workspace routes", () => {
  beforeEach(() => {
    redirect.mockClear();
  });

  it("redirects /projects to /libraries", () => {
    expect(() => ProjectsPage()).toThrow("REDIRECT:/libraries");
    expect(redirect).toHaveBeenCalledWith("/libraries");
  });

  it("redirects /uploads to /libraries", () => {
    expect(() => UploadsPage()).toThrow("REDIRECT:/libraries");
    expect(redirect).toHaveBeenCalledWith("/libraries");
  });
});
