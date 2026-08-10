#!/usr/bin/env python3
"""
Print current OralCheck traffic from Google Analytics.

Exists so project numbers can be quoted from live data instead of from a
figure someone wrote down months ago. Reuses the same credentials as the
world-map reel mode (GA_PROPERTY_ID / GA_SERVICE_ACCOUNT_KEY_PATH).

    python3 ga_stats.py              # last 90 days
    python3 ga_stats.py --days 30
    python3 ga_stats.py --json       # machine-readable
    python3 ga_stats.py --all-time
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# GA4 reports nothing before the property existed; this is early enough to
# stand in for "all time" without the API rejecting the range.
ALL_TIME_START = "2020-01-01"


SETUP_HELP = """
No Google Analytics credentials found. Pick one:

  A) Service account (works unattended, needed for CI)
     1. Google Cloud console > IAM & Admin > Service Accounts > Create
     2. On the new account: Keys > Add key > JSON, and save the file
     3. Point GA_SERVICE_ACCOUNT_KEY_PATH at that file in oralcheck-agent/.env
     4. In Google Analytics > Admin > Property access management, add the
        service account's email as a Viewer on the property

  B) Your own login (fastest for local one-off checks)
     gcloud auth application-default login
     ...then leave GA_SERVICE_ACCOUNT_KEY_PATH blank.
"""


def _client():
    from google.analytics.data_v1beta import BetaAnalyticsDataClient

    key_path = os.environ.get("GA_SERVICE_ACCOUNT_KEY_PATH", "").strip()
    scopes = ["https://www.googleapis.com/auth/analytics.readonly"]

    if key_path and not os.path.isfile(key_path):
        raise SystemExit(
            f"GA_SERVICE_ACCOUNT_KEY_PATH points at {key_path}, which does not exist.\n{SETUP_HELP}"
        )

    if key_path:
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
    else:
        import google.auth

        try:
            creds, _ = google.auth.default(scopes=scopes)
        except Exception:
            raise SystemExit(SETUP_HELP)
    return BetaAnalyticsDataClient(credentials=creds)


def _run(client, property_id, start, end, dimensions, metrics, limit=200):
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
    )

    req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit,
    )
    return client.run_report(req)


def collect(property_id: str, start: str, end: str = "today") -> dict:
    client = _client()

    totals = _run(
        client, property_id, start, end,
        dimensions=[],
        metrics=["activeUsers", "newUsers", "sessions", "screenPageViews", "averageSessionDuration"],
    )
    row = totals.rows[0].metric_values if totals.rows else None
    summary = {
        "active_users": int(row[0].value) if row else 0,
        "new_users": int(row[1].value) if row else 0,
        "sessions": int(row[2].value) if row else 0,
        "pageviews": int(row[3].value) if row else 0,
        "avg_session_seconds": round(float(row[4].value), 1) if row else 0.0,
    }

    countries = {}
    for r in _run(client, property_id, start, end, ["country"], ["activeUsers"]).rows:
        name, n = r.dimension_values[0].value, int(r.metric_values[0].value)
        if name and name != "(not set)" and n > 0:
            countries[name] = n

    pages = {}
    for r in _run(client, property_id, start, end, ["pagePath"], ["screenPageViews"], limit=15).rows:
        pages[r.dimension_values[0].value] = int(r.metric_values[0].value)

    # screener_started / screener_completed are fired by the app, so completion
    # rate is real rather than inferred from pageviews.
    events = {}
    for r in _run(client, property_id, start, end, ["eventName"], ["eventCount"], limit=50).rows:
        events[r.dimension_values[0].value] = int(r.metric_values[0].value)

    started = events.get("screener_started", 0)
    completed = events.get("screener_completed", 0)

    return {
        "range": {"start": start, "end": end},
        "summary": summary,
        "countries": dict(sorted(countries.items(), key=lambda x: -x[1])),
        "country_count": len(countries),
        "top_pages": dict(sorted(pages.items(), key=lambda x: -x[1])),
        "events": dict(sorted(events.items(), key=lambda x: -x[1])),
        "screener": {
            "started": started,
            "completed": completed,
            # More completions than starts means the events are miscounting, not
            # that everyone finished. Report nothing rather than a number that
            # would get quoted. (Historic cause: screener_completed re-fired on
            # every view of the results page, including refreshes.)
            "completion_rate": (
                round(completed / started * 100, 1)
                if started and completed <= started else None
            ),
            "reliable": bool(started) and completed <= started,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--all-time", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    property_id = os.environ.get("GA_PROPERTY_ID", "").strip()
    if not property_id:
        print("GA_PROPERTY_ID is not set. See oralcheck-agent/.env.example.", file=sys.stderr)
        return 1

    start = ALL_TIME_START if args.all_time else f"{args.days}daysAgo"
    data = collect(property_id, start)

    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    s = data["summary"]
    label = "all time" if args.all_time else f"last {args.days} days"
    print(f"\nOralCheck traffic ({label})")
    print("=" * 46)
    print(f"  Users            {s['active_users']:,}")
    print(f"  New users        {s['new_users']:,}")
    print(f"  Sessions         {s['sessions']:,}")
    print(f"  Pageviews        {s['pageviews']:,}")
    print(f"  Avg session      {s['avg_session_seconds']:.0f}s")
    print(f"  Countries        {data['country_count']}")

    sc = data["screener"]
    if sc["started"]:
        print(f"\n  Screener started    {sc['started']:,}")
        print(f"  Screener completed  {sc['completed']:,}")
        if sc["reliable"]:
            print(f"  Completion rate     {sc['completion_rate']}%")
        else:
            print("  Completion rate     not reliable (completions exceed starts)")

    print("\nTop countries")
    for name, n in list(data["countries"].items())[:10]:
        print(f"  {name:<28} {n:>6,}")

    print("\nTop pages")
    for path, n in list(data["top_pages"].items())[:10]:
        print(f"  {path:<38} {n:>6,}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
