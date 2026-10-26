"""
2D reels: the two illustrated plates, with narration.

Replaces reel3d.py (26 Oct 2026). Ian found the 3D model uncanny ("it lacks
depth, realism, and is uncanny"), and the review in docs/model-review chose
drawn plates instead: plate A, the open mouth from the front, and plate B, the
head in section from the side. Both are built by illustration/build_all.py
from the same atlas the 3D model used, and copied here as plate_a.svg and
plate_b.svg.

The plan format is reel3d's, so engine.py and the calendar did not change
shape: a list of shots, each one spoken sentence and a focus.

    {"shots": [
        {"say": "Oral cancer most often starts in places you rarely look.", "focus": "overview"},
        {"say": "The sides of the tongue come first.", "focus": "tongue",
         "label": {"k": "Most common site", "t": "Sides of the tongue", "d": "Stick it out, look left, then right."}},
        ...]}

Every focus picks a plate, a framing and what turns teal (FOCI). Unlike the 3D
model, the plates can also show a sign: a line that says "a white patch" or
"a sore that does not heal" brings up the drawing of it at that site
(LESIONS), and the on-screen footer says it is an illustration, not a real
case. reel2d/scene.html does the drawing; this module does the voice, timing,
sound and assembly, reusing reel3d's sound and reel2's voice and mix.
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

import align
import reel2
import reel3d

log = logging.getLogger("oralcheck.reel2d")

HERE = Path(__file__).parent / "reel2d"
W, H, FPS = 1080, 1920, 30
STAGE = (230, 1000)   # the plate's band on a reel frame: top, height
CREDIT = ("Illustration based on Z-Anatomy (CC BY-SA 4.0) and BodyParts3D (CC BY-SA 2.1 JP). "
          "Shared under CC BY-SA 4.0.")
FOOT = "Illustration for education, not a real case. Not reviewed by a clinician."
MIN_SHOT = 3.4
CTA_HOLD = 2.2

# plate, framing [centre x, centre y, width] at shot start and end (plate
# units), what turns teal, where the label points, and the eyebrow line.
# Plate A is 1000 x 1000, plate B 1000 x 1100; the anchors are the plates'
# own lab-* points.
FOCI = {
    "overview": dict(plate="a", box=[[500, 545, 1080], [500, 545, 1030]], hi=[], anchor=None, view="Mouth · open, from the front"),
    "tongue":   dict(plate="a", box=[[450, 610, 700], [430, 620, 620]], hi=["tongue"], anchor=[368, 640], view="Tongue · sides"),
    "cheek":    dict(plate="a", box=[[330, 590, 680], [300, 600, 580]], hi=["cheeks"], anchor=[215, 560], view="Inside of the cheek"),
    "gums":     dict(plate="a", box=[[460, 760, 720], [430, 770, 640]], hi=["gumUp", "gumLo"], anchor=[232, 800], view="Gums"),
    "lips":     dict(plate="a", box=[[540, 760, 860], [560, 790, 760]], hi=["lips"], anchor=[760, 920], view="Lips"),
    "tonsil":   dict(plate="a", box=[[440, 490, 660], [410, 480, 560]], hi=["tonsils"], anchor=[344, 480], view="Tonsils"),
    "throat":   dict(plate="a", box=[[500, 470, 700], [500, 450, 600]], hi=["wall", "softpalate", "uvula", "tonsils"],
                     anchor=[548, 432], view="Back of the mouth"),
    "teeth":    dict(plate="a", box=[[500, 600, 900], [500, 620, 820]], hi=["teeth"], anchor=[530, 800], view="Teeth"),
    "floor":    dict(plate="b", box=[[700, 650, 600], [720, 665, 500]], hi=["zone-floor"], anchor=[762, 676], view="Floor of the mouth · side section"),
    "base":     dict(plate="b", box=[[660, 670, 600], [640, 680, 500]], hi=["zone-base"], anchor=[600, 718], view="Base of the tongue · side section"),
    "oropharynx": dict(plate="b", box=[[640, 660, 620], [620, 670, 540]], hi=["zone-base", "zone-tonsil", "zone-soft"],
                       anchor=[578, 676], view="Back of the throat · side section"),
    "palate":   dict(plate="b", box=[[700, 610, 600], [710, 620, 500]], hi=["hardpalate"], anchor=[720, 590], view="Roof of the mouth · side section"),
    "nodes":    dict(plate="b", box=[[640, 740, 760], [650, 760, 660]], hi=[], anchor=[690, 800], view="Neck · under the jaw"),
    "cta":      dict(plate="a", box=[[500, 545, 1030], [500, 545, 1100]], hi=[], anchor=None, view=""),
}
# Salivary glands sit under the jaw too; not drawn, so the label points at the place.
FOCI["glands"] = dict(FOCI["nodes"], view="Salivary glands · under the jaw")

# What a spoken line names decides what lights up. Order matters: "the floor
# of the mouth, under the tongue" is the floor, "base of the tongue" is not the
# tongue, and "soft palate" is the throat, not the roof of the mouth.
NAMES = [
    ("floor", r"floor of (?:the|your) mouth|under(?:side of)? (?:the|your) tongue"),
    ("base", r"(?:base|back) of (?:the|your) tongue"),
    ("tonsil", r"tonsil"),
    ("throat", r"\bthroat|soft palate|uvula|back of (?:the|your) mouth|oropharyn"),
    ("palate", r"roof of (?:the|your) mouth|hard palate|\bpalate\b"),
    ("cheek", r"\bcheeks?\b|buccal"),
    ("lips", r"\blips?\b"),
    ("tongue", r"\btongue"),
    ("nodes", r"\bneck\b|lymph node|under (?:the|your) jaw|jaw ?line"),
    ("glands", r"saliva|salivary|\bglands?\b"),
    ("gums", r"\bgum(?:s|line| line)?\b|gingiva"),
    ("teeth", r"\bteeth\b|\btooth\b"),
]

# Signs the plates can show, by the words that name them. "Won't wipe away" is
# a white patch; "wipes away" is thrush.
KINDS = [
    ("thrush", r"thrush|candid|(?<!n't )(?<!not )\bwipes? (?:off|away)|\bcan be wiped"),
    ("lichen", r"lichen|lacy|lace-like"),
    ("speckled", r"speckled|red[- ]and[- ]white|mixed red|erythroleuko"),
    ("white", r"white patch|leukoplak|\bwhite\b"),
    ("red", r"red patch|erythroplak|\bred\b|redness"),
    ("ulcer", r"\bsores?\b|ulcer"),
    # A patch of no stated colour is drawn as the commoner white one (6 Nov
    # reel: "the same painless patches" showed nothing, Ian 26 Oct).
    ("white", r"\bpatch(?:es)?\b"),
    ("lump", r"\blumps?\b|swelling"),
]
# Where each drawing is, by focus and kind, and the point a label marks.
LESION_AT = {
    "tongue": {"white": "white", "red": "red", "ulcer": "ulcer", "thrush": "thrush"},
    "cheek": {"speckled": "speckled", "lichen": "lichen", "white": "whitecheek", "red": "redcheek"},
    "tonsil": {"lump": "lump"}, "throat": {"lump": "lump"},
    "lips": {"ulcer": "lip"},
    "gums": {"white": "whitegum"},
    "floor": {"lump": "floor"}, "base": {"lump": "base"},
}
LESIONS = {"white": [386, 640], "red": [640, 572], "ulcer": [608, 694], "thrush": [470, 610], "speckled": [214, 600],
           "lichen": [214, 495], "whitecheek": [220, 600], "redcheek": [220, 600], "whitegum": [562, 877], "lump": [340, 482], "lip": [640, 934], "floor": [756, 683], "base": [588, 712]}
# A line that names a sign but no place shows it where it is drawn.
KIND_HOME = {"white": "tongue", "red": "tongue", "ulcer": "tongue", "thrush": "tongue",
             "speckled": "cheek", "lichen": "cheek", "lump": "tonsil"}


def named_foci(say: str) -> list[str]:
    """Foci a line names, in the order it names them."""
    low, hits = say.lower(), []
    for focus, pat in NAMES:
        m = re.search(pat, low)
        if m:
            hits.append((m.start(), focus))
            low = low[:m.start()] + " " * (m.end() - m.start()) + low[m.end():]
    return [f for _, f in sorted(hits)]


def lesion_kind(say: str) -> str | None:
    low = say.lower()
    for kind, pat in KINDS:
        if re.search(pat, low):
            return kind
    return None


def match_focus(say: str, focus: str, home: str | None = None) -> str:
    """The focus a shot should have, given what its line says."""
    if focus == "cta":
        return focus
    named = named_foci(say)
    if named:
        return focus if focus in named else named[0]
    # A line that names nothing ("redness or a patch") shows the topic's own
    # place, or the whole mouth: never a place the writer picked that the voice
    # does not say (the 6 Nov reel lit the lips on "if a patch is still there").
    return home if home in FOCI else "overview"


def lesion_for(say: str, focus: str) -> tuple[str, str | None]:
    """(focus, lesion): the drawing a line calls for, at the site it is about.

    A sign is only drawn where the line puts it. A line naming no place moves
    from the whole-mouth view to where the sign is drawn; one already on a
    place with no drawing of that sign shows the place alone, never the sign
    somewhere else.
    """
    kind = lesion_kind(say)
    if not kind:
        return focus, None
    if focus == "overview" and not named_foci(say) and kind in KIND_HOME:
        focus = KIND_HOME[kind]
    return focus, LESION_AT.get(focus, {}).get(kind)


# Places a caption may name only if a shot shows them. "Throat" is any of the
# back-of-mouth foci.
SHOWN_AS = {"throat": {"throat", "tonsil", "base"}, "tonsil": {"tonsil", "throat"}}


def unshown_places(caption: str, shots: list[dict]) -> list[str]:
    """Places the caption names that no shot shows (27 Oct reel: "promised six, showed three")."""
    shown = {s.get("focus") for s in shots}
    return [f for f in named_foci(caption) if f not in ("teeth", "nodes", "glands")
            and not (SHOWN_AS.get(f, {f}) & shown)]


def validate(plan: dict) -> dict:
    """Match each shot's focus and sign to its words, end on the end card."""
    shots, home = [], plan.get("home")
    for s in plan.get("shots", []):
        if not isinstance(s, dict) or not str(s.get("say", "")).strip():
            continue
        say = str(s["say"]).strip()
        f = match_focus(say, s.get("focus") if s.get("focus") in FOCI else "overview", home)
        f, lesion = lesion_for(say, f)
        if f != s.get("focus"):
            log.info("Shot refocused %s -> %s: %s", s.get("focus"), f, say)
        label = s.get("label") if isinstance(s.get("label"), dict) and FOCI[f]["anchor"] and f == s.get("focus") else None
        shots.append({"say": say, "focus": f, "label": label, "lesion": lesion})
    shots = [s for s in shots if s["focus"] != "cta"]
    shots.append({"say": "Check your own risk, free, at oralcheck.org.", "focus": "cta", "label": None, "lesion": None})
    return {"shots": shots}


def _shot(focus: str, lesion: str | None = None) -> dict:
    f = FOCI[focus if focus in FOCI else "overview"]
    box = f["box"]
    if lesion:   # frame the sign, not just the place: centres move partway towards it
        x, y = LESIONS[lesion]
        bottom = {"a": 1000, "b": 1100}[f["plate"]] + 20   # never slide past the plate's lower edge
        box = [[c[0] + 0.45 * (x - c[0]), min(c[1] + 0.45 * (y - c[1]), bottom - c[2] * STAGE[1] / W / 2), c[2]] for c in box]
    return {"plate": f["plate"], "box": box, "hi": [] if lesion else f["hi"], "lesion": lesion,
            "anchor": LESIONS[lesion] if lesion else f["anchor"]}


def _scoped(svg: str, p: str) -> str:
    """Prefix every id in an inline SVG, so two plates can share a page."""
    svg = re.sub(r'id="([^"]+)"', lambda m: f'id="{p}{m.group(1)}"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{p}{m.group(1)})', svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{p}{m.group(1)}"', svg)
    return re.sub(r'<svg ([^>]*?)width="\d+" height="\d+"', r'<svg \1width="100%" height="100%" preserveAspectRatio="xMidYMid slice"',
                  svg, count=1)


def _page() -> str:
    plates = "".join(f'<div class="plate" id="P{p}">{_scoped((HERE / f"plate_{p}.svg").read_text(), p + "-")}</div>' for p in "ab")
    return (HERE / "scene.html").read_text().replace("<!--PLATES-->", plates)


def _serve(route):
    name = route.request.url.split("reel2d.local/", 1)[1].split("?")[0]
    if name == "scene.html":
        return route.fulfill(status=200, body=_page(), headers={"Content-Type": "text/html"})
    path = HERE / name if (HERE / name).exists() else reel3d.HERE / name   # fonts are shared with reel3d
    ctype = {".ttf": "font/ttf", ".js": "text/javascript"}.get(path.suffix, "application/octet-stream")
    route.fulfill(status=200, body=path.read_bytes(), headers={"Content-Type": ctype})


def _open(p, plan: dict, size: tuple[int, int], scale: float = 1):
    page = p.chromium.launch().new_page(viewport={"width": size[0], "height": size[1]}, device_scale_factor=scale)
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)[:300]))
    page.route("http://reel2d.local/**", _serve)
    page.add_init_script(f"window.PLAN = {json.dumps(plan)};")
    page.goto("http://reel2d.local/scene.html")
    try:
        page.wait_for_function("window.render && window.render(0)", timeout=60000)
    except Exception as exc:
        raise RuntimeError(f"2D scene never became ready ({exc}); page errors: {errors[:5]}") from None
    page.evaluate("async () => { await document.fonts.load('600 54px \"Source Sans 3\"'); "
                  "await document.fonts.load('50px \"DM Serif Display\"'); await document.fonts.ready; }")
    return page


def _render_frames(scene_plan: dict, total: float, out_mp4: str) -> None:
    from playwright.sync_api import sync_playwright

    n = int(round(total * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                           "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                           "-r", str(FPS), out_mp4], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        page = _open(p, scene_plan, (W, H))
        t0 = time.time()
        for i in range(n):
            page.evaluate(f"window.render({i / FPS})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=92, timeout=300000))
            if i % 150 == 0:
                log.info("2D frame %d/%d (%.0fs)", i, n, time.time() - t0)
        page.context.browser.close()
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg failed encoding the 2D frames")


def still(focus: str, out_path: str, *, label: dict | None = None, lesion: str | None = None,
          size: tuple[int, int] = (1080, 1000), box: list | None = None, scale: float = 2) -> str:
    """One frame of a plate for an image post or carousel slide, `size` pixels.

    The reel's framing, teal highlight and label, without the reel chrome.
    `lesion` shows that sign's drawing (a LESIONS key) and points the label at
    it; `box` overrides the framing ([centre x, centre y, width], plate units).
    """
    from playwright.sync_api import sync_playwright

    length = 4.0
    shot = {"t0": 0, "len": length, **_shot(focus, lesion), "view": "", "label": label, "tap": 0.55, "words": [], "step": ""}
    if box:
        shot["box"] = [box, box]
    plan = {"shots": [shot], "cta_t0": 999, "credit": "", "foot": "", "still": True, "stage": [0, size[1]]}
    with sync_playwright() as p:
        # Rendered at 2x: posts are laid out at 1080 and output at 1440, so a
        # 1x still was stretched and looked soft (Ian, 26 Oct: "quality is really low").
        page = _open(p, plan, size, scale)
        page.evaluate(f"window.render({length * 0.8})")
        page.screenshot(path=out_path, type="jpeg" if out_path.lower().endswith((".jpg", ".jpeg")) else "png")
        page.context.browser.close()
    return out_path


def build(plan: dict, out_path: str, *, tts, music: str | None = None, workdir: str | None = None) -> str:
    """Render a narrated 2D reel to out_path. `tts(text) -> wav path`."""
    source = plan.get("source")
    shots = validate(plan)["shots"]
    workdir = workdir or tempfile.mkdtemp(prefix="reel2d_")

    wavs = [tts(s["say"]) for s in shots]
    speech = [reel2._duration(w) / reel2.VOICE_TEMPO for w in wavs]
    pads = [reel2.GAP + (CTA_HOLD if s["focus"] == "cta" else max(0.0, MIN_SHOT - d)) for s, d in zip(shots, speech)]
    voice = reel2._voice_track(wavs, pads, workdir)

    t, windows, timing = 0.0, [], []
    for d, pad, s in zip(speech, pads, shots):
        windows.append((t, t + d, s["say"]))
        timing.append((t, d + pad))
        t += d + pad
    total = t
    words = align.align(voice, windows)

    n_story = sum(1 for s in shots if s["focus"] != "cta")
    scene_shots, events, k_story = [], [], 0
    for s, (t0, length), w in zip(shots, timing, words):
        if s["focus"] != "cta":
            k_story += 1
        scene_shots.append({
            "t0": round(t0, 3), "len": round(length, 3), **_shot(s["focus"], s["lesion"]),
            "view": FOCI[s["focus"]]["view"], "label": s["label"], "tap": 0.55, "words": w,
            "step": f"{k_story:02d} / {n_story:02d}" if s["focus"] != "cta" else "",
        })
        if t0 > 0:
            events.append(("glide", max(0.0, t0 - 0.15)))
        if s["label"]:
            events.append(("tap", t0 + 0.55))
        if s["focus"] == "cta":
            events.append(("settle", t0 + 0.1))
    credit = " · ".join(x for x in (source, CREDIT) if x)
    scene_plan = {"shots": scene_shots, "cta_t0": scene_shots[-1]["t0"], "credit": credit, "foot": FOOT}

    video = os.path.join(workdir, "video.mp4")
    _render_frames(scene_plan, total, video)
    audio = reel2._final_audio(voice, reel3d._sfx_track(events, total, workdir), music, total, workdir)
    reel2._run(["ffmpeg", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path])
    log.info("2D reel: %.1fs, %d shots -> %s", total, len(shots), out_path)
    return out_path
