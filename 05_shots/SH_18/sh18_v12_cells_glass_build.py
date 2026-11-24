"""SH_18 v12: entangling-cell circles light up as photons pass + glass cavities read as glass.

Run:
  blender --factory-startup -b sh_18_architecture_intro_11.blend --python sh18_v12_cells_glass_build.py
  -> saves sh_18_architecture_intro_12.blend (v11 stays untouched)
Re-bake only the circle glow (after changing photon spacing/speed):
  blender --factory-startup -b sh_18_architecture_intro_12.blend --python sh18_v12_cells_glass_build.py -- rebake

A. Unit-cell glow
   The 12 "glowing-diagram-circle*" planes (collection glowing-circle-diagram, cut
   from the architecture texture, sitting under each optic-fiber-cavity) get their own
   copy of the texture material, "uc-circle-glow". Its emission is
     base_strength * (OFF_LEVEL + ON_BOOST * uc_glow)
   and tints towards the photon cyan when on. uc_glow is an OBJECT attribute = a
   custom property on each circle, baked per half-frame from the real photon
   positions (evaluated GN instances of the 3 guides): Gaussian falloff of the
   distance (XY) from the circle centre to the nearest photon, instant attack,
   exponential release. Photons run left->right, so the cells of a row switch on
   one after the other.

B. Glass cavities (material Photon_Glass, used by optic-fiber-cavity, Cylinder.001,
   entangling-cells-wafer slot 2)
   1. Volume Scatter density 3.43 -> 0.4 (the value in the shot-15 asset
      04_assets/props/unit_cell_v7.blend). 3.43 made them milky grey.
   2. Reflection environment from shot 15: the hidden emissive sphere with the two
      packed studio HDRIs (window light + ring strips) is appended as
      "GlassEnv_Sphere". Invisible to camera and diffuse; light-linked so it only
      lights the objects in collection "GlassEnv_receivers" (glass parts), so the
      floor / sketch / cards keep their current look.
"""
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
REBAKE_ONLY = "rebake" in argv
HERE = os.path.dirname(bpy.data.filepath)
OUT = os.path.join(HERE, "sh_18_architecture_intro_12.blend")
SH15 = os.path.normpath(os.path.join(HERE, "..", "SH_15", "sh_15_positioning_and_first_cluster_tile_18.blend"))
scene = bpy.context.scene
O = bpy.data.objects

GUIDES = ["Curve_Waveguide.001", "Curve_Waveguide.002", "Curve_Waveguide.004"]
CIRCLE_COLL = "glowing-circle-diagram"
SRC_MAT = "08b_Card_Architecture-simplified_still_v3_4K"
UC_MAT = "uc-circle-glow"

# ---- look settings ---------------------------------------------------------
OFF_LEVEL = 0.15          # circle emission when no photon is near (x original)
ON_BOOST = 3.0            # added at uc_glow = 1
ON_COLOR = (0.613, 0.947, 0.986, 1.0)   # photon cyan
PROX_RADIUS = 0.6        # m, Gaussian sigma-ish of the proximity falloff (circle r = 0.58)
RELEASE_FRAMES = 2.0      # e-folding of the switch-off
GLASS_VOLUME_DENSITY = 0.4
ENV_STRENGTH = 1.2        # emission strength of the reflection sphere (shot 15 = 1.2)
ENV_RADIUS = 22.0         # m
GLASS_RECEIVERS = ["optic-fiber-cavity", "Cylinder.001",
                   "Curve_Waveguide.003", "Curve_Waveguide.005", "Curve_Waveguide.006"]
# (wafer slabs entangling-cells-wafer / Plane.003 left out on purpose: they went milky white)
CELL_LIGHT_W = 25.0       # W of the teal point light in a cell at uc_glow = 1 (like shot 15 PhotonMode_Light)
CELL_LIGHT_Z = 0.25       # between the circle (z -0.06) and the wafer underside (~0.27)
CELL_LIGHT_RADIUS = 0.25
CELL_LIGHT_COLOR = (0.57, 0.95, 0.85)


def fcurves_of(idb):
    ad = idb.animation_data
    if not ad or not ad.action:
        return []
    try:
        return list(ad.action.fcurves)
    except Exception:
        out = []
        for l in ad.action.layers:
            for s in l.strips:
                for cb in s.channelbags:
                    out += list(cb.fcurves)
        return out


def circles():
    return sorted(bpy.data.collections[CIRCLE_COLL].objects, key=lambda o: o.name)


def centre(o):
    bb = [o.matrix_world @ Vector(b) for b in o.bound_box]
    return sum(bb, Vector()) / 8


# ---------------------------------------------------------------- A1. material
def build_uc_material():
    if UC_MAT in bpy.data.materials:
        mat = bpy.data.materials[UC_MAT]
    else:
        mat = bpy.data.materials[SRC_MAT].copy()
        mat.name = UC_MAT
        N, L = mat.node_tree.nodes, mat.node_tree.links
        bsdf = next(n for n in N if n.bl_idname == 'ShaderNodeBsdfPrincipled')
        strength_src = bsdf.inputs["Emission Strength"].links[0].from_socket   # ramp * 6.3
        L.remove(bsdf.inputs["Emission Strength"].links[0])
        x, y = bsdf.location.x - 700, bsdf.location.y - 500
        at = N.new('ShaderNodeAttribute'); at.name = at.label = "UC_glow_attr"
        at.attribute_type = 'OBJECT'; at.attribute_name = "uc_glow"; at.location = (x - 400, y)
        lvl = N.new('ShaderNodeMath'); lvl.operation = 'MULTIPLY_ADD'; lvl.name = lvl.label = "UC_level"
        lvl.inputs[1].default_value = ON_BOOST; lvl.inputs[2].default_value = OFF_LEVEL; lvl.location = (x - 150, y)
        L.new(at.outputs["Fac"], lvl.inputs[0])
        mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.name = mul.label = "UC_strength"; mul.location = (x + 100, y)
        L.new(strength_src, mul.inputs[0]); L.new(lvl.outputs[0], mul.inputs[1])
        L.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
        mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.name = mix.label = "UC_tint"; mix.location = (x + 100, y - 250)
        mix.inputs["A"].default_value = (1, 1, 1, 1)
        mix.inputs["B"].default_value = ON_COLOR
        L.new(at.outputs["Fac"], mix.inputs["Factor"])
        L.new(mix.outputs["Result"], bsdf.inputs["Emission Color"])
    for o in circles():
        o.material_slots[0].link = 'OBJECT'
        o.material_slots[0].material = mat
        o["uc_glow"] = 0.0
    print("uc material on", len(circles()), "circles")


# ---------------------------------------------------------------- A2. bake
def photon_positions_world(obj, dg):
    gs = obj.evaluated_get(dg).evaluated_geometry()
    pc = gs.instances_pointcloud()
    if pc is None or "instance_transform" not in pc.attributes:
        return []
    mw = obj.matrix_world
    # NB: pc.points[i].co is garbage in 5.2 - the real positions are in instance_transform
    return [mw @ Vector(m.value.translation) for m in pc.attributes["instance_transform"].data]


def bake_uc():
    f0, f1 = scene.frame_start - 150, scene.frame_end
    cs = circles()
    cxy = [centre(c).xy for c in cs]
    steps = []
    f = f0
    while f <= f1:
        steps.append(f); f += 0.5
    env = [0.0] * len(cs)
    vals = {c.name: [] for c in cs}
    rel = math.exp(-0.5 / RELEASE_FRAMES)
    for t in steps:
        scene.frame_set(int(t), subframe=t - int(t))
        dg = bpy.context.evaluated_depsgraph_get()
        pts = []
        for g in GUIDES:
            pts += [p.xy for p in photon_positions_world(O[g], dg)]
        for i, c in enumerate(cs):
            d2 = min(((p - cxy[i]).length_squared for p in pts), default=1e9)
            prox = math.exp(-d2 / (PROX_RADIUS ** 2))
            env[i] = max(prox, env[i] * rel)
            if t == int(t):
                vals[c.name].append((int(t), env[i]))
    for c in cs:
        c["uc_glow"] = 0.0
        c.keyframe_insert('["uc_glow"]', frame=scene.frame_start)
        fc = next(x for x in fcurves_of(c) if x.data_path == '["uc_glow"]')
        fc.keyframe_points.clear()
        keys = [(fr, v if v > 0.01 else 0.0) for fr, v in vals[c.name]]
        kept = [k for i, k in enumerate(keys)
                if k[1] > 0 or i in (0, len(keys) - 1) or keys[i - 1][1] > 0 or keys[i + 1][1] > 0]
        fc.keyframe_points.add(len(kept))
        for kp, (fr, v) in zip(fc.keyframe_points, kept):
            kp.co = (fr, v); kp.interpolation = 'LINEAR'
        fc.update()
        on = [fr for i, (fr, v) in enumerate(keys) if v > 0.5 and (i == 0 or keys[i - 1][1] <= 0.5)]
        print(f"{c.name}: {len(on)} switch-ons, first {on[:6]}")


# ---------------------------------------------------------------- B. glass
def fix_glass():
    mat = bpy.data.materials["Photon_Glass"]
    for n in mat.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeVolumeScatter':
            print("glass volume density", n.inputs["Density"].default_value, "->", GLASS_VOLUME_DENSITY)
            n.inputs["Density"].default_value = GLASS_VOLUME_DENSITY


def add_env_sphere():
    if "GlassEnv_Sphere" in O:
        sph = O["GlassEnv_Sphere"]
    else:
        with bpy.data.libraries.load(SH15, link=False) as (src, dst):
            dst.objects = ["Icosphere.002"]
        sph = dst.objects[0]
        sph.name = "GlassEnv_Sphere"
        sph.data.name = "GlassEnv_Sphere"
        sph.active_material.name = "GlassEnv_HDRI"
        coll = bpy.data.collections.get("GlassEnv") or bpy.data.collections.new("GlassEnv")
        if coll.name not in scene.collection.children:
            scene.collection.children.link(coll)
        coll.objects.link(sph)
    for im in bpy.data.images:
        if im.filepath and "HDRI" in im.filepath and not im.packed_file:
            print("WARNING image not packed:", im.filepath)
    sph.parent = None
    sph.animation_data_clear()
    wafer = O["entangling-cells-wafer"]
    sph.location = wafer.matrix_world.translation + Vector((0, 0, 0))
    r0 = max(sph.dimensions) / 2 / max(sph.scale)
    s = ENV_RADIUS / r0
    sph.scale = (s, s, s)
    sph.visible_camera = False
    sph.visible_diffuse = False
    sph.visible_shadow = False
    sph.visible_volume_scatter = False
    sph.visible_glossy = True
    sph.visible_transmission = True
    sph.hide_render = False
    em = next(n for n in sph.active_material.node_tree.nodes if n.bl_idname == 'ShaderNodeEmission')
    em.inputs["Strength"].default_value = ENV_STRENGTH
    # light linking: sphere only lights the glass parts
    rc = bpy.data.collections.get("GlassEnv_receivers") or bpy.data.collections.new("GlassEnv_receivers")
    for nm in GLASS_RECEIVERS:
        if nm in O and nm not in rc.objects:
            rc.objects.link(O[nm])
    sph.light_linking.receiver_collection = rc
    # the receivers collection is only a link set: keep it out of the scene tree
    print("env sphere radius", ENV_RADIUS, "receivers", [o.name for o in rc.objects])


def add_cell_lights():
    """One teal point light per cell, energy driven by that circle's uc_glow."""
    coll = bpy.data.collections.get("UC_lights") or bpy.data.collections.new("UC_lights")
    if coll.name not in scene.collection.children:
        scene.collection.children.link(coll)
    for c in circles():
        nm = "UC_light" + c.name[len("glowing-diagram-circle"):]
        lo = O.get(nm)
        if lo is None:
            ld = bpy.data.lights.new(nm, 'POINT')
            lo = bpy.data.objects.new(nm, ld)
            coll.objects.link(lo)
        ld = lo.data
        ld.color = CELL_LIGHT_COLOR
        ld.shadow_soft_size = CELL_LIGHT_RADIUS
        ld.use_shadow = True
        p = centre(c)
        lo.location = (p.x, p.y, CELL_LIGHT_Z)
        lo["max_watts"] = CELL_LIGHT_W
        if ld.animation_data:
            ld.animation_data_clear()
        fc = ld.driver_add("energy")
        d = fc.driver; d.type = 'SCRIPTED'; d.expression = "g * w"
        v = d.variables.new(); v.name = "g"; v.type = 'SINGLE_PROP'
        v.targets[0].id_type = 'OBJECT'; v.targets[0].id = c; v.targets[0].data_path = '["uc_glow"]'
        v = d.variables.new(); v.name = "w"; v.type = 'SINGLE_PROP'
        v.targets[0].id_type = 'OBJECT'; v.targets[0].id = lo; v.targets[0].data_path = '["max_watts"]'
    print("cell lights:", len(circles()))


# ---------------------------------------------------------------- run
if not REBAKE_ONLY:
    build_uc_material()
    fix_glass()
    add_env_sphere()
    add_cell_lights()
bake_uc()
scene.frame_set(scene.frame_start)
dst = bpy.data.filepath if REBAKE_ONLY else OUT
bpy.ops.wm.save_as_mainfile(filepath=dst)
print("SAVED", dst)
