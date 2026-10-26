"""Record a walkthrough of the interactive head model, as a video.

python demo_video.py out.mp4 [--size 1920x1080]

Drives the published page (artifact.html, wrapped in a document) in Chromium on
the Mac GPU with a visible cursor and short captions, records it with
Playwright, then trims the loading time and encodes an MP4 with ffmpeg.
"""
import shutil, subprocess, sys, tempfile, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402  (serves the files to the page)

OUT = Path(sys.argv[1])
W, H = (int(v) for v in (sys.argv[sys.argv.index("--size") + 1] if "--size" in sys.argv else "1920x1080").split("x"))

# A cursor dot that follows the mouse and pulses on click, and a caption pill.
OVERLAY = """
(() => {
  const s = document.createElement('style');
  s.textContent = `#demoCursor{position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;
    background:rgba(255,255,255,0.9);border:2px solid #0d7377;box-shadow:0 2px 8px rgba(0,0,0,0.35);z-index:99999;pointer-events:none;
    transition:transform .12s ease-out}
  #demoCursor.down{transform:scale(0.7);background:#14a8ae}
  #demoCap{position:fixed;left:50%;bottom:44px;transform:translateX(-50%);z-index:99998;pointer-events:none;
    font:600 30px/1.25 'Source Sans 3',system-ui,sans-serif;color:#f4f1ea;background:rgba(13,26,27,0.86);
    padding:14px 28px;border-radius:14px;opacity:0;transition:opacity .35s ease-out;max-width:80vw;text-align:center}
  #demoCap.on{opacity:1}`;
  document.head.appendChild(s);
  const c = document.createElement('div'); c.id = 'demoCursor'; document.body.appendChild(c);
  const k = document.createElement('div'); k.id = 'demoCap'; document.body.appendChild(k);
  addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
  addEventListener('mousedown', () => c.classList.add('down'), true);
  addEventListener('mouseup', () => c.classList.remove('down'), true);
  window.demoCap = (t) => { k.classList.remove('on'); if (t) setTimeout(() => { k.textContent = t; k.classList.add('on'); }, 150); };
})();
"""


def main():
    page_html = HERE / "_demo.html"
    page_html.write_text('<!doctype html><html><head><meta charset=utf8>'
                         '<meta name=viewport content="width=device-width,initial-scale=1"></head><body>'
                         + (HERE / "artifact.html").read_text() + "</body></html>")
    vid_dir = Path(tempfile.mkdtemp())
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"])
            ctx = b.new_context(viewport={"width": W, "height": H}, record_video_dir=str(vid_dir),
                                record_video_size={"width": W, "height": H}, device_scale_factor=1)
            pg = ctx.new_page()
            pg.route("http://anatomy.local/**", render.serve)
            t0 = time.time()
            pg.goto("http://anatomy.local/_demo.html")
            pg.wait_for_function("document.body.dataset.ready === '1'", timeout=180000)
            pg.evaluate(OVERLAY)
            # start on the open mouth, no labels (no skin on the head since 23 Oct; the whole-head muscle view renders too
            # slowly to orbit smoothly and is not the friendliest first sight). Earlier, orbiting
            # from there swung the camera into the cheek)
            pg.evaluate("document.querySelector('button[data-look=mouth]').click(); oc.clearLabels(); oc.view(0, 6, 1.1, [0, 1.515, 0.07])")
            pg.wait_for_timeout(2500)
            start = time.time() - t0                       # everything before this is loading
            m = pg.mouse
            stage = pg.locator("#stage").bounding_box()
            cx, cy = stage["x"] + stage["width"] / 2, stage["y"] + stage["height"] / 2

            def cap(t, hold=0):
                pg.evaluate(f"window.demoCap({t!r})"); pg.wait_for_timeout(hold)

            def glide(x, y, steps=25):
                m.move(x, y, steps=steps)

            def click(sel, hold=1800):
                box = pg.locator(sel).first.bounding_box()
                glide(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                pg.wait_for_timeout(250); m.down(); pg.wait_for_timeout(90); m.up(); pg.wait_for_timeout(hold)

            def orbit(dx, dy, ms=2600):
                glide(cx - dx / 2, cy - dy / 2, 15); m.down()
                n = max(1, ms // 33)
                for i in range(1, n + 1):
                    m.move(cx - dx / 2 + dx * i / n, cy - dy / 2 + dy * i / n); pg.wait_for_timeout(16)
                m.up(); pg.wait_for_timeout(500)

            def slide(sel, a, b, ms=2600):
                box = pg.locator(sel).bounding_box(); y = box["y"] + box["height"] / 2
                x = lambda f: box["x"] + 10 + (box["width"] - 20) * f
                glide(x(a), y); m.down()
                n = max(1, ms // 40)
                for i in range(1, n + 1):
                    m.move(x(a + (b - a) * i / n), y); pg.wait_for_timeout(20)
                m.up(); pg.wait_for_timeout(500)

            cap("A layered 3D model of the mouth, head and neck, made for OralCheck", 3200)
            cap("Drag to turn it"); orbit(260, 20); orbit(-260, -10)
            cap("Open and close the jaw"); slide("#open", 1.0 / 1.3, 0.05, 2200); slide("#open", 0.05, 1.0 / 1.3, 2200)
            cap("Say ahh: the uvula, the tonsils and the back of the throat"); click("text=Back of the mouth", 3800)
            cap("See-through mode lights up one structure"); click("text=Sides of the tongue", 3600)
            cap("Peel the layers: muscle, bone, deep"); click("button[data-look=layers]", 600)
            slide("#depth", 0.0, 1.0, 3600)
            cap("Cut along any of the three planes"); click("text=Midline section", 2600)
            slide("#cutpos", 0.5, 0.62, 2200); slide("#cutpos", 0.62, 0.5, 1600)
            cap("Tap any part to name it")
            glide(cx + 40, cy + 60); pg.wait_for_timeout(300); m.down(); pg.wait_for_timeout(90); m.up(); pg.wait_for_timeout(2600)
            cap("And the layers of the skin, up close"); click("button[data-look=block]", 3400)
            cap("oralcheck.org", 2600)
            dur = time.time() - t0 - start
            vpath = pg.video.path()
            ctx.close(); b.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-i", str(vpath), "-t", f"{dur:.2f}",
                        "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "30",
                        "-movflags", "+faststart", str(OUT)], check=True)
        print("wrote", OUT, f"{dur:.1f}s")
    finally:
        page_html.unlink(missing_ok=True)
        shutil.rmtree(vid_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
