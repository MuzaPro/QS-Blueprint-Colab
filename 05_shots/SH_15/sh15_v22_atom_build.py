"""SH_15 v22: the hero atom as a nucleus + S-orbital cloud that also reads as the card's dot and circle.
Builds v22 from v21.

    blender -b --factory-startup --python sh15_v22_atom_build.py [-- output.blend]

Everything is computed in one surface shader on a bounding sphere, from the distance at which the line
of sight passes the centre. So the dot and the circle face every camera, in any view, without noise.
The cloud is a ball of points: five slices through the sphere along the line of sight.

Only Icosphere.001 (the hero atom) changes. The cluster's atoms keep the old `atom` material.
Controls: custom properties on Icosphere.001.
DON'T re-run over v22 once the user has edited it by hand.
"""
import bpy, bmesh, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sh_15_positioning_and_first_cluster_tile_21.blend")
DST = os.path.join(HERE, "sh_15_positioning_and_first_cluster_tile_22.blend")
if "--" in sys.argv and sys.argv[sys.argv.index("--") + 1:]:
    DST = sys.argv[sys.argv.index("--") + 1]

BOUND = 0.085          # bounding sphere; atom_radius must stay below about 0.07
PROPS = [
    ("atom_radius",     0.0325, 0.005, 0.07, "Radius of the circle, in metres (the old ball was 0.02)"),
    ("atom_nucleus",    0.27, 0.0, 1.0,  "Radius of the dot, as a fraction of the circle (0.29 on the card)"),
    ("atom_ring",       0.8, 0.0, 1.0,  "Opacity of the circle"),
    ("atom_ring_width", 0.036, 0.005, 0.3, "Half thickness of the circle, as a fraction of its radius"),
    ("atom_rim",        0.25, 0.0, 2.0,  "Soft glow on the inside of the circle: makes it the edge of a ball"),
    ("atom_cloud",      2.6, 0.0, 3.0,  "Brightness of the cloud"),
    ("atom_cloud_size", 0.28, 0.1, 1.5,  "How far the cloud spreads from the nucleus"),
    ("atom_grain",      0.94, 0.0, 1.0,  "0 = smooth fog, 1 = points"),
    ("atom_grain_scale", 8.0, 1.0, 20.0, "Number of points: higher = more and smaller"),
    ("atom_twinkle",    0.6, 0.0, 10.0, "How fast the points come and go"),
]

bpy.ops.wm.open_mainfile(filepath=SRC)
D = bpy.data
ob = D.objects["Icosphere.001"]
for nm, v, lo, hi, tip in PROPS:
    ob[nm] = v
    ob.id_properties_ui(nm).update(min=lo, max=hi, soft_min=lo, soft_max=hi, description=tip)

# ---------------------------------------------------------------- mesh: a bounding sphere
old = ob.data
old.use_fake_user = True
old.name = "Atom_OLD_v21_mesh"
me = D.meshes.new("Atom_bounds")
bm = bmesh.new()
bmesh.ops.create_icosphere(bm, subdivisions=3, radius=BOUND)
bm.to_mesh(me)
bm.free()
ob.data = me
mat = D.materials.new("Atom_orbital")
me.materials.append(mat)
ob.visible_shadow = False

# ---------------------------------------------------------------- shader
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
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


def M(op, a, b=None, c=None, label="", clamp=False):
    n = N("ShaderNodeMath", label, operation=op, use_clamp=clamp)
    for i, v in enumerate((a, b, c)):
        if v is not None:
            put(n.inputs[i], v)
    return n.outputs[0]


def V(op, a, b=None, scale=None, label=""):
    n = N("ShaderNodeVectorMath", label, operation=op)
    put(n.inputs[0], a)
    if b is not None:
        put(n.inputs[1], b)
    if scale is not None:
        put(n.inputs["Scale"], scale)
    return n.outputs["Value"] if op in {"LENGTH", "DOT_PRODUCT", "DISTANCE"} else n.outputs["Vector"]


def step(x, lo, hi, label=""):
    """1 below lo, 0 above hi, smooth in between"""
    n = N("ShaderNodeMapRange", label, interpolation_type="SMOOTHSTEP")
    put(n.inputs["Value"], x)
    put(n.inputs["From Min"], lo)
    put(n.inputs["From Max"], hi)
    n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = 1.0, 0.0
    return n.outputs["Result"]


P = {nm: N("ShaderNodeAttribute", nm, attribute_type="OBJECT", attribute_name=nm).outputs["Fac"]
     for nm, *_ in PROPS}
pos = N("ShaderNodeTexCoord").outputs["Object"]
geo = N("ShaderNodeNewGeometry")
vt = N("ShaderNodeVectorTransform", "view direction", vector_type="VECTOR", convert_from="WORLD", convert_to="OBJECT")
put(vt.inputs[0], geo.outputs["Incoming"])
eye = V("NORMALIZE", vt.outputs[0])
mid = V("SUBTRACT", pos, V("SCALE", eye, scale=V("DOT_PRODUCT", pos, eye)), label="closest point to the centre")
mid = V("SCALE", mid, scale=M("DIVIDE", 1.0, P["atom_radius"]), label="in units of the circle")
b = V("LENGTH", mid, label="b: 0 centre .. 1 circle")

nuc = step(b, M("SUBTRACT", P["atom_nucleus"], 0.03), M("ADD", P["atom_nucleus"], 0.03), "nucleus")
ring = M("ABSOLUTE", M("SUBTRACT", b, 1.0))
ring = M("MULTIPLY", step(ring, M("MULTIPLY", P["atom_ring_width"], 0.4), M("MULTIPLY", P["atom_ring_width"], 1.4), "circle"),
         P["atom_ring"])

rim = M("MULTIPLY", M("EXPONENT", M("DIVIDE", M("SUBTRACT", b, 1.0), 0.09)), P["atom_rim"])
rim = M("MULTIPLY", rim, step(b, 0.97, 1.0), label="rim")

clock = N("ShaderNodeValue", "seconds (driven)")
clock.outputs[0].driver_add("default_value").driver.expression = "frame / 25"
w = M("MULTIPLY", clock.outputs[0], P["atom_twinkle"])
cloud = None
for t in (-0.7, -0.35, 0.0, 0.35, 0.7):
    q = V("ADD", mid, V("SCALE", eye, scale=t), label="slice %+.2f" % t)
    r = V("LENGTH", q)
    dens = M("EXPONENT", M("MULTIPLY", M("DIVIDE", r, P["atom_cloud_size"]), -1.0), label="S orbital")
    vo = N("ShaderNodeTexVoronoi", voronoi_dimensions="4D", feature="F1")
    put(vo.inputs["Vector"], q)
    put(vo.inputs["Scale"], P["atom_grain_scale"])
    put(vo.inputs["W"], M("DIVIDE", w, P["atom_grain_scale"]))
    dots = M("MULTIPLY", step(vo.outputs["Distance"], 0.12, 0.48, "points"), 3.0)
    g = M("ADD", M("MULTIPLY", dots, P["atom_grain"]), M("SUBTRACT", 1.0, P["atom_grain"]))
    lay = M("MULTIPLY", dens, g)
    cloud = lay if cloud is None else M("ADD", cloud, lay)
cloud = M("MULTIPLY", M("MULTIPLY", cloud, P["atom_cloud"]), step(b, 0.72, 0.97, "inside the circle"), label="cloud")

total = M("ADD", M("ADD", M("ADD", nuc, ring), rim), M("MULTIPLY", cloud, 0.4), clamp=True, label="opacity")
total = M("MULTIPLY", total, M("SUBTRACT", 1.0, geo.outputs["Backfacing"]), label="front faces only")
em = N("ShaderNodeEmission")
em.inputs["Color"].default_value = (0.93, 0.97, 1.0, 1.0)
em.inputs["Strength"].default_value = 1.0
tr = N("ShaderNodeBsdfTransparent")
mx = N("ShaderNodeMixShader")
put(mx.inputs[0], total)
put(mx.inputs[1], tr.outputs[0])
put(mx.inputs[2], em.outputs[0])
out = N("ShaderNodeOutputMaterial")
put(out.inputs["Surface"], mx.outputs[0])
for i, n in enumerate(made):
    n.location = ((i % 12) * 190, -(i // 12) * 260)

bpy.ops.wm.save_as_mainfile(filepath=DST)
print("BUILT OK", DST)
