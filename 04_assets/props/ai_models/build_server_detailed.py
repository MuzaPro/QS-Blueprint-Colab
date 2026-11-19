"""Detailed photoreal-ish server rack, built beside the low-poly v01 rack.
Re-runnable: removes its own previous output (everything prefixed SRVD_)."""
import bpy, bmesh, random, math
from mathutils import Matrix, Vector

random.seed(11)
OFFSET_X = 0.9
COLL = "Server_Rack_Detailed"
P = "SRVD_"

# ------------------------------------------------------------------ cleanup
if COLL in bpy.data.collections:
    c = bpy.data.collections[COLL]
    for o in list(c.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(c)
for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.node_groups):
    for d in list(coll):
        if d.name.startswith(P):
            coll.remove(d)

# ------------------------------------------------------------------ node helpers
def hex2lin(h, k=1.0):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c]
    return [min(1.0, x * k) for x in c] + [1.0]

def N(nt, t, **props):
    n = nt.nodes.new(t)
    for k, v in props.items():
        setattr(n, k, v)
    return n

def feed(nt, sock, v):
    if isinstance(v, bpy.types.NodeSocket):
        nt.links.new(v, sock)
    else:
        sock.default_value = v

def mth(nt, op, a, b=0.0, c=None):
    n = N(nt, "ShaderNodeMath", operation=op)
    feed(nt, n.inputs[0], a)
    feed(nt, n.inputs[1], b)
    if c is not None:
        feed(nt, n.inputs[2], c)
    return n.outputs[0]

def maprange(nt, v, a, b, c, d):
    n = N(nt, "ShaderNodeMapRange", clamp=True)
    feed(nt, n.inputs[0], v)
    for i, x in zip((1, 2, 3, 4), (a, b, c, d)):
        n.inputs[i].default_value = x
    return n.outputs[0]

def noise(nt, vec, scale, detail=4.0, rough=0.55):
    n = N(nt, "ShaderNodeTexNoise")
    feed(nt, n.inputs["Vector"], vec)
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    return n.outputs["Fac"]

def by_id(socks, ident):
    return next(s for s in socks if s.identifier == ident)

def mixcol(nt, fac, a, b):
    n = N(nt, "ShaderNodeMix", data_type="RGBA")
    feed(nt, by_id(n.inputs, "Factor_Float"), fac)
    feed(nt, by_id(n.inputs, "A_Color"), a)
    feed(nt, by_id(n.inputs, "B_Color"), b)
    return by_id(n.outputs, "Result_Color")

def planar(nt, obj):
    """2D coords that work on front (-Y) and top (+Z) faces: (x, y+z)."""
    s = N(nt, "ShaderNodeSeparateXYZ")
    nt.links.new(obj, s.inputs[0])
    c = N(nt, "ShaderNodeCombineXYZ")
    nt.links.new(s.outputs[0], c.inputs[0])
    feed(nt, c.inputs[1], mth(nt, "ADD", s.outputs[1], s.outputs[2]))
    return c.outputs[0]

# ---- hex perforation node group: Mask = 1 inside a hole
def make_hex_group():
    ng = bpy.data.node_groups.new(P + "HexPerforation", "ShaderNodeTree")
    ng.interface.new_socket("Vector", in_out="INPUT", socket_type="NodeSocketVector")
    s = ng.interface.new_socket("Pitch", in_out="INPUT", socket_type="NodeSocketFloat"); s.default_value = 0.005
    s = ng.interface.new_socket("Radius", in_out="INPUT", socket_type="NodeSocketFloat"); s.default_value = 0.38
    ng.interface.new_socket("Mask", in_out="OUTPUT", socket_type="NodeSocketFloat")
    gi, go = N(ng, "NodeGroupInput"), N(ng, "NodeGroupOutput")
    sep = N(ng, "ShaderNodeSeparateXYZ")
    ng.links.new(gi.outputs["Vector"], sep.inputs[0])
    dx = mth(ng, "DIVIDE", sep.outputs[0], gi.outputs["Pitch"])
    dy = mth(ng, "DIVIDE", mth(ng, "DIVIDE", sep.outputs[1], gi.outputs["Pitch"]), 0.866)
    row = mth(ng, "FLOOR", dy)
    odd = mth(ng, "MULTIPLY", mth(ng, "FRACT", mth(ng, "MULTIPLY", row, 0.5)), 2.0)
    x2 = mth(ng, "MULTIPLY_ADD", odd, 0.5, dx)
    fx = mth(ng, "SUBTRACT", mth(ng, "FRACT", x2), 0.5)
    fy = mth(ng, "MULTIPLY", mth(ng, "SUBTRACT", mth(ng, "FRACT", dy), 0.5), 0.866)
    d = mth(ng, "SQRT", mth(ng, "ADD", mth(ng, "MULTIPLY", fx, fx), mth(ng, "MULTIPLY", fy, fy)))
    ng.links.new(mth(ng, "LESS_THAN", d, gi.outputs["Radius"]), go.inputs["Mask"])
    return ng

HEX = make_hex_group()

# ------------------------------------------------------------------ materials
def new_mat(name):
    m = bpy.data.materials.new(P + name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    obj = N(nt, "ShaderNodeTexCoord").outputs["Object"]
    return m, nt, bsdf, obj

def mat_paint(name, col, rlo, rhi, metallic=0.0, mode=None, pitch=0.005, radius=0.38,
              hole="#040405", bump=0.06, cvar=(0.85, 1.12)):
    """Powder coat / plastic: noisy roughness (broken-up reflections), smudges,
    slight colour drift and an orange-peel micro bump."""
    m, nt, bsdf, obj = new_mat(name)
    n1 = noise(nt, obj, 5.0, 6, 0.6)
    n2 = noise(nt, obj, 45.0, 3, 0.5)
    n3 = noise(nt, obj, 1.3, 8, 0.65)
    mixv = mth(nt, "MULTIPLY_ADD", n1, 0.6, mth(nt, "MULTIPLY", n2, 0.4))
    rough = mth(nt, "ADD", maprange(nt, mixv, 0.35, 0.65, rlo, rhi),
                maprange(nt, n3, 0.55, 0.75, 0.0, 0.10))            # smudges
    ramp = N(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hex2lin(col, cvar[0])
    ramp.color_ramp.elements[1].color = hex2lin(col, cvar[1])
    nt.links.new(n1, ramp.inputs[0])
    base = ramp.outputs[0]
    b = N(nt, "ShaderNodeBump")
    b.inputs["Strength"].default_value = bump
    b.inputs["Distance"].default_value = 0.0003
    nt.links.new(noise(nt, obj, 700.0, 2, 0.5), b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    if mode:
        g = N(nt, "ShaderNodeGroup"); g.node_tree = HEX
        nt.links.new(planar(nt, obj), g.inputs["Vector"])
        g.inputs["Pitch"].default_value = pitch
        g.inputs["Radius"].default_value = radius
        mask = g.outputs["Mask"]
        if mode == "alpha":
            feed(nt, bsdf.inputs["Alpha"], mth(nt, "SUBTRACT", 1.0, mask))
            m.surface_render_method = "DITHERED"
        else:  # dark holes, no transparency
            base = mixcol(nt, mask, base, hex2lin(hole))
            rough = mth(nt, "MAXIMUM", rough, mask)
    nt.links.new(base, bsdf.inputs["Base Color"])
    feed(nt, bsdf.inputs["Roughness"], rough)
    bsdf.inputs["Metallic"].default_value = metallic
    m.diffuse_color = hex2lin(col)
    m.roughness = (rlo + rhi) / 2
    return m

def mat_metal(name, col, rlo, rhi, brushed=False, rail_pitch=None, z0=0.0):
    m, nt, bsdf, obj = new_mat(name)
    vec = obj
    if brushed:
        mp = N(nt, "ShaderNodeMapping")
        nt.links.new(obj, mp.inputs["Vector"])
        mp.inputs["Scale"].default_value = (4.0, 250.0, 250.0)   # streaks along X
        vec = mp.outputs[0]
        bsdf.inputs["Anisotropic"].default_value = 0.6
    n1 = noise(nt, vec, 8.0, 6, 0.6)
    n2 = noise(nt, obj, 1.5, 6, 0.6)
    rough = mth(nt, "ADD", maprange(nt, n1, 0.3, 0.7, rlo, rhi),
                maprange(nt, n2, 0.55, 0.75, 0.0, 0.12))
    ramp = N(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hex2lin(col, 0.88)
    ramp.color_ramp.elements[1].color = hex2lin(col, 1.06)
    nt.links.new(n1, ramp.inputs[0])
    base = ramp.outputs[0]
    if rail_pitch:  # square mounting holes in rows along Z
        s = N(nt, "ShaderNodeSeparateXYZ"); nt.links.new(obj, s.inputs[0])
        f = mth(nt, "FRACT", mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", s.outputs[2], z0), 1.0 / rail_pitch))
        mask = mth(nt, "LESS_THAN", f, 0.6)
        base = mixcol(nt, mask, base, hex2lin("#030303"))
        rough = mth(nt, "MAXIMUM", rough, mask)
        feed(nt, bsdf.inputs["Metallic"], mth(nt, "SUBTRACT", 1.0, mask))
    else:
        bsdf.inputs["Metallic"].default_value = 1.0
    nt.links.new(base, bsdf.inputs["Base Color"])
    feed(nt, bsdf.inputs["Roughness"], rough)
    m.diffuse_color = hex2lin(col)
    m.metallic = 1.0
    return m

def mat_led(name, col, strength=10.0):
    m, nt, bsdf, obj = new_mat(name)
    bsdf.inputs["Base Color"].default_value = hex2lin(col)
    bsdf.inputs["Roughness"].default_value = 0.2
    bsdf.inputs["Emission Color"].default_value = hex2lin(col)
    bsdf.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = hex2lin(col)
    return m

U = 0.04445
M = dict(
    paint=mat_paint("Cabinet_PowderCoat", "#1a1c21", 0.30, 0.55),
    dark=mat_paint("Cabinet_Interior", "#0b0c0e", 0.5, 0.75, bump=0.02),
    perf=mat_paint("Door_Perforated", "#1a1c21", 0.30, 0.55, mode="alpha", pitch=0.0055, radius=0.40),
    zinc=mat_metal("Zinc_Steel", "#9da3ab", 0.28, 0.45),
    rail=mat_metal("Rail_Holes", "#9da3ab", 0.28, 0.45, rail_pitch=U / 3, z0=0.15),
    brushed=mat_metal("Brushed_Aluminium", "#c4c8cd", 0.16, 0.30, brushed=True),
    bezel=mat_paint("Server_Bezel", "#2a2d33", 0.33, 0.50, metallic=0.4),
    chassis=mat_paint("Server_Chassis", "#3a3e44", 0.28, 0.45, metallic=0.7),
    vent=mat_paint("Server_Vent_Hex", "#2a2d33", 0.33, 0.50, metallic=0.4, mode="dark", pitch=0.0032, radius=0.40),
    caddy=mat_paint("Drive_Caddy", "#121316", 0.38, 0.55),
    port=mat_paint("Port_Black", "#030304", 0.22, 0.35, bump=0.0),
    label=mat_paint("Asset_Label", "#d9d8d2", 0.55, 0.70, bump=0.02, cvar=(0.95, 1.02)),
    rubber=mat_paint("Rubber", "#0a0a0a", 0.70, 0.90),
    brush=mat_paint("Cable_Brush", "#050505", 0.8, 0.95, bump=0.3),
    ledg=mat_led("LED_Green", "#A5C151"),
    ledb=mat_led("LED_Blue", "#6b9fd4"),
    cab_blue=mat_paint("Cable_Blue", "#2f63a8", 0.35, 0.5),
    cab_yel=mat_paint("Cable_Yellow", "#c9a53a", 0.35, 0.5),
    cab_grey=mat_paint("Cable_Grey", "#8a8f96", 0.35, 0.5),
)

# ------------------------------------------------------------------ mesh builder
ROT = {"Z": Matrix.Identity(3),
       "Y": Matrix.Rotation(math.pi / 2, 3, "X"),
       "X": Matrix.Rotation(math.pi / 2, 3, "Y")}

class MB:
    def __init__(self, off=(0, 0, 0)):
        self.bm = bmesh.new(); self.mats = []; self.off = Vector(off)

    def _assign(self, verts, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        i = self.mats.index(mat)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = i

    def box(self, x0, x1, y0, y1, z0, z1, mat):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0),
                           (y0 + y1) / 2 + v.co.y * (y1 - y0),
                           (z0 + z1) / 2 + v.co.z * (z1 - z0))) - self.off
        self._assign(r["verts"], mat)

    def cyl(self, c, r, depth, axis, mat, seg=16):
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg,
                                    radius1=r, radius2=r, depth=depth)
        for v in res["verts"]:
            v.co = ROT[axis] @ v.co + Vector(c) - self.off
        self._assign(res["verts"], mat)

    def build(self, name, parent, bevel=None):
        me = bpy.data.meshes.new(P + name)
        self.bm.normal_update(); self.bm.to_mesh(me); self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(P + name, me)
        col.objects.link(ob)
        ob.parent = parent
        ob.location = self.off
        for p in me.polygons:
            p.use_smooth = bool(bevel)
        if bevel:
            md = ob.modifiers.new("Bevel", "BEVEL")
            md.width, md.segments = bevel
            md.limit_method = "ANGLE"
            md.harden_normals = True
            md.use_clamp_overlap = True
        return ob

# ------------------------------------------------------------------ scene setup
col = bpy.data.collections.new(COLL)
bpy.context.scene.collection.children.link(col)
root = bpy.data.objects.new("Server_Rack_Detailed", None)
root.empty_display_type = "PLAIN_AXES"; root.empty_display_size = 0.3
root.location = (OFFSET_X, 0, 0)
col.objects.link(root)

W, D, H = 0.6, 1.0, 2.0
FRONT = -D / 2
CAB, DET, UNI, FEET = MB(), MB(), MB(), MB()

# ------------------------------------------------------------------ cabinet
CAB.box(-0.285, 0.285, -0.485, 0.485, 0.025, 0.08, M["dark"])          # plinth
CAB.box(-0.3, 0.3, -0.5, 0.5, 0.08, 0.1, M["paint"])                   # base frame
for sx in (-1, 1):
    for sy in (-1, 1):
        CAB.box(sx * 0.265, sx * 0.3, sy * 0.465, sy * 0.5, 0.1, 1.95, M["paint"])  # corner posts
        # levelling feet
        FEET.cyl((sx * 0.25, sy * 0.45, 0.004), 0.024, 0.008, "Z", M["rubber"], 20)
        FEET.cyl((sx * 0.25, sy * 0.45, 0.018), 0.007, 0.022, "Z", M["zinc"], 12)
        FEET.cyl((sx * 0.25, sy * 0.45, 0.022), 0.013, 0.007, "Z", M["zinc"], 6)
    # dark backing behind side panels so panel gaps read
    CAB.box(sx * 0.27, sx * 0.286, -0.465, 0.465, 0.1, 1.95, M["dark"])
    # split side panels
    for z0, z1 in ((0.102, 1.023), (1.027, 1.948)):
        CAB.box(sx * 0.287, sx * 0.299, -0.462, 0.462, z0, z1, M["paint"])
        DET.box(sx * 0.2985, sx * 0.3002, 0.33, 0.43, z1 - 0.07, z1 - 0.055, M["dark"])  # grip slot
        DET.cyl((sx * 0.2995, 0.38, z1 - 0.1), 0.009, 0.004, "X", M["zinc"], 16)        # lock
        DET.box(sx * 0.3005, sx * 0.3015, 0.3795, 0.3805, z1 - 0.106, z1 - 0.094, M["dark"])
    # front + rear mounting rails, front ones with square holes
    CAB.box(sx * 0.239, sx * 0.256, FRONT + 0.08, FRONT + 0.11, 0.1, 1.95, M["zinc"])
    CAB.box(sx * 0.239, sx * 0.256, 0.33, 0.36, 0.1, 1.95, M["zinc"])
    DET.box(sx * 0.243, sx * 0.252, FRONT + 0.0795, FRONT + 0.0805, 0.15, 1.85, M["rail"])
CAB.box(-0.3, 0.3, -0.5, 0.5, 1.95, 1.995, M["paint"])                  # roof
for y0, y1 in ((-0.5, -0.465), (0.465, 0.5)):                           # headers + kick plates
    CAB.box(-0.265, 0.265, y0, y1, 1.85, 1.95, M["paint"])
    CAB.box(-0.265, 0.265, y0, y1, 0.1, 0.15, M["paint"])
CAB.box(-0.265, 0.265, 0.47, 0.49, 0.1, 1.95, M["paint"])               # back panel
CAB.box(-0.265, 0.265, -0.465, 0.47, 0.1, 0.11, M["dark"])              # floor plate
CAB.box(-0.265, 0.265, 0.45, 0.47, 0.11, 1.85, M["dark"])               # dark interior back
# roof fans + cable entry brush
for fy in (-0.18, 0.12):
    DET.cyl((0, fy, 1.996), 0.078, 0.003, "Z", M["zinc"], 32)
    DET.cyl((0, fy, 1.998), 0.072, 0.003, "Z", M["vent"], 32)
    DET.cyl((0, fy, 1.9995), 0.018, 0.002, "Z", M["paint"], 16)
DET.box(-0.2, 0.2, 0.36, 0.44, 1.994, 1.999, M["brush"])

# ------------------------------------------------------------------ rack units
BZ_F, BZ_B = FRONT + 0.07, FRONT + 0.08     # bezel front / back
EAR_F = FRONT + 0.074
cable_ports = []

def dbox(x0, x1, z0, z1, mat, proud=0.0015):
    DET.box(x0, x1, BZ_F - proud, BZ_F + 0.001, z0, z1, mat)

def led():
    return M["ledg"] if random.random() < 0.7 else M["ledb"]

def unit(z0, units, kind):
    h = units * U - 0.002
    z1 = z0 + h
    zc = z0 + h / 2
    UNI.box(-0.2195, 0.2195, BZ_F, BZ_B, z0, z1, M["bezel"])
    UNI.box(-0.215, 0.215, BZ_B, FRONT + 0.82, z0 + 0.001, z1 - 0.001, M["chassis"])
    for sx in (-1, 1):
        UNI.box(sx * 0.2195, sx * 0.2413, EAR_F, FRONT + 0.08, z0, z1, M["bezel"])
        for k in range(units):
            DET.cyl((sx * 0.2335, EAR_F - 0.0008, z0 + k * U + U / 2), 0.0028, 0.002, "Y", M["zinc"], 10)
        if kind != "blank":   # pull handle
            hz0, hz1 = z0 + min(0.008, h * 0.2), z1 - min(0.008, h * 0.2)
            UNI.box(sx * 0.226, sx * 0.232, EAR_F - 0.016, EAR_F, hz0, hz0 + 0.005, M["brushed"])
            UNI.box(sx * 0.226, sx * 0.232, EAR_F - 0.016, EAR_F, hz1 - 0.005, hz1, M["brushed"])
            UNI.box(sx * 0.2255, sx * 0.2325, EAR_F - 0.021, EAR_F - 0.015, hz0, hz1, M["brushed"])

    if kind == "blank":
        if random.random() < 0.5:
            dbox(-0.205, 0.205, z0 + 0.006, z1 - 0.006, M["vent"], 0.0005)
        else:
            for k in range(units):
                dbox(-0.2, 0.2, z0 + k * U + 0.017, z0 + k * U + 0.024, M["bezel"], 0.003)
        return

    if kind == "compute":
        # power button with LED ring, status LEDs, asset label
        DET.cyl((-0.2, BZ_F - 0.0008, z1 - 0.011), 0.0048, 0.002, "Y", led(), 16)
        DET.cyl((-0.2, BZ_F - 0.002, z1 - 0.011), 0.0036, 0.004, "Y", M["brushed"], 16)
        for i in range(random.randint(2, 3)):
            dbox(-0.188 + i * 0.008, -0.184 + i * 0.008, z1 - 0.013, z1 - 0.009, led(), 0.0025)
        if units >= 2:
            dbox(-0.212, -0.172, z0 + 0.006, z0 + 0.017, M["label"], 0.0008)
            dbox(-0.165, 0.062, z0 + 0.005, z1 - 0.005, M["vent"], 0.0005)
            n, x = 8, 0.068
            w = (0.212 - x) / n
            for i in range(n):
                xa = x + i * w
                if random.random() < 0.15:          # empty bay filler
                    dbox(xa + 0.0007, xa + w - 0.0007, z0 + 0.005, z1 - 0.005, M["vent"], 0.002)
                    continue
                dbox(xa + 0.0007, xa + w - 0.0007, z0 + 0.005, z1 - 0.005, M["caddy"], 0.003)
                dbox(xa + 0.003, xa + w - 0.003, z0 + 0.008, z0 + 0.008 + h * 0.38, M["brushed"], 0.0045)
                dbox(xa + w / 2 - 0.0016, xa + w / 2 + 0.0016, z1 - 0.012, z1 - 0.009, led(), 0.0045)
        else:
            dbox(-0.165, -0.13, z0 + 0.008, z0 + 0.016, M["label"], 0.0008)
            dbox(-0.12, 0.205, z0 + 0.005, z1 - 0.005, M["vent"], 0.0005)

    elif kind == "storage":
        rows, cols = units - 1, 4
        ax0, ax1, az0, az1 = -0.19, 0.19, z0 + 0.006, z1 - 0.006
        w, hh = (ax1 - ax0) / cols, (az1 - az0) / rows
        for c_ in range(cols):
            for r_ in range(rows):
                xa, za = ax0 + c_ * w, az0 + r_ * hh
                dbox(xa + 0.001, xa + w - 0.001, za + 0.001, za + hh - 0.001, M["caddy"], 0.004)
                dbox(xa + 0.005, xa + w - 0.03, za + 0.004, za + hh - 0.004, M["vent"], 0.0045)
                dbox(xa + w - 0.026, xa + w - 0.006, za + 0.005, za + hh - 0.005, M["brushed"], 0.006)
                dbox(xa + w - 0.029, xa + w - 0.0265, za + hh - 0.008, za + hh - 0.005, led(), 0.006)
                if random.random() < 0.5:
                    dbox(xa + w - 0.029, xa + w - 0.0265, za + hh - 0.013, za + hh - 0.010, led(), 0.006)
        for i in range(3):
            dbox(-0.21, -0.206, z1 - 0.012 - i * 0.008, z1 - 0.008 - i * 0.008, led(), 0.0025)
        dbox(0.196, 0.214, z0 + 0.01, z0 + 0.04, M["label"], 0.0008)

    elif kind == "switch":
        n = 24
        px0, px1 = -0.165, 0.118
        pw = (px1 - px0) / n
        for i in range(n):
            xa = px0 + i * pw + (0.002 if i >= 12 else 0.0)
            for row, (pz0, pz1) in enumerate(((zc - 0.0115, zc - 0.002), (zc + 0.002, zc + 0.0115))):
                dbox(xa + 0.001, xa + pw - 0.001, pz0, pz1, M["port"], 0.0008)
                lz = pz1 + 0.0012 if row else pz0 - 0.0042
                if random.random() < 0.7:
                    dbox(xa + pw / 2 - 0.0012, xa + pw / 2 + 0.0012, lz, lz + 0.003, M["ledg"], 0.0016)
                if random.random() < 0.3:
                    cable_ports.append(Vector((xa + pw / 2, BZ_F - 0.001, (pz0 + pz1) / 2)))
        for i in range(4):   # SFP cages
            xa = 0.132 + (i % 2) * 0.019
            za = zc - 0.0135 + (i // 2) * 0.0145
            dbox(xa, xa + 0.017, za, za + 0.0125, M["zinc"], 0.0012)
            dbox(xa + 0.002, xa + 0.015, za + 0.002, za + 0.0105, M["port"], 0.0016)
        dbox(-0.208, -0.196, zc - 0.005, zc + 0.005, M["port"], 0.0008)       # console
        for i in range(2):
            dbox(-0.19 + i * 0.007, -0.1865 + i * 0.007, zc - 0.0015, zc + 0.0015, led(), 0.0025)
        dbox(0.18, 0.212, z0 + 0.009, z1 - 0.009, M["label"], 0.0008)

layout = [
    (4, "storage"), (4, "storage"), (1, "blank"),
    (2, "compute"), (2, "compute"), (2, "compute"), (1, "blank"),
    (1, "switch"), (1, "switch"), (1, "blank"),
    (2, "compute"), (2, "compute"), (1, "compute"), (1, "compute"),
    (1, "blank"), (3, "storage"), (2, "compute"), (2, "compute"),
    (1, "switch"), (1, "blank"),
]
z, TOP = 0.15, 1.85
for units, kind in layout:
    if z + units * U > TOP:
        break
    unit(z, units, kind)
    z += units * U
while z + U <= TOP:
    unit(z, 1, "blank")
    z += U

# ------------------------------------------------------------------ door (origin on hinge axis)
HINGE = (-0.3, FRONT - 0.0125, 0.0)
DOOR = MB(off=HINGE)
dy0, dy1 = FRONT - 0.025, FRONT - 0.003
DOOR.box(-0.299, -0.255, dy0, dy1, 0.1, 1.95, M["paint"])
DOOR.box(0.255, 0.299, dy0, dy1, 0.1, 1.95, M["paint"])
DOOR.box(-0.256, 0.256, dy0, dy1, 1.87, 1.95, M["paint"])
DOOR.box(-0.256, 0.256, dy0, dy1, 0.1, 0.16, M["paint"])
DOOR.box(-0.2565, 0.2565, FRONT - 0.016, FRONT - 0.0135, 0.159, 1.871, M["perf"])
# swing handle with lock
DOOR.box(0.263, 0.287, dy0 - 0.005, dy0, 0.95, 1.13, M["caddy"])
DOOR.box(0.268, 0.282, dy0 - 0.02, dy0 - 0.005, 0.975, 1.1, M["brushed"])
DOOR.cyl((0.275, dy0 - 0.006, 1.115), 0.0065, 0.004, "Y", M["zinc"], 16)
for hz in (0.3, 1.0, 1.7):
    DOOR.cyl((-0.3, FRONT - 0.0125, hz), 0.0075, 0.07, "Z", M["zinc"], 12)
# status strip + mini display on door header
DOOR.box(-0.18, 0.2, dy0 - 0.0012, dy0 + 0.001, 1.906, 1.912, M["ledb"])
DOOR.box(-0.245, -0.205, dy0 - 0.0012, dy0 + 0.001, 1.896, 1.922, M["port"])
DOOR.box(-0.24, -0.236, dy0 - 0.002, dy0, 1.907, 1.911, M["ledg"])

# ------------------------------------------------------------------ build objects
cab = CAB.build("Cabinet", root, bevel=(0.003, 3))
uni = UNI.build("Server_Units", root, bevel=(0.0012, 2))
det = DET.build("Details", root)
door = DOOR.build("Door", root, bevel=(0.0025, 2))
feet = FEET.build("Feet", root, bevel=(0.0015, 2))

# ------------------------------------------------------------------ patch cables (curve)
cu = bpy.data.curves.new(P + "Patch_Cables", "CURVE")
cu.dimensions = "3D"; cu.bevel_depth = 0.0026; cu.bevel_resolution = 2
cu.resolution_u = 8; cu.use_fill_caps = True
cab_mats = [M["cab_blue"], M["cab_yel"], M["cab_grey"]]
for m in cab_mats:
    cu.materials.append(m)
for p in cable_ports:
    side = -1 if p.x < -0.02 else 1
    drop = 0.03 + random.random() * 0.05
    bulge = 0.032 + random.random() * 0.01
    pts = [p,
           Vector((p.x, BZ_F - 0.02, p.z - 0.003)),
           Vector((p.x + (side * 0.236 - p.x) * 0.55, BZ_F - bulge, p.z - drop * 0.5)),
           Vector((side * 0.237, BZ_F - 0.034, p.z - drop)),
           Vector((side * 0.27, FRONT + 0.045, p.z - drop - 0.01)),
           Vector((side * 0.27, FRONT + 0.25, p.z - drop - 0.03))]
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    r = random.random()
    sp.material_index = 0 if r < 0.55 else (1 if r < 0.75 else 2)
cables = bpy.data.objects.new(P + "Patch_Cables", cu)
col.objects.link(cables); cables.parent = root

dg = bpy.context.evaluated_depsgraph_get()
tris = 0
for o in (cab, uni, det, door, feet, cables):
    me = o.evaluated_get(dg).to_mesh()
    me.calc_loop_triangles(); tris += len(me.loop_triangles)
    o.evaluated_get(dg).to_mesh_clear()
result = {"tris_evaluated": tris, "cables": len(cable_ports), "top_z": round(z, 3)}
