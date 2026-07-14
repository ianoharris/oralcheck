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
# Topics already posted outside this system (hand-maintained). Never re-suggested.
SEED_FILE = Path(__file__).parent / "used_topics.json"

VALID_MEDIA = {"carousel", "image", "reel"}
# Extra pillars beyond the core rotation.
EXTRA_PILLARS = {
    "awareness": "A branded post tied to a specific awareness day or holiday from the content calendar.",
    "light_lane": (
        "A lighter, more human or gently witty take that still respects the subject. "
        "Never a joke at the expense of patients or the disease. Warmth and relatability, "
        "not shock. This lane always goes to manual review."
    ),
    "trend_comparison": (
        "Connect an oral cancer fact to a current event or trending topic with a striking, "
        "true comparison (e.g. a World Cup stadium holds ~65,000, and ~60,000 Americans are "
        "diagnosed with oral cancer each year). Timely and shareable, but never flippant about "
        "the disease and never an invented number."
    ),
}


def load_seed_topics() -> list[str]:
    if SEED_FILE.exists():
        try:
            return [str(t) for t in json.loads(SEED_FILE.read_text())]
        except Exception:
            return []
    return []


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


def _extract_json_array(resp) -> list:
    """Pull the JSON idea array out of a response that may include web-search blocks.

    Concatenates all text blocks (the final one holds the JSON), strips any code
    fences, and slices from the first '[' to the last ']'.
    """
    texts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    raw = "\n".join(texts).strip()
    if "```" in raw:
        raw = re.sub(r"```[a-zA-Z]*", "", raw).replace("```", "")
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON array found in idea-generation response")
    return json.loads(raw[start:end + 1])


def generate_ideas(count, *, api_key, model, system_prompt, pillar_briefs,
                   calendar_events, ledger) -> list[dict]:
    """Ask the model for `count` fresh ideas, filtered against the ledger.

    Returns coerced idea dicts (not yet written to the ledger).
    """
    all_pillars = {**{p: pillar_briefs[p] for p in pillar_briefs}, **EXTRA_PILLARS}
    valid_pillars = set(all_pillars.keys())

    pillar_lines = "\n".join(f"  - {p}: {desc}" for p, desc in all_pillars.items())
    avoid = _avoid_titles(ledger) + load_seed_topics()
    avoid_block = ("\nDo NOT propose anything similar in topic or angle to these already-used ideas "
                   "(the brand has already posted these). Every idea must be a genuinely new angle:\n"
                   + "\n".join(f"  - {t}" for t in avoid)) if avoid else ""

    cal_block = ""
    if calendar_events:
        cal_lines = "\n".join(
            f"  - {e['name']} in {e['days_until']} days (ref: {e['slug']}): {e['brief']}"
            for e in calendar_events)
        cal_block = ("\nUpcoming awareness days and holidays. Tie 1 to 2 ideas to the nearest ones "
                     "and set calendar_ref to the ref slug:\n" + cal_lines)

    user_msg = (
        f"First, briefly research the current landscape: search the web for recent oral cancer / HPV "
        "news, awareness-day context, culturally trending topics and current events (sports, holidays, "
        "viral moments), and what kinds of health-awareness posts are performing right now. "
        "Use 2 to 4 searches, then stop researching and write the ideas.\n\n"
        f"Then propose {count} distinct Instagram content ideas for OralCheck.\n\n"
        f"Content pillars to draw from (use the pillar key exactly):\n{pillar_lines}\n"
        f"{cal_block}\n{avoid_block}\n\n"
        "Requirements:\n"
        f"  - Return a JSON array of exactly {count} objects as your final message, no markdown fences.\n"
        "  - Each object: title (<=12 words, the specific angle), pillar (one key from above), "
        "media_type (carousel, image, or reel), brief (2 to 3 sentences that a content "
        "generator can act on), angle (one of: surprising-true, myth, how-to, timely, human, trend-comparison), "
        "calendar_ref (a ref slug or null).\n"
        "  - Mix the formats: mostly carousels (about half), plus a couple of reels "
        "(short animated voiceover videos, great for a myth, a single stat, or a timely hook) "
        "and a couple of single images. Aim for at least 2 reels in a batch of 8.\n"
        "  - Every idea must be genuinely distinct from the others and from the avoid list.\n"
        "  - Only real, defensible oral cancer facts. No invented statistics.\n"
        "  - Include at least one light_lane idea, at least one trend_comparison idea that ties an oral "
        "cancer fact to something current or trending with a striking true comparison, and, if a calendar "
        "event is near, at least one awareness idea. Keep every comparison tasteful, never flippant about the disease."
    )

    client = anthropic.Anthropic(api_key=api_key)
    web_tool = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 4}]
    try:
        resp = client.messages.create(
            model=model, max_tokens=4000, system=system_prompt,
            tools=web_tool, messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as exc:
        # Web search may be unavailable (plan/model); fall back to no-tools generation.
        import logging
        logging.getLogger("oralcheck").warning("Web search unavailable (%s); generating without it.", exc)
        resp = client.messages.create(
            model=model, max_tokens=2000, system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )
    parsed = _extract_json_array(resp)

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


def spare_ideas(ledger: dict) -> list[dict]:
    """Ideas from the last batch that were suggested but not picked -- the pool
    to draw a replacement from when a generated post gets rejected."""
    return [i for i in get_last_batch(ledger) if i.get("status") == "suggested"]


def idea_for_manifest(ledger: dict, manifest_id: str) -> dict | None:
    for i in ledger["ideas"]:
        if i.get("manifest_id") == manifest_id:
            return i
    return None


def mark_rejected(ledger: dict, idea_id: str) -> None:
    """A generated post was rejected in review; don't reuse or count the idea."""
    for i in ledger["ideas"]:
        if i["id"] == idea_id:
            i["status"] = "rejected"
            return
