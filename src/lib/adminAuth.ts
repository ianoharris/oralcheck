import { timingSafeEqual } from "node:crypto";

/**
 * Shared-secret gate for the two routes that are not public: the draft reader
 * and the publisher.
 *
 * /api/publish had no authentication at all. It commits to and deletes from the
 * GitHub repo using GITHUB_ACCESS_TOKEN, so any request that reached it could
 * push an unreviewed article live on a health site and delete the draft behind
 * it. The review page it serves is unlinked and noindexed, which hides the page
 * but does nothing for the endpoint: the endpoint answers anyone who knows the
 * path, and the path is in the client bundle.
 *
 * A shared secret is the right weight here. There are no user accounts to hang
 * real auth off, one person publishes, and the secret never reaches a browser
 * except the one that types it in.
 */

const HEADER = "x-oralcheck-admin";

function constantTimeEquals(a: string, b: string): boolean {
  const ab = Buffer.from(a, "utf8");
  const bb = Buffer.from(b, "utf8");
  // timingSafeEqual throws on a length mismatch, and returning early on length
  // leaks it. Compare against a fixed-size digest-shaped buffer instead by
  // padding both to the longer length.
  const len = Math.max(ab.length, bb.length);
  const pa = Buffer.alloc(len);
  const pb = Buffer.alloc(len);
  ab.copy(pa);
  bb.copy(pb);
  return timingSafeEqual(pa, pb) && ab.length === bb.length;
}

export type AdminCheck =
  | { ok: true }
  | { ok: false; status: 401 | 503; error: string };

export function requireAdmin(req: Request): AdminCheck {
  const expected = process.env.ADMIN_SECRET ?? "";
  if (!expected) {
    // Fail closed. An unset secret used to mean "no check at all", which is the
    // exact state that left this open; it must not be the state a missing env
    // var falls back into.
    return {
      ok: false,
      status: 503,
      error: "ADMIN_SECRET is not configured on the server.",
    };
  }
  const provided = req.headers.get(HEADER) ?? "";
  if (!provided || !constantTimeEquals(provided, expected)) {
    return { ok: false, status: 401, error: "Unauthorized" };
  }
  return { ok: true };
}

export const ADMIN_HEADER = HEADER;
