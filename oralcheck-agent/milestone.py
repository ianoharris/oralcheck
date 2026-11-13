#!/usr/bin/env python3
"""
The 1,000-visitor post: built, scheduled and announced the morning the site's
own count first passes 1,000 (Ian, 12 Nov 2026).

Runs daily from calendar.yml, before the drip. GitHub holds no Analytics key,
so the count comes from oralcheck.org/api/reach, which reads Google Analytics
for the live site only and caches it for an hour. When the count is below the
target it does nothing. The first day it is at or over, it:

  1. renders the reel (anim/milestone.html, voiced by anim.py) with that day's
     countries, states and finished-screener numbers,
  2. adds an Instagram and a LinkedIn entry to the calendar for the next free
     10am Central slot, already approved, and uploads their media to the
     release, so the existing drip (LinkedIn, via Publora) and publish
     (Instagram, direct) jobs post them like any other,
  3. messages Ian on Telegram with the numbers and the time.

It never runs twice: the calendar entries are the record that it has.

    python milestone.py check          # print the count and what it would do
    python milestone.py run            # the daily job
    python milestone.py run --force    # build it now regardless of the count (local test; does not schedule)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import tempfile
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

import httpx

import post_calendar as P

log = logging.getLogger("oralcheck.milestone")

TARGET = 1000
REACH_URL = os.environ.get("REACH_URL", "https://oralcheck.org/api/reach")   # overridable for local tests
ID_PREFIX = "milestone-1000"
SLOT = time(10, 0)   # 10am Central, the calendar's posting time

HASHTAGS = ["oralcancer", "oralhealth", "earlydetection", "cancerawareness", "oralcheck"]


def reach() -> dict:
    r = httpx.get(REACH_URL, timeout=30, headers={"cache-control": "no-cache"})
    r.raise_for_status()
    d = r.json()
    if not d.get("live") or "countries" not in d:
        raise RuntimeError(f"/api/reach has no live Analytics numbers: {d}")
    return d


def done(cal: dict) -> bool:
    return any(e["id"].startswith(ID_PREFIX) for e in cal["entries"])


def next_slot(cal: dict, now: datetime) -> datetime:
    """The next 10am Central from tomorrow on with no other Instagram post that day."""
    taken = {e["date"] for e in cal["entries"] if e["network"] == "instagram" and e["status"] not in ("cut",)}
    day = now.astimezone(P.CT).date() + timedelta(days=1)
    while day.isoformat() in taken:
        day += timedelta(days=1)
    return datetime.combine(day, SLOT, tzinfo=P.CT)


def caption(d: dict) -> str:
    finished = int(round(d["finished"] / 10.0) * 10)
    return (
        "OralCheck just passed 1,000 visitors.\n\n"
        f"They came from {d['countries']} countries and {d['states']} US states, and about {finished} of them "
        "made it all the way through the screener to a result.\n\n"
        "The question that brought the most people here from search was some version of: is this a canker "
        "sore, or something worse? The answer is time. Canker sores heal on their own. A sore, patch or lump "
        "that hasn't healed in two weeks needs a dentist or doctor to look at it.\n\n"
        "Thank you to everyone who checked, and to everyone who sent it to someone else. It is free, private "
        "and takes about two minutes: oralcheck.org\n\n"
        "Counts are from Google Analytics for oralcheck.org. They are a floor: some visits, such as those "
        "with ad blockers, are never counted."
    )


def build_reel(d: dict, out_dir: Path) -> Path:
    import anim
    import oralcheck_agent as A

    spec = anim.milestone_spec(d)
    out = out_dir / "reel.mp4"
    music = A._generate_music_bed(40, "anim-milestone")
    if music is None and A.REEL_MUSIC.exists():
        music = A._loop_music_seamless(str(A.REEL_MUSIC), 42)
    anim.build("milestone", str(out), tts=A._fal_tts, music=music, spec=spec)
    return out


def entries_for(d: dict, when: datetime, reel: Path) -> list[dict]:
    cap = caption(d)
    hook = "A thousand people have now visited OralCheck."
    out = []
    for net, short in (("instagram", "in"), ("linkedin", "li")):
        eid = f"{ID_PREFIX}_{short}_reel"
        folder = P.CAL_DIR / eid
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy(reel, folder / "reel.mp4")
        (folder / "manifest.json").write_text(json.dumps({
            "id": eid, "created_at": datetime.now(P.CT).isoformat(), "pillar": "screener_cta", "media_type": "reel",
            "hook": hook, "caption": cap, "hashtags": HASHTAGS, "files": ["reel.mp4"], "slides": [], "status": "pending",
        }, indent=2))
        out.append({
            "id": eid, "date": when.date().isoformat(), "network": net, "media_type": "reel",
            "when": when.astimezone(timezone.utc).isoformat(),
            "status": "approved",
            "idea": {"title": "1,000 visitors: what they came asking", "hook": hook,
                     "brief": "Milestone reel, built automatically by milestone.py from /api/reach on the day the count passed 1,000.",
                     "topic": "milestone", "shape": "story", "hook_style": "statement", "tone": "calm",
                     "pillar": "screener_cta", "media_type": "reel", "calendar_ref": None, "slug": "1000-visitors"},
            "event": {"slug": "milestone-1000", "name": "1,000 visitors", "date": when.date().isoformat()},
            "folder": eid, "version": 1, "uploaded": False, "hook": hook, "caption": cap, "hashtags": HASHTAGS,
            "files": ["reel.mp4"], "review_note": "",
            "notes": [f"Built {datetime.now(P.CT):%d %b %Y} from /api/reach: {json.dumps(d)}"],
        })
    return out


def tell_ian(text: str) -> None:
    try:
        import telegram_review as T
        T.tg("sendMessage", chat_id=T.TELEGRAM_CHAT_ID, text=text)
    except Exception as exc:  # noqa: BLE001
        log.warning("Telegram message not sent: %s", exc)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "run"])
    ap.add_argument("--force", action="store_true", help="build the reel now regardless of the count; never schedules")
    args = ap.parse_args()

    cal = P.load()
    try:
        d = reach()
    except Exception as exc:  # noqa: BLE001
        # Never block the daily drip over a missing count; try again tomorrow.
        log.warning("Could not read the visitor count: %s", exc)
        print("count unavailable")
        return 0
    now = datetime.now(P.CT)
    log.info("Live count %s (target %s); %s countries, %s states, %s finished", d["users"], TARGET, d["countries"], d["states"], d["finished"])

    if args.cmd == "check":
        if done(cal):
            print("already built and scheduled")
        elif d["users"] >= TARGET:
            print(f"would build now and schedule for {next_slot(cal, now):%a %d %b %I:%M %p %Z}")
        else:
            print(f"{TARGET - d['users']} to go")
        return 0

    if args.force:
        out = Path(tempfile.mkdtemp(prefix="milestone_"))
        reel = build_reel({**d, "users": max(TARGET, d["users"])}, out)
        print(f"Test render (not scheduled): {reel}")
        return 0

    if done(cal) or d["users"] < TARGET:
        log.info("Nothing to do.")
        return 0

    when = next_slot(cal, now)
    reel = build_reel(d, Path(tempfile.mkdtemp(prefix="milestone_")))
    cal["entries"].extend(entries_for(d, when, reel))
    cal["entries"].sort(key=lambda e: e["when"])
    P.save(cal)
    P.upload_approved()
    tell_ian(f"OralCheck passed {TARGET:,} visitors ({d['users']:,} today). The thank-you reel is built and scheduled "
             f"for Instagram and LinkedIn at {when:%a %d %b, %I:%M %p} Central: {d['countries']} countries, "
             f"{d['states']} states, about {int(round(d['finished'] / 10.0) * 10)} finished screeners. "
             "To stop it, tell Claude before then.")
    log.info("Scheduled the 1,000 reel for %s", when.isoformat())
    return 0


if __name__ == "__main__":
    sys.exit(main())
