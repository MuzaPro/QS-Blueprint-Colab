"""Make the 'fugly' SH_1 version of the neutral-atom QC: a lab setup forced into a box.

Run:  blender -b --factory-startup --python build_neutral_atom_qc_fugly.py
Reads neutral_atom_qc.blend (keeps the user's cameras, lights, logo, bevels) and
writes neutral_atom_qc_fugly.blend. Never touches the clean file.

Adds: institutional-grey powder coat, clear-anodised extrusion, a mismatched
replacement panel, dull accent strips, cool fluorescent hood light, panel screws,
blackout cloth drapes, gaffer / duct tape, a taped acrylic patch, laser warning
stickers, paper labels, an open rack door, a door left ajar and cable spaghetti.
New objects are prefixed NAF_ in collection NAQC_Fugly. Red lasers, no cyan.
"""
import bpy, bmesh, math, random
from mathutils import Vector as V, Matrix as Mx

DIR = r"C:\Users\mrgav\Documents\GitHub\QS-Blueprint-Colab\04_assets\props\ai_models"
SRC = DIR + r"\neutral_atom_qc.blend"
OUT = globals().get("OUT", DIR + r"\neutral_atom_qc_fugly.blend")
SAVE = globals().get("SAVE", True)
# which layers to add: palette (grey paint, dull strips, fluorescent, replaced panels), screws, cloth, tape, cables.
# The open rack door and the ajar sliding door always come with it (the cable bundles exit through them).
PARTS = set(globals().get("PARTS", ("palette", "screws", "cloth", "tape", "cables")))
COLL_NAME = globals().get("COLL_NAME", "NAQC_Fugly")
rng = random.Random(11)

bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
D = bpy.data
W2, D2, PZ, HZ, CZ, TT = 1.45, 0.75, 0.88, 2.12, 2.45, 0.90
ROOT = D.objects["NAQC_root"]
FC = D.collections.new(COLL_NAME); D.collections["NAQC"].children.link(FC)

# ------------------------------------------------------------------ materials
def pmat(name, col, metal=0.0, rough=0.5, trans=0.0, sheen=0.0, emit=None, estr=0.0):
    m = D.materials.new(name); p = m.node_tree.nodes["Principled BSDF"]
    p.inputs['Base Color'].default_value = (*col, 1); p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough; p.inputs['Transmission Weight'].default_value = trans
    p.inputs['Sheen Weight'].default_value = sheen
    if emit:
        p.inputs['Emission Color'].default_value = (*emit, 1); p.inputs['Emission Strength'].default_value = estr
    m.diffuse_color = (*(emit or col), 1)
    return m

def fabric(name, col):
    m = pmat(name, col, 0.0, 0.92, sheen=0.25)
    nt = m.node_tree; N = nt.nodes; p = N["Principled BSDF"]
    tc = N.new('ShaderNodeTexCoord'); n = N.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 900
    n.inputs['Detail'].default_value = 2
    b = N.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.25; b.inputs['Distance'].default_value = 0.0003
    nt.links.new(tc.outputs['Object'], n.inputs['Vector']); nt.links.new(n.outputs['Factor'], b.inputs['Height'])
    nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    return m

M = {
    'cloth': fabric("NAF_blackout_cloth", (0.008, 0.008, 0.009)),
    'tape_black': pmat("NAF_tape_black", (0.025, 0.025, 0.027), 0.0, 0.62, sheen=0.3),
    'tape_silver': pmat("NAF_tape_silver", (0.55, 0.56, 0.57), 0.7, 0.42),
    'paper': pmat("NAF_paper", (0.82, 0.81, 0.76), 0.0, 0.85),
    'ink': pmat("NAF_ink", (0.03, 0.03, 0.03), 0.0, 0.6),
    'yellow': pmat("NAF_warn_yellow", (0.95, 0.72, 0.02), 0.0, 0.45),
    'acrylic': pmat("NAF_acrylic_frosted", (0.9, 0.9, 0.9), 0.0, 0.35, trans=1.0),
    'screw': D.materials["NA_stainless_b"],
    'strip_plastic': pmat("NAF_powerstrip", (0.78, 0.78, 0.75), 0.0, 0.4),
    'plug': pmat("NAF_plug_black", (0.03, 0.03, 0.03), 0.0, 0.45),
    'c_black': D.materials["NA_rubber"], 'c_grey': D.materials["NA_cable_grey"],
    'c_white': pmat("NAF_cable_white", (0.75, 0.75, 0.72), 0.0, 0.45),
    'c_red': pmat("NAF_cable_red", (0.45, 0.03, 0.02), 0.0, 0.45),
    'c_blue': pmat("NAF_cable_blue", (0.04, 0.06, 0.28), 0.0, 0.45),   # dark blue, not cyan
    'c_yellow': D.materials["NA_fibre"],
    'c_orange': pmat("NAF_fibre_orange", (0.9, 0.3, 0.03), 0.0, 0.4),
    'fluoro': pmat("NAF_fluorescent", (1.0, 0.98, 0.93), emit=(1.0, 0.98, 0.93), estr=9.0),
}
if "palette" in PARTS:
    # replacement panel = copy of graphite (so the detail module treats it as paint)
    rep = D.materials["NA_graphite"].copy(); rep.name = "NA_panel_replaced"
    
    # dull the sexy accent lines (plinth + crown) — no glow, just a cheap grey trim strip
    lw = D.materials["NA_led_warm"].node_tree.nodes["Principled BSDF"]
    lw.inputs['Emission Strength'].default_value = 0.0
    lw.inputs['Base Color'].default_value = (0.3, 0.3, 0.29, 1); lw.inputs['Roughness'].default_value = 0.5
    D.materials["NA_led_warm"].diffuse_color = (0.3, 0.3, 0.29, 1)
    # hood strips -> cool fluorescent
    hl = D.objects["NA_Hood_LEDs"].data
    for i, m in enumerate(hl.materials):
        if m and m.name == "NA_led_warm": hl.materials[i] = M['fluoro']
    
    LEVEL = 'fugly'
    OVERRIDES = {
        'NA_graphite':       dict(col=(0.40, 0.41, 0.40), metal=0.0, rough=0.6, coat=0.0),   # RAL 7035-ish, aged
        'NA_panel_replaced': dict(col=(0.53, 0.49, 0.39), metal=0.0, rough=0.5, coat=0.0),   # yellowed older panel
        'NA_logo_panel':     dict(col=(0.45, 0.46, 0.45), metal=0.0, rough=0.5, coat=0.0),
        'NA_extrusion':      dict(col=(0.72, 0.73, 0.74), metal=1.0, rough=0.42),            # clear anodised
    }
    exec(open(DIR + r"\na_material_detail.py").read())
    
    def reassign(obj_name, test, new_mat, only="NA_graphite"):
        me = D.objects[obj_name].data
        if new_mat.name not in [m.name for m in me.materials if m]: me.materials.append(new_mat)
        ni = [m.name if m else "" for m in me.materials].index(new_mat.name)
        names = [m.name if m else "" for m in me.materials]
        n = 0
        for p in me.polygons:
            if names[p.material_index] == only and test(p.center):
                p.material_index = ni; n += 1
        return n
    print("replaced faces:",
          reassign("NA_Plinth", lambda c: c.x > 0.5 and c.y < -D2 + 0.001 and 0.09 < c.z < PZ - 0.01, rep),
          reassign("NA_Service_Cabinet", lambda c: c.y < -D2 - 0.001 and 0.09 < c.z < CZ - 0.03, rep))

# ------------------------------------------------------------------ mesh builder (minimal)
def T(x, y, z): return Mx.Translation((x, y, z))
def R(axis, deg): return Mx.Rotation(math.radians(deg), 4, axis)
AXY = R('X', -90)

class MB:
    def __init__(s, name): s.name, s.bm, s.mats = name, bmesh.new(), []
    def mi(s, m):
        if m not in s.mats: s.mats.append(m)
        return s.mats.index(m)
    def add(s, verts, faces, m, Mt=Mx(), smooth=False):
        vs = [s.bm.verts.new(Mt @ V(v)) for v in verts]; i = s.mi(m)
        for f in faces:
            nf = s.bm.faces.new([vs[k] for k in f]); nf.material_index = i; nf.smooth = smooth
    def box(s, Mt, size, m):
        x, y, z = (a / 2 for a in size)
        v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
        s.add(v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m, Mt)
    def cyl(s, Mt, r, h, m, seg=12):
        v = [(r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z) for z in (-h / 2, h / 2) for k in range(seg)]
        f = [tuple(range(seg))[::-1], tuple(range(seg, 2 * seg))] + [(k, (k + 1) % seg, seg + (k + 1) % seg, seg + k) for k in range(seg)]
        s.add(v, f, m, Mt, smooth=True)
    def prism(s, Mt, pts2d, h, m):
        """Flat polygon (x, z) extruded along -Y by h (faces -Y)."""
        n = len(pts2d)
        v = [(x, 0, z) for x, z in pts2d] + [(x, -h, z) for x, z in pts2d]
        f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(k, n + k, n + (k + 1) % n, (k + 1) % n) for k in range(n)]
        s.add(v, f, m, Mt)
    def torus(s, Mt, Rr, r, m, seg=16, seg2=6):
        v = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            for j in range(seg2):
                b = 2 * math.pi * j / seg2; rr = Rr + r * math.cos(b)
                v.append((rr * math.cos(a), rr * math.sin(a), r * math.sin(b)))
        f = [(k * seg2 + j, ((k + 1) % seg) * seg2 + j, ((k + 1) % seg) * seg2 + (j + 1) % seg2, k * seg2 + (j + 1) % seg2)
             for k in range(seg) for j in range(seg2)]
        s.add(v, f, m, Mt, smooth=True)
    def done(s, mods=()):
        me = D.meshes.new(s.name)
        for m in s.mats: me.materials.append(m)
        s.bm.normal_update(); s.bm.to_mesh(me); s.bm.free()
        ob = D.objects.new(s.name, me); FC.objects.link(ob); ob.parent = ROOT
        for typ, kw in mods:
            md = ob.modifiers.new(typ.title(), typ)
            for k, v in kw.items(): setattr(md, k, v)
        return ob

# ------------------------------------------------------------------ open the rack door, leave a sliding door ajar
def rotate_mesh_about(obj, pivot, deg):
    Mt = T(*pivot) @ R('Z', deg) @ T(*(-V(pivot)))
    obj.data.transform(Mt)
rotate_mesh_about(D.objects["NA_Rack_Door"], (-W2 - 0.67, -D2 - 0.012, 0), -105)
D.objects["NA_Door_R"].location.x -= 0.24   # slid open: gap at the right end for the cable bundle

# ------------------------------------------------------------------ screws around the sheet-metal panels
if "screws" in PARTS:
    sw = MB("NAF_Panel_Screws")
    def screw_row(p0, p1, y, step=0.16):
        p0, p1 = V(p0), V(p1); n = max(2, int((p1 - p0).length / step) + 1)
        for i in range(n):
            p = p0.lerp(p1, i / (n - 1))
            sw.cyl(T(p.x, y, p.z) @ AXY, 0.0045, 0.003, M['screw'], seg=10)
    for x0, x1 in ((-W2, -0.5), (-0.5, 0.5), (0.5, W2)):
        a, b = x0 + 0.025, x1 - 0.025
        for z in (0.125, PZ - 0.04): screw_row((a, 0, z), (b, 0, z), -D2 - 0.0215)
        for x in (a, b): screw_row((x, 0, 0.125), (x, 0, PZ - 0.04), -D2 - 0.0215)
    for z in (HZ + 0.03, CZ - 0.03): screw_row((-W2 + 0.03, 0, z), (W2 - 0.03, 0, z), -D2 - 0.0615)
    for z in (0.13, CZ - 0.07): screw_row((W2 + 0.05, 0, z), (W2 + 0.64, 0, z), -D2 - 0.0195, 0.12)
    sw.done()

# ------------------------------------------------------------------ blackout cloth drapes
def drape(name, x0, x1, ybase, ztop, zbot, folds, amp, gather, gx, y_back=-0.45, seed=0.0):
    nu, nv_top, nv_hang = 72, 10, 46
    mb = MB(name); rows = []
    for j in range(nv_top + nv_hang + 1):
        row = []
        for i in range(nu + 1):
            u = i / nu
            ph = seed + 1.3 * math.sin(u * 5.0 + seed)
            if j <= nv_top:   # lying on top of the crown, a few soft ripples
                t = j / nv_top
                y = y_back + (ybase + 0.012 - y_back) * t
                z = ztop + 0.004 + 0.006 * (1 + math.sin(2 * math.pi * folds * u * 0.7 + ph)) * (0.3 + 0.7 * t)
                x = x0 + (x1 - x0) * u
            else:             # hanging over the front edge with deepening folds
                t = (j - nv_top) / nv_hang
                zb = zbot + 0.07 * math.sin(u * 7.0 + seed) + 0.035 * math.sin(u * 19.0 + 2 * seed)
                z = ztop - 0.01 - (ztop - 0.01 - zb) * t
                wob = 0.6 * math.sin(2 * math.pi * folds * u + ph) + 0.4 * math.sin(2 * math.pi * folds * 2.3 * u + 2 * ph)
                k = 0.3 + 0.7 * t
                y = ybase - amp * k - amp * k * wob
                xu = x0 + (x1 - x0) * u
                x = xu + (gx - xu) * gather * t * t
                z -= 0.02 * t * t * math.sin(u * 13.0 + seed)
            row.append((x, y, z))
        rows.append(row)
    flat = [p for row in rows for p in row]
    W = nu + 1
    faces = [(j * W + i, j * W + i + 1, (j + 1) * W + i + 1, (j + 1) * W + i) for j in range(len(rows) - 1) for i in range(nu)]
    mb.add(flat, faces, M['cloth'], smooth=True)
    return mb.done(mods=[('SOLIDIFY', dict(thickness=0.0015)), ('SUBSURF', dict(levels=1, render_levels=2))])

if "cloth" in PARTS:
    drape("NAF_Blackout_Cloth_R", 0.72, 1.44, -0.822, CZ, 1.30, 3.2, 0.011, 0.04, 1.44, seed=1.0)
    drape("NAF_Blackout_Cloth_L", -1.44, -1.02, -0.822, CZ, 1.78, 2.4, 0.008, 0.0, -1.44, seed=3.0)

# ------------------------------------------------------------------ tape, acrylic patch, stickers, labels
if "tape" in PARTS:
    tp = MB("NAF_Tape_Stickers")
    def tape(p, size, rot_y=0.0, m='tape_black', face='front'):
        Mt = T(*p) @ R('Y', rot_y) if face == 'front' else T(*p) @ R('Z', rot_y)
        tp.box(Mt, size, M[m])
    # cloth taped to the crown top
    for x in (0.8, 1.1, 1.35, -1.35, -1.0):
        tape((x, -0.62, CZ + 0.012), (0.05, 0.28, 0.0012), m='tape_black', face='top')
    # acrylic patch taped over a cracked lower corner of the left door
    DL_y = -D2 - 0.036 - 0.0055
    tp.box(T(-0.95, DL_y - 0.002, 1.12), (0.36, 0.003, 0.26), M['acrylic'])
    for (dx, dz, sx, sz) in ((0, 0.13, 0.4, 0.05), (0, -0.13, 0.4, 0.05), (-0.18, 0, 0.05, 0.3), (0.18, 0, 0.05, 0.3)):
        tape((-0.95 + dx, DL_y - 0.0042, 1.12 + dz), (sx, 0.0012, sz), rot_y=rng.uniform(-2, 2), m='tape_silver')
    # tape over the door seam / frame and holding a cable to the left mullion
    for z in (1.35, 1.8):
        tape((-W2 - 0.004, -D2 - 0.01, z), (0.06, 0.0012, 0.05), rot_y=rng.uniform(-6, 6), m='tape_silver')
    tape((-0.02, -D2 - 0.048, 1.62), (0.05, 0.0012, 0.12), rot_y=4, m='tape_black')
    # bottom corners of the cloth taped down to the frame / glass
    for x, rz in ((0.78, 8), (1.4, -6), (-1.06, 5)):
        zc = 1.3 if x > 0 else 1.78
        tape((x, -0.85, zc), (0.05, 0.0012, 0.16), rot_y=rz, m='tape_black')
    
    def warning(cx, y, cz, size=0.09):
        h = size * math.sqrt(3) / 2
        tri = lambda s: [(-s / 2, -h * s / size / 3), (s / 2, -h * s / size / 3), (0, 2 * h * s / size / 3)]
        tp.prism(T(cx, y, cz), tri(size), 0.0008, M['yellow'])
        tp.prism(T(cx, y - 0.0008, cz), tri(size * 0.86), 0.0004, M['ink'])
        tp.prism(T(cx, y - 0.0012, cz), tri(size * 0.72), 0.0004, M['yellow'])
        tp.cyl(T(cx - size * 0.1, y - 0.0018, cz) @ AXY, size * 0.06, 0.0004, M['ink'], seg=16)
        tp.box(T(cx + size * 0.08, y - 0.0018, cz), (size * 0.3, 0.0004, size * 0.025), M['ink'])
        for a in range(0, 360, 45):
            tp.box(T(cx - size * 0.1, y - 0.0018, cz) @ R('Y', a) @ T(size * 0.11, 0, 0), (size * 0.05, 0.0004, size * 0.015), M['ink'])
    def label(cx, y, cz, w=0.09, hgt=0.055, rot=0.0, lines=3):
        Mt = T(cx, y, cz) @ R('Y', rot)
        tp.box(Mt, (w, 0.0006, hgt), M['paper'])
        for i in range(lines):
            lw_ = w * rng.uniform(0.45, 0.8)
            tp.box(Mt @ T(-w / 2 + 0.008 + lw_ / 2, -0.0004, hgt / 2 - 0.012 - i * (hgt - 0.02) / max(1, lines - 1) * 0.9),
                   (lw_, 0.0003, 0.0035), M['ink'])
    
    warning(-0.75, -D2 - 0.042, 1.95, 0.1)             # left glass door, top (clear of the cloth and the dive)
    warning(-1.0, -D2 - 0.023, 0.7, 0.08)               # plinth left door
    warning(W2 + 0.34, -D2 - 0.021, 0.72, 0.09)         # service cabinet door, below the logo
    label(0.0, -D2 - 0.022, 0.62, rot=-3)              # plinth centre
    label(-0.82, -D2 - 0.0225, 0.45, 0.12, 0.07, 4, 4)
    label(0.9, -D2 - 0.022, 0.55, 0.07, 0.04, 2, 2)
    label(W2 + 0.3, -D2 - 0.02, 0.9, 0.14, 0.09, -2, 5)
    label(-0.3, -D2 - 0.0625, CZ - 0.09, 0.1, 0.05, 3, 3)   # crown fascia
    label(1.15, -D2 - 0.0625, HZ + 0.12, 0.08, 0.05, -5, 3)
    # sticky notes on the rack frame
    for i, z in enumerate((1.45, 1.38)):
        tp.box(T(-W2 - 0.03 + i * 0.02, -D2 - 0.002, z) @ R('Y', rng.uniform(-8, 8)), (0.06, 0.0006, 0.06),
               M['yellow'] if i == 0 else M['paper'])
    tp.done()

# ------------------------------------------------------------------ cable spaghetti
SPL = {k: [] for k in ('c_black', 'c_grey', 'c_white', 'c_red', 'c_blue', 'c_yellow', 'c_orange')}
zt = MB("NAF_ZipTies")

def catmull(pts, n=4):
    pts = [V(p) for p in pts]; out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1]); return out

def bundle(path, n, mats, spread=0.01, r=1.0, ties=0, floor_z=None):
    pts = catmull(path, 4)
    for c in range(n):
        a0 = rng.uniform(0, 2 * math.pi); rr = spread * math.sqrt(rng.uniform(0.1, 1)); tw = rng.uniform(-0.6, 0.6)
        sp = []
        for i, p in enumerate(pts):
            tng = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            ax = tng.cross(V((0, 0, 1)))
            if ax.length < 1e-3: ax = V((1, 0, 0))
            ax.normalize(); ay = tng.cross(ax).normalized()
            a = a0 + tw * i
            loose = 1.0 + 1.5 * math.sin(i * 0.37 + c)  ** 2       # strands drift apart between ties
            q = p + (ax * math.cos(a) + ay * math.sin(a)) * rr * loose
            if floor_z is not None: q.z = max(q.z, floor_z + 0.003 * (1 + c % 3))
            sp.append(q)
        SPL[rng.choice(mats)].append((sp, r * rng.uniform(0.7, 1.3)))
    for k in range(ties):
        i = int((k + 1) * len(pts) / (ties + 1))
        tng = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        q = tng.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        zt.torus(Mx.Translation(pts[i]) @ q, spread * 1.9 + 0.004, 0.0016, M['plug'])
        zt.box(Mx.Translation(pts[i]) @ q @ T(spread * 1.9 + 0.006, 0, 0), (0.006, 0.005, 0.004), M['plug'])

def sag(p0, p1, depth, n=6):
    p0, p1 = V(p0), V(p1)
    return [p0.lerp(p1, i / n) - V((0, 0, depth * 4 * (i / n) * (1 - i / n))) for i in range(n + 1)]

FZ = 0.0
mixed = ['c_black', 'c_black', 'c_grey', 'c_white', 'c_red', 'c_blue']
fib = ['c_yellow', 'c_yellow', 'c_orange']
xr0, xr1 = -W2 - 0.67, -W2 - 0.02
# 1) patch cables spilling out of the open rack, down to the floor, across the front to the plinth
for k in range(7):
    x = rng.uniform(xr0 + 0.12, xr1 - 0.12); z = rng.uniform(0.5, 1.9)
    xe = rng.uniform(-1.2, 0.4)
    path = [(x, -0.69, z), (x, -0.8, z - 0.05), (x + 0.05, -0.92, z * 0.5), (x + 0.12, -0.98 - 0.02 * k, FZ + 0.01),
            ((x + xe) / 2, -1.0 - 0.03 * (k % 3), FZ + 0.01), (xe, -0.9, FZ + 0.01), (xe + 0.05, -0.77, 0.06), (xe + 0.05, -0.6, 0.06)]
    bundle(path, rng.randint(1, 3), mixed, 0.006, ties=0, floor_z=FZ)
# 2) bundle out of the gap at the right sliding door, drooping to the floor and into the service cabinet
gx = W2 - 0.12
bundle([(1.2, -0.45, TT + 0.02), (gx, -0.62, TT + 0.08), (gx, -0.8, 1.02), (gx + 0.02, -0.9, 0.85), (gx + 0.05, -0.97, 0.3),
        (gx + 0.15, -1.0, FZ + 0.01), (W2 + 0.3, -0.98, FZ + 0.01), (W2 + 0.34, -0.8, 0.05), (W2 + 0.34, -0.6, 0.05)],
       9, mixed + fib, 0.014, ties=3, floor_z=FZ)
# 3) slack loops hanging over the crown front edge
for k, x in enumerate((-0.75, -0.35, 0.1, 0.5)):
    w = rng.uniform(0.18, 0.32); dz = rng.uniform(0.12, 0.3)
    path = [(x, -0.15, CZ + 0.02), (x, -0.6, CZ + 0.02), (x + 0.02, -0.82, CZ + 0.0), (x + w * 0.3, -0.835, CZ - dz),
            (x + w * 0.7, -0.835, CZ - dz * 0.9), (x + w, -0.82, CZ + 0.0), (x + w, -0.6, CZ + 0.02), (x + w + 0.1, -0.1, CZ + 0.02)]
    bundle(path, rng.randint(2, 4), mixed + fib, 0.008, ties=1)
# 4) drop down the gap between rack and hood, taped to the frame
bundle([(-W2 + 0.2, -0.3, CZ + 0.02), (-W2 - 0.005, -0.7, CZ + 0.01), (-W2 - 0.005, -0.8, 2.2), (-W2 - 0.006, -0.79, 1.6),
        (-W2 - 0.006, -0.79, 1.0), (-W2 - 0.01, -0.82, 0.4), (-W2 + 0.05, -0.95, FZ + 0.01), (-0.9, -1.05, FZ + 0.01)],
       5, mixed, 0.01, ties=2, floor_z=FZ)
# 5) inside the hood: loops hanging from the overhead tray and strands across the table (dive path kept clear)
for k in range(6):
    x = rng.choice([-1.2, -0.9, -0.6, 0.8, 1.0, 1.25]) + rng.uniform(-0.08, 0.08)
    path = sag((x, D2 - 0.12, HZ - 0.1), (x + rng.uniform(-0.3, 0.3), D2 - 0.12, HZ - 0.1), rng.uniform(0.25, 0.55))
    bundle(path, rng.randint(1, 3), mixed + fib, 0.006)
for k in range(10):
    side = rng.choice([-1, 1])
    xa = rng.uniform(-1.2, -0.1) if side < 0 else rng.uniform(0.65, 1.25)
    ya = rng.uniform(-0.5, 0.5); xb = xa + rng.uniform(-0.4, 0.4); xb = min(max(xb, -1.25), 1.25)
    if 0.0 < xb < 0.65: xb = -0.05 if side < 0 else 0.7
    path = [(xa, ya, TT + 0.05), (xa, ya, TT + 0.006), ((xa + xb) / 2, (ya + D2 - 0.15) / 2, TT + 0.006),
            (xb, D2 - 0.15, TT + 0.006), (xb, D2 - 0.08, TT + 0.15)]
    bundle(path, 1, mixed + fib, 0.0, floor_z=TT)
# 6) power strip on the floor by the rack, with plugged-in leads
ps = MB("NAF_Power_Strip")
px, py = -1.25, -1.12
ps.box(T(px, py, 0.022), (0.46, 0.065, 0.044), M['strip_plastic'])
ps.box(T(px - 0.205, py, 0.046), (0.03, 0.03, 0.006), M['c_red'])
for i in range(6):
    x = px - 0.15 + i * 0.06
    ps.box(T(x, py, 0.0445), (0.04, 0.04, 0.002), M['plug'])
    if i in (0, 1, 3, 4, 5):
        ps.box(T(x, py, 0.062), (0.034, 0.034, 0.034), M['plug'])
        ex = rng.uniform(-1.8, -0.3)
        SPL['c_black'].append((catmull([(x, py, 0.08), (x, py - 0.06, 0.06), (x + 0.05, py - 0.1, FZ + 0.005),
                                         ((x + ex) / 2, py + 0.1, FZ + 0.005), (ex, -0.85, FZ + 0.005), (ex, -0.74, 0.06)], 4), 1.2))
SPL['c_grey'].append((catmull([(px + 0.23, py, 0.022), (px + 0.4, py - 0.05, FZ + 0.005), (px + 0.6, py - 0.3, FZ + 0.005),
                               (px + 1.2, py - 0.4, FZ + 0.005)], 4), 1.6))
ps.done(); zt.done()

for key, spl in SPL.items():
    if not spl: continue
    cu = D.curves.new("NAF_Cables_" + key[2:], 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = 0.0028 if key not in ('c_yellow', 'c_orange') else 0.0017
    cu.bevel_resolution = 2; cu.resolution_u = 6; cu.use_fill_caps = True
    for pts, rad in spl:
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for pt, p in zip(sp.points, pts): pt.co = (*p, 1.0); pt.radius = rad
    cu.materials.append(M[key])
    ob = D.objects.new(cu.name, cu); FC.objects.link(ob); ob.parent = ROOT

print("FUGLY objects:", len(FC.objects))
if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
print("FUGLY OK")
