/**
 * A daily ceiling on paid model calls made on behalf of anonymous visitors.
 *
 * Per-IP rate limiting answers "is one person hammering this?". It does not
 * answer "what is the most this endpoint can cost me today?", and those are
 * different questions. A thousand IPs making one call each pass every per-IP
 * check ever written, and the traffic spike on 2026-08-17 was exactly that
 * shape: 61 users from one country inside a single hour.
 *
 * Same serverless caveat as the rate limiter: the counter lives in one
 * instance's memory, so the true ceiling is roughly this number times the
 * number of warm instances. It converts an unbounded worst case into a bounded
 * one, which is the point. It is NOT a spend cap.
 *
 * The only real spend cap is the limit set on the Anthropic account itself.
 * Set that too. This is the thing that keeps a bad day from becoming a bad
 * month; the console limit is the thing that keeps a bad month from happening.
 */

type Day = { date: string; count: number };

const state: Day = { date: "", count: 0 };

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

/**
 * Claim one call against today's budget. Returns false when the budget is
 * spent, in which case the caller must degrade rather than fail: the results
 * page already falls back to its deterministic summary, so a visitor who
 * arrives after the cap still gets a complete, accurate result. They just do
 * not get the personalised paragraph.
 */
export function claimAiCall(limit: number): { allowed: boolean; used: number; limit: number } {
  const d = today();
  if (state.date !== d) {
    state.date = d;
    state.count = 0;
  }
  if (state.count >= limit) {
    return { allowed: false, used: state.count, limit };
  }
  state.count += 1;
  return { allowed: true, used: state.count, limit };
}

/** Configurable so a real traffic day can be accommodated without a deploy. */
export function dailyAiLimit(): number {
  const raw = Number(process.env.AI_SUMMARY_DAILY_LIMIT);
  return Number.isFinite(raw) && raw > 0 ? raw : 300;
}
