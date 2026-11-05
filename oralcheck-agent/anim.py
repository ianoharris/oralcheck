"""
Animated reels in the OralCheck house style (anim/STYLE.md).

A scene is a page in anim/ that draws the stage as a pure function of time;
anim/house.js draws everything around it (chrome, captions, labels, the
readout, the end card). This module voices a script, times each line, renders
the page frame by frame and mixes the sound, reusing the reel pipeline's
voice, word alignment, sound effects and music.

    python anim.py gauze out.mp4      # 2D sample: why the dentist grabs your tongue
    python anim.py zoom out.mp4       # 3D sample: from the face to the cells

A script is a list of lines: {"key", "say", "eyebrow"}; the scene keys its
motion to the keys. The closing call to action is added for you.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import align
import reel2
import reel2d
import reel3d

log = logging.getLogger("oralcheck.anim")

HERE = Path(__file__).parent / "anim"
W, H, FPS = 1080, 1920, 30
MIN_LINE = 3.0
CTA_HOLD = 2.2
PLATES = "Illustration based on Z-Anatomy (CC BY-SA 4.0) and BodyParts3D (CC BY-SA 2.1 JP). Shared under CC BY-SA 4.0."

SCRIPTS = {
    # NIDCR, "The Oral Cancer Exam" (NIH Pub. 20-5032), step 6; topics.py tongue_sides.
    "gauze": dict(
        lines=[
            {"key": "hook", "say": "Ever wonder why your dentist grabs your tongue with gauze?", "eyebrow": "The oral cancer exam"},
            {"key": "exam", "say": "It is one step of a routine oral cancer exam.", "eyebrow": "The oral cancer exam"},
            {"key": "pull", "say": "With the gauze, they gently pull it to one side, then the other.", "eyebrow": "Step 6 · gauze"},
            {"key": "why", "say": "The sides and underside of your tongue are the most common place for oral cancer to start.",
             "eyebrow": "Tongue · lateral border"},
            {"key": "hidden", "say": "From straight on, you can barely see them.", "eyebrow": "Tongue · front view"},
            {"key": "you", "say": "So at home, stick your tongue out and look at each side.", "eyebrow": "Your turn"},
        ],
        credit="Source: NIDCR, The Oral Cancer Exam (NIH Pub. 20-5032) · " + PLATES,
    ),
    # ACS, "What Are Oral Cavity and Oropharyngeal Cancers?": almost all are squamous cell
    # carcinomas; squamous cells are the flat, thin cells that line the mouth and throat.
    "zoom": dict(
        lines=[
            {"key": "hook", "say": "Let's zoom from your jaw to the cells where almost every oral cancer starts.", "eyebrow": "Jaw · teeth · tongue"},
            {"key": "tongue", "say": "The side of the tongue, one of the most common places it begins.", "eyebrow": "Tongue · side"},
            {"key": "lining", "say": "Closer, the surface is a lining, many cells deep.", "eyebrow": "Lining · cut in section"},
            {"key": "cells", "say": "Its cells are called squamous cells. Near the surface, they are flat and thin.", "eyebrow": "Squamous cells"},
            {"key": "start", "say": "Almost all oral cancers start in these cells.", "eyebrow": "Where it starts"},
            {"key": "mirror", "say": "And that lining is the surface you can see in a mirror.", "eyebrow": "Back out"},
        ],
        credit="Source: American Cancer Society, What Are Oral Cavity and Oropharyngeal Cancers? · "
               "3D anatomy: Z-Anatomy (CC BY-SA 4.0), from BodyParts3D, DBCLS · Cells: illustration, not to scale in number",
    ),
    # Calendar 19 Nov 2026 (Ian's redo of the age carousel). SEER_BY_AGE and
    # newCaseShareByAge in src/lib/seerStats.ts: SEER 21, 2019 to 2023.
    "age": dict(
        lines=[
            {"key": "hook", "say": "How common is oral cancer at 25? At 45? At 65?", "eyebrow": "Oral cancer by age"},
            {"key": "at25", "say": "At 25, it is rare: about one new case per 100,000 people a year.", "eyebrow": "Age 25 to 29"},
            {"key": "double", "say": "From there, the rate roughly doubles every five years, into your fifties.", "eyebrow": "Age 30 to 54"},
            {"key": "by65", "say": "By 65, it is about 45 per 100,000, and it peaks near 51.", "eyebrow": "Age 65 and up"},
            {"key": "share", "say": "Ninety-four of every hundred new cases are in people 45 and older.", "eyebrow": "Share of new cases"},
            {"key": "any", "say": "But rare is not zero. A sore that lasts two weeks needs a look, at any age.", "eyebrow": "At any age"},
        ],
        credit="Source: National Cancer Institute, SEER*Explorer and Cancer Stat Facts, SEER 21, 2019 to 2023. "
               "Rates per 100,000 people a year, in five-year age groups",
    ),
    # Calendar 1 Dec 2026 (Ian's redo of the Gardasil image). topics.py
    # hpv_vaccine; CDC, HPV Vaccination Considerations, checked 5 Nov 2026.
    "hpvvax": dict(
        lines=[
            {"key": "hook", "say": "The HPV vaccine works best before exposure. But it is still available after.", "eyebrow": "The HPV vaccine"},
            {"key": "range", "say": "Gardasil 9 is approved from age 9 through 45.", "eyebrow": "Who can get it"},
            {"key": "strains", "say": "It protects against HPV 16 and 18, the types behind most HPV-related cancers.", "eyebrow": "What it covers"},
            {"key": "routine", "say": "It is recommended at 11 or 12, ideally before any exposure.", "eyebrow": "The best time"},
            {"key": "adults", "say": "Through 26, catch-up is recommended. From 27 to 45, ask your clinician.", "eyebrow": "If you missed it"},
            {"key": "limits", "say": "It prevents new infections. It cannot treat one you already have.", "eyebrow": "What it cannot do"},
        ],
        credit="Source: CDC, HPV Vaccination Considerations",
    ),
}
CTA = {"key": "cta", "say": "Check your own risk, free, at oralcheck.org.", "eyebrow": ""}


def _page(scene: str) -> str:
    html = (HERE / f"{scene}.html").read_text()
    if "<!--PLATE_A-->" in html:
        html = html.replace("<!--PLATE_A-->", reel2d._scoped((reel2d.HERE / "plate_a.svg").read_text(), "a-"))
    return html


def _serve(scene: str):
    def serve(route):
        name = route.request.url.split("anim.local/", 1)[1].split("?")[0]
        if name == "scene.html":
            return route.fulfill(status=200, body=_page(scene), headers={"Content-Type": "text/html"})
        for d in (HERE, reel3d.HERE):   # fonts, three.js and the 3D model are shared with reel3d
            if (d / name).exists():
                path = d / name
                break
        else:
            return route.fulfill(status=404, body="")
        ctype = {".css": "text/css", ".js": "text/javascript", ".ttf": "font/ttf", ".glb": "model/gltf-binary"}.get(path.suffix, "application/octet-stream")
        route.fulfill(status=200, body=path.read_bytes(), headers={"Content-Type": ctype})
    return serve


def render(scene: str, plan: dict, total: float, out_mp4: str, fps: int = FPS) -> None:
    from playwright.sync_api import sync_playwright

    n = int(round(total * fps))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps),
                           "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                           "-r", str(fps), out_mp4], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": W, "height": H})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)[:300]))
        page.on("console", lambda m: errors.append(m.text[:300]) if m.type == "error" else None)
        page.route("http://anim.local/**", _serve(scene))
        page.add_init_script(f"window.PLAN = {json.dumps(plan)};")
        page.goto("http://anim.local/scene.html")
        try:
            page.wait_for_function("window.render && window.render(0)", timeout=180000)
        except Exception as exc:
            raise RuntimeError(f"scene {scene} never became ready ({exc}); page errors: {errors[:5]}") from None
        page.evaluate("async () => { await document.fonts.ready; }")
        t0 = time.time()
        for i in range(n):
            page.evaluate(f"window.render({i / fps})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=92, timeout=300000))
            if i % 150 == 0:
                log.info("%s frame %d/%d (%.0fs)", scene, i, n, time.time() - t0)
        if errors:
            log.warning("page errors: %s", errors[:5])
        browser.close()
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg failed encoding frames")


def build(scene: str, out_path: str, *, tts, music: str | None = None, workdir: str | None = None) -> str:
    spec = SCRIPTS[scene]
    lines = spec["lines"] + [CTA]
    workdir = workdir or tempfile.mkdtemp(prefix=f"anim_{scene}_")
    wavs = [tts(l["say"]) for l in lines]
    speech = [reel2._duration(w) / reel2.VOICE_TEMPO for w in wavs]
    pads = [reel2.GAP + (CTA_HOLD if l["key"] == "cta" else max(0.0, MIN_LINE - d)) for l, d in zip(lines, speech)]
    voice = reel2._voice_track(wavs, pads, workdir)
    t, windows, timing = 0.0, [], []
    for d, pad, l in zip(speech, pads, lines):
        windows.append((t, t + d, l["say"]))
        timing.append((t, d + pad))
        t += d + pad
    total = t
    words = align.align(voice, windows)
    shots = [{"key": l["key"], "eyebrow": l["eyebrow"], "t0": round(t0, 3), "len": round(n, 3), "words": w}
             for l, (t0, n), w in zip(lines, timing, words)]
    plan = {"shots": shots, "cta_t0": shots[-1]["t0"], "credit": spec["credit"], "foot": spec.get("foot", ""),
            "foot_on": spec.get("foot_on", [])}
    events = [("glide", max(0.0, s["t0"] - 0.15)) for s in shots[1:]] + [("settle", shots[-1]["t0"] + 0.1)]
    video = os.path.join(workdir, "video.mp4")
    render(scene, plan, total, video)
    audio = reel2._final_audio(voice, reel3d._sfx_track(events, total, workdir), music, total, workdir)
    reel2._run(["ffmpeg", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path])
    (Path(out_path).with_suffix(".json")).write_text(json.dumps(plan, indent=1))
    log.info("%s: %.1fs -> %s", scene, total, out_path)
    return out_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    import oralcheck_agent as A
    scene, out = sys.argv[1], sys.argv[2]
    music = A._generate_music_bed(40, f"anim-{scene}")
    if music is None and A.REEL_MUSIC.exists():
        music = A._loop_music_seamless(str(A.REEL_MUSIC), 42)
    build(scene, out, tts=A._fal_tts, music=music)
