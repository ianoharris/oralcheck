"""
Idea suggestion + ledger for OralCheck.

Generates numbered content ideas across pillars and the awareness calendar, and
keeps a persistent ledger so an idea that has been used (selected or posted) is
never suggested again, and recent suggestions do not repeat week to week.

Dependency direction is one-way: the agent imports this module and passes in the
shared brand constants. This module never imports the agent.
"""

import json
import re
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic

LEDGER_FILE = Path(__file__).parent / "ideas.json"

VALID_MEDIA = {"carousel", "image", "infographic"}
# Extra pillars beyond the core rotation.
EXTRA_PILLARS = {
    "awareness": "A branded post tied to a specific awareness day or holiday from the content calendar.",
    "light_lane": (
        "A lighter, more human or gently witty take that still respects the subject. "
        "Never a joke at the expense of patients or the disease. Warmth and relatability, "
        "not shock. This lane always goes to manual review."
    ),
}


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:60]


def load_ledger() -> dict:
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE) as f:
            data = json.load(f)
            data.setdefault("ideas", [])
            data.setdefault("last_batch", [])
            return data
    return {"ideas": [], "last_batch": []}


def save_ledger(ledger: dict) -> None:
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)


USED_STATUSES = ("selected", "queued", "posted")


def _used_slugs(ledger: dict) -> set[str]:
    """Slugs that must never be suggested again (picked, queued, or posted)."""
    return {i["slug"] for i in ledger["ideas"] if i.get("status") in USED_STATUSES}


def _avoid_titles(ledger: dict, fresh_days: int = 45) -> list[str]:
    """Titles to steer the model away from: anything used, plus recent suggestions."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=fresh_days)
    out = []
    for i in ledger["ideas"]:
        if i.get("status") in USED_STATUSES:
            out.append(i["title"])
            continue
        try:
            ts = datetime.fromisoformat(i.get("suggested_at", ""))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                out.append(i["title"])
        except ValueError:
            pass
    return out


def _coerce(idea: dict, valid_pillars: set[str]) -> dict | None:
    title = str(idea.get("title", "")).strip()
    if not title:
        return None
    media = str(idea.get("media_type", "carousel")).lower().strip()
    if media not in VALID_MEDIA:
        media = "carousel"
    pillar = str(idea.get("pillar", "")).lower().strip()
    if pillar not in valid_pillars:
        pillar = "stats"
    return {
        "title": title,
        "pillar": pillar,
        "media_type": media,
        "brief": str(idea.get("brief", "")).strip(),
        "angle": str(idea.get("angle", "")).strip(),
        "calendar_ref": idea.get("calendar_ref") or None,
    }


def generate_ideas(count, *, api_key, model, system_prompt, pillar_briefs,
                   calendar_events, ledger) -> list[dict]:
    """Ask the model for `count` fresh ideas, filtered against the ledger.

    Returns coerced idea dicts (not yet written to the ledger).
    """
    all_pillars = {**{p: pillar_briefs[p] for p in pillar_briefs}, **EXTRA_PILLARS}
    valid_pillars = set(all_pillars.keys())

    pillar_lines = "\n".join(f"  - {p}: {desc}" for p, desc in all_pillars.items())
    avoid = _avoid_titles(ledger)
    avoid_block = ("\nDo NOT propose anything similar in topic or angle to these already-used ideas:\n"
                   + "\n".join(f"  - {t}" for t in avoid)) if avoid else ""

    cal_block = ""
    if calendar_events:
        cal_lines = "\n".join(
            f"  - {e['name']} in {e['days_until']} days (ref: {e['slug']}): {e['brief']}"
            for e in calendar_events)
        cal_block = ("\nUpcoming awareness days and holidays. Tie 1 to 2 ideas to the nearest ones "
                     "and set calendar_ref to the ref slug:\n" + cal_lines)

    user_msg = (
        f"Propose {count} distinct Instagram content ideas for OralCheck.\n\n"
        f"Content pillars to draw from (use the pillar key exactly):\n{pillar_lines}\n"
        f"{cal_block}\n{avoid_block}\n\n"
        "Requirements:\n"
        f"  - Return a JSON array of exactly {count} objects, no markdown fences.\n"
        "  - Each object: title (<=12 words, the specific angle), pillar (one key from above), "
        "media_type (carousel, image, or infographic), brief (2 to 3 sentences that a content "
        "generator can act on), angle (one of: surprising-true, myth, how-to, timely, human), "
        "calendar_ref (a ref slug or null).\n"
        "  - Bias the mix toward carousels (about 60 percent), with some infographics and images.\n"
        "  - Every idea must be genuinely distinct from the others and from the avoid list.\n"
        "  - Only real, defensible oral cancer facts. No invented statistics.\n"
        "  - Include at least one light_lane idea and, if a calendar event is near, at least one awareness idea."
    )

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model, max_tokens=2000, system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    parsed = json.loads(raw)

    used = _used_slugs(ledger)
    seen: set[str] = set()
    out: list[dict] = []
    for item in parsed:
        idea = _coerce(item, valid_pillars)
        if not idea:
            continue
        slug = slugify(idea["title"])
        if slug in used or slug in seen:
            continue
        seen.add(slug)
        idea["slug"] = slug
        out.append(idea)
    return out


def record_suggested(ledger: dict, ideas: list[dict]) -> dict:
    """Add ideas to the ledger as 'suggested' and set them as the current batch."""
    now = datetime.now(timezone.utc).isoformat()
    batch_ids = []
    for idea in ideas:
        idea_id = f"idea_{uuid.uuid4().hex[:8]}"
        record = {**idea, "id": idea_id, "status": "suggested",
                  "suggested_at": now, "used_at": None, "manifest_id": None}
        ledger["ideas"].append(record)
        batch_ids.append(idea_id)
    ledger["last_batch"] = batch_ids
    return ledger


def get_last_batch(ledger: dict) -> list[dict]:
    by_id = {i["id"]: i for i in ledger["ideas"]}
    return [by_id[i] for i in ledger.get("last_batch", []) if i in by_id]


def select(ledger: dict, numbers: list[int]) -> list[dict]:
    """Mark the given 1-based numbers from the last batch as selected. Returns them."""
    batch = get_last_batch(ledger)
    chosen = []
    for n in numbers:
        if 1 <= n <= len(batch):
            idea = batch[n - 1]
            if idea["status"] == "suggested":
                idea["status"] = "selected"
            chosen.append(idea)
    return chosen


def mark_queued(ledger: dict, idea_id: str, manifest_id: str) -> None:
    """An idea has been turned into a post and queued for review."""
    for i in ledger["ideas"]:
        if i["id"] == idea_id:
            i["status"] = "queued"
            i["used_at"] = datetime.now(timezone.utc).isoformat()
            i["manifest_id"] = manifest_id
            return
