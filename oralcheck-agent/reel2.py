"""
Faceless reels, second generation: one timeline, cut to the voice.

The first engine rendered each segment as its own clip, animated for 2.6s and
then held, so a reel was five slow scenes stitched together. This one renders
the whole reel as a single HTML timeline, captured frame by frame, where every
caption word, highlight, counter, zoom and sound effect is placed on the
voiceover's own word timings (align.py). Something on screen changes every
second or two, and diagrams react to the word being spoken: say "tongue" and
the tongue lights up.

A plan is a list of beats. Each beat is one spoken line plus one visual:

    {"say": "Quick test. A mouth sore, three weeks, no pain. Normal?",
     "visual": {"type": "quiz", ...}, "hold": 2.2, "bg": "ink"}

`hold` adds silent time after the line (a quiz countdown). `bg` picks the
colour block; by default beats rotate through the palette so every beat is a
visible cut. Visual types are the keys of VISUALS below.

Costs nothing beyond the voice the pipeline already pays for: graphics are
code, sound effects are synthesized with ffmpeg, alignment runs locally.
"""
from __future__ import annotations

import base64
import json
import logging
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path

import align
import art
import posts2

log = logging.getLogger("oralcheck.reel2")

W, H, FPS = 1080, 1920, 30
GAP = 0.24                 # silence between beats
VOICE_TEMPO = 1.05         # a touch faster than Kokoro's calm read; 1.12 felt rushed
JPEG_Q = 90
MUSIC_VOL = 0.11           # matches REEL_MUSIC_VOL in oralcheck_agent
SFX_VOL = {"whoosh": 0.22, "pop": 0.30, "tick": 0.40, "ding": 0.32, "thud": 0.55}

INK, TEAL, CORAL, CREAM, AMBER = "#14201f", "#0d7377", "#e8634a", "#f4f1ea", "#f2c14e"

PAL = {
    "ink": {"bg": "#0d1a1b", "fg": CREAM, "active": AMBER, "accent": CORAL, "card": "#21403f", "cardfg": CREAM},
    "teal": {"bg": TEAL, "fg": CREAM, "active": AMBER, "accent": AMBER, "card": CREAM, "cardfg": INK},
    "coral": {"bg": CORAL, "fg": "#fff8f0", "active": INK, "accent": INK, "card": "#fff8f0", "cardfg": INK},
    "butter": {"bg": AMBER, "fg": INK, "active": "#c4452a", "accent": "#c4452a", "card": "#fff8f0", "cardfg": INK},
    "cream": {"bg": CREAM, "fg": INK, "active": "#d9552f", "accent": "#d9552f", "card": "#ffffff", "cardfg": INK},
}
ROTATION = ["ink", "coral", "teal", "ink", "butter", "teal", "cream"]

ZONE_WORDS = {"lips": "lip", "cheeks": "cheek", "gums": "gum", "tongue": "tongue",
              "floor": "floor", "roof": "roof", "throat": "throat"}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {r.stderr.decode()[-600:]}")


def _duration(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True)
    return float(out.stdout.strip() or 0)


def A(anim: str, at: float, dur: float = 0.4, base: str = "", **data) -> str:
    """Attributes that put an element on the timeline."""
    extra = "".join(f" data-{k}='{v}'" for k, v in data.items())
    b = f" data-base='{base}'" if base else ""
    return f" data-anim='{anim}' data-at='{at:.3f}' data-dur='{dur:.3f}'{b}{extra}"


def _tag_svg(svg: str, el_id: str, attrs: str) -> str:
    return svg.replace(f"id='{el_id}'", f"id='{el_id}'{attrs}", 1)


class Cue:
    """Timing context for one beat, handed to its visual builder."""

    def __init__(self, idx, start, speech_end, end, words, pal, sfx):
        self.i, self.s, self.se, self.e = idx, start, speech_end, end
        self.words, self.pal, self.sfx = words, pal, sfx

    def at(self, word: str, default: float | None = None) -> float:
        key = align.norm(word)
        for w in self.words:
            if key and align.norm(w["text"]).startswith(key):
                return w["start"]
        return self.s + 0.3 if default is None else default

    def frac(self, f: float) -> float:
        return self.s + (self.se - self.s) * f

    def fx(self, kind: str, t: float) -> None:
        self.sfx.append((kind, t))


# ---------------------------------------------------------------------------
# Visuals. Each returns the HTML for the beat's visual area.
# ---------------------------------------------------------------------------

def v_text(v, c):
    if v.get("kicker"):
        return f"<div class='pill big'{A('pop', c.s, 0.35)}>{posts2.esc(v['kicker'])}</div>"
    return ""


def v_quiz(v, c):
    first = c.i == 0
    t0 = -1 if first else c.s
    opts = ""
    for k, o in enumerate(v["options"]):
        t = c.at(v.get("option_words", [None, None])[k] or "", c.frac(0.55 + 0.2 * k))
        c.fx("pop", t)
        opts += (f"<div class='opt card'{A('pop', t, 0.35)}><span class='optk'>{chr(65 + k)}</span>"
                 f"<span>{posts2.rich(o)}</span></div>")
    ring = ""
    hold = c.e - c.se - GAP
    if hold > 0.6:
        circ = 2 * math.pi * 70
        ring = (f"<div class='ringwrap'{A('pop', c.se, 0.3)}>"
                f"<svg viewBox='0 0 180 180' width='200' height='200'>"
                f"<circle cx='90' cy='90' r='70' fill='none' stroke='rgba(127,127,127,0.25)' stroke-width='14'/>"
                f"<circle cx='90' cy='90' r='70' fill='none' stroke='{c.pal['accent']}' stroke-width='14' "
                f"stroke-linecap='round' stroke-dasharray='{circ:.1f}' transform='rotate(-90 90 90)'"
                f"{A('ring', c.se, hold, c=f'{circ:.1f}')}/></svg>"
                f"<div class='ringnum'{A('countnum', c.se, hold)}>{round(hold)}</div></div>")
        for k in range(int(hold)):
            c.fx("tick", c.se + k)
    return (f"<div class='pill big'{A('fade', t0, 0.2)}>{posts2.esc(v.get('kicker', 'Quick test'))}</div>"
            f"<div class='q heavy'{A('fade', t0, 0.25)}>{posts2.rich(v['question'])}</div>"
            f"<div class='opts'>{opts}</div>{ring}")


def v_calendar(v, c):
    grid = art.calendar_grid(animated=True, uid=f"cal{c.i}", cell=150, gap=20,
                             fill=TEAL if c.pal["bg"] != TEAL else "#0d1a1b", flag=CORAL,
                             text="#fff8f0", empty="rgba(127,127,127,0.22)")
    flag_t = c.at(v.get("flag_word", "weeks"), c.frac(0.75))
    fill_end = max(c.s + 0.6, flag_t - 0.15)
    step = (fill_end - c.s) / 14
    for n in range(1, 15):
        grid = _tag_svg(grid, f"cal{c.i}-d{n}", A("pop", c.s + n * step - step, 0.22))
    grid = _tag_svg(grid, f"cal{c.i}-d15", A("pop", flag_t, 0.4))
    c.fx("pop", flag_t)
    title = (f"<div class='vtitle heavy'{A('rise', c.s, 0.35)}>{posts2.rich(v['title'])}</div>"
             if v.get("title") else "")
    return f"{title}<div style='width:860px'>{grid}</div>"


def v_bars(v, c):
    rows = ""
    for k, item in enumerate(v["items"][:2]):
        val = float(item["value"])
        t = c.at(item.get("word", f"{item['value']}"), c.frac(0.3 + 0.4 * k))
        color = AMBER if k == 0 else CORAL
        c.fx("pop", t)
        rows += (f"<div class='barrow'{A('rise', c.s + 0.1 + 0.15 * k, 0.3)}>"
                 f"<div class='barhead'><span class='barnum heavy' style='color:{color}'"
                 f"{A('count', t, 0.9, to=val, suf='%')}>0%</span>"
                 f"<span class='barlab'>{posts2.esc(item['label'])}</span></div>"
                 f"<div class='track'><div class='fillbar' style='background:{color};width:0'"
                 f"{A('fill', t, 0.9, to=val)}></div></div></div>")
    src = f"<div class='src'{A('fade', c.s + 0.4, 0.4)}>{posts2.esc(v['source'])}</div>" if v.get("source") else ""
    return f"<div class='bars'>{rows}</div>{src}"


def v_mouthmap(v, c):
    zones = v.get("zones") or art.ZONES
    uid = f"mm{c.i}"
    svg = art.mouth_map(badges=zones, animated=True, uid=uid)
    prev, times = c.s + 0.2, []
    for z in zones:
        t = c.at(ZONE_WORDS[z], prev + 0.35)
        times.append(max(t, prev))
        prev = times[-1]
    for k, (z, t) in enumerate(zip(zones, times)):
        off = times[k + 1] if k + 1 < len(zones) else c.e + 1
        svg = _tag_svg(svg, f"{uid}-z-{z}", A("zone", t, 0.25, off=f"{off:.3f}"))
        svg = _tag_svg(svg, f"{uid}-b-{z}", A("pop", t, 0.3))
        c.fx("pop", t)
    title = (f"<div class='vtitle heavy'{A('rise', c.s, 0.35)}>{posts2.rich(v['title'])}</div>"
             if v.get("title") else "")
    return f"{title}<div class='mapcard'{A('pop', c.s, 0.4)}>{svg}</div>"


def v_photo(v, c):
    path = v["photo"]
    label = (f"<div class='chip'{A('pop', c.s + 0.35, 0.3)}>{posts2.esc(v['label'])}</div>"
             if v.get("label") else "")
    credit = f"<div class='credit'>{posts2.esc(v.get('credit', ''))}</div>" if v.get("credit") else ""
    return (f"<div class='photocard'{A('pop', c.s, 0.35)}>"
            f"<img src='{posts2._data_uri(path)}'{A('ken', c.s, max(c.e - c.s, 1))}>{label}</div>{credit}")


def v_myth(v, c):
    strike_t = c.at(v.get("strike_word", ""), c.frac(0.35)) if v.get("strike_word") else c.frac(0.35)
    fact_t = c.at(v.get("fact_word", ""), c.frac(0.55)) if v.get("fact_word") else c.frac(0.55)
    c.fx("thud", strike_t)
    c.fx("ding", fact_t)
    return (f"<div class='pill big' style='background:{c.pal['fg']};color:{c.pal['bg']}'{A('pop', c.s, 0.3)}>Myth</div>"
            f"<div class='mythline'{A('rise', c.s + 0.1, 0.35)}><span>{posts2.esc(v['myth'])}</span>"
            f"<i class='strike'{A('strike', strike_t, 0.35)}></i></div>"
            f"<div class='pill big' style='margin-top:60px;background:{c.pal['accent']};color:{c.pal['bg']}'"
            f"{A('pop', fact_t, 0.3)}>Fact</div>"
            f"<div class='factline heavy'{A('rise', fact_t + 0.08, 0.35)}>{posts2.rich(v['fact'])}</div>")


def v_icons(v, c):
    tiles = ""
    prev = c.s
    for it in v["items"][:6]:
        t = c.at(it.get("word", it["label"].split()[0]), prev + 0.4)
        prev = t
        c.fx("pop", t)
        tiles += (f"<div class='tile card'{A('pop', t, 0.32)}>{art.icon(it['icon'], color=c.pal['cardfg'], size=120, stroke=2.8)}"
                  f"<div>{posts2.esc(it['label'])}</div></div>")
    title = (f"<div class='vtitle heavy'{A('rise', c.s, 0.35)}>{posts2.rich(v['title'])}</div>"
             if v.get("title") else "")
    return f"{title}<div class='tiles'>{tiles}</div>"


def v_stat(v, c):
    raw = str(v["value"])
    num = float(re.sub(r"[^\d.]", "", raw) or 0)
    dec = len(raw.split(".")[1]) if "." in raw else 0
    suf = re.sub(r"[\d.,]", "", raw)
    t = c.at(v.get("word", raw), c.s + 0.15)
    c.fx("pop", t)
    return (f"<div class='bignum heavy'{A('count', t, 1.1, to=num, dec=dec, suf=suf)}>0</div>"
            f"<div class='statlab'{A('rise', t + 0.3, 0.35)}>{posts2.rich(v['label'])}</div>"
            + (f"<div class='src'{A('fade', t + 0.5, 0.4)}>{posts2.esc(v['source'])}</div>" if v.get("source") else ""))


def v_cta(v, c):
    logo = posts2._data_uri(posts2._LOGO)
    c.fx("ding", c.s + 0.5)
    return (f"<img class='ctalogo' src='{logo}'{A('pop', c.s, 0.35)}>"
            f"<div class='ctahead'{A('rise', c.s + 0.15, 0.35)}>{posts2.rich(v.get('headline', posts2.CTA_HEADLINE))}</div>"
            f"<div class='ctaurl heavy'{A('slam', c.s + 0.5, 0.3, rot=0)}>oralcheck.org</div>"
            f"<div class='ctasub'{A('fade', c.s + 0.8, 0.4)}>{posts2.esc(v.get('sub', 'Free. Private. No account.'))}</div>")


VISUALS = {
    "text": v_text, "quiz": v_quiz, "calendar": v_calendar,
    "bars": v_bars, "mouthmap": v_mouthmap, "photo": v_photo, "myth": v_myth,
    "icons": v_icons, "stat": v_stat, "cta": v_cta,
}
# Visuals that carry their own words, so the spoken caption moves out of the way.
NO_CAPTIONS = {"cta"}
CENTER_CAPTIONS = {"text"}


# ---------------------------------------------------------------------------
# Captions
# ---------------------------------------------------------------------------

def _chunks(words: list[dict], end: float, max_words: int = 3, max_chars: int = 16) -> list[list[dict]]:
    out, cur = [], []
    for w in words:
        cur.append(w)
        text = " ".join(x["text"] for x in cur)
        if len(cur) >= max_words or len(text) >= max_chars or re.search(r"[.,?!:;]$", w["text"]):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def _caption_html(beats_words, timing, emphasis) -> tuple[str, list]:
    html, spans = [], []
    for bi, words in enumerate(beats_words):
        start, speech_end, end, kind = timing[bi]
        if kind in NO_CAPTIONS or not words:
            continue
        mode = "mid" if kind in CENTER_CAPTIONS else "low"
        groups = _chunks(words, speech_end)
        for gi, g in enumerate(groups):
            cs = g[0]["start"]
            ce = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else min(end, g[-1]["end"] + 0.5)
            spans.append((cs, ce))
            inner = "".join(
                f"<span class='w{' em' if align.norm(w['text']) in emphasis[bi] else ''}' "
                f"data-s='{w['start']:.3f}'>{posts2.esc(w['text'])}</span>" for w in g)
            html.append(f"<div class='chunk {mode}' data-s='{cs:.3f}' data-e='{ce:.3f}' data-beat='{bi}'>{inner}</div>")
    return "".join(html), spans


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def _css() -> str:
    dm, ss = posts2._font("DMSerifDisplay-Regular.ttf"), posts2._font("SourceSans3-Regular.ttf")
    return f"""
@font-face {{ font-family:'DM Serif Display'; src:url(data:font/truetype;base64,{dm}); }}
@font-face {{ font-family:'Source Sans 3'; src:url(data:font/truetype;base64,{ss}); font-weight:200 900; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:#000; }}
body {{ font-family:'Source Sans 3', sans-serif; -webkit-font-smoothing:antialiased; }}
#stage {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; }}
#cam {{ position:absolute; inset:0; transform-origin:50% 38%; }}
.beat {{ position:absolute; inset:0; display:none; color:var(--fg); }}
.vis {{ position:absolute; left:80px; right:80px; top:240px; height:920px; display:flex; flex-direction:column;
  align-items:center; justify-content:center; gap:34px; text-align:center; }}
.heavy {{ font-weight:900; letter-spacing:-0.03em; line-height:1.0; }}
mark {{ color:var(--markfg, #14201f); padding:0 0.08em; border-radius:0.08em;
  background:linear-gradient(var(--active), var(--active)) no-repeat 0 62% / 100% 82%; }}
.pill {{ display:inline-block; padding:14px 30px; border-radius:999px; background:var(--fg); color:var(--bg);
  font-weight:900; font-size:34px; letter-spacing:0.1em; text-transform:uppercase; }}
.card {{ background:var(--card); color:var(--cardfg); border-radius:34px; }}
.q {{ font-size:96px; max-width:900px; }}
.opts {{ display:flex; flex-direction:column; gap:22px; width:880px; }}
.opt {{ display:flex; align-items:center; gap:26px; padding:30px 36px; font-size:50px; font-weight:800; text-align:left; }}
.optk {{ font-weight:900; font-size:68px; color:var(--accent); }}
.ringwrap {{ position:relative; width:200px; height:200px; }}
.ringnum {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-weight:900; font-size:96px; }}
.vtitle {{ font-size:92px; max-width:920px; }}
.bars {{ width:900px; display:flex; flex-direction:column; gap:60px; text-align:left; }}
.barhead {{ display:flex; align-items:baseline; gap:26px; }}
.barnum {{ font-size:200px; font-variant-numeric:tabular-nums; min-width:410px; }}
.barlab {{ font-size:48px; font-weight:800; line-height:1.12; }}
.track {{ height:34px; border-radius:17px; background:rgba(127,127,127,0.25); margin-top:16px; overflow:hidden; }}
.fillbar {{ height:100%; border-radius:17px; }}
.src {{ font-size:28px; font-weight:700; opacity:0.75; }}
.mapcard {{ width:960px; padding:30px 10px; border-radius:48px; background:#fff8f0; }}
.photocard {{ position:relative; width:920px; height:860px; border-radius:44px; overflow:hidden; }}
.photocard img {{ width:100%; height:100%; object-fit:cover; transform-origin:50% 50%; }}
.chip {{ position:absolute; left:34px; bottom:34px; right:34px; padding:20px 28px; border-radius:24px;
  background:rgba(255,248,240,0.95); color:#14201f; font-size:44px; font-weight:900; text-align:left; }}
.credit {{ font-size:24px; font-weight:600; opacity:0.7; margin-top:-14px; }}
.mythline {{ position:relative; font-size:66px; font-weight:800; opacity:0.75; max-width:900px; }}
.strike {{ position:absolute; left:-10px; right:-10px; top:52%; height:12px; border-radius:6px;
  background:var(--fg); transform-origin:left center; transform:scaleX(0); }}
.factline {{ font-size:96px; max-width:920px; }}
.tiles {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:24px; width:920px; }}
.tile {{ padding:34px 16px 28px; display:flex; flex-direction:column; align-items:center; gap:18px;
  font-size:36px; font-weight:900; }}
.bignum {{ font-size:270px; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.statlab {{ font-size:62px; font-weight:800; max-width:900px; line-height:1.15; }}
.ctalogo {{ width:210px; height:210px; border-radius:50%; background:#fff8f0; padding:14px; }}
.ctahead {{ font-family:'DM Serif Display', serif; font-size:100px; line-height:1.05; max-width:900px; }}
.ctaurl {{ font-size:112px; padding:28px 52px; border-radius:34px; background:var(--fg); color:var(--bg); }}
.ctasub {{ font-size:44px; font-weight:800; opacity:0.85; }}

#caps {{ position:absolute; inset:0; pointer-events:none; }}
.chunk {{ position:absolute; left:60px; right:60px; display:none; flex-wrap:wrap; justify-content:center;
  align-items:center; gap:0 26px; text-align:center; font-weight:900; letter-spacing:-0.02em; line-height:1.05;
  color:var(--cfg); text-shadow:0 6px 0 rgba(0,0,0,0.16); }}
.chunk.low {{ top:1200px; height:300px; font-size:104px; }}
.chunk.mid {{ top:640px; height:600px; font-size:150px; }}
.w {{ display:inline-block; opacity:0.6; }}
.w.said {{ opacity:1; }}
.w.on {{ color:var(--cactive); transform:scale(1.1); }}
.w.em.said {{ color:var(--cactive); }}
#bar {{ position:absolute; left:0; top:0; height:12px; background:rgba(255,255,255,0.75); mix-blend-mode:difference; }}
#mark {{ position:absolute; left:0; right:0; bottom:330px; text-align:center; font-size:30px; font-weight:800;
  letter-spacing:0.08em; opacity:0.55; color:var(--cfg); }}
"""


_RUNTIME = r"""
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eOut = p => 1 - Math.pow(1 - p, 3);
const eBack = p => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); };
const fmt = (v, d) => v.toLocaleString('en-US', {minimumFractionDigits: d, maximumFractionDigits: d});
let anims, beatEls, chunks, stage, cam, bar, caps;
function init() {
  anims = [...document.querySelectorAll('[data-anim]')].map(el => ({
    el, a: el.dataset.anim, at: +el.dataset.at, d: +el.dataset.dur || 0.4, base: el.dataset.base || ''}));
  beatEls = [...document.querySelectorAll('.beat')];
  chunks = [...document.querySelectorAll('.chunk')].map(el => ({
    el, s: +el.dataset.s, e: +el.dataset.e,
    words: [...el.querySelectorAll('.w')].map(w => ({el: w, s: +w.dataset.s}))}));
  stage = document.getElementById('stage'); cam = document.getElementById('cam');
  bar = document.getElementById('bar'); caps = document.getElementById('caps');
}
function anim(o, t) {
  const p = clamp((t - o.at) / o.d), el = o.el, on = t >= o.at;
  switch (o.a) {
    case 'pop': el.style.opacity = on ? clamp(p * 3) : 0;
      el.style.transform = `${o.base} scale(${0.55 + 0.45 * eBack(p)})`; break;
    case 'rise': el.style.opacity = clamp(p * 2.5);
      el.style.transform = `${o.base} translateY(${(1 - eOut(p)) * 70}px)`; break;
    case 'fade': el.style.opacity = p; break;
    case 'slam': el.style.opacity = on ? 1 : 0;
      el.style.transform = `${o.base} scale(${1 + 1.3 * (1 - eOut(p))}) rotate(${el.dataset.rot || 0}deg)`; break;
    case 'strike': el.style.transform = `scaleX(${eOut(p)})`; break;
    case 'count': { const to = +el.dataset.to, d = +(el.dataset.dec || 0);
      el.textContent = fmt(to * eOut(p), d) + (el.dataset.suf || ''); el.style.opacity = on ? 1 : 0; break; }
    case 'fill': el.style.width = (+el.dataset.to * eOut(p)) + '%'; break;
    case 'zone': { const off = +(el.dataset.off || 1e9);
      el.style.opacity = !on ? 0 : t < off ? clamp(p * 4) : 1 - 0.7 * clamp((t - off) / 0.25); break; }
    case 'ken': el.style.transform = `scale(${1.04 + 0.14 * clamp((t - o.at) / o.d)})`; break;
    case 'ring': el.style.strokeDashoffset = +el.dataset.c * clamp((t - o.at) / o.d); break;
    case 'countnum': el.textContent = Math.max(1, Math.ceil(o.d - Math.max(0, t - o.at))); break;
  }
}
function render(t) {
  let bi = BEATS.findIndex(b => t >= b.s && t < b.e);
  if (bi < 0) bi = BEATS.length - 1;
  const b = BEATS[bi];
  beatEls.forEach((el, i) => el.style.display = i === bi ? 'block' : 'none');
  for (const [k, v] of Object.entries(b.vars)) stage.style.setProperty(k, v);
  stage.style.background = b.vars['--bg'];
  // A cut on every beat: snap in slightly zoomed and settle, then drift.
  let sc = 1 + 0.07 * (1 - eOut(clamp((t - b.s) / 0.3))) + 0.03 * clamp((t - b.s) / Math.max(b.e - b.s, 0.1));
  for (const c of chunks) {
    const vis = t >= c.s && t < c.e;
    c.el.style.display = vis ? 'flex' : 'none';
    if (!vis) continue;
    c.el.style.transform = `scale(${0.82 + 0.18 * eBack(clamp((t - c.s) / 0.16))})`;
    c.words.forEach((w, k) => {
      const next = c.words[k + 1];
      w.el.classList.toggle('said', t >= w.s);
      w.el.classList.toggle('on', t >= w.s && (!next || t < next.s));
    });
    sc += 0.02 * (1 - eOut(clamp((t - c.s) / 0.22)));
  }
  cam.style.transform = `scale(${sc})`;
  for (const o of anims) anim(o, t);
  bar.style.width = (100 * t / TOTAL) + '%';
}
init();
window.render = render;
"""


def _page(beat_html: list[str], caps_html: str, beats_meta: list[dict], total: float) -> str:
    beats = "".join(f"<div class='beat'><div class='vis'>{h}</div></div>" for h in beat_html)
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{_css()}</style></head><body>"
            f"<div id='stage'><div id='cam'>{beats}</div><div id='caps'>{caps_html}</div>"
            f"<div id='mark'>oralcheck.org</div><div id='bar'></div></div>"
            f"<script>const BEATS = {json.dumps(beats_meta)}; const TOTAL = {total:.3f};{_RUNTIME}</script>"
            f"</body></html>")


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

_SFX_EXPR = {
    "whoosh": None,
    "pop": ("0.7*sin(2*PI*(520+900*exp(-28*t))*t)*exp(-22*t)", 0.16),
    "tick": ("0.6*sin(2*PI*1600*t)*exp(-70*t)", 0.07),
    "ding": ("0.5*(sin(2*PI*880*t)+0.55*sin(2*PI*1320*t))*exp(-5*t)", 0.7),
    "thud": ("0.9*sin(2*PI*(70+120*exp(-20*t))*t)*exp(-12*t)", 0.35),
}


def _make_sfx(workdir: str) -> dict[str, str]:
    paths = {}
    for name, spec in _SFX_EXPR.items():
        out = os.path.join(workdir, f"sfx_{name}.wav")
        if name == "whoosh":
            _run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anoisesrc=d=0.4:c=pink:a=0.6",
                  "-af", "highpass=f=500,lowpass=f=5000,afade=t=in:d=0.18,afade=t=out:st=0.18:d=0.22",
                  "-ar", "44100", "-ac", "1", out])
        else:
            expr, d = spec
            _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"aevalsrc='{expr}':d={d}:s=44100", "-ac", "1", out])
        paths[name] = out
    return paths


def _sfx_track(events, total, workdir) -> str | None:
    if not events:
        return None
    files = _make_sfx(workdir)
    events = sorted(events, key=lambda e: e[1])
    kept, last = [], {}
    for kind, t in events:
        if t < 0 or t > total:
            continue
        if kind == "pop" and t - last.get(kind, -9) < 0.22:
            continue
        kept.append((kind, t))
        last[kind] = t
    cmd = ["ffmpeg", "-y"]
    for kind, _ in kept:
        cmd += ["-i", files[kind]]
    parts = []
    for k, (kind, t) in enumerate(kept):
        ms = int(t * 1000)
        parts.append(f"[{k}:a]adelay={ms}|{ms},volume={SFX_VOL[kind]}[s{k}]")
    mix = "".join(f"[s{k}]" for k in range(len(kept)))
    parts.append(f"{mix}amix=inputs={len(kept)}:normalize=0,apad=whole_dur={total:.3f}[out]")
    out = os.path.join(workdir, "sfx.wav")
    _run(cmd + ["-filter_complex", ";".join(parts), "-map", "[out]", "-t", f"{total:.3f}",
                "-ar", "44100", "-ac", "2", out])
    return out


def _voice_track(wavs: list[str], pads: list[float], workdir: str) -> str:
    """Each beat's line, followed by its gap and hold, as one continuous track."""
    listing = os.path.join(workdir, "voice.txt")
    with open(listing, "w") as fh:
        for i, (w, pad) in enumerate(zip(wavs, pads)):
            seg = os.path.join(workdir, f"v{i:02d}.wav")
            _run(["ffmpeg", "-y", "-i", w, "-af", f"atempo={VOICE_TEMPO},apad=pad_dur={pad:.3f}",
                  "-ar", "44100", "-ac", "1", seg])
            fh.write(f"file '{seg}'\n")
    out = os.path.join(workdir, "voice.wav")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", out])
    return out


def _final_audio(voice, sfx, music, total, workdir) -> str:
    cmd, parts, labels = ["ffmpeg", "-y", "-i", voice], ["[0:a]aformat=channel_layouts=stereo[v]"], ["[v]"]
    n = 1
    if sfx:
        cmd += ["-i", sfx]
        parts.append(f"[{n}:a]aformat=channel_layouts=stereo[x]")
        labels.append("[x]")
        n += 1
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]
        fade_out = max(0.0, total - 1.5)
        parts.append(f"[{n}:a]atrim=0:{total:.3f},volume={MUSIC_VOL},afade=t=in:d=1.0,"
                     f"afade=t=out:st={fade_out:.2f}:d=1.5,aformat=channel_layouts=stereo[m]")
        labels.append("[m]")
    # Normalised to -14 LUFS, where Instagram and most phones expect speech to
    # sit. Earlier reels came out near -28 and played noticeably quieter than
    # the posts around them. loudnorm resamples internally, hence aresample.
    parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,"
                 f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]")
    out = os.path.join(workdir, "mix.m4a")
    _run(cmd + ["-filter_complex", ";".join(parts), "-map", "[out]", "-t", f"{total:.3f}",
                "-c:a", "aac", "-b:a", "192k", out])
    return out


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(plan: dict, out_path: str, *, tts, music: str | None = None,
          workdir: str | None = None) -> str:
    """Render a plan to an MP4 at out_path.

    tts:   callable(text) -> wav path. The pipeline passes its fal voice.
    music: optional bed, looped and mixed under the voice.
    """
    from playwright.sync_api import sync_playwright

    beats = plan["beats"]
    workdir = workdir or tempfile.mkdtemp(prefix="reel2_")

    wavs = [tts(b["say"]) for b in beats]
    durs = [_duration(w) / VOICE_TEMPO for w in wavs]
    pads = [GAP + float(b.get("hold", 0)) for b in beats]
    voice = _voice_track(wavs, pads, workdir)

    timing, windows, t = [], [], 0.0
    for b, d, pad in zip(beats, durs, pads):
        kind = b.get("visual", {}).get("type", "text")
        timing.append((t, t + d, t + d + pad, kind))
        windows.append((t, t + d, b["say"]))
        t += d + pad
    total = t
    words = align.align(voice, windows)

    sfx, beat_html, meta, emphasis = [], [], [], []
    for i, (b, (s, se, e, kind)) in enumerate(zip(beats, timing)):
        pal_name = b.get("bg") or ROTATION[i % len(ROTATION)]
        pal = PAL[pal_name]
        cue = Cue(i, s, se, e, words[i], pal, sfx)
        if i > 0:
            sfx.append(("whoosh", s - 0.12))
        beat_html.append(VISUALS[kind](b.get("visual", {}), cue))
        meta.append({"s": round(s, 3), "e": round(e, 3), "vars": {
            "--bg": pal["bg"], "--fg": pal["fg"], "--active": pal["active"], "--accent": pal["accent"],
            "--card": pal["card"], "--cardfg": pal["cardfg"], "--cfg": pal["fg"], "--cactive": pal["active"],
            "--markfg": INK if pal["active"] in (AMBER,) else "#fff8f0"}})
        emphasis.append({align.norm(x) for x in b.get("emphasis", [])})
    caps_html, _ = _caption_html(words, timing, emphasis)
    page = _page(beat_html, caps_html, meta, total)

    html_path = os.path.join(workdir, "reel.html")
    Path(html_path).write_text(page, encoding="utf-8")
    audio = _final_audio(voice, _sfx_track(sfx, total, workdir), music, total, workdir)

    n_frames = int(math.ceil(total * FPS))
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
         "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "copy", "-shortest", "-movflags", "+faststart", out_path],
        stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb"])
        page_ = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page_.goto(f"file://{html_path}")
        page_.evaluate("async () => { await document.fonts.ready; "
                       "await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); }")
        for f in range(n_frames):
            page_.evaluate("t => render(t)", f / FPS)
            enc.stdin.write(page_.screenshot(type="jpeg", quality=JPEG_Q))
        browser.close()
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("reel encode failed")
    log.info("reel2: %d beats, %.1fs, %d frames -> %s", len(beats), total, n_frames, out_path)
    return out_path
