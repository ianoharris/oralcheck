"""
Topical hook finder.

Templates 11-16 can carry a pop-culture or calendar hook, but something has to
*find* one. Idea generation already had web search, told loosely to "search for
trending topics", which produced nothing durable: the results were never
structured, never scored, and never remembered, so the same generic angles came
back week after week.

This does the searching as its own step and returns structured, dated hooks that
idea generation can build on, with a ledger so a hook is used once.

Two rules matter more than the rest:

* **Returning nothing is a valid answer.** A forced connection between a film and
  oral cancer reads as cringe and costs more credibility than the post gains. The
  prompt says so explicitly and the parser does not pad the list.
* **Freshness is the whole point.** A hook is only useful in a window. Anything
  outside it is dropped even if the model liked it.

    python3 oralcheck_agent.py --hooks
"""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

import anthropic

HOOKS_FILE = Path(__file__).parent / "hooks.json"

# A hook is live if it happened this recently or lands this soon. Outside this
# window it reads as either old news or a post nobody has context for yet.
LOOKBACK_DAYS = 14
LOOKAHEAD_DAYS = 21

VALID_KINDS = {"product", "film", "tv", "music", "sport", "news", "study",
               "holiday", "awareness", "internet"}

# Hooks that must never be used, regardless of how well they would perform.
# Hanging a marketing post on a named person's illness is the fastest way to
# lose the credibility the rest of the account is built on.
TASTE_RULES = """
Never propose a hook that:
  - names a real person's cancer diagnosis, illness or death
  - attaches the brand to a tragedy, disaster, or an active news emergency
  - makes a joke at the expense of patients or of the disease
  - implies a product, film or event causes or cures cancer
  - requires a strained connection. If the link is not obvious in one sentence,
    it is not a hook.
"""


def load_ledger() -> dict:
    if HOOKS_FILE.exists():
        try:
            d = json.loads(HOOKS_FILE.read_text())
            d.setdefault("hooks", [])
            return d
        except Exception:
            pass
    return {"hooks": []}


def save_ledger(ledger: dict) -> None:
    HOOKS_FILE.write_text(json.dumps(ledger, indent=2))


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:60]


def used_slugs(ledger: dict) -> set[str]:
    return {h["slug"] for h in ledger.get("hooks", [])}


def _in_window(when: str, today: date) -> bool:
    """Keep only hooks inside the live window. Undated hooks are dropped."""
    try:
        d = datetime.strptime(when.strip()[:10], "%Y-%m-%d").date()
    except Exception:
        return False
    return -LOOKBACK_DAYS <= (d - today).days <= LOOKAHEAD_DAYS


def _extract_json_array(resp) -> list:
    texts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    raw = "\n".join(texts).strip()
    if "```" in raw:
        raw = re.sub(r"```[a-zA-Z]*", "", raw).replace("```", "")
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1 or end < start:
        return []
    try:
        return json.loads(raw[start:end + 1])
    except Exception:
        return []


def find_hooks(count: int = 5, *, api_key: str, model: str,
               ledger: dict | None = None, today: date | None = None) -> list[dict]:
    """Search for current hooks worth building a post on."""
    ledger = ledger if ledger is not None else load_ledger()
    today = today or datetime.now(timezone.utc).date()
    seen = used_slugs(ledger)

    recent = [h["title"] for h in ledger.get("hooks", [])][-25:]
    avoid = ("\nAlready used, do not repeat:\n" + "\n".join(f"  - {t}" for t in recent)) if recent else ""

    lo = (today - timedelta(days=LOOKBACK_DAYS)).isoformat()
    hi = (today + timedelta(days=LOOKAHEAD_DAYS)).isoformat()

    system = (
        "You find timely cultural hooks for a health brand's social content. "
        "OralCheck is a free oral cancer risk questionnaire. Its voice is calm, "
        "grounded and evidence-based: no hype, no exclamation points, no em dashes. "
        "You are looking for things people are already talking about that a post "
        "can honestly hang an oral-health point on."
    )

    user = f"""Today is {today.isoformat()}.

Search the web for things happening between {lo} and {hi}: product launches
(especially oral care), film and TV releases, sports events, music, holidays,
awareness dates, viral internet moments, and newly published studies on oral
cancer, HPV, tobacco or alcohol.

Then return up to {count} hooks OralCheck could build a post on.
{TASTE_RULES}
{avoid}

Return ONLY a JSON array, no markdown fences. Each object:
  title      short name of the thing, under 10 words
  kind       one of: {", ".join(sorted(VALID_KINDS))}
  when       YYYY-MM-DD, the date it happened or happens
  why_now    one sentence on why people are talking about it right now
  angle      one sentence: the honest oral-health point it supports. If you
             cannot state this without straining, leave the hook out entirely.
  strength   1 to 5, how strong the connection genuinely is. Be harsh. A 5 is a
             product people put in their mouth. A 2 is a stretch.

Returning fewer than {count} is correct and expected. Returning an empty array
is correct if nothing this fortnight genuinely fits. Do not pad the list."""

    client = anthropic.Anthropic(api_key=api_key)
    # Each search costs a per-search fee AND injects its results into the
    # request as input tokens, which is usually the larger of the two. Three
    # is enough to find a live hook; six was buying diminishing returns at
    # double the price.
    tools = [{"type": "web_search_20260209", "name": "web_search",
              "max_uses": int(os.environ.get("HOOK_SEARCHES", "3"))}]
    try:
        resp = client.messages.create(
            model=model, max_tokens=3000, system=system,
            tools=tools, messages=[{"role": "user", "content": user}],
        )
    except Exception as exc:  # noqa: BLE001
        # Without search this step has no value: an unsearched "current event"
        # is just the model's training data, which is exactly the staleness
        # this is meant to fix.
        print(f"Hook search unavailable ({exc}); skipping hooks this run.", flush=True)
        return []

    out: list[dict] = []
    dropped: list[str] = []
    candidates = _extract_json_array(resp)
    for raw in candidates:
        title = str(raw.get("title", "")).strip()
        angle = str(raw.get("angle", "")).strip()
        if not title or not angle:
            dropped.append(f"{title or '(untitled)'}: no angle stated")
            continue
        kind = str(raw.get("kind", "")).lower().strip()
        if kind not in VALID_KINDS:
            kind = "news"
        when = str(raw.get("when", "")).strip()
        if not _in_window(when, today):
            dropped.append(f"{title}: date {when or '(none)'} outside {lo}..{hi}")
            continue
        try:
            strength = max(1, min(5, int(raw.get("strength", 3))))
        except Exception:
            strength = 3
        slug = _slug(title)
        if slug in seen:
            dropped.append(f"{title}: already used")
            continue
        seen.add(slug)
        out.append({
            "id": f"hook_{uuid.uuid4().hex[:8]}",
            "slug": slug,
            "title": title,
            "kind": kind,
            "when": when[:10],
            "why_now": str(raw.get("why_now", "")).strip(),
            "angle": angle,
            "strength": strength,
            "found_at": datetime.now(timezone.utc).isoformat(),
        })

    # Say what was thrown away and why. Silently discarding candidates makes
    # the filters impossible to tune: a run that returns one hook could mean the
    # model was appropriately picky or that the date window is too tight, and
    # those need different fixes.
    if dropped:
        print(f"Hooks: kept {len(out)} of {len(candidates)}. Dropped:", flush=True)
        for d in dropped:
            print(f"  - {d}", flush=True)

    # Strongest first: a weak hook used because it was first is how the cringe
    # gets in.
    out.sort(key=lambda h: -h["strength"])
    return out


def record(ledger: dict, hooks: list[dict]) -> dict:
    ledger.setdefault("hooks", []).extend(hooks)
    ledger["hooks"] = ledger["hooks"][-120:]
    return ledger


def live_hooks(ledger: dict, today: date | None = None, min_strength: int = 3) -> list[dict]:
    """Hooks still inside their window and worth using."""
    today = today or datetime.now(timezone.utc).date()
    out = [h for h in ledger.get("hooks", [])
           if h.get("strength", 0) >= min_strength and _in_window(h.get("when", ""), today)]
    out.sort(key=lambda h: -h.get("strength", 0))
    return out


def hooks_block(ledger: dict, today: date | None = None, limit: int = 4) -> str:
    """Prompt fragment offering current hooks to idea generation."""
    hooks = live_hooks(ledger, today)[:limit]
    if not hooks:
        return ""
    lines = []
    for h in hooks:
        lines.append(f"  - {h['title']} ({h['kind']}, {h['when']}, strength {h['strength']}/5)")
        lines.append(f"      why now: {h['why_now']}")
        lines.append(f"      angle:   {h['angle']}")
    return (
        "\nTimely hooks found this week. Build ONE to TWO ideas on the strongest of "
        "these, and say which in the idea's brief. Ignore any that would need a "
        "strained connection: a forced tie-in is worse than a plain post.\n"
        + "\n".join(lines)
    )
