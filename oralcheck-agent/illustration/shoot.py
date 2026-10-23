"""Screenshot a local HTML or SVG file: python shoot.py in.html out.png WxH [scale]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
src, out, size = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
w, h = (int(v) for v in size.split("x")); scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-angle=metal", "--enable-gpu"])
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
    pg.goto(src.as_uri()); pg.wait_for_timeout(300)
    pg.screenshot(path=out, type="png" if out.endswith(".png") else "jpeg", **({} if out.endswith(".png") else {"quality": 90}))
    b.close()
