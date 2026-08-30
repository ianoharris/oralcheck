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
    mime = "image/png" if ext == ".png" else "image/jpeg"
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
                counter: str | None = None, theme: str = "dark") -> str:
    """Opening slide: a clean, purely typographic hook. Photos live on their own
    full-bleed slides mid-deck, never as an awkward band under the cover text."""
    kicker_html = f"<div class='kicker' style='margin-bottom:26px;'>{_e(kicker)}</div>" if kicker else ""
    body = f"""
    <div class="frame">
      {_brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {kicker_html}
        <div class="accent" style="margin-bottom:32px;"></div>
        <div class="serif" style="font-size:90px;line-height:1.04;letter-spacing:-0.015em;
             color:var(--text);text-wrap:balance;">{_e(hook)}</div>
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


def slide_cta(headline: str = "Take the free screener.",
              sub: str = "2 minutes. Free. Private.",
              url: str = "oralcheck.org") -> str:
    """Closing slide on a teal ground for contrast against dark content slides."""
    body = f"""
    <div style="width:{POST_W}px;height:{POST_H}px;display:flex;flex-direction:column;background:{TEAL};">
      <div style="padding:76px 78px 0;">
        <div class="brandrow">
          <div class="brand"><div class="dot"></div>
            <span class="wordmark" style="color:rgba(13,26,27,0.6);">OralCheck</span></div>
        </div>
        <div style="height:1px;background:rgba(13,26,27,0.22);margin-top:16px;"></div>
      </div>
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding:0 78px;">
        <div class="serif" style="font-size:88px;line-height:1.05;color:{BG};
             text-wrap:balance;margin-bottom:30px;">{_e(headline)}</div>
        <div style="font-size:30px;color:rgba(13,26,27,0.72);font-weight:600;margin-bottom:44px;">{_e(sub)}</div>
        <div style="display:inline-flex;align-items:center;gap:14px;">
          <span style="font-size:34px;font-weight:700;color:{BG};letter-spacing:0.01em;">{_e(url)}</span>
        </div>
      </div>
      <div style="height:10px;background:{CORAL};width:100%;"></div>
    </div>"""
    return _doc(body, bg=TEAL)


# ---------------------------------------------------------------------------
# Deck assembly
# ---------------------------------------------------------------------------

def render_deck(deck: dict, theme: str = "dark") -> list[str]:
    """Turn a deck spec into a list of rendered slide HTML strings.

    deck = {
      "kicker": "HPV & Oral Cancer",
      "cover":  {"hook": str, "photo": path|None},
      "slides": [ {"type": "stat"|"fact"|"list"|"quote"|"photo", ...}, ... ],
      "cta":    {"headline": str, "sub": str, "url": str}  # optional overrides
    }
    theme picks the visual world (dark | light) for the typographic slides.
    """
    theme = deck.get("theme", theme)
    kicker = deck.get("kicker", "")
    slides_spec = deck.get("slides", [])
    total = 1 + len(slides_spec) + 1  # cover + content + cta
    htmls: list[str] = []

    def ctr(n: int) -> str:
        return f"{n:02d} / {total:02d}"

    cover = deck.get("cover", {})
    htmls.append(slide_cover(cover.get("hook", ""), kicker,
                             cover.get("photo"), ctr(1), theme))

    stat_palette = [CORAL, TEAL_BRT, TEAL] if theme == "dark" else [CORAL, TEAL, TEAL]
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
        else:  # fact
            htmls.append(slide_fact(s.get("headline", ""), s.get("body", ""),
                                    c, s.get("kicker", ""), theme))

    cta = deck.get("cta", {})
    htmls.append(slide_cta(cta.get("headline", "Take the free screener."),
                           cta.get("sub", "2 minutes. Free. Private."),
                           cta.get("url", "oralcheck.org")))
    return htmls


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
                                    color_scheme="dark" if theme == "dark" else "light")
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


def pick_theme() -> str:
    """Rotate visual themes, biased toward the light (higher-legibility) look."""
    import random
    return random.choice(["light", "light", "dark"])


# Back-compat shims for the older carousel path -----------------------------

def info_slide_image(headline: str, body: str) -> str:
    return _screenshot(slide_fact(headline, body, None))


def cta_slide_image() -> str:
    return _screenshot(slide_cta())


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
  animation-name:drift; animation-duration:{KINETIC_TOTAL}s; animation-timing-function:ease-in-out; }}
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
  animation-name:bgpan; animation-duration:{KINETIC_TOTAL}s;
  animation-timing-function:ease-out; animation-fill-mode:both; }}
.bghalo {{ opacity:0.9; }}

.bgrays {{ position:absolute; inset:0; overflow:hidden; }}
.bgrays span {{ position:absolute; bottom:0; width:36px; height:100%;
  background:linear-gradient(to top, var(--ray) 0%, transparent 78%);
  transform-origin:bottom center; opacity:0.2;
  animation-name:rayrise; animation-duration:{KINETIC_TOTAL}s;
  animation-timing-function:ease-out; animation-fill-mode:both; }}

.photobg {{ position:absolute; inset:-4%; background-size:cover;
  background-position:center;
  animation-name:bgpan; animation-duration:{KINETIC_TOTAL}s;
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
"""


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
    if variant == "sweep":
        return (
            f"<div class='bgsweep' style=\"background:linear-gradient(135deg,"
            f"{t['bg']} 0%,{t['bg']} 45%,{t['teal']} 130%)\"></div>"
        )
    if variant == "grid":
        line = f"{t['text']}14"
        return (
            "<div class='bggrid' style=\"background-image:"
            f"linear-gradient(to right,{line} 1px,transparent 1px),"
            f"linear-gradient(to bottom,{line} 1px,transparent 1px);"
            "background-size:120px 120px\"></div>"
            f"<div class='blob b' style='background:{t['teal']}'></div>"
        )
    if variant == "halo":
        return (
            "<div class='bghalo' style=\"background:radial-gradient(circle at 50% 38%,"
            f"{t['teal_brt']}40 0%,transparent 62%)\"></div>"
        )
    if variant == "rays":
        bars = "".join(
            f"<span style='left:{8 + i * 12}%;animation-delay:{i * 0.09:.2f}s'></span>"
            for i in range(8)
        )
        return f"<div class='bgrays' style=\"--ray:{t['teal']}\">{bars}</div>"
    return "<div class='blob a'></div><div class='blob b'></div>"


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
            f"<div class='photobg' style=\"background-image:url('{_img_data_uri(photo)}')\"></div>"
            "<div class='photoscrim'></div>"
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
    Returns (frame_dir, n_frames). Frames are captured at native 1080x1920."""
    from playwright.sync_api import sync_playwright
    html = kinetic_scene_html(segment, theme)
    frame_dir = tempfile.mkdtemp(prefix="kinetic_")
    fh = tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False)
    fh.write(html); fh.close()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage",
                                               "--force-color-profile=srgb"])
            page = browser.new_page(viewport={"width": KINETIC_W, "height": KINETIC_H},
                                    device_scale_factor=1)
            page.goto(f"file://{fh.name}")
            page.evaluate("async () => { await document.fonts.ready; }")
            for i in range(n_frames):
                tt = i / max(n_frames - 1, 1)
                page.evaluate(
                    "(t) => { document.documentElement.style.setProperty('--t', t);"
                    " if (window.__update) window.__update(t); }", tt)
                png = page.screenshot(type="png", full_page=False)
                with open(os.path.join(frame_dir, f"frame_{i:04d}.png"), "wb") as out:
                    out.write(png)
            browser.close()
    finally:
        try:
            os.unlink(fh.name)
        except OSError:
            pass
    return frame_dir, n_frames
