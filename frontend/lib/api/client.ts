import "server-only";
import { randomUUID } from "node:crypto";

import { createSupabaseServerClient } from "@/lib/supabase/server";
import { serverEnv } from "@/lib/env/server";

export type ApiErrorCode =
  | "authentication_required"
  | "invalid_authentication"
  | "user_not_provisioned"
  | "account_disabled"
  | "administrator_required"
  | "invitation_duplicate"
  | "beta_capacity_reached"
  | "provider_unavailable"
  | "validation_failed"
  | "backend_unavailable";

export class ApiClientError extends Error {
  constructor(
    public readonly code: ApiErrorCode,
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

type ErrorPayload = {
  error?: {
    code?: ApiErrorCode;
    message?: string;
  };
};

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  const token = session?.access_token;
  if (!token) {
    throw new ApiClientError("authentication_required", "Authentication is required.", 401);
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(new URL(path, serverEnv.CONTEXTOS_API_URL), {
      ...init,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-Request-ID": randomUUID(),
        ...init.headers,
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
      signal: controller.signal,
    });
    if (!response.ok) {
      let payload: ErrorPayload = {};
      try {
        payload = (await response.json()) as ErrorPayload;
      } catch {
        payload = {};
      }
      throw new ApiClientError(
        payload.error?.code ?? "backend_unavailable",
        payload.error?.message ?? "ContextOS is unavailable.",
        response.status,
      );
    }
    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    throw new ApiClientError("backend_unavailable", "ContextOS is unavailable.", 503);
  } finally {
    clearTimeout(timeout);
  }
}
