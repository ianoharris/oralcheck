import bpy, re, sys
OUT = sys.argv[sys.argv.index("--")+1]
keep_exact = {"Mandible","Maxilla.l","Maxilla.r","Gingiva","Tongue","Soft palate","Uvula of palate","Hyoid bone",
              "Palatine tonsil.l","Palatine tonsil.r","Submandibular gland.l","Submandibular gland.r",
              "Sublingual gland.l","Sublingual gland.r","Submandibular nodes.l","Submandibular nodes.r",
              "Mylohyoid muscle.l","Mylohyoid muscle.r","Geniohyoid muscle.l","Geniohyoid muscle.r","Palatine bone.l","Palatine bone.r"}
tooth = re.compile(r"^(Upper|Lower) .*(incisor|canine|premolar|molar tooth)\.(l|r)$")
keep = [o for o in bpy.data.objects if o.type=="MESH" and (o.name in keep_exact or tooth.match(o.name))]
print("KEEP", len(keep))
bpy.ops.object.select_all(action="DESELECT")
for o in keep:
    o.hide_set(False); o.hide_viewport=False; o.hide_render=False
    o.select_set(True)
    if o.name in ("Tongue","Soft palate","Uvula of palate","Palatine tonsil.l","Palatine tonsil.r"):
        m=o.modifiers.new("smooth","SUBSURF"); m.levels=2; m.render_levels=2
    for p in o.data.polygons: p.use_smooth=True
bpy.context.view_layer.objects.active = keep[0]
bpy.ops.export_scene.gltf(filepath=OUT, use_selection=True, export_apply=True, export_materials="NONE",
                          export_yup=True, export_normals=True)
print("EXPORTED", OUT)
