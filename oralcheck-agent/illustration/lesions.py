"""Lesion drawings for the plates, matched to openly licensed clinical photos.

Each function returns an SVG <g> (hidden by default, so a page or reel switches it
on) and needs LESION_DEFS in the plate's <defs>. Coordinates are plate units;
light comes from the upper left, as on the plates. References for each drawing
are listed in docs/MODEL_REVIEW.md, section 5.
"""
import math
import numpy as np

def organic(cx, cy, rx, ry, seed, wobble=0.18, rot=0.0, n=48, harmonics=(2, 3, 5, 7)):
    """A smooth irregular outline: an ellipse whose radius wanders with a few low harmonics."""
    r = np.random.default_rng(seed); amps = r.uniform(0.3, 1.0, len(harmonics)); ph = r.uniform(0, 2 * math.pi, len(harmonics))
    amps = amps / amps.sum() * wobble
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + sum(A * math.sin(h * a + p) for A, h, p in zip(amps, harmonics, ph))
        x, y = rx * k * math.cos(a), ry * k * math.sin(a)
        c, s = math.cos(rot), math.sin(rot)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts

def smooth(pts, closed=True):
    P = np.array(pts, float); m = len(P); s = [f"M{P[0][0]:.1f},{P[0][1]:.1f}"]
    for i in range(m if closed else m - 1):
        p0 = P[i - 1] if (closed or i) else P[0]; p1, p2 = P[i], P[(i + 1) % m]
        p3 = P[(i + 2) % m] if (closed or i + 2 < m) else P[-1]
        c1 = p1 + (p2 - p0) / 6; c2 = p2 - (p3 - p1) / 6
        s.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return "".join(s) + ("Z" if closed else "")

def inside(pts, x, y):
    """point in polygon"""
    c = False; n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1: c = not c
    return c

def scatter(poly, count, seed, margin=0.0):
    r = np.random.default_rng(seed); xs, ys = zip(*poly); out = []
    while len(out) < count:
        x, y = r.uniform(min(xs), max(xs)), r.uniform(min(ys), max(ys))
        if inside(poly, x, y): out.append((x, y))
    return out

LESION_DEFS = """
  <filter id="lzFeather" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.2"/></filter>
  <filter id="lzSoft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="0.9"/></filter>
  <filter id="lzSoftWide" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6"/></filter>
  <filter id="lzMottle" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="3" seed="11" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 2.4 -0.55" result="m"/>
    <feComposite in="SourceGraphic" in2="m" operator="in" result="patchy"/>
    <feGaussianBlur in="patchy" stdDeviation="1.1"/>
  </filter>
  <filter id="lzGrain" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" seed="5" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.02  0 0 0 0 0.08  0 0 0 -2.2 1.3" result="dots"/>
    <feComposite in="dots" in2="SourceAlpha" operator="in" result="d"/>
    <feComponentTransfer in="d" result="d2"><feFuncA type="linear" slope="0.5"/></feComponentTransfer>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d2"/></feMerge>
  </filter>
  <filter id="lzRim" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="b"/>
    <feOffset in="b" dx="-3" dy="-4" result="bo"/>
    <feComposite in="SourceAlpha" in2="bo" operator="arithmetic" k2="1" k3="-1" result="lower"/>
    <feFlood flood-color="#6e2430" flood-opacity="0.45"/><feComposite in2="lower" operator="in" result="shade"/>
    <feOffset in="b" dx="3" dy="4" result="bo2"/>
    <feComposite in="SourceAlpha" in2="bo2" operator="arithmetic" k2="1" k3="-1" result="upper"/>
    <feFlood flood-color="#ffffff" flood-opacity="0.55"/><feComposite in2="upper" operator="in" result="hi"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/><feMergeNode in="hi"/></feMerge>
  </filter>
  <filter id="lzCrater" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="b"/>
    <feOffset in="b" dx="3" dy="4" result="bo"/>
    <feComposite in="SourceAlpha" in2="bo" operator="arithmetic" k2="1" k3="-1" result="upperInside"/>
    <feFlood flood-color="#5a1822" flood-opacity="0.5"/><feComposite in2="upperInside" operator="in" result="shade"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/></feMerge>
  </filter>
"""

def highlights(spots):
    """small wet glints, the way a mucosa photo shows them"""
    return "".join(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#ffffff" opacity="{o}" transform="rotate(-25 {x:.1f} {y:.1f})"/>'
                   for x, y, rx, ry, o in spots)

def leukoplakia(gid, cx, cy, rx, ry, seed=21, rot=0.0, clip=None):
    """White patch: filmy to dense white, cloudy, the pink showing through in places, a feathered irregular
    edge, faint crinkles, still wet. Matched to File:Severe_dysplasia.jpg (side of tongue) and
    File:NIH_DOC_16_HomogenousLeukoplakia.jpg (homogeneous, crinkled)."""
    poly = organic(cx, cy, rx, ry, seed, 0.24, rot, harmonics=(2, 3, 5, 9))
    core = organic(cx + rx * 0.06, cy - ry * 0.04, rx * 0.62, ry * 0.66, seed + 1, 0.3, rot, harmonics=(2, 4, 7))
    r = np.random.default_rng(seed)
    crinkles = []
    for _ in range(16):                                  # short wandering crinkles in random directions
        x, y = scatter([*core], 1, int(r.integers(1e6)))[0]; a = r.uniform(0, math.pi); L = r.uniform(5, 13)
        pts = [(x + math.cos(a) * L * t + r.uniform(-1.2, 1.2), y + math.sin(a) * L * t + r.uniform(-1.2, 1.2)) for t in (-1, -0.4, 0.3, 1)]
        crinkles.append(smooth(pts, closed=False))
    streaks = [organic(cx + rx * dx, cy + ry * dy, rx * 0.16, ry * 0.32, seed + 7 + i, 0.3, rot + 0.15) for i, (dx, dy) in enumerate([(-0.2, -0.25), (0.15, 0.2)])]
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return f'''<g id="{gid}" opacity="0"{cp}>
  <path d="{smooth(poly)}" fill="#efe4e1" opacity="0.5" filter="url(#lzFeather)"/>
  <path d="{smooth(poly)}" fill="#f1e9e5" opacity="0.7" filter="url(#lzMottle)"/>
  <path d="{smooth(core)}" fill="#f8f4f0" opacity="0.7" filter="url(#lzMottle)"/>
  <g fill="#fbf9f6" opacity="0.65" filter="url(#lzSoft)">{"".join(f'<path d="{smooth(st)}"/>' for st in streaks)}</g>
  <g fill="none" stroke="#d6c4bf" stroke-width="0.9" stroke-linecap="round" opacity="0.6">{"".join(f'<path d="{c}"/>' for c in crinkles)}</g>
  {highlights([(cx - rx * 0.3, cy - ry * 0.35, 3.0, 1.3, 0.75), (cx + rx * 0.2, cy - ry * 0.05, 2.0, 0.9, 0.6), (cx - rx * 0.1, cy + ry * 0.42, 1.6, 0.8, 0.55)])}
</g>'''

def erythroplakia(gid, cx, cy, rx, ry, seed=7, rot=0.0, clip=None):
    """Red patch: bright red, velvety, flat, with an edge that is clear but not outlined.
    No openly licensed photo exists; matched to the description in PMC9065478 and CRUK's (view-only) pictures."""
    poly = organic(cx, cy, rx, ry, seed, 0.22, rot, harmonics=(2, 3, 5, 8))
    r = np.random.default_rng(seed + 5)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r.uniform(0.4, 0.9):.2f}"/>'
                   for x, y in scatter(organic(cx, cy, rx * 0.9, ry * 0.9, seed, 0.22, rot, harmonics=(2, 3, 5, 8)), 160, seed))
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return f'''<g id="{gid}" opacity="0"{cp}>
  <path d="{smooth(organic(cx, cy, rx * 1.25, ry * 1.2, seed + 1, 0.2, rot))}" fill="#d0505e" opacity="0.35" filter="url(#lzFeather)"/>
  <g filter="url(#lzSoft)"><path d="{smooth(poly)}" fill="#c63848" opacity="0.7" filter="url(#lzGrain)"/></g>
  <g fill="#a82536" opacity="0.28" filter="url(#lzSoft)">{dots}</g>
  {highlights([(cx - rx * 0.3, cy - ry * 0.4, 1.6, 0.8, 0.35)])}
</g>'''

def speckled(gid, cx, cy, rx, ry, seed=19, rot=0.0, clip=None):
    """Speckled (erythroleukoplakia): a red patch scattered with small irregular white flecks.
    Matched to File:NIH_DOC_19_Erythroleukoplakia.jpg and File:Eritro.jpg."""
    poly = organic(cx, cy, rx, ry, seed, 0.32, rot, harmonics=(2, 3, 5, 9))
    flecks = scatter(organic(cx, cy, rx * 0.85, ry * 0.85, seed, 0.32, rot, harmonics=(2, 3, 5, 9)), 110, seed)
    r = np.random.default_rng(seed + 3)
    fl = "".join(f'<path d="{smooth(organic(x, y, s, s * r.uniform(0.6, 1.2), int(r.integers(1e6)), 0.35, r.uniform(0, 3)))}"/>'
                 for x, y in flecks for s in [r.uniform(0.8, 3.2)])
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return f'''<g id="{gid}" opacity="0"{cp}>
  <path d="{smooth(poly)}" fill="#c4414f" opacity="0.55" filter="url(#lzFeather)"/>
  <g filter="url(#lzSoft)"><path d="{smooth(poly)}" fill="#bd3a49" opacity="0.75" filter="url(#lzGrain)"/></g>
  <g fill="#f6f1ea" opacity="0.8" filter="url(#lzSoft)">{fl}</g>
  {highlights([(cx - rx * 0.25, cy - ry * 0.35, 2.2, 1.0, 0.6)])}
</g>'''

def ulcer(gid, cx, cy, rx, ry, seed=4, rot=0.0, clip=None):
    """A sore that does not heal (ulcerated carcinoma): an irregular raw red base with yellow-white slough,
    edged by a raised, firm, pale and patchy rim that blends into reddened, whitish tissue around it.
    Matched to File:Carcinomatongue.jpg, and drawn unlike a canker sore (File:Aphthous_stomatitisNZ.jpg:
    small, round, shallow, a clean yellow-grey base and a thin red halo)."""
    halo = organic(cx, cy, rx * 1.7, ry * 1.6, seed, 0.2, rot)
    rim = organic(cx, cy, rx * 1.12, ry * 1.1, seed + 1, 0.32, rot, harmonics=(2, 3, 4, 7, 11))
    base = organic(cx + 1, cy + 1, rx * 0.8, ry * 0.74, seed + 2, 0.3, rot, harmonics=(2, 3, 6, 9))
    r = np.random.default_rng(seed)
    slough = [organic(cx + dx * rx, cy + dy * ry, rx * s, ry * s * 0.75, seed + 5 + i, 0.4, rot)
              for i, (dx, dy, s) in enumerate([(-0.2, -0.15, 0.36), (0.3, 0.1, 0.24), (0.0, 0.32, 0.18), (-0.38, 0.25, 0.12)])]
    pale = [organic(*p, int(r.integers(1e6)), 0.4) for p in [(cx - rx * 1.1, cy - ry * 0.6, rx * 0.35, ry * 0.25), (cx + rx * 0.9, cy + ry * 0.8, rx * 0.4, ry * 0.22), (cx + rx * 0.7, cy - ry * 0.95, rx * 0.3, ry * 0.18)]]
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return f'''<g id="{gid}" opacity="0"{cp}>
  <path d="{smooth(halo)}" fill="#c84f5d" opacity="0.45" filter="url(#lzFeather)"/>
  <g fill="#efe3df" opacity="0.6" filter="url(#lzFeather)">{"".join(f'<path d="{smooth(p)}"/>' for p in pale)}</g>
  <path d="{smooth(rim)}" fill="#dfb0b2" filter="url(#lzRim)"/>
  <path d="{smooth(rim)}" fill="#f1e2df" opacity="0.55" filter="url(#lzMottle)"/>
  <path d="{smooth(base)}" fill="#b13849" filter="url(#lzCrater)"/>
  <path d="{smooth(base)}" fill="#9e2a3b" opacity="0.5" filter="url(#lzGrain)"/>
  <g fill="#e8dcae" opacity="0.92" filter="url(#lzSoft)">{"".join(f'<path d="{smooth(sl)}"/>' for sl in slough)}</g>
  {highlights([(cx - rx * 0.6, cy - ry * 0.75, 2.8, 1.2, 0.75), (cx + rx * 0.15, cy - ry * 0.1, 1.8, 0.8, 0.55), (cx + rx * 0.5, cy + ry * 0.4, 1.4, 0.7, 0.5)])}
</g>'''

def canker(gid, cx, cy, rx, ry, seed=41, rot=0.0, clip=None):
    """A canker sore (aphthous ulcer), the everyday look-alike: small, round or oval, shallow, a clean
    yellow-grey base and a thin red halo, with a neat edge. Matched to File:Aphthous_stomatitisNZ.jpg and the
    site's own description (round or oval, white or yellow center, red rim). Added 26 Oct for the
    day-by-day reel, where it heals and the sore beside it does not."""
    halo = organic(cx, cy, rx * 1.55, ry * 1.55, seed, 0.06, rot, harmonics=(2, 3))
    ring = organic(cx, cy, rx * 1.12, ry * 1.12, seed + 1, 0.05, rot, harmonics=(2, 3))
    base = organic(cx, cy, rx, ry, seed + 2, 0.05, rot, harmonics=(2, 3))
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return f'''<g id="{gid}" opacity="0"{cp}>
  <path d="{smooth(halo)}" fill="#d0525f" opacity="0.55" filter="url(#lzFeather)"/>
  <path d="{smooth(ring)}" fill="#c43e4f" opacity="0.9" filter="url(#lzSoft)"/>
  <path d="{smooth(base)}" fill="#e9dcb8" filter="url(#lzCrater)"/>
  <path d="{smooth(organic(cx, cy + ry * 0.1, rx * 0.7, ry * 0.6, seed + 3, 0.08, rot))}" fill="#d9c99b" opacity="0.6" filter="url(#lzSoft)"/>
  {highlights([(cx - rx * 0.35, cy - ry * 0.4, 2.0, 0.9, 0.7)])}
</g>'''

def lump(gid, cx, cy, rx, ry, seed=13, rot=0.0, clip=None, color=("#c96579", "#a5455b")):
    """A lump: a firm, lobulated swelling, here an enlarged uneven tonsil, with a small ulcer and fine vessels.
    Matched to the OCF and NCI PDQ descriptions (no open photo of a tonsil tumour was found)."""
    poly = organic(cx, cy, rx, ry, seed, 0.14, rot, harmonics=(3, 4, 6))
    lobes = [organic(cx + dx * rx, cy + dy * ry, rx * s, ry * s, seed + i, 0.18, rot) for i, (dx, dy, s) in enumerate([(-0.3, -0.35, 0.42), (0.25, 0.1, 0.48), (-0.2, 0.42, 0.38)])]
    r = np.random.default_rng(seed)
    vessels = []
    for _ in range(3):
        x0, y0 = cx + rx * r.uniform(-0.5, 0.4), cy + ry * r.uniform(-0.5, 0.4); a = r.uniform(0, math.pi)
        vessels.append(smooth([(x0 + math.cos(a) * rx * 0.25 * t + r.uniform(-1, 1), y0 + math.sin(a) * ry * 0.18 * t + r.uniform(-1, 1)) for t in (0, 0.5, 1, 1.5)], closed=False))
    cp = f' clip-path="url(#{clip})"' if clip else ""
    gid_g = f"{gid}-g"
    return f'''<g id="{gid}" opacity="0"{cp}>
  <radialGradient id="{gid_g}" cx="0.38" cy="0.32" r="0.75"><stop offset="0" stop-color="{color[0]}"/><stop offset="1" stop-color="{color[1]}"/></radialGradient>
  <path d="{smooth(poly)}" fill="url(#{gid_g})" stroke="#7d3343" stroke-width="1.3" filter="url(#lzRim)"/>
  <g fill="#d27a8b" opacity="0.35" filter="url(#lzSoft)">{"".join(f'<path d="{smooth(l)}"/>' for l in lobes)}</g>
  <g fill="none" stroke="#8a2d45" stroke-width="0.7" opacity="0.35">{"".join(f'<path d="{v}"/>' for v in vessels)}</g>
  <path d="{smooth(organic(cx + rx * 0.2, cy + ry * 0.15, rx * 0.2, ry * 0.11, seed + 9, 0.18, 0.4, harmonics=(2, 3)))}" fill="#e3d4ae" stroke="#9a4a52" stroke-width="0.7" opacity="0.9"/>
  {highlights([(cx - rx * 0.35, cy - ry * 0.45, 3.0, 1.4, 0.7)])}
</g>'''

def lichen_planus(gid, cx, cy, rx, ry, seed=3, rot=0.0, clip=None):
    """Lichen planus (a look-alike, and itself a condition to have checked): a lacy web of fine white lines
    (Wickham striae) on reddened cheek lining, usually on both sides. Matched to File:Lichen_planus.jpg."""
    r = np.random.default_rng(seed); region = organic(cx, cy, rx, ry, seed, 0.15, rot)
    rows, lines = [], []
    for k in range(9):                                # long wavy striae running down the cheek
        x0 = cx - rx * 0.8 + k * rx * 1.6 / 8 + r.uniform(-4, 4); ph = r.uniform(0, 6.3); amp = r.uniform(4, 9)
        row = [(x0 + amp * math.sin(ph + t * 0.06) + r.uniform(-1.5, 1.5), cy - ry + t) for t in range(0, int(2 * ry) + 1, 12)]
        row = [p for p in row if inside(region, *p)]
        rows.append(row)
        if len(row) > 2: lines.append(smooth(row, closed=False))
    for a_, b_ in zip(rows, rows[1:]):                # short curved bridges between neighbours: the lace
        for i in range(0, min(len(a_), len(b_)) - 1):
            if r.random() > 0.3: continue
            (x1, y1), (x2, y2) = a_[i], b_[i + int(r.integers(0, 2))]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + r.uniform(-9, 9)
            lines.append(f"M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} {x2:.1f},{y2:.1f}")
    paths = "".join(f'<path d="{l}"/>' for l in lines)
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return f'''<g id="{gid}" opacity="0"{cp}>
  <path d="{smooth(region)}" fill="#c9505d" opacity="0.4" filter="url(#lzFeather)"/>
  <g fill="none" stroke="#f3ebe6" stroke-width="9" stroke-linecap="round" opacity="0.3" filter="url(#lzFeather)">{paths}</g>
  <g fill="none" stroke="#f8f2ee" stroke-width="2.2" stroke-linecap="round" opacity="0.72" filter="url(#lzSoft)">{paths}</g>
</g>'''

def lip_sore(gid, cx, cy, rx, ry, seed=17, rot=0.0, clip=None):
    """Lower-lip change from sun: a pale, scaly, blurred border along the lip with a crusted sore that does
    not heal. Matched to File:Left_lower_lip_cancer.jpg and File:Actinic_Cheilitis_Photo.jpg."""
    band = organic(cx - rx * 0.9, cy + ry * 0.6, rx * 3.4, ry * 1.1, seed, 0.12, rot, harmonics=(3, 5, 8))
    crust = organic(cx, cy, rx, ry, seed + 1, 0.3, rot)
    crust_in = organic(cx + 1, cy, rx * 0.55, ry * 0.5, seed + 2, 0.35, rot)
    scales = scatter(band, 46, seed)
    r = np.random.default_rng(seed)
    sc = "".join(f'<path d="{smooth(organic(x, y, r.uniform(1.5, 3.8), r.uniform(0.7, 1.6), int(r.integers(1e6)), 0.45, r.uniform(-0.3, 0.3), n=10, harmonics=(2, 3, 4)))}"/>' for x, y in scales)
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return f'''<g id="{gid}" opacity="0"{cp}>
  <path d="{smooth(band)}" fill="#efe2dc" opacity="0.55" filter="url(#lzFeather)"/>
  <g fill="#f7f1ec" opacity="0.75" filter="url(#lzSoft)">{sc}</g>
  <path d="{smooth(organic(cx, cy, rx * 1.4, ry * 1.5, seed + 3, 0.15))}" fill="#c4505a" opacity="0.45" filter="url(#lzFeather)"/>
  <path d="{smooth(crust)}" fill="#9a5038" filter="url(#lzRim)"/>
  <path d="{smooth(crust_in)}" fill="#6e2f26" opacity="0.85" filter="url(#lzSoft)"/>
  <path d="{smooth(organic(cx - rx * 0.35, cy - ry * 0.2, rx * 0.3, ry * 0.2, seed + 4, 0.3))}" fill="#e8dccb" opacity="0.85"/>
</g>'''


def thrush(gid, cx, cy, rx, ry, seed=29, rot=0.0, clip=None):
    """Oral thrush (candidiasis), the white patch that is NOT a warning sign on its own: creamy white,
    slightly raised, curd-like spots scattered over a reddened surface, one wiped away to show the raw red
    underneath (it wipes off, a leukoplakia does not). Drawn from the CDC's description ("Candida infections
    of the mouth, throat, and esophagus": white patches that can be wiped away, leaving redness), not matched
    to a photo like the others; worth a clinician's look with the rest of the set."""
    r = np.random.default_rng(seed)
    base = organic(cx, cy, rx, ry, seed, 0.2, rot)
    spots = []
    for x, y in scatter(base, 13, seed + 1, 0.0):
        k = r.uniform(0.6, 1.25)
        spots.append(organic(x, y, 9 * k, 6.5 * k, int(r.integers(1e6)), 0.32, r.uniform(0, math.pi), n=24))
    wiped = organic(cx + rx * 0.35, cy + ry * 0.3, 11, 8, seed + 5, 0.3, 0.4, n=24)
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return f'''<g id="{gid}" opacity="0"{cp}>
  <path d="{smooth(base)}" fill="#d9707a" opacity="0.38" filter="url(#lzFeather)"/>
  <path d="{smooth(wiped)}" fill="#c3404f" opacity="0.75" filter="url(#lzSoft)"/>
  <g fill="#f7f1e4" stroke="#e2d6c4" stroke-width="0.6" filter="url(#lzRim)">{"".join(f'<path d="{smooth(sp)}"/>' for sp in spots)}</g>
  <g fill="#fffdf7" opacity="0.7">{"".join(f'<ellipse cx="{sp[0][0] - 3:.1f}" cy="{sp[0][1] - 2:.1f}" rx="2.2" ry="1.1"/>' for sp in spots[::3])}</g>
</g>'''

