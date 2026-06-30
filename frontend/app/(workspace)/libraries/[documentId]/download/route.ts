import { randomUUID } from "node:crypto";

import { NextResponse, type NextRequest } from "next/server";

import { serverEnv } from "@/lib/env/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ documentId: string }> },
) {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  const token = session?.access_token;
  if (!token) {
    return NextResponse.json({ error: "Authentication is required." }, { status: 401 });
  }

  const { documentId } = await params;
  const response = await fetch(
    new URL(`/api/v1/documents/${documentId}/download`, serverEnv.CONTEXTOS_API_URL),
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "X-Request-ID": randomUUID(),
      },
      cache: "no-store",
    },
  );
  if (!response.ok || response.body === null) {
    return NextResponse.json({ error: "Document download is unavailable." }, { status: response.status });
  }
  return new NextResponse(response.body, {
    status: 200,
    headers: {
      "Cache-Control": "private, no-store",
      "Content-Disposition": response.headers.get("Content-Disposition") ?? "attachment",
      "Content-Type": response.headers.get("Content-Type") ?? "application/pdf",
    },
  });
}
