"""
HTML → Playwright screenshot renderers for OralCheck social posts.

Produces crisp 4:5 (1080×1350) images with CSS-quality typography. The centrepiece
is a carousel *design system*: the generic slide shapes here (cover, stat, fact,
list, quote, photo, CTA) plus the sixteen designed layouts in `layouts.py`,
assembled into a cohesive deck. Single-image post types (infographic, image
overlay) reuse the same tokens.

Two visual worlds, dark and light, rotate per post. Both are on-brand; the
variety is what stops a profile grid reading as one long identical block.
"""

import base64
import math
import html as _html
from io import BytesIO

from PIL import Image
import os
import tempfile
from pathlib import Path

FONTS_DIR = Path(__file__).parent / "fonts"
_FONT_CACHE: dict[str, str] = {}

# Feed posts are 4:5 portrait, not square.
#
# Instagram's profile grid uses 4:5 cells. A 1:1 post is scaled to fill the
# taller cell, which makes it wider than the cell and crops 108px off EACH side
# (measured: 1080 * 4/5 = 864 visible). Horizontal padding was 78px, so 30px of
# every headline was inside the cropped region and posts read cut off in the
# grid. Rendering 4:5 natively removes the crop and takes ~25% more vertical
# space in the feed.
POST_W, POST_H = 1080, 1350

# Final delivery size, same 4:5 ratio. Instagram caps feed images at 1440px wide
# via the Graph API, so 1440 is the practical maximum on the long edge.
OUTPUT_W, OUTPUT_H = 1440, 1800
OUTPUT_PX = OUTPUT_W  # back-compat for callers that referenced the square size
JPEG_QUALITY = 95

# --- Brand palette (shared accents) ----------------------------------------
TEAL      = "#0d7377"   # primary
TEAL_BRT  = "#14a8ae"   # bright teal
CORAL     = "#e8634a"   # accent

# Two visual worlds we rotate between for variety. Dark is the moody editorial
# look; light is the warm-paper look (higher legibility, which Ian prefers).
THEMES = {
    "dark": {
        "bg": "#0d1a1b", "text": "#e8e4de", "text_soft": "#b8cfd1",
        "muted": "#5a8082", "hair": "#1c3a3c",
        "teal": "#0d7377", "teal_brt": "#14a8ae", "coral": "#e8634a",
    },
    "light": {
        "bg": "#f4f1ea", "text": "#14201f", "text_soft": "#3f5453",
        "muted": "#7c8b8a", "hair": "#ded7c8",
        "teal": "#0d7377", "teal_brt": "#0d7377", "coral": "#d9552f",
    },
}

# Seasonal worlds for holiday posts (Ian, 22 Oct: "make the halloween one a little
# spooky and thanksgiving with some fall designs"). Same tokens, so every layout
# works in them; the decoration sits behind the text (SEASON_DECOR).
THEMES["halloween"] = {
    "bg": "#141019", "text": "#ece6dc", "text_soft": "#c9bfd2",
    "muted": "#7d6f8a", "hair": "#2a2233",
    "teal": "#14a8ae", "teal_brt": "#14a8ae", "coral": "#f07f2d",
}
# Brewers World Series week (Ian, 26 Oct: team colours and logo on the
# "banned at the Brewers' ballpark" post). Navy ground, gold for the accent
# beat, the brand's bright teal kept for the address so it is still ours.
THEMES["brewers"] = {
    "bg": "#12284b", "text": "#f4efe3", "text_soft": "#c9d3e3",
    "muted": "#8496b5", "hair": "#253f6b",
    "teal": "#3cc3c3", "teal_brt": "#3cc3c3", "coral": "#ffc52f",
}
THEMES["fall"] = {
    "bg": "#f6eee2", "text": "#2a1d14", "text_soft": "#5a4636",
    "muted": "#9a8571", "hair": "#e6d6c0",
    "teal": "#0d7377", "teal_brt": "#0d7377", "coral": "#c4561c",
}
DARKISH = {"dark", "halloween", "brewers"}

_BAT = ("<svg viewBox='0 0 44 16' width='{w}' style='position:absolute;left:{x}px;top:{y}px;"
        "transform:rotate({r}deg);opacity:0.85;'><path fill='#08060b' d='M0,10 C6,2 12,2 16,8 C18,4 20,4 22,8 "
        "C24,4 26,4 28,8 C32,2 38,2 44,10 C38,8 34,10 32,14 C30,11 27,11 25,15 L22,12 L19,15 C17,11 14,11 12,14 "
        "C10,10 6,8 0,10 Z'/></svg>")
# a cobweb in the bottom-left corner: spokes from the corner, sagging threads between them
_WEB = "".join(f"<line x1='0' y1='380' x2='{380 * math.cos(a):.0f}' y2='{380 - 380 * math.sin(a):.0f}'/>"
               for a in [i * math.pi / 12 for i in range(7)])
_WEB += "".join(
    "<polyline fill='none' points='" + " ".join(
        f"{r * (1 - 0.06 * (k % 2)) * math.cos(k * math.pi / 12):.0f},{380 - r * (1 - 0.06 * (k % 2)) * math.sin(k * math.pi / 12):.0f}"
        for k in range(7)) + "'/>" for r in (90, 160, 230, 300))
# a maple leaf: five pointed lobes with small teeth (outline computed once from a polar profile)
_LEAF = ("<svg viewBox='0 0 100 110' width='{w}' style='position:absolute;left:{x}px;top:{y}px;"
         "transform:rotate({r}deg);opacity:{o};'><path fill='{c}' d='M72.9 56.0 L71.9 55.4 L70.9 54.9 L69.7 54.4 L68.5 54.1 L67.3 53.7 L66.2 53.4 L65.6 53.1 L66.4 52.5 L67.4 51.8 L68.3 51.1 L69.1 50.3 L70.0 49.5 L70.8 48.6 L72.3 47.4 L74.2 46.0 L76.0 44.4 L77.6 42.8 L78.9 41.3 L79.8 39.8 L80.3 38.5 L81.9 36.4 L83.2 34.5 L83.8 32.8 L83.8 31.5 L83.0 30.7 L81.7 30.4 L80.4 30.1 L79.7 29.3 L78.5 29.0 L76.8 29.2 L74.7 30.0 L72.4 31.2 L70.0 32.6 L68.2 33.5 L66.7 34.2 L65.2 35.1 L63.6 36.2 L62.1 37.4 L60.7 38.6 L59.4 39.8 L58.6 40.1 L58.2 40.0 L58.2 38.7 L58.3 37.5 L58.2 36.2 L58.1 35.0 L58.0 33.3 L58.2 30.7 L58.3 28.1 L58.2 25.6 L57.9 23.2 L57.4 21.2 L56.8 19.5 L56.2 16.9 L55.5 14.0 L54.7 11.6 L53.6 9.9 L52.5 9.1 L51.2 9.2 L50.0 10.0 L48.8 9.2 L47.5 9.1 L46.4 9.9 L45.3 11.6 L44.5 14.0 L43.8 16.9 L43.2 19.5 L42.6 21.2 L42.1 23.2 L41.8 25.6 L41.7 28.1 L41.8 30.7 L42.0 33.3 L41.9 35.0 L41.8 36.2 L41.7 37.5 L41.8 38.7 L41.8 40.0 L41.4 40.1 L40.6 39.8 L39.3 38.6 L37.9 37.4 L36.4 36.2 L34.8 35.1 L33.3 34.2 L31.8 33.5 L30.0 32.6 L27.6 31.2 L25.3 30.0 L23.2 29.2 L21.5 29.0 L20.3 29.3 L19.6 30.1 L18.3 30.4 L17.0 30.7 L16.2 31.5 L16.2 32.8 L16.8 34.5 L18.1 36.4 L19.7 38.5 L20.2 39.8 L21.1 41.3 L22.4 42.8 L24.0 44.4 L25.8 46.0 L27.7 47.4 L29.2 48.6 L30.0 49.5 L30.9 50.3 L31.7 51.1 L32.6 51.8 L33.6 52.5 L34.4 53.1 L33.8 53.4 L32.7 53.7 L31.5 54.1 L30.3 54.4 L29.1 54.9 L28.1 55.4 L27.1 56.0 L25.0 56.7 L23.0 57.4 L21.3 58.3 L20.0 59.2 L19.3 60.0 L19.1 60.9 L19.0 61.8 L18.3 62.7 L18.2 63.6 L18.8 64.4 L20.0 64.9 L21.8 65.2 L23.9 65.2 L25.4 65.5 L26.6 65.7 L28.1 65.8 L29.7 65.7 L31.4 65.5 L33.1 65.2 L34.6 64.9 L35.3 65.0 L35.9 65.1 L36.6 65.2 L37.3 65.3 L37.9 65.3 L38.6 65.2 L39.1 65.3 L39.2 65.7 L39.4 66.1 L39.7 66.3 L40.0 66.5 L40.5 66.6 L40.9 66.6 L41.2 66.9 L41.3 67.3 L41.5 67.7 L41.8 67.9 L42.2 68.0 L42.6 68.0 L43.1 68.0 L43.3 68.4 L43.5 68.8 L43.8 69.1 L44.1 69.2 L44.5 69.2 L45.0 69.1 L45.4 69.0 L45.8 68.9 L46.2 68.7 L46.7 68.4 L47.1 68.0 L47.6 67.4 L48.0 66.8 L48.4 66.4 L48.7 66.2 L49.0 65.8 L49.3 65.4 L49.5 64.9 L49.8 64.2 L50.0 63.6 L50.2 64.2 L50.5 64.9 L50.7 65.4 L51.0 65.8 L51.3 66.2 L51.6 66.4 L52.0 66.8 L52.4 67.4 L52.9 68.0 L53.3 68.4 L53.8 68.7 L54.2 68.9 L54.6 69.0 L55.0 69.1 L55.5 69.2 L55.9 69.2 L56.2 69.1 L56.5 68.8 L56.7 68.4 L56.9 68.0 L57.4 68.0 L57.8 68.0 L58.2 67.9 L58.5 67.7 L58.7 67.3 L58.8 66.9 L59.1 66.6 L59.5 66.6 L60.0 66.5 L60.3 66.3 L60.6 66.1 L60.8 65.7 L60.9 65.3 L61.4 65.2 L62.1 65.3 L62.7 65.3 L63.4 65.2 L64.1 65.1 L64.7 65.0 L65.4 64.9 L66.9 65.2 L68.6 65.5 L70.3 65.7 L71.9 65.8 L73.4 65.7 L74.6 65.5 L76.1 65.2 L78.2 65.2 L80.0 64.9 L81.2 64.4 L81.8 63.6 L81.7 62.7 L81.0 61.8 L80.9 60.9 L80.7 60.0 L80.0 59.2 L78.7 58.3 L77.0 57.4 L75.0 56.7 Z'/>"
         "<path stroke='{c}' stroke-width='2.5' fill='none' d='M50 60 L50 106'/></svg>")
# A baseball's two seams with their stitches, drawn as arcs off the slide's corner.
def _seam(cx, cy, r, a0, a1, flip):
    pts, stitches = [], []
    for i in range(41):
        a = a0 + (a1 - a0) * i / 40
        x, y = cx + flip * r * math.cos(a), cy + r * math.sin(a)
        pts.append(f"{x:.0f},{y:.0f}")
        if i % 3 == 1:   # a stitch: a short dash across the seam
            nx, ny = flip * math.cos(a), math.sin(a)
            tx, ty = -ny, nx
            stitches.append(f"<line x1='{x - 13 * nx + 6 * tx:.0f}' y1='{y - 13 * ny + 6 * ty:.0f}' "
                            f"x2='{x + 13 * nx - 6 * tx:.0f}' y2='{y + 13 * ny - 6 * ty:.0f}'/>")
    return f"<polyline fill='none' points='{' '.join(pts)}'/>" + "".join(stitches)
_BALL = (_seam(1240, -40, 430, math.pi * 0.55, math.pi * 1.05, 1) + _seam(1240, -40, 260, math.pi * 0.5, math.pi * 1.1, 1))

SEASON_DECOR = {
    "brewers": (
        "<div class='decor'>"
        "<div style='position:absolute;right:-300px;top:-420px;width:1000px;height:1000px;border-radius:50%;"
        "background:radial-gradient(circle,rgba(244,239,227,0.07),rgba(244,239,227,0.02) 60%,transparent 71%);'></div>"
        f"<svg viewBox='0 0 1080 1350' width='1080' height='1350' style='position:absolute;inset:0;' "
        f"stroke='rgba(255,197,47,0.22)' stroke-width='3' stroke-linecap='round'>{_BALL}</svg>"
        "<div style='position:absolute;left:0;right:0;bottom:0;height:10px;background:#ffc52f;'></div>"
        "</div>"),
    "halloween": (
        "<div class='decor'>"
        "<div style='position:absolute;right:-160px;top:-60px;width:640px;height:640px;border-radius:50%;"
        "background:radial-gradient(circle,rgba(255,232,190,0.20) 0%,rgba(255,232,190,0.08) 40%,transparent 68%);'></div>"
        "<div style='position:absolute;right:56px;top:150px;width:230px;height:230px;border-radius:50%;"
        "background:radial-gradient(circle at 38% 36%,#fbf0d8,#d8c49c);opacity:0.22;'></div>"
        + _BAT.format(w=96, x=800, y=270, r=-8) + _BAT.format(w=64, x=920, y=370, r=10) + _BAT.format(w=48, x=740, y=390, r=4)
        + "<svg viewBox='0 0 380 380' width='380' style='position:absolute;left:0;bottom:0;' "
          f"stroke='rgba(236,230,220,0.14)' stroke-width='1.6'>{_WEB}</svg>"
        "<div style='position:absolute;left:0;right:0;bottom:0;height:300px;"
        "background:linear-gradient(to top,rgba(120,96,150,0.14),transparent);'></div>"
        "</div>"),
    "fall": (
        "<div class='decor'>"
        "<div style='position:absolute;inset:0;background:radial-gradient(ellipse at 100% 0%,rgba(214,140,60,0.16),transparent 55%),"
        "radial-gradient(ellipse at 0% 100%,rgba(160,60,30,0.12),transparent 50%);'></div>"
        + _LEAF.format(w=230, x=900, y=-60, r=24, o=0.55, c="#c4561c") + _LEAF.format(w=160, x=840, y=120, r=-30, o=0.45, c="#d99a2b")
        + _LEAF.format(w=120, x=990, y=180, r=60, o=0.5, c="#9b2f1f")
        + _LEAF.format(w=170, x=-70, y=1150, r=-20, o=0.45, c="#a8892f") + _LEAF.format(w=110, x=-30, y=1050, r=35, o=0.45, c="#c4561c")
        + "</div>"),
}


# Back-compat aliases (dark values) for any single-theme callers.
BG        = THEMES["dark"]["bg"]
SURFACE   = "#10201f"
TEXT      = THEMES["dark"]["text"]
TEXT_SOFT = THEMES["dark"]["text_soft"]
HAIRLINE  = THEMES["dark"]["hair"]
MUTED2    = THEMES["dark"]["muted"]


def _font_b64(name: str) -> str:
    if name not in _FONT_CACHE:
        p = FONTS_DIR / name
        _FONT_CACHE[name] = base64.b64encode(p.read_bytes()).decode() if p.exists() else ""
    return _FONT_CACHE[name]


def _img_data_uri(path: str) -> str:
    ext = Path(path).suffix.lower()
    mime = {".png": "image/png", ".svg": "image/svg+xml", ".webp": "image/webp"}.get(ext, "image/jpeg")
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode()}"


def _e(text) -> str:
    return _html.escape(str(text))


# --- Shared stylesheet (font faces + tokens + components) ------------------
# Source Sans 3 is a variable font; one file covers weights 300–700.

def _style(theme: str = "dark") -> str:
    dm = _font_b64("DMSerifDisplay-Regular.ttf")
    ss = _font_b64("SourceSans3-Regular.ttf")
    t = THEMES.get(theme, THEMES["dark"])
    return f"""
@font-face {{
  font-family: 'DM Serif Display';
  src: url('data:font/truetype;base64,{dm}') format('truetype');
  font-weight: 400; font-display: block;
}}
@font-face {{
  font-family: 'Source Sans 3';
  src: url('data:font/truetype;base64,{ss}') format('truetype');
  font-weight: 300 700; font-display: block;
}}
:root {{
  --bg:{t['bg']}; --teal:{t['teal']}; --teal-brt:{t['teal_brt']};
  --coral:{t['coral']}; --text:{t['text']}; --text-soft:{t['text_soft']};
  --muted:{t['muted']}; --hair:{t['hair']};
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: {POST_W}px; height: {POST_H}px; }}
body {{
  overflow: hidden; background: var(--bg); color: var(--text);
  font-family: 'Source Sans 3', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  font-feature-settings: "kern" 1, "liga" 1;
}}
.serif {{ font-family: 'DM Serif Display', Georgia, serif; font-weight: 400; }}
.tnum {{ font-variant-numeric: tabular-nums; }}

.frame {{ width: {POST_W}px; height: {POST_H}px; padding: 92px 96px; display: flex; flex-direction: column; }}

/* top brand row */
.brandrow {{ display: flex; align-items: center; justify-content: space-between; }}
.brand {{ display: flex; align-items: center; gap: 11px; }}
.dot {{ width: 10px; height: 10px; border-radius: 50%; background: var(--coral); }}
.wordmark {{ font-size: 20px; font-weight: 600; letter-spacing: 0.06em; color: var(--teal-brt); }}
.counter {{ font-size: 19px; font-weight: 600; letter-spacing: 0.08em; color: var(--muted); }}
.rule {{ height: 1px; background: var(--hair); margin-top: 16px; }}

.kicker {{ font-size: 21px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: var(--coral); }}
.accent {{ width: 52px; height: 4px; background: var(--coral); border-radius: 2px; }}

.body {{ font-size: 30px; line-height: 1.6; color: var(--text-soft); max-width: 880px; font-weight: 400; }}
.foot {{ display: flex; align-items: center; gap: 14px; }}
.footline {{ width: 40px; height: 3px; background: var(--teal); }}
.footurl {{ font-size: 21px; font-weight: 600; letter-spacing: 0.04em; color: var(--teal); }}
"""


def _doc(body_html: str, theme: str = "dark", bg: str | None = None) -> str:
    style = _style(theme)
    if bg is not None:
        style += f"\nbody {{ background: {bg}; }}"
    if theme in SEASON_DECOR and bg is None:
        # behind everything: body makes the stacking context, the decoration sits at z -1
        style += ("\nbody { position: relative; z-index: 0; }"
                  " .decor { position: absolute; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; }")
        body_html = SEASON_DECOR[theme] + body_html
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{style}</style></head>"
            f"<body>{body_html}</body></html>")


def _brandrow(counter: str | None) -> str:
    right = f"<span class='counter tnum'>{_e(counter)}</span>" if counter else ""
    return (f"<div class='brandrow'><div class='brand'><div class='dot'></div>"
            f"<span class='wordmark'>OralCheck</span></div>{right}</div>"
            f"<div class='rule'></div>")


# ---------------------------------------------------------------------------
# Carousel slide layouts
# ---------------------------------------------------------------------------

def slide_cover(hook: str, kicker: str = "", photo: str | None = None,
                counter: str | None = None, theme: str = "dark",
                logo: str | None = None, note: str = "") -> str:
    """Opening slide: a clean, purely typographic hook. Photos live on their own
    full-bleed slides mid-deck, never as an awkward band under the cover text."""
    kicker_html = f"<div class='kicker' style='margin-bottom:26px;'>{_e(kicker)}</div>" if kicker else ""
    # `logo`: a partner or occasion mark above the hook; `note`: a small line
    # under it (a "not affiliated with" line goes here when a team mark is used)
    logo_html = (f"<img src='{_img_data_uri(logo)}' style='height:150px;width:auto;align-self:flex-start;"
                 f"margin-bottom:40px;'>") if logo else ""
    note_html = (f"<div style='font-size:20px;line-height:1.4;color:var(--muted);margin-top:30px;'>{_e(note)}</div>"
                 if note else "")
    body = f"""
    <div class="frame">
      {_brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {logo_html}
        {kicker_html}
        <div class="accent" style="margin-bottom:32px;"></div>
        <div class="serif" style="font-size:90px;line-height:1.04;letter-spacing:-0.015em;
             color:var(--text);text-wrap:balance;">{_e(hook)}</div>
        {note_html}
      </div>
      <div style="display:flex;align-items:center;gap:12px;">
        <span class="footurl">Swipe</span><span style="color:var(--teal);font-size:24px;">&rarr;</span>
      </div>
    </div>"""
    return _doc(body, theme)


def slide_stat(value: str, label: str, detail: str = "", counter: str | None = None,
               color: str = CORAL, theme: str = "dark") -> str:
    detail_html = (f"<div class='body' style='margin-top:38px;font-size:27px;'>{_e(detail)}</div>"
                   if detail else "")
    body = f"""
    <div class="frame">
      {_brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif tnum" style="font-size:210px;line-height:0.9;letter-spacing:-0.02em;
             color:{color};">{_e(value)}</div>
        <div style="font-size:32px;font-weight:600;color:var(--text);margin-top:20px;
             line-height:1.35;max-width:840px;">{_e(label)}</div>
        {detail_html}
      </div>
    </div>"""
    return _doc(body, theme)


def slide_fact(headline: str, body_text: str, counter: str | None = None,
               kicker: str = "", theme: str = "dark") -> str:
    kicker_html = f"<div class='kicker' style='margin-bottom:24px;'>{_e(kicker)}</div>" if kicker else ""
    accent = "" if kicker else "<div class='accent' style='margin-bottom:28px;'></div>"
    body = f"""
    <div class="frame">
      {_brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {kicker_html}{accent}
        <div class="serif" style="font-size:64px;line-height:1.1;letter-spacing:-0.005em;
             color:var(--text);text-wrap:balance;margin-bottom:34px;">{_e(headline)}</div>
        <div class="body">{_e(body_text)}</div>
      </div>
    </div>"""
    return _doc(body, theme)


def slide_list(headline: str, items: list[str], counter: str | None = None,
               kicker: str = "", theme: str = "dark") -> str:
    kicker_html = f"<div class='kicker' style='margin-bottom:22px;'>{_e(kicker)}</div>" if kicker else ""
    rows = []
    for i, it in enumerate(items, 1):
        top = "border-top:1px solid var(--hair);" if i > 1 else ""
        rows.append(f"""
        <div style="display:flex;gap:26px;align-items:baseline;padding:26px 0;{top}">
          <div class="serif tnum" style="font-size:34px;color:var(--teal-brt);min-width:44px;">{i:02d}</div>
          <div style="font-size:30px;line-height:1.4;color:var(--text);font-weight:400;">{_e(it)}</div>
        </div>""")
    body = f"""
    <div class="frame">
      {_brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {kicker_html}
        <div class="serif" style="font-size:58px;line-height:1.1;color:var(--text);
             margin-bottom:24px;text-wrap:balance;">{_e(headline)}</div>
        <div>{"".join(rows)}</div>
      </div>
    </div>"""
    return _doc(body, theme)


def slide_quote(text: str, attribution: str = "", counter: str | None = None,
                theme: str = "dark") -> str:
    attr_html = (f"<div style='font-size:24px;font-weight:600;letter-spacing:0.04em;"
                 f"color:var(--muted);margin-top:36px;'>{_e(attribution)}</div>"
                 if attribution else "")
    body = f"""
    <div class="frame">
      {_brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:150px;line-height:0.5;color:var(--coral);height:60px;">&ldquo;</div>
        <div class="serif" style="font-size:60px;line-height:1.2;color:var(--text);
             text-wrap:balance;max-width:900px;">{_e(text)}</div>
        {attr_html}
      </div>
    </div>"""
    return _doc(body, theme)


def slide_photo(photo: str, caption: str = "", counter: str | None = None) -> str:
    uri = _img_data_uri(photo)
    cap_html = ""
    if caption:
        cap_html = f"""
        <div style="position:absolute;left:0;right:0;bottom:0;padding:0 78px 84px;z-index:2;">
          <div class="accent" style="margin-bottom:22px;"></div>
          <div class="serif" style="font-size:52px;line-height:1.12;color:var(--text);
               text-wrap:balance;max-width:860px;">{_e(caption)}</div>
        </div>"""
    counter_html = ""
    if counter:
        counter_html = (f"<div style='position:absolute;top:76px;right:78px;z-index:2;' "
                        f"class='counter tnum'>{_e(counter)}</div>")
    body = f"""
    <div style="width:{POST_W}px;height:{POST_H}px;position:relative;overflow:hidden;">
      <img src="{uri}" style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0;" />
      <div style="position:absolute;inset:0;background:{TEAL};mix-blend-mode:color;opacity:0.4;"></div>
      <div style="position:absolute;inset:0;
           background:linear-gradient(to bottom,rgba(13,26,27,0.35) 0%,transparent 32%,
           rgba(13,26,27,0.75) 74%,rgba(13,26,27,0.97) 100%);"></div>
      {counter_html}{cap_html}
    </div>"""
    return _doc(body)


def slide_close(headline: str, body: str = "", kicker: str = "", counter: str | None = None,
                theme: str = "dark", url: str = "oralcheck.org") -> str:
    """The last slide of a carousel, written for that carousel.

    Every deck used to end on the same teal card, appended here whether the
    deck asked for it or not, so a follower saw one identical slide at the end
    of every post (Ian, 26 Oct: "why is this slide on every carousel"). The
    closing words now come from the deck itself (the generator writes them for
    the post's focus) and the slide sits in the deck's own theme, holiday
    decoration included. The address stays, smaller, because a link on a
    slide cannot be tapped and reading it off the screen is the only route."""
    t = THEMES.get(theme, THEMES["dark"])
    size = 84 if len(headline) <= 40 else (72 if len(headline) <= 60 else 62)
    kicker_html = (f"<div class='kicker' style='margin-bottom:26px;'>{_e(kicker)}</div>" if kicker
                   else "<div class='accent' style='margin-bottom:32px;'></div>")
    body_html = (f"<div class='body' style='font-size:32px;margin-top:34px;'>{_e(body)}</div>"
                 if body else "")
    inner = f"""
    <div class="frame">
      {_brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {kicker_html}
        <div class="serif" style="font-size:{size}px;line-height:1.06;letter-spacing:-0.01em;
             color:var(--text);text-wrap:balance;">{_e(headline)}</div>
        {body_html}
      </div>
      <div style="height:1px;background:var(--hair);margin-bottom:30px;"></div>
      <div style="display:flex;align-items:baseline;justify-content:space-between;gap:24px;">
        <span style="font-size:42px;font-weight:700;color:{t['teal_brt'] if theme in DARKISH else t['teal']};
              letter-spacing:0.01em;">{_e(url)}</span>
        <span style="font-size:22px;font-weight:600;color:var(--muted);">Free, private, about two minutes</span>
      </div>
    </div>"""
    return _doc(inner, theme)


def _overlay(html: str, inner: str) -> str:
    """Add an absolutely positioned layer to a rendered slide."""
    return html.replace("</body>", inner + "</body>", 1)


def _source_footer(source: str, theme: str) -> str:
    t = THEMES.get(theme, THEMES["dark"])
    return (f"<div style='position:absolute;left:96px;bottom:40px;font-size:19px;font-weight:600;"
            f"letter-spacing:0.02em;color:{t['muted']};max-width:760px;'>{_e(source)}</div>")


def _swipe_cue(theme: str, on_photo: bool = False) -> str:
    color = "#e8e4de" if on_photo else THEMES.get(theme, THEMES["dark"])["teal_brt"]
    return (f"<div style='position:absolute;right:78px;bottom:34px;font-size:34px;line-height:1;"
            f"color:{color};opacity:0.85;'>&rarr;</div>")


# ---------------------------------------------------------------------------
# Deck assembly
# ---------------------------------------------------------------------------

def render_deck(deck: dict, theme: str = "dark") -> list[str]:
    """Turn a deck spec into a list of rendered slide HTML strings.

    deck = {
      "kicker": "HPV & Oral Cancer",
      "cover":  {"hook": str, "photo": path|None},
      "slides": [ {"type": "stat"|"fact"|"list"|"quote"|"photo", ...}, ...,
                  {"type": "close", "kicker", "headline", "body"} ],
    }
    Nothing is added after the slides: a deck that wants a closing slide ends
    on a "close" slide written for it.
    theme picks the visual world (dark | light) for the typographic slides.
    """
    theme = deck.get("theme", theme)
    kicker = deck.get("kicker", "")
    slides_spec = deck.get("slides", [])
    total = 1 + len(slides_spec)  # cover + slides (the close, if any, is one of them)
    htmls: list[str] = []

    def ctr(n: int) -> str:
        return f"{n:02d} / {total:02d}"

    cover = deck.get("cover", {})
    htmls.append(slide_cover(cover.get("hook", ""), kicker,
                             cover.get("photo"), ctr(1), theme,
                             cover.get("logo"), cover.get("note", "")))

    stat_palette = ([THEMES[theme]["coral"], TEAL_BRT, TEAL] if theme in DARKISH
                    else [THEMES.get(theme, THEMES["light"])["coral"], TEAL, TEAL])
    stat_i = 0
    for idx, s in enumerate(slides_spec, start=2):
        t = s.get("type", "fact")
        c = ctr(idx)
        # Templated layouts first: they are the designed shapes, and the five
        # generic types below are the fallback, not the other way round.
        # Imported here, not at module scope: layouts.py imports this module for
        # its tokens, so a top-level import either way round is a cycle.
        import layouts
        templated = layouts.render(s, theme, c)
        if templated:
            htmls.append(templated)
            continue
        if t == "stat":
            color = stat_palette[stat_i % len(stat_palette)]; stat_i += 1
            htmls.append(slide_stat(s.get("value", ""), s.get("label", ""),
                                    s.get("detail", ""), c, color, theme))
        elif t == "list":
            htmls.append(slide_list(s.get("headline", ""), s.get("items", []),
                                    c, s.get("kicker", ""), theme))
        elif t == "quote":
            htmls.append(slide_quote(s.get("text", ""), s.get("attribution", ""), c, theme))
        elif t == "photo":
            htmls.append(slide_photo(s.get("photo", ""), s.get("caption", ""), c))
        elif t == "close":
            htmls.append(slide_close(s.get("headline", ""), s.get("body", ""), s.get("kicker", ""),
                                     c, theme, s.get("url", "oralcheck.org")))
        elif t == "plate":
            htmls.append(slide_plate(s.get("photo", ""), s.get("caption", ""), s.get("credit", ""), c,
                                     theme, s.get("contain", False)))
        else:  # fact
            htmls.append(slide_fact(s.get("headline", ""), s.get("body", ""),
                                    c, s.get("kicker", ""), theme))

    # A source line on every content slide (any slide can be screenshotted or
    # re-served on its own) and a swipe cue on every slide but the last.
    source = deck.get("source", "")
    for i in range(1, len(htmls)):
        kind = slides_spec[i - 1].get("type")
        if kind == "close":
            continue                      # the last word: no swipe cue, and it carries the address
        on_photo = kind == "photo"
        extra = _swipe_cue("light" if kind == "plate" else theme, on_photo) if i < len(htmls) - 1 else ""
        if source and kind not in ("photo", "plate"):
            extra += _source_footer(source, theme)
        htmls[i] = _overlay(htmls[i], extra)
    return htmls


def slide_plate(photo: str, caption: str = "", credit: str = "", counter: str | None = None,
                theme: str = "dark", contain: bool = False) -> str:
    """A picture shown as itself: a 3D still or a clinical photo, untinted, on a
    light ground with its caption and credit beneath. Used where the old deck
    dropped a teal-washed stock photo between typographic slides."""
    uri = _img_data_uri(photo)
    t = THEMES["light"]
    fit = "contain" if contain else "cover"
    pad = "padding:40px 78px 0;" if contain else ""
    body = f"""
    <div style="width:{POST_W}px;height:{POST_H}px;display:flex;flex-direction:column;background:#eceff0;">
      <div style="padding:76px 78px 0;">{_brandrow(counter)}</div>
      <div style="flex:1;min-height:0;{pad}display:flex;">
        <img src="{uri}" style="width:100%;height:100%;object-fit:{fit};border-radius:{'10px' if contain else '0'};" />
      </div>
      <div style="padding:34px 78px 92px;">
        <div class="serif" style="font-size:50px;line-height:1.12;color:{t['text']};text-wrap:balance;">{_e(caption)}</div>
        {f"<div style='font-size:18px;color:{t['muted']};margin-top:18px;letter-spacing:0.02em;'>{_e(credit)}</div>" if credit else ""}
      </div>
    </div>"""
    return _doc(body, "light", bg="#eceff0")


def _photo_ground(photo: str, default: str = "#eceff0") -> str:
    """The card's ground: the photo's own background when it is a product shot on
    plain white (all four corners the same near-white), else the usual grey.
    A grey band around a white-backed photo reads as a pasted-in box (Ian,
    26 Oct, on the vial: "make the background white the same color as the
    background of the vial image's white")."""
    try:
        with Image.open(photo) as im:
            im = im.convert("RGB"); w, h = im.size
            corners = [im.getpixel(p) for p in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2))]
    except Exception:  # noqa: BLE001
        return default
    lo = [min(c[i] for c in corners) for i in range(3)]
    hi = [max(c[i] for c in corners) for i in range(3)]
    if min(lo) >= 236 and max(h_ - l_ for h_, l_ in zip(hi, lo)) <= 6:
        return "#%02x%02x%02x" % tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    return default


def render_plate(photo: str, hook: str, kicker: str = "", credit: str = "", source: str = "",
                 contain: bool = False, cta: str = "oralcheck.org") -> str:
    """Single image post: the picture above, the hook below, on the light ground
    the 3D reels use, or on the photo's own white when it has one."""
    uri = _img_data_uri(photo)
    t = THEMES["light"]
    ground = _photo_ground(photo)
    fit = "contain" if contain else "cover"
    pad = "padding:24px 78px 0;" if contain else ""
    kick = f"<div class='kicker' style='margin-bottom:20px;color:{t['coral']};'>{_e(kicker)}</div>" if kicker else \
           f"<div class='accent' style='margin-bottom:24px;background:{t['coral']};'></div>"
    foot = " &nbsp;&middot;&nbsp; ".join(_e(x) for x in (credit, source) if x)
    body = f"""
    <div style="width:{POST_W}px;height:{POST_H}px;display:flex;flex-direction:column;background:{ground};">
      <div style="padding:70px 78px 0;"><div class="brandrow"><div class="brand"><div class="dot"></div>
        <span class="wordmark" style="color:{t['teal']};">OralCheck</span></div></div></div>
      <div style="height:820px;{pad}display:flex;">
        <img src="{uri}" style="width:100%;height:100%;object-fit:{fit};border-radius:{'10px' if contain else '0'};" />
      </div>
      <div style="flex:1;padding:30px 78px 52px;display:flex;flex-direction:column;justify-content:flex-end;">
        {kick}
        <div class="serif" style="font-size:{64 if len(hook) < 70 else 54}px;line-height:1.08;color:{t['text']};
             text-wrap:balance;">{_e(hook)}</div>
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:26px;gap:30px;">
          <div class="footurl" style="color:{t['teal']};">{_e(cta)}</div>
          <div style="font-size:17px;color:{t['muted']};text-align:right;">{foot}</div>
        </div>
      </div>
    </div>"""
    return _doc(body, "light", bg=ground)


def render_card(hook: str, kicker: str = "", source: str = "", theme: str = "light",
                cta: str = "oralcheck.org") -> str:
    """Single image post with no picture: the hook set large, for topics where
    any photo would be decoration (numbers, risk statements)."""
    t = THEMES.get(theme, THEMES["light"])
    kick = f"<div class='kicker' style='margin-bottom:28px;'>{_e(kicker)}</div>" if kicker else \
           "<div class='accent' style='margin-bottom:34px;'></div>"
    src = f"<div style='font-size:19px;color:{t['muted']};margin-top:18px;'>{_e(source)}</div>" if source else ""
    body = f"""
    <div class="frame">
      {_brandrow(None)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {kick}
        <div class="serif" style="font-size:{96 if len(hook) < 60 else 80}px;line-height:1.04;letter-spacing:-0.015em;
             color:var(--text);text-wrap:balance;">{_e(hook)}</div>
      </div>
      <div><div class="footurl">{_e(cta)}</div>{src}</div>
    </div>"""
    return _doc(body, theme)


def render_list_card(hook: str, items: list[str], note: str = "", source: str = "", theme: str = "light",
                     cta: str = "oralcheck.org") -> str:
    """Single image post that is the list itself: a big numeral per item, the
    hook above. For "six symptoms" and "five look-alikes" posts, where a
    picture of one thing hid the list (Ian, 26 Oct: "I don't see the 5 things
    being listed anywhere"; "just design the cover nicely like a 6 numbers thing")."""
    t = THEMES.get(theme, THEMES["light"])
    n = len(items)
    size = 34 if n <= 5 else 31
    rows = "".join(
        f"""<div style="display:flex;gap:30px;align-items:baseline;padding:{20 if n <= 5 else 16}px 0;
              border-top:1px solid var(--hair);">
          <div class="serif tnum" style="font-size:64px;line-height:0.9;color:var(--teal);min-width:46px;">{k}</div>
          <div style="font-size:{size}px;line-height:1.25;color:var(--text);">{_list_item(it)}</div></div>"""
        for k, it in enumerate(items, 1))
    nt = f"<div style='font-size:28px;font-weight:600;color:var(--coral);margin-top:26px;'>{_e(note)}</div>" if note else ""
    src = f"<div style='font-size:19px;color:{t['muted']};margin-top:12px;'>{_e(source)}</div>" if source else ""
    body = f"""
    <div class="frame">
      {_brandrow(None)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="accent" style="margin-bottom:28px;"></div>
        <div class="serif" style="font-size:{68 if len(hook) < 60 else 58}px;line-height:1.05;letter-spacing:-0.01em;
             color:var(--text);text-wrap:balance;margin-bottom:34px;">{_e(hook)}</div>
        <div style="border-bottom:1px solid var(--hair);">{rows}</div>
        {nt}
      </div>
      <div><div class="footurl">{_e(cta)}</div>{src}</div>
    </div>"""
    return _doc(body, theme)


def _list_item(text: str) -> str:
    """'Name: what it is' sets the name in bold."""
    head, sep, tail = text.partition(": ")
    return f"<b style='font-weight:700;'>{_e(head)}</b>: {_e(tail)}" if sep else _e(text)


def list_image(hook: str, items: list[str], **kw) -> str:
    return _screenshot(render_list_card(hook, items, **kw))


def render_versus_card(hook: str, sides: list[dict], note: str = "", source: str = "",
                       theme: str = "light", cta: str = "oralcheck.org") -> str:
    """Single image post comparing two causes side by side: a photo each, with
    the number that carries the comparison under it. `sides` is two dicts of
    {photo, value, label, detail, direction, accent}; `direction` (up or down)
    draws an arrow before the number, `accent` puts it in coral, the one beat
    that matters. Built for the HPV-versus-tobacco post
    (Ian, 26 Oct: "use these pics for the hpv one. make the design nice")."""
    t = THEMES.get(theme, THEMES["light"])

    def side(s: dict) -> str:
        color = "var(--coral)" if s.get("accent") else "var(--text)"
        # a drawn arrow, not a +/- sign: the serif minus reads as a dash
        tri = "8,0 16,14 0,14" if s.get("direction") == "up" else "0,0 16,0 8,14"
        arrow = (f"<svg viewBox='0 0 16 14' style='width:44px;height:38px;margin-right:14px;flex:none;'>"
                 f"<polygon points='{tri}' fill='{color}'/></svg>") if s.get("direction") else ""
        return f"""
        <div style="flex:1;display:flex;flex-direction:column;min-width:0;">
          <div style="height:452px;border-radius:22px;overflow:hidden;background:var(--hair);">
            <img src="{_img_data_uri(s['photo'])}" style="width:100%;height:100%;object-fit:cover;
                 object-position:{s.get('focus', 'center')};display:block;"></div>
          <div style="font-size:27px;font-weight:600;color:var(--teal);margin-top:30px;">{_e(s['label'])}</div>
          <div class="serif tnum" style="display:flex;align-items:center;font-size:118px;line-height:0.95;
               letter-spacing:-0.02em;color:{color};margin-top:10px;">{arrow}{_e(s['value'])}</div>
          <div style="font-size:27px;line-height:1.3;color:var(--text-soft);margin-top:12px;
               text-wrap:balance;">{_e(s['detail'])}</div>
        </div>"""

    nt = f"<div style='font-size:25px;line-height:1.35;color:var(--text-soft);margin-top:30px;'>{_e(note)}</div>" if note else ""
    src = f"<div style='font-size:18px;color:{t['muted']};margin-top:10px;'>{_e(source)}</div>" if source else ""
    body = f"""
    <div class="frame" style="padding:84px 84px 76px;">
      {_brandrow(None)}
      <div class="serif" style="font-size:{64 if len(hook) < 60 else 56}px;line-height:1.04;letter-spacing:-0.012em;
           color:var(--text);text-wrap:balance;margin-top:44px;">{_e(hook)}</div>
      <div style="display:flex;gap:28px;margin-top:44px;">{''.join(side(s) for s in sides)}</div>
      {nt}
      <div style="margin-top:auto;"><div class="footurl">{_e(cta)}</div>{src}</div>
    </div>"""
    return _doc(body, theme)


def versus_image(hook: str, sides: list[dict], **kw) -> str:
    return _screenshot(render_versus_card(hook, sides, **kw))


# ---------------------------------------------------------------------------
# Single-image post types (reuse tokens)
# ---------------------------------------------------------------------------

def render_infographic(content: dict, theme: str = "dark") -> str:
    """Data card: headline + up to three stacked hero stats + supporting fact."""
    headline = content.get("headline", "")
    bars = content.get("bars", [])
    fact = content.get("fact", "")
    palette = [CORAL, TEAL_BRT, TEAL]

    rows = []
    for i, b in enumerate(bars):
        val = b.get("value_str", f"{b.get('value', 0)}%")
        label = b.get("label", "")
        color = palette[i % len(palette)]
        top = "border-top:1px solid var(--hair);padding-top:34px;" if i > 0 else ""
        rows.append(f"""
        <div style="padding-bottom:34px;{top}">
          <div class="serif tnum" style="font-size:104px;line-height:0.92;color:{color};
               letter-spacing:-0.015em;">{_e(val)}</div>
          <div style="font-size:25px;color:var(--text-soft);margin-top:12px;line-height:1.4;">{_e(label)}</div>
        </div>""")
    fact_html = (f"<div style='font-size:22px;color:var(--muted);line-height:1.55;'>{_e(fact)}</div>"
                 if fact else "")
    body = f"""
    <div class="frame">
      {_brandrow(None)}
      <div class="serif" style="font-size:50px;line-height:1.16;color:var(--text);
           margin-top:34px;text-wrap:balance;">{_e(headline)}</div>
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">{"".join(rows)}</div>
      {fact_html}
      <div class="foot" style="margin-top:26px;"><div class="footline"></div>
        <span class="footurl">oralcheck.org</span></div>
    </div>"""
    return _doc(body, theme)


def render_image_overlay(image_path: str, hook: str, cta: str = "oralcheck.org",
                         kicker: str = "") -> str:
    uri = _img_data_uri(image_path)
    kicker_html = f"<div class='kicker' style='margin-bottom:22px;'>{_e(kicker)}</div>" if kicker else \
                  "<div class='accent' style='margin-bottom:24px;'></div>"
    body = f"""
    <div style="width:{POST_W}px;height:{POST_H}px;position:relative;overflow:hidden;">
      <img src="{uri}" style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0;" />
      <div style="position:absolute;inset:0;background:{TEAL};mix-blend-mode:color;opacity:0.35;"></div>
      <div style="position:absolute;inset:0;
           background:linear-gradient(to bottom,transparent 24%,rgba(13,26,27,0.72) 56%,
           rgba(13,26,27,0.96) 86%,{BG} 100%);"></div>
      <div style="position:absolute;top:76px;left:78px;z-index:2;" class="brand">
        <div class="dot"></div><span class="wordmark">OralCheck</span></div>
      <div style="position:absolute;bottom:0;left:0;right:0;padding:0 78px 66px;z-index:2;">
        {kicker_html}
        <div class="serif" style="font-size:78px;line-height:1.08;color:var(--text);
             text-wrap:balance;margin-bottom:26px;">{_e(hook)}</div>
        <div class="footurl" style="color:var(--teal-brt);">{_e(cta)}</div>
      </div>
    </div>"""
    return _doc(body)


# ---------------------------------------------------------------------------
# Playwright screenshot
# ---------------------------------------------------------------------------

_BROWSER = None


def _screenshot_many(htmls: list[str]) -> list[str]:
    """Render a batch of HTML docs to JPEGs in one browser session."""
    from playwright.sync_api import sync_playwright
    out_paths: list[str] = []
    tmp_htmls: list[str] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage",
                                               "--force-color-profile=srgb"])
            # Layout is a fixed 1080px frame; render it at 3x (3240px) for heavy
            # supersampling, then downscale to OUTPUT_PX (1440, Instagram's max) so
            # type stays razor-sharp. Larger than 1440 is rejected/downscaled by IG.
            page = browser.new_page(viewport={"width": POST_W, "height": POST_H},
                                    device_scale_factor=3)
            for html in htmls:
                fh = tempfile.NamedTemporaryFile(suffix=".html", mode="w",
                                                 encoding="utf-8", delete=False)
                fh.write(html); fh.close(); tmp_htmls.append(fh.name)
                out = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False); out.close()
                page.goto(f"file://{fh.name}")
                page.evaluate("async () => { await document.fonts.ready; }")
                png_bytes = page.screenshot(type="png", full_page=False)
                with Image.open(BytesIO(png_bytes)) as im:
                    im = im.convert("RGB").resize((OUTPUT_W, OUTPUT_H), Image.LANCZOS)
                    im.save(out.name, "JPEG", quality=JPEG_QUALITY)
                out_paths.append(out.name)
            browser.close()
    finally:
        for h in tmp_htmls:
            try:
                os.unlink(h)
            except OSError:
                pass
    for pth in out_paths:
        _register(pth)
    return out_paths


_TMP: list[str] = []


# Real screens from the product, for posts where stock photography has nothing
# honest to offer. A post about rising incidence used to get "a photo of
# someone's mouth" because that is all a stock search can return for an
# abstract claim; the actual screener is both on-topic and on-brand.
#
# Each entry is a page path plus an optional CSS selector to frame on. The
# selector keeps the shot on the meaningful element instead of a full page of
# whitespace.
SITE_SHOTS: dict[str, dict] = {
    "screener":   {"path": "/screener",         "selector": "main", "label": "the screener"},
    "result":     {"path": "/results",          "selector": "main", "label": "a result page"},
    "find_care":  {"path": "/find-care",        "selector": "main", "label": "the clinic finder"},
    "signs":      {"path": "/learn/signs",      "selector": "main", "label": "the warning signs guide"},
    "self_exam":  {"path": "/learn/self-exam",  "selector": "main", "label": "the self-exam guide"},
    "home":       {"path": "/",                 "selector": "main", "label": "oralcheck.org"},
}

SITE_BASE = os.environ.get("SITE_BASE_URL", "https://oralcheck.org")


def site_screenshot(shot: str, theme: str = "dark") -> str | None:
    """Screenshot a real page of the site, cropped to a 1080x1080 square.

    Returns None rather than raising: a missing screenshot should downgrade the
    post to pure typography, never fail the run.
    """
    spec = SITE_SHOTS.get(shot)
    if not spec:
        return None
    from playwright.sync_api import sync_playwright

    out = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    out.close()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage",
                                              "--force-color-profile=srgb"])
            page = browser.new_page(viewport={"width": 1200, "height": 1200},
                                    device_scale_factor=2,
                                    color_scheme="dark" if theme in DARKISH else "light")
            page.goto(f"{SITE_BASE}{spec['path']}", wait_until="networkidle", timeout=45_000)
            page.evaluate("async () => { await document.fonts.ready; }")
            target = page.locator(spec["selector"]).first
            png = target.screenshot(type="png") if target.count() else page.screenshot(type="png")
            browser.close()

        with Image.open(BytesIO(png)) as im:
            im = im.convert("RGB")
            # Centre-crop to a square on the top of the element, which is where
            # the headline and the primary control live.
            side = min(im.width, im.height)
            left = max(0, (im.width - side) // 2)
            im = im.crop((left, 0, left + side, side))
            im = im.resize((OUTPUT_PX, OUTPUT_PX), Image.LANCZOS)
            im.save(out.name, "JPEG", quality=JPEG_QUALITY)
        return _register(out.name)
    except Exception as exc:  # noqa: BLE001
        print(f"site_screenshot({shot}) failed: {exc}", flush=True)
        try:
            os.unlink(out.name)
        except OSError:
            pass
        return None


def _register(path: str) -> str:
    _TMP.append(path)
    return path


def _screenshot(html: str) -> str:
    return _screenshot_many([html])[0]


# ---------------------------------------------------------------------------
# Public API — each returns a path (or list of paths) to JPEG(s)
# ---------------------------------------------------------------------------

def carousel_deck(deck: dict, theme: str = "dark") -> list[str]:
    """Render a full carousel deck. Returns one JPEG path per slide, in order."""
    return _screenshot_many(render_deck(deck, theme))


def infographic_image(content: dict, theme: str = "dark") -> str:
    return _screenshot(render_infographic(content, theme))


def image_overlay(image_path: str, hook: str, cta: str = "oralcheck.org",
                  kicker: str = "") -> str:
    return _screenshot(render_image_overlay(image_path, hook, cta, kicker))


def plate_image(photo: str, hook: str, **kw) -> str:
    return _screenshot(render_plate(photo, hook, **kw))


def card_image(hook: str, **kw) -> str:
    return _screenshot(render_card(hook, **kw))


def pick_theme(occasion: str = "") -> str:
    """Rotate visual themes, biased toward the light (higher-legibility) look.
    A holiday post gets its seasonal world instead."""
    occ = (occasion or "").lower()   # calendar ideas store a missing occasion as null
    if "halloween" in occ:
        return "halloween"
    if "thanksgiving" in occ:
        return "fall"
    if "brewers" in occ or "world series" in occ:
        return "brewers"
    import random
    return random.choice(["light", "light", "dark"])


# Back-compat shims for the older carousel path -----------------------------

def info_slide_image(headline: str, body: str) -> str:
    return _screenshot(slide_fact(headline, body, None))


# ---------------------------------------------------------------------------
# Kinetic typography (reel scenes)
#
# One animated 1080x1920 scene per reel segment. Every animation is *seekable*:
# all animations are paused and their delay is driven by a single --t (0..1)
# progress variable, so a given frame is rendered deterministically by setting
# --t and screenshotting. This gives perfect, reproducible frames (and thus
# perfect audio sync) instead of relying on real-time playback.
# ---------------------------------------------------------------------------

KINETIC_W, KINETIC_H = 1080, 1920
KINETIC_TOTAL = 2.6   # seconds of animation before the scene holds its end state

# The hold used to be a single frame, cloned by ffmpeg for however long the
# narration ran, so a scene went fully static the moment its text settled (one
# reel measured 2026-09-21: ~5s of zero visual change on its longest lines).
# These add a bounded window of continued, deterministic backdrop motion after
# the reveal, so a typical hold still has something moving instead of freezing
# outright. Anything past this window still freezes, same as before; this
# narrows how often that happens rather than removing it.
KINETIC_HOLD_DRIFT = 2.6   # extra seconds of slow backdrop motion after the reveal settles
KINETIC_HOLD_FPS = 6       # capture rate for that extension; the motion is slow enough
                           # that 6fps reads as smooth once each frame is repeated up to
                           # the reel's real frame rate, at a fraction of the render cost
KINETIC_TOTAL_HOLD = KINETIC_TOTAL + KINETIC_HOLD_DRIFT


def _kinetic_style(theme: str) -> str:
    dm = _font_b64("DMSerifDisplay-Regular.ttf")
    ss = _font_b64("SourceSans3-Regular.ttf")
    t = THEMES.get(theme, THEMES["dark"])
    return f"""
@font-face {{ font-family:'DM Serif Display'; src:url('data:font/truetype;base64,{dm}') format('truetype'); font-weight:400; font-display:block; }}
@font-face {{ font-family:'Source Sans 3'; src:url('data:font/truetype;base64,{ss}') format('truetype'); font-weight:300 700; font-display:block; }}
:root {{
  --t:0; --total:{KINETIC_TOTAL};
  --bg:{t['bg']}; --teal:{t['teal']}; --teal-brt:{t['teal_brt']}; --coral:{t['coral']};
  --text:{t['text']}; --text-soft:{t['text_soft']}; --muted:{t['muted']};
}}
*, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:{KINETIC_W}px; height:{KINETIC_H}px; }}
body {{ overflow:hidden; background:var(--bg); color:var(--text);
  font-family:'Source Sans 3', system-ui, sans-serif;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }}
.serif {{ font-family:'DM Serif Display', Georgia, serif; }}

/* every animated element is paused and seeked by --t */
.anim {{ animation-fill-mode:both; animation-play-state:paused;
  animation-timing-function:cubic-bezier(0.16,1,0.3,1);   /* ease-out-expo: long, soft settle */
  animation-delay:calc(var(--d,0) * 1s - var(--t) * var(--total) * 1s);
  will-change:transform, opacity; }}

/* Shorter travel distances read as smoother at 30fps: a 46px drop across a
   0.5s ease has to move ~3px per frame at the start, which strobes. Halving
   the distance and lengthening the ease keeps per-frame deltas small. */
@keyframes riseIn {{ from{{opacity:0; transform:translateY(26px);}} to{{opacity:1; transform:translateY(0);}} }}
@keyframes fadeDown {{ from{{opacity:0; transform:translateY(-12px);}} to{{opacity:1; transform:translateY(0);}} }}
@keyframes fadeUp {{ from{{opacity:0; transform:translateY(14px);}} to{{opacity:1; transform:translateY(0);}} }}
@keyframes sweep {{ from{{transform:scaleX(0);}} to{{transform:scaleX(1);}} }}
@keyframes popIn {{ from{{opacity:0; transform:scale(0.86);}} to{{opacity:1; transform:scale(1);}} }}
@keyframes drift {{ from{{transform:translate(0,0) scale(1);}} to{{transform:translate(60px,-90px) scale(1.18);}} }}

.scene {{ position:relative; width:{KINETIC_W}px; height:{KINETIC_H}px; overflow:hidden; }}
.blob {{ position:absolute; border-radius:50%; filter:blur(70px); opacity:0.5;
  animation-name:drift; animation-duration:{KINETIC_TOTAL_HOLD}s; animation-timing-function:ease-in-out; }}
.blob.a {{ width:760px; height:760px; left:-160px; top:-120px;
  background:radial-gradient(circle, var(--teal) 0%, transparent 70%); }}
.blob.b {{ width:680px; height:680px; right:-200px; bottom:-140px; opacity:0.4;
  background:radial-gradient(circle, var(--teal-brt) 0%, transparent 70%);
  animation-direction:reverse; }}

/* Alternate backdrops. Each animates off the same seekable timeline as
   everything else, so a rendered frame at time t is always reproducible. */
@keyframes bgpan {{ from{{transform:scale(1.04) translateY(0);}}
                    to{{transform:scale(1.12) translateY(-28px);}} }}
@keyframes rayrise {{ from{{transform:scaleY(0.35); opacity:0.10;}}
                      to{{transform:scaleY(1); opacity:0.34;}} }}

.bgsweep, .bggrid, .bghalo {{ position:absolute; inset:-4%;
  animation-name:bgpan; animation-duration:{KINETIC_TOTAL_HOLD}s;
  animation-timing-function:ease-out; animation-fill-mode:both; }}
.bghalo {{ opacity:0.9; }}

.bgrays {{ position:absolute; inset:0; overflow:hidden; }}
.bgrays span {{ position:absolute; bottom:0; width:36px; height:100%;
  background:linear-gradient(to top, var(--ray) 0%, transparent 78%);
  transform-origin:bottom center; opacity:0.2;
  animation-name:rayrise; animation-duration:{KINETIC_TOTAL_HOLD}s;
  animation-timing-function:ease-out; animation-fill-mode:both; }}

.photobg {{ position:absolute; inset:-4%; background-size:cover;
  background-position:center;
  animation-name:bgpan; animation-duration:{KINETIC_TOTAL_HOLD}s;
  animation-timing-function:ease-out; animation-fill-mode:both; }}
.photoscrim {{ position:absolute; inset:0;
  background:linear-gradient(180deg, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0.30) 42%,
    rgba(0,0,0,0.78) 100%); }}

.content {{ position:absolute; inset:0; display:flex; flex-direction:column;
  justify-content:center; padding:0 104px; }}
.brandrow {{ position:absolute; top:120px; left:104px; display:flex; align-items:center; gap:16px;
  animation-name:fadeDown; animation-duration:0.72s; }}
.dot {{ width:20px; height:20px; border-radius:50%; background:var(--coral); }}
.wordmark {{ font-size:38px; font-weight:600; letter-spacing:0.06em; color:var(--teal-brt); }}

.kicker {{ font-size:34px; font-weight:600; letter-spacing:0.16em; text-transform:uppercase;
  color:var(--coral); margin-bottom:40px; animation-name:fadeUp; animation-duration:0.72s; }}

.headline {{ font-family:'DM Serif Display', Georgia, serif; font-size:104px; line-height:1.1;
  color:var(--text); letter-spacing:-0.01em; }}
.word {{ display:inline-block; animation-name:riseIn; animation-duration:0.85s; }}

/* Opening scene. Words settle from a soft blur at full opacity instead of
   fading up from nothing, so frame 0 already shows the whole hook. The reel's
   first frame is its feed thumbnail; a blank one asks the viewer to wait to
   find out what this is, and most will not. */
.lead .word {{ animation-name:leadIn; animation-duration:0.42s; }}
.lead .kicker {{ animation-name:leadIn; animation-duration:0.32s; }}
@keyframes leadIn {{ from{{opacity:1; transform:translateY(9px) scale(0.985); filter:blur(7px);}}
                     to{{opacity:1; transform:none; filter:blur(0);}} }}
.em {{ position:relative; display:inline-block; color:var(--coral); }}
.uline {{ position:absolute; left:0; right:0; bottom:0.02em; height:0.085em; border-radius:4px;
  background:var(--coral); transform-origin:left center;
  animation-name:sweep; animation-duration:0.72s; }}

.statwrap {{ display:flex; flex-direction:column; }}
.stat {{ font-family:'DM Serif Display', Georgia, serif; font-size:340px; line-height:0.95;
  color:var(--teal-brt); font-variant-numeric:tabular-nums;
  animation-name:popIn; animation-duration:0.8s; }}
.statbar {{ height:10px; width:280px; background:var(--coral); border-radius:5px; margin:24px 0 34px;
  transform-origin:left center; animation-name:sweep; animation-duration:0.75s; }}
.statlabel {{ font-size:52px; line-height:1.25; color:var(--text); max-width:820px;
  animation-name:fadeUp; animation-duration:0.8s; }}

.foot {{ position:absolute; bottom:130px; left:104px; display:flex; align-items:center; gap:18px;
  animation-name:fadeUp; animation-duration:0.75s; }}
.footline {{ width:54px; height:5px; background:var(--teal); border-radius:3px; }}
.footurl {{ font-size:40px; font-weight:600; letter-spacing:0.03em; color:var(--teal); }}
{_scene_css()}
"""


def _scene_css() -> str:
    """CSS for the archetype scenes. Imported here rather than at module scope
    because reel_scenes imports this module for `_e`."""
    import reel_scenes
    return reel_scenes.EXTRA_CSS


def _kinetic_words_html(phrase: str, emphasis: str, lead: bool = False) -> str:
    """Wrap each word in a staggered .word span; emphasis words get coral + a
    sweeping underline. Stagger begins after the kicker settles.

    `lead` is for the opening scene, where the stagger has to be near-zero.
    The old timing started words at 0.55s and stepped 0.10s with a 0.85s
    animation, so a seven-word hook was not fully readable until ~2.0s and
    frame 0 was blank. That blank frame is the feed thumbnail and the first
    thing autoplay shows, which is a good way to get scrolled past.
    """
    em_set = {w.strip(".,;:!?'\"").lower() for w in emphasis.split() if w.strip()}
    start, step = (0.0, 0.035) if lead else (0.55, 0.10)
    out = []
    words = phrase.split()
    for i, w in enumerate(words):
        d = round(start + i * step, 3)
        bare = w.strip(".,;:!?'\"").lower()
        if em_set and bare in em_set:
            u_d = round(start + (i + 1) * 0.10 + 0.05, 3)
            inner = (f"<span class='em'>{_e(w)}"
                     f"<span class='anim uline' style='--d:{u_d}'></span></span>")
            out.append(f"<span class='anim word' style='--d:{d}'>{inner}</span>")
        else:
            out.append(f"<span class='anim word' style='--d:{d}'>{_e(w)}</span>")
    return " ".join(out)


# Background treatments a reel rotates through. Each is CSS-only and seekable
# (driven by --t like everything else), so frames stay reproducible.
BG_VARIANTS = ("blobs", "sweep", "grid", "halo", "rays")


def _kinetic_backdrop(variant: str, t: dict) -> str:
    # Every backdrop carries `anim` so it is paused and scrubbed by --t like the
    # text is, instead of running on its own real-time clock. It used to lack
    # this, which is harmless during the brief reveal capture but meant the
    # extended hold-drift window below had nothing deterministic to render.
    if variant == "sweep":
        return (
            f"<div class='anim bgsweep' style=\"background:linear-gradient(135deg,"
            f"{t['bg']} 0%,{t['bg']} 45%,{t['teal']} 130%)\"></div>"
        )
    if variant == "grid":
        line = f"{t['text']}14"
        return (
            "<div class='anim bggrid' style=\"background-image:"
            f"linear-gradient(to right,{line} 1px,transparent 1px),"
            f"linear-gradient(to bottom,{line} 1px,transparent 1px);"
            "background-size:120px 120px\"></div>"
            f"<div class='anim blob b' style='background:{t['teal']}'></div>"
        )
    if variant == "halo":
        return (
            "<div class='anim bghalo' style=\"background:radial-gradient(circle at 50% 38%,"
            f"{t['teal_brt']}40 0%,transparent 62%)\"></div>"
        )
    if variant == "rays":
        # --d instead of a literal animation-delay: an inline style's delay
        # would out-specificity .anim's calc()-driven one and opt these back
        # out of the --t scrub, exactly the bug being fixed here.
        bars = "".join(
            f"<span class='anim' style='left:{8 + i * 12}%;--d:{i * 0.09:.3f}'></span>"
            for i in range(8)
        )
        return f"<div class='bgrays' style=\"--ray:{t['teal']}\">{bars}</div>"
    return "<div class='anim blob a'></div><div class='anim blob b'></div>"


def kinetic_scene_html(segment: dict, theme: str = "dark") -> str:
    """Build one animated reel scene. `segment` may carry:
      caption   -> the on-screen phrase (kinetic words)
      emphasis  -> word(s) to highlight in coral
      stat      -> {"value": "89%", "label": "..."} for a big-number scene
      is_last   -> show the oralcheck.org footer
    """
    t = THEMES.get(theme, THEMES["dark"])
    stat = segment.get("stat") or {}
    brand = ("<div class='brandrow'><div class='dot'></div>"
             "<span class='wordmark'>OralCheck</span></div>")
    foot = ("<div class='foot'><div class='footline'></div>"
            "<span class='footurl'>oralcheck.org</span></div>"
            if segment.get("is_last") else "")

    # Every scene used to be the same two drifting blobs on the same flat
    # background, which is most of why a finished reel felt repetitive. The
    # caller varies `bg` across a reel's segments.
    backdrop = _kinetic_backdrop(segment.get("bg", "blobs"), t)

    # A photo scene breaks up a run of pure-type scenes. Sits behind a scrim so
    # the headline stays legible over any image.
    photo = segment.get("photo")
    if photo:
        backdrop = (
            f"<div class='anim photobg' style=\"background-image:url('{_img_data_uri(photo)}')\"></div>"
            "<div class='photoscrim'></div>"
        )

    # Archetype scenes get first refusal, the same way layouts.py takes
    # precedence over the generic carousel shapes. A scene that cannot render
    # from the fields it was given returns None and falls through to the
    # stat/headline scenes below, so a malformed script still produces a reel.
    import reel_scenes
    archetype = reel_scenes.render(segment, t)
    if archetype:
        return (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>{_kinetic_style(theme)}</style></head><body>"
            f"<div class='scene' style='background:{t['bg']}'>{backdrop}{brand}"
            f"<div class='content'>{archetype}</div>{foot}</div>"
            f"<script>window.__update=function(t){{}};</script></body></html>"
        )

    if stat.get("value"):
        digits = "".join(ch for ch in str(stat["value"]) if ch.isdigit())
        target = digits or "0"
        suffix = str(stat["value"]).replace(target, "", 1) if digits else str(stat["value"])
        body = (
            "<div class='statwrap'>"
            f"<div class='content-stat'><span class='anim stat serif' "
            f"data-target='{target}' data-suffix='{_e(suffix)}' data-d='0.35'>0{_e(suffix)}</span></div>"
            "<div class='anim statbar' style='--d:0.7'></div>"
            f"<div class='anim statlabel' style='--d:0.85'>{_e(stat.get('label',''))}</div>"
            "</div>"
        )
        update_js = (
            "window.__update=function(t){var el=document.querySelector('.stat');"
            "if(!el)return;var tgt=+el.dataset.target,d=+el.dataset.d,dur=0.9;"
            "var p=Math.max(0,Math.min(1,(t*%s - d)/dur));"
            "el.textContent=Math.round(p*tgt)+el.dataset.suffix;};" % KINETIC_TOTAL
        )
    else:
        kicker = segment.get("kicker", "")
        kicker_html = f"<div class='anim kicker'>{_e(kicker)}</div>" if kicker else ""
        words = _kinetic_words_html(segment.get("caption", ""), segment.get("emphasis", ""),
                                    lead=bool(segment.get("lead")))
        body = f"{kicker_html}<div class='headline'>{words}</div>"
        update_js = "window.__update=function(t){};"

    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{_kinetic_style(theme)}</style></head><body>"
        f"<div class='scene{' lead' if segment.get('lead') else ''}' style='background:{t['bg']}'>{backdrop}{brand}"
        f"<div class='content'>{body}</div>{foot}</div>"
        f"<script>{update_js}</script></body></html>"
    )


def render_kinetic_frames(segment: dict, n_frames: int, theme: str = "dark") -> tuple[str, int]:
    """Render a seekable kinetic scene to a directory of PNG frames (frame_%04d.png).

    Returns (frame_dir, total_frames). Frames are captured at native 1080x1920.

    `n_frames` covers the reveal (0..KINETIC_TOTAL seconds, at the caller's fps).
    After it, this renders a further KINETIC_HOLD_DRIFT seconds of backdrop-only
    motion at the cheaper KINETIC_HOLD_FPS and repeats each sample up to the
    caller's frame rate, so the returned frame count is larger than `n_frames`.
    The caller (`_build_kinetic_segment`) derives its ffmpeg tpad-clone padding
    from the returned total, so a longer runway here means less of the segment
    is a single frozen frame. Anything past KINETIC_HOLD_DRIFT still freezes,
    same as before.
    """
    from playwright.sync_api import sync_playwright
    html = kinetic_scene_html(segment, theme)
    frame_dir = tempfile.mkdtemp(prefix="kinetic_")
    fh = tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False)
    fh.write(html); fh.close()
    cap_fps = round(n_frames / KINETIC_TOTAL) if KINETIC_TOTAL else 30
    repeat = max(1, round(cap_fps / KINETIC_HOLD_FPS))
    hold_samples = max(0, round(KINETIC_HOLD_DRIFT * KINETIC_HOLD_FPS))
    idx = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage",
                                               "--force-color-profile=srgb"])
            page = browser.new_page(viewport={"width": KINETIC_W, "height": KINETIC_H},
                                    device_scale_factor=1)
            page.goto(f"file://{fh.name}")
            page.evaluate("async () => { await document.fonts.ready; }")

            def _capture(tt: float) -> bytes:
                page.evaluate(
                    "(t) => { document.documentElement.style.setProperty('--t', t);"
                    " if (window.__update) window.__update(t); }", tt)
                return page.screenshot(type="png", full_page=False)

            for i in range(n_frames):
                png = _capture(i / max(n_frames - 1, 1))
                with open(os.path.join(frame_dir, f"frame_{idx:04d}.png"), "wb") as out:
                    out.write(png)
                idx += 1

            for j in range(hold_samples):
                elapsed = KINETIC_TOTAL + (j + 1) / KINETIC_HOLD_FPS
                png = _capture(elapsed / KINETIC_TOTAL)
                for _ in range(repeat):
                    with open(os.path.join(frame_dir, f"frame_{idx:04d}.png"), "wb") as out:
                        out.write(png)
                    idx += 1

            browser.close()
    finally:
        try:
            os.unlink(fh.name)
        except OSError:
            pass
    return frame_dir, idx
