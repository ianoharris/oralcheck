"""Render stills of the anatomy viewer from a list of scripted shots.

python render.py shots.json out_dir [--size 1080x1350]
Each shot is {"name", "js": [...oc calls as JS strings...]}.
"""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
TYPES = {".html": "text/html", ".js": "text/javascript", ".glb": "model/gltf-binary"}

def serve(route):
    name = route.request.url.split("anatomy.local/", 1)[1].split("?")[0] or "viewer.html"
    p = HERE / name
    route.fulfill(status=200, body=p.read_bytes(), headers={"Content-Type": TYPES.get(p.suffix, "application/octet-stream")})

def main():
    shots = json.loads(Path(sys.argv[1]).read_text()); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    w, h = (int(x) for x in (sys.argv[sys.argv.index("--size") + 1] if "--size" in sys.argv else "1080x1350").split("x"))
    with sync_playwright() as p:
        # The Mac's GPU through Metal; SwiftShader (software) takes minutes a frame here.
        gpu = ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"]
        soft = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
        b = p.chromium.launch(args=soft if "--soft" in sys.argv else gpu)
        pg = b.new_page(viewport={"width": w, "height": h})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:400]))
        pg.on("console", lambda m: errs.append(m.text[:400]) if m.type == "error" else None)
        pg.route("http://anatomy.local/**", serve)
        pg.add_init_script("window.OC_SCRIPTED = true;")
        pg.goto("http://anatomy.local/viewer.html")
        try:
            pg.wait_for_function("document.body.dataset.ready === '1'", timeout=600000)
        except Exception:
            print("NOT READY", errs[:5]); raise
        for s in shots:
            t = time.time(); res = None
            for js in s["js"]:
                res = pg.evaluate(f"() => {js}")
            pg.evaluate("() => window.oc.render()")
            pg.screenshot(path=str(out / f"{s['name']}.jpg"), type="jpeg", quality=90, timeout=600000)
            print(s["name"], f"{time.time() - t:.0f}s", json.dumps(res)[:1500] if res is not None else "")
        print("GL", pg.evaluate("() => { const c = document.createElement('canvas').getContext('webgl2'); const e = c.getExtension('WEBGL_debug_renderer_info'); return e ? c.getParameter(e.UNMASKED_RENDERER_WEBGL) : '?'; }"))
        if errs: print("ERRORS", errs[:8])
        b.close()

if __name__ == "__main__":
    main()
