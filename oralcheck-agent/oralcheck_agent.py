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

_REQUIRED_ENV = ["ANTHROPIC_API_KEY", "PUBLORA_API_KEY"]
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
PUBLORA_API_KEY     = os.environ["PUBLORA_API_KEY"]
PEXELS_API_KEY      = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

PILLARS_FILE = Path(__file__).parent / "pillars.json"
QUEUE_DIR    = Path(__file__).parent / "queue"

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
            "This is for an Instagram Carousel (4 slides total). "
            "Slide 1: real stock photo background (searched from Pexels/Unsplash). Slides 2-3: branded info slides. "
            "Slide 4: auto-generated CTA slide. Do NOT include slide 4 in your output.\n"
            "Output JSON with these exact fields:\n"
            "  hook: slide 1 headline text (10 words max, powerful stat or insight)\n"
            "  search_query: 3-6 word Pexels/Unsplash search query for slide 1 background (real people, human-focused)\n"
            "  slides: array of exactly 2 objects for slides 2-3, each with:\n"
            "    headline (6 words max, punchy)\n"
            "    body (20-30 words, one concrete supporting fact)\n"
            "  caption: Instagram caption\n"
            "  hashtags: exactly 5 lowercase tags\n"
            "Slides should tell a cohesive story: hook stat -> supporting context -> key insight -> (auto CTA)."
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
            model="claude-sonnet-4-6",
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

    # Bottom gradient: transparent -> off-white
    gradient = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    gradient_start = int(h * 0.45)
    for y in range(gradient_start, h):
        t = (y - gradient_start) / (h - gradient_start)
        alpha = int(215 * (t ** 0.7))
        grad_draw.line([(0, y), (w, y)], fill=(250, 249, 246, alpha))

    img = Image.alpha_composite(img, gradient)
    draw = ImageDraw.Draw(img)

    margin = int(w * 0.07)
    inner_w = w - 2 * margin

    hook_size = int(w * 0.065)
    hook_font = _load_font("DMSerifDisplay-Regular.ttf", hook_size)
    cta_size  = int(w * 0.038)
    cta_font  = _load_font("SourceSans3-Regular.ttf", cta_size)

    wrapped_hook = _wrap_text(hook, hook_font, inner_w)
    line_count = wrapped_hook.count("\n") + 1

    cta_y  = h - int(h * 0.055)
    hook_y = cta_y - (line_count * int(hook_size * 1.25)) - int(h * 0.025)
    bar_y  = hook_y - int(h * 0.022)

    draw.rectangle([(margin, bar_y), (margin + int(w * 0.08), bar_y + 4)], fill=C_TEAL)
    draw.text((margin, hook_y), wrapped_hook, font=hook_font, fill=C_DARK, spacing=int(hook_size * 0.2))
    draw.text((margin, cta_y), cta, font=cta_font, fill=C_TEAL)

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

    headline_font = _load_font("DMSerifDisplay-Regular.ttf", 58)
    body_font     = _load_font("SourceSans3-Regular.ttf", 30)
    mark_font     = _load_font("SourceSans3-Regular.ttf", 22)

    # Brand mark at top
    draw.ellipse([(pad - 14, pad), (pad, pad + 14)], fill=C_CORAL)
    draw.text((pad + 14, pad + 2), "OralCheck", font=mark_font, fill=C_TEAL_RGB)
    draw.rectangle([(pad, pad + 30), (pad + 64, pad + 34)], fill=C_TEAL_RGB)

    # Measure content block for vertical centering
    wrapped_headline = _wrap_text(headline, headline_font, inner_w)
    headline_lines = wrapped_headline.count("\n") + 1
    headline_h = headline_lines * 74

    wrapped_body = _wrap_text(body, body_font, inner_w)
    body_lines = wrapped_body.count("\n") + 1
    body_h = body_lines * 43

    content_h = headline_h + 36 + body_h
    content_y = max((H - content_h) // 2, 180)

    draw.text((pad, content_y), wrapped_headline, font=headline_font, fill=C_TEXT, spacing=16)
    draw.text((pad, content_y + headline_h + 36), wrapped_body, font=body_font, fill=C_MUTED, spacing=12)

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
    """Render a branded data infographic: bar chart comparison on dark brand background."""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)

    pad = 76

    brand_font    = _load_font("SourceSans3-Regular.ttf", 22)
    headline_font = _load_font("DMSerifDisplay-Regular.ttf", 56)
    num_font      = _load_font("DMSerifDisplay-Regular.ttf", 76)
    label_font    = _load_font("SourceSans3-Regular.ttf", 28)
    context_font  = _load_font("SourceSans3-Regular.ttf", 22)
    cta_font      = _load_font("SourceSans3-Regular.ttf", 22)

    # Brand mark
    draw.ellipse([(pad - 14, 58), (pad, 72)], fill=C_CORAL)
    draw.text((pad + 14, 58), "OralCheck", font=brand_font, fill=C_TEAL_RGB)

    # Thin teal separator under brand mark
    draw.rectangle([(pad, 92), (W - pad, 94)], fill=(22, 50, 52))

    # Headline
    headline = content.get("headline", "")
    wrapped_headline = _wrap_text(headline, headline_font, W - 2 * pad)
    draw.text((pad, 116), wrapped_headline, font=headline_font, fill=C_TEXT, spacing=14)
    headline_lines = wrapped_headline.count("\n") + 1
    after_headline_y = 116 + headline_lines * 70 + 12

    # Context label (what the bars measure)
    context = content.get("context", "")
    if context:
        draw.text((pad, after_headline_y), context.upper(), font=context_font, fill=C_MUTED, spacing=8)
        after_headline_y += 38

    bars = content.get("bars", [])
    n_bars = max(len(bars), 1)
    bar_colors = [C_CORAL, C_TEAL_RGB, C_MUTED]

    cta_reserve = 100
    label_h = 40
    fact_reserve = 50 if content.get("fact") else 0
    bar_gap_ratio = 0.8
    bar_w = W - 2 * pad
    track_color = (20, 40, 42)

    # Target bar height: fill available space generously
    available = H - after_headline_y - 28 - cta_reserve - fact_reserve
    raw_h = available / (n_bars + (n_bars - 1) * bar_gap_ratio + n_bars * label_h / 80)
    bar_h = min(max(int(raw_h), 70), 140)
    bar_gap = int(bar_h * bar_gap_ratio)

    # Center chart block vertically in remaining space
    total_chart_h = n_bars * bar_h + (n_bars - 1) * bar_gap + n_bars * label_h + fact_reserve
    remaining = H - cta_reserve - (after_headline_y + 28)
    v_offset = max(0, (remaining - total_chart_h) // 2)
    bar_start_y = after_headline_y + 28 + v_offset
    current_y = bar_start_y

    for idx, bar in enumerate(bars):
        value = bar.get("value", 0)
        label = bar.get("label", "")
        value_str = bar.get("value_str", f"{value}%")
        color = bar_colors[idx % len(bar_colors)]

        by = current_y

        # Track
        draw.rectangle([(pad, by), (pad + bar_w, by + bar_h)], fill=track_color)

        # Fill
        fill_w = max(int(bar_w * value / 100), 4)
        draw.rectangle([(pad, by), (pad + fill_w, by + bar_h)], fill=color)

        # Percentage number
        num_bbox = draw.textbbox((0, 0), value_str, font=num_font)
        num_w = num_bbox[2] - num_bbox[0]
        num_h = num_bbox[3] - num_bbox[1]
        num_y = by + (bar_h - num_h) // 2 - 2

        if fill_w > num_w + 24:
            num_x = pad + fill_w - num_w - 14
            draw.text((num_x, num_y), value_str, font=num_font, fill=C_BG)
        else:
            num_x = pad + fill_w + 14
            draw.text((num_x, num_y), value_str, font=num_font, fill=C_TEXT)

        # Label below bar
        draw.text((pad, by + bar_h + 10), label, font=label_font, fill=C_MUTED)

        current_y += bar_h + label_h + bar_gap

    # Fact / supporting text (positioned after last bar label)
    fact_y = current_y - bar_gap + 10
    fact = content.get("fact", "")
    if fact:
        wrapped_fact = _wrap_text(fact, context_font, W - 2 * pad)
        draw.text((pad, fact_y), wrapped_fact, font=context_font, fill=(70, 100, 102), spacing=8)

    # Bottom rule + CTA
    draw.rectangle([(pad, H - 72), (pad + 56, H - 68)], fill=C_TEAL_RGB)
    draw.text((pad, H - 56), "oralcheck.org", font=cta_font, fill=C_TEAL_RGB)

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
    Build the 4-slide carousel:
      Slide 1: AI background (flux-pro) + hook text overlay
      Slides 2-3: PIL-rendered brand info slides
      Slide 4: PIL-rendered CTA slide (auto)
    """
    paths = []

    log.info("Fetching stock photo for carousel slide 1 (query: %s)...", content["search_query"])
    raw_path = fetch_stock_photo(content["search_query"])
    hook_path = add_text_overlay(raw_path, content["hook"])
    paths.append(hook_path)

    for i, slide in enumerate(content.get("slides", []), 2):
        log.info("Rendering carousel slide %d (brand info)...", i)
        info_path = _render_info_slide(slide["headline"], slide["body"])
        paths.append(info_path)

    log.info("Rendering carousel slide %d (CTA)...", len(paths) + 1)
    cta_path = _render_cta_slide()
    paths.append(cta_path)

    return paths


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
            model="claude-sonnet-4-6",
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
            "Then start the review server:\n"
            "  python review_server.py\n"
            "  http://localhost:8765\n"
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--auto", action="store_true", help="Auto-pick next content pillar")
    mode.add_argument("--directed", metavar="BRIEF", help="Provide a specific content brief")
    mode.add_argument("--map", action="store_true", help="Generate world map post from Google Analytics data")
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

    if args.map:
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
