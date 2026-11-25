"""SH_15 v21: subtle resonance in the photonic mode. Builds v21 from v20.

    blender -b --factory-startup --python sh15_v21_resonance_build.py [-- output.blend]

Only the hero cell (PhotonMode.004) gets it: it receives its own copy of the node group and of the
volume material, so the four cells of the cluster part stay exactly as they were.
The lobes don't move. Their brightness is modulated by a soft bright region that travels between the
two mirrors at constant speed and reflects (it overlaps with its own mirror image at each end).

Controls: custom properties on PhotonMode.004
DON'T re-run over v21 once the user has edited it by hand.
"""
import bpy, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sh_15_positioning_and_first_cluster_tile_20.blend")
DST = os.path.join(HERE, "sh_15_positioning_and_first_cluster_tile_21.blend")
if "--" in sys.argv and sys.argv[sys.argv.index("--") + 1:]:
    DST = sys.argv[sys.argv.index("--") + 1]

START = 276                              # the mode appears at 273-276
PROPS = [
    ("resonance",        1.0,  0.0, 1.0,  "Overall amount, keyed. 0 = the old static mode"),
    ("res_depth",        0.68, 0.0, 0.95, "How much the lobes dim (and brighten) around their old value"),
    ("res_round_trip",   45.0, 5.0, 500., "Frames for one trip up and down"),
    ("res_width",        0.30, 0.05, 1.0, "Length of the bright region, in cavity lengths"),
]
KEYS = [(276, 0.0), (300, 1.0), (560, 1.0), (578, 0.0)]
# from the 431 cut the mode is seen as one solid shape and the card teaches "highest in the centre":
# less depth there, so the shape doesn't turn into a funnel
DEPTH_KEYS = [(276, 0.68), (431, 0.34)]  # constant interpolation

bpy.ops.wm.open_mainfile(filepath=SRC)
D = bpy.data
ob = D.objects["PhotonMode.004"]

for nm, v, lo, hi, tip in PROPS:
    ob[nm] = v
    ob.id_properties_ui(nm).update(min=lo, max=hi, soft_min=lo, soft_max=hi, description=tip)
for f, v in KEYS:
    ob["resonance"] = v
    ob.keyframe_insert('["resonance"]', frame=f)

for f, v in DEPTH_KEYS:
    ob["res_depth"] = v
    ob.keyframe_insert('["res_depth"]', frame=f)
for layer in ob.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                if fc.data_path == '["res_depth"]':
                    for k in fc.keyframe_points:
                        k.interpolation = "CONSTANT"

# ---------------------------------------------------------------- hero copies
mod = ob.modifiers["GeometryNodes"]
shared = mod.node_group
keep = {i.identifier: getattr(mod.properties.inputs, i.identifier).value
        for i in shared.interface.items_tree
        if i.item_type == "SOCKET" and i.in_out == "INPUT" and i.socket_type != "NodeSocketGeometry"}
mat = D.materials["Photon_Volume"].copy()
mat.name = "Photon_Volume_hero_resonance"
ng = shared.copy()
ng.name = "PhotonMode_hero"
next(n for n in ng.nodes if n.bl_idname == "GeometryNodeSetMaterial").inputs["Material"].default_value = mat
mod.node_group = ng
for k, v in keep.items():
    getattr(mod.properties.inputs, k).value = v
for s in ob.material_slots:
    if s.material and s.material.name == "Photon_Volume":
        s.link = "OBJECT"
        s.material = mat

# ---------------------------------------------------------------- shader
nt = mat.node_tree
scat = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeVolumeScatter")
base = scat.inputs["Density"].links[0].from_socket
made = []


def N(t, label="", **kw):
    n = nt.nodes.new(t)
    n.label = label
    for k, v in kw.items():
        setattr(n, k, v)
    made.append(n)
    return n


def put(s, v):
    if hasattr(v, "links"):
        nt.links.new(v, s)
    else:
        s.default_value = v


def M(op, a, b=None, c=None, label=""):
    n = N("ShaderNodeMath", label, operation=op)
    for i, v in enumerate((a, b, c)):
        if v is not None:
            put(n.inputs[i], v)
    return n.outputs[0]


def prop(nm):
    return N("ShaderNodeAttribute", nm, attribute_type="OBJECT", attribute_name=nm).outputs["Fac"]


tc = N("ShaderNodeTexCoord")
sep = N("ShaderNodeSeparateXYZ")
put(sep.inputs[0], tc.outputs["Object"])
s = M("ADD", M("MULTIPLY", sep.outputs[2], 0.5), 0.5, label="height 0..1 (mirror..fibre)")
phase = N("ShaderNodeValue", "round trips (driven)")
d = phase.outputs[0].driver_add("default_value").driver
d.type = "SCRIPTED"
var = d.variables.new()
var.name = "t"
var.targets[0].id = ob
var.targets[0].data_path = '["res_round_trip"]'
d.expression = "(frame - %d) / t" % START
# a trip up and down is a circle of length 2: going up at s, coming down at 2 - s
p = M("MULTIPLY", M("FRACT", phase.outputs[0]), 2.0, label="photon, 0..2")


def bump(where, label):
    w = N("ShaderNodeMath", label, operation="WRAP")
    put(w.inputs[0], M("SUBTRACT", where, p))
    w.inputs[1].default_value, w.inputs[2].default_value = 1.0, -1.0
    q = M("DIVIDE", w.outputs[0], prop("res_width"))
    return M("EXPONENT", M("MULTIPLY", M("MULTIPLY", q, q), -1.0), label=label + " glow")


up = bump(s, "going up")
down = bump(M("SUBTRACT", 2.0, s), "coming down")
near = M("MAXIMUM", up, down, label="bright region 0..1")
signed = M("SUBTRACT", M("MULTIPLY", near, 2.0), 1.0, label="-1 dim .. +1 bright")
amt = M("MULTIPLY", prop("resonance"), prop("res_depth"))
gain = M("ADD", 1.0, M("MULTIPLY", signed, amt), label="gain")
put(scat.inputs["Density"], M("MULTIPLY", base, gain, label="lobes x gain"))
fr = nt.nodes.new("NodeFrame")
fr.label = "v21 resonance"
for i, n in enumerate(made):
    n.parent = fr
    n.location = (-1500 + (i % 7) * 200, -400 - (i // 7) * 180)

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("BUILT OK", DST, [i.identifier for i in ng.interface.items_tree if i.item_type == "SOCKET"], keep)
