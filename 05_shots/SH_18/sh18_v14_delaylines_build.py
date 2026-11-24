"""SH_18 v14: waveguide clean-up after the user's generator edit + delay-line photons.

Run:
  blender --factory-startup -b sh_18_architecture_intro_13.blend --python sh18_v14_delaylines_build.py
  -> saves sh_18_architecture_intro_14.blend
then re-bake both glows on v14 (photon paths changed):
  blender --factory-startup -b sh_18_architecture_intro_14.blend --python sh18_v10_photons_snspd_build.py -- rebake
  blender --factory-startup -b sh_18_architecture_intro_14.blend --python sh18_v12_cells_glass_build.py -- rebake

1. Fixes
   - Curve_Waveguide.001 tube material Glass_Mat -> Photon_Glass (Glass_Mat = milky,
     volume density 5.6, empty texture on base colour: that was the darker guide).
   - Removes the target-less "Hook-Curve_Parent_01" modifiers on .001 / .004 (did nothing).
   - Adds the 3 active guides to GlassEnv_receivers (shot-15 reflection sphere).
   - scene.frame_start 2868 -> 2744 (delivery range 2744-3278).
2. Node group "Curve waveguide fixed": new input "end fade" (curve-factor length,
   0 = off). Photons scale (and, via the 'fade' attribute the photon shader reads,
   fade) from 0 to full over that length at both ends of the curve. Main guides keep 0.
3. Delay lines: three new guides DelayLine_Outer / _Middle / _Inner (collection
   "DelayLines"). Each rides one of the nested U lines of the "DELAY LINES" sketch
   (coordinates measured from the 4K architecture texture): starts inside the
   entangling-cells wafer on the right, runs down past the router, loops once around
   each of the 3 spool circles on its U's bottom edge, runs up the left side and ends
   inside the wafer. Photons fade in / out at the ends (end fade).
   Timing is explicit (linear movement, uniform gap): see DELAY.
   Story: a photon is sent off the chip into a km-long fibre spool so it can be
   entangled with the next clock cycle of photons (more efficient cluster generation).
"""
import bpy, math, os
from mathutils import Vector

HERE = os.path.dirname(bpy.data.filepath)
OUT = os.path.join(HERE, "sh_18_architecture_intro_14.blend")
scene = bpy.context.scene
O = bpy.data.objects
GROUP = "Curve waveguide fixed"
MAIN = ["Curve_Waveguide.001", "Curve_Waveguide.002", "Curve_Waveguide.004"]
Z = 0.67                       # height of all photon guides
Y_WAFER = 0.9                  # start/end inside the wafer (its bottom edge is y 0.21)
SPOOL_X = (-10.06, -10.58, -11.10)   # right, middle, left circle centres
SPOOL_R = 0.43
SPEED = 0.6                    # m / frame (main photons average ~0.6-0.7)
FADE_M = 1.0                   # metres of fade at each end
# name: (x right, x left, y bottom, first entry frame, interval frames, photon count)
DELAY = {
    "DelayLine_Outer":  (-6.91, -14.24, -13.08, 2850, 170, 3),
    "DelayLine_Middle": (-8.02, -13.13, -11.97, 2905, 170, 3),
    "DelayLine_Inner":  (-9.13, -12.02, -10.85, 2960, 170, 2),
}


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


# ---------------------------------------------------------------- 1. fixes
g001 = O["Curve_Waveguide.001"].modifiers["GeometryNodes"]
set_in(g001, "Material", bpy.data.materials["Photon_Glass"])
for nm in ("Curve_Waveguide.001", "Curve_Waveguide.004"):
    for m in list(O[nm].modifiers):
        if m.type == 'HOOK' and m.object is None:
            O[nm].modifiers.remove(m)
rc = bpy.data.collections["GlassEnv_receivers"]
for nm in MAIN:
    if nm not in rc.objects:
        rc.objects.link(O[nm])
scene.frame_start = 2744
# final frames go to their own folder (Render/sh_18_architecture/ holds old v08 frames)
scene.render.filepath = "//Render/sh_18_architecture_v14/sh_18_architecture_v14_"
print("fixes done")

# ---------------------------------------------------------------- 2. end fade in the node group
ng = bpy.data.node_groups[GROUP]
N, L = ng.nodes, ng.links
if iface(ng, "end fade") is None:
    it = ng.interface.new_socket("end fade", in_out='INPUT', socket_type='NodeSocketFloat')
    it.default_value = 0.0; it.min_value = 0.0; it.max_value = 0.5
if "EF_scale" not in N:
    dele, rot = N["Delete Geometry"], N["Rotate Instances"]
    x, y = dele.location.x, dele.location.y - 350
    gi = N.new('NodeGroupInput'); gi.location = (x - 200, y - 200)
    na = N.new('GeometryNodeInputNamedAttribute'); na.data_type = 'FLOAT'
    na.inputs["Name"].default_value = "progression"; na.location = (x - 200, y)

    def mth(op, a, b, dx, dy=0):
        m = N.new('ShaderNodeMath'); m.operation = op; m.location = (x + dx, y + dy)
        for i, v in ((0, a), (1, b)):
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                L.new(v, m.inputs[i])
        return m.outputs[0]

    prog = na.outputs["Attribute"]
    ef = gi.outputs["end fade"]
    a = mth('DIVIDE', prog, ef, 0)
    b = mth('DIVIDE', mth('SUBTRACT', 1.0, prog, 0, -150), ef, 150, -150)
    mn = mth('MINIMUM', a, b, 300)
    mr = N.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; mr.location = (x + 450, y)
    L.new(mn, mr.inputs["Value"])
    on = mth('GREATER_THAN', ef, 0.0, 450, -200)
    sw = N.new('GeometryNodeSwitch'); sw.input_type = 'FLOAT'; sw.location = (x + 650, y)
    L.new(on, sw.inputs["Switch"]); sw.inputs["False"].default_value = 1.0
    L.new(mr.outputs["Result"], sw.inputs["True"])
    sc = N.new('GeometryNodeScaleInstances'); sc.name = sc.label = "EF_scale"; sc.location = (x + 850, y + 200)
    for lk in list(L):
        if lk.from_node == dele and lk.to_node == rot:
            L.remove(lk)
    L.new(dele.outputs[0], sc.inputs["Instances"])
    L.new(sw.outputs[0], sc.inputs["Scale"])
    L.new(sc.outputs[0], rot.inputs["Instances"])
    print("end fade nodes built")

# ---------------------------------------------------------------- 3. delay-line guides
coll = bpy.data.collections.get("DelayLines") or bpy.data.collections.new("DelayLines")
if coll.name not in scene.collection.children:
    scene.collection.children.link(coll)
template = O["Curve_Waveguide.002"]          # no hook, same group + inputs as the main guides


def path(xr, xl, yb):
    pts = [(xr, Y_WAFER, 0.30), (xr, yb, 0.30)]          # (x, y, fillet radius)
    for cx in SPOOL_X:                                    # right -> left
        pts.append((cx + SPOOL_R, yb, 0.0))
        for k in range(1, 25):                            # one full turn, CCW from the right point
            a = math.radians(15 * k)
            pts.append((cx + SPOOL_R * math.cos(a), yb + SPOOL_R * math.sin(a), 0.0))
    pts += [(xl, yb, 0.30), (xl, Y_WAFER, 0.30)]
    return pts


for name, (xr, xl, yb, t0, interval, count) in DELAY.items():
    if name in O:
        bpy.data.objects.remove(O[name], do_unlink=True)
    cd = bpy.data.curves.new(name, 'CURVE'); cd.dimensions = '3D'
    sp = cd.splines.new('POLY')
    pts = path(xr, xl, yb)
    sp.points.add(len(pts) - 1)
    for p, (x, y, r) in zip(sp.points, pts):
        p.co = (x, y, Z, 1.0); p.radius = r
    length = sum((Vector(pts[i][:2]) - Vector(pts[i - 1][:2])).length for i in range(1, len(pts)))
    ob = template.copy(); ob.data = cd; ob.name = name
    ob.animation_data_clear()
    ob.parent = None; ob.matrix_world.identity()
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)
    mod = ob.modifiers["GeometryNodes"]
    dur = length / SPEED                                  # frames for one traversal
    set_in(mod, "OBJ count", count)
    set_in(mod, "distance between OBJ", -(interval / dur))  # uniform gap = interval in curve factor
    set_in(mod, "spacing randomness", 0.0)
    set_in(mod, "min gap", 0.0)
    set_in(mod, "max gap", 100.0)
    set_in(mod, "end fade", FADE_M / length)
    set_in(mod, "Material", bpy.data.materials["Photon_Glass"])
    ident = iface(mod.node_group, "movement progression").identifier
    dp = f'modifiers["GeometryNodes"].properties.inputs.{ident}.value'
    set_in(mod, "movement progression", 0.0)
    ob.keyframe_insert(dp, frame=t0)
    set_in(mod, "movement progression", 1.0)
    ob.keyframe_insert(dp, frame=t0 + dur)
    for fc in fcurves_of(ob):
        fc.extrapolation = 'LINEAR'
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'
        fc.update()
    entries = [round(t0 + i * interval) for i in range(count)]
    print(f"{name}: length {length:.1f} m, traversal {dur:.0f} f, photons enter at {entries}, "
          f"leave at {[round(e + dur) for e in entries]}")

scene.frame_set(scene.frame_start)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
