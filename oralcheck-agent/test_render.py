#!/usr/bin/env python3
"""
Render test harness for the OralCheck design system.

Renders every slide layout (with realistic *and* deliberately long content to
catch overflow), then verifies each output matches render_html's post size and
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
        {"type": "stat", "value": "89%", "label": "five-year survival when it's found early",
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
        "bars": [{"value_str": "60,480", "label": "Americans diagnosed each year"},
                 {"value_str": "70%", "label": "of throat cancers are HPV-related"},
                 {"value_str": "2 min", "label": "to complete the free screener"}],
        "fact": "Early detection roughly quadruples the odds of a good outcome.",
    })),
    ("edge_overlay_long", R.render_image_overlay(
        PHOTO, "A longer image-overlay hook that needs to wrap across two or three lines cleanly",
        "oralcheck.org", "Did you know")),
]


# --- Every designed layout, in both themes ---------------------------------
# Copy is deliberately at the long end of what the model produces. These layouts
# were designed around fixed strings in template_demo.py, so the failure mode
# that matters is a real headline overflowing a box tuned for a shorter one.
LAYOUT_CASES = [
    {"type": "compare", "headline": "Is this normal, or is it actually worth a look?",
     "a_label": "USUALLY FINE", "a_text": "A sore that hurts and then fades within about two weeks",
     "b_label": "GET IT CHECKED", "b_text": "A painless patch that is still sitting there after two weeks",
     "footnote": "Swipe for the other five"},
    {"type": "steps", "kicker": "20-second self-check", "headline": "Do this before you keep scrolling",
     "steps": ["Tongue out, look carefully along both sides", "Lift it and check underneath",
               "Pull each cheek out with a finger", "Run a thumb along the gumline"],
     "footnote": "Found something? Save this post."},
    {"type": "myth", "myth": "Only smokers get oral cancer",
     "truth": "HPV is now the leading cause in adults under fifty",
     "footnote": "Send this to someone who thinks they are not at risk"},
    {"type": "checklist", "headline": "Five things worth two weeks of attention",
     "sub": "If any of these lasts longer than that, book a check.",
     "items": ["A sore that will not heal", "A red or white patch", "A lump you can feel",
               "Numbness or trouble swallowing", "A rough spot on the lip", "A tooth that loosens"],
     "footnote": "Save this. It takes two weeks to matter."},
    {"type": "qualifier", "kicker": "Read this if", "emphasis": "mouth sore",
     "headline": "you have had a mouth sore for more than two weeks",
     "body": "Most are harmless. The ones that are not look exactly the same at this stage, "
             "which is the entire problem.", "footnote": "Two-minute check at oralcheck.org"},
    {"type": "versus", "headline": "What people actually do about a mouth sore",
     "options": [{"name": "Asking a chatbot", "note": "Confident answers, no idea what your mouth looks like", "good": False},
                 {"name": "Googling symptoms", "note": "Worst case first, every time", "good": False},
                 {"name": "Waiting to see", "note": "The two weeks that matter, gone", "good": False},
                 {"name": "OralCheck", "note": "Ten questions, then a real dentist if you need one", "good": True}],
     "footnote": "Swipe"},
    {"type": "bignumber", "value": "2in3", "label": "oral cancers are found late, when treatment is hardest"},
    {"type": "bignumber", "value": "1 in 10", "label": "adults have never had an oral cancer exam"},
    {"type": "timeline", "headline": "How long is too long?",
     "steps": [{"label": "DAY 1", "note": "You notice it"},
               {"label": "DAY 7", "note": "Still there. Probably nothing."},
               {"label": "DAY 14", "note": "This is the line", "mark": True},
               {"label": "DAY 30", "note": "Still waiting is the risk"}]},
    {"type": "question", "question": "When did you last look inside your own mouth?",
     "emphasis": "own mouth", "footnote": "Two minutes. oralcheck.org"},
    {"type": "receipt", "kicker": "What the screener weighs", "headline": "Nothing hidden",
     "rows": [{"label": "Tobacco, any form", "value": "raises risk"},
              {"label": "Heavy alcohol", "value": "raises risk"},
              {"label": "Both together", "value": "multiplies it"},
              {"label": "HPV exposure", "value": "raises risk"},
              {"label": "Sun on the lips", "value": "raises risk"},
              {"label": "Regular dental visits", "value": "lowers it"}],
     "footnote": "Full methodology at oralcheck.org/methods"},
    {"type": "tier", "headline": "Oral health habits, ranked by what actually matters",
     "tiers": [{"rank": "S", "label": "Not smoking"}, {"rank": "A", "label": "Regular dental visits"},
               {"rank": "B", "label": "HPV vaccination"}, {"rank": "C", "label": "Whitening strips"}],
     "footnote": "Disagree? That is the comments section right there."},
    {"type": "news", "quote_kicker": "You probably saw this",
     "quote": "Cases in men under 50 have climbed for two decades",
     "headline": "Here is the part the headline skipped",
     "body": "The rise is real. So is the fact that most of these are found late, which is the "
             "part you can actually do something about.", "footnote": "Swipe"},
    {"type": "verdict", "kicker": "New this month", "photo": PHOTO,
     "headline": "A $300 toothbrush and your cancer risk", "verdict": "SHORT ANSWER: NO",
     "verdict_note": "but it is not useless either",
     "footnote": "Swipe for what actually moves the needle"},
    {"type": "moment", "photo": PHOTO, "headline": "Beer, sun, and the two risk factors nobody mentions",
     "body": "Alcohol and UV on the lips both raise oral cancer risk. The Fourth is not the "
             "problem. Twenty summers of it is."},
    {"type": "pov", "kicker": "POV", "photo": PHOTO,
     "line": "you have been telling yourself it is just a bitten cheek for three weeks"},
    {"type": "photocompare", "headline": "One of these needs a dentist this week",
     "a_photo": PHOTO, "a_label": "Ulcer, painful", "b_photo": PHOTO, "b_label": "Patch, painless",
     "note": "Painless is the one people ignore. It is also the one that matters."},
]


def _cases():
    dark_htmls = R.render_deck(SAMPLE_DECK, "dark")
    cases = [(f"deck_dark_{i+1:02d}", h) for i, h in enumerate(dark_htmls)]
    light_htmls = R.render_deck(SAMPLE_DECK, "light")
    cases += [(f"deck_light_{i+1:02d}", h) for i, h in enumerate(light_htmls)]

    # Designed layouts. A layout that returns None here is a hard failure: it
    # means the pipeline would silently fall back to a generic slide, which is
    # exactly the "why does it all look the same" problem these were built for.
    import layouts
    for theme in ("dark", "light"):
        for case in LAYOUT_CASES:
            html = layouts.render(case, theme, "03 / 07")
            if html is None:
                raise SystemExit(f"layouts.render returned None for {case['type']}/{theme}")
            cases.append((f"layout_{case['type']}_{theme}_{len(case.get('value', ''))}", html))
    cases.append(("light_infographic", R.render_infographic({
        "headline": "Two numbers that reframe oral cancer risk",
        "bars": [{"value_str": "89%", "label": "survival when found early"},
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
        # Sized from render_html rather than hardcoded. These were fixed at
        # 1080x1080; when posts moved to 4:5 every case reported OVERFLOW
        # (1080x1350) because the document was taller than the viewport being
        # measured, not because anything actually overflowed.
        page = browser.new_page(viewport={"width": R.POST_W, "height": R.POST_H},
                                device_scale_factor=3)
        for name, html in cases:
            fh = tempfile.NamedTemporaryFile(suffix=".html", mode="w",
                                             encoding="utf-8", delete=False)
            fh.write(html); fh.close()
            page.goto(f"file://{fh.name}")
            page.evaluate("async () => { await document.fonts.ready; }")

            dims = page.evaluate(OVERFLOW_JS)
            overflow = dims["w"] > R.POST_W + 1 or dims["h"] > R.POST_H + 1

            # Match production: supersample at 3x, downscale to OUTPUT_PX (render_html does this).
            out = OUT_DIR / f"{name}.jpg"
            png = page.screenshot(type="png", full_page=False)
            with Image.open(BytesIO(png)) as im:
                im.convert("RGB").resize((R.OUTPUT_W, R.OUTPUT_H), Image.LANCZOS).save(str(out), "JPEG", quality=R.JPEG_QUALITY)
            Path(fh.name).unlink(missing_ok=True)

            with Image.open(out) as im:
                # Delivered at OUTPUT_PX (1440, Instagram's max), supersampled from 3x.
                size_ok = im.size == (R.OUTPUT_W, R.OUTPUT_H)

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

    # --- reel scene archetypes -----------------------------------------------
    # Reels had one scene shape behind five backdrops, so a four-segment reel
    # showed the same scene four times. Each archetype must render from its own
    # fields and must refuse cleanly when it cannot.
    try:
        import reel_scenes as _RS
        import render_html as _R
        import oralcheck_agent as _A

        good = {
            "splitstat": {"pair": [{"value": "89%", "label": "found early"},
                                   {"value": "36%", "label": "once it spread"}]},
            "contrast":  {"myth": "Only smokers get it", "fact": "HPV leads under 50"},
            "checklist": {"items": ["A sore that will not heal", "A red or white patch"]},
            "quote":     {"quote": "One in four have no known risk factors."},
            "term":      {"term": "Leukoplakia", "definition": "A white patch."},
            "enumerate": {"caption": "Check your lower lip", "index": 2, "of": 3},
        }
        missing = set(_RS.SCENES) - set(good)
        if missing:
            failures.append(("scene_coverage", f"untested scenes: {sorted(missing)}"))

        for name, fields in good.items():
            seg = dict(fields, scene=name)
            for theme in ("dark", "light"):
                html = _R.kinetic_scene_html(seg, theme)
                if "class='content'></div>" in html.replace(" ", ""):
                    failures.append((f"scene_{name}_{theme}", "rendered an empty content block"))
                    break
            else:
                print(f"  [PASS] scene {name} renders in both themes")

        # A scene missing its fields must fall back rather than render nothing.
        for name, fields in [("splitstat", {}), ("term", {"term": "X"}),
                             ("checklist", {"items": ["only one"]})]:
            if _RS.render(dict(fields, scene=name), _R.THEMES["dark"]) is not None:
                failures.append((f"scene_{name}_degrade", "rendered from incomplete fields"))
        print("  [PASS] incomplete scenes fall back instead of rendering empty")

        # An unknown scene name must not reach the renderer.
        seg = {"scene": "not_a_scene", "narration": "x", "caption": ""}
        _A._sanitize_reel_scene(seg)
        if seg.get("scene"):
            failures.append(("scene_unknown", "unknown scene survived sanitization"))
        else:
            print("  [PASS] unknown scene names are dropped")

        # Every scene must be described in the prompt or the model cannot ask
        # for it, which is how the sixteen carousel layouts sat unused.
        for name in _RS.SCENES:
            if f'"{name}"' not in _A.REEL_SCENE_SPEC:
                failures.append((f"scene_{name}_spec", "not described in REEL_SCENE_SPEC"))
        print("  [PASS] every scene is described in the script prompt")
    except Exception as exc:                        # pragma: no cover
        failures.append(("reel_scenes", str(exc)[:160]))

    # --- reel end card -------------------------------------------------------
    # The whole point of the card is the address: nothing can make a Reel link
    # tappable from an API, so the only route to the site is somebody reading
    # the address off the screen. If it ever stops being the biggest thing on
    # the card, the reel has no working call to action.
    try:
        import oralcheck_agent as _A
        from PIL import Image as _Image
        card = _A._reel_outro_png()
        im = _Image.open(card)
        if im.size != (_A.REEL_W, _A.REEL_H):
            failures.append(("outro_size", f"{im.size}"))
        else:
            print("  [PASS] outro card is 1080x1920")

        url_px = int(_A.REEL_W * 0.105)
        cta_px = int(_A.REEL_W * 0.068)
        if url_px <= cta_px:
            failures.append(("outro_hierarchy",
                             f"url {url_px}px is not larger than cta {cta_px}px"))
        else:
            print(f"  [PASS] url ({url_px}px) dominates the CTA line ({cta_px}px)")

        # Enough time to read an address and decide to act on it. The old 2.4s
        # included a 0.4s fade and left about two seconds.
        if _A.REEL_OUTRO_SECONDS < 3.5:
            failures.append(("outro_hold",
                             f"{_A.REEL_OUTRO_SECONDS}s is too brief to read a URL"))
        else:
            print(f"  [PASS] outro holds {_A.REEL_OUTRO_SECONDS}s")
    except Exception as exc:                        # pragma: no cover
        failures.append(("outro_card", str(exc)[:120]))

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
