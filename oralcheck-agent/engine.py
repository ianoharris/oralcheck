"""
Content engine v2: turns one idea into a finished post with posts2 and reel2.

The idea arrives with its topic, shape and hook style already decided
(topics.plan_slots). This module asks the model for a spec in the vocabulary
the templates understand, repairs or drops anything the templates cannot draw,
and renders it:

    write_post(...)  -> {"slides": [...], "hook", "caption", "hashtags"}   carousel, image
    write_reel(...)  -> {"beats": [...],  "hook", "caption", "hashtags"}   reel
    render_post(spec)            -> [jpg paths]
    render_reel(spec, tts, ...)  -> mp4 path

Like ideas.py it never imports the agent. The agent passes in `ask`, a function
that sends a prompt to the model and returns the text.
"""
from __future__ import annotations

import json
import logging
import re
import tempfile

import art
import posts2
import reel2
import topics

log = logging.getLogger("oralcheck.engine")

# ── what the templates accept ─────────────────────────────────────────────────
# *word* marks a highlighted word in any text field that allows it.

SLIDE_SPEC = {
    "cover": 'hook (<=9 words, *highlight* 1-2 words), kicker (2-4 words), optional art: "mouthmap" or an icon name',
    "poster": "text (<=14 words, *highlight* allowed), optional kicker, sub (<=16 words), foot",
    "bignum": 'value (the figure exactly, e.g. "89%" or "2.6x"), label (<=14 words), kicker, source',
    "split": 'title, items: exactly 2 of {value: a percentage like "89%", label}, source',
    "list": "title (<=6 words), items: 3 to 5 strings of <=10 words",
    "mouthmap": "title (<=8 words), optional zones: subset of ZONES in the order to check them, foot",
    "step": 'n ("1", "2"...), area (<=3 words), text (<=22 words), optional tip (<=14 words), zone from ZONES or icon from ICONS',
    "calendar": "title (<=6 words), text (<=24 words), kicker. Draws 14 days with day 15 flagged.",
    "compare": "title (<=8 words), a_title, a: 3-4 short strings, b_title, b: 3-4 short strings, foot. a is the reassuring side, b the get-it-checked side.",
    "icons": "title (<=6 words), items: 3 or 6 of {icon from ICONS, label <=3 words}, optional sub",
    "textpost": "text (<=45 words, plain and conversational, *highlight* allowed), optional meta (<=6 words)",
    "notes": 'title (<=6 words), items: 4 to 7 strings, prefix "[x] " on ones already done, optional date',
    "photo": 'photo: "white" or "mixed" (licensed clinical photos), lines: 2-3 strings of <=5 words',
    "quiz": "question (<=12 words), options: 2 or 3 short strings, kicker",
    "answer": 'answer (<=5 words, e.g. "B. Get it checked"), text (<=30 words), correct (true/false)',
    "cta": "optional headline (<=8 words, *highlight* allowed), sub",
}

VISUAL_SPEC = {
    "text": "optional kicker (2-3 words). The spoken words appear as large captions.",
    "quiz": "question (<=10 words), options: exactly 2 short strings, kicker. Give this beat hold: 2.0 for a countdown.",
    "myth": "myth (the belief, <=8 words), fact (<=8 words, *highlight* allowed), strike_word and fact_word: words from `say` that trigger each",
    "calendar": 'title (<=5 words), flag_word: the word in `say` that flags day 15 (e.g. "weeks")',
    "mouthmap": "zones: ZONES in the order `say` names them, optional title. Each zone lights as it is spoken.",
    "photo": 'photo: "white" or "mixed", label (<=6 words)',
    "icons": "items: 3 to 6 of {icon from ICONS, label <=3 words, word: the word in `say` that reveals it}, optional title",
    "stat": "value (the figure exactly), label (<=8 words), word (the word in `say` that reveals it), source",
    "bars": "items: exactly 2 of {value: number 0-100, label <=5 words, word}, source",
    "cta": "optional headline (<=7 words), sub. Use only on the last beat.",
}

PHOTOS = {"white", "mixed"}   # the only sign photos with attribution cleared


def _vocab() -> str:
    return (f"ZONES: {', '.join(art.ZONES)}\n"
            f"ICONS: {', '.join(art.ICONS)}\n")


def _slot_block(idea: dict) -> str:
    if idea.get("topic") in topics.TOPICS:
        return topics.slot_brief(1, idea) + f"\n    hook line: {idea.get('hook', '')}\n    brief: {idea.get('brief', '')}"
    return f"  Brief:\n    {idea.get('brief', '')}"


def _templates_for(idea: dict, media: str) -> list[str]:
    shape = topics.SHAPES.get(media, {}).get(idea.get("shape") or "")
    return list(shape["templates"]) if shape else []


def _attempt(prompt: str, ask, check) -> dict:
    """Ask, check, and if the result has problems ask once more naming them.

    `check` validates the spec in place and returns (fatal, problems): fatal
    means nothing usable came back and raises; problems are style faults (a
    worn phrase, a reel that is mostly captions) worth one rewrite. A second
    attempt that still has style faults is accepted with a warning, because a
    missed weekly post costs more than an imperfect one, and every post still
    passes through review in Telegram.
    """
    data, problems = None, []
    for attempt in range(2):
        p = prompt if not problems else (
            prompt + "\n\nThe previous attempt was rejected for: " + "; ".join(problems) + ". Fix that.")
        data = _parse(ask(p))
        fatal, problems = check(data)
        if fatal:
            raise ValueError(fatal)
        if not problems:
            return data
        log.info("Spec attempt %d had problems: %s", attempt + 1, "; ".join(problems))
    log.warning("Accepting spec with: %s", "; ".join(problems))
    return data


def _worn(texts) -> list[str]:
    hits = {topics.banned_phrase(t) for t in texts if t}
    return [f'uses the overused phrase "{h}"' for h in sorted(h for h in hits if h)]


def _strings(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [x for v in obj.values() for x in _strings(v)]
    if isinstance(obj, list):
        return [x for v in obj for x in _strings(v)]
    return []


def _post_problems(data: dict, media: str):
    data["slides"] = validate_slides(data.get("slides", []), media)
    if not data["slides"]:
        return f"{media} spec had no usable slides", []
    return None, _worn(_strings(data["slides"]) + [data.get("caption", "")])


def _reel_problems(data: dict):
    data["beats"] = validate_beats(data.get("beats", []))
    if len(data["beats"]) < 3:
        return "reel plan had fewer than 3 usable beats", []
    kinds = [b["visual"]["type"] for b in data["beats"]]
    problems = _worn([b["say"] for b in data["beats"]] + [data.get("caption", "")])
    # Mostly-caption reels are what made the old ones dull.
    if kinds.count("text") > 2:
        problems.append(f"{kinds.count('text')} beats are plain text; use at most 2")
    repeats = sorted({a for a, b in zip(kinds, kinds[1:]) if a == b and a != "text"})
    if repeats:
        problems.append(f"visual type {', '.join(repeats)} used twice in a row")
    words = sum(len(b["say"].split()) for b in data["beats"])
    if words > 80:
        problems.append(f"script runs {words} words; keep it to 55 to 68")
    return None, problems


def _parse(raw: str) -> dict:
    raw = raw.strip()
    if "```" in raw:
        raw = re.sub(r"```[a-zA-Z]*", "", raw).replace("```", "")
    start, end = raw.find("{"), raw.rfind("}")
    return json.loads(raw[start:end + 1])


def _tidy(text: str) -> str:
    return re.sub(r"\s*[—–]\s*", ", ", str(text or "")).strip()


def _finish(data: dict, credits: list[str] = ()) -> dict:
    data["caption"] = _tidy(data.get("caption", ""))
    # The clinical photos are CC-licensed; the credit is drawn on the image and
    # repeated in the caption, where the licence expects to find it.
    for c in dict.fromkeys(credits):
        if c and c not in data["caption"]:
            data["caption"] += f"\n\n{c}"
    data["hook"] = _tidy(data.get("hook", ""))
    data["hashtags"] = [h.lower().strip().lstrip("#") for h in data.get("hashtags", [])][:5]
    if "oralcheck.org" not in data["caption"]:
        data["caption"] += "\n\nCheck your risk, free, at oralcheck.org."
    return data


# ── posts ─────────────────────────────────────────────────────────────────────

def write_post(idea: dict, media: str, ask) -> dict:
    """Ask for a carousel or single-image spec and return it validated."""
    suggested = _templates_for(idea, media)
    if media == "image":
        count = "exactly 1 slide"
        allowed = suggested or ["poster", "bignum", "textpost", "notes", "split", "calendar", "mouthmap", "photo"]
    else:
        count = "5 to 7 slides: a first slide that hooks, the middle that delivers, and cta last"
        allowed = list(SLIDE_SPEC)
    spec_lines = "\n".join(f"  {k}: {v}" for k, v in SLIDE_SPEC.items() if k in allowed or media == "carousel")
    prompt = (
        f"Build this Instagram {media} for OralCheck.\n\n{_slot_block(idea)}\n\n"
        f"Templates available, with their fields:\n{spec_lines}\n\n{_vocab()}\n"
        + (f"This shape is usually built from: {', '.join(suggested)}. Follow it unless the content "
           "clearly needs something else.\n" if suggested else "")
        + f"Make {count}. Every slide is an object with a \"template\" key plus its fields. Do not "
        "repeat a template within a deck except step, bignum and list. The opening slide carries the "
        "hook line. Keep every text field to its word limit: these are read on a phone, mid-scroll.\n"
        "Never present a home check as a test or a diagnosis: looking tells you whether to get "
        "it checked, not what it is.\n"
        "Use only the facts given. Survival figures: 'while still localized', 'once it has spread "
        "to distant sites', never Stage I or IV. No em dashes. Never say 'we'.\n\n"
        'Return only JSON: {"slides": [...], "caption": "...", "hashtags": [5 lowercase tags]}. '
        "The caption is 60 to 140 words, opens with something other than the slide text, and ends "
        "with a call to action naming oralcheck.org."
    )
    data = _attempt(prompt, ask, lambda d: _post_problems(d, media))
    data.setdefault("hook", idea.get("hook") or _first_text(data["slides"][0]))
    return _finish(data, [sl.get("credit", "") for sl in data["slides"]])


def _first_text(slide: dict) -> str:
    for k in ("hook", "text", "question", "title", "value"):
        if slide.get(k):
            return re.sub(r"\*", "", str(slide[k]))
    return ""


def _strs(v, limit: int) -> list[str]:
    return [str(x) for x in (v or []) if str(x).strip()][:limit]


def validate_slides(slides: list, media: str) -> list[dict]:
    """Repair what can be repaired, drop what the templates cannot draw."""
    out = []
    for s in slides if isinstance(slides, list) else []:
        if not isinstance(s, dict):
            continue
        t = s.get("template") or s.get("type")
        if t not in posts2.TEMPLATES:
            log.warning("Dropping slide with unknown template %r", t)
            continue
        s = {k: v for k, v in s.items() if k != "template"}
        s["type"] = t
        for k, v in list(s.items()):
            if isinstance(v, str):
                s[k] = _tidy(v)
        try:
            ok = _check_slide(s)
        except (KeyError, TypeError, ValueError) as exc:
            log.warning("Dropping %s slide (%s)", t, exc)
            continue
        if ok:
            out.append(s)
    if media == "image":
        out = [s for s in out if s["type"] != "cta"][:1]
    elif out:
        out = [s for s in out if s["type"] != "cta"][:7] + [{"type": "cta"}]
    return out


def _check_slide(s: dict) -> bool:
    t = s["type"]
    need = {"cover": ["hook"], "poster": ["text"], "bignum": ["value", "label"], "split": ["title", "items"],
            "list": ["title", "items"], "mouthmap": ["title"], "step": ["n", "area", "text"],
            "calendar": ["title", "text"], "compare": ["title", "a", "b"], "icons": ["title", "items"],
            "textpost": ["text"], "notes": ["title", "items"], "photo": ["photo", "lines"],
            "quiz": ["question", "options"], "answer": ["answer", "text"], "cta": []}[t]
    missing = [k for k in need if not s.get(k)]
    if missing:
        raise ValueError(f"missing {', '.join(missing)}")
    if t == "split":
        s["items"] = [i for i in s["items"] if isinstance(i, dict) and re.search(r"\d", str(i.get("value", "")))][:2]
        if len(s["items"]) < 2:
            raise ValueError("split needs two percentage items")
    if t in ("list",):
        s["items"] = _strs(s["items"], 5)
    if t == "notes":
        s["items"] = _strs(s["items"], 7)
    if t == "compare":
        s["a"], s["b"] = _strs(s["a"], 4), _strs(s["b"], 4)
    if t == "quiz":
        s["options"] = _strs(s["options"], 3)
    if t == "icons":
        s["items"] = [{**i, "icon": i.get("icon") if i.get("icon") in art.ICONS else "check"}
                      for i in s["items"] if isinstance(i, dict) and i.get("label")][:6]
        if len(s["items"]) < 3:
            raise ValueError("icons needs 3 items")
        if len(s["items"]) in (4, 5):
            s["items"] = s["items"][:3]
    if t == "mouthmap" and s.get("zones"):
        s["zones"] = [z for z in s["zones"] if z in art.ZONES] or None
    if t == "step":
        s["n"] = str(s["n"])
        if s.get("zone") not in art.ZONES:
            s.pop("zone", None)
            if s.get("icon") not in art.ICONS:
                s["icon"] = "mirror"
    if t == "cover" and s.get("art") and s["art"] != "mouthmap" and s["art"] not in art.ICONS:
        s.pop("art")
    if t == "photo":
        key = s["photo"] if s["photo"] in PHOTOS else None
        if not key:
            raise ValueError(f"no licensed photo {s['photo']!r}")
        s["photo"], s["credit"] = posts2.sign_photo(key)
        s["lines"] = _strs(s["lines"], 3)
    if t == "answer":
        s["correct"] = bool(s.get("correct", True))
    return True


def render_post(spec: dict, out_dir: str | None = None) -> list[str]:
    out_dir = out_dir or tempfile.mkdtemp(prefix="oc_post_")
    return posts2.render(spec["slides"], out_dir=out_dir)


# ── reels ─────────────────────────────────────────────────────────────────────

def write_reel(idea: dict, ask) -> dict:
    suggested = _templates_for(idea, "reel")
    spec_lines = "\n".join(f"  {k}: {v}" for k, v in VISUAL_SPEC.items())
    prompt = (
        f"Write a faceless Instagram Reel for OralCheck as a sequence of beats.\n\n{_slot_block(idea)}\n\n"
        "Each beat is one spoken sentence with one visual. A calm voice reads `say`; captions show "
        "the words as they are spoken; the visual animates in time with named words.\n\n"
        f"Visual types and their fields:\n{spec_lines}\n\n{_vocab()}\n"
        + (f"This shape is usually built from: {', '.join(suggested)}.\n" if suggested else "")
        + "Rules:\n"
        "  - 6 to 7 beats, 55 to 68 spoken words in total (about 30 seconds). The first beat's `say` "
        "is the hook line. The last beat is a cta visual saying to check your risk, free, at oralcheck.org.\n"
        "  - Each `say` is one sentence of at most 13 words, written to be heard: short words, no "
        "parentheses, no abbreviations a voice would stumble on. Write numbers the way the visual shows them.\n"
        "  - Vary the visuals: no visual type twice in a row, at least three different types, and "
        "at most TWO beats of type text. A reel of captions on plain colour is the failure here.\n"
        "  - Any word a visual waits for must appear in that beat's `say`.\n"
        "  - Optional per beat: emphasis (1-2 words from `say` to colour in the captions), "
        "hold (seconds of silence after, 0 to 2.2).\n"
        "  - Never present a home check as a test or a diagnosis.\n"
        "  - Only the facts given. Survival: 'while still localized', 'once it has spread to distant "
        "sites', never Stage I or IV. No em dashes. Never say 'we'.\n\n"
        'Return only JSON: {"beats": [{"say": "...", "visual": {"type": "...", ...}, "emphasis": [], '
        '"hold": 0}], "caption": "...", "hashtags": [5 lowercase tags]}. The caption is 50 to 120 '
        "words and ends with a call to action naming oralcheck.org."
    )
    data = _attempt(prompt, ask, _reel_problems)
    data.setdefault("hook", data["beats"][0]["say"])
    return _finish(data, [b["visual"].get("credit", "") for b in data["beats"]])


def validate_beats(beats: list) -> list[dict]:
    out = []
    for b in beats if isinstance(beats, list) else []:
        if not isinstance(b, dict) or not str(b.get("say", "")).strip():
            continue
        b["say"] = _tidy(b["say"])
        v = b.get("visual") if isinstance(b.get("visual"), dict) else {}
        kind = v.get("type")
        if kind not in reel2.VISUALS:
            v = {"type": "text"}
        try:
            _check_visual(v)
        except (KeyError, TypeError, ValueError) as exc:
            log.warning("Beat visual %s replaced with text (%s)", kind, exc)
            v = {"type": "text"}
        b["visual"] = v
        b["hold"] = max(0.0, min(float(b.get("hold") or 0), 2.4))
        b["emphasis"] = _strs(b.get("emphasis"), 2)
        out.append(b)
    out = [b for b in out if b["visual"]["type"] != "cta"]
    out.append({"say": "Check your own risk, free, at oralcheck.org.", "hold": 1.8,
                "visual": {"type": "cta"}})
    return out[:9]


def _check_visual(v: dict) -> None:
    t = v["type"]
    if t == "quiz":
        v["options"] = _strs(v["options"], 2)
        if not v.get("question") or len(v["options"]) < 2:
            raise ValueError("quiz needs a question and two options")
    elif t == "myth":
        if not v.get("myth") or not v.get("fact"):
            raise ValueError("myth needs myth and fact")
    elif t == "mouthmap":
        v["zones"] = [z for z in (v.get("zones") or []) if z in art.ZONES] or None
    elif t == "photo":
        if v.get("photo") not in PHOTOS:
            raise ValueError(f"no licensed photo {v.get('photo')!r}")
        v["photo"], v["credit"] = posts2.sign_photo(v["photo"])
    elif t == "icons":
        v["items"] = [{**i, "icon": i.get("icon") if i.get("icon") in art.ICONS else "check"}
                      for i in v.get("items", []) if isinstance(i, dict) and i.get("label")][:6]
        if len(v["items"]) < 2:
            raise ValueError("icons needs at least two items")
    elif t == "stat":
        if not v.get("value") or not v.get("label"):
            raise ValueError("stat needs value and label")
    elif t == "bars":
        items = [i for i in v.get("items", []) if isinstance(i, dict)][:2]
        for i in items:
            i["value"] = float(re.sub(r"[^\d.]", "", str(i["value"])))
        if len(items) < 2:
            raise ValueError("bars needs two items")
        v["items"] = items
    for k, val in list(v.items()):
        if isinstance(val, str):
            v[k] = _tidy(val)


def render_reel(spec: dict, out_path: str, *, tts, music: str | None = None) -> str:
    reel2.build({"beats": spec["beats"]}, out_path, tts=tts, music=music)
    return out_path
