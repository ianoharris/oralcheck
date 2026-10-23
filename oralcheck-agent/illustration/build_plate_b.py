"""Plate B: the mouth and throat in a midline cut, with the head as faded context.

python build_plate_b.py paths.json mask_dir out.svg
Outlines are traced from the Z-Anatomy atlas (tracer.py), so proportions are the
atlas's. A few parts are redrawn by hand, as an illustrator would over a
reference: the soft palate (the atlas has it as a flat shelf), the lips (there
is no skin in the model any more), the back wall of the throat (the atlas
section includes muscles behind it), and the tonsil. Every layer has an id so
the reel can fade layers in and out, and so zones and lesions can be switched.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from tracer import trace
import lesions

PATHS, MASKS, OUT = {}, Path("."), None
W, H = 1000, 1100

def d(*keys): return " ".join(p for k in keys for p in PATHS.get(k, []))
def mask(k): return np.asarray(Image.open(MASKS / f"{k}.png").convert("RGBA"))[:, :, 3] > 127

def catmull(pts, closed=True, n=10):
    """Dense points along a Catmull-Rom curve through pts (for rasterising)."""
    P = np.array(pts, float); m = len(P); out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0, p1, p2, p3 = P[i - 1] if (closed or i) else P[0], P[i], P[(i + 1) % m], P[(i + 2) % m] if (closed or i + 2 < m) else P[-1]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed: out.append(P[-1])
    return [tuple(p) for p in out]

def path(pts, closed=True):
    """SVG cubic path through pts (Catmull-Rom converted to Beziers)."""
    P = np.array(pts, float); m = len(P); s = [f"M{P[0][0]:.1f},{P[0][1]:.1f}"]
    for i in range(m if closed else m - 1):
        p0 = P[i - 1] if (closed or i) else P[0]; p1, p2 = P[i], P[(i + 1) % m]
        p3 = P[(i + 2) % m] if (closed or i + 2 < m) else P[-1]
        c1 = p1 + (p2 - p0) / 6; c2 = p2 - (p3 - p1) / 6
        s.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return "".join(s) + ("Z" if closed else "")

# ---- hand-drawn parts (pixel coordinates of the 1000 x 1100 plate; 1 px is about 0.29 mm) ----
SOFT_PALATE = [(632, 577), (612, 585), (598, 600), (590, 620), (587, 640), (589, 653), (595, 655), (598, 645), (603, 627),
               (615, 612), (634, 604), (662, 601), (648, 588)]
UPPER_LIP = [(798, 566), (818, 561), (834, 563), (843, 584), (848, 610), (849, 630), (846, 645), (838, 652), (826, 650), (821, 638), (819, 612), (811, 588)]
UPPER_VERMILION = [(846, 626), (849, 636), (845, 647), (838, 652), (826, 650), (822, 641), (834, 634)]
LOWER_LIP = [(838, 654), (848, 663), (850, 680), (844, 696), (831, 710), (835, 727), (838, 744), (828, 762), (806, 774), (776, 778),
             (752, 770), (762, 754), (781, 744), (786, 712), (800, 702), (806, 682), (812, 662), (824, 655)]
LOWER_VERMILION = [(838, 654), (848, 663), (850, 678), (840, 676), (826, 668), (818, 657)]
# soft tissue in front of the jaw and the face profile from nose to neck, added to the traced head outline
FACE = [(830, 560), (842, 570), (847, 600), (850, 632), (842, 652), (850, 668), (848, 692), (830, 710), (836, 728), (838, 744),
        (826, 764), (800, 776), (740, 782), (690, 784), (680, 760), (760, 700), (790, 600)]
PHARYNX_FRONT = [(598, 476), (574, 488), (558, 510), (551, 545), (550, 582), (552, 620), (550, 662), (545, 704), (538, 748), (531, 792), (525, 828)]
PHARYNX = PHARYNX_FRONT + [(p[0] - 17, p[1]) for p in reversed(PHARYNX_FRONT)]
GENIOHYOID = [(752, 733), (706, 740), (660, 746), (630, 750), (628, 760), (658, 759), (706, 753), (754, 745)]
FLOOR_ZONE = [(758, 656), (776, 660), (774, 674), (760, 688), (746, 698), (742, 686), (750, 670)]
LARYNX_TISSUE = [(596, 748), (622, 752), (634, 770), (628, 830), (618, 878), (590, 890), (560, 886), (548, 850), (556, 805), (576, 770)]
TONSIL = [(574, 652), (586, 650), (594, 662), (595, 682), (588, 698), (576, 700), (568, 686), (567, 666)]

LASSO = [(606, 474), (645, 478), (646, 572), (700, 600), (800, 603), (812, 645), (790, 662), (700, 655), (606, 700), (596, 746),
         (582, 752), (566, 790), (548, 830), (536, 860), (522, 858), (522, 826), (535, 760), (546, 650), (548, 540), (568, 492)]

def raster(pts):
    im = Image.new("L", (W, H), 0); ImageDraw.Draw(im).polygon(catmull(pts), fill=255); return np.asarray(im) > 0

def traced(a, blur=2.0, min_area=150, eps=0.7, name="_tmp"):
    tmp = MASKS.parent / f"{name}.png"; rgba = Image.new("RGBA", (W, H)); rgba.putalpha(Image.fromarray((a * 255).astype(np.uint8))); rgba.save(tmp)
    return " ".join(trace(tmp, blur=blur, min_area=min_area, eps=eps))

def airway():
    im = Image.new("L", (W, H), 0); ImageDraw.Draw(im).polygon(catmull(LASSO, n=4), fill=255)
    a = np.asarray(im) > 0
    for k in ["tongue", "genio", "palate_mid", "epiglottis_s", "mandible_mid", "upper_inc", "lower_inc", "hyoid",
              "thyroid_c", "cricoid", "arytenoid", "vertebrae", "trachea"]:
        if k == "epiglottis_s": a &= ~np.roll(mask("epiglottis"), -12, axis=1)
        else: a &= ~mask(k)
    for poly in (SOFT_PALATE, UPPER_LIP, LOWER_LIP, PHARYNX, LARYNX_TISSUE): a &= ~raster(poly)
    return traced(a, name="_airway")

def ghost():
    return traced(mask("head") | raster(FACE), blur=5, min_area=2000, eps=1.0, name="_ghost")

def fibres():
    """genioglossus: a fan of fibres from the inside of the chin up into the tongue"""
    o = np.array([742.0, 716.0]); lines = []
    for i in range(24):
        a = np.radians(112 + i * 5.0); r = 200
        e = o + r * np.array([np.cos(a), -np.sin(a)]); c = o + 0.5 * r * np.array([np.cos(a - 0.08), -np.sin(a - 0.08)])
        lines.append(f"M{o[0]:.0f},{o[1]:.0f} Q{c[0]:.0f},{c[1]:.0f} {e[0]:.0f},{e[1]:.0f}")
    return " ".join(lines)

def blob(cx, cy, rx, ry, seed, k=0.22, n=14):
    """an irregular closed shape, for lesions"""
    r = np.random.default_rng(seed); a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    f = 1 + k * (r.random(n) - 0.5) * 2
    return path([(cx + rx * f[i] * np.cos(a[i]), cy + ry * f[i] * np.sin(a[i])) for i in range(n)])

# label: (id, text, anchor point on the structure, label position, side)
LABELS = [
    ("lab-lips", "Lips", (843, 640), (875, 628), "r"),
    ("lab-tongue", "Tongue", (700, 640), (875, 572), "r"),
    ("lab-floor", "Floor of the mouth", (762, 676), (875, 700), "r"),
    ("lab-hard", "Hard palate", (720, 590), (875, 526), "r"),
    ("lab-soft", "Soft palate", (598, 612), (548, 585), "l"),
    ("lab-tonsil", "Tonsil", (578, 676), (548, 650), "l"),
    ("lab-base", "Base of the tongue", (600, 718), (548, 720), "l"),
    ("lab-wall", "Back of the throat", (546, 660), (420, 600), "l"),
    ("lab-epi", "Epiglottis", (560, 760), (420, 770), "l"),
]

def labels():
    out = []
    for i, t, (ax, ay), (lx, ly), side in LABELS:
        tx = lx + (8 if side == "r" else -8)
        out.append(f'<g id="{i}" class="lab"><path d="M{ax},{ay} L{lx},{ly}" stroke="#2a3a3c" stroke-width="1.2" fill="none"/>'
                   f'<circle cx="{ax}" cy="{ay}" r="3.2" fill="#0d7377" stroke="#fff" stroke-width="1.2"/>'
                   f'<text x="{tx}" y="{ly + 5}" font-size="15" font-weight="600" fill="#1e2b2d" style="paint-order:stroke;stroke:#f5f3f0;stroke-width:4px;stroke-linejoin:round" text-anchor="{"start" if side == "r" else "end"}">{t}</text></g>')
    return "\n".join(out)

def svg():
    A, G = airway(), ghost()
    tongue = traced(mask("tongue") | mask("genio"), blur=3, min_area=200, name="_tongue")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="'Source Sans 3', 'Source Sans Pro', system-ui, sans-serif">
<defs>
  <linearGradient id="ghostFill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fbf6f2"/><stop offset="0.72" stop-color="#f9f1ec"/><stop offset="0.93" stop-color="#f5f3f0" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="ghostEdge" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#dccdc5"/><stop offset="0.75" stop-color="#e3d6cf"/><stop offset="0.93" stop-color="#f5f3f0" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="air" cx="0.6" cy="0.4" r="0.8"><stop offset="0" stop-color="#a5434f"/><stop offset="1" stop-color="#6f2532"/></radialGradient>
  <linearGradient id="tongueFill" x1="0" y1="0" x2="0.15" y2="1"><stop offset="0" stop-color="#e58e95"/><stop offset="1" stop-color="#c9646f"/></linearGradient>
  <linearGradient id="enamel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fcfaf4"/><stop offset="1" stop-color="#e6dccb"/></linearGradient>
  <linearGradient id="wallFill" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#e09a97"/><stop offset="1" stop-color="#c7706d"/></linearGradient>
  <filter id="vol" x="-10%" y="-10%" width="120%" height="120%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="6" result="b"/>
    <feComposite in="SourceAlpha" in2="b" operator="arithmetic" k2="1" k3="-1" result="rim"/>
    <feFlood flood-color="#4a1520" flood-opacity="0.34"/><feComposite in2="rim" operator="in" result="shade"/>
    <feOffset in="b" dx="4" dy="6" result="bo"/>
    <feComposite in="SourceAlpha" in2="bo" operator="arithmetic" k2="1" k3="-1" result="lit"/>
    <feFlood flood-color="#ffffff" flood-opacity="0.30"/><feComposite in2="lit" operator="in" result="hi"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/><feMergeNode in="hi"/></feMerge>
  </filter>
  <filter id="soft" x="-10%" y="-10%" width="120%" height="120%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="3.5" result="b"/>
    <feComposite in="SourceAlpha" in2="b" operator="arithmetic" k2="1" k3="-1" result="rim"/>
    <feFlood flood-color="#5b3a2a" flood-opacity="0.2"/><feComposite in2="rim" operator="in" result="shade"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/></feMerge>
  </filter>
  <filter id="cancellous" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.12" numOctaves="2" seed="4" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.66  0 0 0 0 0.56  0 0 0 0 0.40  0 0 0 -14 6.6" result="dots"/>
    <feComposite in="dots" in2="SourceAlpha" operator="in" result="d2"/>
    <feComponentTransfer in="d2" result="d3"><feFuncA type="linear" slope="0.45"/></feComponentTransfer>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d3"/></feMerge>
  </filter>
  <filter id="papillae" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="1" seed="9" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 0.93  0 0 0 0 0.94  0 0 0 -30 8.6" result="dots"/>
    <feComposite in="dots" in2="SourceAlpha" operator="in" result="d2"/>
    <feComponentTransfer in="d2" result="d3"><feFuncA type="linear" slope="0.22"/></feComponentTransfer>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d3"/></feMerge>
  </filter>
  <filter id="leuko" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency="0.35" numOctaves="2" seed="3" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="5" result="disp"/>
    <feGaussianBlur in="disp" stdDeviation="0.6"/>
  </filter>
  <linearGradient id="fadeBottom" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f5f3f0" stop-opacity="0"/><stop offset="1" stop-color="#f5f3f0"/></linearGradient>
{lesions.LESION_DEFS}
  <clipPath id="tongueClip"><path d="{tongue}"/></clipPath>
  <clipPath id="hardPalate"><rect x="600" y="550" width="215" height="62"/></clipPath>
  <clipPath id="lipClip"><rect x="800" y="600" width="60" height="108"/></clipPath>
  <clipPath id="frontTongue"><rect x="645" y="560" width="200" height="200"/></clipPath>
  <clipPath id="backTongue"><rect x="560" y="560" width="85" height="200"/></clipPath>
</defs>
<rect id="paper" width="{W}" height="{H}" fill="#f5f3f0"/>
<g id="ghost"><path d="{G}" fill="url(#ghostFill)" stroke="url(#ghostEdge)" stroke-width="2.2"/></g>
<g id="context" stroke-width="1.1" stroke-linejoin="round">
  <path d="{d('brain')}" fill="#f2ebe8" stroke="#e3d8d3"/>
  <path d="{d('skull_mid')}" fill="#f0eadf" stroke="#ded4c2" fill-rule="evenodd"/>
  <path d="{d('backmus', 'neckmus')}" fill="#f3e6e2" stroke="#e8d7d2"/>
  <path d="{d('cord')}" fill="#f3ede7" stroke="#e3d9cf"/>
  <path d="{d('vertebrae')}" fill="#f0e9dc" stroke="#ddd2be"/>
  <path d="{d('palate_mid')}" fill="#f0e9dc" stroke="#ddd2be" fill-rule="evenodd"/>
  <path d="{d('concha')}" fill="#f2dfdc" stroke="#e5ccc8"/>
  <path d="{d('thyroid_g')}" fill="#f3e7d8" stroke="#e8d7c1"/>
</g>
<g id="airway"><path d="{A}" fill="url(#air)" filter="url(#vol)" fill-rule="evenodd"/></g>
<g id="mouth" stroke-linejoin="round">
  <path id="tonsil" d="{path(TONSIL)}" fill="#c4627a" stroke="#8a3a4c" stroke-width="1.3" filter="url(#vol)"/>
  <path id="wall" d="{path(PHARYNX)}" fill="url(#wallFill)" stroke="#9c514c" stroke-width="1.3" filter="url(#soft)"/>
  <path id="trachea" d="{d('trachea', 'oesophagus')}" fill="#e6b2b0" stroke="#ad6d6b" stroke-width="1.2" filter="url(#soft)"/>
  <path id="larynxTissue" d="{path(LARYNX_TISSUE)}" fill="#eecbc4" stroke="#d3a59c" stroke-width="1"/>
  <path id="larynx" d="{d('thyroid_c', 'cricoid', 'arytenoid')}" fill="#c2d6e4" stroke="#6f8ea6" stroke-width="1.3" filter="url(#soft)"/>
  <path id="epiglottis" transform="translate(-12,0)" d="{d('epiglottis')}" fill="#c2d6e4" stroke="#6f8ea6" stroke-width="1.3" filter="url(#soft)"/>
  <path id="hyoid" d="{d('hyoid')}" fill="#f2e8d2" stroke="#a8946f" stroke-width="1.3" filter="url(#cancellous)"/>
  <g id="tongue">
    <path d="{tongue}" fill="url(#tongueFill)" stroke="#963f4d" stroke-width="1.5" filter="url(#papillae)"/>
    <path d="{fibres()}" fill="none" stroke="#b44f5b" stroke-opacity="0.28" stroke-width="1" clip-path="url(#tongueClip)"/>
  </g>
  {lesions.lump("lesion-base", 588, 712, 15, 22, 37, rot=0.15, color=("#c9707c", "#9f4a5c"))}
  <path id="floor" d="{path(GENIOHYOID)}" fill="#d38279" stroke="#934a43" stroke-width="1.2" filter="url(#soft)"/>
  <path id="mandible" d="{d('mandible_mid')}" fill="#f2e8d2" stroke="#a8946f" stroke-width="1.3" filter="url(#cancellous)"/>
  {lesions.lump("lesion-floor", 756, 683, 15, 10, 31, rot=-0.6, color=("#ead0ca", "#c47079"))}
  <path id="hardpalate" d="{d('palate_mid')}" clip-path="url(#hardPalate)" fill="#f2e8d2" stroke="#a8946f" stroke-width="1.3" filter="url(#cancellous)" fill-rule="evenodd"/>
  <path id="softpalate" d="{path(SOFT_PALATE)}" fill="#d9838b" stroke="#934353" stroke-width="1.4" filter="url(#vol)"/>
  <path id="teeth" d="{d('upper_inc')} {d('lower_inc')}" fill="url(#enamel)" stroke="#a3967f" stroke-width="1.2" filter="url(#soft)"/>
  <g id="lips">
    <path d="{path(UPPER_LIP)}" fill="#efcdc2" stroke="#b98378" stroke-width="1.2" filter="url(#soft)"/>
    <path d="{path(LOWER_LIP)}" fill="#efcdc2" stroke="#b98378" stroke-width="1.2" filter="url(#soft)"/>
    <path d="{path(UPPER_VERMILION)} {path(LOWER_VERMILION)}" fill="#cf6f73" opacity="0.85"/>
  </g>
</g>
<rect id="fade" x="0" y="900" width="{W}" height="200" fill="url(#fadeBottom)"/>
<g id="zones" fill="#3cc3c3" fill-opacity="0.62" stroke="#0d7377" stroke-width="1.6" opacity="0">
  <path id="zone-tongue" d="{tongue}" clip-path="url(#frontTongue)"/>
  <path id="zone-base" d="{tongue}" clip-path="url(#backTongue)"/>
  <path id="zone-floor" d="{path(FLOOR_ZONE)}"/>
  <path id="zone-soft" d="{path(SOFT_PALATE)}"/>
  <path id="zone-tonsil" d="{path(TONSIL)}"/>
  <path id="zone-lips" d="{path(UPPER_VERMILION)} {path(LOWER_VERMILION)}"/>
</g>
<g id="labels" opacity="0">
{labels()}
</g>
</svg>'''

if __name__ == "__main__":
    PATHS, MASKS, OUT = json.load(open(sys.argv[1])), Path(sys.argv[2]), Path(sys.argv[3])
    OUT.write_text(svg()); print(OUT)
