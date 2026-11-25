"""SH_15 v19: laser tweezers polish. Builds v19 from v18 (never writes to v18).

    blender -b --factory-startup --python sh15_v19_tweezers_build.py [-- output.blend]

Replaces the old "Cone" (kept, hidden, in the `archive` collection) with `LaserTweezers`:
one object, one Geometry Nodes group, two materials.
  - LT_beam_volume : Gaussian-beam emission volume, brightest at the waist, with faint
                     standing-wave (optical lattice) fringes around the atom
  - LT_envelope    : thin dashed silhouette of the beam, used as the "ghost" in the fade
All controls are custom properties on the object (read by the GN drivers and the shaders).

DON'T re-run over v19 once the user has edited it by hand: it rebuilds from v18.
"""
import bpy, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sh_15_positioning_and_first_cluster_tile_18.blend")
DST = os.path.join(HERE, "sh_15_positioning_and_first_cluster_tile_19.blend")
if "--" in sys.argv and sys.argv[sys.argv.index("--") + 1:]:
    DST = sys.argv[sys.argv.index("--") + 1]

NAME = "LaserTweezers"
#        name            value  min   max   tooltip
PROPS = [
    ("beam",            1.0,   0.0,  2.0,  "Visibility of the glowing beam volume (animated fade)"),
    ("ghost",           0.0,   0.0,  2.0,  "Visibility of the dashed outline (animated fade)"),
    ("waist",           0.034, 0.005, 0.2, "Beam radius at the focus, where the atom sits"),
    ("rayleigh",        0.48,  0.05, 5.0,  "How slowly the beam opens up. Smaller = stronger hourglass"),
    ("half_length",     4.0,   1.0,  30.0, "Beam length on each side of the atom"),
    ("strength",        21.0,  0.0,  200., "Emission strength at the focus"),
    ("lattice",         0.75,  0.0,  1.0,  "Depth of the standing-wave fringes near the atom"),
    ("lattice_period",  0.085, 0.02, 1.0,  "Distance between fringes"),
    ("lattice_extent",  0.34,  0.02, 5.0,  "How far from the atom the fringes reach"),
]
# fade: glow drains to the dashed outline, the outline dissolves. Gone at 185.
KEYS = {
    "beam":  [(154, 1.0), (173, 0.0)],
    "ghost": [(158, 0.0), (168, 0.6), (173, 0.6), (185, 0.0)],
}
HIDE_FRAME = 186

bpy.ops.wm.open_mainfile(filepath=SRC)
D, S = bpy.data, bpy.context.scene
cone, atom = D.objects["Cone"], D.objects["Icosphere.001"]


# ---------------------------------------------------------------- node helper
class B:
    def __init__(self, nt):
        self.nt = nt

    def n(self, typ, **kw):
        nd = self.nt.nodes.new(typ)
        for k, v in kw.items():
            setattr(nd, k, v)
        return nd

    def put(self, sock, v):
        if v is None:
            return
        if hasattr(v, "links"):
            self.nt.links.new(v, sock)
        else:
            sock.default_value = v

    def m(self, op, a, b=None, c=None, label="", clamp=False):
        nd = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        nd.label = label
        for i, v in enumerate((a, b, c)):
            if v is not None:
                self.put(nd.inputs[i], v)
        return nd.outputs[0]

    def prop(self, name):
        nd = self.n("ShaderNodeAttribute", attribute_type="OBJECT", attribute_name=name)
        nd.label = name
        return nd.outputs["Fac"]


# ---------------------------------------------------------------- materials
def fresh(name):
    m = D.materials.get(name) or D.materials.new(name)
    m.node_tree.nodes.clear()
    return m


def arrange(nt, w=190, h=190):
    """rough left-to-right layout by dependency depth"""
    depth = {}

    def d(nd):
        if nd.name not in depth:
            depth[nd.name] = 0
            kids = [l.to_node for l in nt.links if l.from_node == nd]
            depth[nd.name] = 1 + max([d(k) for k in kids], default=-1)
        return depth[nd.name]
    rows = {}
    for nd in nt.nodes:
        c = d(nd)
        rows[c] = rows.get(c, 0) + 1
        nd.location = (-c * w, 300 - rows[c] * h)


def beam_w2(b, z):
    """squared beam radius over squared waist: 1 + (z/zR)^2"""
    q = b.m("DIVIDE", z, b.prop("rayleigh"))
    return b.m("ADD", b.m("MULTIPLY", q, q), 1.0, label="(w/w0)^2")


vol = fresh("LT_beam_volume")
b = B(vol.node_tree)
tc = b.n("ShaderNodeTexCoord")
sep = b.n("ShaderNodeSeparateXYZ")
b.put(sep.inputs[0], tc.outputs["Object"])
x, y, z = sep.outputs
r2 = b.m("ADD", b.m("MULTIPLY", x, x), b.m("MULTIPLY", y, y), label="r^2")
w2 = beam_w2(b, z)
w0 = b.prop("waist")
u = b.m("DIVIDE", r2, b.m("MULTIPLY", w2, b.m("MULTIPLY", w0, w0)), label="(r/w)^2")
gauss = b.m("EXPONENT", b.m("MULTIPLY", u, -2.0), label="gaussian profile")
core = b.m("EXPONENT", b.m("MULTIPLY", u, -14.0), label="hot core")
axial = b.m("POWER", w2, -1.0, label="dims as it opens")
# standing wave: bright fringes, an antinode exactly on the atom (z = 0)
ph = b.m("MULTIPLY", b.m("DIVIDE", z, b.prop("lattice_period")), 3.14159265)
cs = b.m("COSINE", ph)
fr = b.m("POWER", b.m("MULTIPLY", cs, cs), 1.5, label="fringes")
q = b.m("DIVIDE", z, b.prop("lattice_extent"))
env = b.m("MULTIPLY", b.m("EXPONENT", b.m("MULTIPLY", b.m("MULTIPLY", q, q), -1.0)),
          b.prop("lattice"), label="fringe envelope")
lat = b.m("ADD", b.m("SUBTRACT", 1.0, env),
          b.m("MULTIPLY", env, b.m("MULTIPLY", fr, 2.0)), label="lattice")
# slow axial shimmer
mp = b.n("ShaderNodeMapping")
b.put(mp.inputs["Vector"], tc.outputs["Object"])
mp.inputs["Scale"].default_value = (9.0, 9.0, 1.3)
noise = b.n("ShaderNodeTexNoise", noise_dimensions="4D")
noise.inputs["Scale"].default_value = 1.0
noise.inputs["Detail"].default_value = 2.0
b.put(noise.inputs["Vector"], mp.outputs[0])
tm = b.n("GeometryNodeInputSceneTime")
b.put(noise.inputs["W"], b.m("MULTIPLY", tm.outputs["Seconds"], 0.7))
shim = b.m("ADD", b.m("MULTIPLY", noise.outputs[0], 0.9), 0.55, label="shimmer")
# fade the far ends: the camera (4 units down the beam) must never sit inside glowing volume
ends = b.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP")
b.put(ends.inputs["Value"], b.m("ABSOLUTE", z))
for s_, v_ in (("From Min", 1.7), ("From Max", 3.3), ("To Min", 1.0), ("To Max", 0.0)):
    ends.inputs[s_].default_value = v_
ends.label = "fade far ends"
# and fade close to the lens: at 140-143 the beam sweeps past the camera and would fog the frame
cd = b.n("ShaderNodeCameraData")
near = b.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP")
b.put(near.inputs["Value"], cd.outputs["View Distance"])
for s_, v_ in (("From Min", 2.2), ("From Max", 4.6), ("To Min", 0.0), ("To Max", 1.0)):
    near.inputs[s_].default_value = v_
near.label = "fade near camera"
body = b.m("ADD", gauss, b.m("MULTIPLY", core, 0.65))
e = b.m("MULTIPLY", body, axial)
e = b.m("MULTIPLY", e, lat)
e = b.m("MULTIPLY", e, shim)
e = b.m("MULTIPLY", e, ends.outputs[0])
e = b.m("MULTIPLY", e, near.outputs[0])
e = b.m("MULTIPLY", e, b.prop("strength"))
e = b.m("MULTIPLY", e, b.prop("beam"))
mix = b.n("ShaderNodeMix", data_type="RGBA")
b.put(mix.inputs[0], b.m("MULTIPLY", core, b.m("POWER", axial, 0.35), clamp=True))
mix.inputs[6].default_value = (0.64, 0.31, 0.24, 1)   # rose-copper body, from the old beam
mix.inputs[7].default_value = (0.84, 0.58, 0.45, 1)    # warm core
em = b.n("ShaderNodeEmission")
b.put(em.inputs["Color"], mix.outputs[2])
b.put(em.inputs["Strength"], e)
out = b.n("ShaderNodeOutputMaterial")
b.put(out.inputs["Volume"], em.outputs[0])
arrange(vol.node_tree)

ghost = fresh("LT_envelope")
b = B(ghost.node_tree)
tc = b.n("ShaderNodeTexCoord")
sep = b.n("ShaderNodeSeparateXYZ")
b.put(sep.inputs[0], tc.outputs["Object"])
z = sep.outputs[2]
dash = b.m("LESS_THAN", b.m("FRACT", b.m("ADD", b.m("DIVIDE", z, 0.06), 0.3)), 0.6, label="dashes")
az = b.m("EXPONENT", b.m("MULTIPLY", b.m("MULTIPLY", z, z), -0.16), label="soft ends")
a = b.m("MULTIPLY", dash, az)
a = b.m("MULTIPLY", a, b.prop("ghost"), clamp=True)
em = b.n("ShaderNodeEmission")
em.inputs["Color"].default_value = (0.95, 0.60, 0.52, 1)
em.inputs["Strength"].default_value = 0.9
tr = b.n("ShaderNodeBsdfTransparent")
ms = b.n("ShaderNodeMixShader")
b.put(ms.inputs[0], a)
b.put(ms.inputs[1], tr.outputs[0])
b.put(ms.inputs[2], em.outputs[0])
out = b.n("ShaderNodeOutputMaterial")
b.put(out.inputs["Surface"], ms.outputs[0])
arrange(ghost.node_tree)

# ---------------------------------------------------------------- geometry nodes
ng = D.node_groups.get("LaserTweezersGeo") or D.node_groups.new("LaserTweezersGeo", "GeometryNodeTree")
ng.nodes.clear()
ng.interface.clear()
ids = {}
for nm, dv, tip in (("Waist", .034, "Beam radius at the focus"),
                    ("Rayleigh", .48, "Smaller = stronger hourglass"),
                    ("Half Length", 4., "Length on each side of the atom")):
    s = ng.interface.new_socket(nm, in_out="INPUT", socket_type="NodeSocketFloat")
    s.default_value, s.description = dv, tip
    ids[nm] = s.identifier
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
g = B(ng)
gin, gout, join = g.n("NodeGroupInput"), g.n("NodeGroupOutput"), g.n("GeometryNodeJoinGeometry")
pos = g.n("GeometryNodeInputPosition")
sp = g.n("ShaderNodeSeparateXYZ")
g.put(sp.inputs[0], pos.outputs[0])
zz = g.m("MULTIPLY", g.m("MULTIPLY", g.m("SIGN", sp.outputs[2]),
                         g.m("POWER", g.m("ABSOLUTE", sp.outputs[2]), 2.6)),
         gin.outputs["Half Length"], label="denser rings near focus")
qq = g.m("DIVIDE", zz, gin.outputs["Rayleigh"])
ww = g.m("MULTIPLY", g.m("SQRT", g.m("ADD", g.m("MULTIPLY", qq, qq), 1.0)), gin.outputs["Waist"], label="w(z)")


def shell(k, mat, caps):
    cyl = g.n("GeometryNodeMeshCylinder", fill_type="NGON" if caps else "NONE")
    for s, v in (("Vertices", 64), ("Side Segments", 96), ("Radius", 1.0), ("Depth", 2.0)):
        cyl.inputs[s].default_value = v
    rr = g.m("MULTIPLY", ww, k)
    cmb = g.n("ShaderNodeCombineXYZ")
    g.put(cmb.inputs[0], g.m("MULTIPLY", sp.outputs[0], rr))
    g.put(cmb.inputs[1], g.m("MULTIPLY", sp.outputs[1], rr))
    g.put(cmb.inputs[2], zz)
    setp = g.n("GeometryNodeSetPosition")
    g.put(setp.inputs["Geometry"], cyl.outputs["Mesh"])
    g.put(setp.inputs["Position"], cmb.outputs[0])
    sm = g.n("GeometryNodeSetMaterial")
    g.put(sm.inputs["Geometry"], setp.outputs[0])
    sm.inputs["Material"].default_value = mat
    ss = g.n("GeometryNodeSetShadeSmooth")
    g.put(ss.inputs[0], sm.outputs[0])
    ng.links.new(ss.outputs[0], join.inputs[0])


shell(1.75, vol, True)     # volume domain: gaussian is 0.2 % here, so no visible edge

# dashed outline: the two contour lines of the beam as seen by the active camera
cam = g.n("GeometryNodeInputActiveCamera")
ci = g.n("GeometryNodeObjectInfo", transform_space="RELATIVE")
g.put(ci.inputs["Object"], cam.outputs[0])
cross = g.n("ShaderNodeVectorMath", operation="CROSS_PRODUCT")
cross.inputs[0].default_value = (0, 0, 1)
g.put(cross.inputs[1], ci.outputs["Location"])
norm = g.n("ShaderNodeVectorMath", operation="NORMALIZE")
g.put(norm.inputs[0], cross.outputs[0])
line = g.n("GeometryNodeMeshLine", mode="END_POINTS")
line.inputs["Count"].default_value = 400
line.inputs["Start Location"].default_value = (0, 0, -1)
line.inputs["Offset"].default_value = (0, 0, 1)     # end point in END_POINTS mode
axisv = g.n("ShaderNodeCombineXYZ")
g.put(axisv.inputs[2], zz)
prof = g.n("GeometryNodeCurvePrimitiveCircle")
prof.inputs["Resolution"].default_value = 8
prof.inputs["Radius"].default_value = 0.0015
for side in (1.15, -1.15):
    sc = g.n("ShaderNodeVectorMath", operation="SCALE")
    g.put(sc.inputs[0], norm.outputs[0])
    g.put(sc.inputs["Scale"], g.m("MULTIPLY", ww, side))
    ad = g.n("ShaderNodeVectorMath", operation="ADD")
    g.put(ad.inputs[0], sc.outputs[0])
    g.put(ad.inputs[1], axisv.outputs[0])
    sp2 = g.n("GeometryNodeSetPosition")
    g.put(sp2.inputs["Geometry"], line.outputs[0])
    g.put(sp2.inputs["Position"], ad.outputs[0])
    m2c = g.n("GeometryNodeMeshToCurve")
    g.put(m2c.inputs[0], sp2.outputs[0])
    c2m = g.n("GeometryNodeCurveToMesh")
    g.put(c2m.inputs["Curve"], m2c.outputs[0])
    g.put(c2m.inputs["Profile Curve"], prof.outputs[0])
    sm = g.n("GeometryNodeSetMaterial")
    g.put(sm.inputs["Geometry"], c2m.outputs[0])
    sm.inputs["Material"].default_value = ghost
    ng.links.new(sm.outputs[0], join.inputs[0])
ng.links.new(join.outputs[0], gout.inputs[0])
arrange(ng)

# ---------------------------------------------------------------- object
old = D.objects.get(NAME)
if old:
    D.objects.remove(old)
me = D.meshes.new(NAME)
ob = D.objects.new(NAME, me)
for c in cone.users_collection:
    c.objects.link(ob)
ob.parent = atom
ob.matrix_parent_inverse = cone.matrix_parent_inverse.copy()
ob.matrix_basis = cone.matrix_basis.copy()
me.materials.append(vol)
me.materials.append(ghost)
for nm, v, lo, hi, tip in PROPS:
    ob[nm] = v
    ob.id_properties_ui(nm).update(min=lo, max=hi, soft_min=lo, soft_max=hi, description=tip)
mod = ob.modifiers.new("LaserTweezersGeo", "NODES")
mod.node_group = ng
for sock, pn in (("Waist", "waist"), ("Rayleigh", "rayleigh"), ("Half Length", "half_length")):
    getattr(mod.properties.inputs, ids[sock]).value = ob[pn]
    drv = ob.driver_add('modifiers["%s"].properties.inputs.%s.value' % (mod.name, ids[sock])).driver
    drv.type = "SCRIPTED"
    var = drv.variables.new()
    var.name = "v"
    var.targets[0].id = ob
    var.targets[0].data_path = '["%s"]' % pn
    drv.expression = "v"
ob.visible_shadow = False
ob.visible_diffuse = True

for pn, keys in KEYS.items():
    for f, v in keys:
        ob[pn] = v
        ob.keyframe_insert('["%s"]' % pn, frame=f)
    ob[pn] = keys[0][1]
for f, h in ((1, False), (HIDE_FRAME, True)):
    ob.hide_render = ob.hide_viewport = h
    ob.keyframe_insert("hide_render", frame=f)
    ob.keyframe_insert("hide_viewport", frame=f)

# ---------------------------------------------------------------- retire the old cone
cone.name = "Cone_OLD_tweezers"
cone.hide_render = cone.hide_viewport = True
arch = D.collections.get("archive")
if arch:
    for c in list(cone.users_collection):
        c.objects.unlink(cone)
    arch.objects.link(cone)

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("BUILT OK", DST, "axis", [round(v, 3) for v in ob.matrix_world.col[2]])
