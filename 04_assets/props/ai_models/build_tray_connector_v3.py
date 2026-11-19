"""Tray-connector v3 — our own cryo photonic module (reference-inspired, not a copy).
Builds the tray + photonic chip procedurally and swaps them into trays_setup.blend.
Tray-local coords: X = depth (back cold-rail at -X), Y = width, Z = up.
Stays inside X +-0.073, Y +-0.145, Z +-0.0084 so the TrayStack pitch is unchanged."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
D = bpy.data
SAVE = True

# ================================================================ materials
def pbsdf(m):
    m.use_nodes = True
    return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def mat(name, base, metal=0.0, rough=0.4, coat=0.0, **extra):
    m = D.materials.get(name) or D.materials.new(name)
    b = pbsdf(m)
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    for k, v in extra.items():
        b.inputs[k].default_value = v
    m.diffuse_color = (*base, 1)
    return m

M = {
    "nickel":  mat("TC3_Nickel_Satin",   (0.38, 0.37, 0.355), 1.0, 0.42, **{"Anisotropic": 0.4}),
    "gold":    mat("TC3_Gold_Plate",     (1.00, 0.77, 0.38), 1.0, 0.22),
    "mask":    mat("TC3_Soldermask_Navy", (0.010, 0.015, 0.032), 0.0, 0.40, coat=0.35),
    "trace":   mat("TC3_Mask_Over_Trace", (0.020, 0.032, 0.065), 0.0, 0.34, coat=0.35),
    "lcp":     mat("TC3_Connector_LCP",  (0.26, 0.255, 0.24), 0.0, 0.55),
    "slot":    mat("TC3_Recess_Dark",    (0.004, 0.004, 0.004), 0.0, 0.85),
    "steel":   mat("TC3_Steel",          (0.70, 0.70, 0.72), 1.0, 0.24),
    "silk":    mat("TC3_Silkscreen",     (0.78, 0.78, 0.75), 0.0, 0.6),
    "cap":     mat("TC3_SMD_Ceramic",    (0.36, 0.27, 0.17), 0.0, 0.5),
    "alumina": mat("TC3_Alumina",        (0.80, 0.78, 0.73), 0.0, 0.42),
    "ic":      mat("TC3_IC_Mold",        (0.018, 0.018, 0.02), 0.0, 0.45),
    "glass":   mat("TC3_Glass",          (0.95, 0.97, 1.0), 0.0, 0.03, **{"Transmission Weight": 1.0, "IOR": 1.46}),
    "fiber":   mat("TC3_Fiber_Yellow",   (0.85, 0.55, 0.03), 0.0, 0.42, coat=0.3),
    "boot":    mat("TC3_Rubber_Boot",    (0.03, 0.03, 0.032), 0.0, 0.6),
}

# photonic die: deep violet silicon with a faint waveguide grid (user will detail the chip later)
chip = D.materials.get("TC3_Photonic_Chip") or D.materials.new("TC3_Photonic_Chip")
chip.use_nodes = True
nt = chip.node_tree; nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (600, 0)
bs = nt.nodes.new("ShaderNodeBsdfPrincipled"); bs.location = (300, 0)
tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-700, 0)
mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-500, 0); mp.inputs["Scale"].default_value = (260, 260, 260)
br = nt.nodes.new("ShaderNodeTexBrick"); br.location = (-300, 0); br.offset = 0.0
br.inputs["Color1"].default_value = (0.13, 0.06, 0.26, 1)
br.inputs["Color2"].default_value = (0.11, 0.05, 0.23, 1)
br.inputs["Mortar"].default_value = (0.30, 0.22, 0.42, 1)
br.inputs["Mortar Size"].default_value = 0.02
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], br.inputs["Vector"])
nt.links.new(br.outputs["Color"], bs.inputs["Base Color"])
bs.inputs["Metallic"].default_value = 0.35
bs.inputs["Roughness"].default_value = 0.14
bs.inputs["Coat Weight"].default_value = 0.6
bs.inputs["Coat Roughness"].default_value = 0.03
nt.links.new(bs.outputs[0], out.inputs[0])
chip.diffuse_color = (0.13, 0.06, 0.26, 1)
M["chip"] = chip

ORDER = list(M.keys())
MI = {k: i for i, k in enumerate(ORDER)}

# ================================================================ helpers
def merge(dst, src, xf=None):
    if xf is not None:
        bmesh.ops.transform(src, matrix=xf, verts=src.verts)
    vmap = {v: dst.verts.new(v.co) for v in src.verts}
    for f in src.faces:
        nf = dst.faces.new([vmap[v] for v in f.verts]); nf.material_index = f.material_index; nf.smooth = True
    src.free()

def prism(bm_out, outline, z0, z1, m, bev=0.0003, top_inset=None, xf=None):
    """Extrude a CCW XY outline from z0 to z1, bevel all edges, optional inset/recessed top."""
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, y, z0)) for x, y in outline])
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in (e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)):
        v.co.z = z1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bev > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bev, segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
    for fc in bm.faces: fc.material_index = MI[m]
    if top_inset:
        inset, depth, inner_m = top_inset
        tops = [fc for fc in bm.faces if fc.normal.z > 0.99 and abs(fc.calc_center_median().z - z1) < 1e-6]
        bmesh.ops.inset_region(bm, faces=tops, thickness=inset, depth=0)
        bmesh.ops.translate(bm, vec=(0, 0, -depth), verts=list({v for fc in tops for v in fc.verts}))
        for fc in tops: fc.material_index = MI[inner_m]
    merge(bm_out, bm, xf)

def box(bm, x0, x1, y0, y1, z0, z1, m, bev=0.0003, top_inset=None):
    prism(bm, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, m, bev, top_inset)

def chamfer_rect(x0, x1, y0, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]

def round_rect(x0, x1, y0, y1, r, seg=5):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def circle(cx, cy, r, seg):
    return [(cx + r * math.cos(2 * math.pi * i / seg), cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]

def socket_screw(bm, z0, r=0.0021, h=0.0021, xf=None, cx=0.0, cy=0.0):
    """socket-head cap screw standing on z0 (local), optional transform for side-mounted screws"""
    prism(bm, circle(cx, cy, r, 28), z0, z0 + h, "steel", bev=0.00035, xf=xf)
    prism(bm, circle(cx, cy, r * 0.48, 6), z0 + h - 0.0011, z0 + h + 0.00004, "slot", bev=0, xf=xf)

def disc(bm, cx, cy, r, z, m, seg=20, t=0.00005, xf=None):
    prism(bm, circle(cx, cy, r, seg), z, z + t, m, bev=0, xf=xf)

def side_xf(face, a, b):
    """matrix taking a part built on the XY plane at origin (pointing +Z) onto a tray side face.
    face: '-x' back, '+x' front, '+y'/'-y' sides. (a, b) = in-face coords (y,z) or (x,z)."""
    if face == '-x': return Matrix.Translation((X0, a, b)) @ Matrix.Rotation(math.radians(-90), 4, 'Y')
    if face == '+x': return Matrix.Translation((X1, a, b)) @ Matrix.Rotation(math.radians(90), 4, 'Y')
    if face == '+y': return Matrix.Translation((a, Y1, b)) @ Matrix.Rotation(math.radians(-90), 4, 'X')
    if face == '-y': return Matrix.Translation((a, -Y1, b)) @ Matrix.Rotation(math.radians(90), 4, 'X')

def strip(bm, pts, w, z, m, t=0.00004):
    """flat trace following an XY polyline"""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        d = Vector((bx - ax, by - ay)); L = d.length
        if L < 1e-7: continue
        d /= L; n = Vector((-d.y, d.x)) * (w / 2)
        a = Vector((ax, ay)) - d * (w / 2); b = Vector((bx, by)) + d * (w / 2)
        prism(bm, [tuple(a - n), tuple(b - n), tuple(b + n), tuple(a + n)], z, z + t, m, bev=0)

def tube(bm_out, pts, r, m, seg=8):
    bm = bmesh.new(); rings = []
    pts = [Vector(p) for p in pts]
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = d.cross(Vector((0, 0, 1)))
        side = Vector((0, 1, 0)) if side.length < 1e-6 else side.normalized()
        up = side.cross(d).normalized()
        rings.append([bm.verts.new(p + r * (math.cos(2 * math.pi * k / seg) * side + math.sin(2 * math.pi * k / seg) * up)) for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces: f.material_index = MI[m]
    merge(bm_out, bm)

def smooth_path(ctrl, n=6):
    """Catmull-Rom resample of a 3D control polyline"""
    P = [Vector(p) for p in ctrl]; out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1]); return out

# ================================================================ layout
X0, X1, Y1 = -0.073, 0.073, 0.145
Z_BOT, Z_TOP = -0.0084, 0.0084
BASE_TOP = -0.0030
PCB_TOP = -0.0014
CHIP_C = Vector((-0.0178, 0.0))
CARRIER_TOP = 0.0002
CHIP_T = 0.0008
RAIL_X1 = X0 + 0.012
BX0, BX1 = RAIL_X1 + 0.003, X1 - 0.005       # board X extents
BY0, BY1 = 0.030, Y1 - 0.005                  # board |Y| extents
SEAM_Z = -0.0052

def build_tray():
    bm = bmesh.new()
    rnd = random.Random(7)
    # ---------- cold plate (satin nickel) with fibre notch at the front centre
    nb = 0.011
    c = 0.004
    base = [(X0 + c, -Y1), (X1 - c, -Y1), (X1, -Y1 + c), (X1, -nb), (0.056, -nb), (0.056, nb), (X1, nb),
            (X1, Y1 - c), (X1 - c, Y1), (X0 + c, Y1), (X0, Y1 - c), (X0, -Y1 + c)]
    prism(bm, base, Z_BOT, BASE_TOP, "nickel", bev=0.0005)
    # back cold-rail
    prism(bm, chamfer_rect(X0, RAIL_X1, -Y1, Y1, 0.003), BASE_TOP - 0.0002, Z_TOP, "nickel", bev=0.0006)
    # engraved lines on the rail top
    box(bm, X0 + 0.004, X0 + 0.0048, -0.12, -0.06, Z_TOP, Z_TOP + 0.00004, "slot", bev=0)
    box(bm, X0 + 0.0065, X0 + 0.0073, -0.12, -0.09, Z_TOP, Z_TOP + 0.00004, "slot", bev=0)
    # back face: socket screws into the cold-rail + gold thermal-link pad
    for y in (-0.118, -0.042, 0.042, 0.118):
        socket_screw(bm, 0.0, r=0.0019, h=0.0012, xf=side_xf('-x', y, 0.0030))
    prism(bm, round_rect(-0.022, 0.022, -0.0055, 0.0055, 0.0015), 0.0, 0.0008, "gold", bev=0.0002,
          xf=side_xf('-x', 0.0, 0.0) @ Matrix.Rotation(math.radians(90), 4, 'Z'))
    for y in (-0.015, 0.015):
        socket_screw(bm, 0.0008, r=0.0013, h=0.0009, xf=side_xf('-x', y, 0.0))
    # seam groove + tapped holes on the outer faces (what reads in the stacked column)
    for face, span, holes in (('-x', (-Y1 + 0.004, Y1 - 0.004), ()),
                              ('+y', (X0 + 0.004, X1 - 0.004), (-0.045, 0.0, 0.045)),
                              ('-y', (X0 + 0.004, X1 - 0.004), (-0.045, 0.0, 0.045))):
        a0, a1 = span
        prism(bm, [(-0.00015, a0), (0.00015, a0), (0.00015, a1), (-0.00015, a1)], 0, 0.00005, "slot", bev=0,
              xf=side_xf(face, 0, SEAM_Z) @ Matrix.Rotation(math.radians(90), 4, 'Z') if face != '-x' else side_xf(face, 0, SEAM_Z))
        for h in holes:
            disc(bm, 0, 0, 0.0011, 0, "slot", xf=side_xf(face, h, -0.0068))
    for y0, y1 in ((-Y1 + 0.004, -nb), (nb, Y1 - 0.004)):
        prism(bm, [(-0.00015, y0), (0.00015, y0), (0.00015, y1), (-0.00015, y1)], 0, 0.00005, "slot", bev=0,
              xf=side_xf('+x', 0, SEAM_Z))
    for y in (-0.11, -0.05, 0.05, 0.11):
        disc(bm, 0, 0, 0.0011, 0, "slot", xf=side_xf('+x', y, -0.0068))
    # dowel pins in the exposed centre strip
    for x in (BX0 + 0.004, 0.050):
        for s in (-1, 1):
            prism(bm, circle(x, s * 0.022, 0.0011, 16), BASE_TOP, BASE_TOP + 0.0009, "steel", bev=0.0002)

    for s in (-1, 1):
        # ---------- navy board, chamfered corners
        y0, y1 = sorted((s * BY0, s * BY1))
        prism(bm, chamfer_rect(BX0, BX1, y0, y1, 0.003), BASE_TOP, PCB_TOP, "mask", bev=0.0002)
        # corner + mid screws with gold annular rings
        for x in (BX0 + 0.005, BX1 - 0.005):
            for y in (s * (BY0 + 0.005), s * (BY1 - 0.005), s * 0.085):
                disc(bm, x, y, 0.0034, PCB_TOP, "gold", seg=24)
                socket_screw(bm, PCB_TOP + 0.00005, cx=x, cy=y)
        # ---------- connectors: 3 per board, long axis along X
        for k, yc in enumerate((s * 0.052, s * 0.085, s * 0.118)):
            if k == 1:
                yc = s * 0.0855
            cx0, cx1 = -0.010, 0.026
            box(bm, cx0, cx1, yc - 0.0052, yc + 0.0052, PCB_TOP, PCB_TOP + 0.0042, "lcp", bev=0.0003,
                top_inset=(0.0011, 0.0026, "slot"))
            # LCP tongue inside the slot with a row of gold contacts on each face
            box(bm, cx0 + 0.0022, cx1 - 0.0022, yc - 0.0007, yc + 0.0007, PCB_TOP + 0.0008, PCB_TOP + 0.0034, "lcp", bev=0.0001)
            n_pins = 16
            for p in range(n_pins):
                px = cx0 + 0.0030 + p * (cx1 - cx0 - 0.0060) / (n_pins - 1)
                for side in (-1, 1):
                    y_in = yc + side * 0.0007
                    ya, yb = sorted((y_in, y_in + side * 0.00012))
                    box(bm, px - 0.00025, px + 0.00025, ya, yb, PCB_TOP + 0.0016, PCB_TOP + 0.0033, "gold", bev=0)
            # steel latch ears at both ends
            for ex in (cx0 - 0.0018, cx1 + 0.0002):
                box(bm, ex, ex + 0.0016, yc - 0.0036, yc + 0.0036, PCB_TOP, PCB_TOP + 0.0030, "steel", bev=0.0002)
            # pin-1 silk dot
            box(bm, cx1 + 0.0028, cx1 + 0.0040, yc - 0.0062, yc - 0.0050, PCB_TOP, PCB_TOP + 0.00005, "silk", bev=0)
            # fan-out traces + vias behind each connector
            for o in (-0.0030, -0.0015, 0.0, 0.0015, 0.0030):
                ty = yc + o * 1.9
                pts = [(cx0 - 0.0018, yc + o), (cx0 - 0.0050, yc + o), (cx0 - 0.0050 - abs(o * 0.9), ty), (-0.032, ty)]
                strip(bm, pts, 0.00055, PCB_TOP, "trace")
                disc(bm, -0.032, ty, 0.00055, PCB_TOP, "gold", seg=10, t=0.00006)
                disc(bm, -0.032, ty, 0.00025, PCB_TOP + 0.00006, "slot", seg=8, t=0.00002)
            # two decoupling caps in front of each connector
            for j, dy in enumerate((-0.0028, 0.0028)):
                x = cx1 + 0.0065
                box(bm, x - 0.0008, x + 0.0008, yc + dy - 0.0004, yc + dy + 0.0004, PCB_TOP, PCB_TOP + 0.0007, "cap", bev=0.0001)
                for e in (-1, 1):
                    box(bm, x + e * 0.0008 - 0.0002, x + e * 0.0008 + 0.0002, yc + dy - 0.00042, yc + dy + 0.00042,
                        PCB_TOP, PCB_TOP + 0.00072, "steel", bev=0.00005)
        # ---------- QFN bias IC + 0402 array near the chip edge
        qx, qy = -0.046, s * 0.050
        box(bm, qx - 0.0025, qx + 0.0025, qy - 0.0025, qy + 0.0025, PCB_TOP, PCB_TOP + 0.0008, "ic", bev=0.00015)
        disc(bm, qx - 0.0017, qy - 0.0017, 0.0003, PCB_TOP + 0.0008, "silk", seg=8, t=0.00002)
        for i in range(6):
            for j in range(2):
                x = -0.047 + i * 0.0026; y = s * (0.0355 + j * 0.0022)
                box(bm, x - 0.0005, x + 0.0005, y - 0.00025, y + 0.00025, PCB_TOP, PCB_TOP + 0.00045, "cap", bev=0.00004)
        # traces from the 0402 array to the channel edge
        for i in range(6):
            x = -0.047 + i * 0.0026
            strip(bm, [(x, s * 0.0345), (x, s * (BY0 + 0.0012))], 0.0004, PCB_TOP, "trace")
        # ---------- silkscreen: ID lines + 2D datamatrix on the front corner
        fx, fy = 0.047, s * 0.106
        for i, w in enumerate((0.018, 0.012, 0.015)):
            x = fx + i * 0.0026
            ya, yb = sorted((fy, fy + s * w))
            box(bm, x, x + 0.0012, ya, yb, PCB_TOP, PCB_TOP + 0.00005, "silk", bev=0)
        dmx, dmy, cell = 0.050, s * 0.068, 0.0006
        for i in range(10):
            for j in range(10):
                edge = i == 0 or j == 0 or (i == 9 and j % 2 == 0) or (j == 9 and i % 2 == 0)
                if edge or rnd.random() < 0.45:
                    box(bm, dmx + i * cell, dmx + (i + 1) * cell, dmy + j * cell, dmy + (j + 1) * cell,
                        PCB_TOP, PCB_TOP + 0.00005, "silk", bev=0)
        # gold test points
        for (x, y) in ((0.040, s * 0.040), (0.040, s * 0.130), (-0.040, s * 0.132)):
            disc(bm, x, y, 0.0009, PCB_TOP, "gold", seg=14, t=0.00006)

    # ---------- chip carrier: gold-plated copper pedestal + alumina bond ring
    cx, cy = CHIP_C
    hc = 0.0185
    prism(bm, round_rect(cx - hc, cx + hc, cy - hc, cy + hc, 0.0025), BASE_TOP, CARRIER_TOP, "gold", bev=0.0003)
    hi, ho, rt = 0.0114, 0.0150, CARRIER_TOP + 0.0004
    box(bm, cx - ho, cx + ho, cy + hi, cy + ho, CARRIER_TOP, rt, "alumina", bev=0.0001)
    box(bm, cx - ho, cx + ho, cy - ho, cy - hi, CARRIER_TOP, rt, "alumina", bev=0.0001)
    box(bm, cx - ho, cx - hi, cy - hi, cy + hi, CARRIER_TOP, rt, "alumina", bev=0.0001)
    for i in range(11):                       # bond pads along both long sides
        x = cx - 0.0090 + i * 0.0018
        for sy in (-1, 1):
            box(bm, x - 0.00045, x + 0.00045, cy + sy * 0.0128 - 0.0007, cy + sy * 0.0128 + 0.0007, rt, rt + 0.00004, "gold", bev=0)
    for i in range(6):                        # and the back side
        y = cy - 0.0075 + i * 0.003
        box(bm, cx - 0.0135, cx - 0.0121, y - 0.0005, y + 0.0005, rt, rt + 0.00004, "gold", bev=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            socket_screw(bm, CARRIER_TOP, r=0.0011, h=0.0008, cx=cx + sx * 0.0166, cy=cy + sy * 0.0166)
    # RuOx-style temperature sensor behind the carrier, with gold leads
    sx0 = cx - hc - 0.006
    box(bm, sx0 - 0.0016, sx0 + 0.0016, -0.0030, 0.0030, BASE_TOP, BASE_TOP + 0.0012, "ic", bev=0.0002)
    tx = sx0 - 0.0075                        # alumina terminal pad the leads solder to
    box(bm, tx - 0.0022, tx + 0.0022, -0.0040, 0.0040, BASE_TOP, BASE_TOP + 0.0004, "alumina", bev=0.0001)
    for y in (-0.0018, 0.0018):
        box(bm, tx - 0.0012, tx + 0.0012, y - 0.0009, y + 0.0009, BASE_TOP + 0.0004, BASE_TOP + 0.00045, "gold", bev=0)
        tube(bm, smooth_path([(sx0 - 0.0016, y, BASE_TOP + 0.0006), (sx0 - 0.0038, y, BASE_TOP + 0.0008),
                              (tx, y, BASE_TOP + 0.00055)], 4), 0.00018, "gold", seg=6)

    # ---------- fibre array unit: glass V-groove block + lid, steel bracket, rubber boot
    fx0 = cx + 0.0105                       # chip front edge
    box(bm, fx0, fx0 + 0.0056, -0.0036, 0.0036, CARRIER_TOP, CARRIER_TOP + 0.0016, "glass", bev=0.0001)
    box(bm, fx0 + 0.0008, fx0 + 0.0056, -0.0030, 0.0030, CARRIER_TOP + 0.0016, CARRIER_TOP + 0.0023, "glass", bev=0.0001)
    bx = cx + hc
    box(bm, bx - 0.001, bx + 0.0075, -0.0034, 0.0034, BASE_TOP, CARRIER_TOP - 0.0003, "steel", bev=0.0002)
    zb = CARRIER_TOP + 0.0007
    tube(bm, [(fx0 + 0.0056, 0, zb), (bx + 0.0075, 0, zb)], 0.0013, "boot", seg=16)
    zf = BASE_TOP + 0.00048
    for s in (-1, 1):
        tube(bm, smooth_path([(bx + 0.0072, s * 0.0005, zb), (bx + 0.012, s * 0.0011, zb - 0.0010),
                              (bx + 0.018, s * 0.0013, zf), (0.050, s * 0.0013, zf),
                              (0.0565, s * 0.0013, zf - 0.0008), (0.0595, s * 0.0013, zf - 0.0045),
                              (0.0605, s * 0.0013, Z_BOT - 0.0035)], 5), 0.00045, "fiber", seg=10)
    # fibre saddle clips
    for x in (0.022, 0.040):
        prism(bm, round_rect(x - 0.002, x + 0.002, -0.0048, 0.0048, 0.0012), BASE_TOP, BASE_TOP + 0.0014, "steel", bev=0.0002)
        socket_screw(bm, BASE_TOP + 0.0014, r=0.0010, h=0.0007, cx=x, cy=0.0)
    return bm

def build_chip():
    bm = bmesh.new()
    h = 0.0105
    box(bm, -h, h, -h, h, -CHIP_T / 2, CHIP_T / 2, "chip", bev=0.00015)
    return bm

def to_mesh(bm, name):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-8)
    me = D.meshes.get(name)
    if me: me.clear_geometry()
    else: me = D.meshes.new(name)
    me.materials.clear()
    for k in ORDER: me.materials.append(M[k])      # slots BEFORE geometry, or indices reset
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(40))
    return me

tray_me = to_mesh(build_tray(), "TrayConnector_v3")
chip_me = to_mesh(build_chip(), "PhotonicChip_v3")
chip_z = CARRIER_TOP + CHIP_T / 2
both = build_tray()
cb = build_chip(); bmesh.ops.translate(cb, vec=(CHIP_C.x, CHIP_C.y, chip_z), verts=cb.verts)
merge(both, cb)
with_me = to_mesh(both, "TrayConnector_v3_with_chip")

# ================================================================ swap
spare = D.collections["spare_parts"]
hero = D.objects["Tray-connector"]; chip_ob = D.objects["photonic_chip"]; inst = D.objects["Tray-connector-with_chip"]
for ob, new in ((hero, tray_me), (chip_ob, chip_me), (inst, with_me)):
    old = ob.data
    if old == new: continue
    generated = old.name.startswith(("TrayConnector_v", "PhotonicChip_v"))
    if not generated:   # original hand-made placeholder: keep it in spare_parts
        keep = D.objects.get(ob.name + "_placeholder") or D.objects.new(ob.name + "_placeholder", old)
        keep.data = old
        if keep.name not in spare.objects: spare.objects.link(keep)
        keep.matrix_world = ob.matrix_world.copy(); keep.hide_render = True; keep.hide_viewport = True
    ob.data = new
    for sl in ob.material_slots: sl.link = 'DATA'
    if generated and old.users == 0:
        D.meshes.remove(old)
chip_ob.location = (CHIP_C.x, CHIP_C.y, chip_z)
for m in list(D.materials):        # drop unused materials from earlier generated versions
    if m.name.startswith("TC_") and m.users == 0:
        D.materials.remove(m)
print("TRAY verts", len(tray_me.vertices), "WITH", len(with_me.vertices))
if SAVE:
    bpy.ops.wm.save_mainfile()
print("MODEL OK")
