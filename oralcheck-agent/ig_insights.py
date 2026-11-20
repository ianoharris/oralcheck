#!/usr/bin/env python3
"""
Read-only export of Instagram insights for every post on the account, for
growth analysis (Ian, 20 Nov 2026). Publishes and changes nothing.

The token lives only in GitHub secrets, so this runs from the
"Export Instagram insights" workflow. The repo is public, so the workflow
encrypts the output to a public key passed in at dispatch and uploads only the
ciphertext; the matching private key never leaves the Mac that asked for it.

    python ig_insights.py out.json
"""
from __future__ import annotations

import json
import sys

import meta_ig as M

FIELDS = "id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count"
# Asked for one at a time: Meta rejects the whole call if any one metric is
# not offered for that media type or API version.
REEL = ["views", "reach", "saved", "shares", "likes", "comments", "total_interactions",
        "ig_reels_avg_watch_time", "ig_reels_video_view_total_time", "reels_skip_rate", "follows",
        "profile_visits", "profile_activity"]
OTHER = ["views", "reach", "saved", "shares", "likes", "comments", "total_interactions", "follows",
         "profile_visits", "profile_activity"]


def metric(media_id: str, name: str):
    try:
        d = M._get(f"{media_id}/insights", metric=name)
    except M.MetaError as exc:
        return {"error": str(exc)[:160]}
    rows = d.get("data") or []
    if not rows:
        return None
    r = rows[0]
    if "values" in r:
        return r["values"][0].get("value")
    return r.get("total_value", {}).get("value")


def main() -> int:
    acct = M.account()
    media, after = [], None
    while True:
        params = {"fields": FIELDS, "limit": 50}
        if after:
            params["after"] = after
        page = M._get(f"{acct['id']}/media", **params)
        media += page.get("data", [])
        after = (page.get("paging") or {}).get("cursors", {}).get("after")
        if not after or not (page.get("paging") or {}).get("next"):
            break
    for m in media:
        names = REEL if m.get("media_product_type") == "REELS" else OTHER
        m["insights"] = {n: metric(m["id"], n) for n in names}
    acct_ins = {}
    for n in ("follower_count", "reach", "profile_views", "website_clicks", "accounts_engaged"):
        try:
            extra = {} if n == "follower_count" else {"metric_type": "total_value"}
            acct_ins[n] = M._get(f"{acct['id']}/insights", metric=n, period="day", **extra)
        except M.MetaError as exc:
            acct_ins[n] = {"error": str(exc)[:160]}
    try:
        prof = M._get(acct["id"], fields="followers_count,follows_count,media_count")
    except M.MetaError as exc:
        prof = {"error": str(exc)[:160]}
    json.dump({"account": acct, "profile": prof, "account_insights": acct_ins, "media": media},
              open(sys.argv[1], "w"), indent=1)
    print(f"{len(media)} posts exported")   # counts only; the data stays encrypted
    return 0


if __name__ == "__main__":
    sys.exit(main())
