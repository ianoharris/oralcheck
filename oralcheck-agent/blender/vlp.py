"""
Mouth Notes, 3D lane prototype (22 Nov 2026): "The HPV vaccine is a virus with
nothing inside."

Run by anim.py with the narration's timing:
    blender -b --factory-startup -P blender/vlp.py -- plan.json out_dir/

plan.json is anim's plan ({"shots": [{"key", "t0", "len"}], "total"}); this
renders the stage band (1080 x 1000) as PNG frames out_dir/f0000.png ... keyed to
those shot times, and the house frame is laid over them by anim/bg3d.html.

Science (NCI, "Preventing Cervical Cancer: The Development of HPV Vaccines";
Schiller and Lowy): the HPV shell is made of the L1 protein, 360 copies grouped
in 72 five-sided capsomers around the viral DNA. L1 alone assembles into an
empty look-alike shell (a virus-like particle) with no viral DNA, so it cannot
infect; the immune system makes antibodies that fit its surface and later bind
real HPV. Stylized: capsomer placement is an even spread, not the exact T=7
lattice; antibodies are simple Y shapes; nothing is to scale.
"""
import bpy, json, math, sys
from mathutils import Vector, Euler

argv = sys.argv[sys.argv.index("--") + 1:]
plan = json.load(open(argv[0])); OUT = argv[1].rstrip("/") + "/"
FPS = 30
T = {s["key"]: s["t0"] for s in plan["shots"]}
TOTAL = plan["total"]
N_FRAMES = int(round(TOTAL * FPS))
fr = lambda t: 1 + int(round(t * FPS))

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
world = bpy.data.worlds.new("W"); sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.913, 0.896, 0.871, 1); bg.inputs[1].default_value = 1.0

def mat(name, rgb, rough=0.55, sss=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    try:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (0.3, 0.15, 0.1)
    except Exception:
        pass
    if emit:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = emit
    return m
def srgb(h): return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5))
TEAL, TEAL_L, CORAL, IVORY = mat("teal", srgb("#0d7377"), 0.45, 0.1), mat("tealL", srgb("#5aa8a9"), 0.5), mat("coral", srgb("#e8634a"), 0.4, 0.2), mat("ivory", srgb("#f1ece2"), 0.6, 0.1)

# ---- lights and camera ---------------------------------------------------------------
def light(kind, loc, energy, size=5):
    d = bpy.data.lights.new(kind + str(loc), kind); d.energy = energy
    if kind == "AREA": d.size = size
    o = bpy.data.objects.new(d.name, d); o.location = loc; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o
light("AREA", (6, -8, 7), 1600, 8); light("AREA", (-7, -3, 2), 500, 6); light("AREA", (0, 6, 5), 700, 6)
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 62
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
target = bpy.data.objects.new("target", None); sc.collection.objects.link(target)
con = cam.constraints.new("TRACK_TO"); con.target = target; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"

# ---- the shell: 72 five-sided capsomers ------------------------------------------------
R = 2.0
def fib(n):
    pts = []
    g = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - (i / (n - 1)) * 2; r = math.sqrt(1 - y * y); th = g * i
        pts.append(Vector((math.cos(th) * r, y, math.sin(th) * r)))
    return pts
bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.43, depth=0.30)   # packed: the shell is closed, capsomer against capsomer
proto = bpy.context.active_object; proto.name = "capsomer_proto"
bev = proto.modifiers.new("b", "BEVEL"); bev.width = 0.05; bev.segments = 3
bpy.ops.object.shade_smooth()
proto.data.materials.append(TEAL)
proto.hide_render = True; proto.hide_viewport = True
caps = []
shell = bpy.data.objects.new("shell", None); sc.collection.objects.link(shell)
# the shell's inner surface, so the closed particle reads as solid; it opens with the capsomers
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=R - 0.1)
inner = bpy.context.active_object; inner.name = "inner"; bpy.ops.object.shade_smooth()
inner.data.materials.append(mat("tealD", srgb("#0b5d60"), 0.6)); inner.parent = shell
for i, p in enumerate(fib(72)):
    o = proto.copy(); o.data = proto.data; o.hide_render = False; o.hide_viewport = False
    sc.collection.objects.link(o); o.parent = shell
    o.location = p * R
    o.rotation_euler = p.to_track_quat("Z", "Y").to_euler()
    caps.append((o, p))

# ---- the DNA inside a real virus: a coiled tube -----------------------------------------
curve = bpy.data.curves.new("dna", "CURVE"); curve.dimensions = "3D"; curve.bevel_depth = 0.09; curve.bevel_resolution = 4
sp = curve.splines.new("POLY"); n = 420; sp.points.add(n - 1)
for i in range(n):
    a = i / n * 2 * math.pi * 9
    rr = 1.25 * math.sin(i / n * math.pi * 3.7) ** 2 + 0.2
    sp.points[i].co = (rr * math.cos(a), 1.3 * math.sin(i / n * 13.1), rr * math.sin(a * 1.07), 1)
dna = bpy.data.objects.new("dna", curve); dna.data.materials.append(CORAL); sc.collection.objects.link(dna); dna.parent = shell

# ---- antibodies: simple Y shapes ------------------------------------------------------
def antibody(name):
    parts = []
    for (loc, rot, L) in [((0, 0, 0), (0, 0, 0), 0.55), ((0.16, 0, 0.42), (0, 0.6, 0), 0.42), ((-0.16, 0, 0.42), (0, -0.6, 0), 0.42)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.065, depth=L, location=loc, rotation=rot)
        c = bpy.context.active_object; bpy.ops.object.shade_smooth(); parts.append(c)
    for c in parts: c.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join()
    ab = bpy.context.active_object; ab.name = name; ab.data.materials.append(IVORY)
    return ab
abs_ = []
pts = fib(40)
for i, p in enumerate(pts):
    ab = antibody(f"ab{i}"); abs_.append((ab, p))

# ---- animation ---------------------------------------------------------------------------
def key(obj, f, **kw):
    for k, v in kw.items():
        setattr(obj, k, v); obj.keyframe_insert(k, frame=f)
def ease(x): return 0 if x <= 0 else 1 if x >= 1 else 1 - (1 - x) ** 4
def span(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a)))

cam_from = Vector((0, -9.5, 1.6))
for f in range(1, N_FRAMES + 1, 2):       # key every other frame; Blender interpolates between
    t = (f - 1) / FPS
    # the shell turns slowly the whole time
    key(shell, f, rotation_euler=Euler((0.25 * math.sin(t * 0.3), 0, t * 0.35)))
    # front opens on frame 0 (empty), closes for "real" with the DNA, scatters and reassembles for "build",
    # opens again for "empty", closes for "immune" and stays closed
    # open (cut away at the front) for the hook (empty), "real" (DNA inside) and "empty"; closed otherwise
    openK = (1 - span(t, T["real"] + 3.2, T["build"])) \
        + span(t, T["empty"] - 0.2, T["empty"] + 0.8) * (1 - span(t, T["immune"] - 0.2, T["immune"] + 0.6))
    openK += 0.75 * span(t, T["later"] + 0.6, T["later"] + 1.4)   # the real virus, cut away under its antibodies
    openK = max(0.0, min(1.0, openK))
    dnaK = span(t, T["real"] - 0.1, T["real"] + 0.7) * (1 - span(t, T["build"] - 0.2, T["build"] + 0.4)) + span(t, T["later"] + 0.2, T["later"] + 1.0)
    # the inner surface hides while the shell is open or scattered
    build_on = span(t, T["build"] - 0.1, T["build"] + 0.5) * (1 - span(t, T["build"] + 3.0, T["build"] + 3.6))
    key(inner, f, scale=(max(0.001, (1 - openK) * (1 - build_on)),) * 3)
    key(dna, f, scale=(max(0.001, dnaK),) * 3)
    build = span(t, T["build"] - 0.1, T["build"] + 0.5), ease(span(t, T["build"] + 0.6, T["build"] + 3.6))
    for i, (o, p) in enumerate(caps):
        # front-facing capsomers (towards the camera, after the shell's own turn) peel away to show inside
        world_p = shell.rotation_euler.to_matrix() @ p
        front = max(0.0, -world_p.y)
        peel = openK * min(1.0, max(0.0, front - 0.25) * 3.0)   # a clean round opening facing the camera
        scatter = build[0] * (1 - build[1])
        dirv = p * (1 + 2.8 * scatter + 0.6 * peel) + Vector((0, 0, 0.6 * math.sin(i))) * scatter
        key(o, f, location=dirv * R, scale=(max(0.001, 1 - peel),) * 3)
    # antibodies fly in and bind
    for i, (ab, p) in enumerate(abs_):
        k = ease(span(t, T["immune"] + 0.4 + i * 0.03, T["immune"] + 1.8 + i * 0.03))
        out = p * (R + 0.62) + Vector((0, 0, 0))
        far = p * 9 + Vector((3 * math.sin(i), -4, 2 * math.cos(i)))
        rot_shell = shell.rotation_euler.to_matrix()
        loc = rot_shell @ (far.lerp(out, k))
        key(ab, f, location=loc, rotation_euler=(rot_shell @ p).to_track_quat("-Z", "Y").to_euler(), scale=(max(0.001, k),) * 3)
    # camera: a slow orbit; pushes in for "empty", back out for "later"
    push = ease(span(t, T["empty"] - 0.2, T["empty"] + 1.4)) * (1 - ease(span(t, T["immune"], T["immune"] + 1.4)))
    pull = ease(span(t, T["later"], T["later"] + 2.0))
    a = t * 0.12
    dist = 9.5 - 1.4 * push + 1.2 * pull
    key(cam, f, location=Vector((math.sin(a) * dist, -math.cos(a) * dist, 1.6 + 0.4 * math.sin(t * 0.25))))

if len(argv) > 2:   # preview: only these seconds, as stills
    for sec in argv[2].split(","):
        sc.frame_set(fr(float(sec))); sc.render.filepath = OUT + f"p_{float(sec):05.1f}.png"
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("RENDERED", N_FRAMES)
