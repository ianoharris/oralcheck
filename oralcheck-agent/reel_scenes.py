"""
Reel scene archetypes, the moving-image half of the design system.

`layouts.py` gave carousels sixteen real designs. Reels never got that work:
every segment rendered as a kicker plus a line of kinetic type, or a single
big number, over one of five backdrops. Five backdrops behind one shape is not
variety, it is the same scene repainted, and a four-segment reel showed the
same scene four times.

This module adds structurally different scenes, each mapped to a content
pillar the account actually posts:

    splitstat   two numbers compared          <- stats
    contrast    the myth, then the fact       <- myth busting
    checklist   items ticking in one by one   <- self exam, signs
    quote       a pulled line with weight     <- HPV connection, caveats
    term        a word and what it means      <- clinical vocabulary
    enumerate   step N of M                   <- self exam, prevention

Two constraints every scene here has to respect:

* **Seekable.** Frames are rendered by setting `--t` from 0 to 1 and
  screenshotting, so audio sync is exact. Anything animated must use the
  `.anim` class with a `--d` delay and no JS-driven timing, or the rendered
  frame stops matching the narration.
* **Legible muted on a phone.** Most reels are watched without sound, at
  arm's length. Type is huge, contrast is high, and no scene depends on
  reading more than about a dozen words.

Every scene degrades: given fewer fields than it wants it renders what it has,
and given nothing usable it returns None so the caller falls back to the
ordinary headline scene. Adding one means writing the function, adding it to
SCENES, and describing it in REEL_SCENE_SPEC in oralcheck_agent.py. It is
unreachable until it is in both.
"""
from __future__ import annotations

import render_html as R

_e = R._e


def _fit(text: str, base: int, ideal: int, floor: float = 0.58) -> int:
    """Shrink type as copy grows, so a long line gets smaller, not clipped."""
    n = len(text or "")
    if n <= ideal:
        return base
    return int(base * max(floor, (ideal / n) ** 0.5))


# ---------------------------------------------------------------------------
# CSS. Appended to the shared kinetic stylesheet, so it inherits the tokens,
# the paused/seekable .anim machinery and the brand row.
# ---------------------------------------------------------------------------

EXTRA_CSS = """
/* --- splitstat: two numbers, weighed against each other ------------------ */
.sp { display:flex; flex-direction:column; gap:56px; }
.sprow { display:flex; align-items:baseline; gap:36px; }
.spval { font-family:'DM Serif Display', Georgia, serif; font-size:220px; line-height:0.92;
  font-variant-numeric:tabular-nums; animation-name:popIn; animation-duration:0.8s; }
.spval.good { color:var(--teal-brt); }
.spval.bad  { color:var(--coral); }
.splab { font-size:46px; line-height:1.2; color:var(--text-soft); max-width:640px;
  animation-name:fadeUp; animation-duration:0.7s; }
.spvs { font-size:38px; font-weight:600; letter-spacing:0.18em; text-transform:uppercase;
  color:var(--muted); animation-name:fadeUp; animation-duration:0.6s; }

/* --- contrast: struck-through myth above, the fact below ----------------- */
.ct { display:flex; flex-direction:column; gap:52px; }
.ctmyth { position:relative; display:inline-block; font-size:66px; line-height:1.22;
  color:var(--muted); animation-name:fadeUp; animation-duration:0.7s; }
.ctstrike { position:absolute; left:0; right:0; top:52%; height:6px; border-radius:3px;
  background:var(--muted); transform-origin:left center;
  animation-name:sweep; animation-duration:0.6s; }
.ctfact { font-family:'DM Serif Display', Georgia, serif; font-size:92px; line-height:1.1;
  color:var(--text); animation-name:riseIn; animation-duration:0.85s; }
.ctrule { width:120px; height:8px; border-radius:4px; background:var(--coral);
  transform-origin:left center; animation-name:sweep; animation-duration:0.6s; }

/* --- checklist: items arriving one at a time ---------------------------- */
.ck { display:flex; flex-direction:column; gap:44px; }
.ckrow { display:flex; align-items:flex-start; gap:32px;
  animation-name:riseIn; animation-duration:0.7s; }
.ckmark { flex:none; width:64px; height:64px; border-radius:50%;
  border:5px solid var(--teal-brt); position:relative; margin-top:6px; }
.ckmark::after { content:''; position:absolute; left:18px; top:8px; width:20px; height:34px;
  border-right:6px solid var(--teal-brt); border-bottom:6px solid var(--teal-brt);
  transform:rotate(42deg); }
.cktext { font-size:62px; line-height:1.22; color:var(--text); }

/* --- quote: a line given room ------------------------------------------- */
.qt { display:flex; flex-direction:column; gap:40px; }
.qtmark { font-family:'DM Serif Display', Georgia, serif; font-size:220px; line-height:0.6;
  color:var(--coral); opacity:0.9; animation-name:fadeDown; animation-duration:0.7s; }
.qtbody { font-family:'DM Serif Display', Georgia, serif; font-size:86px; line-height:1.16;
  color:var(--text); animation-name:riseIn; animation-duration:0.9s; }
.qtattr { font-size:38px; letter-spacing:0.06em; color:var(--muted);
  animation-name:fadeUp; animation-duration:0.7s; }

/* --- term: a word and what it means ------------------------------------- */
.tm { display:flex; flex-direction:column; gap:38px; }
.tmword { font-family:'DM Serif Display', Georgia, serif; font-size:118px; line-height:1.02;
  color:var(--teal-brt); animation-name:riseIn; animation-duration:0.8s; }
.tmsay { font-size:40px; letter-spacing:0.05em; color:var(--muted); font-style:italic;
  animation-name:fadeUp; animation-duration:0.6s; }
.tmrule { width:100%; height:4px; background:var(--teal); opacity:0.5; transform-origin:left center;
  animation-name:sweep; animation-duration:0.7s; }
.tmdef { font-size:62px; line-height:1.26; color:var(--text);
  animation-name:fadeUp; animation-duration:0.8s; }

/* --- enumerate: step N of M --------------------------------------------- */
.en { display:flex; flex-direction:column; gap:44px; }
.ennum { display:flex; align-items:baseline; gap:22px;
  animation-name:popIn; animation-duration:0.75s; }
.enbig { font-family:'DM Serif Display', Georgia, serif; font-size:200px; line-height:0.9;
  color:var(--coral); font-variant-numeric:tabular-nums; }
.enof { font-size:46px; letter-spacing:0.12em; text-transform:uppercase; color:var(--muted); }
.entext { font-family:'DM Serif Display', Georgia, serif; font-size:88px; line-height:1.12;
  color:var(--text); animation-name:riseIn; animation-duration:0.85s; }
.endots { display:flex; gap:20px; margin-top:26px;
  animation-name:fadeUp; animation-duration:0.6s; }
.endot { width:74px; height:12px; border-radius:6px; background:var(--muted); opacity:0.35; }
.endot.on { background:var(--coral); opacity:1; }
"""


# ---------------------------------------------------------------------------
# Scenes. Each returns the inner HTML for `.content`, or None to fall back.
# ---------------------------------------------------------------------------

def _splitstat(s: dict, t: dict) -> str | None:
    pair = s.get("pair") or []
    if len(pair) < 2:
        return None
    a, b = pair[0], pair[1]
    av, bv = str(a.get("value", "")).strip(), str(b.get("value", "")).strip()
    if not av or not bv:
        return None
    vs = _e(str(s.get("versus", "vs")).strip() or "vs")
    return (
        "<div class='sp'>"
        f"<div class='sprow'><span class='anim spval good' style='--d:0.25'>{_e(av)}</span>"
        f"<span class='anim splab' style='--d:0.5'>{_e(str(a.get('label','')))}</span></div>"
        f"<div class='anim spvs' style='--d:0.7'>{vs}</div>"
        f"<div class='sprow'><span class='anim spval bad' style='--d:0.9'>{_e(bv)}</span>"
        f"<span class='anim splab' style='--d:1.15'>{_e(str(b.get('label','')))}</span></div>"
        "</div>"
    )


def _contrast(s: dict, t: dict) -> str | None:
    myth, fact = str(s.get("myth", "")).strip(), str(s.get("fact", "")).strip()
    if not myth or not fact:
        return None
    return (
        "<div class='ct'>"
        f"<div><span class='anim ctmyth' style='--d:0.15;font-size:{_fit(myth,66,44)}px'>{_e(myth)}"
        "<span class='anim ctstrike' style='--d:0.7'></span></span></div>"
        "<div class='anim ctrule' style='--d:0.95'></div>"
        f"<div class='anim ctfact' style='--d:1.05;font-size:{_fit(fact,92,42)}px'>{_e(fact)}</div>"
        "</div>"
    )


def _checklist(s: dict, t: dict) -> str | None:
    items = [str(i).strip() for i in (s.get("items") or []) if str(i).strip()][:4]
    if len(items) < 2:
        return None
    longest = max(len(i) for i in items)
    size = _fit("x" * longest, 62, 30)
    rows = "".join(
        f"<div class='anim ckrow' style='--d:{0.25 + i * 0.45:.2f}'>"
        f"<div class='ckmark'></div>"
        f"<div class='cktext' style='font-size:{size}px'>{_e(it)}</div></div>"
        for i, it in enumerate(items)
    )
    return f"<div class='ck'>{rows}</div>"


def _quote(s: dict, t: dict) -> str | None:
    body = str(s.get("quote", "")).strip()
    if not body:
        return None
    attr = str(s.get("attrib", "")).strip()
    attr_html = (f"<div class='anim qtattr' style='--d:1.1'>{_e(attr)}</div>"
                 if attr else "")
    return (
        "<div class='qt'>"
        "<div class='anim qtmark' style='--d:0.1'>&ldquo;</div>"
        f"<div class='anim qtbody' style='--d:0.4;font-size:{_fit(body,86,60)}px'>{_e(body)}</div>"
        f"{attr_html}</div>"
    )


def _term(s: dict, t: dict) -> str | None:
    word = str(s.get("term", "")).strip()
    definition = str(s.get("definition", "")).strip()
    if not word or not definition:
        return None
    say = str(s.get("say", "")).strip()
    say_html = f"<div class='anim tmsay' style='--d:0.45'>{_e(say)}</div>" if say else ""
    return (
        "<div class='tm'>"
        f"<div class='anim tmword' style='--d:0.2;font-size:{_fit(word,118,14)}px'>{_e(word)}</div>"
        f"{say_html}"
        "<div class='anim tmrule' style='--d:0.6'></div>"
        f"<div class='anim tmdef' style='--d:0.8;font-size:{_fit(definition,62,52)}px'>{_e(definition)}</div>"
        "</div>"
    )


def _enumerate(s: dict, t: dict) -> str | None:
    text = str(s.get("caption", "")).strip()
    try:
        idx = int(s.get("index", 0))
        of = int(s.get("of", 0))
    except (TypeError, ValueError):
        return None
    if not text or idx < 1 or of < 1 or idx > of:
        return None
    dots = "".join(
        f"<span class='endot{' on' if i < idx else ''}'></span>" for i in range(of)
    )
    return (
        "<div class='en'>"
        f"<div class='anim ennum' style='--d:0.2'><span class='enbig'>{idx}</span>"
        f"<span class='enof'>of {of}</span></div>"
        f"<div class='anim entext' style='--d:0.55;font-size:{_fit(text,88,40)}px'>{_e(text)}</div>"
        f"<div class='anim endots' style='--d:0.9'>{dots}</div>"
        "</div>"
    )


SCENES = {
    "splitstat": _splitstat,
    "contrast": _contrast,
    "checklist": _checklist,
    "quote": _quote,
    "term": _term,
    "enumerate": _enumerate,
}

# Which scenes need which fields. Used by the agent to validate a script and to
# decide whether a segment can actually take the scene it asked for.
SCENE_FIELDS = {
    "splitstat": ("pair",),
    "contrast": ("myth", "fact"),
    "checklist": ("items",),
    "quote": ("quote",),
    "term": ("term", "definition"),
    "enumerate": ("caption", "index", "of"),
}


def render(segment: dict, theme: dict) -> str | None:
    """Inner HTML for `.content`, or None to fall back to the headline scene."""
    fn = SCENES.get(str(segment.get("scene", "")).strip().lower())
    if not fn:
        return None
    try:
        return fn(segment, theme)
    except Exception:            # a malformed segment must not kill the reel
        return None
