"""Trace flat masks from render_plate.py into smooth SVG paths.

python tracer.py mask_dir out.json [name=blur,min_area ...]
Blurring the mask before contouring at half height is what smooths away the
atlas's slivers and stair-steps; the blur radius is per structure.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

def contours(a, lv):
    """Marching squares: closed polylines (x, y in pixels) where a crosses lv."""
    b = a >= lv
    tl, tr, br, bl = b[:-1, :-1], b[:-1, 1:], b[1:, 1:], b[1:, :-1]
    case = tl * 8 + tr * 4 + br * 2 + bl * 1
    ys, xs = np.nonzero((case > 0) & (case < 15))
    def cross(y0, x0, y1, x1):
        v0, v1 = a[y0, x0], a[y1, x1]; t = (lv - v0) / (v1 - v0 + 1e-12)
        return (x0 + t * (x1 - x0), y0 + t * (y1 - y0))
    # edges: T(top) R(right) B(bottom) L(left) of each cell, oriented so the high side is on the left
    E = {"T": lambda y, x: cross(y, x, y, x + 1), "R": lambda y, x: cross(y, x + 1, y + 1, x + 1),
         "B": lambda y, x: cross(y + 1, x, y + 1, x + 1), "L": lambda y, x: cross(y, x, y + 1, x)}
    SEG = {1: [("L", "B")], 2: [("B", "R")], 3: [("L", "R")], 4: [("R", "T")], 5: [("L", "T"), ("R", "B")], 6: [("B", "T")], 7: [("L", "T")],
           8: [("T", "L")], 9: [("T", "B")], 10: [("T", "R"), ("B", "L")], 11: [("T", "R")], 12: [("R", "L")], 13: [("R", "B")], 14: [("B", "L")]}
    key = lambda y, x, e: {"T": (y, x, "h"), "B": (y + 1, x, "h"), "L": (y, x, "v"), "R": (y, x + 1, "v")}[e]
    nxt, pt = {}, {}
    for y, x in zip(ys.tolist(), xs.tolist()):
        for e0, e1 in SEG[int(case[y, x])]:
            k0, k1 = key(y, x, e0), key(y, x, e1)
            nxt[k0] = k1; pt[k0] = E[e0](y, x); pt[k1] = E[e1](y, x)
    out, seen = [], set()
    for k in list(nxt):
        if k in seen: continue
        poly, c = [], k
        while c in nxt and c not in seen:
            seen.add(c); poly.append(pt[c]); c = nxt[c]
        if len(poly) > 2: out.append(np.array(poly + [poly[0]]))
    return out

def rdp(pts, eps):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]; ab = b - a; n = np.hypot(*ab) or 1e-9
    d = np.abs(np.cross(ab, pts - a)) / n
    i = int(np.argmax(d))
    if d[i] > eps: return np.vstack([rdp(pts[:i + 1], eps)[:-1], rdp(pts[i:], eps)])
    return np.array([a, b])

def to_path(pts):
    # closed Catmull-Rom through the points, as cubic Beziers
    n = len(pts); d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6; c2 = p2 - (p3 - p1) / 6
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return "".join(d) + "Z"

def trace(path, blur=3.0, min_area=60.0, eps=0.8, grow=0.0):
    a = np.asarray(Image.open(path).convert("RGBA"))[:, :, 3]
    im = Image.fromarray(a)
    if grow: im = im.filter(ImageFilter.MaxFilter(int(grow) * 2 + 1))
    a = np.asarray(im.filter(ImageFilter.GaussianBlur(blur)), dtype=float) / 255.0
    lines = contours(np.pad(a, 1), 0.5) ; lines = [l - 1 for l in lines]
    out = []
    for ln in lines:
        if len(ln) < 8: continue
        x, y = ln[:, 0], ln[:, 1]; area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        if area < min_area: continue
        p = rdp(ln[:-1] if np.allclose(ln[0], ln[-1]) else ln, eps)
        if len(p) >= 4: out.append(to_path(p))
    return out

if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    opts = {}
    for a in sys.argv[3:]:
        k, v = a.split("="); vals = [float(x) for x in v.split(",")]
        opts[k] = dict(zip(["blur", "min_area", "eps", "grow"], vals))
    res = {f.stem: trace(f, **opts.get(f.stem, {})) for f in sorted(src.glob("*.png")) if f.stem in opts or "all" in opts}
    dst.write_text(json.dumps(res)); print({k: len(v) for k, v in res.items()})
