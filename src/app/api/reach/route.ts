import { getMilestoneStats, getReach } from "@/lib/reach";

/**
 * Aggregate visitor counts, for the daily job that posts the 1,000-visitor
 * reel (oralcheck-agent/milestone.py). GitHub holds no Analytics key, so the
 * job reads the numbers here instead. Totals only: nothing about any visitor.
 */
export async function GET() {
  const [reach, stats] = await Promise.all([getReach(), getMilestoneStats()]);
  return Response.json(
    { users: reach.users, live: reach.live, ...(stats ? { countries: stats.countries, states: stats.states, finished: stats.finished, asOf: stats.asOf } : {}) },
    { headers: { "cache-control": "public, max-age=600" } },
  );
}
