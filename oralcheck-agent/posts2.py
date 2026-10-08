"""
Static posts and carousels, second generation.

Three families, chosen by Ian on 2026-10-08:

  Big and graphic   poster, bignum, split, list, cover, cta
                    Type that fills the slide on a solid colour block, so a
                    post still reads as a grid thumbnail.
  Illustrated       mouthmap, step, calendar, compare, icons
                    Code-drawn diagrams from art.py: where to look, what is
                    usually fine and what is not. The most saved kind of post.
  Creator-native    textpost, notes, photo, quiz, answer
                    Looks like a person posted it rather than a brand.

Every slide is HTML rendered by Playwright at 1080x1350 (4:5, the Instagram
grid cell) and delivered at 1440x1800. Text marked `*like this*` gets the
highlighter treatment. Headline sizes are fitted to their box in the browser,
so a long line shrinks rather than overflowing and a short one fills the space.

Nothing here invents a person, a quote, a handle or an engagement count. The
creator-native formats borrow the shape of a post or a note, never a
platform's name or logo.
"""
from __future__ import annotations

import base64
import html as _html
import json
import os
import re
import tempfile
from pathlib import Path

import art

W, H = 1080, 1350
SCALE = 4 / 3            # delivered at 1440x1800
JPEG_QUALITY = 92

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
PUBLIC = HERE.parent / "public"
SIGN_PHOTO_META = HERE.parent / "src" / "lib" / "signPhotos.json"

# Brand colours, plus the amber the site already uses for its middle tier.
INK, TEAL, CORAL, CREAM, AMBER = "#14201f", "#0d7377", "#e8634a", "#f4f1ea", "#f2c14e"
NIGHT = "#0d1a1b"

PALETTES = {
    "coral": {"bg": CORAL, "fg": "#fff8f0", "soft": "#ffe1d6", "accent": INK,
              "mark": AMBER, "markfg": INK, "card": "#fff8f0", "cardfg": INK},
    "teal": {"bg": TEAL, "fg": CREAM, "soft": "#c4e6e4", "accent": AMBER,
             "mark": AMBER, "markfg": INK, "card": CREAM, "cardfg": INK},
    "ink": {"bg": NIGHT, "fg": CREAM, "soft": "#9dbcbd", "accent": CORAL,
            "mark": CORAL, "markfg": "#fff8f0", "card": "#16292a", "cardfg": CREAM},
    "cream": {"bg": CREAM, "fg": INK, "soft": "#56686a", "accent": "#d9552f",
              "mark": AMBER, "markfg": INK, "card": "#ffffff", "cardfg": INK},
    "butter": {"bg": AMBER, "fg": INK, "soft": "#5c4a1c", "accent": "#c4452a",
               "mark": "#fff8f0", "markfg": INK, "card": "#fff8f0", "cardfg": INK},
}

# The rotation a carousel walks through when slides do not name a colour.
ROTATION = ["coral", "cream", "teal", "cream", "ink", "cream", "butter"]


def _font(name: str) -> str:
    return base64.b64encode((FONTS / name).read_bytes()).decode()


def _data_uri(path: str | Path) -> str:
    p = Path(path)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def esc(t) -> str:
    return _html.escape(str(t or ""))


def rich(t) -> str:
    """Escape, then turn *word* into a highlighter mark."""
    return re.sub(r"\*(.+?)\*", r"<mark>\1</mark>", esc(t))


def sign_photo(key: str) -> tuple[str, str] | None:
    """(path, credit line) for one of the site's clinical sign photos."""
    meta = json.loads(SIGN_PHOTO_META.read_text())
    m = meta.get(key)
    if not m:
        return None
    path = PUBLIC / m["src"].lstrip("/")
    host = "Wikimedia Commons" if "wikimedia" in m.get("source", "") else m.get("source", "")
    who = "" if m.get("author", "").lower().startswith("unknown") else f"{m['author']}, "
    return str(path), f"Photo: {who}{host}, {m.get('license', '')}".rstrip(", ")


_LOGO = HERE.parent / "public" / "icon-512.png"


def _css() -> str:
    dm, ss = _font("DMSerifDisplay-Regular.ttf"), _font("SourceSans3-Regular.ttf")
    return f"""
@font-face {{ font-family:'DM Serif Display'; src:url(data:font/truetype;base64,{dm}); font-weight:400; }}
@font-face {{ font-family:'Source Sans 3'; src:url(data:font/truetype;base64,{ss}); font-weight:200 900; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; }}
body {{ background:var(--bg); color:var(--fg); font-family:'Source Sans 3', system-ui, sans-serif;
  -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; }}
.frame {{ position:relative; width:{W}px; height:{H}px; padding:76px 80px 70px; display:flex; flex-direction:column; }}
.serif {{ font-family:'DM Serif Display', Georgia, serif; font-weight:400; letter-spacing:-0.01em; }}
.heavy {{ font-weight:900; letter-spacing:-0.03em; line-height:1.0; }}
/* The highlight is a trimmed band rather than a full background: in tight
   display type a full-height block covers the descenders of the line above. */
mark {{ color:var(--markfg); padding:0 0.1em; border-radius:0.08em; background:
  linear-gradient(var(--mark), var(--mark)) no-repeat 0 62% / 100% 80%;
  -webkit-box-decoration-break:clone; box-decoration-break:clone; }}

.top {{ display:flex; align-items:center; justify-content:space-between; font-weight:800;
  font-size:24px; letter-spacing:0.04em; }}
.brand {{ display:flex; align-items:center; gap:10px; }}
.brand .dot {{ width:14px; height:14px; border-radius:50%; background:var(--accent); }}
.count {{ opacity:0.7; font-variant-numeric:tabular-nums; }}
.pill {{ display:inline-flex; align-self:flex-start; align-items:center; gap:10px; padding:12px 22px;
  border-radius:999px; background:var(--fg); color:var(--bg); font-weight:800; font-size:24px;
  letter-spacing:0.08em; text-transform:uppercase; }}
.fitbox {{ flex:1; min-height:0; display:flex; flex-direction:column; justify-content:center; }}
.fit {{ display:block; }}
.sub {{ font-size:34px; line-height:1.3; font-weight:600; color:var(--soft); max-width:860px; }}
.foot {{ display:flex; align-items:center; justify-content:space-between; gap:20px;
  font-size:24px; font-weight:700; opacity:0.85; }}
.src {{ font-size:22px; font-weight:600; opacity:0.75; }}
.swipe {{ display:inline-flex; align-items:center; gap:12px; padding:14px 26px; border-radius:999px;
  border:3px solid var(--fg); font-weight:800; font-size:26px; letter-spacing:0.06em; text-transform:uppercase; }}
.card {{ background:var(--card); color:var(--cardfg); border-radius:36px; }}
"""


def _top(ctx: dict) -> str:
    count = f"<span class='count'>{ctx['i']} / {ctx['n']}</span>" if ctx["n"] > 1 else ""
    return f"<div class='top'><div class='brand'><span class='dot'></span>OralCheck</div>{count}</div>"


def _fit(inner: str, cls: str, max_px: int, min_px: int = 40, style: str = "") -> str:
    return (f"<div class='fitbox'><div class='fit {cls}' data-fit='{max_px}' data-min='{min_px}' "
            f"style='{style}'>{inner}</div></div>")


# ---------------------------------------------------------------------------
# Big and graphic
# ---------------------------------------------------------------------------

def t_poster(s, ctx):
    kicker = f"<div class='pill'>{esc(s['kicker'])}</div>" if s.get("kicker") else ""
    sub = f"<div class='sub' style='margin-top:26px'>{rich(s['sub'])}</div>" if s.get("sub") else ""
    return (f"<div class='frame'>{_top(ctx)}<div style='height:56px'></div>{kicker}"
            f"{_fit(rich(s['text']), 'heavy', 190, 64, 'margin:30px 0')}{sub}"
            f"<div class='foot' style='margin-top:36px'><span>oralcheck.org</span>"
            f"<span>{esc(s.get('foot', ''))}</span></div></div>")


def t_bignum(s, ctx):
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div class='pill' style='margin-top:56px'>{esc(s.get('kicker', 'The number'))}</div>"
            f"<div class='fitbox'><div class='fit heavy' data-fit='420' data-min='120' "
            f"style='white-space:nowrap;line-height:0.86;font-variant-numeric:tabular-nums'>{esc(s['value'])}</div>"
            f"<div class='serif' style='font-size:66px;line-height:1.08;margin-top:30px;max-width:900px'>"
            f"{rich(s['label'])}</div></div>"
            f"<div class='foot'><span class='src'>{esc(s.get('source', ''))}</span><span>oralcheck.org</span></div></div>")


def t_split(s, ctx):
    rows = ""
    for k, item in enumerate(s["items"][:2]):
        color = AMBER if k == 0 else CORAL
        pct = float(re.sub(r"[^\d.]", "", item["value"]) or 0)
        rows += (
            f"<div style='margin-top:{48 if k else 0}px'>"
            f"<div style='display:flex;align-items:baseline;gap:28px'>"
            f"<div class='heavy' style='font-size:230px;color:{color}'>{esc(item['value'])}</div>"
            f"<div style='font-size:40px;font-weight:700;line-height:1.15;max-width:420px'>{rich(item['label'])}</div></div>"
            f"<div style='height:28px;border-radius:14px;background:rgba(255,255,255,0.14);margin-top:18px'>"
            f"<div style='height:100%;width:{pct:.1f}%;border-radius:14px;background:{color}'></div></div></div>"
        )
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div class='serif' style='font-size:76px;line-height:1.05;margin-top:60px'>{rich(s['title'])}</div>"
            f"<div class='fitbox'>{rows}</div>"
            f"<div class='foot'><span class='src'>{esc(s.get('source', ''))}</span><span>oralcheck.org</span></div></div>")


def t_list(s, ctx):
    items = "".join(
        f"<div style='display:flex;gap:30px;align-items:baseline;padding:22px 0;"
        f"border-top:3px solid color-mix(in srgb, var(--fg) 22%, transparent)'>"
        f"<div class='heavy' style='font-size:84px;color:var(--accent);min-width:76px'>{n}</div>"
        f"<div style='font-size:44px;font-weight:700;line-height:1.18'>{rich(it)}</div></div>"
        for n, it in enumerate(s["items"][:5], 1)
    )
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div class='heavy' style='font-size:96px;margin:54px 0 30px'>{rich(s['title'])}</div>"
            f"<div class='fitbox' style='justify-content:flex-start'>{items}</div>"
            f"<div class='foot'><span>{esc(s.get('foot', ''))}</span><span>oralcheck.org</span></div></div>")


def t_cover(s, ctx):
    art_html = ""
    if s.get("art") == "mouthmap":
        art_html = (f"<div style='position:absolute;left:50%;bottom:-150px;width:980px;transform:translateX(-50%)'>"
                    f"{art.mouth_map(highlight=s.get('highlight', []), uid='cov')}</div>")
    elif s.get("art") in art.ICONS:
        art_html = (f"<div style='position:absolute;right:60px;bottom:170px;opacity:0.95'>"
                    f"{art.icon(s['art'], color=PALETTES[ctx['pal']]['fg'], size=300, stroke=2.4)}</div>")
    # The fit area stops short of the swipe pill, which is absolutely placed
    # and otherwise sat under the last line of a long hook.
    hook_box = "height:560px" if art_html and s.get("art") == "mouthmap" else "flex:1;margin-bottom:120px"
    return (f"<div class='frame' style='overflow:hidden'>{_top(ctx)}"
            f"<div class='pill' style='margin-top:56px'>{esc(s.get('kicker', ''))}</div>"
            f"<div style='{hook_box};min-height:0;display:flex;flex-direction:column;justify-content:center'>"
            f"<div class='fit heavy' data-fit='170' data-min='70'>{rich(s['hook'])}</div></div>"
            f"{art_html}"
            f"<div style='position:absolute;left:80px;bottom:70px'><span class='swipe' "
            f"style='background:var(--bg)'>Swipe &rarr;</span></div></div>")


# Non-breaking space so the highlight never splits "2" from "minutes".
CTA_HEADLINE = "Check your risk in *2\u00a0minutes*"


def t_cta(s, ctx):
    logo = _data_uri(_LOGO)
    return (f"<div class='frame' style='align-items:center;justify-content:center;text-align:center'>"
            f"<img src='{logo}' style='width:170px;height:170px;border-radius:50%;margin-bottom:46px;"
            f"background:#fff8f0;padding:12px'>"
            f"<div class='serif' style='font-size:84px;line-height:1.05;max-width:860px'>"
            f"{rich(s.get('headline', CTA_HEADLINE))}</div>"
            f"<div class='heavy' style='font-size:92px;margin-top:46px;padding:24px 44px;border-radius:28px;"
            f"background:var(--fg);color:var(--bg)'>oralcheck.org</div>"
            f"<div style='font-size:34px;font-weight:700;margin-top:36px;color:var(--soft)'>"
            f"{esc(s.get('sub', 'Free. Private. No account.'))}</div></div>")


# ---------------------------------------------------------------------------
# Illustrated guides
# ---------------------------------------------------------------------------

def t_mouthmap(s, ctx):
    zones = s.get("zones") or art.ZONES
    if len(zones) == 1:
        # One place, not a tour: light it up and name it, no numbered legend.
        z = zones[0]
        pose = "tongue_up" if z == "floor" else "open"
        return (f"<div class='frame'>{_top(ctx)}"
                f"<div class='serif' style='font-size:84px;line-height:1.02;margin-top:44px'>{rich(s['title'])}</div>"
                f"<div style='margin:10px -30px 0'>{art.mouth_map(highlight=[z], pose=pose, uid='mm1')}</div>"
                f"<div class='pill' style='align-self:flex-start;margin-top:6px'>{esc(art.ZONE_LABELS[z])}</div>"
                f"<div style='font-size:38px;line-height:1.3;font-weight:600;margin-top:26px'>{rich(s.get('foot', ''))}</div>"
                f"<div class='foot' style='margin-top:auto'><span></span><span>oralcheck.org</span></div></div>")
    legend = "".join(
        f"<div style='display:flex;align-items:center;gap:16px;font-size:31px;font-weight:700'>"
        f"<span style='flex:none;width:46px;height:46px;border-radius:50%;background:{CORAL};color:#fff8f0;"
        f"display:flex;align-items:center;justify-content:center;font-weight:900;font-size:26px'>{n}</span>"
        f"<span>{esc(art.ZONE_LABELS[z])}</span></div>"
        for n, z in enumerate(zones, 1)
    )
    neck = ""
    if s.get("neck", True):
        neck = (f"<div style='display:flex;align-items:center;gap:16px;font-size:31px;font-weight:700'>"
                f"<span style='flex:none;width:46px;height:46px;border-radius:50%;background:var(--accent);"
                f"color:var(--bg);display:flex;align-items:center;justify-content:center;font-weight:900;"
                f"font-size:26px'>{len(zones) + 1}</span>Face and neck, by feel</div>")
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div class='serif' style='font-size:74px;line-height:1.02;margin-top:44px'>{rich(s['title'])}</div>"
            f"<div style='margin:6px -30px 0;'>{art.mouth_map(badges=zones, uid='mm')}</div>"
            f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:18px 30px;margin-top:-10px'>{legend}{neck}</div>"
            f"<div class='foot' style='margin-top:auto'><span>{esc(s.get('foot', 'Once a month. A mirror and good light.'))}</span>"
            f"<span>oralcheck.org</span></div></div>")


def t_step(s, ctx):
    zone = s.get("zone")
    if zone in art.ZONES:
        pose = "tongue_up" if zone == "floor" else "open"
        visual = f"<div style='margin:0 -20px'>{art.mouth_map(highlight=[zone], pose=pose, uid='st')}</div>"
    else:
        visual = (f"<div style='display:flex;justify-content:center;padding:30px 0'>"
                  f"{art.icon(s.get('icon', 'neck'), color=PALETTES[ctx['pal']]['fg'], size=330, stroke=2.2)}</div>")
    tip = (f"<div class='card' style='padding:24px 30px;font-size:30px;font-weight:700;line-height:1.3;"
           f"margin-top:22px'>{rich(s['tip'])}</div>") if s.get("tip") else ""
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div style='display:flex;align-items:baseline;gap:22px;margin-top:40px'>"
            f"<span class='heavy' style='font-size:120px;color:var(--accent)'>{esc(s['n'])}</span>"
            f"<span class='serif' style='font-size:76px;line-height:1'>{esc(s['area'])}</span></div>"
            f"{visual}"
            f"<div style='font-size:38px;line-height:1.3;font-weight:600'>{rich(s['text'])}</div>{tip}</div>")


def t_calendar(s, ctx):
    pal = PALETTES[ctx["pal"]]
    grid = art.calendar_grid(fill=TEAL if ctx["pal"] != "teal" else NIGHT, flag=CORAL, text="#fff8f0",
                             empty="rgba(127,127,127,0.18)", cell=150, gap=20, uid="cal")
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div class='pill' style='margin-top:50px'>{esc(s.get('kicker', 'The rule'))}</div>"
            f"<div class='heavy' style='font-size:118px;margin:26px 0 40px'>{rich(s['title'])}</div>"
            f"<div style='width:830px'>{grid}</div>"
            f"<div style='font-size:38px;line-height:1.3;font-weight:600;margin-top:40px;color:{pal['fg']}'>"
            f"{rich(s['text'])}</div></div>")


def t_compare(s, ctx):
    def col(title, items, ic, color):
        lis = "".join(
            f"<div style='display:flex;gap:16px;align-items:flex-start;font-size:33px;font-weight:600;line-height:1.22'>"
            f"<span style='flex:none;margin-top:2px'>{art.icon(ic, color=color, size=40, stroke=4)}</span><span>{rich(i)}</span></div>"
            for i in items)
        return (f"<div class='card' style='flex:1;padding:36px 30px;display:flex;flex-direction:column;gap:22px'>"
                f"<div class='heavy' style='font-size:52px;color:{color}'>{esc(title)}</div>{lis}</div>")
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div class='serif' style='font-size:80px;line-height:1.02;margin:46px 0 40px'>{rich(s['title'])}</div>"
            f"<div style='display:flex;gap:24px;flex:1;min-height:0'>"
            f"{col(s.get('a_title', 'Usually fine'), s['a'], 'check', TEAL)}"
            f"{col(s.get('b_title', 'Get it checked'), s['b'], 'alert', '#d9552f')}</div>"
            f"<div class='foot' style='margin-top:30px'><span>{esc(s.get('foot', ''))}</span><span>oralcheck.org</span></div></div>")


def t_icons(s, ctx):
    pal = PALETTES[ctx["pal"]]
    tiles = "".join(
        f"<div class='card' style='padding:30px 20px;display:flex;flex-direction:column;align-items:center;"
        f"gap:16px;text-align:center'>{art.icon(it['icon'], color=pal['cardfg'], size=104, stroke=2.8)}"
        f"<div style='font-size:31px;font-weight:800;line-height:1.15'>{esc(it['label'])}</div></div>"
        for it in s["items"][:6])
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div class='heavy' style='font-size:100px;margin:50px 0 44px'>{rich(s['title'])}</div>"
            f"<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:22px'>{tiles}</div>"
            f"<div class='sub' style='margin-top:40px'>{rich(s.get('sub', ''))}</div>"
            f"<div class='foot' style='margin-top:auto'><span></span><span>oralcheck.org</span></div></div>")


# ---------------------------------------------------------------------------
# Creator-native
# ---------------------------------------------------------------------------

def t_textpost(s, ctx):
    logo = _data_uri(_LOGO)
    return (f"<div class='frame' style='justify-content:center;padding:80px 64px'>"
            f"<div class='card' style='padding:54px 56px;box-shadow:0 30px 80px rgba(0,0,0,0.22)'>"
            f"<div style='display:flex;align-items:center;gap:20px;margin-bottom:34px'>"
            f"<img src='{logo}' style='width:92px;height:92px;border-radius:50%'>"
            f"<div><div style='font-size:36px;font-weight:800'>OralCheck</div>"
            f"<div style='font-size:28px;opacity:0.55;font-weight:600'>oralcheck.org</div></div></div>"
            f"<div style='height:640px;display:flex;flex-direction:column;justify-content:center'>"
            f"<div class='fit' data-fit='84' data-min='40' style='font-weight:600;line-height:1.22;"
            f"letter-spacing:-0.01em'>{rich(s['text'])}</div></div>"
            f"<div style='margin-top:30px;font-size:26px;opacity:0.5;font-weight:600'>{esc(s.get('meta', ''))}</div>"
            f"</div></div>")


def t_notes(s, ctx):
    items = ""
    for it in s["items"]:
        done = it.startswith("[x]")
        text = it[3:].strip() if done else it
        box = (f"<span style='flex:none;width:44px;height:44px;border-radius:50%;margin-top:4px;"
               f"border:3px solid {'#e2a400' if done else '#b9b4a8'};background:{'#e2a400' if done else 'transparent'};"
               f"display:flex;align-items:center;justify-content:center'>"
               f"{art.icon('check', color='#fffdf7', size=28, stroke=6) if done else ''}</span>")
        items += (f"<div style='display:flex;gap:22px;align-items:flex-start;font-size:40px;line-height:1.3;"
                  f"color:{'#8a8576' if done else '#1d1d1b'}'>{box}<span>{rich(text)}</span></div>")
    return (f"<div style='width:{W}px;height:{H}px;background:#fffdf7;color:#1d1d1b;padding:60px 76px;"
            f"display:flex;flex-direction:column'>"
            f"<div style='display:flex;justify-content:space-between;color:#e2a400;font-size:36px;font-weight:600'>"
            f"<span>&lsaquo; Notes</span><span>Done</span></div>"
            f"<div style='text-align:center;color:#a39e92;font-size:26px;margin:34px 0 26px'>{esc(s.get('date', ''))}</div>"
            f"<div style='font-size:64px;font-weight:800;line-height:1.1;margin-bottom:40px'>{rich(s['title'])}</div>"
            f"<div style='display:flex;flex-direction:column;gap:30px'>{items}</div>"
            f"<div style='margin-top:auto;font-size:26px;color:#a39e92;font-weight:600'>oralcheck.org</div></div>")


def t_photo(s, ctx):
    path, credit = s["photo"], s.get("credit", "")
    lines = "".join(
        f"<div><span style='display:inline;background:{'#fff8f0' if k % 2 == 0 else CORAL};"
        f"color:{INK if k % 2 == 0 else '#fff8f0'};font-weight:900;font-size:70px;line-height:1.42;"
        f"padding:6px 22px;-webkit-box-decoration-break:clone;box-decoration-break:clone;border-radius:14px'>"
        f"{esc(line)}</span></div>"
        for k, line in enumerate(s["lines"]))
    return (f"<div style='position:relative;width:{W}px;height:{H}px;overflow:hidden'>"
            f"<img src='{_data_uri(path)}' style='position:absolute;inset:0;width:100%;height:100%;object-fit:cover'>"
            f"<div style='position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0.05) 40%,rgba(0,0,0,0.6) 100%)'></div>"
            f"<div style='position:absolute;left:70px;right:70px;bottom:150px;display:flex;flex-direction:column;gap:8px'>{lines}</div>"
            f"<div style='position:absolute;left:70px;right:70px;bottom:60px;display:flex;justify-content:space-between;"
            f"color:#fff;font-size:22px;font-weight:600;opacity:0.85'><span>{esc(credit)}</span><span>oralcheck.org</span></div></div>")


def t_quiz(s, ctx):
    opts = "".join(
        f"<div class='card' style='display:flex;align-items:center;gap:26px;padding:30px 34px;font-size:44px;"
        f"font-weight:700'><span class='heavy' style='font-size:64px;color:var(--accent)'>{chr(65 + k)}</span>"
        f"<span>{rich(o)}</span></div>" for k, o in enumerate(s["options"]))
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div class='pill' style='margin-top:50px'>{esc(s.get('kicker', 'Quick quiz'))}</div>"
            f"{_fit(rich(s['question']), 'heavy', 130, 60, 'margin:20px 0')}"
            f"<div style='display:flex;flex-direction:column;gap:20px'>{opts}</div>"
            f"<div class='foot' style='margin-top:40px'><span>Answer on the next slide &rarr;</span>"
            f"<span>oralcheck.org</span></div></div>")


def t_answer(s, ctx):
    ok = s.get("correct", True)
    pal = PALETTES[ctx["pal"]]
    return (f"<div class='frame'>{_top(ctx)}"
            f"<div style='margin-top:60px'>{art.icon('check' if ok else 'cross', color=pal['accent'], size=190, stroke=5)}</div>"
            f"<div class='heavy' style='font-size:120px;margin-top:10px'>{rich(s['answer'])}</div>"
            f"<div style='font-size:44px;line-height:1.3;font-weight:600;margin-top:36px;max-width:900px'>{rich(s['text'])}</div>"
            f"<div class='foot' style='margin-top:auto'><span>{esc(s.get('foot', ''))}</span><span>oralcheck.org</span></div></div>")


TEMPLATES = {
    "poster": t_poster, "bignum": t_bignum, "split": t_split, "list": t_list,
    "cover": t_cover, "cta": t_cta,
    "mouthmap": t_mouthmap, "step": t_step, "calendar": t_calendar,
    "compare": t_compare, "icons": t_icons,
    "textpost": t_textpost, "notes": t_notes, "photo": t_photo,
    "quiz": t_quiz, "answer": t_answer,
}

# Templates whose background is part of the format and ignores the palette.
SELF_STYLED = {"notes", "photo"}

_FIT_JS = """
() => {
  // Fit each headline to the box it sits in. Measured against the parent,
  // not the element itself: with line-height under 1 the glyphs always
  // overhang the element's own box, so it never "fits" itself and every
  // headline collapsed to its minimum size. The allowance is that overhang.
  for (const el of document.querySelectorAll('[data-fit]')) {
    const box = el.parentElement;
    let lo = +el.dataset.min || 30, hi = +el.dataset.fit;
    const fits = (px) => box.scrollHeight <= box.clientHeight + px * 0.16
                      && el.scrollWidth <= el.clientWidth + 2;
    el.style.fontSize = hi + 'px';
    if (fits(hi)) continue;
    while (hi - lo > 1) {
      const mid = (lo + hi) >> 1;
      el.style.fontSize = mid + 'px';
      if (fits(mid)) lo = mid; else hi = mid;
    }
    el.style.fontSize = lo + 'px';
  }
}
"""


def slide_html(slide: dict, i: int = 1, n: int = 1) -> str:
    kind = slide["type"]
    pal_name = slide.get("bg") or ROTATION[(i - 1) % len(ROTATION)]
    # The drawn lips are coral-pink and vanish into the coral palette.
    if kind in ("mouthmap", "step") and pal_name == "coral":
        pal_name = "cream"
    pal = PALETTES[pal_name]
    ctx = {"i": i, "n": n, "pal": pal_name}
    body = TEMPLATES[kind](slide, ctx)
    vars_ = ";".join(f"--{k}:{v}" for k, v in pal.items())
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{_css()}</style></head>"
            f"<body style='{vars_}'>{body}</body></html>")


def render(slides: list[dict], out_dir: str | None = None, prefix: str = "slide") -> list[str]:
    """Render slides to 1440x1800 JPEGs. Returns the file paths in order."""
    from playwright.sync_api import sync_playwright

    out_dir = out_dir or tempfile.mkdtemp(prefix="posts2_")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb"])
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        for i, slide in enumerate(slides, 1):
            page.set_content(slide_html(slide, i, len(slides)))
            page.evaluate("async () => { await document.fonts.ready; }")
            page.evaluate(_FIT_JS)
            path = os.path.join(out_dir, f"{prefix}_{i:02d}.jpg")
            page.screenshot(path=path, type="jpeg", quality=JPEG_QUALITY)
            paths.append(path)
        browser.close()
    return paths
