"""SH_18 v14 (in place): denser delay-line photon traffic.

Run:
  blender --factory-startup -b sh_18_architecture_intro_14.blend --python sh18_v14_delay_density.py
  -> re-saves sh_18_architecture_intro_14.blend. Touches ONLY DelayLine_* objects: the main guides
     and the baked SNSPD / cell glows are untouched (delay photons are not part of those bakes).

Each loop gets random (Poisson-like) spacing instead of fixed entry times, starting well
before the shot so the lines are already populated at 2744. Target: ~2-4 photons on the
three loops at any frame. Prints the per-frame count for the delivery range.
"""
import bpy
from mathutils import Vector

scene = bpy.context.scene
O = bpy.data.objects
SPEED = 0.6            # m/frame, same as v14 build
T0 = 2560              # first photon enters here (pre-roll so 2744 is already busy)
COUNT = 24             # photons per loop (more than enough to reach 3278)
# name: (mean interval, min interval, max interval) in frames, seed
LOOPS = {
    "DelayLine_Outer":  ((48, 14, 110), 101),
    "DelayLine_Middle": ((48, 14, 110), 202),
    "DelayLine_Inner":  ((48, 14, 110), 303),
}
F0, F1 = 2744, 3278


def iface(ng, name):
    for it in ng.interface.items_tree:
        if it.item_type == 'SOCKET' and it.in_out == 'INPUT' and it.name == name:
            return it


def set_in(mod, name, value):
    mod.properties.inputs[iface(mod.node_group, name).identifier]["value"] = value


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


for name, ((mean, mn, mx), seed) in LOOPS.items():
    ob = O[name]
    sp = ob.data.splines[0]
    pts = [p.co.xyz for p in sp.points]
    length = sum((pts[i] - pts[i - 1]).length for i in range(1, len(pts)))
    dur = length / SPEED
    mod = ob.modifiers["GeometryNodes"]
    set_in(mod, "OBJ count", COUNT)
    set_in(mod, "spacing randomness", 1.0)
    set_in(mod, "distance between OBJ", -(mean / dur))
    set_in(mod, "min gap", mn / dur)
    set_in(mod, "max gap", mx / dur)
    set_in(mod, "spacing seed", seed)
    ident = iface(mod.node_group, "movement progression").identifier
    dp = f'modifiers["GeometryNodes"].properties.inputs.{ident}.value'
    if ob.animation_data:
        ob.animation_data_clear()
    set_in(mod, "movement progression", 0.0); ob.keyframe_insert(dp, frame=T0)
    set_in(mod, "movement progression", 1.0); ob.keyframe_insert(dp, frame=T0 + dur)
    for fc in fcurves_of(ob):
        fc.extrapolation = 'LINEAR'
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'
        fc.update()
    ob.update_tag()
    print(f"{name}: traversal {dur:.0f} f, mean interval {mean} f")

# ---- verify: photons (heads) on the loops per frame
counts = []
for f in range(F0, F1 + 1):
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    n = 0
    for name in LOOPS:
        gs = O[name].evaluated_get(dg).evaluated_geometry()   # keep a ref, or the pointcloud is freed
        pc = gs.instances_pointcloud()
        if pc is not None and "photon_offset" in pc.attributes:
            n += len({round(a.value, 6) for a in pc.attributes["photon_offset"].data})
    counts.append(n)
hist = {k: counts.count(k) for k in sorted(set(counts))}
print("photons on delay lines per frame: min", min(counts), "max", max(counts),
      "mean %.2f" % (sum(counts) / len(counts)), "histogram", hist)
scene.frame_set(scene.frame_start)
bpy.ops.wm.save_mainfile()
print("SAVED", bpy.data.filepath)
