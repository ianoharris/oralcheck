"""
Idea suggestion + ledger for OralCheck.

Generates numbered content ideas across pillars and the awareness calendar, and
keeps a persistent ledger so an idea that has been used (selected or posted) is
never suggested again, and recent suggestions do not repeat week to week.

Dependency direction is one-way: the agent imports this module and passes in the
shared brand constants. This module never imports the agent.
"""

import json
import os
import logging
import re
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic

import topics

log = logging.getLogger("oralcheck")

LEDGER_FILE = Path(__file__).parent / "ideas.json"
# Topics already posted outside this system (hand-maintained). Never re-suggested.
SEED_FILE = Path(__file__).parent / "used_topics.json"

VALID_MEDIA = {"carousel", "image", "reel"}
# Extra pillars beyond the core rotation. A trend_comparison pillar ("a stadium
# holds 65,000...") was dropped 2026-10-08: its tie-ins read as forced.
EXTRA_PILLARS = {
    "awareness": "A branded post tied to a specific awareness day or holiday from the content calendar.",
    "light_lane": (
        "A lighter, more human or gently witty take that still respects the subject. "
        "Never a joke at the expense of patients or the disease. Warmth and relatability, "
        "not shock. This lane always goes to manual review."
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
            data.setdefault("feedback", [])
            return data
    return {"ideas": [], "last_batch": [], "feedback": []}


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


# Statistics the account leans on. The headline survival figure had been
# appearing in post after post: good shorthand, but a follower who sees it four
# times in a row learns nothing new the last three. Recently used figures are
# fed back into the prompt as a do-not-reuse list so the pool actually rotates.
# Figures track SEER Cancer Stat Facts: Oral Cavity and Pharynx Cancer, the same
# source src/lib/seerStats.ts reads from. Keep the two in step: a post quoting a
# number the site no longer shows is worse than a repetitive post.
STAT_PATTERNS = [
    (r"\b(?:88|89)\s?%|\b88\.7\b", "89% five-year survival while still localized"),
    (r"\b(?:69(?:\.9)?|70)\s?%(?!\s*of)", "~70% overall five-year survival"),
    (r"\b36\s?%", "36% survival once it has spread to distant sites"),
    (r"\b60[,.]?\d{3}\b", "60,480 Americans diagnosed a year"),
    (r"\b26\s?%|\b1 in 4\b", "only 26% are found while still localized"),
    (r"\b1 in 10\b", "1 in 10 cases in nonsmokers"),
    (r"\b13,?\d{3}\b", "~13,150 deaths a year"),
    (r"\b70\s?% of\b", "~70% of oropharyngeal cancers are HPV-linked"),
    (r"\b2\.6x\b|\b2\.6 times\b", "men diagnosed ~2.6x more often than women"),
    (r"\btwo weeks\b|\b2 weeks\b", "the two-week rule for a non-healing sore"),
]

STAT_RECENCY = 6  # how many recent ideas to consider "fresh in the feed"


FEEDBACK_KEEP = 12  # how many past notes to carry into the prompt


def record_feedback(ledger: dict, note: str, *, title: str = "",
                    media_type: str = "") -> dict:
    """Store a rejection reason so the next batch can avoid repeating it."""
    note = (note or "").strip()
    if not note:
        return ledger
    ledger.setdefault("feedback", []).append({
        "note": note,
        "title": title,
        "media_type": media_type,
        "at": datetime.now(timezone.utc).isoformat(),
    })
    ledger["feedback"] = ledger["feedback"][-FEEDBACK_KEEP * 2:]
    return ledger


def _feedback_block(ledger: dict) -> str:
    """The standing notes, newest first, as prompt input.

    These are corrections the user has already made once. Repeating a mistake
    they have explicitly called out is worse than any individual weak idea, so
    they lead the requirements rather than trailing them.
    """
    notes = ledger.get("feedback", [])[-FEEDBACK_KEEP:]
    if not notes:
        return ""
    lines = []
    for f in reversed(notes):
        ctx = f" (on a {f['media_type']})" if f.get("media_type") else ""
        lines.append(f"  - {f['note']}{ctx}")
    return ("\nDirect feedback from the account owner on earlier posts. These are "
            "standing rules, not suggestions. Do not repeat anything called out here:\n"
            + "\n".join(lines))


def _recent_stats_block(ledger: dict) -> str:
    """List the statistics used in the most recent ideas so they get benched."""
    recent = [i for i in ledger.get("ideas", []) if i.get("used_at")]
    recent.sort(key=lambda i: i.get("used_at") or "", reverse=True)
    haystack = " ".join(
        f"{i.get('title','')} {i.get('brief','')}" for i in recent[:STAT_RECENCY]
    ).lower()

    hits = [label for pat, label in STAT_PATTERNS if re.search(pat, haystack)]
    if not hits:
        return ""
    return (
        "\nStatistics already used in recent posts. Do NOT build an idea around any of these; "
        "the feed has covered them and repeating a number teaches the audience nothing:\n"
        + "\n".join(f"  - {h}" for h in hits)
        + "\nReach for a different, equally defensible figure or a non-numeric angle instead."
    )


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


def _salvage_objects(blob: str) -> list:
    """Parse the top-level {...} objects out of an array body one at a time.

    Used when the array as a whole will not parse. Walking balanced braces and
    decoding each object independently means one malformed idea costs one idea,
    and a response truncated mid-object costs only the object it stopped in,
    instead of the entire batch.
    """
    out: list = []
    depth = 0
    start = -1
    in_str = False
    escape = False
    for i, ch in enumerate(blob):
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                try:
                    out.append(json.loads(blob[start:i + 1]))
                except Exception:
                    pass          # one bad idea, not a lost batch
                start = -1
    return out


def _extract_json_array(resp) -> list:
    """Pull the JSON idea array out of a response that may include web-search blocks.

    Concatenates all text blocks (the final one holds the JSON), strips any code
    fences, and slices from the first '[' to the last ']'.

    Never raises. This used to propagate a JSONDecodeError, and because
    generate_by_type calls it once per format in sequence, one unparseable
    response destroyed the whole weekly run: on 2026-08-24 carousel and reel had
    already generated successfully and were thrown away when the image batch
    came back malformed. A bad response should cost at most the ideas in it.
    """
    texts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    raw = "\n".join(texts).strip()
    if "```" in raw:
        raw = re.sub(r"```[a-zA-Z]*", "", raw).replace("```", "")
    start, end = raw.find("["), raw.rfind("]")
    if start == -1:
        log.warning("No JSON array in idea response (%d chars); skipping this batch.", len(raw))
        return []
    # A missing closing bracket means truncation, so salvage from the opening one.
    body = raw[start:end + 1] if end > start else raw[start:]
    try:
        parsed = json.loads(body)
        if isinstance(parsed, list):
            return parsed
    except Exception as exc:
        log.warning("Idea response was not valid JSON (%s); salvaging objects.", exc)
    salvaged = _salvage_objects(body)
    log.warning("Salvaged %d idea object(s) from the malformed response.", len(salvaged))
    return salvaged


def generate_by_type(per_type, *, api_key, model, system_prompt, pillar_briefs,
                     calendar_events, ledger, only: str | None = None,
                     hook_block: str = "") -> list[dict]:
    """Generate `per_type` ideas for each format, kept in format order.

    Topic, shape and hook style for every slot are assigned up front for the
    whole batch (topics.plan_slots), so no two ideas share a topic even across
    formats. The model is then called once per format to write its slots.
    Each format is still isolated: whatever goes wrong writing one of them, the
    formats that already succeeded reach Telegram, because the run happens once
    a week and a failure costs the whole week.

    `only` restricts generation to one format, which is what a top-up uses.
    """
    wanted = [m for m in ([only] if only else ["carousel", "reel", "image"]) if m in VALID_MEDIA]
    slots = topics.plan_slots(ledger, [m for m in wanted for _ in range(per_type)])
    out: list[dict] = []
    for media in wanted:
        mine = [sl for sl in slots if sl["media_type"] == media]
        try:
            got = generate_ideas(
                len(mine), api_key=api_key, model=model, system_prompt=system_prompt,
                pillar_briefs=pillar_briefs, calendar_events=calendar_events,
                ledger=ledger, hook_block=hook_block, slots=mine,
                extra_avoid=[i["title"] for i in out],
            )
        except Exception as exc:  # noqa: BLE001
            log.error("Idea generation failed for %s (%s); continuing with the other formats.",
                      media, exc)
            continue
        if not got:
            log.warning("No usable %s ideas came back this run.", media)
        out.extend(got)
    return out


def _problems(idea: dict) -> list[str]:
    """Why a written idea would read like the old feed, if it would."""
    found = []
    for field in ("title", "hook"):
        hit = topics.banned_phrase(idea.get(field, ""))
        if hit:
            found.append(f'{field} uses the overused phrase "{hit}"')
    if topics.two_sentence_title(idea.get("title", "")):
        found.append('title is two sentences ("X. Y."); write one line')
    if not idea.get("title") or not idea.get("brief"):
        found.append("title or brief is missing")
    return found


def _write_slots(slots, *, api_key, model, system_prompt, calendar_events, avoid,
                 hook_block, notes=None) -> list[dict]:
    blocks = "\n\n".join(topics.slot_brief(n + 1, sl) for n, sl in enumerate(slots))
    cal_block = ""
    if calendar_events:
        cal_block = ("\nAwareness days coming up. Tie at most ONE slot to one of these, and only "
                     "when its topic genuinely fits; set calendar_ref to the ref slug. A forced "
                     "tie-in is worse than none:\n" + "\n".join(
                         f"  - {e['name']} in {e['days_until']} days (ref: {e['slug']})"
                         for e in calendar_events))
    avoid_block = ("\nRecent titles. Do not echo their wording or rhythm:\n"
                   + "\n".join(f"  - {t}" for t in avoid[-20:])) if avoid else ""
    notes_block = ""
    if notes:
        notes_block = ("\nA previous attempt at these slots was rejected for: "
                       + "; ".join(notes) + ". Fix that.")
    user_msg = (
        "Write one Instagram post idea for each slot below. The topic, shape and opening "
        "style are already decided. Your job is to find the most interesting way in: a "
        "specific moment, a surprising detail inside the facts, a question the viewer can "
        "answer about their own mouth. Make each one feel like it came from a different "
        "person on a different day.\n\n"
        f"{blocks}\n{cal_block}\n{hook_block}\n{avoid_block}\n{notes_block}\n\n"
        "Rules:\n"
        "  - Use only the facts listed for that slot. No other numbers, no invented statistics.\n"
        "  - title: at most 10 words, ONE line, not two sentences. It names the post for the "
        "owner picking from a list, so make it specific rather than clever.\n"
        "  - hook: the literal first line the viewer sees or hears, in the slot's hook style, "
        "at most 12 words.\n"
        "  - brief: 2 to 3 sentences laying out the beats of the post in the slot's shape, "
        "concrete enough for a designer to build from.\n"
        "  - Never write: most people, nobody tells you, did you know, here's why, the truth "
        "about, actually, silent killer. No em dashes.\n"
        "  - Survival figures are SEER summary stage: say 'while still localized' and 'once it "
        "has spread to distant sites', never Stage I or Stage IV.\n\n"
        "Return only a JSON array, one object per slot in order: "
        '{"slot": n, "title": "...", "hook": "...", "brief": "...", "calendar_ref": null}'
    )
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model, max_tokens=3000, system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    written = _extract_json_array(resp)
    out = []
    for n, sl in enumerate(slots):
        got = next((w for w in written if isinstance(w, dict) and w.get("slot") == n + 1), None)
        if got is None and n < len(written) and isinstance(written[n], dict):
            got = written[n]
        got = got or {}
        out.append({
            **sl,
            "title": str(got.get("title", "")).strip(),
            "hook": str(got.get("hook", "")).strip(),
            "brief": str(got.get("brief", "")).strip(),
            "angle": sl["shape"],
            "calendar_ref": got.get("calendar_ref") or None,
        })
    return out


def generate_ideas(count, *, api_key, model, system_prompt, pillar_briefs,
                   calendar_events, ledger, force_media: str | None = None,
                   extra_avoid: list[str] | None = None,
                   hook_block: str = "", slots: list[dict] | None = None) -> list[dict]:
    """Write `count` ideas, filtered against the ledger.

    Without `slots`, plans its own: all `force_media`, or a rotation of the
    three formats. Any idea that comes back in the old feed's voice (a banned
    phrase, an "X. Y." title) gets one rewrite; if the rewrite fails too, the
    slot is dropped rather than shipped.

    Returns idea dicts not yet written to the ledger.
    """
    if slots is None:
        cycle = ["carousel", "reel", "image"]
        media_list = [force_media] * count if force_media else [cycle[n % 3] for n in range(count)]
        slots = topics.plan_slots(ledger, media_list)
    if not slots:
        return []
    avoid = _avoid_titles(ledger) + load_seed_topics() + list(extra_avoid or [])
    kw = dict(api_key=api_key, model=model, system_prompt=system_prompt,
              calendar_events=calendar_events, avoid=avoid, hook_block=hook_block)

    written = _write_slots(slots, **kw)
    bad = [(n, _problems(w)) for n, w in enumerate(written) if _problems(w)]
    if bad:
        log.info("Rewriting %d idea(s) that read like the old feed: %s", len(bad),
                 "; ".join(p[0] for _, p in bad))
        retry = _write_slots([slots[n] for n, _ in bad], notes=[p for _, ps in bad for p in ps], **kw)
        for (n, _), w in zip(bad, retry):
            written[n] = w

    used = _used_slugs(ledger)
    seen: set[str] = set()
    out: list[dict] = []
    for w in written:
        if _problems(w):
            log.warning("Dropped idea after rewrite (%s): %s", "; ".join(_problems(w)), w.get("title"))
            continue
        w["title"] = _strip_dashes(w["title"])
        w["hook"] = _strip_dashes(w["hook"])
        w["brief"] = _strip_dashes(w["brief"])
        slug = slugify(w["title"])
        if slug in used or slug in seen:
            continue
        seen.add(slug)
        w["slug"] = slug
        out.append(w)
    return out


def _strip_dashes(text: str) -> str:
    return re.sub(r"\s*[\u2014\u2013]\s*", ", ", text or "")


def _balance_formats(ideas: list[dict]) -> list[dict]:
    """Guarantee every format is represented in a batch.

    The prompt asks for a mix, but nothing enforced it, so a batch could come
    back as eight carousels and the week would ship one format. Reassigns the
    media_type of surplus ideas from the most common format until each of
    image, carousel, and reel appears at least once.

    Order is preserved: a week is picked off the front of the batch, so
    front-loading the variety is what makes "one of each per week" hold.
    """
    if len(ideas) < len(VALID_MEDIA):
        return ideas

    def counts() -> dict[str, int]:
        c = {m: 0 for m in VALID_MEDIA}
        for i in ideas:
            c[i["media_type"]] += 1
        return c

    for fmt in ("reel", "image", "carousel"):
        c = counts()
        if c[fmt] > 0:
            continue
        # Take from whichever format is most over-represented, and take the
        # last one so the earliest (best) ideas keep their intended treatment.
        donor = max(c, key=lambda m: c[m])
        for idea in reversed(ideas):
            if idea["media_type"] == donor:
                idea["media_type"] = fmt
                break

    # Interleave so the first three ideas are three different formats.
    by_fmt: dict[str, list[dict]] = {m: [] for m in VALID_MEDIA}
    for i in ideas:
        by_fmt[i["media_type"]].append(i)
    ordered: list[dict] = []
    while any(by_fmt.values()):
        for fmt in ("carousel", "reel", "image"):
            if by_fmt[fmt]:
                ordered.append(by_fmt[fmt].pop(0))
    return ordered


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


def release_stale_selected(ledger: dict) -> list[str]:
    """Return ideas claimed by a run that died before building them.

    `select()` and the replacement path both mark an idea "selected" *before*
    generating the post, so two runs cannot claim the same one. If the run then
    dies between the claim and `mark_queued`, the idea keeps that status
    forever, and since "selected" is in USED_STATUSES it is also never
    suggested again. The topic is silently gone.

    That is not hypothetical: the 2026-08-31 run left
    "Alcohol Is an Oral Cancer Risk Factor Most People Never Hear About"
    stranded, and the two failed 09-07 runs could not reach it either.

    Safe to call at the start of a fresh batch and nowhere else: at that moment
    nothing is legitimately mid-build, so any leftover claim is a dead one. An
    idea that reached a manifest is left alone, since that post exists.
    """
    released = []
    for i in ledger["ideas"]:
        if i.get("status") == "selected" and not i.get("manifest_id"):
            i["status"] = "suggested"
            released.append(i["id"])
    return released


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


def mark_failed(ledger: dict, idea_id: str) -> None:
    """A spare idea couldn't be generated into a post; skip it so the
    replacement loop moves on to the next spare instead of retrying it."""
    for i in ledger["ideas"]:
        if i["id"] == idea_id:
            i["status"] = "failed"
            return
