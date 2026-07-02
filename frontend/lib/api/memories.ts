import "server-only";

import { apiFetch } from "@/lib/api/client";
import type { Memory, MemoryList, MemoryType } from "@/lib/api/types";

export function getMemories(status?: string): Promise<MemoryList> {
  const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiFetch<MemoryList>(`/api/v1/memories${suffix}`);
}

export function getMemorySuggestions(): Promise<MemoryList> {
  return apiFetch<MemoryList>("/api/v1/memories/suggestions");
}

export function createMemory(memoryType: MemoryType, content: string): Promise<Memory> {
  return apiFetch<Memory>("/api/v1/memories", {
    method: "POST",
    body: JSON.stringify({ memory_type: memoryType, content }),
  });
}

export function updateMemory(
  memoryId: string,
  memoryType: MemoryType,
  content: string,
): Promise<Memory> {
  return apiFetch<Memory>(`/api/v1/memories/${memoryId}`, {
    method: "PATCH",
    body: JSON.stringify({ memory_type: memoryType, content }),
  });
}

export function approveMemory(memoryId: string): Promise<Memory> {
  return apiFetch<Memory>(`/api/v1/memories/${memoryId}/approve`, { method: "POST" });
}

export function rejectMemory(memoryId: string): Promise<Memory> {
  return apiFetch<Memory>(`/api/v1/memories/${memoryId}/reject`, { method: "POST" });
}

export function disableMemory(memoryId: string): Promise<Memory> {
  return apiFetch<Memory>(`/api/v1/memories/${memoryId}/disable`, { method: "POST" });
}

export function enableMemory(memoryId: string): Promise<Memory> {
  return apiFetch<Memory>(`/api/v1/memories/${memoryId}/enable`, { method: "POST" });
}

export function deleteMemory(memoryId: string): Promise<void> {
  return apiFetch<void>(`/api/v1/memories/${memoryId}`, { method: "DELETE" });
}
