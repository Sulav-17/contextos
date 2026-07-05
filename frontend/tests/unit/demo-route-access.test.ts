import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { proxy } from "@/proxy";

const { getUser } = vi.hoisted(() => ({
  getUser: vi.fn(),
}));

vi.mock("@supabase/ssr", () => ({
  createServerClient: vi.fn(() => ({
    auth: { getUser },
  })),
}));

function request(pathname: string) {
  return new NextRequest(new Request(`http://localhost:3000${pathname}`));
}

describe("demo route access", () => {
  beforeEach(() => {
    getUser.mockReset();
    process.env.NEXT_PUBLIC_SUPABASE_URL = "http://localhost:54321";
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY = "local-publishable-key";
  });

  it("allows unauthenticated users to visit /demo", async () => {
    getUser.mockResolvedValue({ data: { user: null } });

    const response = await proxy(request("/demo"));

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });

  it("allows authenticated users to visit /demo", async () => {
    getUser.mockResolvedValue({ data: { user: { id: "demo-auth-user" } } });

    const response = await proxy(request("/demo"));

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });

  it("keeps workspace routes protected for unauthenticated users", async () => {
    getUser.mockResolvedValue({ data: { user: null } });

    const response = await proxy(request("/home"));

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("http://localhost:3000/login?next=%2Fhome");
  });
});
