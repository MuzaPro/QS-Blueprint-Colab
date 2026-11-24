"""SH_18 v13: replace the placeholder router (brick-textured glass) with a wafer-based
photonic router material. Renames Plane.004 -> photonic-router-wafer.

Run (after `python sh18_router_layout_gen.py` has written tex/router_*.png):
  blender --factory-startup -b sh_18_architecture_intro_12.blend --python sh18_v13_router_build.py
  -> saves sh_18_architecture_intro_13.blend

Material "photonic-router-wafer" (old "decorative-texture-1" is kept, unassigned, fake user):
  frosted pale wafer base (Principled, satin coat) with three layout layers stacked in depth:
    L3 deep   (soft dark regions)       depth ROUTER_DEPTH_L3 below the surface
    L2 metal  (heaters, traces, pads)   depth ROUTER_DEPTH_L2
    L1 surface (waveguides, labels)     on the surface
  The deeper layers are sampled with a parallax offset from the view direction, so they
  slide against the surface as the camera moves -> reads as a layered, translucent wafer
  (style ref: ref/router-material-style-inspiration2.jpg).
  router_active.png: the 3 lanes the shot's photons use, faint cyan emission (ACTIVE_GLOW).
UV: object space, u = (x - X0)/(X1 - X0), v = (y - Y0)/(Y1 - Y0)  (same constants as the generator).
Group inputs (node "ROUTER_controls" values, tweak in the material): see CONTROLS.
"""
import bpy, os

HERE = os.path.dirname(bpy.data.filepath)
OUT = os.path.join(HERE, "sh_18_architecture_intro_13.blend")
X0, X1, Y0, Y1 = -10.78, 27.71, -0.954, 0.954
NEW_NAME = "photonic-router-wafer"

CONTROLS = {                 # name: default
    "base_value": 0.74,      # wafer brightness (frosted pale)
    "deep_amount": 0.72,
    "metal_amount": 0.80,
    "line_amount": 0.85,
    "depth_L2": 0.05,        # m below the surface
    "depth_L3": 0.16,
    "active_glow": 0.15,     # emission of the 3 photon lanes (0 = off)
}
ACTIVE_COLOR = (0.613, 0.947, 0.986, 1.0)
BASE_TINT = (0.93, 0.95, 1.0, 1.0)     # very slightly cool, like the refs


o = bpy.data.objects.get("Plane.004") or bpy.data.objects[NEW_NAME]
o.name = NEW_NAME
o.data.name = NEW_NAME
old = o.active_material
if old and old.name == "decorative-texture-1":
    old.use_fake_user = True

mat = bpy.data.materials.get(NEW_NAME) or bpy.data.materials.new(NEW_NAME)
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
N, L = nt.nodes, nt.links


def n(t, x, y, name=None, **kw):
    nd = N.new(t); nd.location = (x, y)
    if name:
        nd.name = nd.label = name
    for k, v in kw.items():
        setattr(nd, k, v)
    return nd


def math_(op, x, y, a=None, b=None, name=None):
    m = n('ShaderNodeMath', x, y, name, operation=op)
    for i, v in ((0, a), (1, b)):
        if isinstance(v, (int, float)):
            m.inputs[i].default_value = v
        elif v is not None:
            L.new(v, m.inputs[i])
    return m.outputs[0]


# controls as a group-less "value" bank (named Value nodes -> easy to find)
ctrl = {}
for i, (k, v) in enumerate(CONTROLS.items()):
    vn = n('ShaderNodeValue', -2200, 600 - i * 90, "ROUTER_" + k)
    vn.outputs[0].default_value = v
    ctrl[k] = vn.outputs[0]

# ---------------------------------------------------------------- UVs + parallax
tc = n('ShaderNodeTexCoord', -2200, -200)
sep = n('ShaderNodeSeparateXYZ', -2000, -200)
L.new(tc.outputs["Object"], sep.inputs[0])
u = math_('MULTIPLY_ADD', -1800, -150, sep.outputs["X"], 1.0 / (X1 - X0));
u.node.inputs[2].default_value = -X0 / (X1 - X0)
v = math_('MULTIPLY_ADD', -1800, -300, sep.outputs["Y"], 1.0 / (Y1 - Y0))
v.node.inputs[2].default_value = -Y0 / (Y1 - Y0)

geo = n('ShaderNodeNewGeometry', -2200, -500)
vt = n('ShaderNodeVectorTransform', -2000, -500, vector_type='VECTOR', convert_from='WORLD', convert_to='OBJECT')
L.new(geo.outputs["Incoming"], vt.inputs[0])
isep = n('ShaderNodeSeparateXYZ', -1800, -500)
L.new(vt.outputs[0], isep.inputs[0])
iz = math_('MAXIMUM', -1600, -600, isep.outputs["Z"], 0.2)          # avoid blow-up at grazing angles
px_ = math_('DIVIDE', -1400, -450, isep.outputs["X"], iz)            # tan offset per metre of depth
py_ = math_('DIVIDE', -1400, -600, isep.outputs["Y"], iz)


def layer_uv(depth_sock, x, y):
    # deep point seen at surface p sits at p - V.xy/V.z * d
    du = math_('MULTIPLY', x, y, px_, depth_sock)
    dv = math_('MULTIPLY', x, y - 120, py_, depth_sock)
    uu = math_('SUBTRACT', x + 180, y, u, math_('DIVIDE', x + 90, y, du, X1 - X0))
    vv = math_('SUBTRACT', x + 180, y - 120, v, math_('DIVIDE', x + 90, y - 120, dv, Y1 - Y0))
    cx = n('ShaderNodeCombineXYZ', x + 360, y)
    L.new(uu, cx.inputs[0]); L.new(vv, cx.inputs[1])
    return cx.outputs[0]


uv0 = n('ShaderNodeCombineXYZ', -1200, -150)
L.new(u, uv0.inputs[0]); L.new(v, uv0.inputs[1])
uv2 = layer_uv(ctrl["depth_L2"], -1300, -800)
uv3 = layer_uv(ctrl["depth_L3"], -1300, -1100)


def tex(fname, uv_sock, x, y, name):
    t = n('ShaderNodeTexImage', x, y, name)
    path = os.path.join(HERE, "tex", fname)
    img = bpy.data.images.load(path, check_existing=True)
    img.filepath = "//tex/" + fname
    img.colorspace_settings.name = 'Non-Color'
    t.image = img
    t.extension = 'EXTEND'
    t.interpolation = 'Cubic'
    L.new(uv_sock, t.inputs[0])
    return t.outputs["Color"]


l1 = tex("router_L1_waveguides.png", uv0.outputs[0], -800, 200, "ROUTER_L1_surface")
la = tex("router_active.png", uv0.outputs[0], -800, -50, "ROUTER_active")
l2 = tex("router_L2_metal.png", uv2, -800, -800, "ROUTER_L2_metal")
l3 = tex("router_L3_deep.png", uv3, -800, -1100, "ROUTER_L3_deep")

# ---------------------------------------------------------------- composite value
# c = base * (1 - deep*L3) * (1 - metal*L2) * (1 - line*L1)
def atten(layer, amount, x, y):
    return math_('SUBTRACT', x + 150, y, 1.0, math_('MULTIPLY', x, y, layer, amount))

c = math_('MULTIPLY', -200, -400, ctrl["base_value"], atten(l3, ctrl["deep_amount"], -450, -1100))
c = math_('MULTIPLY', 0, -400, c, atten(l2, ctrl["metal_amount"], -450, -800))
c = math_('MULTIPLY', 200, -400, c, atten(l1, ctrl["line_amount"], -450, 200))
tint = n('ShaderNodeMix', 400, -300, "ROUTER_tint", data_type='RGBA', blend_type='MULTIPLY')
tint.inputs["Factor"].default_value = 1.0
L.new(c, tint.inputs["A"]); tint.inputs["B"].default_value = BASE_TINT

# metal reads a touch glossier than the frosted base, waveguides a touch smoother too
rough = math_('SUBTRACT', 400, -600, 0.42, math_('MULTIPLY', 250, -650, l2, 0.18))

bsdf = n('ShaderNodeBsdfPrincipled', 700, -300)
L.new(tint.outputs["Result"], bsdf.inputs["Base Color"])
L.new(rough, bsdf.inputs["Roughness"])
bsdf.inputs["Coat Weight"].default_value = 0.6      # polished top cladding
bsdf.inputs["Coat Roughness"].default_value = 0.06
bsdf.inputs["Specular IOR Level"].default_value = 0.5
bsdf.inputs["Emission Color"].default_value = ACTIVE_COLOR
L.new(math_('MULTIPLY', 400, -850, la, ctrl["active_glow"]), bsdf.inputs["Emission Strength"])
out = n('ShaderNodeOutputMaterial', 1000, -300)
L.new(bsdf.outputs[0], out.inputs["Surface"])

o.data.materials.clear()
o.data.materials.append(mat)
print("router renamed to", o.name, "material", mat.name)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
