import "server-only";
import { z } from "zod";

const serverEnvSchema = z.object({
  CONTEXTOS_API_URL: z.string().url().default("http://127.0.0.1:8000"),
  NEXT_PUBLIC_SUPABASE_URL: z.string().url().default("http://localhost:54321"),
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: z.string().min(1).default("local-publishable-key"),
  NEXT_PUBLIC_SITE_URL: z.string().url().default("http://localhost:3000"),
});

export const serverEnv = serverEnvSchema.parse(process.env);
