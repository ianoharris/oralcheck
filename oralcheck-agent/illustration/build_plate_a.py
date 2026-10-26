"""Plate A: the open mouth from the front ("say ahh"), with no face around it.

python build_plate_a.py front_dir out.svg
The teeth, gums, tongue, soft palate and tonsils are traced from the atlas's
visible regions in this view (an id render from render_plate.py, so what is in
front of what is the atlas's). The lips, the uvula, the pillars of the fauces,
the cheeks and the back wall of the throat are drawn by hand: the atlas has
flat sheets for the cheeks and the throat wall and a stub for a uvula.
Lesions are separate groups so each can be switched on alone.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from tracer import trace
from build_plate_b import path, blob
import lesions

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
W = H = 1000
ids = np.asarray(Image.open(SRC / "ids.png").convert("RGBA")); LEG = json.load(open(SRC / "ids.json"))
rgb = (ids[:, :, 0].astype(int) << 16) | (ids[:, :, 1].astype(int) << 8) | ids[:, :, 2]; vis = ids[:, :, 3] > 0

def region(pattern_fn, blur=1.6, min_area=60, eps=0.6, grow=0):
    m = np.zeros((H, W), bool)
    for n, h in LEG.items():
        if pattern_fn(n): m |= (rgb == int(h[1:], 16)) & vis
    tmp = SRC / "_r.png"; im = Image.new("RGBA", (W, H)); im.putalpha(Image.fromarray((m * 255).astype(np.uint8))); im.save(tmp)
    return trace(tmp, blur=blur, min_area=min_area, eps=eps, grow=grow)

TOOTH = ("incisor", "canine", "premolar", "molar")
teeth_up = [p for n in LEG if n.startswith("Upper") and any(t in n for t in TOOTH) for p in region(lambda x, n=n: x == n, blur=1.2, min_area=40)]
def top(n): ys = np.nonzero((rgb == int(LEG[n][1:], 16)) & vis)[0]; return ys.min() if len(ys) else 0
# back teeth whose crowns poke up past the tongue in this view are left out (they read as spikes)
teeth_lo = [p for n in LEG if n.startswith("Lower") and any(t in n for t in TOOTH) and top(n) > 730 for p in region(lambda x, n=n: x == n, blur=1.2, min_area=40)]
TONGUE = " ".join(region(lambda n: n == "Tongue", blur=2.5))
GUM_UP = " ".join(region(lambda n: n == "Upper gingiva", blur=2))
GUM_LO = " ".join(region(lambda n: n == "Lower gingiva", blur=2))
SOFT = " ".join(region(lambda n: n in ("Soft palate", "Soft palate mucosa"), blur=2.5))
TONSIL_R = " ".join(region(lambda n: n == "Palatine tonsil.r", blur=2))   # viewer's left
TONSIL_L = " ".join(region(lambda n: n == "Palatine tonsil.l", blur=2))

def mirror(pts): return [(W - x, y) for x, y in pts]
# hand-drawn parts, viewer's left side; the right is mirrored
UVULA = [(474, 372), (526, 372), (527, 405), (524, 440), (517, 466), (500, 480), (483, 466), (476, 440), (473, 405)]
SOFT_HAND = [(300, 280), (700, 280), (690, 330), (648, 360), (600, 380), (552, 384), (526, 384), (500, 380), (474, 384), (448, 384), (400, 380), (352, 360), (310, 330)]
TONSIL_HAND = [(338, 420), (356, 428), (366, 456), (368, 492), (360, 528), (344, 540), (328, 528), (320, 492), (322, 452)]
ANT_PILLAR = [(300, 330), (352, 360), (330, 400), (314, 460), (310, 530), (318, 600), (336, 660), (318, 670), (294, 610), (286, 530), (288, 450), (294, 380)]
WALL = [(392, 372), (608, 372), (612, 470), (604, 560), (590, 600), (410, 600), (396, 560), (388, 470)]
POST_PILLAR = [(452, 382), (430, 392), (412, 420), (402, 466), (398, 524), (402, 590), (410, 640), (388, 650), (376, 600), (372, 524),
               (376, 456), (388, 410), (412, 384)]
CHEEK = [(160, 300), (260, 302), (300, 330), (292, 380), (282, 450), (278, 530), (284, 610), (300, 680), (280, 730), (220, 740),
         (170, 700), (140, 560), (140, 420)]
LIP_OUTER = [(500, 104), (560, 92), (650, 104), (760, 150), (850, 260), (896, 420), (906, 530), (892, 660), (840, 820), (740, 935),
             (600, 982), (500, 990), (400, 982), (260, 935), (160, 820), (108, 660), (94, 530), (104, 420), (150, 260), (240, 150),
             (350, 104), (440, 92)]
LIP_INNER = [(500, 196), (610, 192), (720, 208), (800, 262), (846, 380), (858, 530), (846, 680), (800, 810), (700, 868), (580, 884),
             (500, 886), (420, 884), (300, 868), (200, 810), (154, 680), (142, 530), (154, 380), (200, 262), (280, 208), (390, 192)]
TONGUE_GROOVE = "M500,505 C499,560 500,640 501,720"

def lesion_groups():
    """the lesions, each drawn to its reference photos (lesions.py) and set at its own depth in the
    drawing (a tonsil lump behind the pillar, a lip sore on the lip); one is switched on at a time"""
    L = lesions
    lichen = lambda gid, x, seed, clip: L.lichen_planus(gid, x, 470, 50, 120, seed, clip=clip).replace('opacity="0"', "", 1)
    return {
        "white": L.leukoplakia("lesion-white", 386, 640, 26, 62, 21, rot=0.06, clip="tongueOnly"),     # side of the tongue, patient's right
        "red": L.erythroplakia("lesion-red", 640, 572, 24, 30, 7, rot=0.4, clip="tongueOnly"),        # side and back of the tongue, patient's left
        "ulcer": L.ulcer("lesion-ulcer", 608, 694, 34, 25, 4, rot=-0.35, clip="tongueOnly"),           # side of the tongue, patient's left
        "lump": L.lump("lesion-lump", 340, 482, 38, 66, 13),                                         # one tonsil swollen and uneven
        "lip": L.lip_sore("lesion-lip", 640, 934, 28, 13, 17),                                       # lower lip, sun damage
        "speckled": L.speckled("lesion-speckled", 214, 600, 40, 54, 19, rot=0.15, clip="cheekL"),     # inside of the cheek near the corner
        "lichen": '<g id="lesion-lichen" opacity="0">' + lichen("lichen-l", 214, 3, "cheekL") + lichen("lichen-r", 786, 8, "cheekR") + "</g>",
        "thrush": L.thrush("lesion-thrush", 500, 600, 78, 92, 29, clip="tongueOnly"),                 # look-alike: wipes away (added 26 Oct)
        "whitecheek": L.leukoplakia("lesion-whitecheek", 220, 600, 20, 46, 23, rot=0.12, clip="cheekL"),   # inside of the cheek (added 26 Oct)
        "redcheek": L.erythroplakia("lesion-redcheek", 220, 600, 20, 26, 9, rot=0.3, clip="cheekL"),
        "canker": L.canker("lesion-canker", 392, 694, 15, 11, 41, rot=0.3, clip="tongueOnly"),          # look-alike: heals in 7 to 14 days (added 26 Oct)
    }

# (id, text, anchor, label position, side)
LABELS = [
    ("lab-tongue-side", "Side of the tongue", (368, 640), (122, 640), "l"),
    ("lab-tonsil", "Tonsil", (344, 480), (40, 470), "l"),
    ("lab-cheek", "Inside of the cheek", (215, 560), (40, 560), "l"),
    ("lab-gums", "Gums", (232, 800), (40, 860), "l"),
    ("lab-uvula", "Uvula", (500, 455), (960, 380), "r"),
    ("lab-soft", "Soft palate", (604, 392), (960, 300), "r"),
    ("lab-wall", "Back of the throat", (548, 432), (960, 470), "r"),
    ("lab-lip", "Lips", (760, 920), (960, 900), "r"),
]
def labels():
    out = []
    for i, t, (ax, ay), (lx, ly), side in LABELS:
        out.append(f'<g id="{i}"><path d="M{ax},{ay} L{lx + (150 if side == "l" else -150)},{ly} L{lx},{ly}" stroke="#2a3a3c" stroke-width="1.3" fill="none" opacity="0"/>'
                   f'<circle cx="{ax}" cy="{ay}" r="4" fill="#0d7377" stroke="#fff" stroke-width="1.5"/>'
                   f'<text x="{lx}" y="{ly - 8}" font-size="22" font-weight="600" fill="#1e2b2d" style="paint-order:stroke;stroke:#f5f3f0;stroke-width:5px;stroke-linejoin:round" text-anchor="{"start" if side == "l" else "end"}">{t}</text>'
                   f'<path d="M{ax},{ay} L{lx + (150 if side == "l" else -150)},{ly} L{lx},{ly}" stroke="#2a3a3c" stroke-width="1.3" fill="none"/></g>')
    return "\n".join(out)

def svg():
    LZ = lesion_groups()
    teeth = lambda ps, gid: "\n".join(f'<path d="{p}"/>' for p in ps)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="'Source Sans 3', 'Source Sans Pro', system-ui, sans-serif">
<defs>
  <radialGradient id="cavity" cx="0.5" cy="0.48" r="0.6"><stop offset="0" stop-color="#5e1a28"/><stop offset="1" stop-color="#83303d"/></radialGradient>
  <linearGradient id="wallG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a94b55"/><stop offset="0.5" stop-color="#d5848a"/><stop offset="1" stop-color="#a94b55"/></linearGradient>
  <linearGradient id="softG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9a2a6"/><stop offset="1" stop-color="#d27980"/></linearGradient>
  <radialGradient id="tongueA" cx="0.5" cy="0.3" r="0.8"><stop offset="0" stop-color="#ea9aa0"/><stop offset="0.7" stop-color="#d9777f"/><stop offset="1" stop-color="#bb5b65"/></radialGradient>
  <linearGradient id="cheekG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e0959a"/><stop offset="1" stop-color="#b9606a"/></linearGradient>
  <linearGradient id="gumG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eba6a2"/><stop offset="1" stop-color="#df8f8d"/></linearGradient>
  <linearGradient id="enamelA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f1ebde"/><stop offset="0.6" stop-color="#fbf8f2"/><stop offset="1" stop-color="#ebe3d3"/></linearGradient>
  <linearGradient id="lipG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d98184"/><stop offset="0.5" stop-color="#cc6d72"/><stop offset="1" stop-color="#d47b7f"/></linearGradient>
  <filter id="vol" x="-10%" y="-10%" width="120%" height="120%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="7" result="b"/>
    <feComposite in="SourceAlpha" in2="b" operator="arithmetic" k2="1" k3="-1" result="rim"/>
    <feFlood flood-color="#4a1520" flood-opacity="0.32"/><feComposite in2="rim" operator="in" result="shade"/>
    <feOffset in="b" dx="4" dy="7" result="bo"/>
    <feComposite in="SourceAlpha" in2="bo" operator="arithmetic" k2="1" k3="-1" result="lit"/>
    <feFlood flood-color="#ffffff" flood-opacity="0.32"/><feComposite in2="lit" operator="in" result="hi"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/><feMergeNode in="hi"/></feMerge>
  </filter>
  <filter id="soft" x="-10%" y="-10%" width="120%" height="120%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="b"/>
    <feComposite in="SourceAlpha" in2="b" operator="arithmetic" k2="1" k3="-1" result="rim"/>
    <feFlood flood-color="#5b3a2a" flood-opacity="0.22"/><feComposite in2="rim" operator="in" result="shade"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shade"/></feMerge>
  </filter>
  <filter id="papillae" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves="1" seed="9" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 0.92  0 0 0 0 0.93  0 0 0 -30 8.6" result="dots"/>
    <feComposite in="dots" in2="SourceAlpha" operator="in" result="d2"/>
    <feComponentTransfer in="d2" result="d3"><feFuncA type="linear" slope="0.3"/></feComponentTransfer>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d3"/></feMerge>
  </filter>
  <filter id="crypts" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="2" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.15  0 0 0 0 0.22  0 0 0 -18 6.4" result="dots"/>
    <feComposite in="dots" in2="SourceAlpha" operator="in" result="d2"/>
    <feComponentTransfer in="d2" result="d3"><feFuncA type="linear" slope="0.5"/></feComponentTransfer>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d3"/></feMerge>
  </filter>
  <filter id="leuko" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency="0.3" numOctaves="2" seed="3" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="3.5" result="disp"/>
    <feGaussianBlur in="disp" stdDeviation="0.5"/>
  </filter>
  <filter id="velvet" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="1" seed="5" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.55  0 0 0 0 0.08  0 0 0 0 0.12  0 0 0 -12 6" result="dots"/>
    <feComposite in="dots" in2="SourceAlpha" operator="in" result="d2"/>
    <feComponentTransfer in="d2" result="d3"><feFuncA type="linear" slope="0.35"/></feComponentTransfer>
    <feGaussianBlur in="SourceGraphic" stdDeviation="0.8" result="sg"/>
    <feMerge><feMergeNode in="sg"/><feMergeNode in="d3"/></feMerge>
  </filter>
  <clipPath id="tongueOnly"><path d="{TONGUE}"/></clipPath>
  <clipPath id="cheekL"><path d="{path(CHEEK)}"/></clipPath>
  <clipPath id="cheekR"><path d="{path(mirror(CHEEK))}"/></clipPath>
  <clipPath id="palateR"><path d="{path(mirror(ANT_PILLAR))}"/><path d="{path(SOFT_HAND)}"/></clipPath>
{lesions.LESION_DEFS}
  <clipPath id="lowTeeth"><rect x="0" y="688" width="1000" height="312"/></clipPath>
  <clipPath id="opening"><path d="{path(LIP_INNER)}"/></clipPath>
</defs>
<rect id="paper" width="{W}" height="{H}" fill="#f5f3f0"/>
<g id="inside" clip-path="url(#opening)" stroke-linejoin="round">
  <rect width="{W}" height="{H}" fill="url(#cavity)"/>
  <path id="wall" d="{path(WALL)}" fill="url(#wallG)" filter="url(#soft)"/>
  <g id="wallBumps" fill="#e3a0a4" opacity="0.55"><ellipse cx="462" cy="470" rx="9" ry="6"/><ellipse cx="530" cy="452" rx="8" ry="5"/><ellipse cx="505" cy="530" rx="10" ry="6"/><ellipse cx="452" cy="548" rx="7" ry="5"/><ellipse cx="560" cy="520" rx="8" ry="5"/></g>
  <g id="pillarsPost" fill="#cf767e" stroke="#8f3b49" stroke-width="1.2" filter="url(#vol)"><path d="{path(POST_PILLAR)}"/><path d="{path(mirror(POST_PILLAR))}"/></g>
  <g id="tonsils" fill="#c4627a" stroke="#83344a" stroke-width="1.2" filter="url(#crypts)"><path d="{path(TONSIL_HAND)}"/><path d="{path(mirror(TONSIL_HAND))}"/></g>
  {LZ["lump"]}
  <g id="pillarsAnt" fill="#d27b83" stroke="#8f3b49" stroke-width="1.2" filter="url(#vol)"><path d="{path(ANT_PILLAR)}"/><path d="{path(mirror(ANT_PILLAR))}"/></g>
  <g id="cheeks" fill="url(#cheekG)" stroke="#9b4752" stroke-width="1.2" filter="url(#vol)"><path d="{path(CHEEK)}"/><path d="{path(mirror(CHEEK))}"/></g>
  {LZ["speckled"]}
  {LZ["whitecheek"]}
  {LZ["redcheek"]}
  {LZ["lichen"]}
  <path id="softpalate" d="{path(SOFT_HAND)}" fill="url(#softG)" stroke="#9a4553" stroke-width="1.3" filter="url(#vol)"/>
  <path id="uvula" d="{path(UVULA)}" fill="#d9838a" stroke="#93404e" stroke-width="1.3" filter="url(#vol)"/>
  <g id="tongue">
    <path d="{TONGUE}" fill="url(#tongueA)" stroke="#963f4d" stroke-width="1.5" filter="url(#papillae)"/>
    <path d="{TONGUE_GROOVE}" fill="none" stroke="#a84b58" stroke-width="2.2" stroke-linecap="round" opacity="0.6"/>
  </g>
  {LZ["white"]}
  {LZ["red"]}
  {LZ["ulcer"]}
  {LZ["thrush"]}
  {LZ["canker"]}
  <path id="gumUp" d="{GUM_UP}" fill="url(#gumG)" stroke="#a6545c" stroke-width="1.2" filter="url(#soft)"/>
  <path id="gumLo" d="{GUM_LO}" fill="url(#gumG)" stroke="#a6545c" stroke-width="1.2" filter="url(#soft)"/>
  <g id="teeth" fill="url(#enamelA)" stroke="#a3967f" stroke-width="1.1" filter="url(#soft)">
{teeth(teeth_up, 'up')}
{teeth(teeth_lo, 'lo')}
  </g>
</g>
<g id="lips">
  <path d="{path(LIP_OUTER)} {path(LIP_INNER)}" fill="url(#lipG)" fill-rule="evenodd" stroke="#9c4a4e" stroke-width="1.6" filter="url(#vol)"/>
  <path d="M470,104 C485,118 515,118 530,104" fill="none" stroke="#a9575b" stroke-width="1.4" opacity="0.7"/>
</g>
<g id="lesions">
{LZ["lip"]}
</g>
<g id="labels" opacity="0">
{labels()}
</g>
</svg>'''

if __name__ == "__main__":
    OUT.write_text(svg()); print(OUT)
