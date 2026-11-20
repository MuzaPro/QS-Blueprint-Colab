"""chandelier-holder: aluminium support frame + ancillary kit for a dilution-fridge 'chandelier'.

Builds a fresh scene and saves 04_assets/props/ai_models/chandelier-holder.blend.
Run:  blender -b --factory-startup --python build_chandelier_holder.py
Set SAVE = False in globals before exec() to build without saving (preview scripts).

Axis / placement convention
  * Asset origin == the chandelier's origin (Generic Superconducting Quantum Computer.blend,
    collection 'Quantum_Comp'). Place the 'chandelier-holder' collection at the same
    location as the Quantum_Comp instance and they line up.
  * Floor is at z = -1.55 (matches SH_1: floor -1.24, chandelier origin 0.31).
  * Chandelier top plate (r 1.51 m) top face at z = 3.35, it bolts under the deck beams.
  * Front of the rig faces -Y. Control rack on -X, compressor / gas cabinets on +X.
"""
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector as V, Matrix

random.seed(7)
SAVE = globals().get("SAVE", True)
REPO = r"C:\Users\mrgav\Documents\GitHub\QS-Blueprint-Colab"
OUT = REPO + r"\04_assets\props\ai_models\chandelier-holder.blend"
QC_LIB = REPO + r"\04_assets\props\Generic Superconducting Quantum Computer.blend"

FLOOR = -1.55
TOP = 3.35            # chandelier plate top == underside of deck beams
P = 0.1               # base profile size
XH, YH = 2.55, 2.05   # outer corner-post centres
RT = TOP + 0.2        # rail top

# ------------------------------------------------------------------ reset
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
    for d in list(blk):
        blk.remove(d)

# ------------------------------------------------------------------ materials
MATS, MI = [], {}

def lin(h, k=1.0):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c]
    return [min(1.0, x * k) for x in c] + [1.0]

def _reg(name, m, vp):
    m.diffuse_color = vp
    MI[name] = len(MATS)
    MATS.append(m)
    return m

def _bsdf(m):
    m.use_nodes = True
    nt = m.node_tree
    b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if b is None:
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        b = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(b.outputs[0], out.inputs[0])
    return nt, b

def mat(name, col, metal=0.0, rough=0.5, emit=None, es=0.0, aniso=0.0, bump=None, coat=0.0):
    m = bpy.data.materials.new("CHH_" + name)
    nt, b = _bsdf(m)
    b.inputs["Base Color"].default_value = lin(col)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if aniso:
        b.inputs["Anisotropic"].default_value = aniso
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.1
    if emit:
        b.inputs["Emission Color"].default_value = lin(emit)
        b.inputs["Emission Strength"].default_value = es
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = bump[2] if len(bump) > 2 else (1, 1, 1)
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs[0], nz.inputs["Vector"])
        nz.inputs["Scale"].default_value = bump[0]
        nz.inputs["Detail"].default_value = 8
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump[1]
        bp.inputs["Distance"].default_value = 0.002
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return _reg(name, m, lin(col) if not emit else lin(emit))

def glass_mat(name):
    m = bpy.data.materials.new("CHH_" + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs[0].default_value = (0.9, 0.93, 0.94, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.03
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.25
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[3].default_value = 0.08
    mr.inputs[4].default_value = 0.6
    nt.links.new(lw.outputs["Fresnel"], mr.inputs[0])
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    try:
        m.surface_render_method = 'BLENDED'
    except Exception:
        pass
    return _reg(name, m, (0.6, 0.7, 0.75, 0.3))

def screen_mat(name, img, es=2.5):
    m = bpy.data.materials.new("CHH_" + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = es
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.08
    gl.inputs[0].default_value = (0.04, 0.04, 0.04, 1)
    ad = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tx.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], ad.inputs[0])
    nt.links.new(gl.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs[0])
    return _reg(name, m, (0.3, 0.4, 0.6, 1))

# --- screen images (generated, packed) -------------------------------------
def canvas(w, h, bg):
    a = np.zeros((h, w, 4), np.float32)
    a[:, :, :3] = bg
    a[:, :, 3] = 1
    return a

def rect(a, x0, y0, x1, y1, c, fill=True, t=2):
    h, w = a.shape[:2]
    x0, x1 = sorted((int(max(0, min(w, x0))), int(max(0, min(w, x1)))))
    y0, y1 = sorted((int(max(0, min(h, y0))), int(max(0, min(h, y1)))))
    if fill:
        a[y0:y1, x0:x1, :3] = c
    else:
        a[y0:y0 + t, x0:x1, :3] = c; a[y1 - t:y1, x0:x1, :3] = c
        a[y0:y1, x0:x0 + t, :3] = c; a[y0:y1, x1 - t:x1, :3] = c

def ring(a, cx, cy, r, c, t=2):
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    a[(d < r) & (d > r - t), :3] = c

def polyline(a, xs, ys, c, t=2):
    h, w = a.shape[:2]
    for x, y in zip(xs, ys):
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            a[max(0, y - t // 2):y + t // 2 + 1, max(0, x - t // 2):x + t // 2 + 1, :3] = c

def mkimg(name, a):
    h, w = a.shape[:2]
    img = bpy.data.images.new("CHH_" + name, w, h, alpha=False)
    img.pixels.foreach_set(a.ravel())
    img.pack()
    return img

rng = np.random.default_rng(3)

def img_schematic():
    # P&ID-style mimic: white lines on dark slate
    a = canvas(768, 480, (0.015, 0.018, 0.024))
    W, Hh = (0.85, 0.87, 0.9), (0.45, 0.47, 0.5)
    rect(a, 0, 450, 768, 480, (0.12, 0.13, 0.15))
    for i in range(6):
        rect(a, 10 + i * 80, 457, 70 + i * 80, 472, (0.4, 0.42, 0.45))
    nodes = [(rng.integers(60, 700), rng.integers(50, 420)) for _ in range(16)]
    for (x0, y0), (x1, y1) in zip(nodes, nodes[1:] + nodes[:1]):
        polyline(a, np.linspace(x0, x1, 400), np.full(400, y0), W)
        polyline(a, np.full(400, x1), np.linspace(y0, y1, 400), W)
    for x, y in nodes:
        k = rng.integers(0, 3)
        if k == 0:
            rect(a, x - 18, y - 12, x + 18, y + 12, (0.015, 0.018, 0.024)); rect(a, x - 18, y - 12, x + 18, y + 12, W, False)
        elif k == 1:
            rect(a, x - 9, y - 9, x + 9, y + 9, (0.015, 0.018, 0.024)); ring(a, x, y, 10, W)
        else:
            rect(a, x - 6, y - 6, x + 6, y + 6, (0.9, 0.55, 0.12) if rng.random() < 0.5 else (0.25, 0.8, 0.35))
    rect(a, 560, 30, 750, 140, (0.05, 0.06, 0.08))
    rect(a, 560, 30, 750, 140, Hh, False)
    for i in range(5):
        rect(a, 572, 44 + i * 18, 572 + rng.integers(60, 160), 52 + i * 18, Hh)
    return mkimg("screen_schematic", a)

def img_ui():
    # rack console: blue-violet UI with bars and a trace
    a = canvas(640, 400, (0.03, 0.07, 0.30))
    rect(a, 0, 360, 640, 400, (0.08, 0.14, 0.45))
    for i in range(8):
        rect(a, 20, 320 - i * 26, 20 + rng.integers(60, 220), 330 - i * 26, (0.75, 0.8, 0.95))
    rect(a, 300, 90, 620, 330, (0.02, 0.04, 0.18))
    xs = np.linspace(305, 615, 600)
    polyline(a, xs, 210 + 70 * np.sin(xs / 22) * np.exp(-(xs - 300) / 400), (0.95, 0.95, 1.0))
    polyline(a, xs, 150 + 20 * np.sin(xs / 7), (1.0, 0.7, 0.2))
    for i in range(4):
        rect(a, 20 + i * 70, 20, 80 + i * 70, 60, (0.15, 0.25, 0.65))
    return mkimg("screen_ui", a)

def img_scope(seed):
    r = np.random.default_rng(seed)
    a = canvas(320, 200, (0.01, 0.02, 0.015))
    for gx in range(0, 320, 32):
        a[:, gx, :3] = 0.12
    for gy in range(0, 200, 25):
        a[gy, :, :3] = 0.12
    xs = np.linspace(0, 319, 900)
    polyline(a, xs, 130 + 35 * np.sin(xs / r.uniform(8, 20)), (1.0, 0.85, 0.15))
    polyline(a, xs, 60 + 20 * np.sign(np.sin(xs / r.uniform(10, 25))), (0.3, 1.0, 0.45))
    return mkimg("screen_scope%d" % seed, a)

def img_lcd(col):
    a = canvas(128, 48, (0.02, 0.02, 0.02))
    for i in range(3):
        rect(a, 10 + i * 38, 12, 40 + i * 38, 36, col)
    return mkimg("lcd_%d" % int(col[0] * 100), a)

# --- material list ----------------------------------------------------------
mat("alu", "#c9ccd0", metal=1.0, rough=0.32, aniso=0.5, bump=(900, 0.04, (1, 1, 30)))
mat("alu_cast", "#8d9196", metal=1.0, rough=0.5, bump=(400, 0.08))
mat("cap_black", "#151617", rough=0.55)
mat("steel", "#b8bbbd", metal=1.0, rough=0.22)
mat("steel_dark", "#55595d", metal=1.0, rough=0.35)
mat("powder_black", "#18191b", rough=0.55, bump=(600, 0.12))
mat("graphite", "#2c2f33", rough=0.5, bump=(600, 0.08))
mat("vent", "#050505", rough=0.8)
mat("rubber", "#0d0d0e", rough=0.62)
mat("cable_grey", "#6a6d70", rough=0.5)
mat("cable_light", "#b9bcbf", rough=0.45)
mat("cable_navy", "#20356e", rough=0.45)
mat("cable_red", "#8a1712", rough=0.45)
mat("cable_yellow", "#c9a21c", rough=0.45)
mat("cable_orange", "#b4521a", rough=0.45)
mat("copper", "#b87346", metal=1.0, rough=0.28)
mat("braid", "#a7abae", metal=1.0, rough=0.38, bump=(2500, 0.35))
mat("bellows", "#c4c7c9", metal=1.0, rough=0.25)
glass_mat("glass")
mat("led_green", "#2cff5a", emit="#2cff5a", es=12)
mat("led_red", "#ff2a1a", emit="#ff2a1a", es=12)
mat("led_amber", "#ffa21a", emit="#ffa21a", es=10)
mat("led_white", "#ffffff", emit="#e8f0ff", es=6)
screen_mat("screen_schematic", img_schematic(), 2.2)
screen_mat("screen_ui", img_ui(), 2.5)
screen_mat("screen_scope1", img_scope(1), 2.0)
screen_mat("screen_scope2", img_scope(2), 2.0)
screen_mat("lcd_amber", img_lcd((1.0, 0.55, 0.1)), 2.0)
screen_mat("lcd_green", img_lcd((0.4, 1.0, 0.4)), 2.0)
mat("panel_grey", "#9a9ea2", rough=0.45)
mat("panel_light", "#d4d6d4", rough=0.4)
mat("panel_dark", "#36393d", rough=0.45)
mat("label_yellow", "#e8b80c", rough=0.4)
mat("label_white", "#e6e6e2", rough=0.4)
mat("brass", "#c49a45", metal=1.0, rough=0.3)
mat("gold", "#d8ac52", metal=1.0, rough=0.2)
mat("plastic_black", "#121212", rough=0.4)
mat("plastic_white", "#d8d8d4", rough=0.4)
mat("paint_brown", "#5b3a22", rough=0.4, coat=0.5)
mat("cyl_grey", "#8f9497", rough=0.35, coat=0.6)
mat("red_paint", "#b0170f", rough=0.35, coat=0.5)

# ------------------------------------------------------------------ geometry helpers
BMS = {}

def BM(name):
    if name not in BMS:
        bm = bmesh.new()
        bm.loops.layers.uv.verify()
        BMS[name] = bm
    return BMS[name]

def basis(d, up=None):
    z = V(d).normalized()
    if up is None:
        up = V((0, 0, 1)) if abs(z.z) < 0.95 else V((1, 0, 0))
    x = V(up).cross(z).normalized()
    y = z.cross(x)
    return Matrix((x, y, z)).transposed()

def faces_from(bm, cos, faces, mat_, smooth=False, uvs=None):
    vs = [bm.verts.new(c) for c in cos]
    mi = MI[mat_] if isinstance(mat_, str) else mat_
    out = []
    uvl = bm.loops.layers.uv.active
    for fi, f in enumerate(faces):
        try:
            face = bm.faces.new([vs[i] for i in f])
        except ValueError:
            continue
        face.material_index = mi
        face.smooth = smooth if not isinstance(smooth, (list, tuple)) else smooth[fi]
        if uvs is not None and uvl is not None:
            for lp, uv in zip(face.loops, uvs[fi]):
                lp[uvl].uv = uv
        out.append(face)
    return out

_CUBE_F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]

def box(bm, c, s, m, R=None):
    c = V(c)
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    loc = [V((-hx, -hy, -hz)), V((hx, -hy, -hz)), V((hx, hy, -hz)), V((-hx, hy, -hz)),
           V((-hx, -hy, hz)), V((hx, -hy, hz)), V((hx, hy, hz)), V((-hx, hy, hz))]
    if R is not None:
        loc = [R @ p for p in loc]
    return faces_from(bm, [c + p for p in loc], _CUBE_F, m)

def bmm(bm, a, b, m):
    a, b = V(a), V(b)
    return box(bm, (a + b) / 2, [abs(b[i] - a[i]) for i in range(3)], m)

def cyl(bm, p0, p1, r, m, n=16, r1=None, cap=True, smooth=True):
    p0, p1 = V(p0), V(p1)
    d = p1 - p0
    if d.length < 1e-6:
        return
    R = basis(d)
    r1 = r if r1 is None else r1
    cos = []
    for rad, base in ((r, p0), (r1, p1)):
        for k in range(n):
            a = 2 * math.pi * k / n
            cos.append(base + R @ V((rad * math.cos(a), rad * math.sin(a), 0)))
    f = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    sm = [smooth] * n
    if cap:
        f += [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
        sm += [False, False]
    faces_from(bm, cos, f, m, smooth=sm)

def prism(bm, outline, p0, p1, m, up=None, smooth=False):
    p0, p1 = V(p0), V(p1)
    R = basis(p1 - p0, up)
    L = (p1 - p0).length
    n = len(outline)
    cos = [p0 + R @ V((x, y, 0)) for x, y in outline] + [p0 + R @ V((x, y, L)) for x, y in outline]
    f = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    f += [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    faces_from(bm, cos, f, m, smooth=[smooth] * n + [False, False])

def quad(bm, corners, m):
    faces_from(bm, corners, [(0, 1, 2, 3)], m, uvs=[[(0, 0), (1, 0), (1, 1), (0, 1)]])

def tslot(w, h, nw=1, nh=1, sw=0.024, sd=0.014):
    pts = []
    def edge(p0, p1, n, inward):
        L = (p1 - p0).length
        t = (p1 - p0) / L
        pts.append(p0)
        for k in range(n):
            c = (k + 0.5) / n * L
            a, b = p0 + t * (c - sw / 2), p0 + t * (c + sw / 2)
            pts.extend([a, a + inward * sd, b + inward * sd, b])
    hw, hh = w / 2, h / 2
    c = [V((-hw, -hh)), V((hw, -hh)), V((hw, hh)), V((-hw, hh))]
    edge(c[0], c[1], nw, V((0, 1))); edge(c[1], c[2], nh, V((-1, 0)))
    edge(c[2], c[3], nw, V((0, -1))); edge(c[3], c[0], nh, V((1, 0)))
    return [(p.x, p.y) for p in pts]

def profile(bm, p0, p1, w=P, h=P, up=None, m="alu"):
    nw = max(1, round(w / P)); nh = max(1, round(h / P))
    prism(bm, tslot(w, h, nw, nh, sw=0.024 * w / P if w < P else 0.024), p0, p1, m, up)

def frames(pts):
    n = len(pts)
    T = []
    for i in range(n):
        t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        T.append(t.normalized() if t.length > 1e-9 else V((0, 0, 1)))
    up = V((0, 0, 1)) if abs(T[0].z) < 0.9 else V((1, 0, 0))
    nrm = up.cross(T[0]).normalized()
    N = [nrm]
    for i in range(1, n):
        q = T[i - 1].rotation_difference(T[i])
        nrm = q @ nrm
        nrm = (nrm - T[i] * nrm.dot(T[i])).normalized()
        N.append(nrm)
    B = [T[i].cross(N[i]) for i in range(n)]
    return T, N, B

def tube(bm, pts, r, m, n=8, radii=None, cap=True):
    pts = [V(p) for p in pts]
    if len(pts) < 2:
        return
    T, N, B = frames(pts)
    cos = []
    for i, p in enumerate(pts):
        rr = radii[i] if radii else r
        for k in range(n):
            a = 2 * math.pi * k / n
            cos.append(p + (N[i] * math.cos(a) + B[i] * math.sin(a)) * rr)
    f = []
    for i in range(len(pts) - 1):
        for k in range(n):
            k2 = (k + 1) % n
            f.append((i * n + k, i * n + k2, (i + 1) * n + k2, (i + 1) * n + k))
    sm = [True] * len(f)
    if cap:
        f += [tuple(range(n))[::-1], tuple(range((len(pts) - 1) * n, len(pts) * n))]
        sm += [False, False]
    faces_from(bm, cos, f, m, smooth=sm)

def catmull(ctrl, step=0.04):
    Pp = [V(c) for c in ctrl]
    Pp = [Pp[0]] + Pp + [Pp[-1]]
    out = []
    for i in range(1, len(Pp) - 2):
        p0, p1, p2, p3 = Pp[i - 1], Pp[i], Pp[i + 1], Pp[i + 2]
        m = max(2, int((p2 - p1).length / step))
        for j in range(m):
            t = j / m; t2 = t * t; t3 = t2 * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(Pp[-2])
    return out

def densify(pts, step):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, int((b - a).length / step))
        for j in range(1, k + 1):
            out.append(a.lerp(b, j / k))
    return out

def fillet(pts, rad, n=10, step=0.05):
    Pp = [V(p) for p in pts]
    out = [Pp[0]]
    for i in range(1, len(Pp) - 1):
        a, b, c = Pp[i - 1], Pp[i], Pp[i + 1]
        r = min(rad, (b - a).length * 0.45, (c - b).length * 0.45)
        s = b + (a - b).normalized() * r
        e = b + (c - b).normalized() * r
        for j in range(n + 1):
            t = j / n
            out.append((1 - t) ** 2 * s + 2 * (1 - t) * t * b + t * t * e)
    out.append(Pp[-1])
    return densify(out, step)

def cumlen(pts):
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + (b - a).length)
    return L

def at_len(pts, L, s):
    for i in range(1, len(L)):
        if L[i] >= s:
            return i
    return len(L) - 1

def sag(a, b, s, n=24):
    a, b = V(a), V(b)
    return [a.lerp(b, i / n) - V((0, 0, s * 4 * (i / n) * (1 - i / n))) for i in range(n + 1)]

CABLE_MIX = ["cable_grey", "cable_grey", "rubber", "rubber", "cable_navy", "cable_light", "copper"]

def bundle(bm, ctrl, n, R, mats=CABLE_MIX, rmin=0.004, rmax=0.008, ties=0.45, tie_m="plastic_black",
           step=0.03, nseg=6, wob=0.004, path=None):
    C = path if path is not None else catmull(ctrl, step)
    T, N, B = frames(C)
    L = cumlen(C)
    for _ in range(n):
        ang = random.uniform(0, 2 * math.pi)
        rad = R * math.sqrt(random.random()) * 0.85
        tw = random.uniform(-1.2, 1.2)
        rr = random.uniform(rmin, rmax)
        ph = random.uniform(0, 10)
        pts = []
        for i, p in enumerate(C):
            a = ang + tw * L[i]
            w = wob * math.sin(L[i] * 3.3 + ph)
            pts.append(p + N[i] * (math.cos(a) * (rad + w)) + B[i] * (math.sin(a) * (rad + w)))
        tube(bm, pts, rr, random.choice(mats), n=nseg)
    s = ties * 0.5
    while ties and s < L[-1] - 0.05:
        i = at_len(C, L, s)
        cyl(bm, C[i] - T[i] * 0.003, C[i] + T[i] * 0.003, R + 0.002, tie_m, n=12, smooth=True)
        s += ties * random.uniform(0.8, 1.2)
    return C

def bellows(bm, pts, r, m="bellows", pitch=0.018, amp=0.12, n=16):
    D = densify([V(p) for p in pts], pitch / 4)
    L = cumlen(D)
    radii = [r * (1 + amp * math.sin(2 * math.pi * s / pitch)) for s in L]
    tube(bm, D, r, m, n=n, radii=radii)
    # end cuffs
    for i0, i1 in ((0, min(6, len(D) - 1)), (len(D) - 1, max(len(D) - 7, 0))):
        cyl(bm, D[i0], D[i1], r * 1.2, "steel", n=n)

def bolt(bm, c, d, r=0.008, h=0.006, m="steel"):
    c, d = V(c), V(d).normalized()
    cyl(bm, c, c + d * h, r, m, n=6, smooth=False)

def kf_flange(bm, c, d, r, m="steel"):
    c, d = V(c), V(d).normalized()
    cyl(bm, c - d * 0.016, c + d * 0.016, r * 1.45, m, n=24)
    cyl(bm, c - d * 0.006, c + d * 0.006, r * 1.6, "steel_dark", n=24)   # clamp
    s = d.orthogonal().normalized()
    bolt(bm, c + s * r * 1.6, s, 0.006, 0.02, "steel_dark")

# ================================================================== FRAME
fr = BM("CHH_Frame")
for sx in (-1, 1):
    for sy in (-1, 1):
        for k in (0, 1):
            x = sx * (XH - k * P)
            profile(fr, (x, sy * YH, FLOOR + 0.02), (x, sy * YH, RT))
            bmm(fr, (x - P / 2, sy * YH - P / 2, RT), (x + P / 2, sy * YH + P / 2, RT + 0.008), "cap_black")
        # base plate + anchors
        cx = sx * (XH - P / 2)
        bmm(fr, (cx - 0.19, sy * YH - 0.12, FLOOR), (cx + 0.19, sy * YH + 0.12, FLOOR + 0.02), "steel_dark")
        for ax in (-0.15, 0.15):
            for ay in (-0.085, 0.085):
                bolt(fr, (cx + ax, sy * YH + ay, FLOOR + 0.02), (0, 0, 1), 0.014, 0.012)
                cyl(fr, (cx + ax, sy * YH + ay, FLOOR + 0.02), (cx + ax, sy * YH + ay, FLOOR + 0.045), 0.006, "steel", n=8)
        # gusset plates at top joints (outer faces)
        gy = sy * (YH + P / 2 + 0.004)
        bmm(fr, (sx * (XH - 0.5 * P) - 0.17, gy - 0.004, TOP - 0.16), (sx * (XH - 0.5 * P) + 0.17, gy + 0.004, RT), "alu_cast")
        gx = sx * (XH + P / 2 + 0.004)
        bmm(fr, (gx - 0.004, sy * YH - 0.17 * sy - 0.17, TOP - 0.16), (gx + 0.004, sy * YH - 0.17 * sy + 0.17, RT), "alu_cast")
        for bz in (TOP - 0.11, TOP + 0.05, TOP + 0.15):
            for bx in (-0.12, 0.12):
                bolt(fr, (sx * (XH - 0.5 * P) + bx, gy + sy * 0.004, bz), (0, sy, 0))
                bolt(fr, (gx + sx * 0.004, sy * YH - 0.17 * sy + bx, bz), (sx, 0, 0))
        # knee braces
        bl = 0.8
        x_in = sx * (XH - 1.5 * P)
        profile(fr, (x_in + sx * 0.02, sy * YH, TOP - bl - 0.02), (x_in - sx * (bl + 0.02), sy * YH, TOP + 0.02), 0.08, 0.08, up=(0, 1, 0))
        y_in = sy * (YH - 0.5 * P)
        profile(fr, (sx * XH, y_in + sy * 0.02, TOP - bl - 0.02), (sx * XH, y_in - sy * (bl + 0.02), TOP + 0.02), 0.08, 0.08, up=(1, 0, 0))
        for (p, n_) in (((x_in, sy * (YH + 0.045), TOP - bl + 0.02), (0, sy, 0)),
                        ((x_in - sx * bl, sy * (YH + 0.045), TOP - 0.03), (0, sy, 0)),
                        ((sx * (XH + 0.045), y_in, TOP - bl + 0.02), (sx, 0, 0)),
                        ((sx * (XH + 0.045), y_in - sy * bl, TOP - 0.03), (sx, 0, 0))):
            box(fr, p, (0.1, 0.008, 0.1) if n_[1] else (0.008, 0.1, 0.1), "alu_cast")
            bolt(fr, V(p) + V(n_) * 0.004, n_)

# top rails
for sy in (-1, 1):
    profile(fr, (-(XH - 1.5 * P), sy * YH, TOP + 0.1), ((XH - 1.5 * P), sy * YH, TOP + 0.1), P, 2 * P, up=(0, 0, 1))
for sx in (-1, 1):
    profile(fr, (sx * XH, -(YH - P / 2), TOP + 0.1), (sx * XH, (YH - P / 2), TOP + 0.1), P, 2 * P, up=(0, 0, 1))
# deck beams + cross members
DY, DX = 0.8, 0.85
for sy in (-1, 1):
    profile(fr, (-(XH - P / 2), sy * DY, TOP + 0.1), ((XH - P / 2), sy * DY, TOP + 0.1), P, 2 * P, up=(0, 0, 1))
for sx in (-1, 1):
    for y0, y1 in ((-(YH - P / 2), -(DY + P / 2)), (-(DY - P / 2), DY - P / 2), (DY + P / 2, YH - P / 2)):
        profile(fr, (sx * DX, y0, TOP + 0.1), (sx * DX, y1, TOP + 0.1), P, 2 * P, up=(0, 0, 1))
# joining plates on top
joints = [(sx * (XH - P / 2), sy * DY) for sx in (-1, 1) for sy in (-1, 1)]
joints += [(sx * DX, sy * DY) for sx in (-1, 1) for sy in (-1, 1)]
joints += [(sx * DX, sy * (YH - P / 2)) for sx in (-1, 1) for sy in (-1, 1)]
for jx, jy in joints:
    bmm(fr, (jx - 0.1, jy - 0.1, RT), (jx + 0.1, jy + 0.1, RT + 0.008), "alu_cast")
    for bx in (-0.07, 0.07):
        for by in (-0.07, 0.07):
            bolt(fr, (jx + bx, jy + by, RT + 0.008), (0, 0, 1))
# chandelier hanger brackets
for sx in (-1, 1):
    for sy in (-1, 1):
        x = sx * math.sqrt(1.51 ** 2 - DY ** 2) * 0.93
        yi = sy * (DY - P / 2) - sy * 0.006
        bmm(fr, (x - 0.07, yi - 0.006, TOP), (x + 0.07, yi + 0.006, TOP + 0.17), "steel_dark")
        bmm(fr, (x - 0.07, yi - sy * 0.11, TOP), (x + 0.07, yi, TOP + 0.014), "steel_dark")
        for bx in (-0.04, 0.04):
            bolt(fr, (x + bx, yi - sy * 0.06, TOP + 0.014), (0, 0, 1), 0.01, 0.01)
            bolt(fr, (x + bx, yi - sy * 0.006, TOP + 0.12), (0, -sy, 0), 0.01, 0.008)
        y = sy * math.sqrt(1.51 ** 2 - DX ** 2) * 0.93
        xi = sx * (DX - P / 2) - sx * 0.006
        bmm(fr, (xi - 0.006, y - 0.07, TOP), (xi + 0.006, y + 0.07, TOP + 0.17), "steel_dark")
        bmm(fr, (xi - sx * 0.11, y - 0.07, TOP), (xi, y + 0.07, TOP + 0.014), "steel_dark")
# lower rails (sides + back) and a mid back rail
LZ = FLOOR + 0.5
for sx in (-1, 1):
    profile(fr, (sx * XH, -(YH - P / 2), LZ), (sx * XH, YH - P / 2, LZ), up=(0, 0, 1))
profile(fr, (-(XH - 1.5 * P), YH, LZ), (XH - 1.5 * P, YH, LZ), up=(0, 0, 1))
# cable trays (ladder) on left, back and part of front rail
def ladder(bm, a, b, w=0.24, hgt=0.06, rung=0.22):
    a, b = V(a), V(b)
    d = (b - a).normalized()
    s = V((0, 0, 1)).cross(d).normalized()
    L = (b - a).length
    for k in (-1, 1):
        o = s * k * w / 2
        prism(bm, [(-0.003, 0), (0.003, 0), (0.003, hgt), (-0.003, hgt)], a + o, b + o, "steel", up=(0, 0, 1))
        prism(bm, [(-0.012, 0), (0.012, 0), (0.012, 0.004), (-0.012, 0.004)], a + o - s * k * 0.012, b + o - s * k * 0.012, "steel", up=(0, 0, 1))
    t = rung / 2
    while t < L:
        c = a + d * t + V((0, 0, 0.004))
        box(bm, c, (0.02, w, 0.008), "steel", R=Matrix((d, s, (0, 0, 1))).transposed())
        t += rung

ladder(fr, (-XH, -(YH - 0.1), RT + 0.008), (-XH, YH - 0.1, RT + 0.008))
ladder(fr, (-(XH - 0.15), YH, RT + 0.008), (XH - 0.15, YH, RT + 0.008))
ladder(fr, (-(XH - 0.15), -YH, RT + 0.008), (-0.4, -YH, RT + 0.008))
# tray support brackets dropping to rails
for t in np.linspace(-1.8, 1.8, 7):
    bmm(fr, (-XH - 0.13, t - 0.02, RT - 0.06), (-XH - 0.12, t + 0.02, RT + 0.01), "steel_dark")
    bmm(fr, (t - 0.02, YH + 0.12, RT - 0.06), (t + 0.02, YH + 0.13, RT + 0.01), "steel_dark")

# ================================================================== TOP HARDWARE & PLUMBING
hw = BM("CHH_TopHardware")
# pulse tube cold head + rotary valve motor
PT = V((0.38, 0.3, TOP))
cyl(hw, PT, PT + V((0, 0, 0.03)), 0.13, "steel", n=32)
for i in range(8):
    a = i * math.pi / 4
    bolt(hw, PT + V((0.112 * math.cos(a), 0.112 * math.sin(a), 0.03)), (0, 0, 1), 0.009, 0.008)
cyl(hw, PT + V((0, 0, 0.03)), PT + V((0, 0, 0.42)), 0.075, "steel", n=24)
for z in (0.12, 0.2, 0.28):
    cyl(hw, PT + V((0, 0, z)), PT + V((0, 0, z + 0.012)), 0.082, "steel_dark", n=24)
cyl(hw, PT + V((0, 0, 0.42)), PT + V((0, 0, 0.45)), 0.1, "steel", n=24)
bmm(hw, PT + V((-0.11, -0.09, 0.45)), PT + V((0.11, 0.09, 0.62)), "graphite")
cyl(hw, PT + V((0.11, 0, 0.535)), PT + V((0.2, 0, 0.535)), 0.055, "panel_dark", n=20)
cyl(hw, PT + V((0.2, 0, 0.535)), PT + V((0.215, 0, 0.535)), 0.045, "plastic_black", n=20)
for dx in (-0.05, 0.05):
    cyl(hw, PT + V((dx, 0.09, 0.53)), PT + V((dx, 0.13, 0.53)), 0.018, "brass", n=12)   # He connectors
bmm(hw, PT + V((-0.08, -0.095, 0.5)), PT + V((-0.02, -0.09, 0.53)), "label_white")
cyl(hw, PT + V((0.06, -0.09, 0.58)), PT + V((0.06, -0.097, 0.58)), 0.006, "led_green", n=8)

# feedthrough ports on the plate
ports = []
for r_, angs in ((1.2, range(0, 360, 18)), (0.55, (200, 235, 270, 305, 340, 15, 150))):
    for ang in angs:
        x, y = r_ * math.cos(math.radians(ang)), r_ * math.sin(math.radians(ang))
        if abs(abs(y) - DY) < 0.14 or abs(abs(x) - DX) < 0.14:
            continue
        if (V((x, y)) - PT.xy).length < 0.25 or (V((x, y)) - V((-0.35, -0.25))).length < 0.25:
            continue
        ports.append(V((x, y, TOP)))
for p in ports:
    cyl(hw, p, p + V((0, 0, 0.012)), 0.06, "steel", n=20)
    cyl(hw, p, p + V((0, 0, 0.09)), 0.035, "steel", n=16)
    kf_flange(hw, p + V((0, 0, 0.09)), (0, 0, 1), 0.035)
    cyl(hw, p + V((0, 0, 0.106)), p + V((0, 0, 0.15)), 0.03, random.choice(["panel_dark", "gold", "steel_dark"]), n=16)

# main pumping line (rigid) with gate valve + turbo
PL = V((-0.35, -0.25, TOP))
cyl(hw, PL, PL + V((0, 0, 0.03)), 0.12, "steel", n=32)
bmm(hw, PL + V((-0.1, -0.1, 0.22)), PL + V((0.1, 0.1, 0.32)), "steel")
cyl(hw, PL + V((0.1, 0, 0.27)), PL + V((0.32, 0, 0.27)), 0.045, "steel_dark", n=20)
cyl(hw, PL + V((0.32, 0, 0.27)), PL + V((0.34, 0, 0.27)), 0.05, "red_paint", n=20)
pipe_ctrl = [PL + V((0, 0, 0.03)), PL + V((0, 0, 0.7)), V((-0.35, 1.55, TOP + 0.7)), V((2.2, 1.55, TOP + 0.7)), V((2.2, 1.55, TOP + 0.25))]
pipe = fillet(pipe_ctrl, 0.18, step=0.04)
tube(hw, pipe, 0.055, "steel", n=20)
Lp = cumlen(pipe)
for s in np.linspace(0.12, Lp[-1] - 0.05, 7):
    i = at_len(pipe, Lp, s)
    d = pipe[min(i + 1, len(pipe) - 1)] - pipe[max(i - 1, 0)]
    kf_flange(hw, pipe[i], d, 0.055)
TB = V((1.3, 1.55, TOP + 0.7))
cyl(hw, TB, TB + V((0, 0, 0.12)), 0.06, "steel", n=24)
kf_flange(hw, TB + V((0, 0, 0.12)), (0, 0, 1), 0.06)
cyl(hw, TB + V((0, 0, 0.13)), TB + V((0, 0, 0.36)), 0.1, "steel", n=32)
for z in np.linspace(0.16, 0.33, 7):
    cyl(hw, TB + V((0, 0, z)), TB + V((0, 0, z + 0.008)), 0.112, "steel_dark", n=32)
cyl(hw, TB + V((0, 0, 0.36)), TB + V((0, 0, 0.4)), 0.08, "panel_dark", n=24)
bmm(hw, TB + V((0.13, -0.08, 0.14)), TB + V((0.33, 0.08, 0.3)), "panel_dark")
cyl(hw, TB + V((0.2, -0.08, 0.26)), TB + V((0.2, -0.086, 0.26)), 0.006, "led_green", n=8)
cyl(hw, TB + V((0.24, -0.08, 0.26)), TB + V((0.24, -0.086, 0.26)), 0.006, "led_amber", n=8)
# bellows run down the back-right corner into the gas handling cabinet
bel = catmull([V((2.2, 1.55, TOP + 0.25)), V((2.2, 1.55, TOP - 0.3)), V((2.22, 1.5, 1.2)),
               V((2.26, 1.45, -0.2)), V((2.45, 1.45, -0.42)), V((2.78, 1.45, -0.45))], 0.05)
bellows(hw, bel, 0.055, pitch=0.022, amp=0.13, n=20)
kf_flange(hw, V((2.2, 1.55, TOP + 0.25)), (0, 0, 1), 0.055)
for zc in (2.6, 1.4, 0.3):
    i = min(range(len(bel)), key=lambda j: abs(bel[j].z - zc))
    p = bel[i]
    cyl(hw, p - V((0, 0, 0.015)), p + V((0, 0, 0.015)), 0.072, "steel_dark", n=20)       # hose clamp
    bmm(hw, V((p.x + 0.06, p.y - 0.02, p.z - 0.015)), V((2.45, p.y + 0.02, p.z + 0.015)), "steel_dark")  # strap to post
# secondary small lines on the deck
for start, ctrl in (
        (V((-0.1, 0.45, TOP)), [V((-0.1, 0.45, TOP + 0.4)), V((-0.6, 0.6, TOP + 0.45)), V((-1.4, 1.3, RT + 0.1)), V((-2.2, 1.95, RT + 0.06))]),
        (V((0.62, -0.42, TOP)), [V((0.62, -0.42, TOP + 0.3)), V((1.1, -0.5, RT + 0.12)), V((2.0, -0.6, RT + 0.1)), V((2.55, -0.6, RT + 0.05))])):
    cyl(hw, start, start + V((0, 0, 0.02)), 0.06, "steel", n=20)
    pth = fillet([start] + ctrl, 0.12, step=0.03)
    tube(hw, pth, 0.018, "steel", n=12)
    kf_flange(hw, start + V((0, 0, 0.12)), (0, 0, 1), 0.018)
# junction boxes on the deck beams
for jx, jy, sz in ((-1.6, DY, (0.32, 0.18, 0.16)), (1.7, -DY, (0.28, 0.16, 0.14)), (-0.3, -(YH - 0.05), (0.36, 0.14, 0.18))):
    c = V((jx, jy, RT + sz[2] / 2))
    box(hw, c, sz, "panel_grey")
    box(hw, c + V((0, 0, sz[2] / 2 + 0.004)), (sz[0] + 0.01, sz[1] + 0.01, 0.008), "panel_grey")
    for k in range(4):
        cyl(hw, c + V((-sz[0] / 2 + 0.05 + k * 0.07, -sz[1] / 2, -0.02)), c + V((-sz[0] / 2 + 0.05 + k * 0.07, -sz[1] / 2 - 0.025, -0.02)), 0.012, "plastic_black", n=12)
# small electronics shelf on back-left post
SH = V((-2.15, YH - 0.12, FLOOR + 1.9))
bmm(hw, SH + V((-0.3, -0.18, -0.01)), SH + V((0.3, 0.07, 0)), "steel_dark")
for dx in (-0.25, 0.25):
    prism(hw, [(0, 0), (0.2, 0), (0, 0.2)], SH + V((dx - 0.003, 0.07, -0.01)), SH + V((dx + 0.003, 0.07, -0.01)), "steel_dark", up=(0, 0, 1))
box(hw, SH + V((-0.12, -0.05, 0.065)), (0.3, 0.24, 0.13), "panel_light")
quad(hw, [SH + V((-0.24, -0.171, 0.04)), SH + V((-0.1, -0.171, 0.04)), SH + V((-0.1, -0.171, 0.1)), SH + V((-0.24, -0.171, 0.1))], "lcd_green")
for k in range(3):
    cyl(hw, SH + V((-0.05 + k * 0.035, -0.17, 0.06)), SH + V((-0.05 + k * 0.035, -0.185, 0.06)), 0.01, "plastic_black", n=12)
box(hw, SH + V((0.17, -0.06, 0.05)), (0.22, 0.2, 0.1), "panel_dark")
quad(hw, [SH + V((0.09, -0.161, 0.04)), SH + V((0.19, -0.161, 0.04)), SH + V((0.19, -0.161, 0.075)), SH + V((0.09, -0.161, 0.075))], "lcd_amber")
# E-stop + junction box + warning labels on front posts
bmm(hw, (-XH - 0.07, -YH - 0.13, 0.5), (-XH + 0.07, -YH - 0.05, 0.72), "panel_grey")
for k in range(3):
    cyl(hw, (-XH - 0.04 + k * 0.04, -YH - 0.09, 0.5), (-XH - 0.04 + k * 0.04, -YH - 0.09, 0.47), 0.01, "plastic_black", n=10)
box(hw, (-(XH - P), -YH - 0.09, 1.0), (0.09, 0.08, 0.09), "label_yellow")
cyl(hw, (-(XH - P), -YH - 0.13, 1.0), (-(XH - P), -YH - 0.15, 1.0), 0.028, "red_paint", n=20)
cyl(hw, (-(XH - P), -YH - 0.15, 1.0), (-(XH - P), -YH - 0.165, 1.0), 0.034, "red_paint", n=20)
for sx in (-1, 1):
    for z in (1.6, TOP - 0.3):
        bmm(hw, (sx * XH - 0.035, -YH - 0.053, z), (sx * XH + 0.035, -YH - 0.051, z + 0.06), "label_yellow")
        bmm(hw, (sx * XH - 0.02, -YH - 0.0535, z + 0.012), (sx * XH + 0.02, -YH - 0.0525, z + 0.045), "plastic_black")

# ================================================================== CABLES
cb = BM("CHH_Cables")
RX, RY, RW, RD, RH = -3.35, -1.4, 0.8, 1.0, 2.25
RZ1 = FLOOR + RH
# thick conduits rack -> frame top -> deck feedthroughs
for k, (r_, m_) in enumerate(((0.034, "rubber"), (0.028, "rubber"), (0.022, "cable_grey"), (0.018, "rubber"))):
    o = (k - 1.5) * 0.075
    ctrl = [V((RX + 0.1 + o, RY + 0.25, RZ1)), V((RX + 0.1 + o, RY + 0.25, RZ1 + 0.5)),
            V((RX + 0.35 + o * 0.5, RY + 0.1, 2.5 + k * 0.05)), V((-XH - 0.05, -1.0 + o, RT + 0.25)),
            V((-XH, -0.6 + o, RT + 0.06 + r_)), V((-XH, 0.05 + o, RT + 0.06 + r_)),
            V((-1.9, 0.1 + o, RT + 0.12)), V((-1.0, 0.0 + o, RT + 0.1)), V((-0.7, -0.1 + o * 0.5, TOP + 0.35)),
            V((-0.55 + o * 0.3, -0.35, TOP + 0.12))]
    tube(cb, catmull(ctrl, 0.04), r_, m_, n=14)
# braided helium lines GHS -> pulse-tube motor
for k in range(2):
    o = k * 0.07
    ctrl = [V((3.0 + o, 1.15, FLOOR + 2.0)), V((3.0 + o, 1.15, FLOOR + 2.4)), V((2.82 + o, 1.08 - o, 2.6)),
            V((XH + 0.05, 1.0 - o, RT + 0.07)), V((1.8, 0.85 - o, RT + 0.14)), V((1.0, 0.55 - o, RT + 0.12)),
            V((PT.x - 0.05 + 0.1 * k, PT.y + 0.35, TOP + 0.6)), V((PT.x - 0.05 + 0.1 * k, PT.y + 0.13, TOP + 0.53))]
    C = catmull(ctrl, 0.03)
    tube(cb, C, 0.02, "braid", n=14)
    for i in (0, len(C) - 1):
        d = (C[min(i + 1, len(C) - 1)] - C[max(i - 1, 0)]).normalized()
        cyl(cb, C[i] - d * 0.03, C[i] + d * 0.03, 0.026, "brass", n=6, smooth=False)
# compressor -> motor power / control lines
for k, m_ in enumerate(("rubber", "cable_grey")):
    ctrl = [V((3.1 + k * 0.1, 0.75, -0.05)), V((3.1 + k * 0.1, 0.8, 0.6)), V((2.75, 0.9, 2.2)),
            V((XH + 0.05, 0.7 + k * 0.05, RT + 0.05)), V((1.5, 0.6, RT + 0.2)), V((PT.x + 0.2, PT.y, TOP + 0.535))]
    tube(cb, catmull(ctrl, 0.04), 0.011, m_, n=10)

# coax / loom bundles from feedthroughs into the trays
for p in ports:
    top = p + V((0, 0, 0.15))
    if p.x < -0.3:
        tgt = V((-XH, p.y * 0.8 + random.uniform(-0.2, 0.2), RT + 0.05)); run = V((0, -0.6 if tgt.y > 0 else 0.6, 0))
    elif p.y > 0.2:
        tgt = V((p.x * 0.8, YH, RT + 0.05)); run = V((-0.6 if tgt.x > -0.5 else 0.6, 0, 0))
    else:
        tgt = V((XH, p.y * 0.7 - 0.3, RT + 0.05)); run = V((0, -0.5, 0))
    mid = top.lerp(tgt, 0.45); mid.z = RT + 0.16 + random.uniform(0, 0.06)
    n = random.randint(5, 10)
    mats = random.choice([["copper", "copper", "cable_light"], ["cable_navy", "cable_light", "copper"], ["rubber", "cable_grey", "cable_light"]])
    bundle(cb, [top - V((0, 0, 0.02)), top + V((0, 0, 0.12)), mid, tgt, tgt + run], n, 0.02 + n * 0.0018, mats=mats,
           rmin=0.0025, rmax=0.005, ties=0.6, nseg=5)
# long bundles laid in the trays
bundle(cb, [V((-XH, -1.95, RT + 0.05)), V((-XH + 0.02, -0.5, RT + 0.05)), V((-XH - 0.02, 0.7, RT + 0.05)), V((-XH + 0.03, 1.9, RT + 0.06)), V((-2.3, YH, RT + 0.06))],
       16, 0.07, ties=0.7, nseg=6, wob=0.01)
bundle(cb, [V((-2.3, YH, RT + 0.06)), V((-0.5, YH + 0.02, RT + 0.05)), V((1.0, YH - 0.02, RT + 0.05)), V((2.4, YH, RT + 0.05))],
       12, 0.065, ties=0.7, nseg=6, wob=0.01)
bundle(cb, [V((-0.45, -YH, RT + 0.05)), V((-1.2, -YH + 0.02, RT + 0.05)), V((-2.3, -YH, RT + 0.05)), V((-XH, -1.8, RT + 0.06))],
       8, 0.05, ties=0.7, nseg=6, wob=0.01)

def pclips(bm, pts, every=0.5, post_xy=None, R=0.03):
    L = cumlen(pts)
    s = 0.3
    while s < L[-1] - 0.3:
        i = at_len(pts, L, s)
        p = pts[i]
        cyl(bm, p - V((0, 0, 0.012)), p + V((0, 0, 0.012)), R + 0.006, "steel_dark", n=14)
        if post_xy is not None:
            q = V((post_xy[0], post_xy[1], p.z))
            d = (q - p)
            if d.length > 0.01:
                box(bm, p.lerp(q, 0.5), (0.02, 0.02, 0.024), "steel_dark", R=basis(d))
        s += every

# drops down the posts to the rack / gas cabinet
C = bundle(cb, [V((-2.3, YH, RT + 0.06)), V((-2.32, YH - 0.12, RT - 0.2)), V((-2.33, YH - 0.12, 1.5)), V((-2.33, YH - 0.12, FLOOR + 0.3)),
               V((-2.4, YH - 0.25, FLOOR + 0.05)), V((-2.9, 1.0, FLOOR + 0.05)), V((-3.2, RY + 0.55, FLOOR + 0.05)), V((-3.25, RY + 0.48, FLOOR + 0.3))],
           12, 0.045, ties=0.7, nseg=6)
pclips(cb, [p for p in C if p.z > FLOOR + 0.4 and p.z < RT - 0.3], 0.55, (-2.45, YH), 0.045)
C = bundle(cb, [V((-XH, -1.8, RT + 0.06)), V((-XH - 0.12, -1.95, RT - 0.2)), V((-XH - 0.13, -2.0, 1.6)), V((-2.75, -1.6, 1.0)),
               V((RX + 0.25, RY + 0.2, RZ1 + 0.25)), V((RX + 0.25, RY + 0.25, RZ1 - 0.02))], 9, 0.04, ties=0.7, nseg=6)
C = bundle(cb, [V((2.4, YH, RT + 0.06)), V((2.35, YH - 0.12, RT - 0.2)), V((2.36, YH - 0.13, 1.0)), V((2.4, 1.85, 0.7)),
               V((2.9, 1.3, FLOOR + 2.15)), V((3.15, 1.3, FLOOR + 2.0))], 9, 0.04, ties=0.7, nseg=6)
pclips(cb, [p for p in C if p.z > 1.0 and p.z < RT - 0.3], 0.55, (2.45, YH), 0.04)
# loose loops hanging off the left tray (excess cable)
for k in range(5):
    y0 = -1.4 + k * 0.55
    a = V((-XH - 0.12, y0, RT + 0.04))
    b = V((-XH - 0.12, y0 + 0.35 + random.uniform(0, 0.2), RT + 0.04))
    depth = random.uniform(0.5, 1.3)
    out = random.uniform(0.04, 0.1)
    pts = [p + V((-out * math.sin(i / 30 * math.pi), 0, 0)) for i, p in enumerate(sag(a, b, depth, 30))]
    tube(cb, pts, random.uniform(0.004, 0.007), random.choice(["cable_yellow", "cable_grey", "cable_navy", "cable_orange"]), n=6)
# loops hanging off the back tray behind the frame
for k in range(4):
    x0 = -1.8 + k * 1.1
    a = V((x0, YH + 0.13, RT + 0.04)); b = V((x0 + 0.5, YH + 0.13, RT + 0.04))
    pts = sag(a, b, random.uniform(0.6, 1.4), 20)
    pts = [p + V((0, 0.05 * math.sin(i / 3), 0)) for i, p in enumerate(pts)]
    tube(cb, catmull(pts, 0.04), random.uniform(0.004, 0.008), random.choice(["cable_grey", "rubber", "cable_yellow"]), n=6)
# yellow single-mode fibre arcing from the rack to the frame
tube(cb, catmull([V((RX - 0.15, RY + 0.3, RZ1)), V((RX - 0.15, RY + 0.3, RZ1 + 0.3)), V((-3.0, -1.3, 2.0)),
                  V((-XH - 0.06, -1.6, RT + 0.08)), V((-XH, -1.2, RT + 0.07))], 0.03), 0.003, "cable_yellow", n=6)
# floor runs behind the frame: rack -> gas handling
for k in range(5):
    o = k * 0.05
    pts = [V((RX + 0.2, RY + 0.5, FLOOR + 0.2)), V((RX + 0.25 + o, RY + 0.6, FLOOR + 0.012)), V((-2.9 + o, 2.35 + o, FLOOR + 0.012)),
           V((0.0, 2.45 + o + random.uniform(-0.05, 0.05), FLOOR + 0.012)), V((2.9 - o, 2.35 + o, FLOOR + 0.012)), V((3.1, 1.75, FLOOR + 0.012)), V((3.1, 1.72, FLOOR + 0.25))]
    r_ = random.uniform(0.008, 0.014)
    pts = [p if i in (0, len(pts) - 1) else p + V((0, 0, r_ - 0.012)) for i, p in enumerate(pts)]
    tube(cb, catmull(pts, 0.05), r_, random.choice(["rubber", "cable_grey", "cable_navy"]), n=8)
prism(cb, [(-0.16, 0), (0.16, 0), (0.08, 0.04), (-0.08, 0.04)], V((0.0, 2.15, FLOOR)), V((0.0, 2.85, FLOOR)), "label_yellow", up=(0, 0, 1))
for k in range(4):
    bmm(cb, (-0.05, 2.2 + k * 0.17, FLOOR + 0.0405), (0.05, 2.28 + k * 0.17, FLOOR + 0.0415), "plastic_black")

# ================================================================== RACK
rk = BM("CHH_Rack")
x0, x1 = RX - RW / 2, RX + RW / 2
y0, y1 = RY - RD / 2, RY + RD / 2
z0, z1 = FLOOR, RZ1
bmm(rk, (x0 + 0.03, y0 + 0.04, z0 + 0.015), (x1 - 0.03, y1 - 0.04, z0 + 0.09), "graphite")
for fx in (x0 + 0.07, x1 - 0.07):
    for fy in (y0 + 0.08, y1 - 0.08):
        cyl(rk, (fx, fy, z0), (fx, fy, z0 + 0.015), 0.025, "plastic_black", n=12)
for cx in (x0 + 0.02, x1 - 0.02):
    for cy in (y0 + 0.03, y1 - 0.02):
        bmm(rk, (cx - 0.02, cy - 0.02, z0 + 0.09), (cx + 0.02, cy + 0.02, z1), "powder_black")
for sx_, xx in ((-1, x0), (1, x1)):
    bmm(rk, (xx - 0.008, y0 + 0.05, z0 + 0.09), (xx + 0.008, y1, z1 - 0.03), "powder_black")
bmm(rk, (x0, y1 - 0.016, z0 + 0.09), (x1, y1, z1 - 0.03), "powder_black")
bmm(rk, (x0, y0 + 0.02, z1 - 0.035), (x1, y1, z1), "powder_black")
for fy in (y0 + 0.35, y0 + 0.65):
    cyl(rk, (RX - 0.15, fy, z1), (RX - 0.15, fy, z1 + 0.003), 0.07, "vent", n=24)
    cyl(rk, (RX - 0.15, fy, z1), (RX - 0.15, fy, z1 + 0.006), 0.018, "plastic_black", n=12)
bmm(rk, (RX + 0.0, y1 - 0.4, z1), (RX + 0.33, y1 - 0.1, z1 + 0.004), "rubber")
# side vents (towards the frame)
for col in range(3):
    for row in range(22):
        zz = z1 - 0.25 - row * 0.035
        yy = y0 + 0.2 + col * 0.25
        bmm(rk, (x1 + 0.008, yy, zz), (x1 + 0.0095, yy + 0.2, zz + 0.012), "vent")
        bmm(rk, (x0 - 0.0095, yy, zz), (x0 - 0.008, yy + 0.2, zz + 0.012), "vent")
# glass door
dy = y0
for a, b in (((x0, dy, z0 + 0.09), (x0 + 0.05, dy + 0.025, z1)), ((x1 - 0.05, dy, z0 + 0.09), (x1, dy + 0.025, z1)),
             ((x0, dy, z1 - 0.06), (x1, dy + 0.025, z1)), ((x0, dy, z0 + 0.09), (x1, dy + 0.025, z0 + 0.16))):
    bmm(rk, a, b, "powder_black")
bmm(rk, (x0 + 0.05, dy + 0.01, z0 + 0.16), (x1 - 0.05, dy + 0.014, z1 - 0.06), "glass")
bmm(rk, (x1 - 0.04, dy - 0.03, (z0 + z1) / 2 - 0.15), (x1 - 0.02, dy, (z0 + z1) / 2 + 0.15), "steel_dark")
for hz in (z0 + 0.3, z1 - 0.3):
    cyl(rk, (x0 - 0.005, dy + 0.005, hz - 0.04), (x0 - 0.005, dy + 0.005, hz + 0.04), 0.01, "steel_dark", n=10)
# 19" rails
FY = y0 + 0.065
for rxx in (RX - 0.235, RX + 0.235):
    bmm(rk, (rxx - 0.012, FY, z0 + 0.12), (rxx + 0.012, FY + 0.03, z1 - 0.06), "steel_dark")
# units
U = 0.04445
PW = 0.483
def panel(zb, nu, m):
    zt = zb + nu * U - 0.001
    bmm(rk, (RX - PW / 2, FY - 0.006, zb), (RX + PW / 2, FY, zt), m)
    bmm(rk, (RX - 0.215, FY, zb + 0.002), (RX + 0.215, FY + 0.45, zt - 0.002), "graphite")
    for sx_ in (-1, 1):
        for zz in ((zb + zt) / 2,) if nu == 1 else (zb + 0.012, zt - 0.012):
            cyl(rk, (RX + sx_ * 0.233, FY - 0.006, zz), (RX + sx_ * 0.233, FY - 0.0105, zz), 0.0045, "steel", n=8)
    return zt

def ports_row(zc, n, x_start, pitch=0.016, plug=0.4):
    out = []
    for k in range(n):
        px = x_start + k * pitch
        bmm(rk, (px - 0.006, FY - 0.0075, zc - 0.006), (px + 0.006, FY - 0.006, zc + 0.006), "vent")
        if random.random() < plug:
            out.append(V((px, FY - 0.008, zc)))
            bmm(rk, (px - 0.0055, FY - 0.022, zc - 0.0055), (px + 0.0055, FY - 0.0075, zc + 0.0055), "plastic_white" if random.random() < 0.3 else "plastic_black")
    return out

patch_pts = []
def unit(kind, zb):
    if kind == "blank1":
        return panel(zb, 1, "powder_black")
    if kind == "blank2":
        return panel(zb, 2, "powder_black")
    if kind == "patch":
        zt = panel(zb, 1, "powder_black")
        for g in range(2):
            patch_pts.extend(ports_row(zb + U / 2, 12, RX - 0.2 + g * 0.21, plug=0.55))
        return zt
    if kind == "switch":
        zt = panel(zb, 1, "panel_dark")
        patch_pts.extend(ports_row(zb + U / 2 - 0.004, 24, RX - 0.19, pitch=0.0155, plug=0.5))
        for k in range(24):
            if random.random() < 0.7:
                bmm(rk, (RX - 0.193 + k * 0.0155, FY - 0.0072, zb + U - 0.01), (RX - 0.188 + k * 0.0155, FY - 0.0062, zb + U - 0.007),
                    random.choice(["led_green", "led_green", "led_amber"]))
        return zt
    if kind == "display":
        zt = panel(zb, 6, "panel_dark")
        quad(rk, [V((RX - 0.17, FY - 0.0065, zb + 0.03)), V((RX + 0.17, FY - 0.0065, zb + 0.03)),
                  V((RX + 0.17, FY - 0.0065, zt - 0.03)), V((RX - 0.17, FY - 0.0065, zt - 0.03))], "screen_ui")
        bmm(rk, (RX + 0.19, FY - 0.0075, zb + 0.03), (RX + 0.205, FY - 0.0065, zb + 0.04), "led_green")
        return zt
    if kind == "scopes":
        zt = panel(zb, 4, "powder_black")
        for k, sm in ((0, "screen_scope1"), (1, "screen_scope2")):
            xc = RX - 0.11 + k * 0.225
            bmm(rk, (xc - 0.105, FY - 0.05, zb + 0.008), (xc + 0.105, FY - 0.006, zt - 0.01), "panel_light")
            quad(rk, [V((xc - 0.095, FY - 0.0505, zb + 0.06)), V((xc + 0.015, FY - 0.0505, zb + 0.06)),
                      V((xc + 0.015, FY - 0.0505, zt - 0.025)), V((xc - 0.095, FY - 0.0505, zt - 0.025))], sm)
            for kx in range(3):
                for kz in range(3):
                    cyl(rk, (xc + 0.035 + kx * 0.025, FY - 0.05, zb + 0.05 + kz * 0.035), (xc + 0.035 + kx * 0.025, FY - 0.062, zb + 0.05 + kz * 0.035),
                        0.007 if kz else 0.009, "plastic_black", n=12)
            for kx in range(4):
                cyl(rk, (xc - 0.085 + kx * 0.03, FY - 0.05, zb + 0.03), (xc - 0.085 + kx * 0.03, FY - 0.064, zb + 0.03), 0.006, "steel", n=10)
            bmm(rk, (xc - 0.095, FY - 0.0505, zt - 0.02), (xc - 0.05, FY - 0.05, zt - 0.015), "label_white")
        return zt
    if kind == "awg":
        zt = panel(zb, 2, "panel_grey")
        quad(rk, [V((RX - 0.2, FY - 0.0065, zb + 0.03)), V((RX - 0.11, FY - 0.0065, zb + 0.03)),
                  V((RX - 0.11, FY - 0.0065, zb + 0.065)), V((RX - 0.11 - 0.09, FY - 0.0065, zb + 0.065))], "lcd_amber")
        for k in range(8):
            px = RX - 0.06 + k * 0.032
            cyl(rk, (px, FY - 0.006, zb + 0.045), (px, FY - 0.02, zb + 0.045), 0.006, "steel", n=10)
            cyl(rk, (px, FY - 0.006, zb + 0.045), (px, FY - 0.01, zb + 0.045), 0.009, "steel_dark", n=10)
            if random.random() < 0.6:
                patch_pts.append(V((px, FY - 0.02, zb + 0.045)))
        return zt
    if kind == "leds":
        zt = panel(zb, 1, "powder_black")
        for k in range(6):
            px = RX - 0.15 + k * 0.06
            cyl(rk, (px, FY - 0.006, zb + U / 2), (px, FY - 0.011, zb + U / 2), 0.0045, "led_red", n=10)
            bmm(rk, (px + 0.01, FY - 0.0065, zb + U / 2 - 0.004), (px + 0.03, FY - 0.006, zb + U / 2 + 0.004), "label_white")
        return zt
    if kind == "server":
        zt = panel(zb, 2, "panel_dark")
        for k in range(12):
            px = RX - 0.2 + k * 0.032
            bmm(rk, (px, FY - 0.012, zb + 0.008), (px + 0.028, FY - 0.006, zt - 0.008), "graphite")
            bmm(rk, (px + 0.004, FY - 0.0125, zt - 0.016), (px + 0.008, FY - 0.0118, zt - 0.012), random.choice(["led_green", "led_green", "led_amber"]))
        return zt
    if kind == "psu":
        zt = panel(zb, 2, "panel_grey")
        quad(rk, [V((RX - 0.18, FY - 0.0065, zb + 0.035)), V((RX - 0.08, FY - 0.0065, zb + 0.035)),
                  V((RX - 0.08, FY - 0.0065, zb + 0.07)), V((RX - 0.18, FY - 0.0065, zb + 0.07))], "lcd_green")
        for k, m_ in enumerate(("red_paint", "plastic_black", "red_paint", "plastic_black")):
            cyl(rk, (RX + 0.02 + k * 0.035, FY - 0.006, zb + 0.04), (RX + 0.02 + k * 0.035, FY - 0.02, zb + 0.04), 0.007, m_, n=10)
        bmm(rk, (RX + 0.17, FY - 0.018, zb + 0.025), (RX + 0.2, FY - 0.006, zb + 0.06), "plastic_black")
        cyl(rk, (RX - 0.04, FY - 0.006, zb + 0.06), (RX - 0.04, FY - 0.016, zb + 0.06), 0.012, "plastic_black", n=14)
        return zt
    if kind == "cablemgr":
        zt = panel(zb, 1, "powder_black")
        bmm(rk, (RX - 0.2, FY - 0.0075, zb + 0.012), (RX + 0.2, FY - 0.006, zt - 0.012), "rubber")
        return zt

layout = ["patch", "switch", "patch", "cablemgr", "switch", "blank1", "display", "blank1", "scopes", "blank2",
          "awg", "blank1", "leds", "blank2", "awg", "switch", "blank1", "server", "blank2", "server", "blank1",
          "psu", "psu", "blank2"]
zt = z1 - 0.075
for kind in layout:
    nu = {"display": 6, "scopes": 4, "awg": 2, "server": 2, "psu": 2, "blank2": 2}.get(kind, 1)
    zb = zt - nu * U
    if zb < z0 + 0.15:
        break
    unit(kind, zb)
    zt = zb - (U if random.random() < 0.15 else 0)
# patch cables inside the door, draped to the left/right cable channels
for p in patch_pts:
    side = -1 if p.x < RX else 1
    xs = RX + side * random.uniform(0.18, 0.225)
    drop = random.uniform(0.04, 0.16)
    pts = [p, p + V((0, -0.012, 0)), V(((p.x + xs) / 2, FY - 0.03, p.z - drop * 0.6)), V((xs, FY - 0.028, p.z - drop)), V((xs + side * 0.02, FY + 0.03, p.z - drop - 0.05))]
    tube(rk, catmull(pts, 0.012), 0.0028, random.choice(["cable_navy", "cable_yellow", "cable_grey", "cable_light", "cable_red"]), n=5)
# vertical looms in the side channels (seen through the glass)
for sx_ in (-1, 1):
    bundle(rk, [V((RX + sx_ * 0.27, FY + 0.02, z0 + 0.15)), V((RX + sx_ * 0.275, FY + 0.03, (z0 + z1) / 2)), V((RX + sx_ * 0.27, FY + 0.05, z1 - 0.04))],
           10, 0.025, mats=["cable_navy", "cable_grey", "cable_yellow", "rubber"], rmin=0.0025, rmax=0.004, ties=0.25, nseg=5)

# ================================================================== CABINETS + MONITOR
cab = BM("CHH_Cabinets")
CX, CY, CW, CD, CH = 3.45, 0.35, 1.25, 0.95, 1.5
cx0, cx1, cy0, cy1, cz0, cz1 = CX - CW / 2, CX + CW / 2, CY - CD / 2, CY + CD / 2, FLOOR, FLOOR + CH
bmm(cab, (cx0 + 0.03, cy0 + 0.06, cz0), (cx1 - 0.03, cy1 - 0.03, cz0 + 0.06), "graphite")
bmm(cab, (cx0, cy0 + 0.03, cz0 + 0.06), (cx1, cy1, cz1), "powder_black")
for a, b in (((cx0, cy0, cz0 + 0.06), (cx0 + 0.05, cy0 + 0.03, cz1)), ((cx1 - 0.05, cy0, cz0 + 0.06), (cx1, cy0 + 0.03, cz1)),
             ((cx0, cy0, cz1 - 0.06), (cx1, cy0 + 0.03, cz1)), ((cx0, cy0, cz0 + 0.06), (cx1, cy0 + 0.03, cz0 + 0.12)),
             ((CX - 0.02, cy0, cz0 + 0.06), (CX + 0.02, cy0 + 0.03, cz1))):
    bmm(cab, a, b, "powder_black")
bmm(cab, (cx0 + 0.05, cy0 + 0.028, cz0 + 0.12), (cx1 - 0.05, cy0 + 0.03, cz1 - 0.06), "vent")
nsl = 15
for k in range(nsl):
    zc = cz0 + 0.16 + k * (CH - 0.26) / (nsl - 1)
    Rr = Matrix.Rotation(math.radians(-38), 3, 'X')
    for xa, xb in ((cx0 + 0.05, CX - 0.02), (CX + 0.02, cx1 - 0.05)):
        box(cab, ((xa + xb) / 2, cy0 + 0.018, zc), (xb - xa, 0.006, 0.075), "powder_black", R=Rr)
for hx in (CX - 0.06, CX + 0.06):
    bmm(cab, (hx - 0.01, cy0 - 0.03, cz0 + 0.75), (hx + 0.01, cy0, cz0 + 0.95), "steel_dark")
    cyl(cab, (hx, cy0, cz0 + 1.05), (hx, cy0 - 0.008, cz0 + 1.05), 0.012, "steel", n=12)
bmm(cab, (cx0 + 0.08, cy0 - 0.002, cz1 - 0.05), (cx0 + 0.26, cy0, cz1 - 0.015), "steel")
for k, m_ in enumerate(("led_green", "led_green", "led_amber")):
    cyl(cab, (cx1 - 0.16 + k * 0.035, cy0, cz1 - 0.035), (cx1 - 0.16 + k * 0.035, cy0 - 0.005, cz1 - 0.035), 0.006, m_, n=10)
for k in range(9):           # side louvres facing the frame
    zc = cz0 + 0.3 + k * 0.1
    bmm(cab, (cx0 - 0.004, cy0 + 0.2, zc), (cx0, cy1 - 0.2, zc + 0.05), "vent")
    box(cab, (cx0 - 0.008, CY + 0.0, zc + 0.03), (0.006, CD - 0.42, 0.06), "powder_black", R=Matrix.Rotation(math.radians(30), 3, 'Y'))
for k in range(3):           # rear fittings
    cyl(cab, (CX - 0.3 + k * 0.2, cy1, cz1 - 0.3), (CX - 0.3 + k * 0.2, cy1 + 0.06, cz1 - 0.3), 0.025, "brass", n=6, smooth=False)
# monitor on top, slightly turned toward the camera
MW = Matrix.Translation(V((CX - 0.12, CY - 0.12, cz1))) @ Matrix.Rotation(math.radians(-14), 4, 'Z')
R3 = MW.to_3x3()
def lbox(c, s, m):
    box(cab, MW @ V(c), s, m, R=R3)
lbox((0, 0.02, 0.008), (0.3, 0.24, 0.016), "panel_dark")
lbox((0, 0.07, 0.22), (0.07, 0.04, 0.42), "panel_dark")
lbox((0, 0.04, 0.42), (0.14, 0.04, 0.14), "plastic_black")
lbox((0, 0.0, 0.5), (0.76, 0.045, 0.48), "plastic_black")
hw_, hh_ = 0.355, 0.22
quad(cab, [MW @ V((-hw_, -0.0232, 0.5 - hh_)), MW @ V((hw_, -0.0232, 0.5 - hh_)), MW @ V((hw_, -0.0232, 0.5 + hh_)), MW @ V((-hw_, -0.0232, 0.5 + hh_))], "screen_schematic")
lbox((0.3, -0.0235, 0.272), (0.012, 0.001, 0.005), "led_white")
tube(cab, catmull([MW @ V((0, 0.09, 0.3)), MW @ V((0.02, 0.15, 0.1)), V((CX, cy1 - 0.1, cz1 + 0.01)), V((CX + 0.2, cy1 + 0.02, cz1 - 0.05))], 0.03), 0.004, "rubber", n=6)
# tall gas-handling cabinet behind
gx0, gx1, gy0, gy1, gz1 = 2.78, 3.48, 0.9, 1.7, FLOOR + 2.0
bmm(cab, (gx0, gy0, FLOOR), (gx1, gy1, gz1), "graphite")
bmm(cab, (gx0 - 0.01, gy0 - 0.01, gz1), (gx1 + 0.01, gy1 + 0.01, gz1 + 0.03), "powder_black")
bmm(cab, (gx0 + 0.04, gy0 - 0.004, gz1 - 0.55), (gx1 - 0.04, gy0, gz1 - 0.05), "panel_light")
for k in range(5):           # mimic panel lines + valve LEDs
    zz = gz1 - 0.12 - k * 0.08
    bmm(cab, (gx0 + 0.08, gy0 - 0.006, zz), (gx1 - 0.08, gy0 - 0.004, zz + 0.006), "plastic_black")
    for j in range(4):
        xx = gx0 + 0.13 + j * 0.14
        cyl(cab, (xx, gy0 - 0.004, zz + 0.003), (xx, gy0 - 0.009, zz + 0.003), 0.012, random.choice(["led_green", "led_red", "led_amber", "plastic_black"]), n=12)
for k in range(3):           # gauges + valves on the side facing the frame
    gz = FLOOR + 1.35 - k * 0.32
    cyl(cab, (gx0, 1.12, gz), (gx0 - 0.03, 1.12, gz), 0.055, "steel", n=24)
    cyl(cab, (gx0 - 0.03, 1.12, gz), (gx0 - 0.031, 1.12, gz), 0.047, "plastic_white", n=24)
    box(cab, (gx0 - 0.032, 1.12, gz + 0.015), (0.001, 0.004, 0.035), "red_paint", R=Matrix.Rotation(random.uniform(-1, 1), 3, 'X'))
    cyl(cab, (gx0, 1.45, gz), (gx0 - 0.07, 1.45, gz), 0.012, "steel", n=10)
    ring_pts = [V((gx0 - 0.07, 1.45 + 0.045 * math.cos(t), gz + 0.045 * math.sin(t))) for t in np.linspace(0, 2 * math.pi, 25)]
    tube(cab, ring_pts, 0.006, "red_paint" if k != 1 else "plastic_black", n=6, cap=False)
for k in range(3):
    cyl(cab, (gx0 + 0.15 + k * 0.2, 1.3, gz1 + 0.03), (gx0 + 0.15 + k * 0.2, 1.3, gz1 + 0.08), 0.025, "steel", n=12)

# ================================================================== EXTRAS (gas bottles, pump)
ex = BM("CHH_Extras")
for k, (bx, by) in enumerate(((3.75, 1.95), (4.05, 2.05))):
    b0 = V((bx, by, FLOOR))
    cyl(ex, b0, b0 + V((0, 0, 1.25)), 0.115, "cyl_grey", n=32)
    cyl(ex, b0 + V((0, 0, 1.25)), b0 + V((0, 0, 1.36)), 0.115, "paint_brown", n=32, r1=0.08)
    cyl(ex, b0 + V((0, 0, 1.36)), b0 + V((0, 0, 1.41)), 0.08, "paint_brown", n=32, r1=0.03)
    cyl(ex, b0 + V((0, 0, 1.41)), b0 + V((0, 0, 1.47)), 0.022, "brass", n=12)
    bmm(ex, b0 + V((-0.03, -0.03, 1.47)), b0 + V((0.03, 0.03, 1.53)), "brass")
    for gdir in (V((0, -1, 0)), V((1, 0, 0))):
        cyl(ex, b0 + V((0, 0, 1.5)) + gdir * 0.03, b0 + V((0, 0, 1.5)) + gdir * 0.05, 0.03, "steel", n=16)
        cyl(ex, b0 + V((0, 0, 1.5)) + gdir * 0.05, b0 + V((0, 0, 1.5)) + gdir * 0.055, 0.026, "plastic_white", n=16)
    for zz in (0.8, 1.15):
        cyl(ex, b0 + V((0, 0, zz)), b0 + V((0, 0, zz + 0.03)), 0.119, "plastic_black", n=32)
    tube(ex, catmull([b0 + V((-0.03, 0, 1.5)), b0 + V((-0.25, -0.1, 1.45)), V((gx1 + 0.05, 1.5, FLOOR + 1.6)), V((gx1, 1.5, FLOOR + 1.55))], 0.03), 0.005, "steel", n=8)
bmm(ex, (3.55, 2.25, FLOOR), (4.25, 2.3, FLOOR + 1.3), "steel_dark")          # bottle rack back
for zz in (FLOOR + 0.8, FLOOR + 1.15):
    bmm(ex, (3.55, 2.2, zz), (4.25, 2.25, zz + 0.04), "steel_dark")
# scroll pump on the floor inside the back-left corner + bellows up to the deck
SP = V((-1.75, 1.45, FLOOR))
bmm(ex, SP + V((-0.25, -0.17, 0)), SP + V((0.25, 0.17, 0.03)), "steel_dark")
cyl(ex, SP + V((-0.22, 0, 0.18)), SP + V((0.05, 0, 0.18)), 0.13, "panel_light", n=32)
cyl(ex, SP + V((0.05, 0, 0.18)), SP + V((0.24, 0, 0.18)), 0.12, "graphite", n=32)
for k in range(8):
    xx = SP.x + 0.07 + k * 0.02
    cyl(ex, (xx, SP.y, SP.z + 0.18), (xx + 0.008, SP.y, SP.z + 0.18), 0.125, "graphite", n=32)
bmm(ex, SP + V((-0.08, -0.08, 0.3)), SP + V((0.08, 0.08, 0.38)), "panel_dark")
bel2 = catmull([SP + V((0, 0, 0.38)), SP + V((0.0, 0.05, 0.6)), V((-1.8, 1.6, 0.9)), V((-1.85, 1.65, TOP - 0.25)),
                V((-1.65, 1.4, RT + 0.14)), V((-1.0, 0.95, RT + 0.12)), V((-0.68, 0.6, TOP + 0.3)), V((-0.68, 0.55, TOP + 0.05))], 0.04)
bellows(ex, bel2, 0.022, pitch=0.012, amp=0.15, n=12)
cyl(ex, V((-0.68, 0.55, TOP)), V((-0.68, 0.55, TOP + 0.05)), 0.04, "steel", n=16)
tube(ex, catmull([SP + V((0.24, 0.05, 0.18)), SP + V((0.4, 0.2, 0.05)), V((-2.2, 1.9, FLOOR + 0.012)), V((-2.4, 1.9, FLOOR + 0.3))], 0.04), 0.007, "rubber", n=8)

# ================================================================== objects
root = bpy.data.collections.new("chandelier-holder")
bpy.context.scene.collection.children.link(root)
emp = bpy.data.objects.new("chandelier-holder", None)
emp.empty_display_type = 'PLAIN_AXES'
emp.empty_display_size = 0.5
root.objects.link(emp)
BEVEL = {"CHH_Frame": 0.0035, "CHH_Rack": 0.0015, "CHH_Cabinets": 0.002, "CHH_TopHardware": 0.0015, "CHH_Extras": 0.002}
stats = []
for name, bm in BMS.items():
    me = bpy.data.meshes.new(name)
    for m in MATS:
        me.materials.append(m)          # slots BEFORE to_mesh (see agent guide)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    root.objects.link(ob)
    ob.parent = emp
    if name in BEVEL:
        bv = ob.modifiers.new("Bevel", 'BEVEL')
        bv.width = BEVEL[name]
        bv.segments = 2
        bv.limit_method = 'ANGLE'
        bv.angle_limit = math.radians(50)
        bv.harden_normals = False
    # drop unused material slots
    used = {p.material_index for p in me.polygons}
    for i in reversed(range(len(me.materials))):
        if i not in used:
            me.materials.pop(index=i)
    stats.append((name, len(me.vertices), len(me.polygons)))

root.instance_offset = (0, 0, 0)
try:
    root.asset_mark()
    root.asset_data.description = "Aluminium support frame for a dilution-fridge chandelier, with rack, compressor, gas handling, plumbing and cabling. Origin = chandelier origin; floor at z=-1.55."
    root.asset_data.tags.new("quantum")
    root.asset_data.tags.new("lab")
except Exception as e:
    print("asset mark failed", e)

# reference chandelier (linked, separate collection: not part of the asset)
try:
    ref = bpy.data.collections.new("REF_chandelier (linked, not part of asset)")
    bpy.context.scene.collection.children.link(ref)
    with bpy.data.libraries.load(QC_LIB, link=True) as (src, dst):
        dst.collections = ["Quantum_Comp"]
    qc = dst.collections[0]
    inst = bpy.data.objects.new("REF_Quantum_Comp", None)
    inst.instance_type = 'COLLECTION'
    inst.instance_collection = qc
    ref.objects.link(inst)
    print("REF linked, offset", tuple(qc.instance_offset))
except Exception as e:
    print("REF link failed", e)

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.render.fps = 25
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0
for s in stats:
    print("STAT", *s)
print("TOTAL verts", sum(s[1] for s in stats))
if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=OUT, relative_remap=True)
    print("SAVED", OUT)
print("BUILT OK")
