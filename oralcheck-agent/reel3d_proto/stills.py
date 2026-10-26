import sys, time
from playwright.sync_api import sync_playwright
D = sys.argv[1]; ts = [float(x) for x in sys.argv[2].split(",")]
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
    pg.goto("http://127.0.0.1:8765/scene.html")
    pg.wait_for_function("window.render && window.render(0)", timeout=120000)
    pg.evaluate("document.fonts.ready")
    for t in ts:
        t0 = time.time(); pg.evaluate(f"window.render({t})")
        pg.screenshot(path=f"{D}/still_{t:05.2f}.jpg", type="jpeg", quality=88)
        print(f"t={t} {time.time()-t0:.2f}s")
    b.close()
