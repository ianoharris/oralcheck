"""Capture plates from the illustration renderer.

python render_plate.py steps.json out_dir
Each step is {"js": [...], "save": "name"} (the rendered plate, RGBA PNG),
{"js": [...], "mask": "name", "pattern": "regex or null"} (a flat white shape), or
{"js": [...]} (the last expression's value is printed).
The model is read from MODEL (default: the anatomy3d head.glb in Ian's main checkout).
"""
import base64, json, os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
MODEL = Path(os.environ.get("MODEL", "/Users/ianharris/projects/OralCheck/oralcheck-agent/anatomy3d/head.glb"))
TYPES = {".html": "text/html", ".js": "text/javascript", ".glb": "model/gltf-binary"}

def serve(route):
    name = route.request.url.split("plate.local/", 1)[1].split("?")[0] or "plate.html"
    p = MODEL if name == "head.glb" else HERE / name
    route.fulfill(status=200, body=p.read_bytes(), headers={"Content-Type": TYPES.get(p.suffix, "application/octet-stream")})

def save(url, path):
    path.write_bytes(base64.b64decode(url.split(",", 1)[1]))

def session():
    p = sync_playwright().start()
    b = p.chromium.launch(args=["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1200, "height": 1200})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:400]))
    pg.on("console", lambda m: errs.append(m.text[:400]) if m.type in ("error", "warning") else None)
    pg.route("http://plate.local/**", serve)
    pg.goto("http://plate.local/plate.html")
    pg.wait_for_function("document.body.dataset.ready === '1' || !!document.body.dataset.error", timeout=600000)
    if pg.evaluate("() => document.body.dataset.error"): raise SystemExit(pg.evaluate("() => document.body.dataset.error"))
    return p, b, pg, errs

def run(pg, steps, out):
    for s in steps:
        t = time.time(); res = None
        for js in s.get("js", []): res = pg.evaluate(f"() => {js}")
        if "save" in s: save(pg.evaluate("() => pl.render()"), out / f"{s['save']}.png"); res = s["save"]
        if "ids" in s:
            o = pg.evaluate("() => pl.ids()"); save(o["url"], out / f"{s['ids']}.png")
            (out / f"{s['ids']}.json").write_text(json.dumps(o["legend"])); res = s["ids"]
        if "mask" in s: save(pg.evaluate(f"() => pl.mask({json.dumps(s.get('pattern'))}, {json.dumps(bool(s.get('section')))})"), out / f"{s['mask']}.png"); res = s["mask"]
        print(f"{time.time() - t:.1f}s", json.dumps(res)[:2000] if res is not None else "")

if __name__ == "__main__":
    steps = json.loads(Path(sys.argv[1]).read_text()); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    p, b, pg, errs = session()
    try: run(pg, steps, out)
    finally:
        if errs: print("CONSOLE", errs[:8])
        b.close(); p.stop()
