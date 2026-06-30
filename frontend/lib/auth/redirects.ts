const ALLOWED_PATHS = new Set([
  "/home",
  "/settings",
  "/admin/invitations",
  "/conversations",
  "/libraries",
  "/projects",
  "/memories",
  "/uploads",
]);

export function safeRedirectPath(candidate: string | null | undefined, fallback = "/home") {
  if (!candidate || !candidate.startsWith("/") || candidate.startsWith("//")) {
    return fallback;
  }
  return ALLOWED_PATHS.has(candidate) ? candidate : fallback;
}
