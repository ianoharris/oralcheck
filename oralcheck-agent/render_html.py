"""
HTML → Playwright screenshot renderers for OralCheck social posts.

Produces crisp 1080×1080 images with CSS-quality typography. The centrepiece is
a carousel *design system*: a small library of distinct slide layouts (cover,
stat, fact, list, quote, photo, CTA) assembled into a cohesive deck. Single-image
post types (infographic, image overlay) reuse the same tokens.

Brand is deliberately single-theme (dark). These are Instagram/Facebook posts, not
theme-aware web pages, so there is no light mode by design.
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

# Final delivery size. Rendered at 2x internally, downscaled to this. Must stay
# <= 1440 (Instagram Graph API max image width).
OUTPUT_PX = 1080

# --- Brand tokens ----------------------------------------------------------
BG        = "#0d1a1b"   # near-black teal ground
SURFACE   = "#10201f"   # barely-raised panel tint
TEAL      = "#0d7377"   # primary
TEAL_BRT  = "#14a8ae"   # bright teal (kickers, links)
CORAL     = "#e8634a"   # accent, used sparingly
TEXT      = "#e8e4de"   # warm off-white
TEXT_SOFT = "#b8cfd1"   # body on dark
HAIRLINE  = "#1c3a3c"   # thin rules / dividers
MUTED2    = "#5a8082"   # muted label / secondary


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

def _style() -> str:
    dm = _font_b64("DMSerifDisplay-Regular.ttf")
    ss = _font_b64("SourceSans3-Regular.ttf")
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
  --bg:{BG}; --surface:{SURFACE}; --teal:{TEAL}; --teal-brt:{TEAL_BRT};
  --coral:{CORAL}; --text:{TEXT}; --text-soft:{TEXT_SOFT};
  --muted:{MUTED2}; --hair:{HAIRLINE};
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1080px; height: 1080px; }}
body {{
  overflow: hidden; background: var(--bg); color: var(--text);
  font-family: 'Source Sans 3', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  font-feature-settings: "kern" 1, "liga" 1;
}}
.serif {{ font-family: 'DM Serif Display', Georgia, serif; font-weight: 400; }}
.tnum {{ font-variant-numeric: tabular-nums; }}

.frame {{ width: 1080px; height: 1080px; padding: 76px 78px; display: flex; flex-direction: column; }}

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


def _doc(body_html: str, bg: str = BG) -> str:
    style = _style()
    if bg != BG:
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
                counter: str | None = None) -> str:
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
    return _doc(body)


def slide_stat(value: str, label: str, detail: str = "", counter: str | None = None,
               color: str = CORAL) -> str:
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
    return _doc(body)


def slide_fact(headline: str, body_text: str, counter: str | None = None,
               kicker: str = "") -> str:
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
    return _doc(body)


def slide_list(headline: str, items: list[str], counter: str | None = None,
               kicker: str = "") -> str:
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
    return _doc(body)


def slide_quote(text: str, attribution: str = "", counter: str | None = None) -> str:
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
    return _doc(body)


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
    <div style="width:1080px;height:1080px;position:relative;overflow:hidden;">
      <img src="{uri}" style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0;" />
      <div style="position:absolute;inset:0;background:{TEAL};mix-blend-mode:color;opacity:0.4;"></div>
      <div style="position:absolute;inset:0;
           background:linear-gradient(to bottom,rgba(13,26,27,0.35) 0%,transparent 32%,
           rgba(13,26,27,0.75) 74%,rgba(13,26,27,0.97) 100%);"></div>
      {counter_html}{cap_html}
    </div>"""
    return _doc(body)


def slide_cta(headline: str = "Take the free screener.",
              sub: str = "10 questions. 2 minutes. Private.",
              url: str = "oralcheck.org") -> str:
    """Closing slide on a teal ground for contrast against dark content slides."""
    body = f"""
    <div style="width:1080px;height:1080px;display:flex;flex-direction:column;background:{TEAL};">
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

def render_deck(deck: dict) -> list[str]:
    """Turn a deck spec into a list of rendered slide HTML strings.

    deck = {
      "kicker": "HPV & Oral Cancer",
      "cover":  {"hook": str, "photo": path|None},
      "slides": [ {"type": "stat"|"fact"|"list"|"quote"|"photo", ...}, ... ],
      "cta":    {"headline": str, "sub": str, "url": str}  # optional overrides
    }
    """
    kicker = deck.get("kicker", "")
    slides_spec = deck.get("slides", [])
    total = 1 + len(slides_spec) + 1  # cover + content + cta
    htmls: list[str] = []

    def ctr(n: int) -> str:
        return f"{n:02d} / {total:02d}"

    cover = deck.get("cover", {})
    htmls.append(slide_cover(cover.get("hook", ""), kicker,
                             cover.get("photo"), ctr(1)))

    stat_palette = [CORAL, TEAL_BRT, TEAL]
    stat_i = 0
    for idx, s in enumerate(slides_spec, start=2):
        t = s.get("type", "fact")
        c = ctr(idx)
        if t == "stat":
            color = stat_palette[stat_i % len(stat_palette)]; stat_i += 1
            htmls.append(slide_stat(s.get("value", ""), s.get("label", ""),
                                    s.get("detail", ""), c, color))
        elif t == "list":
            htmls.append(slide_list(s.get("headline", ""), s.get("items", []),
                                    c, s.get("kicker", "")))
        elif t == "quote":
            htmls.append(slide_quote(s.get("text", ""), s.get("attribution", ""), c))
        elif t == "photo":
            htmls.append(slide_photo(s.get("photo", ""), s.get("caption", ""), c))
        else:  # fact
            htmls.append(slide_fact(s.get("headline", ""), s.get("body", ""),
                                    c, s.get("kicker", "")))

    cta = deck.get("cta", {})
    htmls.append(slide_cta(cta.get("headline", "Take the free screener."),
                           cta.get("sub", "10 questions. 2 minutes. Private."),
                           cta.get("url", "oralcheck.org")))
    return htmls


# ---------------------------------------------------------------------------
# Single-image post types (reuse tokens)
# ---------------------------------------------------------------------------

def render_infographic(content: dict) -> str:
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
    return _doc(body)


def render_image_overlay(image_path: str, hook: str, cta: str = "oralcheck.org",
                         kicker: str = "") -> str:
    uri = _img_data_uri(image_path)
    kicker_html = f"<div class='kicker' style='margin-bottom:22px;'>{_e(kicker)}</div>" if kicker else \
                  "<div class='accent' style='margin-bottom:24px;'></div>"
    body = f"""
    <div style="width:1080px;height:1080px;position:relative;overflow:hidden;">
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
            page = browser.new_page(viewport={"width": 1080, "height": 1080},
                                    device_scale_factor=2)
            for html in htmls:
                fh = tempfile.NamedTemporaryFile(suffix=".html", mode="w",
                                                 encoding="utf-8", delete=False)
                fh.write(html); fh.close(); tmp_htmls.append(fh.name)
                out = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False); out.close()
                page.goto(f"file://{fh.name}")
                page.evaluate("async () => { await document.fonts.ready; }")
                # Render at 2x (2160px) for supersampled crispness, then downscale to
                # OUTPUT_PX. Instagram's Graph API rejects image widths over 1440px, and
                # posts display at ~1080, so 1080 is the right delivery size.
                png_bytes = page.screenshot(type="png", full_page=False)
                with Image.open(BytesIO(png_bytes)) as im:
                    im = im.convert("RGB").resize((OUTPUT_PX, OUTPUT_PX), Image.LANCZOS)
                    im.save(out.name, "JPEG", quality=90)
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


def _register(path: str) -> str:
    _TMP.append(path)
    return path


def _screenshot(html: str) -> str:
    return _screenshot_many([html])[0]


# ---------------------------------------------------------------------------
# Public API — each returns a path (or list of paths) to JPEG(s)
# ---------------------------------------------------------------------------

def carousel_deck(deck: dict) -> list[str]:
    """Render a full carousel deck. Returns one JPEG path per slide, in order."""
    return _screenshot_many(render_deck(deck))


def infographic_image(content: dict) -> str:
    return _screenshot(render_infographic(content))


def image_overlay(image_path: str, hook: str, cta: str = "oralcheck.org",
                  kicker: str = "") -> str:
    return _screenshot(render_image_overlay(image_path, hook, cta, kicker))


# Back-compat shims for the older carousel path -----------------------------

def info_slide_image(headline: str, body: str) -> str:
    return _screenshot(slide_fact(headline, body, None))


def cta_slide_image() -> str:
    return _screenshot(slide_cta())
