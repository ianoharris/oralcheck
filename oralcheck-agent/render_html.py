"""
HTML → Playwright screenshot renderers for OralCheck Instagram posts.
Produces crisp 1080×1080 images with proper CSS anti-aliased typography.
Falls back to PIL if Playwright is unavailable.
"""

import base64
import html as _html
import os
import tempfile
from pathlib import Path

FONTS_DIR = Path(__file__).parent / "fonts"
_FONT_CACHE: dict[str, str] = {}


def _font_b64(name: str) -> str:
    if name not in _FONT_CACHE:
        p = FONTS_DIR / name
        _FONT_CACHE[name] = base64.b64encode(p.read_bytes()).decode() if p.exists() else ""
    return _FONT_CACHE[name]


def _base_style() -> str:
    dm = _font_b64("DMSerifDisplay-Regular.ttf")
    ss = _font_b64("SourceSans3-Regular.ttf")
    return f"""
@font-face {{
  font-family: 'DM Serif Display';
  src: url('data:font/truetype;base64,{dm}') format('truetype');
  font-weight: 400;
}}
@font-face {{
  font-family: 'Source Sans 3';
  src: url('data:font/truetype;base64,{ss}') format('truetype');
  font-weight: 400;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  width: 1080px;
  height: 1080px;
  overflow: hidden;
  background: #0d1a1b;
  font-family: 'Source Sans 3', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  font-feature-settings: "kern" 1, "liga" 1;
}}
"""


def _e(text: str) -> str:
    return _html.escape(str(text))


def _brand() -> str:
    return """
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
    <div style="width:10px;height:10px;border-radius:50%;background:#e8634a;flex-shrink:0;"></div>
    <span style="font-size:19px;color:#14a8ae;letter-spacing:0.05em;">OralCheck</span>
  </div>
  <div style="height:1px;background:#1c3a3c;"></div>
"""


def _screenshot(html_content: str) -> str:
    """Render HTML at 1080×1080 and return path to JPEG."""
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
        f.write(html_content)
        html_path = f.name

    out = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    out.close()

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page(viewport={"width": 1080, "height": 1080})
            page.goto(f"file://{html_path}")
            # Wait for fonts to finish loading
            page.evaluate("() => document.fonts.ready")
            page.screenshot(path=out.name, type="jpeg", quality=95, full_page=False)
            browser.close()
    finally:
        os.unlink(html_path)

    return out.name


# ---------------------------------------------------------------------------
# Infographic: hero stats
# ---------------------------------------------------------------------------

def render_infographic(content: dict) -> str:
    bars     = content.get("bars", [])
    headline = _e(content.get("headline", ""))
    fact     = content.get("fact", "")

    stat_colors = ["#e8634a", "#14a8ae", "#0d7377"]
    stats_parts = []
    for idx, bar in enumerate(bars):
        value_str = _e(bar.get("value_str", f"{bar.get('value', 0)}%"))
        label     = _e(bar.get("label", ""))
        color     = stat_colors[idx % len(stat_colors)]
        border_top = "border-top:1px solid #1c3a3c;padding-top:36px;" if idx > 0 else ""
        stats_parts.append(f"""
  <div style="padding-bottom:36px;{border_top}">
    <div style="font-family:'DM Serif Display',serif;font-size:108px;line-height:0.95;
                color:{color};letter-spacing:-0.015em;">{value_str}</div>
    <div style="font-size:24px;color:#a8ccce;margin-top:14px;line-height:1.45;">{label}</div>
  </div>""")

    fact_html = (
        f'<div style="font-size:21px;color:#5a8082;line-height:1.6;margin-bottom:28px;">{_e(fact)}</div>'
        if fact else ""
    )

    style = _base_style()
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{style}</style></head>
<body>
<div style="width:1080px;height:1080px;padding:64px 76px;display:flex;flex-direction:column;">
  {_brand()}

  <div style="font-family:'DM Serif Display',serif;font-size:50px;color:#e8e4de;
               line-height:1.18;margin-top:36px;flex:0 0 auto;">
    {headline}
  </div>

  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding:32px 0;">
    {"".join(stats_parts)}
  </div>

  {fact_html}

  <div style="display:flex;align-items:center;gap:14px;">
    <div style="width:44px;height:3px;background:#0d7377;"></div>
    <span style="font-size:20px;color:#0d7377;letter-spacing:0.03em;">oralcheck.org</span>
  </div>
</div>
</body></html>"""


# ---------------------------------------------------------------------------
# Info slide: carousel text panel
# ---------------------------------------------------------------------------

def render_info_slide(headline: str, body: str) -> str:
    style = _base_style()
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{style}</style></head>
<body>
<div style="width:1080px;height:1080px;padding:64px 76px;display:flex;flex-direction:column;">
  {_brand()}

  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:80px;">
    <div style="width:48px;height:4px;background:#e8634a;margin-bottom:28px;"></div>
    <div style="font-family:'DM Serif Display',serif;font-size:66px;color:#e8e4de;
                 line-height:1.1;margin-bottom:40px;text-wrap:balance;">
      {_e(headline)}
    </div>
    <div style="font-size:28px;color:#b8cfd1;line-height:1.65;max-width:880px;">
      {_e(body)}
    </div>
  </div>

  <div style="display:flex;align-items:center;gap:14px;padding-bottom:0;">
    <div style="width:44px;height:3px;background:#1c3a3c;"></div>
    <span style="font-size:20px;color:#2a5254;letter-spacing:0.03em;">oralcheck.org</span>
  </div>
</div>
</body></html>"""


# ---------------------------------------------------------------------------
# CTA slide
# ---------------------------------------------------------------------------

def render_cta_slide() -> str:
    dm = _font_b64("DMSerifDisplay-Regular.ttf")
    ss = _font_b64("SourceSans3-Regular.ttf")
    style = f"""
@font-face {{ font-family:'DM Serif Display'; src:url('data:font/truetype;base64,{dm}') format('truetype'); }}
@font-face {{ font-family:'Source Sans 3'; src:url('data:font/truetype;base64,{ss}') format('truetype'); font-weight:400; }}
*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ width:1080px; height:1080px; overflow:hidden; background:#0d7377;
        font-family:'Source Sans 3',system-ui,sans-serif;
        -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }}
"""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{style}</style></head>
<body>
<div style="width:1080px;height:1080px;display:flex;flex-direction:column;">
  <div style="padding:64px 76px 0;">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
      <div style="width:10px;height:10px;border-radius:50%;background:#e8634a;"></div>
      <span style="font-size:19px;color:rgba(13,26,27,0.55);letter-spacing:0.05em;">OralCheck</span>
    </div>
    <div style="height:1px;background:rgba(13,26,27,0.2);"></div>
  </div>

  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding:0 76px;">
    <div style="font-family:'DM Serif Display',serif;font-size:82px;color:#0d1a1b;
                 line-height:1.08;margin-bottom:48px;text-wrap:balance;">
      Take the free screener.
    </div>
    <div style="font-size:38px;color:rgba(13,26,27,0.75);letter-spacing:0.01em;">oralcheck.org</div>
  </div>

  <div style="height:8px;background:#e8634a;width:100%;flex-shrink:0;"></div>
</div>
</body></html>"""


# ---------------------------------------------------------------------------
# Image overlay: stock photo with dark gradient + hook text
# ---------------------------------------------------------------------------

def render_image_overlay(image_path: str, hook: str, cta: str = "oralcheck.org") -> str:
    mime = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
    img_b64 = base64.b64encode(open(image_path, "rb").read()).decode()
    data_uri = f"data:{mime};base64,{img_b64}"

    dm = _font_b64("DMSerifDisplay-Regular.ttf")
    ss = _font_b64("SourceSans3-Regular.ttf")
    style = f"""
@font-face {{ font-family:'DM Serif Display'; src:url('data:font/truetype;base64,{dm}') format('truetype'); }}
@font-face {{ font-family:'Source Sans 3'; src:url('data:font/truetype;base64,{ss}') format('truetype'); font-weight:400; }}
*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ width:1080px; height:1080px; overflow:hidden; position:relative;
        font-family:'Source Sans 3',system-ui,sans-serif;
        -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }}
"""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{style}</style></head>
<body>
<img src="{data_uri}"
     style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0;" />
<div style="position:absolute;inset:0;
             background:linear-gradient(to bottom,transparent 25%,rgba(13,26,27,0.7) 55%,rgba(13,26,27,0.96) 85%,#0d1a1b 100%);"></div>
<div style="position:absolute;bottom:0;left:0;right:0;padding:0 76px 60px;">
  <div style="width:52px;height:4px;background:#e8634a;margin-bottom:24px;"></div>
  <div style="font-family:'DM Serif Display',serif;font-size:80px;color:#e8e4de;
               line-height:1.1;margin-bottom:28px;text-wrap:balance;">
    {_e(hook)}
  </div>
  <div style="font-size:22px;color:#14a8ae;letter-spacing:0.05em;">{_e(cta)}</div>
</div>
</body></html>"""


# ---------------------------------------------------------------------------
# Public API — each function returns a path to a JPEG
# ---------------------------------------------------------------------------

def infographic_image(content: dict) -> str:
    return _screenshot(render_infographic(content))


def info_slide_image(headline: str, body: str) -> str:
    return _screenshot(render_info_slide(headline, body))


def cta_slide_image() -> str:
    return _screenshot(render_cta_slide())


def image_overlay(image_path: str, hook: str, cta: str = "oralcheck.org") -> str:
    return _screenshot(render_image_overlay(image_path, hook, cta))
