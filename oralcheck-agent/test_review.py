#!/usr/bin/env python3
"""
Review-flow tests: ordering, stale pruning, slot spacing, and messaging.

Telegram and Publora are stubbed, so this runs offline in CI. It covers the
behaviours that were actually wrong in production and would otherwise only be
noticed mid-review on a phone:

  * posts arriving in queue order instead of carousel-first
  * two-month-old drafts still marked pending and leading the batch
  * "Rejected." with no way to tell which post it meant
  * a top-up run booking a day that already has a post

Run:  python3.11 test_review.py
Exit code 0 = all good, 1 = one or more failures.
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

# telegram_review reads these at import time and raises KeyError without them.
# The CI verify step deliberately has no secrets, and locally a .env supplies
# them, so this file passed on a laptop and took the whole workflow down on the
# runner. setdefault, not assignment: a real token in the environment is left
# alone, and every network call is stubbed below regardless.
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "test-chat")

import telegram_review as T  # noqa: E402

QUEUE = Path(tempfile.mkdtemp(prefix="oralcheck_review_"))
SENT: list[tuple[str, str]] = []
DECISIONS: dict[str, str] = {}
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:34} {detail}")
    if not ok:
        FAILURES.append(name)


# --- stubs -----------------------------------------------------------------
# SCHEDULE_FILE is redirected before anything can call record_slot. Without this
# the tests append to the real ledger and every run shifts the live schedule.
T.QUEUE_DIR = QUEUE
T.SCHEDULE_FILE = QUEUE / "schedule.json"
T.PUBLORA_API_KEY = "stub"
T.LINKEDIN_HANDOFF = False
T.APPROVAL_TIMEOUT = 30

_mid = [1000]


def _fake_tg(method, **kw):
    SENT.append((method, kw.get("text", "")))
    _mid[0] += 1
    return {"result": {"message_id": _mid[0]}}


T.tg = _fake_tg
T.tg_upload = lambda *a, **k: SENT.append(("upload", "")) or {"result": {}}
T.tg_media_group = lambda *a, **k: SENT.append(("album", "")) or {"result": {}}
T.post_via_publora = lambda m, f, when=None: f"pg_{m['id'][-3:]}"
T._collect_reject_reason = lambda m: "too generic"
T._await_one = lambda manifest, item_dir, deadline: DECISIONS.get(manifest["id"], "approve")


class _Ledger:
    """Minimal stand-in: no spare ideas, so rejection ends the round."""
    def load_ledger(self): return {}
    def save_ledger(self, l): pass
    def idea_for_manifest(self, l, p): return None
    def record_feedback(self, *a, **k): pass
    def mark_rejected(self, *a): pass
    def spare_ideas(self, l): return []


T.ideas = _Ledger()


def make_post(name: str, media_type: str, hook: str, days_ago: int = 0) -> str:
    stamp = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y%m%d_%H%M%S")
    d = QUEUE / f"{stamp}_{name}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "image.jpg").write_bytes(b"x")
    (d / "manifest.json").write_text(json.dumps({
        "id": d.name, "media_type": media_type, "hook": hook, "caption": "c",
        "hashtags": [], "files": ["image.jpg"], "status": "pending", "pillar": "stats"}))
    return d.name


def reset() -> None:
    for child in QUEUE.iterdir():
        shutil.rmtree(child, ignore_errors=True) if child.is_dir() else child.unlink()
    SENT.clear()
    DECISIONS.clear()


def main() -> int:
    print("\nReview flow:")

    # Format ordering. Directory names sort image < reel < carousel here, so
    # queue order and review order genuinely disagree.
    reset()
    make_post("aaa", "image", "an image post")
    make_post("bbb", "reel", "a reel post")
    make_post("ccc", "carousel", "a carousel post")
    order = [m["media_type"] for m, _ in T.get_all_pending()]
    check("carousel reviewed first", order == ["carousel", "reel", "image"], str(order))

    # Serial review: one post on screen at a time, each scheduled before the next.
    reset()
    make_post("aaa", "image", "an image post")
    make_post("ccc", "carousel", "a carousel post")
    T.review_batch()
    sends = [t for m, t in SENT if m == "sendMessage"]
    captions = [t for t in sends if t.startswith("*Post ")]
    check("every post gets buttons", len(captions) == 2, f"{len(captions)} sent")
    check("scheduled in format order",
          "carousel" in "".join(sends[:4]) and sends[0].startswith("2 post(s)"))

    # Progress: a slow publish announces itself, then edits into the outcome.
    check("slow step announces itself",
          any(t.startswith("Uploading and scheduling") for m, t in SENT if m == "sendMessage"))
    check("outcome replaces the status",
          sum(1 for m, _ in SENT if m == "editMessageText") == 2)

    # Rejection names the post.
    reset()
    pid = make_post("rej", "carousel", "a carousel nobody wanted")
    DECISIONS[pid] = "reject"
    T.review_batch()
    rejects = [t for m, t in SENT if t.startswith("Rejected ")]
    check("rejection names the post",
          bool(rejects) and "a carousel nobody wanted" in rejects[0],
          rejects[0].split("\n")[0] if rejects else "no message")

    # Stale pruning.
    reset()
    make_post("old", "carousel", "a stale June draft", days_ago=60)
    make_post("new", "carousel", "this week's draft")
    kept = [m["hook"] for m, _ in T.get_all_pending()]
    check("stale drafts pruned", kept == ["this week's draft"], str(kept))

    print("\nSlot spacing:")
    base = datetime.now(timezone.utc)

    def book(*days: int) -> None:
        T.SCHEDULE_FILE.write_text(json.dumps({"slots": [
            (base + timedelta(days=d)).replace(hour=T.POST_HOUR, minute=0, second=0,
                                               microsecond=0).isoformat() for d in days]}))

    def offsets(slots) -> list[int]:
        return sorted((s.date() - base.date()).days for s in slots)

    book()
    check("fresh week of 3 spreads evenly", offsets(T._weekly_slots(3)) == [1, 4, 7])

    book(1)
    got = offsets(T._weekly_slots(2))
    check("top-up avoids the booked day", 1 not in got, f"booked day 1, got {got}")
    check("top-up spaces against it", got == [4, 7], str(got))

    book(*range(1, 8))
    full = T._weekly_slots(2)
    check("full week still yields distinct times", len(set(full)) == 2)

    # record_slot must persist, or the next run repeats this one's days.
    T.SCHEDULE_FILE.write_text(json.dumps({"slots": []}))
    when = (base + timedelta(days=3)).replace(hour=T.POST_HOUR, minute=0,
                                              second=0, microsecond=0)
    T.record_slot(when)
    check("approved slot is remembered", T._booked() == [when])

    shutil.rmtree(QUEUE, ignore_errors=True)
    if FAILURES:
        print(f"\n  {len(FAILURES)} check(s) failed: {', '.join(FAILURES)}")
        return 1
    print("\n  All review-flow checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
