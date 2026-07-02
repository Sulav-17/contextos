import "server-only";

import { apiFetch } from "@/lib/api/client";
import type { DashboardData } from "@/lib/api/types";

export function getDashboard(): Promise<DashboardData> {
  return apiFetch<DashboardData>("/api/v1/dashboard");
}
