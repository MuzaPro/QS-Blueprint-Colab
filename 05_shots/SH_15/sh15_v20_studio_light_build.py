"""SH_15 v20: studio lighting for the single-cell part of the shot. Builds v20 from v19.

    blender -b --factory-startup --python sh15_v20_studio_light_build.py [-- output.blend]

One control: the empty `StudioLight_CTRL`, custom property `early`
    1 = studio look (single cell)      0 = the user's original lighting (several cells)
It drives three things:
  - Material.004 (dome Icosphere.002): original environment <-> procedural studio bands
  - Point.001   : original spot, its disc was the white blob in the fibre; off while early
  - Point.001_floor_only : same spot, light-linked to the floor panel only, on while early

DON'T re-run over v20 once the user has edited it by hand.
"""
import bpy, os, sys
from math import radians

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sh_15_positioning_and_first_cluster_tile_19.blend")
DST = os.path.join(HERE, "sh_15_positioning_and_first_cluster_tile_20.blend")
if "--" in sys.argv and sys.argv[sys.argv.index("--") + 1:]:
    DST = sys.argv[sys.argv.index("--") + 1]

FADE = [(572, 1.0), (598, 0.0)]     # several cells are in view from 600 on: untouched
CELL = (2.6, 0.0, 0.6)              # the bands are laid out as seen from here
AZ0 = -58.0                         # middle of the early cameras' azimuth around the cell
FLOOR_SPOT = 150.0
GLASS_BOOST = [(1, 7.5), (431, 1.0)] # frame, brightness of the bands just above the horizon (see below).
                                    # From the 431 cut the camera is below the mirror: no boost
BACK = 0.8                          # behind the cell, just above the horizon: the mirror's top rim
ZENITH = 0.10                       # overhead: the dish and the top of the fibre

# name, degrees from AZ0 (+ = screen right), half width, softness, strength, colour
# On the cylinder a band sits at screen position s = sin(offset / 2).
BANDS = [
    ("key left",      -80,  7,  7, 1.5, (1.0, 1.0, 1.0)),
    ("strip right",    70,  4,  6, 1.2, (0.90, 1.0, 0.98)),
    ("soft left",     -44, 10, 16, 0.20, (0.93, 1.0, 0.99)),
    ("soft right",     38,  8, 14, 0.13, (0.93, 1.0, 0.99)),
    ("rim left",     -130,  4,  5, 1.1, (0.88, 1.0, 0.98)),
    ("rim right",     128,  4,  5, 1.0, (1.0, 1.0, 1.0)),
]
BASE = 0.012
TRANSMISSION = 0.70                 # how strongly the bands show through the glass

bpy.ops.wm.open_mainfile(filepath=SRC)
D, S = bpy.data, bpy.context.scene

# ---------------------------------------------------------------- control
ctrl = D.objects.new("StudioLight_CTRL", None)
ctrl.empty_display_type, ctrl.empty_display_size = "SPHERE", 0.4
ctrl.location = (2.6, 0.0, 3.6)
S.collection.objects.link(ctrl)
ctrl["early"] = 1.0
ctrl.id_properties_ui("early").update(min=0, max=1, soft_min=0, soft_max=1,
                                      description="1 = studio look, 0 = original lighting")
for f, v in FADE:
    ctrl["early"] = v
    ctrl.keyframe_insert('["early"]', frame=f)
ctrl["early"] = 1.0
for f, v in GLASS_BOOST:
    ctrl["glass_boost"] = v
    ctrl.keyframe_insert('["glass_boost"]', frame=f)
ctrl.id_properties_ui("glass_boost").update(min=0, max=30, soft_min=0, soft_max=15,
                                            description="Brightness of the bands reflected by the glass fibre")
ctrl["glass_boost"] = GLASS_BOOST[0][1]
for layer in ctrl.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                if fc.data_path == '["glass_boost"]':
                    for k in fc.keyframe_points:
                        k.interpolation = "CONSTANT"


def drive(owner, path, expr, prop="early"):
    d = owner.driver_add(path).driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name = "e"
    v.targets[0].id = ctrl
    v.targets[0].data_path = '["%s"]' % prop
    d.expression = expr


# ---------------------------------------------------------------- spot
spot = D.objects["Point.001"]
floor = D.objects["Cube.001"]
fl = spot.copy()
fl.data = spot.data.copy()
fl.name = fl.data.name = "Point.001_floor_only"
S.collection.objects.link(fl)
lc = D.collections.new("Studio floor light linking")
lc.objects.link(floor)
fl.light_linking.receiver_collection = lc
lc.collection_objects[0].light_linking.link_state = "INCLUDE"
E0 = spot.data.energy
drive(spot.data, "energy", "%g * (1 - e) * (1 - e) * (1 - e) * (1 - e)" % E0)
drive(fl.data, "energy", "%g * e" % FLOOR_SPOT)

# ---------------------------------------------------------------- floor panel
# The half-disc on the mirror was the reflected outline of the black floor panel. While early, the
# panel is invisible to glossy rays, so the cylinder shows the bands down its full height.
fnt = D.materials["Material.006"].node_tree
assert [o.name for o in D.objects if any(m.material == D.materials["Material.006"] for m in o.material_slots)] == ["Cube.001"]
fout = next(n for n in fnt.nodes if n.bl_idname == "ShaderNodeOutputMaterial")
src = fout.inputs["Surface"].links[0].from_socket
flp, ftr, fmx = fnt.nodes.new("ShaderNodeLightPath"), fnt.nodes.new("ShaderNodeBsdfTransparent"), fnt.nodes.new("ShaderNodeMixShader")
fmu = fnt.nodes.new("ShaderNodeMath")
fmu.operation, fmu.label = "MULTIPLY", "hide from reflections (early, driven)"
fnt.links.new(flp.outputs["Is Glossy Ray"], fmu.inputs[0])
drive(fmu.inputs[1], "default_value", "e")
fnt.links.new(fmu.outputs[0], fmx.inputs[0])
fnt.links.new(src, fmx.inputs[1])
fnt.links.new(ftr.outputs[0], fmx.inputs[2])
fnt.links.new(fmx.outputs[0], fout.inputs["Surface"])
for n, xy in ((flp, (-300, 500)), (fmu, (-100, 500)), (ftr, (-100, 320)), (fmx, (120, 480))):
    n.location = xy

# ---------------------------------------------------------------- dome
nt = D.materials["Material.004"].node_tree
old = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeEmission")
targets = [l.to_socket for l in nt.links if l.from_node == old]
made = []


def N(t, label="", **kw):
    n = nt.nodes.new(t)
    n.label = label
    for k, v in kw.items():
        setattr(n, k, v)
    made.append(n)
    return n


def put(sock, v):
    if hasattr(v, "links"):
        nt.links.new(v, sock)
    else:
        sock.default_value = v


def M(op, a, b=None, label="", clamp=False):
    n = N("ShaderNodeMath", label, operation=op, use_clamp=clamp)
    put(n.inputs[0], a)
    if b is not None:
        put(n.inputs[1], b)
    return n.outputs[0]


def smooth(v, a, b, lo, hi, label=""):
    n = N("ShaderNodeMapRange", label, interpolation_type="SMOOTHSTEP")
    put(n.inputs["Value"], v)
    for s, x in (("From Min", a), ("From Max", b), ("To Min", lo), ("To Max", hi)):
        n.inputs[s].default_value = x
    return n.outputs[0]


geo = N("ShaderNodeNewGeometry")
sub = N("ShaderNodeVectorMath", "from the cell", operation="SUBTRACT")
put(sub.inputs[0], geo.outputs["Position"])
sub.inputs[1].default_value = CELL
sep = N("ShaderNodeSeparateXYZ")
put(sep.inputs[0], sub.outputs[0])
az = M("MULTIPLY", M("ARCTAN2", sep.outputs[1], sep.outputs[0]), 57.29578, "azimuth deg")
rel = M("SUBTRACT", az, AZ0)
hor = M("SQRT", M("ADD", M("MULTIPLY", sep.outputs[0], sep.outputs[0]),
                  M("MULTIPLY", sep.outputs[1], sep.outputs[1])))
el = M("MULTIPLY", M("ARCTAN2", sep.outputs[2], hor), 57.29578, "elevation deg")

total = None
for nm, c, hw, so, st, col in BANDS:
    wrap = N("ShaderNodeMath", nm + " distance", operation="WRAP")
    put(wrap.inputs[0], M("SUBTRACT", rel, float(c)))
    wrap.inputs[1].default_value, wrap.inputs[2].default_value = 180.0, -180.0
    k = smooth(M("ABSOLUTE", wrap.outputs[0]), hw, hw + so, st, 0.0, nm)
    vm = N("ShaderNodeVectorMath", nm + " colour", operation="SCALE")
    vm.inputs[0].default_value = col
    put(vm.inputs["Scale"], k)
    if total is None:
        total = vm.outputs[0]
    else:
        ad = N("ShaderNodeVectorMath", operation="ADD")
        put(ad.inputs[0], total)
        put(ad.inputs[1], vm.outputs[0])
        total = ad.outputs[0]
# Seen from the cameras the fibre reflects slightly UP and the mirror slightly DOWN. Glass only
# reflects ~4 %, so the part of the bands above the horizon is boosted: crisp lines on the fibre.
lp = N("ShaderNodeLightPath")
only = M("MULTIPLY", lp.outputs["Is Glossy Ray"], M("SUBTRACT", 1.0, lp.outputs["Is Transmission Ray"]))
gb = N("ShaderNodeValue", "glass boost (driven)")
drive(gb.outputs[0], "default_value", "e", "glass_boost")
boost = M("ADD", 1.0, M("MULTIPLY", M("MULTIPLY", only, smooth(el, 1.5, 5, 0.0, 1.0, "above horizon")),
                        M("SUBTRACT", gb.outputs[0], 1.0)))
shape = M("MULTIPLY", smooth(el, 25, 60, 1.0, 0.0, "fade to zenith"),
          smooth(el, -55, -25, 0.0, 1.0, "fade below"))
sc = N("ShaderNodeVectorMath", operation="SCALE")
put(sc.inputs[0], total)
put(sc.inputs["Scale"], M("MULTIPLY", shape, boost))
ab = N("ShaderNodeVectorMath", "base level", operation="ADD")
put(ab.inputs[0], sc.outputs[0])
ab.inputs[1].default_value = (BASE * 0.8, BASE, BASE)
bw = N("ShaderNodeMath", "back distance", operation="WRAP")
put(bw.inputs[0], M("SUBTRACT", rel, 180.0))
bw.inputs[1].default_value, bw.inputs[2].default_value = 180.0, -180.0
bk = M("MULTIPLY", smooth(M("ABSOLUTE", bw.outputs[0]), 20, 60, BACK, 0.0, "back glow"),
       M("MULTIPLY", smooth(el, 0.5, 5, 0.0, 1.0), smooth(el, 14, 28, 1.0, 0.0)))
bk = M("MULTIPLY", bk, lp.outputs["Is Glossy Ray"], "reflections only")
bk = M("MULTIPLY", bk, M("SUBTRACT", 1.0, lp.outputs["Is Transmission Ray"]))
extra = M("ADD", bk, smooth(el, 45, 75, 0.0, ZENITH, "zenith"))
ex = N("ShaderNodeVectorMath", "back + zenith", operation="SCALE")
ex.inputs[0].default_value = (0.9, 1.0, 0.99)
put(ex.inputs["Scale"], extra)
ax = N("ShaderNodeVectorMath", operation="ADD")
put(ax.inputs[0], ab.outputs[0])
put(ax.inputs[1], ex.outputs[0])
tr = M("SUBTRACT", 1.0, M("MULTIPLY", lp.outputs["Is Transmission Ray"], 1.0 - TRANSMISSION), "dimmer through glass")
em = N("ShaderNodeEmission", "STUDIO BANDS")
put(em.inputs["Color"], ax.outputs[0])
put(em.inputs["Strength"], tr)
val = N("ShaderNodeValue", "early (driven)")
drive(val.outputs[0], "default_value", "e")
mix = N("ShaderNodeMixShader", "original / studio")
put(mix.inputs[0], val.outputs[0])
put(mix.inputs[1], old.outputs[0])
put(mix.inputs[2], em.outputs[0])
for t in targets:
    nt.links.new(mix.outputs[0], t)
fr = nt.nodes.new("NodeFrame")
fr.label = "v20 studio bands (early part of the shot)"
for i, n in enumerate(made):
    n.parent = fr
    n.location = (-2200 + (i % 8) * 200, -900 - (i // 8) * 200)

# the cards' text showed up mirrored in the metal
for n in ("Card_13-14_v2", "Card_15"):
    D.objects[n].visible_glossy = False

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("BUILT OK", DST)
