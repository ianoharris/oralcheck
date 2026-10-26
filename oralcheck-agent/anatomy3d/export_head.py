"""Export a head-and-neck bust from the Z-Anatomy atlas, every layer, to head.glb.

blender -b --disable-autoexec --factory-startup Z-Anatomy/Startup.blend --python export_head.py -- head.glb

Each mesh carries extras {cls, region} so the viewer can texture and group it.
Vessels and nerves are curves in the atlas; they are converted to tubes here.
The skin gets three procedural layers under it (epidermis, dermis,
hypodermis), because no atlas models skin as separate volumes: they are
offset shells of the skin surface, with the epidermis thickened so it reads.
"""
import bmesh, bpy, math, os, re, sys
# Where the lips meet (m), placed by Ian with the lip tuner on 22 Oct: 14.5 mm above the slit the atlas
# skin has for a mouth (SLIT), in the groove between the two bulges of the lips, just above the tips of the
# upper teeth. The skin is parted here and the viewer's jaw rig opens it here (skinJaw in src/main.js).
SLIT = 1.5155
STOMION = 1.530
MOUTH_HALF = 0.026   # half the width of the opening
# Whether the head carries its skin (epidermis, dermis, subcutaneous fat, and the lashes and brows that grow
# from it). Off since 23 Oct: Ian, "just delete the skin layer its honestly too terrifying". The skin is still
# built (the mouth's linings are fitted against it), just left out of the file at the end; True brings it back.
SKIN_IN_MODEL = False
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = sys.argv[sys.argv.index("--") + 1]
Z_CUT = 1.425                      # bottom of the bust (base of the neck)
X_CUT = 0.125                      # half-width of the bust at the shoulders
dg = bpy.context.evaluated_depsgraph_get()

def col(o):
    return o.users_collection[0].name if o.users_collection else ""

def classify(o):
    n, c = o.name, col(o)
    if re.search(r"hair|eyelash|sulcus|fissure|Lat_Fis|-curve|-profile|-path|\.g$|^\?|reference|plane", n, re.I):
        return None
    if c.startswith("9"):                                   # surface regions = skin
        return "skin"
    if c.startswith("1"):
        if re.search(r"(incisor|canine|premolar|molar)\b", n): return "tooth"
        if re.search(r"cartilage|epiglott", n, re.I): return "cartilage"
        return "bone"
    if c.startswith("4"):
        return "fascia" if re.search(r"fascia|aponeurosis|sheath|septum|raphe", n, re.I) else "muscle"
    if c.startswith("5"):
        return "vein" if re.search(r"vein|sinus|plexus", n, re.I) else "artery"
    if c.startswith("6"): return "lymph"
    if c.startswith("8"):
        if re.search(r"gland|hypophysis", n, re.I): return "gland"
        if re.search(r"duct", n, re.I): return "duct"
        if re.search(r"epiglott|cartilage", n, re.I): return "cartilage"
        return "mucosa"
    if c.startswith("7") or c == "Nervous system":
        if o.type == "CURVE" or re.search(r"nerve|ganglion|chorda|trunk|plexus", n, re.I): return "nerve"
        if re.search(r"eyeball|cornea|iris|lens|sclera|retina|chamber|vitreous|pupil", n, re.I): return "eye"
        if re.search(r"lacrimal|cochlea|tube|vestibul|semicircular|tympan|ossicle|malleus|incus|stapes", n, re.I): return "sense"
        return "brain"
    if c.startswith("3"): return None                       # joints: capsules overlap the bone
    return None

def bbox_z(o):
    zs = [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
    return min(zs), max(zs)

# neck column: centred on the third cervical vertebra, a little forward of it
c3 = bpy.data.objects.get("Intervertebral disc C3-C4")
if c3:
    cc = sum((c3.matrix_world @ Vector(c) for c in c3.bound_box), Vector()) / 8
    NECK = Vector((0.0, cc.y - 0.02))
else:
    NECK = Vector((0.0, 0.0))
print("NECK", NECK)

def inside(v):
    if v.z < Z_CUT: return False
    if v.z < 1.50:                                          # neck: a rounded column, no shoulders
        d = Vector((v.x - NECK.x, (v.y - NECK.y) * 0.85)).length
        return d < 0.085
    return abs(v.x) < 0.13

work = bpy.data.collections.new("export"); bpy.context.scene.collection.children.link(work)
made, skipped = [], 0
for o in list(bpy.data.objects):
    if o.type not in ("MESH", "CURVE"): continue
    cls = classify(o)
    if not cls: continue
    z0, z1 = bbox_z(o)
    if z1 < Z_CUT: continue
    if o.type == "CURVE":
        o.data.bevel_resolution = 1; o.data.resolution_u = min(o.data.resolution_u, 6)
        if o.data.bevel_depth < 0.0006: o.data.bevel_depth = 0.0006
    ev = o.evaluated_get(dg)
    try:
        me = ev.to_mesh()
    except Exception:
        skipped += 1; continue
    if me is None or len(me.vertices) < 4:
        ev.to_mesh_clear(); continue
    bm = bmesh.new(); bm.from_mesh(me); ev.to_mesh_clear()
    bm.transform(o.matrix_world)
    # clean straight cuts: the base of the neck and the two shoulders
    for co, no in (((0, 0, Z_CUT), (0, 0, -1)), ((X_CUT, 0, 0), (1, 0, 0)), ((-X_CUT, 0, 0), (-1, 0, 0))):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_outer=True)
    if len(bm.faces) < 4:
        bm.free(); continue
    nm = bpy.data.meshes.new(o.name); bm.to_mesh(nm); bm.free()
    for p in nm.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(o.name, nm); work.objects.link(ob)
    ob["cls"] = cls; ob["src"] = col(o); ob["label"] = o.name
    made.append(ob)
print("MADE", len(made), "SKIPPED", skipped)


# ---- helpers for the generated oral surfaces --------------------------------
def link_bm(name, cls, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); work.objects.link(ob); ob["cls"] = cls; ob["label"] = name
    return ob

def faces_to_bm(faces, offset=None):
    """Copy faces (keeping their winding) into a new bmesh, optionally moving each vertex."""
    nb, vm = bmesh.new(), {}
    for f in faces:
        vs = []
        for v in f.verts:
            if v not in vm: vm[v] = nb.verts.new(v.co + offset(v) if offset else v.co.copy())
            vs.append(vm[v])
        try: nb.faces.new(vs)
        except ValueError: pass
    nb.normal_update(); return nb

def shell(bm, thick):
    """Give a sheet whose normals face the side that shows a back surface `thick` behind it."""
    bm.normal_update(); vn = {v: v.normal.copy() for v in bm.verts}
    dup = bmesh.ops.duplicate(bm, geom=list(bm.faces))
    for v, n in vn.items():
        if v in dup["vert_map"]: dup["vert_map"][v].co = v.co - n * thick
    bmesh.ops.reverse_faces(bm, faces=[g for g in dup["geom"] if isinstance(g, bmesh.types.BMFace)])
    return bm

def W(label):
    return next((o for o in work.objects if o.get("label") == label), None)

def bm_of(*objs):
    b = bmesh.new()
    for o in objs:
        if o: b.from_mesh(o.data)
    b.normal_update(); return b

def apply_mod(o, mod):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=mod.name)

FISSURE = 1.530        # height of the line between the lips

# skin: merge the surface regions into one smooth surface, then build layers
skins = [o for o in made if o["cls"] == "skin"]
if skins:
    bpy.ops.object.select_all(action="DESELECT")
    for o in skins: o.select_set(True)
    bpy.context.view_layer.objects.active = skins[0]
    bpy.ops.object.join()
    skin = bpy.context.view_layer.objects.active; skin.name = "Skin"; skin["cls"] = "skin"
    bm = bmesh.new(); bm.from_mesh(skin.data)
    # remember where the patches' edges were: the stitched seams are smoothed below
    seam_l = bm.verts.layers.int.new("seam")
    for e in bm.edges:
        if e.is_boundary:
            for v in e.verts: v[seam_l] = 1
    # The regions are separate patches; close the seams between them (but not the
    # mouth, nostrils or eyes, which are wider than this).
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0022)
    # Seams between patches can be wider than that: weld open edges to each
    # other up to 4.5 mm (the mouth, nostrils and eyelids are wider still).
    edge_verts = list({v for e in bm.edges if e.is_boundary for v in e.verts})
    bmesh.ops.remove_doubles(bm, verts=edge_verts, dist=0.0045)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
    # What is left open are loops of boundary edges. Fill the thin ones (seams,
    # the closed lips) and leave the wide ones (eyes, the neck cut).
    seen, filled = set(), 0
    fill_l = bm.faces.layers.int.new("fill")   # lids over filled openings, relaxed into curved skin below
    for e0 in [e for e in bm.edges if e.is_boundary]:
        if e0 in seen: continue
        loop, stack = [], [e0]; seen.add(e0)
        while stack:
            e = stack.pop(); loop.append(e)
            for v in e.verts:
                for e2 in v.link_edges:
                    if e2.is_boundary and e2 not in seen: seen.add(e2); stack.append(e2)
        verts = list({v for e in loop for v in e.verts})
        per = sum(e.calc_length() for e in loop)
        c = sum((v.co for v in verts), Vector()) / len(verts)
        # mean width of the opening: its area over half its perimeter, area from the spread about the centre
        spread = sum((v.co - c).length for v in verts) / len(verts)
        width = 3.14159 * spread * spread / max(per / 2, 1e-6) if per > 0 else 0
        # Also the openings left under the nose and along the smile lines, which the layers below
        # crumple around (three.js y = Blender z, z = -Blender y): anything on the front of the lower
        # face below the eyes. The lips are parted later, on purpose.
        front_face = -c.y > 0.04 and 1.50 < c.z < 1.585 and per < 0.26
        if per < 0.30 and (width < 0.006 or per < 0.02) or front_face:
            try:
                lid = bmesh.ops.holes_fill(bm, edges=loop, sides=len(loop) + 1)["faces"]; filled += 1
                for f in lid: f[fill_l] = 1
            except Exception:
                pass
        elif -c.y > 0.03 and 1.48 < c.z < 1.60:
            print("SKIN left open", round(per, 3), round(width, 4), tuple(round(x, 3) for x in (c.x, -c.y, c.z)))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    print("SKIN seams filled", filled)
    # A lid is flat and made of long thin triangles, which shade as facets: give it vertices
    # inside, then relax them so the lid bows smoothly between its edges like the skin around it.
    lids = [f for f in bm.faces if f[fill_l]]
    bmesh.ops.subdivide_edges(bm, edges=list({e for f in lids for e in f.edges}), cuts=2, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    inner = [v for v in bm.verts if v.link_faces and all(f[fill_l] for f in v.link_faces)]
    for _ in range(40): bmesh.ops.smooth_vert(bm, verts=inner, factor=0.6, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    print("SKIN lid verts relaxed", len(inner))
    # Where two patches were stitched the surface keeps a crease (it showed as lines across the
    # forehead and cheeks): relax the stitched vertices and two rings around them, leaving the
    # openings (eyes, neck cut) where they are.
    def on_open(v): return any(e.is_boundary for e in v.link_edges)
    ring = {v for v in bm.verts if v[seam_l] and not on_open(v)}
    for _ in range(2): ring |= {w for v in list(ring) for e in v.link_edges for w in e.verts}
    ring = [v for v in ring if not on_open(v)]
    for _ in range(8): bmesh.ops.smooth_vert(bm, verts=ring, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    print("SKIN seam verts smoothed", len(ring))
    # Stitching patches leaves creases, flaps and lids that shade as sharp lines (Ian's screenshot of
    # the nose and lips, 22 Oct). So the skin is rebuilt as one clean surface: close every remaining
    # opening (the eyes and the neck cut, as marked lids), melt the closed skin into a solid on a
    # 0.8 mm grid and take its surface (a voxel remesh, which also fuses the lips and fills the
    # nostrils), thin it to about 60,000 triangles where the shape allows, and then reopen the
    # eyes and the neck by removing what was built over the lids.
    IRIS_C = []
    for lab in ("Iris.l", "Iris.r"):
        io = next((o for o in bpy.data.objects if o.get("label") == lab or o.name.startswith(lab)), None)
        if io: IRIS_C.append(sum((io.matrix_world @ Vector(c) for c in io.bound_box), Vector()) / 8)
    print("SKIN iris centres", [tuple(round(x, 3) for x in c) for c in IRIS_C])
    # each eye's opening, traced from the original skin's open edge round that iris, as a polygon
    # seen from the front (x, height), ordered by angle
    EYE_POLY = []
    for ic in IRIS_C:
        rimv = [v.co.copy() for v in bm.verts if any(e.is_boundary for e in v.link_edges)
                and (Vector((v.co.x, v.co.z)) - Vector((ic.x, ic.z))).length < 0.02 and -v.co.y > -ic.y - 0.012]
        rimv.sort(key=lambda q: math.atan2(q.z - ic.z, q.x - ic.x))
        EYE_POLY.append([(q.x, q.z) for q in rimv])
    print("SKIN eye outline points", [len(pq) for pq in EYE_POLY])
    def inside(pt, poly):
        x, y, c = pt[0], pt[1], False
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[i - 1]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: c = not c
        return c
    # The atlas's skin is a hollow shell about 4 mm thick (an outer and an inner surface), with the
    # mouth a slit through it, and the ears single sheets with no thickness, which a voxel remesh
    # would erase. So: thicken everything by 1.2 mm, remesh, keep only the outer surface, then close
    # the mouth slit and the nostrils with relaxed patches. The eyes and the neck cut stay open.
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    neck_z = min(v.co.z for v in bm.verts)
    # How far to thicken: 2.5 mm each way over most of the head, so the gaps between the atlas's pieces close,
    # but only 0.6 mm round the ears, nose and eyes, which are too tightly curved for that (thickening them as
    # much roofed over the eye openings and the bowl of the ear and tore them). Weight 1 is the full amount.
    # Inside those zones it stays thin all the way; the change happens just outside them, over the coarse mesh.
    def tight_zone(c):
        ear = abs(c.x) > 0.055 and -0.035 < c.y < 0.04 and 1.525 < c.z < 1.635
        nose = abs(c.x) < 0.016 and c.z > 1.538 and -c.y > 0.085   # the nostrils only: the crease beside each
                                                                     # nose wing has a slit that needs the full amount
        eye = any((Vector((c.x, c.z)) - Vector((ic.x, ic.z))).length < 0.026 and -c.y > 0.05 for ic in IRIS_C)
        return ear or nose or eye
    bm.verts.index_update()
    zone = [tight_zone(v.co) for v in bm.verts]
    wlist = [0.0 if z else 1.0 for z in zone]
    for _ in range(2):
        wlist = [(wlist[v.index] + sum(wlist[e.other_vert(v).index] for e in v.link_edges)) / (1 + len(v.link_edges)) for v in bm.verts]
        wlist = [0.0 if z else w for z, w in zip(zone, wlist)]
    from mathutils.kdtree import KDTree
    wkd = KDTree(len(bm.verts))
    for v in bm.verts: wkd.insert(v.co, v.index)
    wkd.balance()
    dl = bm.verts.layers.deform.verify()
    bm.verts.ensure_lookup_table()
    for i, w in enumerate(wlist): bm.verts[i][dl][0] = w
    THIN = 0.24          # 1.2 mm of the full 5 mm
    me = bpy.data.meshes.new("skin_solid"); bm.to_mesh(me)
    if os.environ.get("SKIN_DEBUG"):
        import pickle
        pickle.dump([[tuple(v.co) for v in f.verts] for f in bm.faces], open(os.environ["SKIN_DEBUG"] + "_pre.pkl", "wb"))
    atlas_tree = BVHTree.FromBMesh(bm)          # the atlas skin itself, to pull the new surface back onto
    bm.free()
    so = bpy.data.objects.new("skin_solid", me); work.objects.link(so); so.vertex_groups.new(name="thick")
    # Thickened 2.5 mm each way, so the atlas's two layers fuse into one solid and every gap between its
    # pieces closes over (at 1.2 mm they fused only in patches, which left rows of pits and pleats down the
    # chin and neck and along the smile lines). The surface is pulled back onto the skin below.
    m = so.modifiers.new("thick", "SOLIDIFY"); m.thickness = 0.005; m.offset = 0.0
    m.vertex_group = "thick"; m.thickness_vertex_group = THIN; apply_mod(so, m)
    m = so.modifiers.new("vox", "REMESH"); m.mode = "VOXEL"; m.voxel_size = 0.0008; m.adaptivity = 0.0; apply_mod(so, m)
    n0 = len(so.data.polygons)
    m = so.modifiers.new("thin", "DECIMATE"); m.ratio = min(1.0, 120000 / max(1, 2 * n0)); apply_mod(so, m)
    bm = bmesh.new(); bm.from_mesh(so.data); bpy.data.objects.remove(so); bpy.data.meshes.remove(me)
    bmesh.ops.triangulate(bm, faces=bm.faces); bm.normal_update()
    # The outer surface is what can be seen from outside: a face is kept if, looking at it from
    # any of 50 directions spread round a sphere, it is the first skin a ray meets. The inner
    # surface is hidden behind the outer one from every direction (except, faintly, through the
    # mouth slit, which is why a test from the faces outward was not enough).
    otree = BVHTree.FromBMesh(bm)
    dirs = []
    for k in range(50):
        zz = 1 - 2 * (k + 0.5) / 50; r = math.sqrt(1 - zz * zz); a = k * 2.39996
        dirs.append(Vector((r * math.cos(a), r * math.sin(a), zz)))
    inner = []
    for f in bm.faces:
        c = f.calc_center_median(); seen_out = False
        for d in dirs:
            if d.dot(f.normal) <= 0.05: continue           # only from the side the face looks toward
            h = otree.ray_cast(c + d * 0.6, -d, 0.61)
            if h[0] is not None and (h[0] - c).length < 0.0006: seen_out = True; break
        if not seen_out: inner.append(f)
    bmesh.ops.delete(bm, geom=inner, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    # The mouth slit runs back into the shell, so its walls (and whatever can be seen through it)
    # would close the mouth deep inside instead of at the lips: cut away anything in the mouth that
    # lies more than 3 mm behind the front surface there, so the opening is closed where the lips meet.
    ftree = BVHTree.FromBMesh(bm)
    tunnel = []
    for f in bm.faces:
        c = f.calc_center_median()
        if abs(c.x) < 0.03 and 1.500 < c.z < 1.532:
            h = ftree.ray_cast(Vector((c.x, -0.3, c.z)), Vector((0, 1, 0)), 0.5)
            if h[0] is not None and (c.y - h[0].y) > 0.003: tunnel.append(f)
    bmesh.ops.delete(bm, geom=tunnel, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    print("SKIN mouth slit walls removed", len(tunnel))
    # keep the largest connected piece (the face and head); stray bits of inner wall go
    seen, parts = set(), []
    for f0 in bm.faces:
        if f0 in seen: continue
        comp, st = [], [f0]; seen.add(f0)
        while st:
            f = st.pop(); comp.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g not in seen: seen.add(g); st.append(g)
        parts.append(comp)
    parts.sort(key=len, reverse=True)
    bmesh.ops.delete(bm, geom=[f for comp in parts[1:] for f in comp], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    print("SKIN outer surface", len(bm.faces), "faces; inner removed", len(inner), "; pieces dropped", len(parts) - 1)
    # Bring the surface back in by as much as it was thickened, along its own normal, then snap each vertex
    # onto the atlas skin where the skin is right there (within 0.6 mm), which restores the fine shape of the
    # lips, nose and ears. Over a gap between the atlas's pieces there is nothing that close, so the surface
    # bridges it. (Snapping every vertex to its nearest point instead pulled the two sides of each gap onto
    # different pieces and stood the triangles between them on edge, as jagged dark seams.)
    bm.normal_update()
    nrm = {v: v.normal.copy() for v in bm.verts}
    for _ in range(3):   # a smoother normal field, so the offset does not wrinkle
        nrm = {v: (nrm[v] + sum((nrm[e.other_vert(v)] for e in v.link_edges), Vector())).normalized() for v in bm.verts}
    # each vertex steps back by however far it was thickened beyond the thin zones' 0.6 mm
    snapped = 0
    for v in bm.verts:
        _, k, _ = wkd.find(v.co)
        # (in the thin zones it does not step back at all, as before this rebuild: stepping back along the
        # normal inside the folds of the ear crossed the surface over itself and left flaps)
        t = v.co - nrm[v] * 0.0025 * wlist[k]
        if wlist[k] > 0.5:
            hit = atlas_tree.find_nearest(t)[0]
            if hit is not None and (hit - t).length < 0.0006: t = hit; snapped += 1
        v.co = t
    inside = [v for v in bm.verts if not any(e.is_boundary for e in v.link_edges)]
    bmesh.ops.smooth_vert(bm, verts=inside, factor=0.3, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.normal_update()
    print("SKIN brought back to the atlas skin;", snapped, "of", len(bm.verts), "vertices snapped onto it")
    def boundary_loops():
        out, seen = [], set()
        for e0 in [e for e in bm.edges if e.is_boundary]:
            if e0 in seen: continue
            loop, st = [], [e0]; seen.add(e0)
            while st:
                e = st.pop(); loop.append(e)
                for v in e.verts:
                    for e2 in v.link_edges:
                        if e2.is_boundary and e2 not in seen: seen.add(e2); st.append(e2)
            vs = list({v for e in loop for v in e.verts})
            out.append((loop, vs, sum((v.co for v in vs), Vector()) / len(vs), sum(e.calc_length() for e in loop)))
        return out
    MOUTH_LOOP = []
    for loop, vs, lc, per in boundary_loops():
        if abs(lc.x) < 0.01 and 1.49 < lc.z < 1.535 and -lc.y > 0.04 and per < 0.2: MOUTH_LOOP = vs
    # The atlas's mouth slit is not where the lips meet (Ian placed that 14.5 mm higher), so it is sealed
    # for good: its upper and lower edges are drawn together onto the middle of the slit, no more than
    # 2.5 mm behind the front of the lips, with the skin around following on a falloff, and then welded.
    # (A fan patch sat recessed behind the lips and showed as a pale oval.)
    if MOUTH_LOOP:
        front = {}
        for v in bm.verts:
            if abs(v.co.z - SLIT) < 0.005:
                b = round(v.co.x * 1000); front[b] = min(front.get(b, 1.0), v.co.y)
        disp, upper = {}, set()
        for v in MOUTH_LOOP:
            nb = [u for u in MOUTH_LOOP if abs(u.co.x - v.co.x) < 0.0015]
            mz = (max(u.co.z for u in nb) + min(u.co.z for u in nb)) / 2
            if v.co.z >= mz: upper.add(v)
            b = round(v.co.x * 1000)
            fy = min(front.get(k, 1.0) for k in (b - 1, b, b + 1))
            ty = min(sum(u.co.y for u in nb) / len(nb), fy + 0.0025)
            disp[v] = Vector((v.co.x, ty, mz)) - v.co
        ring, dist, N = list(MOUTH_LOOP), {v: 0 for v in MOUTH_LOOP}, 10
        for r in range(1, N + 1):
            nxt = []
            for v in ring:
                for e in v.link_edges:
                    u = e.other_vert(v)
                    if u not in dist: dist[u] = r; disp[u] = disp[v]; nxt.append(u)
            ring = nxt
        for v, d in disp.items(): v.co += d * (1 - dist[v] / (N + 1)) ** 2
        up, lo = [v for v in MOUTH_LOOP if v in upper], [v for v in MOUTH_LOOP if v not in upper]
        if up and lo:
            tmap = {v: min(up, key=lambda u: (u.co - v.co).length) for v in lo}
            bmesh.ops.weld_verts(bm, targetmap=tmap)
            bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
            # smooth out the crease the weld leaves (it showed as a wrinkle under the lower lip)
            zone, ring = set(v for v in up if v.is_valid), [v for v in up if v.is_valid]
            for _ in range(8):
                ring = [e.other_vert(v) for v in ring for e in v.link_edges if e.other_vert(v) not in zone]
                zone.update(ring)
            zone = [v for v in zone if not any(e.is_boundary for e in v.link_edges)]
            for _ in range(40): bmesh.ops.smooth_vert(bm, verts=zone, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
        print("SKIN atlas mouth slit sealed:", len(up), "upper and", len(lo), "lower edge verts welded,", len(disp), "moved, max",
              round(max(d.length for d in disp.values()) * 1000, 1), "mm")
    # close every opening except the eyes and the cut across the neck, then relax the patches. The neck cut
    # is told apart by its size, not its height: small holes low on the neck (down the middle and the sides,
    # where the atlas's skin pieces meet) were being taken for it and left open, and showed as dark specks.
    EYE_RIM, lid_faces = [], []
    lid_l = bm.faces.layers.int.new("lid")
    loops = boundary_loops()
    neck_per = max((per for _, _, lc, per in loops if lc.z < neck_z + 0.03 and per > 0.25), default=0)
    for loop, vs, lc, per in loops:
        if neck_per and lc.z < neck_z + 0.03 and per == neck_per: continue
        if any((Vector((lc.x, lc.z)) - Vector((ic.x, ic.z))).length < 0.015 for ic in IRIS_C):
            EYE_RIM += [v.co.copy() for v in vs]; continue
        mid = bm.verts.new(lc)
        for e in loop:
            try:
                f = bm.faces.new((e.verts[1], e.verts[0], mid)); f[lid_l] = 1; lid_faces.append(f)
            except ValueError: pass
    print("SKIN openings:", len(loops), "found; neck cut perimeter", round(neck_per, 3), "m")
    bmesh.ops.subdivide_edges(bm, edges=list({e for f in lid_faces if f.is_valid for e in f.edges}), cuts=2, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.normal_update()
    lidv = [v for v in bm.verts if v.link_faces and all(f[lid_l] for f in v.link_faces)]
    print("SKIN openings closed with", sum(1 for f in bm.faces if f[lid_l]), "patch faces; eye rim points", len(EYE_RIM))
    for _ in range(40): bmesh.ops.smooth_vert(bm, verts=lidv, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    for _ in range(2): bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if not any(e.is_boundary for e in v.link_edges)], factor=0.3, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    # Skin more than 10 mm behind the front of the face in the middle of the mouth is a leftover of the atlas's
    # inner lining (it showed as a dark sliver 25 mm in, behind the teeth, when the mouth opened). (At 6 mm and
    # across the whole mouth this also took real skin out of the creases beside the nose, as see-through holes.)
    ftree2 = BVHTree.FromBMesh(bm)
    deep = []
    for f in bm.faces:
        c = f.calc_center_median()
        if abs(c.x) < 0.02 and 1.495 < c.z < 1.535:          # below the nose, whose wings stand out over the cheek
            h = ftree2.ray_cast(Vector((c.x, -0.3, c.z)), Vector((0, 1, 0)), 0.5)
            if h[0] is not None and c.y - h[0].y > 0.010: deep.append(f)
    bmesh.ops.delete(bm, geom=deep, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    print("SKIN deep pieces behind the mouth removed:", len(deep), "faces")
    # Last, close any small hole left on the face itself (a notch where the nose wing meets the cheek, two
    # slits at the ends of the sealed mouth slit). Not the eyes, and not the edges left deep in the mouth.
    ftree3, small = BVHTree.FromBMesh(bm), 0
    for loop, vs, lc, per in boundary_loops():
        if per > 0.1 or any((Vector((lc.x, lc.z)) - Vector((ic.x, ic.z))).length < 0.02 for ic in IRIS_C): continue
        if abs(lc.x) < 0.03 and 1.495 < lc.z < 1.535:   # round the mouth, skip the edges left deep inside it
            # (measured at the hole's own edge: a ray through its middle passes straight through the hole)
            dd = sorted((v.co.y - h[0].y) for v in vs for h in [ftree3.ray_cast(Vector((v.co.x, -0.3, v.co.z)), Vector((0, 1, 0)), 0.5)] if h[0] is not None)
            if not dd or dd[len(dd) // 2] > 0.004: continue
        mid = bm.verts.new(lc)
        for e in loop:
            try: bm.faces.new((e.verts[1], e.verts[0], mid)); small += 1
            except ValueError: pass
    bm.normal_update()
    print("SKIN small holes on the face closed:", small, "faces")
    # Close the grooves left where the atlas's skin pieces did not quite meet: down the middle of the chin and
    # neck, down the sides of the neck, and along the fold from the nose to the corner of the mouth (Ian, 22 Oct:
    # "fix the neck and chin marks and the smile lines"). Each shows as a narrow crease with a sharp rim, so
    # every vertex where neighbouring faces meet at more than 55 degrees is found, widened by three rings, and
    # smoothed. The places that are meant to be sharp are left alone: lips, nostrils, eyes, ears, open edges.
    bm.normal_update()
    def keep_sharp(c):
        if abs(c.x) > 0.058: return True                                              # ears
        if any((Vector((c.x, c.z)) - Vector((ic.x, ic.z))).length < 0.024 and -c.y > 0.05 for ic in IRIS_C): return True
        if abs(c.x) < 0.024 and c.z > 1.543 and -c.y > 0.07: return True              # nose and nostrils
        if abs(c.x) < 0.034 and abs(c.z - STOMION) < 0.007 and -c.y > 0.06: return True   # where the lips meet
        return False
    crease = set()
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.link_faces[0].normal.angle(e.link_faces[1].normal, 0) > math.radians(55):
            crease.update(v for v in e.verts if not keep_sharp(v.co))
    zone, ring = set(crease), list(crease)
    for _ in range(3):
        ring = [u for v in ring for e in v.link_edges for u in [e.other_vert(v)] if u not in zone and not keep_sharp(u.co)]
        zone.update(ring)
    zone = [v for v in zone if not any(e.is_boundary for e in v.link_edges)]
    for _ in range(30): bmesh.ops.smooth_vert(bm, verts=zone, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.normal_update()
    left = sum(1 for e in bm.edges if len(e.link_faces) == 2 and not keep_sharp(e.verts[0].co)
               and e.link_faces[0].normal.angle(e.link_faces[1].normal, 0) > math.radians(55))
    print("SKIN creases smoothed:", len(crease), "sharp vertices,", len(zone), "smoothed;", left, "sharp edges left")
    # and the band where the atlas's mouth slit was sealed, under the lower lip, which kept two small marks
    seal = [v for v in bm.verts if abs(v.co.x) < 0.03 and abs(v.co.z - SLIT) < 0.005 and -v.co.y > 0.06
            and not any(e.is_boundary for e in v.link_edges)]
    for _ in range(30): bmesh.ops.smooth_vert(bm, verts=seal, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    if os.environ.get("SKIN_DEBUG"):
        pickle.dump([[tuple(v.co) for v in f.verts] for f in bm.faces], open(os.environ["SKIN_DEBUG"] + "_post.pkl", "wb"))
        sys.exit(0)
    print("SKIN remeshed", n0, "->", len(bm.faces), "faces")
    # The regions do not join into one clean surface, so winding cannot be
    # trusted, and ray parity is fooled by the eye, mouth and neck openings.
    # Skin always lies outside muscle and bone, so "outward" is away from the
    # nearest deep tissue. That distance also caps how deep the layers go.
    from mathutils.bvhtree import BVHTree
    deep = bmesh.new()
    for o in work.objects:
        if o.get("cls") in ("muscle", "bone", "cartilage"):
            deep.from_mesh(o.data)
    dtree = BVHTree.FromBMesh(deep); deep.free()
    # Face by face, that vote goes wrong where the deep tissue is ambiguous (round the nose and
    # lips), leaving a patchwork. So first make the winding consistent across each connected
    # piece of surface, then let the whole piece vote, weighted by area, and flip it together.
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update(); flip = []
    seen = set()
    for f0 in bm.faces:
        if f0 in seen: continue
        comp, stack = [], [f0]; seen.add(f0)
        while stack:
            f = stack.pop(); comp.append(f)
            for e in f.edges:
                if not e.is_manifold: continue
                for g in e.link_faces:
                    if g not in seen: seen.add(g); stack.append(g)
        vote = 0.0
        for f in comp:
            c = f.calc_center_median(); q = dtree.find_nearest(c)[0]
            if q is not None: vote += f.calc_area() * (1 if (c - q).dot(f.normal) > 0 else -1)
        if vote < 0: flip.extend(comp)
    bmesh.ops.reverse_faces(bm, faces=flip); bm.normal_update()
    print("SKIN faces", len(bm.faces), "flipped", len(flip))
    out, room = {}, {}
    for v in bm.verts:
        n = sum((f.normal * f.calc_area() for f in v.link_faces), Vector())
        q, _, _, dist = dtree.find_nearest(v.co)
        if n.length < 1e-9 and q is not None: n = v.co - q
        out[v] = n.normalized() if n.length > 1e-9 else Vector((0, 0, 1))
        room[v] = dist if dist is not None else 0.01
    # Thin places (ear, nostril rim, eyelid, lip edge) have little or no muscle
    # under them, so also cap the depth at a third of the skin's own thickness
    # there: the distance to the skin's far side, straight in.
    stree = BVHTree.FromBMesh(bm)
    for v in bm.verts:
        hit = stree.ray_cast(v.co - out[v] * 1e-4, -out[v], 0.05)
        if hit[0] is not None: room[v] = min(room[v], (hit[0] - v.co).length / 3.0)
    # Layers, depth range in metres under the surface. Real facial epidermis is
    # ~0.1 mm; it is drawn at 0.4 mm so it shows in a cut. Dermis ~1.5 mm,
    # subcutaneous fat ~4 mm. Each layer is an outer surface facing out and an
    # inner one facing in, so a cut shows it as a band.
    layers = [("Epidermis", "epidermis", 0.0, 0.0004), ("Dermis", "dermis", 0.0004, 0.002),
              ("Hypodermis (subcutaneous fat)", "hypodermis", 0.002, 0.006)]
    for name, cls, d0, d1 in layers:
        lb = bm.copy(); lout = {lv: out[v] for lv, v in zip(lb.verts, bm.verts)}
        inner = bmesh.ops.duplicate(lb, geom=list(lb.faces))
        imap = inner["vert_map"]
        lroom = {lv: room[v] for lv, v in zip(lb.verts, bm.verts)}
        # never deeper than 80% of the way to the muscle or bone underneath
        k = {v: min(1.0, 0.8 * lroom[v] / 0.006) for v in lout}
        for v in list(lout):
            if v in imap: imap[v].co = v.co - lout[v] * d1 * k[v]
        for v in list(lout): v.co = v.co - lout[v] * d0 * k[v]
        bmesh.ops.reverse_faces(lb, faces=[g for g in inner["geom"] if isinstance(g, bmesh.types.BMFace)])
        me = bpy.data.meshes.new(name); lb.to_mesh(me); lb.free()
        for p in me.polygons: p.use_smooth = True
        ob = bpy.data.objects.new(name, me); work.objects.link(ob); ob["cls"] = cls; ob["label"] = name
    bm.free()
    bpy.data.objects.remove(skin)

# ---- the mouth ------------------------------------------------------------------
# Where most oral cancers start, so it gets the most care. The atlas's tongue,
# tonsils, soft palate and throat wall are coarse, so they are smoothed; the
# gum is split into upper and lower (so the jaw can open); and the linings the
# atlas does not have at all are generated, fitted to the anatomy around them:
# inner lips, cheeks, hard palate and floor of the mouth.
from mathutils.bvhtree import BVHTree
RECLASS = {"Tongue": "tongue", "Palatine tonsil.l": "tonsil", "Palatine tonsil.r": "tonsil", "Soft palate": "oral",
           "Uvula of palate": "oral", "Oropharynx": "oral", "Nasopharynx": "oral", "Laryngopharynx": "oral", "Gingiva": "gingiva"}
SMOOTH = {"Tongue": 2, "Palatine tonsil.l": 2, "Palatine tonsil.r": 2, "Soft palate": 2, "Uvula of palate": 1,
          "Oropharynx": 2, "Nasopharynx": 1, "Laryngopharynx": 1, "Gingiva": 1}
for label, cls in RECLASS.items():
    o = W(label)
    if not o: continue
    o["cls"] = cls
    if label == "Soft palate":            # a flat plate in the atlas: give it its real thickness (about 8 mm)
        m = o.modifiers.new("thick", "SOLIDIFY"); m.thickness = 0.006; m.offset = 0.0; apply_mod(o, m)
    if SMOOTH.get(label):
        m = o.modifiers.new("smooth", "SUBSURF"); m.levels = SMOOTH[label]; apply_mod(o, m)

teeth_up = [o for o in work.objects if o.get("cls") == "tooth" and o["label"].startswith("Upper")]
teeth_lo = [o for o in work.objects if o.get("cls") == "tooth" and o["label"].startswith("Lower")]
gum = W("Gingiva")
if gum and teeth_up and teeth_lo:
    tu, tl = BVHTree.FromBMesh(bm_of(*teeth_up)), BVHTree.FromBMesh(bm_of(*teeth_lo))
    gb = bm_of(gum)
    up = [f for f in gb.faces if tu.find_nearest(f.calc_center_median())[3] < tl.find_nearest(f.calc_center_median())[3]]
    ups = set(up)
    def main_parts(faces):
        # drop the small flaps (between tooth roots) that stick out of the bone and catch the light
        faces = set(faces); comps, seen = [], set()
        for f0 in faces:
            if f0 in seen: continue
            comp, stack = [], [f0]; seen.add(f0)
            while stack:
                f = stack.pop(); comp.append(f)
                for e in f.edges:
                    for g in e.link_faces:
                        if g in faces and g not in seen: seen.add(g); stack.append(g)
            comps.append(comp)
        big = max(len(c) for c in comps)
        return [f for c in comps if len(c) > 0.08 * big for f in c]
    link_bm("Upper gingiva", "gingiva", faces_to_bm(main_parts(up)))
    link_bm("Lower gingiva", "gingiva", faces_to_bm(main_parts([f for f in gb.faces if f not in ups])))
    gb.free(); bpy.data.objects.remove(gum)

# hard palate: the underside of the maxillae and palatine bones inside the arch
bones = [W(n) for n in ("Maxilla.l", "Maxilla.r", "Palatine bone.l", "Palatine bone.r")]
if all(bones):
    b = bm_of(*bones); t = BVHTree.FromBMesh(b); under = []
    tt = BVHTree.FromBMesh(bm_of(*teeth_up)) if teeth_up else None
    for f in b.faces:
        c = f.calc_center_median()
        if abs(c.x) < 0.021 and -0.088 < c.y < -0.026 and 1.533 < c.z < 1.562 and t.ray_cast(c - Vector((0, 0, 2e-4)), Vector((0, 0, -1)), 0.03)[0] is None:
            # not the tooth sockets: those faces poke out between the roots
            if tt is None or tt.find_nearest(c)[3] > 0.003: under.append(f)
    bmesh.ops.reverse_faces(b, faces=[f for f in under if f.normal.z > 0]); b.normal_update()
    if under: link_bm("Hard palate mucosa", "oral", shell(faces_to_bm(under, lambda v: Vector((0, 0, -4e-4))), 0.002))
    b.free()

# ---- the lining of the mouth, swept along the dental arch -----------------------------
# The atlas has no lips, cheek lining or floor lining. They are built here as
# smooth swept surfaces, measured from the gums, the skin and the tongue around
# them, sector by sector around the arch (angle 0 straight ahead):
#   cheeks: upper gum, up into the fold where gum meets cheek, down the inside of
#           the cheek, the lower fold, back onto the lower gum;
#   lips:   the same lining at the front, split at the mouth line, rolling over
#           the lip edge into the red of the lip (upper and lower lip separate, so
#           the mouth can open between them);
#   floor:  from the inside of the lower gum, down into the floor and up under
#           the side of the tongue.
ARCH_C = 0.045            # forward position of the arch's centre (Blender -y is forward)
LIPLINE = 1.518           # height where the lips meet, measured off the skin's mouth opening
NS = 71; TH = [-1.75 + 3.5 * i / (NS - 1) for i in range(NS)]; DTH = TH[1] - TH[0]

def polar(p):
    f = -p.y - ARCH_C
    return math.atan2(p.x, f), math.hypot(p.x, f)

def world(theta, r, h):
    return Vector((math.sin(theta) * r, -(ARCH_C + math.cos(theta) * r), h))

def sectors(objs):
    out = [[] for _ in TH]
    for o in objs:
        if not o: continue
        for v in o.data.vertices:
            p = o.matrix_world @ v.co; t, r = polar(p); i = round((t - TH[0]) / DTH)
            for j in (i - 1, i, i + 1):
                if 0 <= j < NS and abs(t - TH[j]) < 0.07: out[j].append((r, p.z))
    return out

def series(vals, k=3):
    known = [i for i, v in enumerate(vals) if v is not None]
    if not known: return None
    f = [v if v is not None else vals[min(known, key=lambda j: abs(j - i))] for i, v in enumerate(vals)]
    return [sum(f[max(0, i - k):i + k + 1]) / len(f[max(0, i - k):i + k + 1]) for i in range(NS)]

def at(arr, th):
    x = min(max((th - TH[0]) / DTH, 0), NS - 1.001); i = int(x); u = x - i
    return arr[i] * (1 - u) + arr[i + 1] * u

def catmull(P, n):
    q = [P[0]] + P + [P[-1]]; out = []
    for s in range(len(P) - 1):
        p0, p1, p2, p3 = q[s], q[s + 1], q[s + 2], q[s + 3]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(P[-1]); return out

def sweep(name, cls, thetas, profile, toward, thick=0.002, n=6):
    """Sweep `profile(theta)` (a list of (radius, height)) across `thetas`; normals face `toward(point)`."""
    nb = bmesh.new()
    rows = [[nb.verts.new(world(th, r, h)) for r, h in catmull(profile(th), n)] for th in thetas]
    for a, b in zip(rows, rows[1:]):
        for j in range(len(a) - 1): nb.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
    nb.normal_update()
    if sum((toward(f.calc_center_median()) - f.calc_center_median()).dot(f.normal) for f in nb.faces) < 0:
        bmesh.ops.reverse_faces(nb, faces=list(nb.faces)); nb.normal_update()
    # Single sheets: the viewer draws them from the lining side only, so you can look into the mouth
    # through the near cheek and see the far one from inside.
    return link_bm(name, cls, shell(nb, thick) if thick else nb)

ug, lg = sectors([W("Upper gingiva")]), sectors([W("Lower gingiva")])
sk, tg = sectors([W("Epidermis")]), sectors([W("Tongue")])
def stat(sec, f):
    return series([f(c) if c else None for c in sec])
R_UO = stat(ug, lambda c: max(r for r, h in c))
Y_UT = stat(ug, lambda c: max(h for r, h in c if r > max(rr for rr, _ in c) - 0.004))
R_LO = stat(lg, lambda c: max(r for r, h in c))
Y_LB = stat(lg, lambda c: min(h for r, h in c if r > max(rr for rr, _ in c) - 0.004))
R_LI = stat(lg, lambda c: min(r for r, h in c))
Y_LI = stat(lg, lambda c: min(h for r, h in c if r < min(rr for rr, _ in c) + 0.004))
R_SK = stat(sk, lambda c: max([r for r, h in c if abs(h - LIPLINE) < 0.003] or [None]) if any(abs(h - LIPLINE) < 0.003 for r, h in c) else None)
R_TG = stat(tg, lambda c: max(r for r, h in c))
t_end = max(abs(TH[i]) for i in range(NS) if ug[i]) - 0.05 if any(ug) else 1.5
print("ARCH", round(at(R_UO, 0), 4), round(at(R_LI, 0), 4), round(at(R_SK, 0), 4), round(at(Y_UT, 0), 4), round(at(Y_LB, 0), 4), "t_end", round(t_end, 2))

TC = 0.5                  # half-angle of the mouth opening, corner to corner
def taper(th): return math.sqrt(max(0.0, math.cos(min(abs(th) / TC, 1.0) * math.pi / 2)))
axis_at = lambda c: Vector((0, -ARCH_C, c.z))
away = lambda c: c + (c - Vector((0, -ARCH_C, c.z))) * 2

def cheek(th):
    ru, yu, rl, yl = at(R_UO, th), at(Y_UT, th), at(R_LO, th), at(Y_LB, th)
    return [(ru + 0.0004, yu - 0.002), (ru + 0.0042, yu + 0.0025), (max(ru, rl) + 0.0032, (yu + yl) / 2),
            (rl + 0.0042, yl - 0.0025), (rl + 0.0004, yl + 0.002)]
for side, suffix in ((1, ".l"), (-1, ".r")):
    ths = [side * (TC - 0.08 + (t_end - TC + 0.08) * i / 24) for i in range(25)]
    if side < 0: ths = ths[::-1]
    sweep("Buccal mucosa" + suffix, "oral", ths, cheek, axis_at, thick=0)

def edge(th, ru):  # where the inner lip meets the red of the lip, 55% of the way out through the lip
    return ru + (max(at(R_SK, th), ru + 0.006) - ru) * 0.55
front = [-TC + 2 * TC * i / 30 for i in range(31)]
sweep("Upper labial mucosa", "oral", front, lambda th: [
    (at(R_UO, th) + 0.0004, at(Y_UT, th) - 0.002), (at(R_UO, th) + 0.0042, at(Y_UT, th) + 0.0025),
    (at(R_UO, th) + 0.0035, LIPLINE + 0.007), (edge(th, at(R_UO, th)), LIPLINE + 0.0006)], axis_at, thick=0)
sweep("Lower labial mucosa", "oral", front, lambda th: [
    (edge(th, at(R_LO, th)), LIPLINE - 0.0006), (at(R_LO, th) + 0.0035, LIPLINE - 0.007),
    (at(R_LO, th) + 0.0042, at(Y_LB, th) - 0.0025), (at(R_LO, th) + 0.0004, at(Y_LB, th) + 0.002)], axis_at, thick=0)
def lip(th, up):
    rs = max(at(R_SK, th), at(R_UO if up else R_LO, th) + 0.006); s = 1 if up else -1; tp = taper(th)
    rf = edge(th, at(R_UO if up else R_LO, th))
    pts = [(rf, LIPLINE + s * 0.0006), (rs - 0.0015, LIPLINE + s * 0.0022),
           (rs - 0.0002, LIPLINE + s * (0.001 + (0.0045 if up else 0.005) * tp)),
           (rs - 0.0015, LIPLINE + s * (0.001 + (0.0085 if up else 0.0095) * tp))]
    return pts if up else pts[::-1]
sweep("Upper lip", "lip", front, lambda th: lip(th, True), away, thick=0)
sweep("Lower lip", "lip", front, lambda th: lip(th, False), away, thick=0)

def floor(th):
    rli, yb = at(R_LI, th), at(Y_LI, th); rt = min(at(R_TG, th), rli - 0.006)
    return [(rli - 0.0004, yb + 0.004), (rli - 0.0025, yb - 0.003), ((rli + rt) / 2, yb - 0.0045),
            (rt + 0.0015, yb - 0.002), (rt - 0.0005, yb + 0.004)]
sweep("Floor of mouth mucosa", "oral", [-1.45 + 2.9 * i / 48 for i in range(49)], floor,
      lambda c: Vector((0, -ARCH_C, c.z + 0.02)), thick=0)

# the back wall of the throat, seen behind the uvula and tonsils when the mouth is wide open: the
# atlas only has a rough block for the throat space. A concave sheet just behind the uvula, curving
# forward at the sides toward the tonsils, facing the mouth.
nb = bmesh.new(); NX, NY = 24, 18
gridw = [[nb.verts.new((x, -(0.008 + 0.016 * (x / 0.024) ** 2), 1.492 + 0.075 * j / (NY - 1)))
          for j in range(NY)] for x in [-0.024 + 0.048 * i / (NX - 1) for i in range(NX)]]
for i in range(NX - 1):
    for j in range(NY - 1): nb.faces.new((gridw[i][j], gridw[i + 1][j], gridw[i + 1][j + 1], gridw[i][j + 1]))
nb.normal_update()
if sum(f.normal.y for f in nb.faces) > 0: bmesh.ops.reverse_faces(nb, faces=list(nb.faces))   # face forward (-y)
link_bm("Posterior pharyngeal wall", "oral", nb)

# The arches of the throat (fauces), which the atlas does not have: in an open mouth they frame the
# opening to the throat, the palatoglossal arch in front and the palatopharyngeal arch behind, with a
# tonsil in the niche between them. Each is a curtain on one side, rising from the tongue to meet the
# soft palate beside the uvula, its free edge rolled back into a rounded fold. (three.js coordinates
# here: x, y up, z forward; Blender's vertex is (x, -z, y).)
from math import sqrt, sin
def sstep(a, b, x): t = min(1.0, max(0.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def curtain(name, z0, w0, y_apex, x_out, y_bot=1.50, y_top=1.557, y_low=1.524):
    for side, sfx in ((1, ".l"), (-1, ".r")):
        nb = bmesh.new(); NU, NV = 16, 44; g = []
        for i in range(NU):
            u = (i / (NU - 1)) ** 1.6; col = []
            for j in range(NV):
                y = y_bot + (y_top - y_bot) * j / (NV - 1)
                e = w0 if y <= y_low else w0 * sqrt(max(0.0, 1 - ((y - y_low) / (y_apex - y_low)) ** 2)) if y < y_apex else 0.0
                x = e + (x_out - e) * u
                z = z0 - 0.004 * (1 - sstep(0.0, 0.004, x - e))
                col.append(nb.verts.new((side * x, -z, y)))
            g.append(col)
        for i in range(NU - 1):
            for j in range(NV - 1): nb.faces.new((g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]))
        nb.normal_update()
        if sum(f.normal.y for f in nb.faces) > 0: bmesh.ops.reverse_faces(nb, faces=list(nb.faces))   # face forward (-y)
        link_bm(name + sfx, "oral", nb)
curtain("Palatoglossal arch", 0.036, 0.019, 1.551, 0.036)
curtain("Palatopharyngeal arch", 0.023, 0.0135, 1.551, 0.03)
# The atlas's soft palate is a flat plate that reads as a box from below. Its lining is generated as
# a curved roof instead: from under the back of the hard palate (z 46 mm, where its lining is at
# y 1.548 m) back to the uvula (z 16 mm), domed a little, and curving down at the sides into the arches.
# It starts 12 mm further forward, tucked just under the hard palate, so no gap shows between the two.
nb = bmesh.new(); NX, NZ = 28, 22; g = []
for i in range(NX):
    x = -0.024 + 0.048 * i / (NX - 1); col = []
    for j in range(NZ):
        z = 0.058 - 0.042 * j / (NZ - 1); t = max(0.0, (0.046 - z) / 0.030)
        y = 1.5468 - (0.0003 if z > 0.046 else 0) + 0.0047 * sin(3.14159 * t) + 0.0032 * t - 0.006 * (abs(x) / 0.024) ** 3 * (0.4 + 0.6 * t)
        col.append(nb.verts.new((x, -z, y)))
    g.append(col)
for i in range(NX - 1):
    for j in range(NZ - 1): nb.faces.new((g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]))
nb.normal_update()
if sum(f.normal.z for f in nb.faces) > 0: bmesh.ops.reverse_faces(nb, faces=list(nb.faces))   # face down, into the mouth
link_bm("Soft palate mucosa", "oral", nb)
# The atlas's tonsils are small and sit high, level with the soft palate; in life a tonsil fills the
# niche between the arches, down to the level of the tongue. Lowered and enlarged to fill it.
for sfx, side in ((".l", 1), (".r", -1)):
    o = W("Palatine tonsil" + sfx)
    if not o: continue
    mw = o.matrix_world; inv = mw.inverted()
    pts = [mw @ v.co for v in o.data.vertices]
    c = sum(pts, Vector()) / len(pts)
    to = Vector((side * 0.0215, -0.0295, 1.534))
    for v, q in zip(o.data.vertices, pts):
        d = q - c
        v.co = inv @ (to + Vector((d.x * 1.3, d.y * 1.1, d.z * 1.9)))

# Part the lips: the skin runs unbroken from upper lip to lower lip, so opening the jaw would stretch
# a sheet across the mouth. Split every skin layer along the line where the lips meet (STOMION,
# MOUTH_HALF either side of the middle) with no gap: the cut edges are duplicated and nudged 0.05 mm
# to either side (wider let the teeth show through as a white line), so the closed lips still meet (an earlier cut removed a 3 mm strip, which showed as a slot).
for lab in ("Epidermis", "Dermis", "Hypodermis (subcutaneous fat)"):
    o = W(lab)
    if not o: continue
    bm = bmesh.new(); bm.from_mesh(o.data)
    near = [f for f in bm.faces if any(abs(v.co.x) < MOUTH_HALF + 0.006 and -v.co.y > 0.055 and abs(v.co.z - STOMION) < 0.006 for v in f.verts)]
    geom = list({g for f in near for g in list(f.verts) + list(f.edges)}) + near
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, STOMION), plane_no=(0, 0, 1))
    # Every face across the mouth now lies wholly above or below the line. Split every edge between an upper
    # face and a lower one (taking only the edges that lie on the plane left gaps in the cut wherever the
    # bisect landed on an existing vertex, and the jaw stretched those spots into slivers), then push every
    # vertex near the line onto its own lip, so the rig in the viewer never sees one sitting on the line.
    side = {}
    for f in bm.faces:
        c = f.calc_center_median()
        if abs(c.x) < MOUTH_HALF and -c.y > 0.06 and abs(c.z - STOMION) < 0.006: side[f] = c.z > STOMION
    seam = [e for e in bm.edges if len(e.link_faces) == 2 and all(f in side for f in e.link_faces)
            and side[e.link_faces[0]] != side[e.link_faces[1]]]
    bmesh.ops.split_edges(bm, edges=seam)
    moved = 0
    for v in bm.verts:
        fs = [f for f in v.link_faces if f in side]
        if not fs or abs(v.co.z - STOMION) > 0.00005: continue
        if all(side[f] for f in fs): v.co.z = STOMION + 0.00005; moved += 1
        elif not any(side[f] for f in fs): v.co.z = STOMION - 0.00005; moved += 1
    bm.to_mesh(o.data); bm.free()
    print("PARTED", lab, len(seam), "edges", moved, "verts")

# Eyelashes and eyebrows, as fine strands of geometry (Ian, 22 Oct). Lashes grow from the rim of each
# eye opening, curving forward and up (down for the lower lid), longest in the middle of the lid.
# Brow hairs lie almost flat on the skin along the brow arch, pointing outward and slightly up.
import random
random.seed(7)
epi = W("Epidermis")
if epi and IRIS_C:
    sb = bmesh.new(); sb.from_mesh(epi.data); sb.transform(epi.matrix_world)
    stree = BVHTree.FromBMesh(sb)
    hb = bmesh.new()
    def strand(root, d, bend, length, width, n=4):
        """a thin flat ribbon from root along d, bending toward `bend`, facing roughly forward"""
        pts = [root + (d * (t * length)) + bend * (length * 0.35 * t * t) for t in (i / n for i in range(n + 1))]
        side = d.cross(Vector((0, -1, 0)))
        if side.length < 1e-6: side = Vector((1, 0, 0))
        side.normalize()
        prev = None
        for i, q in enumerate(pts):
            w = width * (1 - 0.8 * i / n)
            a, b = hb.verts.new(q - side * w / 2), hb.verts.new(q + side * w / 2)
            if prev: hb.faces.new((prev[0], prev[1], b, a))
            prev = (a, b)
    nl = 0
    front_of = lambda x, z: stree.ray_cast(Vector((x, -0.3, z)), Vector((0, 1, 0)))
    for ic in IRIS_C:
        side = 1 if ic.x > 0 else -1
        # The skin folds back into the socket round the eyeball, so the lid margin is found by stepping
        # up (or down) from the middle of the eye until the skin seen from the front is level with the
        # front of the eye again; lashes grow there.
        for upper, count, lmax in ((True, 70, 0.0075), (False, 35, 0.0038)):
            for k in range(count):
                u = (k + 0.2 + 0.6 * random.random()) / count
                x = ic.x - 0.0135 + 0.027 * u
                root = None
                for j in range(1, 60):
                    z = ic.z + (1 if upper else -1) * 0.00025 * j
                    hit = front_of(x, z)
                    if hit[0] is not None and -hit[0].y > -ic.y - 0.007:
                        root = hit[0]; break
                if root is None: continue
                edge = abs(x - ic.x) / 0.0135                            # 0 in the middle, 1 at the corners
                length = lmax * (0.4 + 0.6 * (1 - edge * edge)) * (0.85 + 0.3 * random.random())
                up = Vector((0, 0, 1 if upper else -1))
                d = (Vector((0, -1, 0)) * 0.85 + up * 0.35 + Vector((x - ic.x, 0, 0)) * 10).normalized()
                strand(root + Vector((0, -0.0002, 0)), d, up * 1.6, length, 0.00013); nl += 1
        # brow: an arch above the eye, thick at the inner end and thinning outward
        for k in range(700):
            u = random.random() ** 0.85
            bx = side * (0.012 + 0.048 * u)
            by = ic.z + 0.0165 + 0.0045 * math.sin(math.pi * min(1.0, u * 1.25)) - 0.003 * u * u
            th = 0.0085 * (1 - 0.65 * u)
            by += (random.random() - 0.5) * th
            hit = front_of(bx, by)
            if hit[0] is None: continue
            p0, nrm = hit[0], hit[1].normalized()
            if nrm.y > 0: nrm = -nrm
            out = Vector((side, 0, 0.55 + (0.3 if u < 0.25 else 0))).normalized()
            t = (out - nrm * out.dot(nrm)).normalized()                  # along the skin
            d = (t + nrm * 0.25).normalized()
            strand(p0 + nrm * 0.00015, d, -nrm * 0.6, 0.006 + 0.004 * random.random(), 0.00012, 3); nl += 1
    sb.free()
    link_bm("Eyelashes and eyebrows", "hair", hb)
    print("HAIR strands", nl)

# The falx (the sheet of dura between the two halves of the brain) is lumpy in the atlas, and a
# midline cut shows it face on: relax it.
for o in work.objects:
    if o.get("label", "").startswith(("Falx cerebri", "Tentorium cerebelli", "Falx cerebelli")):
        b = bmesh.new(); b.from_mesh(o.data)
        inner = [v for v in b.verts if not any(e.is_boundary for e in v.link_edges)]
        for _ in range(12): bmesh.ops.smooth_vert(b, verts=inner, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
        b.to_mesh(o.data); b.free(); print("RELAXED", o["label"])

print("ORAL", [o["label"] for o in work.objects if o.get("cls") in ("oral", "lip", "gingiva", "tongue", "tonsil")])

# Keep it affordable. Simplify here, per tissue, rather than over the whole
# file afterwards: the skin layers are never simplified, because simplifying
# three nested shells separately lets them cross and the fat shows through.
RATIO = {"artery": 0.3, "vein": 0.3, "nerve": 0.3, "brain": 0.35, "muscle": 0.5, "bone": 0.55, "lymph": 0.4,
         "sense": 0.4, "gland": 0.6, "duct": 0.4}
for o in list(work.objects):
    r = RATIO.get(o["cls"])
    n = len(o.data.vertices)
    if not r or n < 400: continue
    d = o.modifiers.new("dec", "DECIMATE"); d.ratio = r
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier="dec")

if not SKIN_IN_MODEL:
    for o in [o for o in work.objects if o.get("cls") in ("epidermis", "dermis", "hypodermis", "hair")]:
        bpy.data.objects.remove(o)
    print("SKIN left out of the model")
from collections import Counter
print("CLASSES", Counter(o["cls"] for o in work.objects))
print("VERTS", sum(len(o.data.vertices) for o in work.objects))
bpy.ops.object.select_all(action="DESELECT")
for o in work.objects: o.select_set(True)
bpy.context.view_layer.objects.active = work.objects[0]
bpy.ops.export_scene.gltf(filepath=OUT, use_selection=True, export_apply=True, export_materials="NONE",
                          export_yup=True, export_normals=True, export_extras=True)
print("EXPORTED", OUT)
