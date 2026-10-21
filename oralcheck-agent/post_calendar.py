"""
A posting calendar: weeks of posts built up front, reviewed once, released on schedule.

The weekly flow (Monday ideas, pick in Telegram, review in Telegram) depended
on Ian answering within GitHub's 6-hour job limit, and twice in October it ran
out of time and lost the week. The calendar replaces it: a batch of posts is
planned, written and rendered in one sitting, Ian reviews the lot on one page,
and a small daily job hands each approved post to Publora a few days before
its date. Publora's plan holds three scheduled posts at a time, so the drip
never schedules further ahead than that allows.

    python post_calendar.py plan --start 2026-10-26 --weeks 10    # dates, formats, topics, ideas
    python post_calendar.py build                                  # render every post (resumable)
    python post_calendar.py drip                                   # daily: schedule what is due

Everything lives in calendar/: calendar.json (the plan and each post's status)
and one folder per post with its media and manifest. Statuses:
planned -> built -> approved | redo | cut -> scheduled.
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

log = logging.getLogger("oralcheck.calendar")

HERE = Path(__file__).parent
CAL_DIR = HERE / "calendar"
CAL_FILE = CAL_DIR / "calendar.json"
CT = ZoneInfo("America/Chicago")

IG_HOUR_CT = 17          # Instagram posts at 5pm Central, as the weekly flow did
LI_HOUR_CT = 9           # LinkedIn at 9am Central
DRIP_DAYS = 3            # schedule a post this many days before it goes out
RELEASE = "calendar-2026-fall"   # GitHub release holding approved posts' media for CI

# Awareness days pinned to a date in the window, with the topic that fits.
PINNED = {
    "great-american-smokeout": ("quitting", "Great American Smokeout"),
    "dental-hygiene-month": ("dentist_screening", "National Dental Hygiene Month"),
    "new-year-screening": ("monthly_self_exam", "New Year"),
}


def load() -> dict:
    if CAL_FILE.exists():
        return json.loads(CAL_FILE.read_text())
    return {"entries": []}


def save(cal: dict) -> None:
    CAL_DIR.mkdir(parents=True, exist_ok=True)
    CAL_FILE.write_text(json.dumps(cal, indent=2))


def _at(day: date, hour: int) -> str:
    """A Central-time wall clock time, stored as UTC (so DST is handled)."""
    return datetime(day.year, day.month, day.day, hour, tzinfo=CT).astimezone(timezone.utc).isoformat()


def plan_dates(start: date, weeks: int) -> list[dict]:
    """Three posts a week: Instagram Tuesday and Friday, LinkedIn Wednesday.

    Each week carries one reel (Instagram only, alternating Tuesday and
    Friday), and the other two slots alternate carousel and image, so the
    batch comes out 10 reels, 10 carousels, 10 images over ten weeks.
    """
    monday = start - timedelta(days=start.weekday())
    out = []
    for w in range(weeks):
        wk = monday + timedelta(weeks=w)
        reel_on_tue = w % 2 == 0
        ig_post = "carousel" if w % 2 == 0 else "image"
        li_post = "image" if w % 2 == 0 else "carousel"
        out.append({"date": wk + timedelta(days=1), "network": "instagram", "media_type": "reel" if reel_on_tue else ig_post})
        out.append({"date": wk + timedelta(days=2), "network": "linkedin", "media_type": li_post})
        out.append({"date": wk + timedelta(days=4), "network": "instagram", "media_type": ig_post if reel_on_tue else "reel"})
    for e in out:
        e["when"] = _at(e["date"], IG_HOUR_CT if e["network"] == "instagram" else LI_HOUR_CT)
        e["date"] = e["date"].isoformat()
    return out


def plan(start: date, weeks: int) -> dict:
    import content_calendar
    import ideas
    import oralcheck_agent as A
    import topics

    slots = plan_dates(start, weeks)
    ledger = ideas.load_ledger()
    assigned = topics.plan_slots(ledger, [s["media_type"] for s in slots])
    if len(assigned) != len(slots):
        raise RuntimeError(f"planned {len(assigned)} topics for {len(slots)} dates")

    # Awareness days: move the fitting topic onto the post nearest the day.
    end = date.fromisoformat(slots[-1]["date"])
    events = [e for e in content_calendar.upcoming(within_days=(end - start).days + 7, today=start)
              if e["slug"] in PINNED]
    for ev in events:
        day = date.fromisoformat(ev["date"])
        k = min(range(len(slots)), key=lambda i: (abs((date.fromisoformat(slots[i]["date"]) - day).days),
                                                  slots[i]["media_type"] == "reel"))
        topic, name = PINNED[ev["slug"]]
        j = next((i for i, a in enumerate(assigned) if a["topic"] == topic), None)
        if j is not None and j != k and assigned[j]["media_type"] == assigned[k]["media_type"]:
            assigned[j], assigned[k] = assigned[k], assigned[j]
        elif j is None or assigned[j]["media_type"] != assigned[k]["media_type"]:
            fresh = topics.plan_slots({"ideas": []}, [slots[k]["media_type"]], seed=k)
            if fresh:
                assigned[k] = {**fresh[0], "topic": topic, "pillar": topics.TOPICS[topic]["pillar"]}
        # A topic moved onto another slot may not suit that slot's shape (the
        # first run put quitting into a two-week-rule timeline, and the post
        # came out about sores). Give it a shape its tags can carry.
        shapes = topics.SHAPES[assigned[k]["media_type"]]
        need = shapes.get(assigned[k]["shape"], {}).get("needs")
        if need and need not in topics.TOPICS[topic]["tags"]:
            assigned[k]["shape"] = next(n for n, sh in shapes.items()
                                        if sh["needs"] is None or sh["needs"] in topics.TOPICS[topic]["tags"])
        assigned[k]["event"] = {"slug": ev["slug"], "name": name, "date": ev["date"]}
        if day.weekday() == 3 and slots[k]["network"] == "instagram":   # Smokeout is a Thursday: post on the day
            slots[k]["date"] = day.isoformat()
            slots[k]["when"] = _at(day, IG_HOUR_CT)

    # Write every idea: one model call per format, events written on their own.
    entries = []
    by_media: dict[str, list[int]] = {}
    for i, a in enumerate(assigned):
        if not a.get("event"):
            by_media.setdefault(a["media_type"], []).append(i)
    written: dict[int, dict] = {}
    common = dict(api_key=A.ANTHROPIC_API_KEY, model=A.CONTENT_MODEL, system_prompt=A.SYSTEM_PROMPT,
                  pillar_briefs=A.PILLAR_BRIEFS, ledger=ledger)
    for media, idxs in by_media.items():
        got = ideas.generate_ideas(len(idxs), calendar_events=[], slots=[assigned[i] for i in idxs], **common)
        by_topic = {g["topic"]: g for g in got}
        for i in idxs:
            if assigned[i]["topic"] in by_topic:
                written[i] = by_topic[assigned[i]["topic"]]
    for i, a in enumerate(assigned):
        if a.get("event"):
            ev = next(e for e in events if e["slug"] == a["event"]["slug"])
            got = ideas.generate_ideas(1, calendar_events=[{**ev, "days_until": 0}], slots=[a], **common)
            if got:
                written[i] = got[0]
                written[i]["calendar_ref"] = a["event"]["slug"]
    missing = [i for i in range(len(slots)) if i not in written]
    if missing:
        log.warning("%d slot(s) came back without an idea; retrying them once.", len(missing))
        for i in missing:
            got = ideas.generate_ideas(1, calendar_events=[], slots=[assigned[i]], **common)
            if got:
                written[i] = got[0]

    for i, s in enumerate(slots):
        idea = written.get(i)
        if not idea:
            raise RuntimeError(f"no idea for {s['date']} {s['media_type']}")
        entries.append({
            "id": f"{s['date']}_{s['network'][:2]}_{s['media_type']}",
            **s, "status": "planned",
            "idea": {k: idea.get(k) for k in ("title", "hook", "brief", "topic", "shape", "hook_style",
                                               "tone", "pillar", "media_type", "calendar_ref", "slug")},
            "event": assigned[i].get("event"),
        })
    cal = {"created": datetime.now(timezone.utc).isoformat(), "start": start.isoformat(),
           "weeks": weeks, "entries": entries}
    save(cal)

    # The ledger records these as used, so the rotation keeps moving after the batch.
    ledger = ideas.record_suggested(ledger, [{**e["idea"], "media_type": e["media_type"]} for e in entries])
    for rec in ledger["ideas"][-len(entries):]:
        rec["status"] = "selected"
    ideas.save_ledger(ledger)
    return cal


def build(only: str | None = None) -> None:
    """Render every planned post. Resumable: built posts are skipped."""
    import oralcheck_agent as A

    cal = load()
    for e in cal["entries"]:
        if only and e["id"] != only:
            continue
        if e["status"] not in ("planned", "redo"):
            continue
        log.info("Building %s: %s", e["id"], e["idea"]["title"])
        idea = dict(e["idea"])
        if e["status"] == "redo" and e.get("review_note"):
            idea["brief"] += ("\n\nThe last version of this post was sent back with this note. "
                              f"Address it: {e['review_note']}")
        try:
            manifest = A._queue_idea(idea)
        except Exception as exc:  # noqa: BLE001
            log.exception("Build failed for %s (%s); it stays planned.", e["id"], exc)
            e["error"] = str(exc)[:300]
            save(cal)
            continue
        src = A.QUEUE_DIR / manifest["id"]
        dst = CAL_DIR / e["id"]
        if dst.exists():
            shutil.rmtree(dst)
        shutil.move(str(src), str(dst))
        e.update(status="built", folder=e["id"], version=(e.get("version") or (1 if e.get("folder") else 0)) + 1, uploaded=False, hook=manifest.get("hook"), caption=manifest.get("caption"),
                 hashtags=manifest.get("hashtags", []), files=manifest.get("files", []))
        e.pop("error", None)
        save(cal)
        log.info("Built %s", e["id"])


def _gh(*args: str) -> None:
    import subprocess
    subprocess.run(["gh", *args], check=True, cwd=HERE)


def upload_approved() -> int:
    """Put approved posts' media and manifests on the release CI downloads from.

    Media stays out of git: ten weeks of reels and carousels is ~100 MB, and
    a release keeps it out of every clone's history. Only approved posts go up.
    Asset names are "<entry id>__<file name>".
    """
    import subprocess
    cal = load()
    exists = subprocess.run(["gh", "release", "view", RELEASE], cwd=HERE, capture_output=True).returncode == 0
    if not exists:
        _gh("release", "create", RELEASE, "--title", "Posting calendar, autumn 2026",
            "--notes", "Media for approved calendar posts. Used by .github/workflows/calendar.yml.")
    n = 0
    for e in cal["entries"]:
        if e["status"] != "approved" or e.get("uploaded"):
            continue
        folder = CAL_DIR / e["folder"]
        staged = []
        for f in ["manifest.json", *[x for x in e.get("files", []) if x != "preview.jpg"]]:
            tmp = folder / f"{e['id']}__{f}"
            shutil.copy(folder / f, tmp)
            staged.append(str(tmp))
        try:
            _gh("release", "upload", RELEASE, *staged, "--clobber")
        finally:
            for t in staged:
                Path(t).unlink(missing_ok=True)
        e["uploaded"] = True
        save(cal)
        n += 1
    return n


def _ensure_media(e: dict) -> Path:
    """The post's folder, downloading it from the release when absent (CI)."""
    folder = CAL_DIR / (e.get("folder") or e["id"])
    if (folder / "manifest.json").exists():
        return folder
    folder.mkdir(parents=True, exist_ok=True)
    _gh("release", "download", RELEASE, "--pattern", f"{e['id']}__*", "--dir", str(folder), "--clobber")
    for f in folder.iterdir():
        if f.name.startswith(e["id"] + "__"):
            f.rename(folder / f.name.split("__", 1)[1])
    return folder


def drip(now: datetime | None = None, dry_run: bool = False) -> list[str]:
    """Schedule approved posts that are due within DRIP_DAYS. Returns their ids."""
    import telegram_review as T

    now = now or datetime.now(timezone.utc)
    cal = load()
    done = []
    for e in cal["entries"]:
        if e["status"] != "approved":
            continue
        when = datetime.fromisoformat(e["when"])
        if when < now:
            log.warning("%s was approved but its date has passed; leaving it for a decision.", e["id"])
            continue
        if when - now > timedelta(days=DRIP_DAYS):
            continue
        if dry_run:
            log.info("Would schedule %s for %s on %s", e["id"], e["when"], e["network"])
            continue
        folder = _ensure_media(e)
        manifest = json.loads((folder / "manifest.json").read_text())
        media = [folder / f for f in manifest["files"] if f != "preview.jpg"]
        gid = T.post_via_publora(manifest, media, when=when, networks=[e["network"]])
        e.update(status="scheduled", publora_id=gid, scheduled_at=now.isoformat())
        save(cal)
        T.record_slot(when)
        done.append(e["id"])
        log.info("Scheduled %s (%s) for %s", e["id"], e["network"], e["when"])
        if e["media_type"] == "reel":
            T.tg("sendMessage", chat_id=T.TELEGRAM_CHAT_ID,
                 text=(f"Reel scheduled for {when.astimezone(CT):%a %d %b, %-I%p} CT: {e['idea']['title']}.\n"
                       "Once it is live, share it to your Story with a link sticker to oralcheck.org."))
    return done


REVIEW_DIR = CAL_DIR / "review"


def _review_media(e: dict, out: Path) -> list[dict]:
    """Small review copies of a built post's media. Returns [{type, src, poster?}]."""
    import subprocess
    from PIL import Image

    folder = CAL_DIR / e["folder"]
    dest = out / "m" / e["id"]
    dest.mkdir(parents=True, exist_ok=True)
    items = []
    for n, f in enumerate(x for x in e.get("files", []) if x != "preview.jpg"):
        src = folder / f
        if src.suffix == ".mp4":
            vid, poster = dest / f"{n}.mp4", dest / f"{n}.jpg"
            if not vid.exists():
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", "scale=540:-2",
                                "-c:v", "libx264", "-crf", "30", "-preset", "veryfast", "-c:a", "aac", "-b:a", "96k",
                                "-movflags", "+faststart", str(vid)], check=True)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", str(src), "-frames:v", "1",
                                "-vf", "scale=540:-2", str(poster)], check=True)
            items.append({"type": "video", "src": f"m/{e['id']}/{n}.mp4", "poster": f"m/{e['id']}/{n}.jpg"})
        else:
            img = dest / f"{n}.jpg"
            if not img.exists():
                im = Image.open(src).convert("RGB")
                im.thumbnail((540, 675))
                im.save(img, "JPEG", quality=82)
            items.append({"type": "image", "src": f"m/{e['id']}/{n}.jpg"})
    return items


def review_page() -> Path:
    """Write calendar/review/: index.html plus review copies of every built post."""
    cal = load()
    out = REVIEW_DIR
    out.mkdir(parents=True, exist_ok=True)
    posts = []
    for e in cal["entries"]:
        when = datetime.fromisoformat(e["when"]).astimezone(CT)
        posts.append({
            "id": e["id"], "date": e["date"], "label": f"{when:%a %-d %b} \u00b7 {when:%-I%p}".replace("AM", "am").replace("PM", "pm"),
            "week": (date.fromisoformat(e["date"]) - timedelta(days=date.fromisoformat(e["date"]).weekday())).isoformat(),
            "network": e["network"], "format": e["media_type"], "title": e["idea"]["title"],
            "hook": e.get("hook") or e["idea"].get("hook", ""), "caption": e.get("caption", ""),
            "hashtags": e.get("hashtags", []), "event": (e.get("event") or {}).get("name"),
            "built": e["status"] not in ("planned",), "v": e.get("version", 1), "media": _review_media(e, out) if e.get("folder") else [],
        })
    template = (HERE / "calendar_review.html").read_text()
    (out / "index.html").write_text(template.replace("/*__POSTS__*/[]", json.dumps(posts, ensure_ascii=False)))
    return out


def apply_decisions(rows: list[dict]) -> dict:
    """Copy review-page decisions ({id, decision, note}) onto the calendar."""
    cal = load()
    by_id = {e["id"]: e for e in cal["entries"]}
    counts: dict[str, int] = {}
    for r in rows:
        e = by_id.get(r.get("id"))
        if not e or e["status"] == "scheduled" or r.get("decision") not in ("approve", "redo", "cut"):
            continue
        if (r.get("v") or 1) != e.get("version", 1):
            continue  # a decision about a version that has since been rebuilt
        e["status"] = {"approve": "approved", "redo": "redo", "cut": "cut"}[r["decision"]]
        e["review_note"] = (r.get("note") or "").strip()
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    save(cal)
    return counts


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("--start", required=True); p.add_argument("--weeks", type=int, default=10)
    b = sub.add_parser("build"); b.add_argument("--only")
    d = sub.add_parser("drip"); d.add_argument("--dry-run", action="store_true")
    sub.add_parser("review")
    sub.add_parser("upload")
    args = ap.parse_args()
    if args.cmd == "plan":
        cal = plan(date.fromisoformat(args.start), args.weeks)
        for e in cal["entries"]:
            print(f"{e['date']}  {e['network']:9s} {e['media_type']:8s} {e['idea']['title']}")
    elif args.cmd == "build":
        build(args.only)
    elif args.cmd == "review":
        print(review_page())
    elif args.cmd == "upload":
        print(f"uploaded {upload_approved()} post(s)")
    else:
        print(drip(dry_run=args.dry_run))


if __name__ == "__main__":
    sys.exit(main())
