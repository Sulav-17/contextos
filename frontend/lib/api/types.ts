export type GreetingMode = "full" | "minimized" | "direct";
export type MotionMode = "system" | "reduced";
export type ThemeMode = "dark" | "system";

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
