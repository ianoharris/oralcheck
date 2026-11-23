"""
Mouth Notes, 3D lane (22 Nov 2026): "drunk cigs", for people who only smoke when
they drink.

Run by anim.py with the narration's timing:
    blender -b --factory-startup -P blender/drunkcigs.py -- plan.json out_dir/ [preview seconds]

Shots: hook (one cigarette, turning), count (four a weekend falls into ten packs:
208 a year, about 10 packs of 20), study (the packs hold; the 1.5x readout is the
house overlay), years (nineteen more layers, one a year, to about 200 packs), drink
(a cross-section of the mouth lining: smoke particles sit on top until a wash of
drink passes and they sink in between the cells), close (the years come off the
top again).

Science: Berthiller et al., Int J Epidemiol 2016 (INHANCE): >0-3 a day OR 1.52, the
excess seen with 20+ years of smoking. NCI, Alcohol and Cancer Risk: alcohol is
thought to make it easier for the mouth to absorb harmful chemicals from smoke.
Stylized: cells are rounded blocks, smoke is coral dots, nothing is to scale.
"""
import bpy, json, math, sys, random
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
plan = json.load(open(argv[0])); OUT = argv[1].rstrip("/") + "/"
FPS = 30
T = {s["key"]: s["t0"] for s in plan["shots"]}
TOTAL = plan["total"]
N_FRAMES = int(round(TOTAL * FPS))
fr = lambda t: 1 + int(round(t * FPS))
rnd = random.Random(7)

# ---- scene, render settings ---------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1080, 1000
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N_FRAMES
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = OUT + "f"
sc.view_settings.view_transform = "Standard"
try:
    sc.eevee.taa_render_samples = 32
    sc.eevee.use_shadows = True
except Exception:
    pass
BG = (0.913, 0.896, 0.871)
world = bpy.data.worlds.new("W"); sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (*BG, 1); bg.inputs[1].default_value = 1.0


def mat(name, rgb, rough=0.55, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    try:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (0.3, 0.15, 0.1)
    except Exception:
        pass
    return m
def srgb(h): return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5))

PAPER = mat("paper", srgb("#f6f3ec"), 0.7)
FILTER = mat("filter", srgb("#d9984a"), 0.6)
PACK = mat("pack", srgb("#0d7377"), 0.45)    # stylized, unbranded: teal with an ivory band
BAND = mat("band", srgb("#f1ece2"), 0.5)
CELL = mat("cell", srgb("#f1c9cf"), 0.55, 0.25)
CELL_D = mat("cellD", srgb("#e3a9b2"), 0.55, 0.25)
SMOKE = mat("smoke", srgb("#e8634a"), 0.4, 0.1)
AMBER = mat("amber", srgb("#e0a24a"), 0.12)
FLOOR = mat("floor", tuple(c * 0.8 for c in BG), 0.9)   # darker albedo so the lit floor meets the background without a horizon

# ---- lights, camera, floor ---------------------------------------------------------------
def light(kind, loc, energy, size=5, aim=(0, 0, 0)):
    d = bpy.data.lights.new(kind + str(loc), kind); d.energy = energy
    if kind == "AREA": d.size = size
    o = bpy.data.objects.new(d.name, d); o.location = loc; sc.collection.objects.link(o)
    o.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o
for X in (0, 30):   # the pack table at x=0, the lining at x=30
    light("AREA", (X + 6, -8, 9), 700, 8, (X, 0, 0)); light("AREA", (X - 7, -3, 3), 160, 6, (X, 0, 0)); light("AREA", (X, 6, 6), 220, 6, (X, 0, 0))
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 55
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
target = bpy.data.objects.new("target", None); sc.collection.objects.link(target)
con = cam.constraints.new("TRACK_TO"); con.target = target; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
bpy.ops.mesh.primitive_plane_add(size=120, location=(15, 0, 0))
bpy.context.active_object.data.materials.append(FLOOR)

def active(): return bpy.context.active_object
def join(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); return active()
def instance(proto, name):
    o = proto.copy(); o.data = proto.data; o.name = name; o.hide_render = False; o.hide_viewport = False
    sc.collection.objects.link(o); return o

# ---- a cigarette: 83 mm long, 8 mm across (1 unit = 100 mm), lying along y, filter at -y ----
CL, CR = 0.83, 0.04
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=CR, depth=0.62, location=(0, 0, 0.105)); paper = active(); paper.data.materials.append(PAPER)
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=CR * 1.01, depth=0.21, location=(0, 0, -0.31)); filt = active(); filt.data.materials.append(FILTER)
cig_proto = join([paper, filt]); bpy.ops.object.shade_smooth()
cig_proto.rotation_euler = (math.pi / 2, 0, 0); bpy.ops.object.transform_apply(rotation=True)
cig_proto.hide_render = True; cig_proto.hide_viewport = True

# ---- a pack: 55 x 88 x 22 mm lying flat, white with a teal band ---------------------------
PW, PL, PH = 0.57, 0.90, 0.23
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0)); box = active(); box.scale = (PW, PL, PH)
bpy.ops.object.transform_apply(scale=True); box.data.materials.append(PACK)
bv = box.modifiers.new("b", "BEVEL"); bv.width = 0.015; bv.segments = 2; bpy.ops.object.modifier_apply(modifier="b")
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.18, 0)); band = active(); band.scale = (PW + 0.006, 0.16, PH + 0.006)
bpy.ops.object.transform_apply(scale=True); band.data.materials.append(BAND)
pack_proto = join([box, band]); pack_proto.hide_render = True; pack_proto.hide_viewport = True

# table layout: a 5 x 2 grid of packs; layer L sits on L-1
GX, GY = 0.64, 0.98
def pack_pos(k, layer):
    i, j = k % 5, k // 5
    return Vector(((i - 2) * GX, (j - 0.5) * GY, PH / 2 + layer * (PH + 0.006)))
LAYERS = 20
packs = [[instance(pack_proto, f"pack{L}_{k}") for k in range(10)] for L in range(LAYERS)]

# 20 cigarettes per pack, rows of 7, 6, 7, filling pack by pack, four at a time (one weekend)
SLOTS = []
for row, n in ((-1, 7), (0, 6), (1, 7)):
    for c in range(n):
        SLOTS.append(Vector(((c - (n - 1) / 2) * 0.078, 0, row * 0.068)))
N_CIG = 200
cigs = []
c0, c1 = T["count"] + 0.35, T["study"] - 0.6
for n in range(N_CIG):
    o = instance(cig_proto, f"cig{n}")
    k, s = n // 20, n % 20
    end = pack_pos(k, 0) + SLOTS[s]
    g = n // 4
    ta = c0 + g * (c1 - c0) / (N_CIG / 4)
    start = Vector((end.x + rnd.uniform(-0.6, 0.6), end.y + rnd.uniform(-0.4, 0.4), 3.2 + rnd.uniform(0, 1.4)))
    spin = (rnd.uniform(-2, 2), rnd.uniform(-1, 1), rnd.uniform(-3, 3))
    cigs.append((o, k, start, end, ta, spin))
# the hook cigarette is the first one to fall
HOOK_POS = Vector((0, 0, 1.25))
box_t = [cigs[20 * k + 19][4] + 0.55 for k in range(10)]   # a pack closes when its last cigarette lands

# ---- the lining, in cross-section, at x = 30 -------------------------------------------------
X0 = 30.0
P = 0.57
bpy.ops.mesh.primitive_cube_add(size=1); cell_proto = active(); cell_proto.scale = (0.46, 0.46, 0.5)   # gaps between cells, so the smoke shows going in
bpy.ops.object.transform_apply(scale=True)
bv = cell_proto.modifiers.new("b", "BEVEL"); bv.width = 0.12; bv.segments = 4; bpy.ops.object.modifier_apply(modifier="b")
bpy.ops.object.shade_smooth()
cell_proto.hide_render = True; cell_proto.hide_viewport = True
COLS, ROWS, DEEP = 14, 3, 4
lining_root = bpy.data.objects.new("lining_root", None); sc.collection.objects.link(lining_root)   # sinks out of sight outside its shot
for c in range(COLS):
    for r in range(ROWS):
        for d in range(DEEP):
            o = cell_proto.copy(); o.data = cell_proto.data.copy(); o.hide_render = False; o.hide_viewport = False
            o.data.materials.append(CELL if r == ROWS - 1 else CELL_D)
            o.location = (X0 + (c - (COLS - 1) / 2) * P, (d - (DEEP - 1) / 2) * P, 0.25 + r * P + rnd.uniform(-0.02, 0.02))
            o.scale = (1 + rnd.uniform(-0.04, 0.04),) * 3
            sc.collection.objects.link(o); o.parent = lining_root
TOP = 0.25 + (ROWS - 1) * P + 0.25
GAPS = [X0 + (c - (COLS - 1) / 2) * P + P / 2 for c in range(COLS - 1)]
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.062); dot_proto = active()
bpy.ops.object.shade_smooth(); dot_proto.data.materials.append(SMOKE); dot_proto.hide_render = True; dot_proto.hide_viewport = True
dots = []
for i in range(70):
    o = instance(dot_proto, f"dot{i}")
    gx = rnd.choice(GAPS)
    y = rnd.uniform(-0.9, 0.9) if i % 3 else -(DEEP - 1) / 2 * P + rnd.uniform(-0.15, 0.15)   # a third along the front face
    land = Vector((gx + rnd.uniform(-0.18, 0.18), y, TOP + 0.075))
    depth = rnd.uniform(0.35, 1.45)
    dots.append((o, land, depth, rnd.uniform(0, 0.9)))
bpy.ops.mesh.primitive_cube_add(size=1); wave = active(); wave.scale = (1.6, DEEP * P + 0.3, 0.07)
bpy.ops.object.transform_apply(scale=True)
bv = wave.modifiers.new("b", "BEVEL"); bv.width = 0.03; bv.segments = 3; bpy.ops.object.modifier_apply(modifier="b")
wave.data.materials.append(AMBER)

# ---- animation ---------------------------------------------------------------------------
def key(obj, f, **kw):
    for k, v in kw.items():
        setattr(obj, k, v); obj.keyframe_insert(k, frame=f)
def ease(x): return 0 if x <= 0 else 1 if x >= 1 else 1 - (1 - x) ** 4
def inout(x): return 0 if x <= 0 else 1 if x >= 1 else (3 * x * x - 2 * x * x * x)
def span(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a)))
def lerp(a, b, k): return a + (b - a) * k
Z = (0.001,) * 3

y0, y1 = T["years"] + 0.4, T["drink"] - 1.0
def layer_t(L): return y0 + (L - 1) * (y1 - y0) / (LAYERS - 1)
d0 = T["drink"]
w0, w1 = d0 + 1.3, d0 + 3.3                       # the wash crosses left to right
cl0, cl1 = T["close"] + 0.5, T["cta"] - 0.3         # the years come back off, top first
def off_t(L): return cl0 + (LAYERS - 1 - L) * (cl1 - cl0) / LAYERS
KEEP = 2                                            # layers left standing at the end

for f in range(1, N_FRAMES + 1, 2):
    t = (f - 1) / FPS
    in_drink = d0 - 0.05 <= t < T["close"] - 0.05
    # cigarettes
    for (o, k, start, end, ta, spin) in cigs:
        if o.name == "cig0":
            fall = inout(span(t, T["count"] + 0.1, T["count"] + 0.9))
            pos = HOOK_POS.lerp(end, fall)
            rot = (0.35 * math.sin(t * 0.8) * (1 - fall), 0.25 * (1 - fall), (t * 0.9 + 0.4) * (1 - fall))
            vis = 1.0
        else:
            k_ = ease(span(t, ta - 0.55, ta))
            pos = start.lerp(end, k_)
            rot = tuple(s * (1 - k_) for s in spin)
            vis = 1.0 if t >= ta - 0.6 else 0.0
        if t > box_t[k] + 0.35 or in_drink:
            vis = 0.0
        key(o, f, location=pos, rotation_euler=rot, scale=(vis,) * 3 if vis else Z)
    # packs: layer 0 closes over its cigarettes; the rest arrive a year at a time
    for L in range(LAYERS):
        for kk, o in enumerate(packs[L]):
            if L == 0:
                s = ease(span(t, box_t[kk] - 0.1, box_t[kk] + 0.3)); drop = 0.0
            else:
                tl = layer_t(L) + kk * 0.015
                s = ease(span(t, tl, tl + 0.25)); drop = 0.5 * (1 - s)
            if L >= KEEP:
                s *= 1 - ease(span(t, off_t(L), off_t(L) + 0.25))
            if in_drink:
                s = 0.0
            key(o, f, location=pack_pos(kk, L) + Vector((0, 0, drop)), scale=(max(0.001, s),) * 3)
    # lining: smoke lands, the wash passes, the smoke sinks in between the cells
    wx = lerp(X0 - 6.0, X0 + 6.0, inout(span(t, w0, w1)))
    key(lining_root, f, location=(0, 0, 0) if in_drink else (0, 0, -60))
    key(wave, f, location=(wx, 0, TOP + 0.06), scale=(1, 1, 1) if (w0 - 0.1 < t < w1 + 0.1 and in_drink) else Z)
    for (o, land, depth, delay) in dots:
        dk = ease(span(t, d0 + 0.1 + delay * 0.8, d0 + 0.6 + delay * 0.8))
        pos = land + Vector((0, 0, 2.5 * (1 - dk)))
        tpass = lerp(w0, w1, (land.x - (X0 - 6.0)) / 12.0)
        sink = inout(span(t, tpass, tpass + 1.6))
        pos = pos + Vector((0, 0, -depth * sink))
        key(o, f, location=pos, scale=(1, 1, 1) if (dk > 0.01 and in_drink) else Z)
    # camera
    tp = HOOK_POS + Vector((0, 0, -0.05)); dist = 1.75; elev = 0.62; az = 0.35 + t * 0.12
    k1 = inout(span(t, T["count"] - 0.1, T["count"] + 1.3))
    tp = tp.lerp(Vector((0, 0, 0.05)), k1); dist = lerp(dist, 5.2, k1); elev = lerp(elev, 0.85, k1)
    k2 = inout(span(t, T["study"], T["study"] + 3.0)); dist += 0.7 * k2
    k3 = inout(span(t, T["years"], T["drink"] - 0.6))
    tp = tp.lerp(Vector((0, 0, 2.3)), k3); dist = lerp(dist, 12.5, k3); elev = lerp(elev, 0.45, k3)
    if in_drink:
        tp = Vector((X0, 0, TOP - 0.55)); dist = 7.6 - 0.8 * inout(span(t, d0, T["close"])); elev = 0.5
        az = 0.12 * math.sin((t - d0) * 0.4)
    elif t >= T["close"] - 0.05:
        kc = inout(span(t, T["close"], T["cta"]))
        tp = Vector((0, 0, lerp(2.3, 0.6, kc))); dist = lerp(12.5, 7.5, kc); elev = 0.45
    d = Vector((math.sin(az), -math.cos(az), elev)).normalized()
    key(target, f, location=tp)
    key(cam, f, location=tp + d * dist)

if len(argv) > 2:   # preview: only these seconds, as stills
    for sec in argv[2].split(","):
        sc.frame_set(fr(float(sec))); sc.render.filepath = OUT + f"p_{float(sec):05.1f}.png"
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("RENDERED", N_FRAMES)
