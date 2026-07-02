"use server";

import { revalidatePath } from "next/cache";

import {
  approveMemory,
  createMemory,
  deleteMemory,
  disableMemory,
  enableMemory,
  rejectMemory,
  updateMemory,
} from "@/lib/api/memories";
import type { MemoryType } from "@/lib/api/types";

export type MemoryActionState = {
  status: "idle" | "success" | "error";
  message: string;
};

const memoryTypes = new Set<MemoryType>([
  "identity",
  "background",
  "goal",
  "preference",
  "project",
  "decision",
  "constraint",
  "other",
]);

function parseType(value: FormDataEntryValue | null): MemoryType {
  const type = String(value ?? "other") as MemoryType;
  return memoryTypes.has(type) ? type : "other";
}

export async function createMemoryAction(
  _state: MemoryActionState,
  formData: FormData,
): Promise<MemoryActionState> {
  const content = String(formData.get("content") ?? "").trim();
  if (!content) {
    return { status: "error", message: "Enter memory content before saving." };
  }
  try {
    await createMemory(parseType(formData.get("memory_type")), content);
    revalidatePath("/memories");
    revalidatePath("/home");
    return { status: "success", message: "Memory saved." };
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Memory could not be saved.",
    };
  }
}

export async function updateMemoryAction(
  _state: MemoryActionState,
  formData: FormData,
): Promise<MemoryActionState> {
  const memoryId = String(formData.get("memory_id") ?? "");
  const content = String(formData.get("content") ?? "").trim();
  if (!memoryId || !content) {
    return { status: "error", message: "Enter memory content before saving." };
  }
  try {
    await updateMemory(memoryId, parseType(formData.get("memory_type")), content);
    revalidatePath("/memories");
    revalidatePath("/home");
    return { status: "success", message: "Memory updated." };
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Memory could not be updated.",
    };
  }
}

export async function approveMemoryAction(formData: FormData): Promise<void> {
  await approveMemory(String(formData.get("memory_id") ?? ""));
  revalidatePath("/memories");
  revalidatePath("/home");
}

export async function rejectMemoryAction(formData: FormData): Promise<void> {
  await rejectMemory(String(formData.get("memory_id") ?? ""));
  revalidatePath("/memories");
  revalidatePath("/home");
}

export async function disableMemoryAction(formData: FormData): Promise<void> {
  await disableMemory(String(formData.get("memory_id") ?? ""));
  revalidatePath("/memories");
  revalidatePath("/home");
}

export async function enableMemoryAction(formData: FormData): Promise<void> {
  await enableMemory(String(formData.get("memory_id") ?? ""));
  revalidatePath("/memories");
  revalidatePath("/home");
}

export async function deleteMemoryAction(formData: FormData): Promise<void> {
  await deleteMemory(String(formData.get("memory_id") ?? ""));
  revalidatePath("/memories");
  revalidatePath("/home");
}
