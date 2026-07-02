export type GreetingMode = "full" | "minimized" | "direct";
export type MotionMode = "system" | "reduced";
export type ThemeMode = "dark" | "light" | "system";

export type Me = {
  id: string;
  email: string;
  display_name: string | null;
  role: "user" | "admin";
  status: string;
  memory_enabled: boolean;
};

export type Preferences = {
  user_id: string;
  greeting_mode: GreetingMode;
  motion_mode: MotionMode;
  theme_mode: ThemeMode;
  welcome_completed: boolean;
};

export type Invitation = {
  id: string;
  email: string;
  requested_role: "user" | "admin";
  status: string;
  expires_at: string;
  sent_at: string | null;
  accepted_at: string | null;
};

export type InvitationList = {
  beta_max_users: number;
  occupied_slots: number;
  invitations: Invitation[];
};

export type DocumentStatus = "uploaded" | "queued" | "processing" | "ready" | "failed" | "deleted";

export type DocumentMetadata = {
  id: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  checksum_sha256: string | null;
  status: DocumentStatus;
  page_count: number | null;
  extracted_character_count: number | null;
  failure_code: string | null;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
  processed_at: string | null;
};

export type DocumentList = {
  documents: DocumentMetadata[];
};

export type UsageBucket = {
  used: number;
  limit: number;
  remaining: number;
};

export type UsageStatus = {
  daily: UsageBucket;
  monthly: UsageBucket;
};

export type ConversationSummary = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
};

export type Citation = {
  citation_index: number;
  document_id: string;
  document_name: string;
  page_number: number;
  excerpt: string;
};

export type ConversationMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: string;
  created_at: string;
  citations: Citation[];
  memory_references: MemoryReference[];
  source_mode: SourceMode;
};

export type ConversationList = {
  conversations: ConversationSummary[];
};

export type ConversationDetail = ConversationSummary & {
  messages: ConversationMessage[];
  selected_document_ids: string[];
};

export type MessageCreateResponse = {
  message: ConversationMessage;
  usage: UsageStatus;
  evidence_status: "grounded" | "insufficient_evidence";
  memory_used: boolean;
  memory_references: MemoryReference[];
  source_mode: SourceMode;
};

export type SourceMode =
  | "general"
  | "contextos"
  | "memory"
  | "documents"
  | "documents_and_memory"
  | "memory_suggestion_created"
  | "insufficient_evidence";

export type MemoryType =
  | "identity"
  | "background"
  | "goal"
  | "preference"
  | "project"
  | "decision"
  | "constraint"
  | "other";

export type MemoryStatus = "suggested" | "approved" | "disabled" | "rejected";

export type Memory = {
  id: string;
  memory_type: MemoryType;
  content: string;
  status: MemoryStatus;
  source_kind: "manual" | "conversation";
  source_conversation_id: string | null;
  source_conversation_title: string | null;
  source_message_id: string | null;
  created_at: string;
  updated_at: string;
  disabled_at: string | null;
};

export type MemoryList = {
  memories: Memory[];
};

export type MemoryReference = {
  id: string;
  memory_type: MemoryType;
  content: string;
  source_conversation_id: string | null;
  source_conversation_title: string | null;
};

export type DashboardCounts = {
  active_documents: number;
  active_conversations: number;
  approved_memories: number;
  pending_suggestions: number;
};

export type DashboardConversation = {
  id: string;
  title: string;
  updated_at: string;
  archived_at: string | null;
};

export type DashboardDocument = {
  id: string;
  original_filename: string;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
};

export type DashboardMemory = {
  id: string;
  memory_type: MemoryType;
  content: string;
  status: MemoryStatus;
  source_conversation_id: string | null;
  source_conversation_title: string | null;
  updated_at: string;
};

export type DashboardData = {
  counts: DashboardCounts;
  usage: UsageStatus;
  recent_conversations: DashboardConversation[];
  recent_documents: DashboardDocument[];
  recent_memories: DashboardMemory[];
  pending_suggestions: DashboardMemory[];
};
