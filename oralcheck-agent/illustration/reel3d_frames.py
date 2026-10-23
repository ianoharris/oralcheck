"""Frames for the 3D prototype reel (same timeline as make_reel.py): the atlas mouth, open, turning,
drawn with the illustration shader. python reel3d_frames.py out_dir"""
import base64, io, math, sys
from pathlib import Path
from PIL import Image
from render_plate import session

FPS, DUR, W, H = 30, 12.0, 540, 960
def ease(x): return 0 if x <= 0 else 1 if x >= 1 else x * x * (3 - 2 * x)
def ramp(t, a, b): return ease((t - a) / (b - a))

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
p, b, pg, errs = session()
try:
    ev = lambda js: pg.evaluate(f"() => {js}")
    ev("pl.cut(null)"); ev("pl.jaw(1.3, 1)")
    ev("""pl.show({tooth:{},tongue:{},mucosa:{},softpalate:{},tonsil:{}}, '^(Upper labial|Lower labial|Buccal|Palatoglossal|Hard palate mucosa|Mucosa of nasal|Trachea|Oesophagus|Floor of mouth|Genioglossus|Hyoglossus|Styloglossus)')""")
    # pin the white patch on the side of the tongue, found from the front as in plate A
    ev("pl.size(1000, 1000, 1)"); ev("pl.view({dir:[0,-0.3,1], target:[0,1.522,0.05], height:0.1})")
    hit = ev("pl.hit(0.372, 0.64, '^Tongue$')"); print("patch at", hit)
    ev(f"pl.decal({hit['p']}, {hit['n']}, 0.0032, '#eee8dc', 7)"); ev("pl.decalScale(0)")
    ev(f"pl.size({W}, {H}, 2)")
    for i in range(int(FPS * DUR)):
        t = i / FPS
        az = math.radians(-55 + 40 * ramp(t, 0.0, 5.0) - 15 * ramp(t, 5.0, 9.6))
        h = 0.125 - 0.04 * ramp(t, 5.0, 9.6)
        tx = -0.008 * ramp(t, 5.0, 9.6)
        ev(f"pl.view({{dir:[{math.sin(az):.4f},-0.3,{math.cos(az):.4f}], target:[{tx:.4f},{1.546 - 0.01 * ramp(t, 5.0, 9.6):.4f},0.045], height:{h:.4f}}})")
        z = ramp(t, 3.0, 3.4) * (1 - ramp(t, 4.7, 5.0))
        ev(f"pl.tint('^Tongue$', {0.55 * z:.3f})"); ev(f"pl.tint('^(Soft palate|Uvula|Palatine tonsil)', {0.55 * ramp(t, 3.5, 3.9) * (1 - ramp(t, 4.7, 5.0)):.3f})")
        ev(f"pl.decalScale({ramp(t, 7.4, 8.2):.3f})")
        url = ev("pl.render()")
        im = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1]))).convert("RGBA")
        bg = Image.new("RGBA", im.size, (245, 243, 240, 255)); bg.alpha_composite(im)
        bg.convert("RGB").save(out / f"f{i:04d}.png")
        if i % 60 == 0: print(i, flush=True)
finally:
    if errs: print("CONSOLE", errs[:5])
    b.close(); p.stop()
