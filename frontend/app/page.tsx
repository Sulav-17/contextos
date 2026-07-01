import { redirect } from "next/navigation";

import { PublicLanding } from "@/components/public/public-landing";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export default async function IndexPage() {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (session) {
    redirect("/home");
  }
  return <PublicLanding />;
}
