import { createSign } from "node:crypto";
import { unstable_cache } from "next/cache";

// How many people have used the site, for the homepage's live stat.
//
// Read from Google Analytics (totalUsers since launch) on the server, cached
// for an hour. GA is a floor, not a census: it never counts people with ad
// blockers, and from 22 Sep to 21 Oct 2026 the site's own CSP blocked most of
// its hits (see docs/OWNERS_GUIDE.md, section 11). So the card says "+" and
// never claims an exact count.
//
// Needs two Vercel env vars: GA_PROPERTY_ID and GA_SERVICE_ACCOUNT_KEY (the
// service account's JSON key, raw or base64). Without them, or if GA fails,
// it shows REACH_FLOOR: the GA total last read by hand.
export const REACH_FLOOR = { users: 847, asOf: "2026-10-21" } as const;

type Key = { client_email: string; private_key: string };

function readKey(): Key | null {
  const raw = process.env.GA_SERVICE_ACCOUNT_KEY;
  if (!raw) return null;
  try {
    const json = raw.trim().startsWith("{") ? raw : Buffer.from(raw, "base64").toString("utf8");
    const key = JSON.parse(json);
    return key.client_email && key.private_key ? key : null;
  } catch {
    return null;
  }
}

const b64url = (s: string | Buffer) => Buffer.from(s).toString("base64url");

async function accessToken(key: Key): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const head = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claims = b64url(JSON.stringify({
    iss: key.client_email,
    scope: "https://www.googleapis.com/auth/analytics.readonly",
    aud: "https://oauth2.googleapis.com/token",
    iat: now,
    exp: now + 3600,
  }));
  const sig = createSign("RSA-SHA256").update(`${head}.${claims}`).sign(key.private_key);
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion: `${head}.${claims}.${b64url(sig)}`,
    }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`token ${res.status}`);
  return (await res.json()).access_token;
}

async function fetchReach(): Promise<number | null> {
  const key = readKey();
  const property = process.env.GA_PROPERTY_ID?.trim();
  if (!key || !property) return null;
  try {
    const token = await accessToken(key);
    const res = await fetch(`https://analyticsdata.googleapis.com/v1beta/properties/${property}:runReport`, {
      method: "POST",
      headers: { authorization: `Bearer ${token}`, "content-type": "application/json" },
      body: JSON.stringify({
        dateRanges: [{ startDate: "2020-01-01", endDate: "today" }],
        metrics: [{ name: "totalUsers" }],
      }),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`runReport ${res.status}`);
    const value = Number((await res.json()).rows?.[0]?.metricValues?.[0]?.value);
    return Number.isFinite(value) && value > 0 ? value : null;
  } catch (err) {
    console.error("reach: GA read failed", err);
    return null;
  }
}

const cachedReach = unstable_cache(fetchReach, ["ga-total-users"], { revalidate: 3600 });

/** People who have used the site: GA's total, never below the hand-read floor. */
export async function getReach(): Promise<{ users: number; live: boolean }> {
  const users = await cachedReach();
  return users ? { users: Math.max(users, REACH_FLOOR.users), live: true } : { users: REACH_FLOOR.users, live: false };
}
