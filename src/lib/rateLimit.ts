/**
 * Simple in-memory sliding-window rate limiter.
 *
 * Works well for a single-process dev server and light Vercel traffic.
 * For high-scale multi-instance deployments, swap the Map for Redis
 * (e.g. @upstash/ratelimit).
 */

type WindowEntry = { count: number; windowStart: number };

const store = new Map<string, WindowEntry>();

// Prune stale entries every 5 minutes so the Map doesn't grow forever.
const PRUNE_INTERVAL_MS = 5 * 60 * 1000;
let lastPruned = Date.now();

function prune(windowMs: number) {
  const now = Date.now();
  if (now - lastPruned < PRUNE_INTERVAL_MS) return;
  lastPruned = now;
  for (const [key, entry] of store.entries()) {
    if (now - entry.windowStart > windowMs) store.delete(key);
  }
}

export function checkRateLimit(
  ip: string,
  limit: number,
  windowMs = 60_000,
): { allowed: boolean; remaining: number; resetMs: number } {
  const now = Date.now();
  prune(windowMs);

  const entry = store.get(ip);

  if (!entry || now - entry.windowStart > windowMs) {
    // New window
    store.set(ip, { count: 1, windowStart: now });
    return { allowed: true, remaining: limit - 1, resetMs: windowMs };
  }

  if (entry.count >= limit) {
    const resetMs = windowMs - (now - entry.windowStart);
    return { allowed: false, remaining: 0, resetMs };
  }

  entry.count += 1;
  return {
    allowed: true,
    remaining: limit - entry.count,
    resetMs: windowMs - (now - entry.windowStart),
  };
}

export function getIp(req: Request): string {
  // Vercel sets x-forwarded-for; fall back to a placeholder in local dev.
  const forwarded = req.headers.get("x-forwarded-for");
  return forwarded ? forwarded.split(",")[0].trim() : "127.0.0.1";
}
