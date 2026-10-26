import sys, subprocess, time
from playwright.sync_api import sync_playwright
D, out, fps, dur = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto("http://127.0.0.1:8765/scene.html")
    pg.wait_for_function("window.render && window.render(0)", timeout=120000); pg.evaluate("document.fonts.ready")
    t0 = time.time(); n = int(dur * fps)
    for i in range(n):
        pg.evaluate(f"window.render({i / fps})")
        ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
        if i % 60 == 0: print(f"frame {i}/{n} {time.time() - t0:.0f}s", flush=True)
    b.close()
ff.stdin.close(); ff.wait(); print("done", time.time() - t0)
