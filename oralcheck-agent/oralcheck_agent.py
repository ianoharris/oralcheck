#!/usr/bin/env python3
"""
OralCheck Instagram Content Pipeline
Generates oral cancer awareness content and saves to local queue for review.
Use review_server.py to preview and approve posts.
"""

import argparse
import atexit
import json
import logging
import os
import re
import shutil
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic
import subprocess

import httpx
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

import content_calendar
import ideas

try:
    import render_html as _html_render
    _USE_HTML_RENDER = True
except ImportError:
    _USE_HTML_RENDER = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("oralcheck")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# PUBLORA is only used by the legacy publora_post path; the active poster
# (telegram_review.py) uses the Instagram Graph API, so it isn't required here.
_REQUIRED_ENV = ["ANTHROPIC_API_KEY"]
_STOCK_ENV    = ["PEXELS_API_KEY", "UNSPLASH_ACCESS_KEY"]


def _validate_env() -> None:
    missing = [k for k in _REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        log.error("Missing required environment variables: %s", ", ".join(missing))
        log.error("Copy .env.example to .env and fill in the values.")
        sys.exit(1)
    missing_stock = [k for k in _STOCK_ENV if not os.environ.get(k)]
    if missing_stock:
        log.warning("Stock photo API keys not set (%s) -- set at least one in .env", ", ".join(missing_stock))


_validate_env()

ANTHROPIC_API_KEY   = os.environ["ANTHROPIC_API_KEY"]
PUBLORA_API_KEY     = os.environ.get("PUBLORA_API_KEY", "")
PEXELS_API_KEY      = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

PILLARS_FILE = Path(__file__).parent / "pillars.json"
QUEUE_DIR    = Path(__file__).parent / "queue"

CONTENT_MODEL = "claude-sonnet-4-6"

PILLARS = ["stats", "myth_busting", "self_exam", "hpv_connection", "screener_cta"]

PILLAR_BRIEFS = {
    "stats": (
        "Create a post anchored in a compelling oral cancer statistic. "
        "Examples: '54,000 Americans are diagnosed yearly', '84% survival when caught early'. "
        "Lead with the number, follow with what the audience can do about it."
    ),
    "myth_busting": (
        "Bust a common myth about oral cancer. Key myth: 'Only smokers get oral cancer' -- "
        "false. HPV is now the leading cause in adults under 50. Be clear without being preachy."
    ),
    "self_exam": (
        "Teach followers how to do a quick oral cancer self-exam. "
        "What to look for: white or red patches, sores that don't heal, lumps, difficulty swallowing. "
        "Make it feel approachable, not scary."
    ),
    "hpv_connection": (
        "Explain the HPV-oral cancer connection. Fastest growing group is adults aged 35-55. "
        "Many people don't know HPV can cause oral cancer. Lead with that gap in awareness."
    ),
    "screener_cta": (
        "Drive followers to take the free risk screener at oralcheck.org. "
        "Key message: 10 questions, 2 minutes, free. Make it feel low-effort and high-value."
    ),
    "awareness": (
        "A branded post tied to a specific awareness day or holiday. Anchor the post to the date "
        "and its meaning, then connect it back to oral cancer early detection and the free screener."
    ),
    "light_lane": (
        "A lighter, more human or gently witty take that still respects the subject. Warmth and "
        "relatability over shock, never a joke at the expense of patients or the disease. Keep the "
        "brand voice calm and grounded, and still close with the oralcheck.org screener."
    ),
}

WRITING_STYLE_RULES = """
Sentence rhythm: sentences build toward a point rather than dropping ideas abruptly. Ideas are
developed across the sentence, not compressed into fragments. Prose flows naturally; bullets are
used only when content is genuinely list-like.

Contractions are welcome even in professional contexts (can't, it's, you're).

No em dashes. No colons or semicolons unless genuinely necessary.

Tone is warm and grounded, never stiff, never effusive. Specific and earned over hollow or generic.
Avoid filler phrases like "It's important to note," "Please don't hesitate," or "Certainly."

Frame statements as observed facts rather than absolute declarations. The voice carries confidence
through specificity (a precise stat, a concrete action) rather than proclamation.
"""

SYSTEM_PROMPT = (
    "You are a content strategist for OralCheck (oralcheck.org), a free oral cancer risk screener.\n\n"
    "Brand voice rules (follow these exactly, and if anything below conflicts, these win):\n"
    "- Direct, not alarmist\n"
    "- Lead with a stat or fact, follow with action\n"
    "- No exclamation marks\n"
    "- Never say 'we'\n"
    "- No medical jargon, plain language only\n"
    "- Every caption ends with a call to action that includes oralcheck.org\n"
    "- NEVER use em dashes (--) in any output, not even in hooks or captions -- use a period or rewrite the sentence instead\n"
    "- hashtags must ALL be lowercase, no camelCase (e.g. 'oralcancer' not 'oralCancer')\n\n"
    "Caption writing style (apply these to all captions; brand voice rules above take priority on any conflict):\n"
    + WRITING_STYLE_RULES.strip()
    + "\n\nStock photo search query guidance (for image and carousel posts):\n"
    "- Write a concise 3-6 word search query that will surface real photography on Pexels/Unsplash.\n"
    "- Focus on real human subjects: faces, smiling people, doctor-patient moments, close-up dental/mouth shots.\n"
    "- Avoid abstract or object-only queries -- we need people in the frame.\n"
    "- No cliches: no white coats, no stethoscopes, no generic 'doctor smiling at camera'.\n"
    "- Good examples: 'person smiling natural light', 'close up mouth teeth', 'young adult medical appointment',\n"
    "  'worried person health checkup', 'diverse people wellness'.\n"
    "- For video (reels), search_query should be portrait-friendly and human-focused\n"
    "  (e.g. 'person dental exam', 'smiling woman health checkup', 'close up mouth teeth').\n"
)

MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# Temp file cleanup registry
# ---------------------------------------------------------------------------

_tmp_files: list[str] = []


def _register_tmp(path: str) -> str:
    _tmp_files.append(path)
    return path


@atexit.register
def _cleanup_tmp() -> None:
    for path in _tmp_files:
        try:
            Path(path).unlink(missing_ok=True)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Retry wrapper
# ---------------------------------------------------------------------------

def _with_retry(fn, *args, max_attempts: int = 3, base_delay: float = 2.0, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except (httpx.TransportError, httpx.TimeoutException) as exc:
            if attempt == max_attempts:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            log.warning("Transient error (attempt %d/%d): %s -- retrying in %.1fs", attempt, max_attempts, exc, delay)
            time.sleep(delay)
        except httpx.HTTPStatusError as exc:
            if attempt == max_attempts or exc.response.status_code < 500:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            log.warning("HTTP %d (attempt %d/%d) -- retrying in %.1fs", exc.response.status_code, attempt, max_attempts, delay)
            time.sleep(delay)


# ---------------------------------------------------------------------------
# Pillar rotation
# ---------------------------------------------------------------------------

def load_pillar_state() -> dict:
    if PILLARS_FILE.exists():
        with open(PILLARS_FILE) as f:
            return json.load(f)
    return {"last_pillar": None, "history": []}


def save_pillar_state(state: dict) -> None:
    with open(PILLARS_FILE, "w") as f:
        json.dump(state, f, indent=2)


def pick_next_pillar(state: dict) -> str:
    last = state.get("last_pillar")
    history = state.get("history", [])
    candidates = [p for p in PILLARS if p != last]
    candidates.sort(key=lambda p: history.index(p) if p in history else -1)
    return candidates[0]


def record_pillar_used(state: dict, pillar: str) -> dict:
    history = state.get("history", [])
    if pillar in history:
        history.remove(pillar)
    history.append(pillar)
    return {**state, "last_pillar": pillar, "history": history}


# ---------------------------------------------------------------------------
# Content generation (Anthropic)
# ---------------------------------------------------------------------------

def _strip_dashes(text: str) -> str:
    """Enforce the no-em-dash brand rule on any model-produced string."""
    if not isinstance(text, str):
        return text
    return text.replace(" -- ", ", ").replace("--", ", ").replace(" — ", ", ").replace("—", ", ")


_VALID_SLIDE_TYPES = {"stat", "fact", "list", "quote"}


def _sanitize_carousel_slides(slides: list) -> list[dict]:
    """Validate and clean typed carousel slides, dropping malformed ones.

    Guarantees each returned slide has the fields its type needs, keeps at most
    5 slides, and strips em dashes from every text field.
    """
    clean: list[dict] = []
    for s in slides:
        if not isinstance(s, dict):
            continue
        t = str(s.get("type", "fact")).lower().strip()
        if t not in _VALID_SLIDE_TYPES:
            t = "fact"
        if t == "stat":
            value = str(s.get("value", "")).strip()
            label = _strip_dashes(str(s.get("label", "")).strip())
            if not value or not label:
                continue
            clean.append({"type": "stat", "value": value, "label": label,
                          "detail": _strip_dashes(str(s.get("detail", "")).strip())})
        elif t == "list":
            items = [_strip_dashes(str(i).strip()) for i in s.get("items", []) if str(i).strip()]
            headline = _strip_dashes(str(s.get("headline", "")).strip())
            if not headline or len(items) < 2:
                continue
            clean.append({"type": "list", "headline": headline, "items": items[:5]})
        elif t == "quote":
            text = _strip_dashes(str(s.get("text", "")).strip())
            if not text:
                continue
            clean.append({"type": "quote", "text": text,
                          "attribution": _strip_dashes(str(s.get("attribution", "")).strip())})
        else:  # fact
            headline = _strip_dashes(str(s.get("headline", "")).strip())
            body = _strip_dashes(str(s.get("body", "")).strip())
            if not headline or not body:
                continue
            clean.append({"type": "fact", "headline": headline, "body": body})
    return clean[:5]


def build_deck_from_content(content: dict, photo_path: str | None) -> dict:
    """Map generated carousel content + a fetched photo into a render_html deck spec.

    The cover is purely typographic. The photo appears as its own full-bleed slide
    mid-deck so every carousel carries real imagery (which lifts engagement) without
    the awkward text-over-photo cover composition.
    """
    slides = list(content.get("slides", []))
    photo_caption = _strip_dashes(content.get("photo_caption", "")).strip()

    if photo_path:
        insert_at = 1 if len(slides) >= 2 else len(slides)
        slides.insert(insert_at, {"type": "photo", "photo": photo_path, "caption": photo_caption})

    return {
        "kicker": content.get("kicker", ""),
        "cover": {"hook": content.get("hook", "")},
        "slides": slides,
        "cta": {},
    }


def generate_content(brief: str, media_type: str) -> dict:
    if media_type == "infographic":
        media_note = (
            "This is for a data-driven Instagram infographic (1080x1080 square). "
            "A PIL chart renderer will draw horizontal bars comparing two or three stats. "
            "Choose a compelling angle from the pillar brief below. Examples:\n"
            "  - Survival rate comparison (early vs late detection)\n"
            "  - Risk factor breakdown (HPV, tobacco, alcohol, age)\n"
            "  - Awareness gap (% who can ID symptoms vs % who can't)\n"
            "Output JSON with exactly these fields:\n"
            "  headline: punchy statement, 8 words max (no question marks)\n"
            "  context: 3-5 word label describing what the bars measure (e.g. '5-year survival rate')\n"
            "  bars: array of 2-3 objects, each with:\n"
            "    label: short bar label (3-5 words, e.g. 'Caught early')\n"
            "    value: integer 0-100 (percentage for bar width)\n"
            "    value_str: display text (e.g. '84%' or '1 in 3')\n"
            "  fact: one source/context sentence under 20 words (e.g. 'Source: Oral Cancer Foundation')\n"
            "  caption: full Instagram caption with oralcheck.org CTA\n"
            "  hashtags: exactly 5 lowercase tags\n"
            "Note: value is used to determine bar width (0-100 scale). If stat is not a percentage, "
            "normalize to 0-100 for visual proportion but use value_str for display."
        )
    elif media_type == "animated":
        media_note = (
            "This is for an animated Instagram Reel. A Manim motion-graphics scene will reveal "
            "a key oral health stat with brand animation. "
            "Output JSON with exactly these fields: "
            "hook (punchy one-liner, 10 words max, no question mark needed -- e.g. 'Most people miss the early signs'), "
            "stat (short compelling number or phrase, e.g. '84%' or '54,000 Americans'), "
            "stat_context (5 words max label for the stat, e.g. 'early-stage survival rate'), "
            "fact (one clear supporting sentence, 25 words max, no em dashes), "
            "caption (full Instagram caption with oralcheck.org CTA), "
            "hashtags (exactly 5 lowercase tags)."
        )
    elif media_type == "reel":
        media_note = (
            "This is for an Instagram Reel (portrait 9:16 video). "
            "A real stock video will be fetched from Pexels using your search_query, "
            "then branded text will be overlaid on it. "
            "Output JSON with fields: hook, caption, "
            "search_query (3-6 word Pexels video search, portrait-friendly and human-focused -- "
            "e.g. 'person dental exam', 'smiling woman wellness', 'young adult health checkup', "
            "'close up mouth teeth'), hashtags (exactly 5 tags)."
        )
    elif media_type == "carousel":
        media_note = (
            "This is for an Instagram Carousel with a designed template system. The renderer builds:\n"
            "  - a cover slide (your hook, over a real stock photo)\n"
            "  - a mid-deck photo slide (uses your photo_caption)\n"
            "  - your typed content slides, rendered in distinct brand layouts\n"
            "  - an auto-generated CTA closing slide (do NOT include it)\n\n"
            "Output JSON with these exact fields:\n"
            "  hook: cover headline, 10 words max, the single strongest insight or surprising-true fact\n"
            "  kicker: 2-4 word topic eyebrow in title case (e.g. 'HPV & Oral Cancer', 'Know The Signs')\n"
            "  search_query: 3-6 word Pexels/Unsplash query for the photo (real people, human-focused)\n"
            "  photo_caption: one line, 14 words max, that pairs with the photo mid-deck\n"
            "  slides: array of 3 to 4 typed content slides. Each object has a 'type' plus fields:\n"
            "    - {\"type\":\"stat\", \"value\":\"70%\", \"label\":\"6-10 word plain-language meaning\", \"detail\":\"one 12-18 word supporting sentence\"}\n"
            "    - {\"type\":\"fact\", \"headline\":\"6-8 word serif headline\", \"body\":\"20-30 word supporting paragraph\"}\n"
            "    - {\"type\":\"list\", \"headline\":\"4-6 word headline\", \"items\":[\"3 to 5 short items, 4-8 words each\"]}\n"
            "    - {\"type\":\"quote\", \"text\":\"a short, human, 8-14 word line\", \"attribution\":\"who said it, optional\"}\n"
            "  caption: full Instagram caption ending with an oralcheck.org CTA\n"
            "  hashtags: exactly 5 lowercase tags\n\n"
            "Rules for the slides array:\n"
            "  - Include at least one 'stat' slide and at least one 'fact' slide.\n"
            "  - Use a 'list' slide when the pillar is about signs, symptoms, or steps.\n"
            "  - Vary the types, do not output three of the same type.\n"
            "  - Slides must tell a cohesive story: surprising hook -> why it matters -> what to do -> (auto CTA).\n"
            "  - Every stat 'value' must be a real, defensible number for oral cancer. No invented statistics."
        )
    else:
        media_note = (
            "This is for a static Instagram image post (square format). "
            "Background will be a real stock photo fetched from Pexels/Unsplash. "
            "Output JSON with fields: hook, caption, search_query (3-6 word Pexels search query, human-focused), hashtags (exactly 5 tags)."
        )

    def _call():
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CONTENT_MODEL,
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"{brief}\n\n{media_note}\n\nOutput valid JSON only, no markdown fences.",
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw_lines = raw.split("\n")
            raw = "\n".join(raw_lines[1:-1]) if raw_lines[-1].strip() == "```" else "\n".join(raw_lines[1:])
        data = json.loads(raw)

        if media_type == "infographic":
            required = {"headline", "context", "bars", "fact", "caption", "hashtags"}
            if "hook" not in data:
                data["hook"] = data.get("headline", "")
        elif media_type == "animated":
            required = {"hook", "caption", "hashtags", "stat", "stat_context", "fact"}
        elif media_type == "carousel":
            required = {"hook", "caption", "hashtags", "search_query", "slides"}
            data.setdefault("kicker", "")
            data.setdefault("photo_caption", "")
            data["slides"] = _sanitize_carousel_slides(data.get("slides", []))
            if not data["slides"]:
                raise ValueError("carousel produced no valid content slides")
        elif media_type == "reel":
            required = {"hook", "caption", "hashtags", "search_query"}
        else:
            required = {"hook", "caption", "hashtags", "search_query"}
        missing_keys = required - data.keys()
        if missing_keys:
            raise ValueError(f"Claude response missing keys: {missing_keys}")

        tags = [h.lower().strip().lstrip("#") for h in data.get("hashtags", [])]
        data["hashtags"] = tags[:5]
        return data

    return _with_retry(_call)


import random


def fetch_stock_photo(query: str, size: int = 1080) -> str:
    """Fetch a real stock photo from Pexels (primary) or Unsplash (fallback).
    Returns local JPEG path cropped/resized to size x size."""

    def _try_pexels() -> str | None:
        if not PEXELS_API_KEY:
            return None
        url = "https://api.pexels.com/v1/search"
        params = {"query": query, "per_page": 15, "orientation": "square"}
        headers = {"Authorization": PEXELS_API_KEY}
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, params=params, headers=headers)
            resp.raise_for_status()
        photos = resp.json().get("photos", [])
        if not photos:
            return None
        photo = random.choice(photos[:10])
        img_url = photo["src"].get("large2x") or photo["src"]["original"]
        log.info("Pexels photo: %s (id=%s)", img_url[:60], photo["id"])
        return img_url

    def _try_unsplash() -> str | None:
        if not UNSPLASH_ACCESS_KEY:
            return None
        url = "https://api.unsplash.com/search/photos"
        params = {"query": query, "per_page": 15, "orientation": "squarish"}
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, params=params, headers=headers)
            resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            return None
        photo = random.choice(results[:10])
        img_url = photo["urls"].get("regular") or photo["urls"]["full"]
        log.info("Unsplash photo: %s (id=%s)", img_url[:60], photo["id"])
        return img_url

    img_url = _try_pexels() or _try_unsplash()
    if not img_url:
        raise RuntimeError(
            f"No stock photos found for query '{query}'. "
            "Check PEXELS_API_KEY / UNSPLASH_ACCESS_KEY in .env."
        )

    with httpx.Client(timeout=60, follow_redirects=True) as client:
        resp = client.get(img_url)
        resp.raise_for_status()
        content = resp.content

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp.write(content)
    tmp.close()
    _register_tmp(tmp.name)

    img = Image.open(tmp.name).convert("RGB")
    w, h = img.size
    crop_size = min(w, h)
    left = (w - crop_size) // 2
    top  = (h - crop_size) // 2
    img  = img.crop((left, top, left + crop_size, top + crop_size))
    img  = img.resize((size, size), Image.LANCZOS)
    img.save(tmp.name, "JPEG", quality=95)

    log.info("Stock photo saved: %s (%dx%d)", tmp.name, size, size)
    return tmp.name


def fetch_stock_video(query: str) -> str:
    """Fetch a portrait stock video from Pexels. Returns local .mp4 path."""
    if not PEXELS_API_KEY:
        raise RuntimeError("PEXELS_API_KEY required for reel generation. Set it in .env.")

    params = {"query": query, "per_page": 15, "orientation": "portrait"}
    headers = {"Authorization": PEXELS_API_KEY}
    with httpx.Client(timeout=15) as client:
        resp = client.get("https://api.pexels.com/videos/search", params=params, headers=headers)
        resp.raise_for_status()

    videos = resp.json().get("videos", [])
    if not videos:
        raise RuntimeError(f"No Pexels videos found for query '{query}'.")

    video = random.choice(videos[:10])
    files = video.get("video_files", [])
    mp4_files = [f for f in files if f.get("file_type") == "video/mp4"]
    portrait_mp4 = [f for f in mp4_files if f.get("height", 0) > f.get("width", 0)]
    candidates = portrait_mp4 or mp4_files
    candidates.sort(key=lambda f: f.get("width", 0), reverse=True)
    best = candidates[0] if candidates else None
    if not best:
        raise RuntimeError(f"No MP4 files found for Pexels query '{query}'.")

    log.info("Pexels video: id=%s %dx%d", video["id"], best.get("width", 0), best.get("height", 0))
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        resp = client.get(best["link"])
        resp.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp.write(resp.content)
    tmp.close()
    _register_tmp(tmp.name)
    log.info("Stock video saved: %s (%d KB)", tmp.name, len(resp.content) // 1024)
    return tmp.name


def _render_overlay_frame(i: int, total: int, W: int, H: int, hook: str, cta: str) -> Image.Image:
    """Render one RGBA frame of the animated text overlay. t goes 0.0 -> 1.0."""
    t = i / max(total - 1, 1)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = int(W * 0.07)
    inner_w = W - 2 * margin
    hook_size = int(W * 0.065)
    hook_font = _load_font("DMSerifDisplay-Regular.ttf", hook_size)
    cta_size = int(W * 0.038)
    cta_font = _load_font("SourceSans3-Regular.ttf", cta_size)

    wrapped_hook = _wrap_text(hook, hook_font, inner_w)
    line_count = wrapped_hook.count("\n") + 1
    cta_y = H - int(H * 0.055)
    hook_y = cta_y - (line_count * int(hook_size * 1.25)) - int(H * 0.025)
    bar_y = hook_y - int(H * 0.022)

    # Scrim gradient fades in (t=0.0-0.4)
    scrim_alpha = min(1.0, t / 0.4)
    gradient_start = int(H * 0.55)
    for y in range(gradient_start, H):
        base_t = (y - gradient_start) / (H - gradient_start)
        base_alpha = int(210 * (base_t ** 0.7))
        draw.line([(0, y), (W, y)], fill=(13, 26, 27, int(base_alpha * scrim_alpha)))

    # Teal bar slides in from left (t=0.3-0.7)
    bar_phase = max(0.0, min(1.0, (t - 0.3) / 0.4))
    bar_w = int(int(W * 0.08) * bar_phase)
    if bar_w > 0:
        draw.rectangle([(margin, bar_y), (margin + bar_w, bar_y + 4)], fill=(13, 115, 119, 255))

    # Hook text fades in and rises (t=0.5-1.0)
    hook_phase = max(0.0, min(1.0, (t - 0.5) / 0.5))
    if hook_phase > 0:
        rise = int(H * 0.015 * (1.0 - hook_phase))
        draw.text(
            (margin, hook_y + rise), wrapped_hook,
            font=hook_font,
            fill=(232, 228, 222, int(255 * hook_phase)),
            spacing=int(hook_size * 0.2),
        )

    # CTA fades in (t=0.75-1.0)
    cta_phase = max(0.0, min(1.0, (t - 0.75) / 0.25))
    if cta_phase > 0:
        draw.text((margin, cta_y), cta, font=cta_font, fill=(13, 115, 119, int(255 * cta_phase)))

    return img


def add_animated_text_overlay_video(video_path: str, hook: str, cta: str = "oralcheck.org") -> str:
    """Animated hook + CTA over stock video using PNG frame sequence for alpha compositing."""
    W, H = 1080, 1920
    FPS = 24
    ANIM_FRAMES = 36  # 1.5 s of animation, then holds last frame indefinitely

    frame_dir = tempfile.mkdtemp(prefix="overlay_frames_")
    _register_tmp(frame_dir)

    log.info("Rendering %d animation frames for text overlay...", ANIM_FRAMES)
    for i in range(ANIM_FRAMES):
        frame = _render_overlay_frame(i, ANIM_FRAMES, W, H, hook, cta)
        frame.save(os.path.join(frame_dir, f"frame_{i:04d}.png"))

    out_tmp = tempfile.NamedTemporaryFile(suffix="_reel.mp4", delete=False)
    out_tmp.close()
    _register_tmp(out_tmp.name)

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-framerate", str(FPS), "-i", os.path.join(frame_dir, "frame_%04d.png"),
            "-filter_complex",
            (
                f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H}[v];"
                f"[1:v]loop=loop=-1:size=1:start={ANIM_FRAMES - 1}[anim];"
                f"[v][anim]overlay=0:0:format=auto:shortest=1"
            ),
            "-c:v", "libx264", "-crf", "20", "-preset", "fast",
            "-an",
            out_tmp.name,
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg composite failed:\n{result.stderr.decode()}")

    log.info("Animated video overlay applied -> %s", out_tmp.name)
    return out_tmp.name


# ---------------------------------------------------------------------------
# Manim animated reel (stat-reveal format)
# ---------------------------------------------------------------------------

MANIM_REEL_TEMPLATE = """\
from manim import *
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_height = 16

BG     = "#0d1a1b"
TEAL   = "#0d7377"
CORAL  = "#e8634a"
OFFWHT = "#e8e4de"
MUTED  = "#5a7476"

HOOK         = {hook!r}
STAT         = {stat!r}
STAT_CONTEXT = {stat_context!r}
FACT         = {fact!r}


class OralCheckStatReveal(Scene):
    def construct(self):
        self.camera.background_color = BG

        # Brand mark
        dot = Dot(color=CORAL, radius=0.18)
        brand = Text("OralCheck", font="DM Serif Display", font_size=32, color=TEAL)
        brand.next_to(dot, RIGHT, buff=0.22)
        mark = VGroup(dot, brand).move_to(UP * 6.9)

        self.play(FadeIn(mark, shift=DOWN * 0.3), run_time=0.7)
        self.wait(0.2)

        # Hook
        hook_mob = Text(
            HOOK, font="DM Serif Display", font_size=52,
            color=OFFWHT, line_spacing=1.3,
        )
        hook_mob.set_width(min(hook_mob.width, 8.2)).move_to(UP * 4.0)
        self.play(FadeIn(hook_mob, shift=UP * 0.35), run_time=0.9)
        self.wait(0.4)

        # Teal divider
        div = Line(LEFT * 4.2, RIGHT * 4.2, color=TEAL, stroke_width=3)
        div.move_to(UP * 2.0)
        self.play(Create(div), run_time=0.5)

        # Stat
        stat_mob = Text(
            STAT, font="DM Serif Display", font_size=80, color=CORAL,
        )
        stat_mob.set_width(min(stat_mob.width, 8.5)).move_to(UP * 0.4)
        ctx_mob = Text(
            STAT_CONTEXT, font="Source Sans 3", font_size=30, color=MUTED,
        )
        ctx_mob.next_to(stat_mob, DOWN, buff=0.4)

        self.play(FadeIn(stat_mob, scale=0.88), run_time=0.7)
        self.wait(0.2)
        self.play(FadeIn(ctx_mob, shift=UP * 0.2), run_time=0.5)
        self.wait(0.4)

        # Fact
        fact_mob = Text(
            FACT, font="Source Sans 3", font_size=30,
            color=OFFWHT, line_spacing=1.3,
        )
        fact_mob.set_width(min(fact_mob.width, 8.2)).move_to(DOWN * 2.5)
        self.play(FadeIn(fact_mob, shift=UP * 0.25), run_time=0.8)
        self.wait(0.5)

        # CTA bar slides up from bottom
        bar = Rectangle(
            width=9, height=2.8,
            fill_color=TEAL, fill_opacity=1, stroke_width=0,
        )
        url_txt = Text(
            "oralcheck.org", font="DM Serif Display", font_size=46, color=BG,
        )
        sub_txt = Text(
            "free  ·  private  ·  2 minutes",
            font="Source Sans 3", font_size=22, color=BG,
        )
        url_txt.move_to(ORIGIN)
        sub_txt.next_to(url_txt, DOWN, buff=0.2)
        cta = VGroup(bar, url_txt, sub_txt).move_to(DOWN * 6.6)
        cta.shift(DOWN * 3.5)

        self.play(cta.animate.shift(UP * 3.5), run_time=0.9, rate_func=smooth)
        self.wait(1.8)
"""


def _break_text(text: str, max_chars: int = 28) -> str:
    """Insert newlines so Manim Text wraps at approximately max_chars per line."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def render_manim_reel(content: dict) -> str:
    """Render a branded animated stat-reveal reel with Manim. Returns local .mp4 path."""
    hook = _break_text(content.get("hook", ""), max_chars=28)
    stat = content.get("stat", "")
    stat_context = content.get("stat_context", "")
    fact = _break_text(content.get("fact", ""), max_chars=40)

    scene_code = MANIM_REEL_TEMPLATE.format(
        hook=hook, stat=stat, stat_context=stat_context, fact=fact,
    )

    work_dir = tempfile.mkdtemp(prefix="manim_reel_")
    _register_tmp(work_dir)
    scene_file = os.path.join(work_dir, "reel_scene.py")
    with open(scene_file, "w") as f:
        f.write(scene_code)

    out_dir = os.path.join(work_dir, "out")
    os.makedirs(out_dir)

    log.info("Rendering Manim animated reel (30-90 seconds)...")
    result = subprocess.run(
        [
            "python3.11", "-m", "manim",
            scene_file, "OralCheckStatReveal",
            "--media_dir", out_dir,
            "--output_file", "reel.mp4",
            "--disable_caching",
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Manim render failed:\n{result.stderr[-3000:]}")

    mp4_files = list(Path(out_dir).rglob("reel.mp4"))
    if not mp4_files:
        mp4_files = list(Path(out_dir).rglob("*.mp4"))
    if not mp4_files:
        raise RuntimeError(f"Manim output not found in {out_dir}.\nstderr: {result.stderr[-2000:]}")

    out_path = str(mp4_files[0])
    log.info("Manim reel rendered: %s", out_path)
    return out_path


# ---------------------------------------------------------------------------
# Text overlay (hook + CTA composited over AI background)
# ---------------------------------------------------------------------------

FONTS_DIR = Path(__file__).parent / "fonts"

C_TEAL     = (13, 115, 119, 255)
C_OFFWHITE = (250, 249, 246, 210)
C_DARK     = (45, 45, 45, 255)


def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONTS_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    log.warning("Font not found: %s -- using PIL default.", path)
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        _, _, right, _ = draw.textbbox((0, 0), candidate, font=font)
        if right <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def add_text_overlay(image_path: str, hook: str, cta: str = "oralcheck.org") -> str:
    """Composite hook text and CTA over a full-bleed background image."""
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size

    # Dark gradient from 35% down → cinematic, editorial feel
    gradient = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    gradient_start = int(h * 0.35)
    for y in range(gradient_start, h):
        t = (y - gradient_start) / (h - gradient_start)
        alpha = int(224 * min(1.0, t ** 0.55))
        grad_draw.line([(0, y), (w, y)], fill=(13, 26, 27, alpha))

    img = Image.alpha_composite(img, gradient)
    draw = ImageDraw.Draw(img)

    margin = int(w * 0.07)
    inner_w = w - 2 * margin

    hook_size = int(w * 0.075)
    hook_font = _load_font("DMSerifDisplay-Regular.ttf", hook_size)
    cta_size  = int(w * 0.036)
    cta_font  = _load_font("SourceSans3-Regular.ttf", cta_size)

    wrapped_hook = _wrap_text(hook, hook_font, inner_w)
    line_count = wrapped_hook.count("\n") + 1

    cta_y  = h - int(h * 0.055)
    hook_y = cta_y - (line_count * int(hook_size * 1.25)) - int(h * 0.03)
    bar_y  = hook_y - int(h * 0.024)

    # Coral accent line above hook text
    draw.rectangle([(margin, bar_y), (margin + int(w * 0.06), bar_y + 4)], fill=(232, 99, 74, 255))
    # Light text on dark gradient
    draw.text((margin, hook_y), wrapped_hook, font=hook_font, fill=(232, 228, 222), spacing=int(hook_size * 0.2))
    draw.text((margin, cta_y), cta, font=cta_font, fill=(13, 115, 119, 255))

    p = Path(image_path)
    out_path = str(p.parent / (p.stem + "_final" + p.suffix))
    img.convert("RGB").save(out_path, "JPEG", quality=95)
    _register_tmp(out_path)
    log.info("Text overlay applied -> %s", out_path)
    return out_path


# ---------------------------------------------------------------------------
# Brand slide renderers (pure PIL, no AI)
# ---------------------------------------------------------------------------

C_BG       = (13, 26, 27)      # #0d1a1b
C_TEAL_RGB = (13, 115, 119)    # #0d7377
C_TEXT     = (232, 228, 222)   # #e8e4de
C_MUTED    = (90, 116, 118)    # #5a7476
C_CORAL    = (232, 99, 74)     # #e8634a


def _render_info_slide(headline: str, body: str) -> str:
    """PIL-rendered info slide: dark brand background with headline + body text."""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)

    pad = 80
    inner_w = W - 2 * pad

    headline_font = _load_font("DMSerifDisplay-Regular.ttf", 64)
    body_font     = _load_font("SourceSans3-Regular.ttf", 30)
    mark_font     = _load_font("SourceSans3-Regular.ttf", 20)

    # Brand mark
    draw.ellipse([(pad, 52), (pad + 10, 62)], fill=C_CORAL)
    draw.text((pad + 18, 50), "OralCheck", font=mark_font, fill=C_TEAL_RGB)
    draw.rectangle([(pad, 78), (W - pad, 80)], fill=(22, 50, 52))

    wrapped_headline = _wrap_text(headline, headline_font, inner_w)
    headline_lines = wrapped_headline.count("\n") + 1
    headline_h = headline_lines * 80

    wrapped_body = _wrap_text(body, body_font, inner_w)
    body_lines = wrapped_body.count("\n") + 1
    body_h = body_lines * 44

    content_h = headline_h + 48 + body_h
    content_y = max((H - content_h) // 2, 160)

    # Short coral accent above headline
    draw.rectangle([(pad, content_y - 22), (pad + 48, content_y - 18)], fill=C_CORAL)

    draw.text((pad, content_y), wrapped_headline, font=headline_font, fill=C_TEXT, spacing=16)
    draw.text((pad, content_y + headline_h + 48), wrapped_body, font=body_font, fill=C_MUTED, spacing=14)

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name, "JPEG", quality=95)
    tmp.close()
    _register_tmp(tmp.name)
    return tmp.name


def _render_cta_slide() -> str:
    """PIL-rendered CTA slide: teal background with screener prompt."""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), C_TEAL_RGB)
    draw = ImageDraw.Draw(img)

    pad = 80
    inner_w = W - 2 * pad

    headline_font = _load_font("DMSerifDisplay-Regular.ttf", 76)
    url_font      = _load_font("SourceSans3-Regular.ttf", 38)
    sub_font      = _load_font("SourceSans3-Regular.ttf", 22)

    headline_text = "Take the free screener."
    wrapped = _wrap_text(headline_text, headline_font, inner_w)
    lines = wrapped.count("\n") + 1
    headline_h = lines * 96

    total_h = headline_h + 44 + 50
    y_start = max((H - total_h) // 2 - 30, 120)

    draw.text((pad, y_start), wrapped, font=headline_font, fill=C_BG, spacing=14)
    draw.text((pad, y_start + headline_h + 44), "oralcheck.org", font=url_font, fill=C_BG)

    draw.rectangle([(0, H - 8), (W, H)], fill=C_CORAL)
    draw.text((pad, H - 50), "free   private   2 minutes", font=sub_font, fill=(9, 80, 83))

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name, "JPEG", quality=95)
    tmp.close()
    _register_tmp(tmp.name)
    return tmp.name


# ---------------------------------------------------------------------------
# Infographic renderer (pure PIL, data-driven)
# ---------------------------------------------------------------------------

def render_infographic_image(content: dict) -> str:
    """Render a branded data infographic: hero stats on dark brand background."""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)

    pad = 76

    brand_font    = _load_font("SourceSans3-Regular.ttf", 20)
    headline_font = _load_font("DMSerifDisplay-Regular.ttf", 52)
    label_font    = _load_font("SourceSans3-Regular.ttf", 24)
    fact_font     = _load_font("SourceSans3-Regular.ttf", 22)
    cta_font      = _load_font("SourceSans3-Regular.ttf", 20)

    # Brand mark: coral dot + name + thin separator
    draw.ellipse([(pad, 52), (pad + 10, 62)], fill=C_CORAL)
    draw.text((pad + 18, 50), "OralCheck", font=brand_font, fill=C_TEAL_RGB)
    draw.rectangle([(pad, 80), (W - pad, 82)], fill=(22, 50, 52))

    # Headline
    headline = content.get("headline", "")
    wrapped_headline = _wrap_text(headline, headline_font, W - 2 * pad)
    headline_y = 106
    draw.text((pad, headline_y), wrapped_headline, font=headline_font, fill=C_TEXT, spacing=12)
    headline_lines = wrapped_headline.count("\n") + 1
    after_headline_y = headline_y + headline_lines * 64 + 32

    bars = content.get("bars", [])
    n_bars = len(bars)
    stat_colors = [C_CORAL, C_TEAL_RGB, (14, 145, 150)]

    # Large font for ≤2 stats, smaller for 3+
    stat_size = 108 if n_bars <= 2 else 82
    stat_font = _load_font("DMSerifDisplay-Regular.ttf", stat_size)

    # Layout: stat number + label + inter-stat gap
    num_h_est    = int(stat_size * 1.05)
    label_h_est  = 34
    gap_between  = 44
    stat_block_h = num_h_est + 8 + label_h_est
    total_stats_h = n_bars * stat_block_h + max(0, n_bars - 1) * gap_between

    fact        = content.get("fact", "")
    cta_reserve = 90
    fact_reserve = 58 if fact else 0

    available = H - after_headline_y - cta_reserve - fact_reserve
    v_offset  = max(0, (available - total_stats_h) // 2)
    current_y = after_headline_y + v_offset

    for idx, bar in enumerate(bars):
        value_str = bar.get("value_str", f"{bar.get('value', 0)}%")
        label     = bar.get("label", "")
        color     = stat_colors[idx % len(stat_colors)]

        # Hero number — bbox returns absolute coords; use bbox bottom for label placement
        draw.text((pad, current_y), value_str, font=stat_font, fill=color)
        num_bbox = draw.textbbox((pad, current_y), value_str, font=stat_font)
        text_bottom = num_bbox[3]  # absolute y of bounding box bottom

        # Label beneath number with a clear gap
        label_y = text_bottom + 10
        wrapped_label = _wrap_text(label, label_font, W - 2 * pad)
        draw.text((pad, label_y), wrapped_label, font=label_font, fill=C_MUTED)
        label_lines = wrapped_label.count("\n") + 1
        block_bottom = label_y + label_lines * 32

        # Thin separator between stats (not after the last one)
        if idx < n_bars - 1:
            sep_y = block_bottom + gap_between // 2
            draw.rectangle([(pad, sep_y), (W - pad, sep_y + 1)], fill=(28, 56, 58))
            current_y = sep_y + gap_between // 2
        else:
            current_y = block_bottom + gap_between

    # Supporting fact
    if fact:
        fact_y = H - cta_reserve - fact_reserve + 6
        wrapped_fact = _wrap_text(fact, fact_font, W - 2 * pad)
        draw.text((pad, fact_y), wrapped_fact, font=fact_font, fill=C_MUTED, spacing=8)

    # CTA
    draw.rectangle([(pad, H - 60), (pad + 44, H - 57)], fill=C_TEAL_RGB)
    draw.text((pad, H - 46), "oralcheck.org", font=cta_font, fill=C_TEAL_RGB)

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name, "JPEG", quality=95)
    tmp.close()
    _register_tmp(tmp.name)
    log.info("Infographic rendered -> %s", tmp.name)
    return tmp.name


# ---------------------------------------------------------------------------
# Carousel generation
# ---------------------------------------------------------------------------

def generate_carousel_slides(content: dict) -> list[str]:
    """
    Build a designed carousel deck:
      Cover (hook over stock photo) -> typed content slides (stat/fact/list/quote)
      with one mid-deck photo slide -> auto CTA closing slide.
    Rendered via the HTML/Playwright design system for crisp typography.
    """
    log.info("Fetching stock photo for carousel (query: %s)...", content["search_query"])
    try:
        raw_path = fetch_stock_photo(content["search_query"])
    except Exception as exc:
        log.warning("Stock photo fetch failed (%s); rendering photo-less carousel.", exc)
        raw_path = None

    if _USE_HTML_RENDER:
        deck = build_deck_from_content(content, raw_path)
        log.info("Rendering carousel deck (%d slides + cover + CTA)...", len(deck["slides"]))
        return _html_render.carousel_deck(deck)

    # Fallback: PIL renderer with flattened typed slides
    paths = []
    if raw_path:
        paths.append(add_text_overlay(raw_path, content["hook"]))
    for slide in content.get("slides", []):
        headline, body = _flatten_slide(slide)
        if headline or body:
            paths.append(_render_info_slide(headline, body))
    paths.append(_render_cta_slide())
    return paths


def _flatten_slide(slide: dict) -> tuple[str, str]:
    """Reduce a typed carousel slide to (headline, body) for the PIL fallback."""
    t = slide.get("type", "fact")
    if t == "stat":
        return slide.get("value", ""), slide.get("label", "")
    if t == "list":
        return slide.get("headline", ""), "  •  ".join(slide.get("items", []))
    if t == "quote":
        return slide.get("text", ""), slide.get("attribution", "")
    return slide.get("headline", ""), slide.get("body", "")


def stitch_carousel_preview(slide_paths: list[str]) -> str:
    """Stitch slides side-by-side for the review server preview strip."""
    PREVIEW_W = 480
    images = []
    for p in slide_paths:
        im = Image.open(p).convert("RGB")
        ratio = PREVIEW_W / im.width
        new_h = int(im.height * ratio)
        images.append(im.resize((PREVIEW_W, new_h), Image.LANCZOS))
    h = images[0].height
    strip = Image.new("RGB", (PREVIEW_W * len(images), h), C_BG)
    for i, im in enumerate(images):
        strip.paste(im, (i * PREVIEW_W, 0))
    tmp = tempfile.NamedTemporaryFile(suffix="_preview.jpg", delete=False)
    strip.save(tmp.name, "JPEG", quality=82)
    tmp.close()
    return _register_tmp(tmp.name)


# ---------------------------------------------------------------------------
# Publora
# ---------------------------------------------------------------------------

PUBLORA_BASE = "https://api.publora.com/api/v1"


def publora_get_platform_id() -> str:
    headers = {"x-publora-key": PUBLORA_API_KEY}

    def _get():
        resp = httpx.get(f"{PUBLORA_BASE}/platform-connections", headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()

    data = _with_retry(_get)
    for conn in data.get("connections", []):
        pid = conn.get("platformId", "")
        if pid.startswith("instagram-"):
            return pid
    raise RuntimeError("No connected Instagram account found in Publora.")


def publora_post(
    caption: str,
    hashtags: list,
    local_paths: list[str],
    media_type: str,
    schedule_at: datetime | None = None,
) -> dict:
    """Post to Instagram via Publora (draft -> upload -> schedule)."""
    headers = {"x-publora-key": PUBLORA_API_KEY, "Content-Type": "application/json"}
    is_video = media_type in ("reel", "animated")
    mime     = "video/mp4" if is_video else "image/jpeg"
    ext      = "mp4"       if is_video else "jpg"
    fal_type = "video"     if is_video else "image"

    log.info("Fetching Publora platform ID...")
    platform_id = publora_get_platform_id()
    log.info("Platform: %s", platform_id)

    full_caption = caption
    if hashtags:
        full_caption += "\n\n" + " ".join(f"#{h}" for h in hashtags)

    log.info("Creating Publora draft post...")
    post_resp = httpx.post(
        f"{PUBLORA_BASE}/create-post",
        headers=headers,
        json={"content": full_caption, "platforms": [platform_id]},
        timeout=30,
    )
    post_resp.raise_for_status()
    post_group_id = post_resp.json()["postGroupId"]
    log.info("Draft created: %s", post_group_id)

    for i, local_path in enumerate(local_paths, 1):
        filename = f"oralcheck_{int(time.time())}_{i}.{ext}"
        log.info("Getting upload URL for file %d/%d...", i, len(local_paths))
        url_resp = httpx.post(
            f"{PUBLORA_BASE}/get-upload-url",
            headers=headers,
            json={
                "fileName": filename,
                "contentType": mime,
                "postGroupId": post_group_id,
                "type": fal_type,
            },
            timeout=30,
        )
        url_resp.raise_for_status()
        upload_url = url_resp.json()["uploadUrl"]

        log.info("Uploading file %d/%d...", i, len(local_paths))
        with open(local_path, "rb") as f:
            put_resp = httpx.put(
                upload_url,
                content=f.read(),
                headers={"Content-Type": mime},
                timeout=180,
            )
        put_resp.raise_for_status()

    if schedule_at is None:
        schedule_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    scheduled_time = schedule_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    log.info("Scheduling post for %s...", scheduled_time)
    schedule_resp = httpx.put(
        f"{PUBLORA_BASE}/update-post/{post_group_id}",
        headers=headers,
        json={"status": "scheduled", "scheduledTime": scheduled_time},
        timeout=30,
    )
    schedule_resp.raise_for_status()
    log.info("Post scheduled. Post group ID: %s", post_group_id)
    return {"postGroupId": post_group_id}


# ---------------------------------------------------------------------------
# Queue system
# ---------------------------------------------------------------------------

def save_to_queue(
    content: dict,
    media_type: str,
    pillar: str | None,
    file_paths: list[str],
) -> dict:
    """Copy generated files into queue/ and write a manifest. Returns manifest dict."""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    short_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    item_dir = QUEUE_DIR / f"{timestamp}_{short_id}"
    item_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for i, src in enumerate(file_paths):
        suffix = Path(src).suffix
        if media_type in ("reel", "animated"):
            dst_name = f"reel{suffix}"
        elif len(file_paths) == 1:
            dst_name = f"image{suffix}"
        else:
            dst_name = f"slide_{i+1:02d}{suffix}"
        shutil.copy2(src, item_dir / dst_name)
        saved_files.append(dst_name)

    if media_type == "carousel" and len(file_paths) > 1:
        preview_path = stitch_carousel_preview(file_paths)
        shutil.copy2(preview_path, item_dir / "preview.jpg")
        saved_files.append("preview.jpg")

    manifest = {
        "id": f"{timestamp}_{short_id}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pillar": pillar,
        "media_type": media_type,
        "hook": content.get("hook", ""),
        "caption": content.get("caption", ""),
        "hashtags": content.get("hashtags", []),
        "search_query": content.get("search_query", ""),
        "visual_prompt": content.get("visual_prompt", ""),
        "slides": content.get("slides", []),
        "files": saved_files,
        "status": "pending",
    }

    with open(item_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    log.info("Saved to queue: %s", item_dir.name)
    return manifest


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    brief: str,
    media_type: str,
    pillar: str | None = None,
) -> dict | None:
    """Generate content, create media, and save to queue for review."""
    log.info("Generating content...")
    content = generate_content(brief, media_type)
    log.info("Hook: %s", content["hook"])

    if media_type == "infographic":
        log.info("Rendering infographic...")
        if _USE_HTML_RENDER:
            file_paths = [_html_render.infographic_image(content)]
        else:
            file_paths = [render_infographic_image(content)]
    elif media_type == "animated":
        log.info("Rendering Manim animated reel...")
        reel_path = render_manim_reel(content)
        file_paths = [reel_path]
    elif media_type == "carousel":
        file_paths = generate_carousel_slides(content)
    elif media_type == "image":
        log.info("Fetching stock photo (query: %s)...", content["search_query"])
        raw_path = fetch_stock_photo(content["search_query"])
        if _USE_HTML_RENDER:
            composited = _html_render.image_overlay(raw_path, content["hook"])
        else:
            composited = add_text_overlay(raw_path, content["hook"])
        file_paths = [composited]
    else:  # reel
        log.info("Fetching stock video (query: %s)...", content["search_query"])
        raw_path = fetch_stock_video(content["search_query"])
        composited = add_animated_text_overlay_video(raw_path, content["hook"])
        file_paths = [composited]

    manifest = save_to_queue(content, media_type, pillar, file_paths)
    log.info("Queued: %s -- open http://localhost:8765 to review.", manifest["id"])
    return manifest


# ---------------------------------------------------------------------------
# World-map mode (Google Analytics -> map image -> queue)
# ---------------------------------------------------------------------------

def fetch_ga_countries(property_id: str, key_path: str, days: int = 90) -> dict[str, int]:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

    if key_path:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(
            key_path,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        client = BetaAnalyticsDataClient(credentials=creds)
    else:
        import google.auth
        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        client = BetaAnalyticsDataClient(credentials=creds)

    req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")],
        limit=200,
    )
    resp = client.run_report(req)
    data = {}
    for row in resp.rows:
        name = row.dimension_values[0].value
        count = int(row.metric_values[0].value)
        if name and name != "(not set)" and count > 0:
            data[name] = count
    return dict(sorted(data.items(), key=lambda x: x[1], reverse=True))


def _country_name_to_iso3(name: str) -> str | None:
    import pycountry
    try:
        c = pycountry.countries.lookup(name)
        return c.alpha_3
    except LookupError:
        pass
    _OVERRIDES = {
        "South Korea": "KOR", "North Korea": "PRK", "Russia": "RUS",
        "Taiwan": "TWN", "Hong Kong": "HKG", "Macau": "MAC",
        "Bolivia": "BOL", "Venezuela": "VEN", "Syria": "SYR",
        "Laos": "LAO", "Moldova": "MDA", "Tanzania": "TZA",
        "Ivory Coast": "CIV", "Democratic Republic of the Congo": "COD",
        "Republic of the Congo": "COG", "Myanmar (Burma)": "MMR",
        "Trinidad & Tobago": "TTO", "Sint Maarten": "SXM",
        "Eswatini": "SWZ", "Timor-Leste": "TLS", "Kosovo": "XKX",
        "United States": "USA", "United Kingdom": "GBR",
    }
    return _OVERRIDES.get(name)


def generate_map_image(country_data: dict[str, int]) -> tuple[str, int, int]:
    import io
    import plotly.graph_objects as go
    import plotly.io as pio

    locations, z_vals = [], []
    for name, count in country_data.items():
        iso3 = _country_name_to_iso3(name)
        if iso3:
            locations.append(iso3)
            z_vals.append(count)

    n_countries = len(locations)
    total_users = sum(country_data.values())
    log.info("Mapping %d countries, %d total users", n_countries, total_users)

    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=["AFG"], z=[0], showscale=False,
        colorscale=[[0, "#1c1c1a"], [1, "#1c1c1a"]],
        marker_line_color="#2a2a28", marker_line_width=0.6, geo="geo",
    ))
    if locations:
        fig.add_trace(go.Choropleth(
            locations=locations, z=z_vals,
            colorscale=[
                [0.0, "#0a4447"], [0.25, "#0d7377"],
                [0.65, "#14a8ae"], [1.0, "#e8634a"],
            ],
            zmin=1, zmax=max(z_vals), showscale=False,
            marker_line_color="#0d7377", marker_line_width=0.8, geo="geo",
        ))

    fig.update_layout(
        paper_bgcolor="#111110", plot_bgcolor="#111110",
        width=1080, height=1080,
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            bgcolor="#111110", showland=True, landcolor="#1c1c1a",
            showocean=True, oceancolor="#0a0a09", showcountries=True,
            countrycolor="#2a2a28", showcoastlines=False, showframe=False,
            projection_type="natural earth", lataxis_range=[-60, 85],
        ),
    )

    raw_bytes = pio.to_image(fig, format="png", width=1080, height=1080, scale=2)
    base = Image.open(io.BytesIO(raw_bytes)).resize((1080, 1080), Image.LANCZOS)
    draw = ImageDraw.Draw(base)
    W, H = 1080, 1080
    pad = 58

    def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
        p = Path(__file__).parent / "fonts" / name
        try:
            return ImageFont.truetype(str(p), size)
        except Exception:
            return ImageFont.load_default(size=size)

    serif_lg = _font("DMSerifDisplay-Regular.ttf", 72)
    serif_sm = _font("DMSerifDisplay-Regular.ttf", 34)
    sans_reg = _font("SourceSans3-Regular.ttf", 26)

    panel_h = 220
    overlay = Image.new("RGBA", (W, panel_h), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for y in range(panel_h):
        alpha = int(210 * (y / panel_h) ** 0.6)
        ov_draw.rectangle([(0, y), (W, y + 1)], fill=(17, 17, 16, alpha))
    crop = base.crop((0, H - panel_h, W, H)).convert("RGBA")
    composited = Image.alpha_composite(crop, overlay).convert("RGB")
    base.paste(composited, (0, H - panel_h))

    draw.text((pad, pad), "OralCheck", font=serif_sm, fill="#0d7377")
    draw.text((pad, H - panel_h + 28), f"{n_countries} countries", font=serif_lg, fill="#e6e2dc")
    draw.text((pad, H - 52), f"{total_users:,} users \xb7 past 90 days \xb7 oralcheck.org", font=sans_reg, fill="#8a8680")
    draw.ellipse([(pad - 18, pad + 6), (pad - 6, pad + 18)], fill="#e8634a")

    out = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    _register_tmp(out.name)
    base.save(out.name, "PNG")
    log.info("Map image saved -> %s", out.name)
    return out.name, n_countries, total_users


def generate_map_caption(country_data: dict[str, int], n_countries: int, total_users: int) -> dict:
    top5 = list(country_data.items())[:5]
    top_str = ", ".join(f"{c} ({n:,})" for c, n in top5)

    prompt = (
        f"You write content for OralCheck (oralcheck.org), a free private oral cancer risk screener.\n\n"
        f"Data: {total_users:,} users across {n_countries} countries in the past 90 days.\n"
        f"Top countries: {top_str}\n\n"
        "Write an Instagram caption for a world-map post showing global reach.\n"
        "Tone: calm, grounded, evidence-based. No em dashes. No exclamation points.\n"
        "Structure:\n"
        "  - 1-2 sentence hook that makes the global reach feel meaningful\n"
        "  - 2-3 sentences about why this matters\n"
        "  - Quiet CTA: share the link or take the screener\n"
        "  - Exactly 5 hashtags\n\n"
        'Output JSON only: {"hook": "...", "caption": "...", "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"]}'
    )

    def _call():
        resp = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY).messages.create(
            model=CONTENT_MODEL,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:-1])
        return json.loads(text)

    return _with_retry(_call)


def run_map_pipeline(days: int = 90) -> None:
    ga_key  = os.environ.get("GA_SERVICE_ACCOUNT_KEY_PATH", "").strip()
    ga_prop = os.environ.get("GA_PROPERTY_ID", "").strip()
    if not ga_prop:
        log.error("Set GA_PROPERTY_ID in .env to use --map.")
        sys.exit(1)
    if not ga_key:
        log.info("GA_SERVICE_ACCOUNT_KEY_PATH not set -- using Application Default Credentials.")

    log.info("Fetching GA country data (past %d days)...", days)
    country_data = fetch_ga_countries(ga_prop, ga_key, days)
    if not country_data:
        log.error("No country data returned from GA.")
        sys.exit(1)

    log.info("Generating map image...")
    map_path, n_countries, total_users = generate_map_image(country_data)

    log.info("Generating caption with Claude...")
    content = generate_map_caption(country_data, n_countries, total_users)
    content["visual_prompt"] = ""
    content.setdefault("slides", [])

    manifest = save_to_queue(content, "image", "map", [map_path])
    log.info("Map post queued: %s", manifest["id"])
    log.info("Open http://localhost:8765 to review and approve.")


# ---------------------------------------------------------------------------
# Idea suggestion + weekly planning
# ---------------------------------------------------------------------------

def _tg_send_message(text: str) -> bool:
    """Send a Markdown message to the review Telegram chat. Non-fatal if unset."""
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    cid = os.environ.get("TELEGRAM_CHAT_ID")
    if not (tok and cid):
        return False
    try:
        httpx.post(
            f"https://api.telegram.org/bot{tok}/sendMessage",
            json={"chat_id": cid, "text": text, "parse_mode": "Markdown"},
            timeout=30,
        )
        return True
    except Exception as exc:
        log.warning("Telegram idea send failed: %s", exc)
        return False


def _ideas_telegram_text(batch: list[dict]) -> str:
    upcoming = content_calendar.upcoming(within_days=30)
    lines = ["*OralCheck content ideas*  (web-researched, none repeat past posts)"]
    if upcoming:
        lines.append(f"_Upcoming: {upcoming[0]['name']} in {upcoming[0]['days_until']} days_")
    lines.append("")
    for n, idea in enumerate(batch, 1):
        lines.append(f"*{n}.*  _{idea['media_type']} · {idea['pillar'].replace('_', ' ')}_")
        lines.append(idea["title"])
        lines.append("")
    lines.append("Reply with the numbers you want, e.g.  *1, 3, 8*")
    return "\n".join(lines)


def tg_wait_for_reply(timeout: int = 7200) -> str | None:
    """Long-poll Telegram for the next text message from the review chat."""
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    cid = os.environ.get("TELEGRAM_CHAT_ID")
    if not (tok and cid):
        return None
    base = f"https://api.telegram.org/bot{tok}"
    # Skip stale updates
    last = None
    stale = httpx.get(f"{base}/getUpdates", params={"offset": -1, "limit": 1}, timeout=10).json().get("result", [])
    if stale:
        last = stale[-1]["update_id"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        params = {"timeout": 30, "allowed_updates": '["message"]'}
        if last is not None:
            params["offset"] = last + 1
        try:
            resp = httpx.get(f"{base}/getUpdates", params=params, timeout=35)
            resp.raise_for_status()
        except Exception as exc:
            log.warning("Poll error: %s", exc)
            time.sleep(5)
            continue
        for update in resp.json().get("result", []):
            last = update["update_id"]
            msg = update.get("message", {})
            if str(msg.get("chat", {}).get("id")) == str(cid) and msg.get("text"):
                return msg["text"]
    return None


def _print_ideas(batch: list[dict]) -> None:
    upcoming = content_calendar.upcoming(within_days=30)
    if upcoming:
        near = upcoming[0]
        print(f"\n  Upcoming: {near['name']} in {near['days_until']} days\n")
    else:
        print()
    for n, idea in enumerate(batch, 1):
        tag = f"{idea['media_type']} · {idea['pillar']}"
        print(f"  {n:>2}. [{tag}]")
        print(f"      {idea['title']}")
    print(f"\n  Pick with:  python oralcheck_agent.py --pick \"1,3,5\"")
    print(f"  (regenerate with --ideas to get a fresh batch)\n")


def run_ideas(count: int) -> None:
    """Generate a numbered batch of fresh ideas and record them as suggested."""
    ledger = ideas.load_ledger()
    upcoming = content_calendar.upcoming(within_days=30)
    log.info("Generating %d ideas (avoiding %d used/recent)...",
             count, len(ideas._avoid_titles(ledger)))
    fresh = ideas.generate_ideas(
        count, api_key=ANTHROPIC_API_KEY, model=CONTENT_MODEL,
        system_prompt=SYSTEM_PROMPT, pillar_briefs=PILLAR_BRIEFS,
        calendar_events=upcoming, ledger=ledger,
    )
    if not fresh:
        print("No fresh ideas produced (they may all overlap with used ideas). Try again.")
        return
    ledger = ideas.record_suggested(ledger, fresh)
    ideas.save_ledger(ledger)
    batch = ideas.get_last_batch(ledger)
    _print_ideas(batch)
    if _tg_send_message(_ideas_telegram_text(batch)):
        log.info("Idea list sent to Telegram for review.")


def _queue_idea(idea: dict) -> dict | None:
    brief = (f"Content pillar: {idea['pillar'].replace('_', ' ').title()}\n"
             f"{idea['brief']}")
    if idea.get("calendar_ref"):
        brief += f"\n(Tied to awareness date: {idea['calendar_ref']})"
    return run_pipeline(brief, idea["media_type"], pillar=idea["pillar"])


def run_pick(numbers: list[int]) -> None:
    """Turn selected idea numbers into queued posts for Telegram/web review."""
    ledger = ideas.load_ledger()
    chosen = ideas.select(ledger, numbers)
    if not chosen:
        print("No matching ideas in the last batch. Run --ideas first, then pick by number.")
        return
    ideas.save_ledger(ledger)  # persist 'selected' before the slow render work
    for idea in chosen:
        log.info("Generating post for idea: %s", idea["title"])
        try:
            manifest = _queue_idea(idea)
        except Exception as exc:
            log.error("Failed to generate '%s': %s", idea["title"], exc)
            continue
        if manifest:
            ideas.mark_queued(ledger, idea["id"], manifest["id"])
            ideas.save_ledger(ledger)
            print(f"  queued {manifest['id']}  ({idea['media_type']})  {idea['title']}")
    print("\n  Review at http://localhost:8765 or via the Telegram approval flow.")


def run_await_picks(timeout: int = 7200) -> None:
    """Wait for a Telegram reply naming idea numbers, then generate+queue those posts.

    This is the hands-off step: after --ideas sends the batch to Telegram, this
    listens for the reply (e.g. "1, 3, 8"), generates each picked post, and queues
    it. Run telegram_review.py afterward to review and post the queued batch.
    """
    ledger = ideas.load_ledger()
    batch = ideas.get_last_batch(ledger)
    if not batch:
        print("No idea batch to pick from. Run --ideas first.")
        return
    log.info("Waiting for your pick reply on Telegram (up to %dh)...", timeout // 3600)
    reply = tg_wait_for_reply(timeout)
    if not reply:
        _tg_send_message("No pick received in time. Send the ideas again when you're ready.")
        return
    nums = [int(x) for x in re.findall(r"\d+", reply)]
    chosen = ideas.select(ledger, nums)
    if not chosen:
        _tg_send_message("Couldn't read any valid numbers from that. Reply like `1, 3, 8`.")
        return
    ideas.save_ledger(ledger)
    _tg_send_message(f"Got it, generating {len(chosen)} post(s) now. They'll come back for approval.")
    for idea in chosen:
        log.info("Generating post for idea: %s", idea["title"])
        try:
            manifest = _queue_idea(idea)
        except Exception as exc:
            log.error("Failed to generate '%s': %s", idea["title"], exc)
            continue
        if manifest:
            ideas.mark_queued(ledger, idea["id"], manifest["id"])
            ideas.save_ledger(ledger)
    print("Picks generated and queued. Run telegram_review.py to review and post them.")


def run_plan_week(count: int) -> None:
    """Auto-plan a week: generate a balanced batch and queue all of it for review."""
    ledger = ideas.load_ledger()
    upcoming = content_calendar.upcoming(within_days=14)
    log.info("Planning a week of %d posts...", count)
    fresh = ideas.generate_ideas(
        count, api_key=ANTHROPIC_API_KEY, model=CONTENT_MODEL,
        system_prompt=SYSTEM_PROMPT, pillar_briefs=PILLAR_BRIEFS,
        calendar_events=upcoming, ledger=ledger,
    )
    if not fresh:
        print("No fresh ideas produced for the week. Try again later.")
        return
    ledger = ideas.record_suggested(ledger, fresh)
    ideas.save_ledger(ledger)
    batch = ideas.get_last_batch(ledger)
    print(f"\n  Weekly plan ({len(batch)} posts):")
    for idea in batch:
        print(f"    - [{idea['media_type']} · {idea['pillar']}] {idea['title']}")
    print()
    for idea in batch:
        log.info("Generating: %s", idea["title"])
        try:
            manifest = _queue_idea(idea)
        except Exception as exc:
            log.error("Failed '%s': %s", idea["title"], exc)
            continue
        if manifest:
            ideas.mark_queued(ledger, idea["id"], manifest["id"])
            ideas.save_ledger(ledger)
            print(f"  queued {manifest['id']}  ({idea['media_type']})  {idea['title']}")
    print("\n  Review the whole batch at http://localhost:8765 or via Telegram.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="OralCheck content pipeline -- generates and queues posts for review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python oralcheck_agent.py --auto\n"
            "  python oralcheck_agent.py --auto --media-type carousel\n"
            "  python oralcheck_agent.py --auto --media-type reel\n"
            "  python oralcheck_agent.py --auto --media-type animated\n"
            '  python oralcheck_agent.py --directed "HPV awareness for parents"\n'
            "  python oralcheck_agent.py --map\n"
            "\n"
            "Idea workflow (suggest, then pick what you like):\n"
            "  python oralcheck_agent.py --ideas 8\n"
            '  python oralcheck_agent.py --pick "1,3,5"\n'
            "  python oralcheck_agent.py --plan-week 3\n"
            "\n"
            "Then start the review server:\n"
            "  python review_server.py\n"
            "  http://localhost:8765\n"
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--auto", action="store_true", help="Auto-pick next content pillar")
    mode.add_argument("--directed", metavar="BRIEF", help="Provide a specific content brief")
    mode.add_argument("--map", action="store_true", help="Generate world map post from Google Analytics data")
    mode.add_argument("--ideas", type=int, metavar="N", nargs="?", const=8,
                      help="Suggest N numbered content ideas (default 8) to pick from")
    mode.add_argument("--pick", metavar="NUMS",
                      help="Generate posts from picked idea numbers, e.g. \"1,3,5\"")
    mode.add_argument("--await-picks", action="store_true",
                      help="Wait for a Telegram reply with idea numbers, then generate those posts")
    mode.add_argument("--plan-week", type=int, metavar="N", nargs="?", const=3,
                      help="Auto-plan and queue a week of N posts (default 3) for batch review")
    parser.add_argument(
        "--media-type",
        choices=["reel", "image", "carousel", "animated", "infographic"],
        default="image",
        help="Type of media to generate (default: image)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Days of GA history for --map mode (default: 90)",
    )
    args = parser.parse_args()

    if args.ideas is not None:
        run_ideas(args.ideas)
    elif args.pick:
        try:
            nums = [int(x) for x in re.split(r"[,\s]+", args.pick.strip()) if x]
        except ValueError:
            parser.error('--pick expects numbers like "1,3,5"')
        run_pick(nums)
    elif args.await_picks:
        run_await_picks()
    elif args.plan_week is not None:
        run_plan_week(args.plan_week)
    elif args.map:
        run_map_pipeline(days=args.days)
    elif args.auto:
        state = load_pillar_state()
        pillar = pick_next_pillar(state)
        log.info("Selected pillar: %s", pillar.replace("_", " ").title())
        brief = f"Content pillar: {pillar.replace('_', ' ').title()}\n{PILLAR_BRIEFS[pillar]}"
        manifest = run_pipeline(brief, args.media_type, pillar=pillar)
        if manifest:
            save_pillar_state(record_pillar_used(state, pillar))
    else:
        run_pipeline(args.directed, args.media_type)


if __name__ == "__main__":
    main()
