"""Prototype reels, 1080 x 1920, 12 s at 30 fps, with the same captions and timing.

python make_reel.py 2d plate_a.svg plate_b.svg out.mp4
python make_reel.py 3d frames_dir out.mp4          (frames from reel3d_frames.py)
The page is driven frame by frame (window.setT), so the video is exact and repeatable.
"""
import re, subprocess, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

FPS, DUR, W, H = 30, 12.0, 1080, 1920
FONT = "/Users/ianharris/projects/OralCheck/oralcheck-agent/reel3d/SourceSans3.ttf"

# (start, end, kicker, line); the words are the site's own ("two weeks", messages/en.json)
CAPTIONS = [
    (0.3, 3.0, "Mouth and throat", "Where can mouth cancer start?"),
    (3.0, 5.0, "Mouth and throat", "The tongue, the floor of the mouth, the tonsils, the palate, the lips"),
    (5.4, 7.6, "What to look for", "Check the sides of your tongue"),
    (7.6, 9.8, "What to look for", "A white patch that won't wipe away is one sign to get checked"),
    (9.8, 12.0, "OralCheck", "Lasting more than two weeks? See a dentist or doctor."),
]
FOOT = "Illustration for education, not a real case. Not reviewed by a clinician."

def scoped(svg, p):
    """give every id in an inline SVG a prefix, so two plates can share a page"""
    svg = re.sub(r'id="([^"]+)"', lambda m: f'id="{p}{m.group(1)}"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{p}{m.group(1)})', svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{p}{m.group(1)}"', svg)
    return re.sub(r'<svg ([^>]*?)width="\d+" height="\d+"', r'<svg \1width="100%" height="100%" preserveAspectRatio="xMidYMid slice"', svg, count=1)

def page(mode, a=None, b=None, frames=None):
    caps = "".join(f'<div class="cap" data-s="{s}" data-e="{e}"><i>{k}</i><b>{t}</b></div>' for s, e, k, t in CAPTIONS)
    if mode == "2d":
        stage = f'<div id="B" class="plate">{scoped(b, "b-")}</div><div id="A" class="plate">{scoped(a, "a-")}</div>'
    else:
        stage = f'<img id="F" src="file://{frames}/f0000.png">'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Source Sans 3'; src: url('file://{FONT}'); font-weight: 200 900; }}
html,body {{ margin:0; width:{W}px; height:{H}px; overflow:hidden; background:#f5f3f0; font-family:'Source Sans 3',sans-serif; color:#15201f; }}
.plate, #F {{ position:absolute; inset:0; width:100%; height:100%; }} .plate svg {{ display:block; }}
.cap {{ position:absolute; left:84px; right:84px; top:150px; opacity:0; }}
.cap i {{ display:block; font-style:normal; font-weight:600; font-size:30px; letter-spacing:.06em; text-transform:uppercase; color:#0d7377; margin-bottom:18px; }}
.cap b {{ display:block; font-weight:600; font-size:66px; line-height:1.08; }}
#foot {{ position:absolute; left:84px; right:84px; bottom:120px; font-size:26px; color:#5b6766; opacity:0; }}
#url {{ position:absolute; left:84px; bottom:180px; font-size:40px; font-weight:600; color:#0d7377; opacity:0; }}
#bar {{ position:absolute; left:84px; right:84px; bottom:84px; height:4px; background:#d9dcd8; border-radius:2px; }} #bar i {{ position:absolute; left:0; top:0; bottom:0; background:#0d7377; border-radius:2px; }}
#scrim {{ position:absolute; left:0; right:0; top:0; height:560px; background:linear-gradient(#f5f3f0 55%, rgba(245,243,240,0)); }}
#scrimB {{ position:absolute; left:0; right:0; bottom:0; height:420px; background:linear-gradient(rgba(245,243,240,0), #f5f3f0 55%); }}
#endcard {{ position:absolute; inset:0; background:#f5f3f0; opacity:0; }}
</style></head><body>{stage}<div id="scrim"></div><div id="scrimB"></div><div id="endcard"></div>{caps}<div id="url">oralcheck.org</div><div id="foot">{FOOT}</div><div id="bar"><i></i></div>
<script>
const ease = (x) => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
const ramp = (t, a, b) => ease((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const vb = (el, box) => el && el.setAttribute("viewBox", box.map((v) => v.toFixed(2)).join(" "));
const op = (id, v) => {{ const e = document.getElementById(id); if (e) e.setAttribute("opacity", v.toFixed(3)); }};
// 9:16 boxes: [x, y, w, h]
const fit = (cx, cy, w) => [cx - w / 2, cy - w * 16 / 9 / 2, w, w * 16 / 9];
window.setT = (t) => {{
  document.querySelectorAll(".cap").forEach((c) => {{ const s = +c.dataset.s, e = +c.dataset.e;
    c.style.opacity = Math.min(ramp(t, s, s + 0.35), 1 - ramp(t, e - 0.3, e)); c.style.transform = `translateY(${{(1 - ramp(t, s, s + 0.45)) * 18}}px)`; }});
  document.getElementById("endcard").style.opacity = ramp(t, 9.8, 10.3) * 0.0;
  document.getElementById("url").style.opacity = ramp(t, 10.0, 10.4);
  document.getElementById("foot").style.opacity = t > 5.4 ? Math.min(ramp(t, 7.6, 8.0), 1) : 0;
  document.querySelector("#bar i").style.width = (100 * t / {DUR}) + "%";
  const F = document.getElementById("F");
  if (F) {{ F.src = `file://{frames}/f${{String(Math.round(t * {FPS})).padStart(4, "0")}}.png`; return; }}
  // plate B: whole head, then into the mouth; the mouth fades in over the faded head
  const kB = ramp(t, 0.6, 3.4), svgB = document.querySelector("#B svg");
  const a0 = fit(500, 520, 840), a1 = fit(690, 700, 470);
  vb(svgB, a0.map((v, i) => lerp(v, a1[i], kB)));
  op("b-airway", ramp(t, 0.4, 1.4)); op("b-mouth", ramp(t, 0.4, 1.4));
  op("b-zones", 1); ["tongue", "base", "floor", "soft", "tonsil", "lips"].forEach((z, i) => op("b-zone-" + z, 0.0 + ramp(t, 3.0 + i * 0.25, 3.35 + i * 0.25) * (1 - ramp(t, 4.7, 5.0))));
  op("b-labels", 0);
  // plate A: the open mouth, then towards the side of the tongue, where the patch appears
  const kA = ramp(t, 5.2, 9.6), svgA = document.querySelector("#A svg");
  document.getElementById("A").style.opacity = ramp(t, 4.8, 5.4);
  document.getElementById("B").style.opacity = 1 - ramp(t, 5.0, 5.5);
  const b0 = fit(500, 560, 1040), b1 = fit(430, 610, 640);
  vb(svgA, b0.map((v, i) => lerp(v, b1[i], kA)));
  const ts = document.getElementById("a-lab-tongue-side");
  if (ts && !ts.dataset.moved) {{ ts.dataset.moved = 1; const tx = ts.querySelector("text"); tx.setAttribute("x", 122); tx.setAttribute("font-size", 24); tx.setAttribute("font-weight", 600);
    tx.setAttribute("style", "paint-order:stroke; stroke:#f5f3f0; stroke-width:6px; stroke-linejoin:round");
    ts.querySelectorAll("path").forEach((p) => p.setAttribute("d", "M368,640 L340,640 L122,640")); }}
  op("a-labels", 1); document.querySelectorAll("#a-labels > g").forEach((g) => g.setAttribute("opacity", g.id === "a-lab-tongue-side" ? ramp(t, 6.0, 6.4).toFixed(3) : "0"));
  op("a-lesion-white", ramp(t, 7.4, 8.2));
}};
setT(0);
</script></body></html>"""

def render(html, out):
    with tempfile.TemporaryDirectory() as td:
        hp = Path(td) / "reel.html"; hp.write_text(html)
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--use-angle=metal", "--enable-gpu", "--allow-file-access-from-files"])
            pg = b.new_page(viewport={"width": W, "height": H}); pg.goto(hp.as_uri()); pg.wait_for_timeout(500)
            for i in range(int(FPS * DUR)):
                pg.evaluate(f"setT({i / FPS})")
                if pg.evaluate("!!document.getElementById('F')"):
                    pg.wait_for_function("document.getElementById('F').complete")
                pg.screenshot(path=f"{td}/{i:04d}.jpg", type="jpeg", quality=92)
            b.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{td}/%04d.jpg", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "18", "-movflags", "+faststart", str(out)], check=True)

if __name__ == "__main__":
    if sys.argv[1] == "2d":
        render(page("2d", Path(sys.argv[2]).read_text(), Path(sys.argv[3]).read_text()), sys.argv[4])
    else:
        render(page("3d", frames=Path(sys.argv[2]).resolve()), sys.argv[3])
    print(sys.argv[-1])
