"""
3D reels: real anatomy, rendered clinical and minimal, with narration.

A reel is a list of shots. Each shot is one spoken sentence and a focus, the
part of the mouth it is about:

    {"shots": [
        {"say": "Oral cancer most often starts in places you rarely look.", "focus": "overview"},
        {"say": "The sides of the tongue come first.", "focus": "tongue",
         "label": {"k": "Most common site", "t": "Sides of the tongue", "d": "Stick it out, look left, then right."}},
        ...
        {"say": "Check your own risk, free, at oralcheck.org.", "focus": "cta"}]}

Every focus has a preset camera move and a set of structures that fade to glass
around it (FOCI), so a plan never has to say anything about cameras. The look:
ivory anatomy on pale studio grey, a section cut through the upper jaw, the
subject in teal, a hairline label with a tap. reel3d/scene.html does the
drawing; this module does the voice, timing, sound and assembly, reusing
reel2's voice track, word alignment and final mix.

Anatomy is Z-Anatomy (CC BY-SA 4.0, from BodyParts3D). Share-alike means
each reel carries CREDIT on screen and in its caption. See reel3d/ATTRIBUTION.md.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path

import align
import reel2

log = logging.getLogger("oralcheck.reel3d")

HERE = Path(__file__).parent / "reel3d"
W, H, FPS = 1080, 1920, 30
CREDIT = "3D anatomy: Z-Anatomy (CC BY-SA 4.0), from BodyParts3D, DBCLS"
MIN_SHOT = 3.4      # seconds: room for the camera move, the tap and the label
CTA_HOLD = 2.2      # silent hold on the end card after the last line

ALL = ["bone", "teeth", "gums", "tongue", "floor", "throat", "other"]


def _except(*keep):
    return [g for g in ALL if g not in keep]


# cam: [[azimuth, elevation, distance] at shot start, same at shot end], degrees.
FOCI = {
    "overview": dict(focus=None, ghost=[], cam=[[38, 10, 6.4], [20, 6, 5.8]], view="Oral cavity · anterolateral"),
    "tongue":   dict(focus="tongue", ghost=_except("tongue"), cam=[[70, 2, 4.6], [80, 0, 4.3]], view="Tongue · lateral border"),
    "floor":    dict(focus="floor", ghost=_except("floor"), cam=[[34, -40, 4.6], [22, -44, 4.3]], view="Floor of mouth · inferior"),
    "lips":     dict(focus="lips", ghost=["bone", "other"], cam=[[-30, 6, 5.0], [-14, 4, 4.8]], view="Lips · lower border"),
    "gums":     dict(focus="gums", ghost=["bone", "other"], cam=[[16, 4, 4.9], [-10, 2, 4.7]], view="Gingiva · anterior"),
    "teeth":    dict(focus="teeth", ghost=["bone", "gums", "other"], cam=[[-26, 6, 5.0], [-8, 4, 4.8]], view="Dentition · anterior"),
    "throat":   dict(focus="throat", ghost=_except("throat"), cam=[[128, 8, 3.6], [142, 6, 3.3]], aim=-0.1, view="Oropharynx · tonsils"),
    "nodes":    dict(focus="nodes", ghost=ALL, cam=[[30, -32, 5.4], [10, -28, 5.1]], view="Lymph nodes · neck"),
    "glands":   dict(focus="glands", ghost=ALL, cam=[[62, -22, 5.0], [48, -24, 4.8]], view="Salivary glands"),
    "cta":      dict(focus=None, ghost=[], cam=[[20, 6, 5.8], [-12, 6, 6.3]], view=""),
}

# Sound is quiet and clinical: a soft click on each tap, a breath of air as the
# camera moves, one low tone under the end card. No pops, no dings.
SFX = {
    "tap":    (["-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*2200*t)*exp(-t*140)+0.25*sin(2*PI*900*t)*exp(-t*60)':d=0.12:s=44100"], 0.30),
    "glide":  (["-f", "lavfi", "-i", "anoisesrc=d=1.1:c=pink:a=0.5"], 0.10),
    "settle": (["-f", "lavfi", "-i", "aevalsrc='0.4*sin(2*PI*392*t)*exp(-t*1.6)+0.25*sin(2*PI*587.3*t)*exp(-t*2.2)':d=2.4:s=44100"], 0.16),
}
SFX_FILTER = {
    "glide": "highpass=f=350,lowpass=f=2600,afade=t=in:d=0.45,afade=t=out:st=0.5:d=0.6",
    "settle": "afade=t=in:d=0.05",
}


def _sfx_track(events: list[tuple[str, float]], total: float, workdir: str) -> str | None:
    if not events:
        return None
    files = {}
    for name, (src, _) in SFX.items():
        out = os.path.join(workdir, f"sfx3d_{name}.wav")
        filt = ["-af", SFX_FILTER[name]] if name in SFX_FILTER else []
        reel2._run(["ffmpeg", "-y", *src, *filt, "-ar", "44100", "-ac", "1", out])
        files[name] = out
    cmd, parts = ["ffmpeg", "-y"], []
    for k, (name, t) in enumerate(events):
        cmd += ["-i", files[name]]
        ms = max(0, int(t * 1000))
        parts.append(f"[{k}:a]adelay={ms}|{ms},volume={SFX[name][1]}[s{k}]")
    parts.append("".join(f"[s{k}]" for k in range(len(events)))
                 + f"amix=inputs={len(events)}:normalize=0,apad=whole_dur={total:.3f}[out]")
    out = os.path.join(workdir, "sfx3d.wav")
    reel2._run(cmd + ["-filter_complex", ";".join(parts), "-map", "[out]", "-t", f"{total:.3f}",
                      "-ar", "44100", "-ac", "2", out])
    return out


def validate(plan: dict) -> dict:
    """Drop unknown foci, make sure the reel ends on the end card."""
    shots = []
    for s in plan.get("shots", []):
        if not isinstance(s, dict) or not str(s.get("say", "")).strip():
            continue
        f = s.get("focus") if s.get("focus") in FOCI else "overview"
        label = s.get("label") if isinstance(s.get("label"), dict) and FOCI[f]["focus"] else None
        shots.append({"say": str(s["say"]).strip(), "focus": f, "label": label})
    shots = [s for s in shots if s["focus"] != "cta"]
    shots.append({"say": "Check your own risk, free, at oralcheck.org.", "focus": "cta", "label": None})
    return {"shots": shots}


def _render_frames(scene_plan: dict, total: float, out_mp4: str) -> None:
    from playwright.sync_api import sync_playwright

    n = int(round(total * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                           "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                           "-r", str(FPS), out_mp4], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        # Software WebGL: the same renderer locally and on a GPU-less CI runner.
        browser = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": W, "height": H})

        def serve(route):
            name = route.request.url.split("reel3d.local/", 1)[1].split("?")[0]
            path = HERE / name
            ctype = {".html": "text/html", ".js": "text/javascript", ".glb": "model/gltf-binary",
                     ".ttf": "font/ttf"}.get(path.suffix, "application/octet-stream")
            route.fulfill(status=200, body=path.read_bytes(), headers={"Content-Type": ctype})

        page.route("http://reel3d.local/**", serve)
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)[:300]))
        page.on("console", lambda m: errors.append(m.text[:300]) if m.type == "error" else None)
        page.add_init_script(f"window.PLAN = {json.dumps(scene_plan)};")
        page.goto("http://reel3d.local/scene.html")
        try:
            page.wait_for_function("window.render && window.render(0)", timeout=180000)
        except Exception as exc:
            raise RuntimeError(f"3D scene never became ready ({exc}); page errors: {errors[:5]}") from None
        page.evaluate("async () => { await document.fonts.load('600 54px \"Source Sans 3\"'); "
                      "await document.fonts.load('500 20px \"JetBrains Mono\"'); await document.fonts.ready; }")
        t0 = time.time()
        for i in range(n):
            page.evaluate(f"window.render({i / FPS})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=92))
            if i % 150 == 0:
                log.info("3D frame %d/%d (%.0fs)", i, n, time.time() - t0)
        browser.close()
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg failed encoding the 3D frames")


def build(plan: dict, out_path: str, *, tts, music: str | None = None, workdir: str | None = None) -> str:
    """Render a narrated 3D reel to out_path. `tts(text) -> wav path`."""
    plan = validate(plan)
    shots = plan["shots"]
    workdir = workdir or tempfile.mkdtemp(prefix="reel3d_")

    wavs = [tts(s["say"]) for s in shots]
    speech = [reel2._duration(w) / reel2.VOICE_TEMPO for w in wavs]
    pads = []
    for k, d in enumerate(speech):
        floor = CTA_HOLD if shots[k]["focus"] == "cta" else max(0.0, MIN_SHOT - d)
        pads.append(reel2.GAP + floor)
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
        f = FOCI[s["focus"]]
        if s["focus"] != "cta":
            k_story += 1
        scene_shots.append({
            "t0": round(t0, 3), "len": round(length, 3), "focus": f["focus"], "ghost": f["ghost"],
            "cam": f["cam"], "aim": f.get("aim"), "view": f["view"], "label": s["label"], "tap": 0.55, "words": w,
            "step": f"{k_story:02d} / {n_story:02d}" if s["focus"] != "cta" else "",
        })
        if t0 > 0:
            events.append(("glide", max(0.0, t0 - 0.15)))
        if s["label"]:
            events.append(("tap", t0 + 0.55))
        if s["focus"] == "cta":
            events.append(("settle", t0 + 0.1))
    cta_t0 = scene_shots[-1]["t0"]
    scene_plan = {"shots": scene_shots, "cta_t0": cta_t0, "credit": CREDIT}

    video = os.path.join(workdir, "video.mp4")
    _render_frames(scene_plan, total, video)
    audio = reel2._final_audio(voice, _sfx_track(events, total, workdir), music, total, workdir)
    reel2._run(["ffmpeg", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path])
    log.info("3D reel: %.1fs, %d shots -> %s", total, len(shots), out_path)
    return out_path
