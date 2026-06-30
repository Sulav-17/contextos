import { beforeEach, describe, expect, it, vi } from "vitest";
import type { NextRequest } from "next/server";

import { GET } from "@/app/auth/confirm/route";

const exchangeCodeForSession = vi.fn();
const verifyOtp = vi.fn();

vi.mock("server-only", () => ({}));

vi.mock("@/lib/supabase/server", () => ({
  createSupabaseServerClient: vi.fn(async () => ({
    auth: {
      exchangeCodeForSession,
      verifyOtp,
    },
  })),
}));

describe("auth confirmation route", () => {
  beforeEach(() => {
    exchangeCodeForSession.mockReset();
    verifyOtp.mockReset();
  });

  it("redirects successful code exchange to the configured public site URL", async () => {
    exchangeCodeForSession.mockResolvedValue({ error: null });
    const request = new Request(
      "http://container-host:3000/auth/confirm?code=test-code&next=/home",
    ) as NextRequest;

    const response = await GET(request);

    expect(exchangeCodeForSession).toHaveBeenCalledWith("test-code");
    expect(response.headers.get("location")).toBe("http://localhost:3000/home");
  });

  it("redirects failed code exchange to the configured public site auth error page", async () => {
    exchangeCodeForSession.mockResolvedValue({ error: { message: "expired" } });
    const request = new Request(
      "http://container-host:3000/auth/confirm?code=test-code&next=/home",
    ) as NextRequest;

    const response = await GET(request);

    expect(exchangeCodeForSession).toHaveBeenCalledWith("test-code");
    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/auth/error?reason=expired-link",
    );
  });
});
