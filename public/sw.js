// Bumped from v1 on 2026-10-30. The activate handler deletes every other
// cache, which is the only way to reach visitors already stuck on stale pages
// (see the fetch handler).
const CACHE_NAME = "oralcheck-v2";

// Pages to pre-cache for offline access
const PRECACHE_URLS = [
  "/",
  "/learn",
  "/learn/signs",
  "/learn/self-exam",
  "/learn/facts",
  "/about",
  "/offline",
];

// ── Install: pre-cache educational pages ──────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .catch(() => {
        // Non-fatal: some pages may not be reachable at install time
      }),
  );
  self.skipWaiting();
});

// ── Activate: delete caches from old versions ─────────────────────────────────
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((names) =>
        Promise.all(
          names
            .filter((n) => n !== CACHE_NAME)
            .map((n) => caches.delete(n)),
        ),
      ),
  );
  self.clients.claim();
});

// ── Fetch ─────────────────────────────────────────────────────────────────────
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle same-origin GET requests
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  // Skip API routes — always need fresh data
  if (url.pathname.startsWith("/api/")) return;

  // Next.js build chunks: cache-first (they're content-hashed, safe to cache forever)
  if (url.pathname.startsWith("/_next/static/")) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Pages and everything else: network first, cache only as the offline
  // fallback. "/", /learn and /about used to be stale-while-revalidate, which
  // was wrong twice over. Its background refresh was never passed to
  // event.waitUntil, so the browser stopped the worker before the fresh copy
  // was saved and a returning visitor got the page as it was on their first
  // visit, indefinitely. And a stale page is not just old text: it carries the
  // old response headers (the pre-21-Oct security policy, which blocks Google
  // Analytics) and points at JavaScript chunks that later deploys removed, so
  // its scripts fail to load. Found 2026-10-30 when GA showed returning
  // visitors' pageviews going missing.
  event.respondWith(networkFirst(request));
});

// ── Strategies ────────────────────────────────────────────────────────────────

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, response.clone());
  }
  return response;
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached ?? offlineFallback();
  }
}

function offlineFallback() {
  return new Response(
    `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>OralCheck — Offline</title>
    <style>
      body{font-family:system-ui,sans-serif;background:#faf9f6;color:#2d2d2d;
           display:flex;flex-direction:column;align-items:center;justify-content:center;
           min-height:100vh;margin:0;padding:2rem;text-align:center;}
      h1{font-size:2rem;margin-bottom:1rem;}
      p{color:#6b6b6b;max-width:320px;line-height:1.6;}
      a{color:#0d7377;font-weight:600;}
    </style></head>
    <body>
      <h1>You're offline</h1>
      <p>The screener and clinic finder need an internet connection.
         The <a href="/learn">Learn pages</a> and <a href="/about">About</a>
         are available offline once you've visited them.</p>
    </body></html>`,
    { headers: { "Content-Type": "text/html" } },
  );
}
