"use server";

import { revalidatePath } from "next/cache";

import {
  createConversation,
  deleteConversation,
  submitQuestion,
} from "@/lib/api/conversations";

export type ChatActionState = {
  status: "idle" | "success" | "error";
  message: string;
};

export async function createConversationAction(): Promise<void> {
  await createConversation();
  revalidatePath("/conversations");
}

export async function deleteConversationAction(formData: FormData): Promise<void> {
  const conversationId = String(formData.get("conversation_id") ?? "");
  await deleteConversation(conversationId);
  revalidatePath("/conversations");
}

export async function submitQuestionAction(
  _state: ChatActionState,
  formData: FormData,
): Promise<ChatActionState> {
  const conversationId = String(formData.get("conversation_id") ?? "");
  const question = String(formData.get("question") ?? "").trim();
  const documentIds = formData.getAll("document_ids").map(String);
  if (!conversationId || !question) {
    return { status: "error", message: "Write a question before sending." };
  }
  try {
    await submitQuestion(conversationId, question, documentIds);
    revalidatePath("/conversations");
    return { status: "success", message: "Answer added." };
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Question failed.",
    };
  }
}
