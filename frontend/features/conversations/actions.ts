"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import {
  archiveConversation,
  createConversation,
  createScopedConversation,
  deleteConversation,
  submitQuestion,
  unarchiveConversation,
  updateConversationTitle,
} from "@/lib/api/conversations";

export type ChatActionState = {
  status: "idle" | "success" | "error";
  message: string;
};

export async function createConversationAction(): Promise<void> {
  const conversation = await createConversation();
  revalidatePath("/conversations");
  redirect(`/conversations?conversation=${conversation.id}`);
}

export async function createScopedConversationAction(formData: FormData): Promise<void> {
  const documentIds = formData.getAll("document_ids").map(String).filter(Boolean);
  const conversation = await createScopedConversation(documentIds);
  revalidatePath("/conversations");
  revalidatePath("/home");
  revalidatePath("/libraries");
  redirect(`/conversations?conversation=${conversation.id}`);
}

export async function deleteConversationAction(formData: FormData): Promise<void> {
  const conversationId = String(formData.get("conversation_id") ?? "");
  await deleteConversation(conversationId);
  revalidatePath("/conversations");
  redirect("/conversations");
}

export async function archiveConversationAction(formData: FormData): Promise<void> {
  const conversationId = String(formData.get("conversation_id") ?? "");
  await archiveConversation(conversationId);
  revalidatePath("/conversations");
}

export async function unarchiveConversationAction(formData: FormData): Promise<void> {
  const conversationId = String(formData.get("conversation_id") ?? "");
  await unarchiveConversation(conversationId);
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
    const response = await submitQuestion(conversationId, question, documentIds);
    revalidatePath("/conversations");
    if (response.source_mode === "memory_suggestion_created") {
      return { status: "success", message: "Memory suggestion created. Awaiting approval." };
    }
    return { status: "success", message: "Answer added." };
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Question failed.",
    };
  }
}

export async function quickStartConversationAction(
  _state: ChatActionState,
  formData: FormData,
): Promise<ChatActionState> {
  const question = String(formData.get("question") ?? "").trim();
  const documentIds = formData.getAll("document_ids").map(String);
  if (!question) {
    return { status: "error", message: "Write a question before starting." };
  }
  let conversationId = "";
  try {
    const conversation = await createConversation();
    await submitQuestion(conversation.id, question, documentIds);
    conversationId = conversation.id;
    revalidatePath("/home");
    revalidatePath("/conversations");
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Conversation could not start.",
    };
  }
  redirect(`/conversations?conversation=${conversationId}`);
}

export async function renameConversationAction(
  _state: ChatActionState,
  formData: FormData,
): Promise<ChatActionState> {
  const conversationId = String(formData.get("conversation_id") ?? "");
  const title = String(formData.get("title") ?? "").trim();
  if (!conversationId || !title) {
    return { status: "error", message: "Enter a title before saving." };
  }
  try {
    await updateConversationTitle(conversationId, title);
    revalidatePath("/conversations");
    return { status: "success", message: "Title updated." };
  } catch (error) {
    return {
      status: "error",
      message: error instanceof Error ? error.message : "Title could not be updated.",
    };
  }
}
