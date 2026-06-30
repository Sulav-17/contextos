import { NextRequest, NextResponse } from "next/server";
import { serverEnv } from "@/lib/env/server";
import { safeRedirectPath } from "@/lib/auth/redirects";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const tokenHash = url.searchParams.get("token_hash");
  const type = url.searchParams.get("type");
  const code = url.searchParams.get("code");
  const next = safeRedirectPath(url.searchParams.get("next"), "/update-password");
  const supabase = await createSupabaseServerClient();

  if (code) {
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      return NextResponse.redirect(new URL(next, serverEnv.NEXT_PUBLIC_SITE_URL));
    }
  }

  if (tokenHash && (type === "invite" || type === "recovery")) {
    const { error } = await supabase.auth.verifyOtp({
      token_hash: tokenHash,
      type,
    });
    if (!error) {
      return NextResponse.redirect(new URL(type === "invite" ? "/update-password" : next, serverEnv.NEXT_PUBLIC_SITE_URL));
    }
  }

  return NextResponse.redirect(new URL("/auth/error?reason=expired-link", serverEnv.NEXT_PUBLIC_SITE_URL));
}
