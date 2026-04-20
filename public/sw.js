const CACHE_NAME = "oralcheck-v1";

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

  // Educational + static pages: stale-while-revalidate
  if (
    url.pathname === "/" ||
    url.pathname.startsWith("/learn") ||
    url.pathname === "/about"
  ) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Everything else: network first with offline fallback
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

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  const fetchPromise = fetch(request)
    .then((response) => {
      if (response.ok) cache.put(request, response.clone());
      return response;
    })
    .catch(() => null);
  return cached ?? (await fetchPromise) ?? offlineFallback();
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
