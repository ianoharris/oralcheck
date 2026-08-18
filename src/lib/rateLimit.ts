/**
 * Simple in-memory fixed-window rate limiter.
 *
 * Know what this does and does not buy you. The Map lives in one serverless
 * instance, and Vercel runs as many instances as traffic demands, so the real
 * ceiling is roughly `limit x concurrent instances` and it resets whenever an
 * instance is recycled. It stops a single client hammering one warm instance.
 * It does not stop a distributed flood, and it is not a spend cap.
 *
 * The routes it guards spend real money per call (Anthropic on /api/summary,
 * Google Places on /api/clinics, Resend on the mail routes), so the durable
 * protections are the provider-side quotas and budgets, with this as the cheap
 * first line. Swap the Map for Redis (@upstash/ratelimit) to make the limits
 * mean exactly what they say.
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
  // Order matters. `x-forwarded-for` is a client-supplied header that proxies
  // append to, so its FIRST entry is whatever the caller put there: reading
  // that value let anyone rotate their own rate-limit bucket by sending a new
  // x-forwarded-for on every request, which makes the limits below decorative.
  //
  // Vercel sets `x-vercel-forwarded-for` and `x-real-ip` from the connection
  // itself and strips inbound copies, so those cannot be forged by the client.
  // The x-forwarded-for fallback is for local dev and non-Vercel hosts; on
  // those the LAST entry is the one the nearest trusted proxy wrote.
  const trusted =
    req.headers.get("x-vercel-forwarded-for") ?? req.headers.get("x-real-ip");
  if (trusted) return trusted.split(",")[0].trim();

  const forwarded = req.headers.get("x-forwarded-for");
  if (forwarded) {
    const parts = forwarded.split(",").map((p) => p.trim()).filter(Boolean);
    if (parts.length) return parts[parts.length - 1];
  }
  return "127.0.0.1";
}
