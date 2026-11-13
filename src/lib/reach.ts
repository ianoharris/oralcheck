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

// Only the real site counts. Development servers once reported to the same GA
// property (376 of 1,321 page views in the 90 days to 30 Oct 2026), which put
// the homepage count about 24 people above the truth.
const LIVE_HOSTS = {
  filter: { fieldName: "hostName", inListFilter: { values: ["oralcheck.org", "www.oralcheck.org"] } },
};

async function runReport(body: Record<string, unknown>): Promise<{ rows?: { dimensionValues?: { value: string }[]; metricValues: { value: string }[] }[] } | null> {
  const key = readKey();
  const property = process.env.GA_PROPERTY_ID?.trim();
  if (!key || !property) return null;
  try {
    const token = await accessToken(key);
    const res = await fetch(`https://analyticsdata.googleapis.com/v1beta/properties/${property}:runReport`, {
      method: "POST",
      headers: { authorization: `Bearer ${token}`, "content-type": "application/json" },
      body: JSON.stringify({ dateRanges: [{ startDate: "2020-01-01", endDate: "today" }], limit: 500, ...body }),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`runReport ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("reach: GA read failed", err);
    return null;
  }
}

async function fetchReach(): Promise<number | null> {
  const data = await runReport({ metrics: [{ name: "totalUsers" }], dimensionFilter: LIVE_HOSTS });
  const value = Number(data?.rows?.[0]?.metricValues?.[0]?.value);
  return Number.isFinite(value) && value > 0 ? value : null;
}

/** How many distinct values of a dimension real visitors have, "(not set)" excluded. */
async function countDistinct(dimension: string, extra?: Record<string, unknown>): Promise<number | null> {
  const filters: Record<string, unknown>[] = [LIVE_HOSTS];
  if (extra) filters.push(extra);
  const data = await runReport({
    dimensions: [{ name: dimension }],
    metrics: [{ name: "totalUsers" }],
    dimensionFilter: { andGroup: { expressions: filters } },
  });
  if (!data) return null;
  return (data.rows ?? []).filter((r) => r.dimensionValues?.[0]?.value && r.dimensionValues[0].value !== "(not set)").length;
}

/**
 * The figures the 1,000-visitor post is built from, read the morning it goes
 * out (oralcheck-agent/milestone.py, via /api/reach). "Finished" is people who
 * reached a results page in any language: a floor, like every GA number.
 */
async function fetchMilestone() {
  const [users, countries, states, finishedData] = await Promise.all([
    fetchReach(),
    countDistinct("country"),
    countDistinct("region", { filter: { fieldName: "country", stringFilter: { value: "United States" } } }),
    runReport({
      metrics: [{ name: "totalUsers" }],
      dimensionFilter: {
        andGroup: {
          expressions: [LIVE_HOSTS, { filter: { fieldName: "pagePath", inListFilter: { values: ["/results", "/es/results", "/pt/results"] } } }],
        },
      },
    }),
  ]);
  const finished = Number(finishedData?.rows?.[0]?.metricValues?.[0]?.value);
  if (!users || countries === null || states === null || !Number.isFinite(finished)) return null;
  return { users, countries, states, finished, asOf: new Date().toISOString() };
}

export const getMilestoneStats = unstable_cache(fetchMilestone, ["ga-milestone"], { revalidate: 3600 });

const cachedReach = unstable_cache(fetchReach, ["ga-total-users"], { revalidate: 3600 });

/** People who have used the site: GA's total, never below the hand-read floor. */
export async function getReach(): Promise<{ users: number; live: boolean }> {
  const users = await cachedReach();
  return users ? { users: Math.max(users, REACH_FLOOR.users), live: true } : { users: REACH_FLOOR.users, live: false };
}
