const CACHE_VERSION = "v1";
const STATIC_CACHE = `contextos-static-${CACHE_VERSION}`;
const SHELL_CACHE = `contextos-shell-${CACHE_VERSION}`;
const PUBLIC_ASSETS = [
  "/offline.html",
  "/manifest.webmanifest",
  "/icons/contextos-icon.svg",
  "/icons/contextos-maskable.svg",
  "/icons/contextos-apple.svg",
];
const PRIVATE_ROUTE_PATTERNS = [
  /^\/api\//,
  /^\/auth\//,
  /^\/login/,
  /^\/signup/,
  /^\/forgot-password/,
  /^\/update-password/,
  /^\/invite\//,
  /^\/libraries\/[^/]+\/download/,
  /^\/conversations/,
  /^\/memories/,
  /^\/settings/,
  /^\/admin/,
  /^\/home/,
];
const PRIVATE_REQUEST_HINTS = [
  "authorization",
  "sb-",
  "supabase",
  "access_token",
  "refresh_token",
  "document",
  "upload",
  "download",
  "conversation",
  "memory",
  "dashboard",
  "usage",
];

function isPrivateRequest(request) {
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    return true;
  }
  if (request.method !== "GET") {
    return true;
  }
  if (request.headers.has("Authorization")) {
    return true;
  }
  const combined = `${url.pathname} ${url.search}`.toLowerCase();
  return (
    PRIVATE_ROUTE_PATTERNS.some((pattern) => pattern.test(url.pathname)) ||
    PRIVATE_REQUEST_HINTS.some((hint) => combined.includes(hint))
  );
}

function isStaticAsset(request) {
  const url = new URL(request.url);
  return (
    url.origin === self.location.origin &&
    request.method === "GET" &&
    (url.pathname.startsWith("/_next/static/") ||
      url.pathname.startsWith("/icons/") ||
      PUBLIC_ASSETS.includes(url.pathname))
  );
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PUBLIC_ASSETS)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((names) =>
        Promise.all(
          names
            .filter((name) => name.startsWith("contextos-") && ![STATIC_CACHE, SHELL_CACHE].includes(name))
            .map((name) => caches.delete(name)),
        ),
      )
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (isPrivateRequest(request)) {
    event.respondWith(fetch(request, { cache: "no-store" }));
    return;
  }

  if (isStaticAsset(request)) {
    event.respondWith(
      caches.open(STATIC_CACHE).then(async (cache) => {
        const cached = await cache.match(request);
        if (cached) {
          return cached;
        }
        const response = await fetch(request);
        if (response.ok && response.type === "basic") {
          await cache.put(request, response.clone());
        }
        return response;
      }),
    );
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(fetch(request).catch(() => caches.match("/offline.html")));
  }
});
