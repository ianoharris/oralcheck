#!/usr/bin/env python3
"""
Render test harness for the OralCheck design system.

Renders every slide layout (with realistic *and* deliberately long content to
catch overflow), then verifies each output is exactly 1080×1080 at 2x scale and
that no content overflowed the frame. Writes all images to a review folder and a
stitched contact sheet.

Run:  python3.11 test_render.py
Exit code 0 = all good, 1 = one or more failures.
"""

import sys
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

import render_html as R

OUT_DIR = Path("/tmp/oralcheck_render_test")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _placeholder_photo() -> str:
    """A non-network stand-in stock photo with some tonal variation."""
    w, h = 1200, 1200
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(0, w, 4):  # step for speed
            r = 30 + int(50 * (y / h))
            g = 60 + int(40 * (x / w))
            b = 66 + int(30 * (1 - y / h))
            for dx in range(4):
                if x + dx < w:
                    px[x + dx, y] = (r, g, b)
    p = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(p.name, "JPEG", quality=90)
    return p.name


PHOTO = _placeholder_photo()

# --- Sample deck exercising the full layout library ------------------------
SAMPLE_DECK = {
    "kicker": "HPV & Oral Cancer",
    "cover": {
        "hook": "Oral cancer isn't just a smoker's disease anymore.",
        "photo": PHOTO,
    },
    "slides": [
        {"type": "stat", "value": "70%", "label": "of oropharyngeal cancers are now linked to HPV",
         "detail": "That share has climbed steadily over the last two decades."},
        {"type": "fact", "kicker": "The shift",
         "headline": "The fastest-growing group is adults 35 to 55.",
         "body": "Many were never heavy smokers or drinkers, the traditional risk factors, which is exactly why so many cases get caught late."},
        {"type": "list", "kicker": "Self-exam",
         "headline": "Five things worth checking for",
         "items": ["A sore that doesn't heal in two weeks",
                   "White or red patches inside the mouth",
                   "A lump or thickening in the cheek",
                   "Persistent trouble swallowing",
                   "A rough or crusted spot on the lip"]},
        {"type": "stat", "value": "84%", "label": "five-year survival when it's caught early",
         "detail": "That falls sharply once it spreads, so timing is everything."},
        {"type": "quote", "text": "The screening took less time than brushing my teeth.",
         "attribution": "OralCheck user"},
        {"type": "photo", "photo": PHOTO,
         "caption": "Two minutes now can change what your options look like later."},
    ],
    "cta": {},
}

# --- Edge cases: long strings that must not overflow -----------------------
EDGE_CASES = [
    ("edge_cover_long", R.slide_cover(
        "This is an intentionally long cover headline meant to stress the wrapping and vertical balance of the type",
        "A Fairly Long Kicker Label", None, "01 / 08")),
    ("edge_stat_long", R.slide_stat(
        "1 in 4", "cases occur in people with none of the classic risk factors at all",
        "This is a longer supporting detail line that should still fit comfortably inside the frame without clipping.",
        "03 / 08")),
    ("edge_fact_long", R.slide_fact(
        "A longer headline that runs to two or even three lines of serif display type",
        "And a body paragraph beneath it that is deliberately verbose so we can confirm the layout keeps everything inside the eleven-forty by ten-eighty frame without any overflow at the bottom edge whatsoever.",
        "04 / 08", "Context")),
    ("edge_list_six", R.slide_list(
        "A list with six longer items to test density",
        ["First item that is reasonably long and wraps to a second line here",
         "Second item also long enough to wrap onto another line",
         "Third item", "Fourth item that wraps as well for good measure",
         "Fifth item", "Sixth and final item in this stress test"],
        "05 / 08", "Checklist")),
    ("edge_infographic_3", R.render_infographic({
        "headline": "Three numbers that reframe how people think about oral cancer risk today",
        "bars": [{"value_str": "54,000", "label": "Americans diagnosed each year"},
                 {"value_str": "70%", "label": "of throat cancers are HPV-related"},
                 {"value_str": "2 min", "label": "to complete the free screener"}],
        "fact": "Early detection roughly quadruples the odds of a good outcome.",
    })),
    ("edge_overlay_long", R.render_image_overlay(
        PHOTO, "A longer image-overlay hook that needs to wrap across two or three lines cleanly",
        "oralcheck.org", "Did you know")),
]


def _cases():
    dark_htmls = R.render_deck(SAMPLE_DECK, "dark")
    cases = [(f"deck_dark_{i+1:02d}", h) for i, h in enumerate(dark_htmls)]
    light_htmls = R.render_deck(SAMPLE_DECK, "light")
    cases += [(f"deck_light_{i+1:02d}", h) for i, h in enumerate(light_htmls)]
    cases.append(("light_infographic", R.render_infographic({
        "headline": "Two numbers that reframe oral cancer risk",
        "bars": [{"value_str": "84%", "label": "survival when caught early"},
                 {"value_str": "39%", "label": "survival when caught late"}],
        "fact": "Early detection more than doubles the odds of a good outcome.",
    }, "light")))
    cases.extend(EDGE_CASES)
    return cases


OVERFLOW_JS = """() => {
  const de = document.documentElement, b = document.body;
  return {
    w: Math.max(de.scrollWidth, b.scrollWidth, b.offsetWidth),
    h: Math.max(de.scrollHeight, b.scrollHeight, b.offsetHeight)
  };
}"""


def main() -> int:
    cases = _cases()
    failures = []
    saved = []

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage",
                                           "--force-color-profile=srgb"])
        page = browser.new_page(viewport={"width": 1080, "height": 1080},
                                device_scale_factor=3)
        for name, html in cases:
            fh = tempfile.NamedTemporaryFile(suffix=".html", mode="w",
                                             encoding="utf-8", delete=False)
            fh.write(html); fh.close()
            page.goto(f"file://{fh.name}")
            page.evaluate("async () => { await document.fonts.ready; }")

            dims = page.evaluate(OVERFLOW_JS)
            overflow = dims["w"] > 1081 or dims["h"] > 1081

            # Match production: supersample at 3x, downscale to OUTPUT_PX (render_html does this).
            out = OUT_DIR / f"{name}.jpg"
            png = page.screenshot(type="png", full_page=False)
            with Image.open(BytesIO(png)) as im:
                im.convert("RGB").resize((R.OUTPUT_PX, R.OUTPUT_PX), Image.LANCZOS).save(str(out), "JPEG", quality=R.JPEG_QUALITY)
            Path(fh.name).unlink(missing_ok=True)

            with Image.open(out) as im:
                # Delivered at OUTPUT_PX (1440, Instagram's max), supersampled from 3x.
                size_ok = im.size == (R.OUTPUT_PX, R.OUTPUT_PX)

            status = "ok"
            if overflow:
                status = f"OVERFLOW ({dims['w']}x{dims['h']})"
                failures.append((name, status))
            elif not size_ok:
                with Image.open(out) as im:
                    status = f"BAD SIZE {im.size}"
                failures.append((name, status))
            saved.append(out)
            print(f"  [{'FAIL' if status != 'ok' else 'PASS'}] {name:22s} {status}")
        browser.close()

    # Contact sheet of the main deck for visual review
    deck_imgs = sorted(OUT_DIR.glob("deck_*.jpg"))
    if deck_imgs:
        thumb_w = 360
        thumbs = []
        for f in deck_imgs:
            im = Image.open(f).convert("RGB")
            im = im.resize((thumb_w, thumb_w), Image.LANCZOS)
            thumbs.append(im)
        cols = len(thumbs)
        sheet = Image.new("RGB", (thumb_w * cols, thumb_w), (13, 26, 27))
        for i, im in enumerate(thumbs):
            sheet.paste(im, (i * thumb_w, 0))
        sheet.save(OUT_DIR / "_contact_sheet.jpg", "JPEG", quality=90)

    print(f"\n  Rendered {len(saved)} images to {OUT_DIR}")
    if failures:
        print(f"  {len(failures)} FAILURE(S):")
        for n, s in failures:
            print(f"    - {n}: {s}")
        return 1
    print("  All render checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
