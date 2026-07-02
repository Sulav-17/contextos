"use client";

export async function clearPrivateClientState() {
  try {
    window.sessionStorage.clear();
    for (const key of Object.keys(window.localStorage)) {
      if (key.startsWith("contextos.")) {
        window.localStorage.removeItem(key);
      }
    }
    if ("caches" in window) {
      const names = await caches.keys();
      await Promise.all(
        names.filter((name) => name.startsWith("contextos-")).map((name) => caches.delete(name)),
      );
    }
  } catch {
    // Best-effort browser cleanup before server-side logout clears the session.
  }
}
