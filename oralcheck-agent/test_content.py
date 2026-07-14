#!/usr/bin/env python3
"""
Unit tests for the content calendar and idea ledger (the non-API logic).

Run:  python3.11 test_content.py   ->  exit 0 all pass, 1 on failure.
"""

import sys
from datetime import date

import content_calendar as C
import ideas as I

_fails = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        _fails.append(name)


# --- Calendar --------------------------------------------------------------
def test_calendar():
    # World Head & Neck Cancer Day is July 27
    evs = {e["slug"]: e for e in C.upcoming(within_days=30, today=date(2026, 7, 10))}
    check("whncd surfaces mid-July", evs.get("world-head-neck-cancer-day", {}).get("days_until") == 17)

    # April is Oral Cancer Awareness Month; on Apr 15 it is active now (0 days)
    apr = {e["slug"]: e for e in C.upcoming(within_days=30, today=date(2026, 4, 15))}
    check("awareness month active in April", apr.get("oral-cancer-awareness-month", {}).get("days_until") == 0)

    # Great American Smokeout = 3rd Thursday of November 2026 -> Nov 19
    gaso = C.next_occurrence(
        {"rule": {"type": "nth-weekday", "month": 11, "weekday": 3, "n": 3}}, date(2026, 11, 1))
    check("nth-weekday resolves (Nov 19 2026)", gaso == date(2026, 11, 19))

    # Nothing within 5 days of a quiet date
    quiet = C.upcoming(within_days=5, today=date(2026, 6, 10))
    check("quiet window empty", quiet == [])


# --- Ledger / ideas --------------------------------------------------------
def test_slugify():
    check("slugify basic", I.slugify("HPV Is the Leading Cause!") == "hpv-is-the-leading-cause")
    check("slugify collapses", I.slugify("A  --  B") == "a-b")


def test_ledger_flow():
    ledger = {"ideas": [], "last_batch": []}
    fresh = [
        {"title": "Stat one", "slug": "stat-one", "pillar": "stats",
         "media_type": "carousel", "brief": "b", "angle": "surprising-true", "calendar_ref": None},
        {"title": "Myth two", "slug": "myth-two", "pillar": "myth_busting",
         "media_type": "image", "brief": "b", "angle": "myth", "calendar_ref": None},
    ]
    ledger = I.record_suggested(ledger, fresh)
    check("record assigns batch", len(ledger["last_batch"]) == 2)
    check("all suggested", all(i["status"] == "suggested" for i in ledger["ideas"]))

    chosen = I.select(ledger, [1])
    check("select returns one", len(chosen) == 1 and chosen[0]["title"] == "Stat one")
    check("selected status set", ledger["ideas"][0]["status"] == "selected")

    # Used slug is now off-limits; avoid list includes it
    check("used slug tracked", "stat-one" in I._used_slugs(ledger))
    check("avoid includes used", "Stat one" in I._avoid_titles(ledger))

    I.mark_queued(ledger, ledger["ideas"][0]["id"], "manifest_123")
    check("mark_queued sets status", ledger["ideas"][0]["status"] == "queued")
    check("mark_queued records manifest", ledger["ideas"][0]["manifest_id"] == "manifest_123")

    # Out-of-range picks are ignored, not crashing
    check("out-of-range pick ignored", I.select(ledger, [99]) == [])


def test_coerce():
    good = I._coerce({"title": "T", "pillar": "stats", "media_type": "carousel",
                      "brief": "b", "angle": "a"}, {"stats"})
    check("coerce keeps valid", good is not None and good["media_type"] == "carousel")
    bad_media = I._coerce({"title": "T", "media_type": "hologram", "pillar": "stats"}, {"stats"})
    check("coerce fixes bad media", bad_media["media_type"] == "carousel")
    reel_ok = I._coerce({"title": "T", "media_type": "reel", "pillar": "stats"}, {"stats"})
    check("coerce keeps reel", reel_ok["media_type"] == "reel")
    bad_pillar = I._coerce({"title": "T", "pillar": "nope"}, {"stats"})
    check("coerce fixes bad pillar", bad_pillar["pillar"] == "stats")
    check("coerce drops empty title", I._coerce({"title": ""}, {"stats"}) is None)


def main():
    print("Calendar:");      test_calendar()
    print("Slugify:");       test_slugify()
    print("Ledger flow:");   test_ledger_flow()
    print("Coerce:");        test_coerce()
    if _fails:
        print(f"\n  {len(_fails)} FAILURE(S): {', '.join(_fails)}")
        return 1
    print("\n  All content-logic checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
