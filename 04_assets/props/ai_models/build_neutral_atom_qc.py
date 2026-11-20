"""Build a generic neutral-atom quantum computer (SH_1 competitor mockup).

Run:  blender -b --factory-startup --python build_neutral_atom_qc.py
Writes 04_assets/props/ai_models/neutral_atom_qc.blend (SAVE=True).

Conventions: metres, floor at z=0, front faces -Y, root empty NAQC_root at origin.
Vacuum chamber centre = NAQC_Atoms empty; camera dive goes through the big
front viewport (NAQC_DiveTarget). Red lasers only, no cyan (competitor tech).
"""
import bpy, bmesh, math, random
from mathutils import Vector as V, Matrix as Mx

SAVE = globals().get("SAVE", True)
OUT = globals().get("OUT", r"C:\Users\mrgav\Documents\GitHub\QS-Blueprint-Colab\04_assets\props\ai_models\neutral_atom_qc.blend")
rng = random.Random(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.render.fps = 25
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0

# ------------------------------------------------------------------ helpers
def T(x, y, z): return Mx.Translation((x, y, z))
def R(axis, deg): return Mx.Rotation(math.radians(deg), 4, axis)
AX = {'X': R('Y', 90), 'Y': R('X', -90), 'Z': Mx()}

def orient(p, fwd, up=(0, 0, 1)):
    y = V(fwd).normalized(); up = V(up)
    x = y.cross(up)
    if x.length < 1e-6: x = y.cross(V((1, 0, 0)))
    x.normalize(); z = x.cross(y).normalized()
    p = V(p)
    return Mx(((x.x, y.x, z.x, p.x), (x.y, y.y, z.y, p.y), (x.z, y.z, z.z, p.z), (0, 0, 0, 1)))

def align_z(p0, p1):
    """Matrix placing a Z-aligned, origin-centred primitive between p0 and p1."""
    p0, p1 = V(p0), V(p1); d = p1 - p0
    q = d.normalized().to_track_quat('Z', 'Y')
    return Mx.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4(), d.length

# ------------------------------------------------------------------ materials
MAT = {}
def mat(key, col, metal=0.0, rough=0.5, emit=None, estr=0.0, trans=0.0, ior=1.45, coat=0.0):
    m = bpy.data.materials.new("NA_" + key)
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs['Base Color'].default_value = (*col, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['IOR'].default_value = ior
    p.inputs['Transmission Weight'].default_value = trans
    p.inputs['Coat Weight'].default_value = coat
    if emit:
        p.inputs['Emission Color'].default_value = (*emit, 1)
        p.inputs['Emission Strength'].default_value = estr
    m.diffuse_color = (*(emit or col), 1)
    m.metallic = metal; m.roughness = rough
    MAT[key] = m
    return m

mat('graphite',   (0.032, 0.033, 0.036), 0.25, 0.48)
mat('logo_panel', (0.045, 0.045, 0.05), 0.2, 0.32, coat=0.3)
mat('extrusion',  (0.09, 0.09, 0.095), 1.0, 0.38)
mat('vent',       (0.008, 0.008, 0.009), 0.0, 0.7)
mat('glass_door', (0.78, 0.78, 0.78), 0.0, 0.02, trans=1.0, ior=1.5)
mat('stainless',  (0.62, 0.6, 0.58), 1.0, 0.2)
mat('stainless_b',(0.55, 0.54, 0.52), 1.0, 0.38)
mat('alu',        (0.78, 0.78, 0.79), 1.0, 0.42)
mat('black',      (0.014, 0.014, 0.016), 0.5, 0.35)
mat('mirror',     (0.92, 0.92, 0.92), 1.0, 0.03)
mat('optic',      (0.95, 0.93, 0.9), 0.0, 0.0, trans=1.0, ior=1.5)
mat('viewport',   (0.93, 0.88, 0.82), 0.0, 0.01, trans=1.0, ior=1.46)
mat('copper',     (0.95, 0.45, 0.25), 1.0, 0.28)
mat('peek',       (0.5, 0.42, 0.3), 0.0, 0.45)
mat('kapton',     (0.75, 0.32, 0.04), 0.0, 0.25, trans=0.3)
mat('gold',       (1.0, 0.74, 0.35), 1.0, 0.25)
mat('ceramic',    (0.85, 0.84, 0.8), 0.0, 0.3)
mat('magnet',     (0.12, 0.12, 0.13), 0.6, 0.4)
mat('rubber',     (0.02, 0.02, 0.022), 0.0, 0.6)
mat('cable_grey', (0.12, 0.12, 0.13), 0.0, 0.5)
mat('fibre',      (0.95, 0.72, 0.04), 0.0, 0.35)
mat('red_plastic',(0.55, 0.02, 0.02), 0.0, 0.4)
mat('panel_alu',  (0.6, 0.6, 0.61), 1.0, 0.45)
mat('panel_grey', (0.2, 0.2, 0.21), 0.3, 0.45)
mat('beam',       (1.0, 0.03, 0.02), emit=(1.0, 0.03, 0.02), estr=22.0)

def soft_mat(key, col, strength):
    """Translucent glow (transparent + emission) for wide, faint beams and halos."""
    m = bpy.data.materials.new("NA_" + key); nt = m.node_tree; N = nt.nodes
    N.clear()
    out = N.new('ShaderNodeOutputMaterial'); add = N.new('ShaderNodeAddShader')
    tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*col, 1); em.inputs['Strength'].default_value = strength
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.6
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = strength
    inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs['Facing'], inv.inputs[1])      # brighter in the core, fades at the edges
    nt.links.new(inv.outputs[0], mul.inputs[0]); nt.links.new(mul.outputs[0], em.inputs['Strength'])
    nt.links.new(tr.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs['Surface'])
    m.diffuse_color = (*col, 0.3); MAT[key] = m
soft_mat('beam_soft', (1.0, 0.05, 0.03), 0.5)
soft_mat('atoms_halo', (1.0, 0.18, 0.12), 0.35)
mat('atoms',      (1.0, 0.2, 0.15), emit=(1.0, 0.2, 0.15), estr=60.0)
mat('led_warm',   (1.0, 0.82, 0.62), emit=(1.0, 0.82, 0.62), estr=18.0)
mat('disp_amber', (1.0, 0.5, 0.08), emit=(1.0, 0.5, 0.08), estr=3.0)
mat('disp_white', (0.9, 0.88, 0.85), emit=(0.9, 0.88, 0.85), estr=2.0)
mat('disp_red',   (1.0, 0.05, 0.02), emit=(1.0, 0.05, 0.02), estr=4.0)
mat('led_green',  (0.25, 1.0, 0.1), emit=(0.25, 1.0, 0.1), estr=8.0)
mat('led_amber',  (1.0, 0.45, 0.0), emit=(1.0, 0.45, 0.0), estr=8.0)
mat('led_red',    (1.0, 0.02, 0.0), emit=(1.0, 0.02, 0.0), estr=8.0)

def hole_mat():
    """Optical-table top: stainless with a 25 mm M6 hole grid (object coords)."""
    m = mat('table_top', (0.5, 0.5, 0.5), 1.0, 0.35)
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]
    tc = N.new('ShaderNodeTexCoord')
    def vm(op, a, b=None):
        n = N.new('ShaderNodeVectorMath'); n.operation = op
        L.new(a, n.inputs[0])
        if b is not None: n.inputs[1].default_value = b
        return n
    v1 = vm('DIVIDE', tc.outputs['Object'], (0.025, 0.025, 1))
    v2 = vm('FRACTION', v1.outputs[0])
    v3 = vm('SUBTRACT', v2.outputs[0], (0.5, 0.5, 0.5))
    v4 = vm('MULTIPLY', v3.outputs[0], (1, 1, 0))
    v5 = vm('LENGTH', v4.outputs[0])
    def mr(a, b, lo, hi):
        n = N.new('ShaderNodeMapRange'); L.new(v5.outputs['Value'], n.inputs['Value'])
        n.inputs['From Min'].default_value = a; n.inputs['From Max'].default_value = b
        n.inputs['To Min'].default_value = lo; n.inputs['To Max'].default_value = hi
        return n
    L.new(mr(0.11, 0.125, 0.012, 0.52).outputs['Result'], p.inputs['Base Color'])
    L.new(mr(0.11, 0.125, 0.7, 0.33).outputs['Result'], p.inputs['Roughness'])
    L.new(mr(0.11, 0.125, 0.0, 1.0).outputs['Result'], p.inputs['Metallic'])
hole_mat()

# ------------------------------------------------------------------ collections
root_coll = bpy.data.collections.new("NAQC"); sc.collection.children.link(root_coll)
COLL = {}
for c in ("NAQC_Enclosure", "NAQC_Table_Optics", "NAQC_Vacuum", "NAQC_Racks", "NAQC_Cables", "NAQC_Beams", "NAQC_Helpers"):
    COLL[c] = bpy.data.collections.new(c); root_coll.children.link(COLL[c])
ROOT = bpy.data.objects.new("NAQC_root", None); root_coll.objects.link(ROOT)
ROOT.empty_display_type = 'PLAIN_AXES'; ROOT.empty_display_size = 0.5

# ------------------------------------------------------------------ mesh builder
class MB:
    """Each primitive is built in a scratch bmesh (s.bm), then copied into s.out.
    Keeps bevel ops from touching / reindexing earlier parts."""
    def __init__(s, name, coll):
        s.name, s.coll, s.mats = name, COLL[coll], []
        s.out = bmesh.new(); s.bm = bmesh.new()
    def mi(s, m):
        if m not in s.mats: s.mats.append(m)
        return s.mats.index(m)
    def _new(s, n):
        return list(s.bm.verts)
    def _fin(s, vs, m, M, smooth=True):
        t = s.bm
        bmesh.ops.transform(t, matrix=M, verts=list(t.verts))
        i = s.mi(m); o = s.out; vmap = {}
        for v in t.verts: vmap[v] = o.verts.new(v.co)
        for f in t.faces:
            nf = o.faces.new([vmap[v] for v in f.verts]); nf.material_index = i; nf.smooth = smooth
        t.free(); s.bm = bmesh.new()
        return None
    def _bevel(s, n, vs, bev, seg):
        bmesh.ops.bevel(s.bm, geom=list(s.bm.edges), offset=bev, segments=seg, affect='EDGES', clamp_overlap=True)
        return list(s.bm.verts)
    def box(s, M, size, m, bev=0.0, seg=1):
        n = 0
        bmesh.ops.create_cube(s.bm, size=1.0)
        vs = s._new(n)
        for v in vs: v.co = V((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        if bev > 0: vs = s._bevel(n, vs, bev, seg)
        return s._fin(vs, m, M)
    def boxp(s, p0, p1, m, bev=0.0, seg=1):
        """Axis-aligned box from corner p0 to corner p1."""
        c = [(a + b) / 2 for a, b in zip(p0, p1)]; sz = [abs(b - a) for a, b in zip(p0, p1)]
        return s.box(T(*c), sz, m, bev, seg)
    def cyl(s, M, r, h, m, seg=24, r2=None, cap=True, bev=0.0):
        n = len(s.bm.verts)
        bmesh.ops.create_cone(s.bm, cap_ends=cap, cap_tris=False, segments=seg,
                              radius1=r, radius2=r if r2 is None else r2, depth=h)
        vs = s._new(n)
        if bev > 0:
            es = [e for e in {e for v in vs for e in v.link_edges}
                  if len(e.link_faces) == 2 and abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-7]
            bmesh.ops.bevel(s.bm, geom=es, offset=bev, segments=1, affect='EDGES', clamp_overlap=True)
            vs = s._new(n)
        return s._fin(vs, m, M)
    def ring(s, M, ri, ro, h, m, seg=32):
        n = len(s.bm.verts); bm = s.bm; rows = []
        for k in range(seg):
            a = 2 * math.pi * k / seg; c, sn = math.cos(a), math.sin(a)
            rows.append([bm.verts.new((ro * c, ro * sn, -h / 2)), bm.verts.new((ro * c, ro * sn, h / 2)),
                         bm.verts.new((ri * c, ri * sn, h / 2)), bm.verts.new((ri * c, ri * sn, -h / 2))])
        for k in range(seg):
            A, B = rows[k], rows[(k + 1) % seg]
            for j in range(4):
                j2 = (j + 1) % 4
                bm.faces.new((A[j], B[j], B[j2], A[j2]))
        return s._fin(s._new(n), m, M)
    def torus(s, M, Rr, r, m, seg=32, seg2=8):
        n = len(s.bm.verts); bm = s.bm; rows = []
        for k in range(seg):
            a = 2 * math.pi * k / seg; row = []
            for j in range(seg2):
                b = 2 * math.pi * j / seg2; rr = Rr + r * math.cos(b)
                row.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), r * math.sin(b))))
            rows.append(row)
        for k in range(seg):
            A, B = rows[k], rows[(k + 1) % seg]
            for j in range(seg2):
                j2 = (j + 1) % seg2
                bm.faces.new((A[j], B[j], B[j2], A[j2]))
        return s._fin(s._new(n), m, M)
    def sphere(s, M, r, m, seg=16):
        n = len(s.bm.verts)
        bmesh.ops.create_uvsphere(s.bm, u_segments=seg, v_segments=seg // 2, radius=r)
        return s._fin(s._new(n), m, M)
    def seg(s, p0, p1, r, m, seg=8):
        M, L = align_z(p0, p1)
        return s.cyl(M, r, L, m, seg=seg)
    def segbox(s, p0, p1, w, h, m):
        M, L = align_z(p0, p1)
        return s.box(M, (w, h, L), m)
    def done(s):
        me = bpy.data.meshes.new(s.name)
        for m in s.mats: me.materials.append(MAT[m])
        s.out.to_mesh(me); s.out.free(); s.bm.free()
        me.set_sharp_from_angle(angle=math.radians(32))
        ob = bpy.data.objects.new(s.name, me); s.coll.objects.link(ob); ob.parent = ROOT
        return ob

def curves(name, coll, splines, r, m, res=10):
    """splines: list of (points, radius_scale)."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = r; cu.bevel_resolution = 3; cu.resolution_u = res; cu.use_fill_caps = True
    for pts, sc_r in splines:
        sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = sc_r
    cu.materials.append(MAT[m])
    ob = bpy.data.objects.new(name, cu); COLL[coll].objects.link(ob); ob.parent = ROOT
    return ob

def route(p0, d0, p1, d1, via=(), lead=0.06):
    p0, p1 = V(p0), V(p1)
    return [p0, p0 + V(d0) * lead, *[V(v) for v in via], p1 + V(d1) * lead, p1]

# ------------------------------------------------------------------ key dimensions
W2, D2 = 1.45, 0.75          # main body half width / half depth
PZ, HZ, CZ = 0.88, 2.12, 2.45  # plinth top, hood top, crown top
TT = 0.90                     # optical table surface
BZ = 0.975                    # beam height on table
BH = BZ - TT
C = V((0.35, 0.0, 1.15))      # vacuum chamber centre (atoms)
TX, TY = 1.30, 0.60           # optical table half sizes

# ================================================================== ENCLOSURE
def build_enclosure():
    pl = MB("NA_Plinth", "NAQC_Enclosure")
    # kick plate + feet
    pl.boxp((-W2 + 0.03, -D2 + 0.03, 0.02), (W2 - 0.03, D2 - 0.03, 0.1), 'vent')
    for x in (-W2 + 0.12, 0, W2 - 0.12):
        for y in (-D2 + 0.12, D2 - 0.12):
            pl.cyl(T(x, y, 0.012), 0.035, 0.024, 'rubber', seg=20, bev=0.003)
            pl.cyl(T(x, y, 0.06), 0.008, 0.06, 'stainless', seg=12)
    # front door panels: left, centre (logo), right
    segs = [(-W2, -0.5, 'door'), (-0.5, 0.5, 'logo'), (0.5, W2, 'door')]
    for x0, x1, kind in segs:
        x0g, x1g = x0 + 0.003, x1 - 0.003
        m = 'logo_panel' if kind == 'logo' else 'graphite'
        pl.boxp((x0g, -D2 - 0.02, 0.1), (x1g, -D2, PZ - 0.012), m, bev=0.004, seg=2)
        if kind == 'door':
            # vent grille (louvres) bottom of door
            gx0, gx1 = x0g + 0.06, x1g - 0.06
            pl.boxp((gx0, -D2 - 0.021, 0.16), (gx1, -D2 - 0.019, 0.36), 'vent')
            for i in range(14):
                z = 0.168 + i * 0.0137
                pl.box(T((gx0 + gx1) / 2, -D2 - 0.024, z) @ R('X', 35), (gx1 - gx0 - 0.004, 0.002, 0.012), 'graphite')
            # recessed vertical handle
            hx = x1g - 0.05 if x0 < 0 else x0g + 0.05
            pl.boxp((hx - 0.012, -D2 - 0.021, 0.5), (hx + 0.012, -D2 - 0.019, 0.78), 'vent')
            pl.boxp((hx - 0.006, -D2 - 0.032, 0.52), (hx + 0.006, -D2 - 0.02, 0.76), 'extrusion', bev=0.003, seg=2)
    # sides + back skins
    for sx in (-1, 1):
        pl.boxp((sx * W2, -D2, 0.1), (sx * (W2 + 0.02), D2, PZ - 0.012), 'graphite', bev=0.003)
    pl.boxp((-W2, D2, 0.1), (W2, D2 + 0.02, PZ - 0.012), 'graphite')
    # top deck around the optical table (gap frame)
    pl.boxp((-W2 - 0.02, -D2 - 0.02, PZ - 0.012), (W2 + 0.02, -TY - 0.01, PZ + 0.012), 'graphite', bev=0.004, seg=2)
    pl.boxp((-W2 - 0.02, TY + 0.01, PZ - 0.012), (W2 + 0.02, D2 + 0.02, PZ + 0.012), 'graphite', bev=0.004, seg=2)
    for sx in (-1, 1):
        a, b = sorted((sx * (TX + 0.01), sx * (W2 + 0.02)))
        pl.boxp((a, -TY - 0.01, PZ - 0.012), (b, TY + 0.01, PZ + 0.012), 'graphite', bev=0.004, seg=2)
    # thin warm light line on plinth top edge (signature)
    pl.boxp((-W2 + 0.04, -D2 - 0.0215, PZ - 0.03), (W2 - 0.04, -D2 - 0.0205, PZ - 0.024), 'led_warm')
    pl.done()

    # ---- extrusion frame of the hood
    fr = MB("NA_Hood_Frame", "NAQC_Enclosure")
    e = 0.045; h = e / 2
    def ext(p0, p1):
        c = [(a + b) / 2 for a, b in zip(p0, p1)]
        sz = [max(abs(b - a), e) for a, b in zip(p0, p1)]
        fr.box(T(*c), sz, 'extrusion', bev=0.003, seg=2)
        # dark T-slot grooves on the two visible long faces
        axis = max(range(3), key=lambda i: abs(p1[i] - p0[i]))
        for k in range(3):
            if k == axis: continue
            for sgn in (-1, 1):
                gsz = list(sz); gsz[k] = 0.002
                others = [i for i in range(3) if i not in (axis, k)][0]
                gsz[others] = 0.008; gsz[axis] = sz[axis] - 0.01
                gc = list(c); gc[k] += sgn * (sz[k] / 2 + 0.0002)
                fr.box(T(*gc), gsz, 'vent')
    zb, zt = PZ + 0.012 + h, HZ - h
    for x in (-W2 + h, 0.0, W2 - h):
        ext((x, -D2 + h, PZ + 0.012), (x, -D2 + h, HZ))
    for x in (-W2 + h, W2 - h):
        ext((x, D2 - h, PZ + 0.012), (x, D2 - h, HZ))
        ext((x, -D2 + h, zt), (x, D2 - h, zt))
        ext((x, -D2 + h, zb), (x, D2 - h, zb))
        ext((x, -D2 + h, 1.55), (x, D2 - h, 1.55))
    for y in (-D2 + h, D2 - h):
        ext((-W2 + h, y, zt), (W2 - h, y, zt))
        ext((-W2 + h, y, zb), (W2 - h, y, zb))
    # sliding-door tracks
    fr.boxp((-W2, -D2 - 0.05, HZ - 0.05), (W2, -D2, HZ - 0.02), 'extrusion', bev=0.003)
    fr.boxp((-W2, -D2 - 0.05, PZ + 0.012), (W2, -D2, PZ + 0.03), 'extrusion', bev=0.003)
    # gussets / corner brackets
    for x in (-W2 + e, W2 - e):
        for y in (-D2 + e, D2 - e):
            for z in (zb + h, zt - h):
                fr.box(T(x, y, z), (0.03, 0.03, 0.03), 'black', bev=0.002)
    fr.done()

    # ---- side glass + back wall
    gl = MB("NA_Hood_SideGlass", "NAQC_Enclosure")
    for sx in (-1, 1):
        x = sx * (W2 - h)
        gl.boxp((x - 0.003, -D2 + e, PZ + 0.012 + e), (x + 0.003, D2 - e, HZ - e), 'glass_door')
    gl.done()
    bw = MB("NA_Hood_BackWall", "NAQC_Enclosure")
    bw.boxp((-W2 + e, D2 - 0.03, PZ + 0.012), (W2 - e, D2 - 0.015, HZ - e), 'graphite')
    # slotted vertical cable ducts on back wall
    for x in (-1.25, 1.25):
        bw.boxp((x - 0.04, D2 - 0.09, TT + 0.1), (x + 0.04, D2 - 0.03, HZ - 0.08), 'graphite', bev=0.002)
        for i in range(36):
            z = TT + 0.13 + i * 0.03
            bw.boxp((x - 0.041, D2 - 0.091, z), (x + 0.041, D2 - 0.085, z + 0.008), 'vent')
    # horizontal cable tray under the crown, back
    bw.boxp((-W2 + e, D2 - 0.2, HZ - 0.12), (W2 - e, D2 - 0.04, HZ - 0.115), 'stainless_b')
    for x in [(-W2 + 0.1) + i * 0.1 for i in range(28)]:
        bw.boxp((x, D2 - 0.2, HZ - 0.115), (x + 0.004, D2 - 0.04, HZ - 0.1), 'stainless_b')
    bw.boxp((-W2 + e, D2 - 0.205, HZ - 0.12), (W2 - e, D2 - 0.2, HZ - 0.075), 'stainless_b')
    bw.done()

    # ---- sliding glass doors (separate objects, animate/hide freely)
    for name, x0, x1, y in (("NA_Door_L", -W2 + 0.02, 0.03, -D2 - 0.036), ("NA_Door_R", -0.03, W2 - 0.02, -D2 - 0.018)):
        d = MB(name, "NAQC_Enclosure")
        z0, z1 = PZ + 0.035, HZ - 0.055
        d.boxp((x0 + 0.02, y - 0.004, z0 + 0.02), (x1 - 0.02, y + 0.004, z1 - 0.02), 'glass_door')
        for (a, b) in (((x0, z0), (x1, z0 + 0.03)), ((x0, z1 - 0.03), (x1, z1)),
                       ((x0, z0), (x0 + 0.025, z1)), ((x1 - 0.025, z0), (x1, z1))):
            d.boxp((a[0], y - 0.008, a[1]), (b[0], y + 0.008, b[1]), 'extrusion', bev=0.002)
        hx = x1 - 0.07 if name.endswith("L") else x0 + 0.07
        d.boxp((hx - 0.008, y - 0.045, 1.2), (hx + 0.008, y - 0.03, 1.75), 'stainless', bev=0.004, seg=2)
        for z in (1.25, 1.7):
            d.boxp((hx - 0.006, y - 0.032, z - 0.006), (hx + 0.006, y - 0.008, z + 0.006), 'stainless')
        d.done()

    # ---- crown with fan filter units
    cr = MB("NA_Crown", "NAQC_Enclosure")
    cr.boxp((-W2 - 0.02, -D2 - 0.06, HZ), (W2 + 0.02, D2 + 0.02, CZ), 'graphite', bev=0.006, seg=2)
    cr.boxp((-0.55, -D2 - 0.064, HZ + 0.06), (0.55, -D2 - 0.058, CZ - 0.06), 'logo_panel', bev=0.002)
    cr.boxp((-W2 + 0.05, -D2 - 0.0645, HZ + 0.025), (W2 - 0.05, -D2 - 0.0635, HZ + 0.031), 'led_warm')
    for sx in (-1, 1):  # side vents on crown front
        x0, x1 = sorted((sx * 0.7, sx * 1.3))
        for i in range(10):
            z = HZ + 0.1 + i * 0.014
            cr.boxp((x0, -D2 - 0.0625, z), (x1, -D2 - 0.058, z + 0.006), 'vent')
    for x in (-0.72, 0.72):
        cr.boxp((x - 0.32, -0.35, CZ), (x + 0.32, 0.35, CZ + 0.07), 'stainless_b', bev=0.004)
        for i in range(30):
            xx = x - 0.29 + i * 0.02
            cr.boxp((xx, -0.32, CZ + 0.07), (xx + 0.006, 0.32, CZ + 0.076), 'vent')
        cr.boxp((x - 0.32, 0.36, CZ + 0.01), (x - 0.18, 0.44, CZ + 0.05), 'black', bev=0.003)
    cr.done()

    # ---- interior LED strips
    led = MB("NA_Hood_LEDs", "NAQC_Enclosure")
    for y in (-D2 + 0.06, D2 - 0.25):
        led.boxp((-W2 + 0.06, y - 0.012, HZ - 0.012), (W2 - 0.06, y + 0.012, HZ - 0.002), 'extrusion')
        led.boxp((-W2 + 0.07, y - 0.008, HZ - 0.014), (W2 - 0.07, y + 0.008, HZ - 0.012), 'led_warm')
    led.done()

# ================================================================== RACK (left) & SERVICE CABINET (right)
UH = 0.04445
def instrument(mb, xc, yf, zb, u, kind):
    h = u * UH; w = 0.483
    mb.box(T(xc, yf + 0.25, zb + h / 2), (0.43, 0.48, h - 0.004), 'graphite')
    pm = rng.choice(['panel_alu', 'panel_grey', 'black', 'panel_grey'])
    mb.box(T(xc, yf + 0.002, zb + h / 2), (w, 0.004, h - 0.0016), pm, bev=0.0008)
    fy = yf  # front surface
    if u >= 2:
        for sx in (-1, 1):
            hx = xc + sx * 0.222
            mb.boxp((hx - 0.005, fy - 0.03, zb + 0.012), (hx + 0.005, fy - 0.022, zb + h - 0.012), 'stainless', bev=0.002)
            for z in (zb + 0.012, zb + h - 0.02):
                mb.boxp((hx - 0.005, fy - 0.026, z), (hx + 0.005, fy, z + 0.008), 'stainless')
    xl, xr = xc - 0.2, xc + 0.2
    zc = zb + h / 2
    def knob(x, z, r=0.009, m='black'):
        mb.cyl(T(x, fy - 0.007, z) @ AX['Y'], r, 0.014, m, seg=16, bev=0.0015)
        mb.cyl(T(x, fy - 0.015, z) @ AX['Y'], r * 0.25, 0.002, 'alu', seg=8)
    def bnc(x, z):
        mb.cyl(T(x, fy - 0.006, z) @ AX['Y'], 0.0055, 0.012, 'stainless', seg=12)
        mb.cyl(T(x, fy - 0.013, z) @ AX['Y'], 0.0025, 0.004, 'gold', seg=8)
    def led(x, z, m):
        mb.cyl(T(x, fy - 0.0015, z) @ AX['Y'], 0.0018, 0.003, m, seg=8)
    def disp(x0, x1, z0, z1, m):
        mb.boxp((x0 - 0.004, fy - 0.0015, z0 - 0.004), (x1 + 0.004, fy, z1 + 0.004), 'black')
        mb.boxp((x0, fy - 0.0025, z0), (x1, fy - 0.0015, z1), m)
    if kind == 'scope':
        disp(xl + 0.01, xl + 0.2, zb + 0.02, zb + h - 0.02, rng.choice(['disp_white', 'disp_amber']))
        for i in range(3):
            for j in range(2):
                knob(xl + 0.25 + i * 0.04, zc - 0.02 + j * 0.04)
        for i in range(4): bnc(xl + 0.25 + i * 0.035, zb + 0.015)
        led(xr - 0.01, zb + h - 0.015, 'led_green')
    elif kind == 'driver':
        n = rng.choice([4, 6, 8])
        for i in range(n):
            x = xl + 0.03 + i * (0.34 / n)
            knob(x, zc + 0.006, 0.007, rng.choice(['black', 'alu']))
            led(x, zc - 0.014, rng.choice(['led_green', 'led_green', 'led_amber']))
            bnc(x + 0.02, zc + 0.006)
    elif kind == 'psu':
        for i in range(2):
            disp(xl + 0.02 + i * 0.12, xl + 0.1 + i * 0.12, zc + 0.004, zc + 0.026, 'disp_red')
            knob(xl + 0.04 + i * 0.12, zc - 0.02)
            knob(xl + 0.08 + i * 0.12, zc - 0.02)
        for i, m in enumerate(['red_plastic', 'black', 'red_plastic', 'black']):
            mb.cyl(T(xr - 0.11 + i * 0.03, fy - 0.01, zc - 0.012) @ AX['Y'], 0.006, 0.02, m, seg=12)
        led(xr - 0.02, zc + 0.02, 'led_green')
    elif kind == 'switch':
        for i in range(12):
            for j in range(2):
                x = xl + 0.08 + i * 0.022; z = zc - 0.009 + j * 0.016
                mb.boxp((x, fy - 0.0015, z - 0.0055), (x + 0.016, fy - 0.0005, z + 0.0055), 'vent')
                led(x + 0.003, z + 0.0075, rng.choice(['led_green', 'led_amber']))
        disp(xl + 0.005, xl + 0.06, zc - 0.007, zc + 0.007, 'disp_amber')
    elif kind == 'vent':
        for i in range(int(h / 0.01) - 1):
            z = zb + 0.008 + i * 0.01
            mb.boxp((xl, fy - 0.0012, z), (xr, fy - 0.0002, z + 0.004), 'vent')
    elif kind == 'controller':
        disp(xl + 0.02, xl + 0.12, zc - 0.012, zc + 0.012, rng.choice(['disp_amber', 'disp_white']))
        for i in range(6):
            mb.boxp((xl + 0.15 + i * 0.022, fy - 0.004, zc - 0.007), (xl + 0.165 + i * 0.022, fy, zc + 0.007), 'panel_grey', bev=0.001)
        led(xr - 0.02, zc, 'led_green'); led(xr - 0.035, zc, 'led_amber')
        for i in range(3): bnc(xr - 0.12 + i * 0.025, zc)

def build_rack():
    x0, x1 = -W2 - 0.67, -W2 - 0.02
    xc = (x0 + x1) / 2; y0, y1 = -D2, D2; H = 2.25
    fr = MB("NA_Rack_Cabinet", "NAQC_Racks")
    for x in (x0 + 0.015, x1 - 0.015):
        for y in (y0 + 0.015, y1 - 0.015):
            fr.boxp((x - 0.015, y - 0.015, 0.06), (x + 0.015, y + 0.015, H), 'extrusion', bev=0.002)
    fr.boxp((x0, y0, H - 0.04), (x1, y1, H), 'graphite', bev=0.004)
    fr.boxp((x0, y0, 0.06), (x1, y1, 0.12), 'graphite', bev=0.003)
    for x in (x0 + 0.003, x1 - 0.003):
        fr.boxp((x - 0.003, y0 + 0.03, 0.12), (x + 0.003, y1 - 0.03, H - 0.04), 'graphite')
    fr.boxp((x0 + 0.03, y1 - 0.006, 0.12), (x1 - 0.03, y1, H - 0.04), 'graphite')
    for sx in (-1, 1):  # 19" rails
        x = xc + sx * 0.235
        fr.boxp((x - 0.008, y0 + 0.06, 0.12), (x + 0.008, y0 + 0.064, H - 0.04), 'stainless_b')
    for x in (x0 + 0.06, x1 - 0.06):
        for y in (y0 + 0.08, y1 - 0.08):
            fr.cyl(T(x, y, 0.03) @ AX['X'], 0.03, 0.02, 'rubber', seg=16)
            fr.boxp((x - 0.02, y - 0.03, 0.045), (x + 0.02, y + 0.03, 0.06), 'stainless_b')
    # top cable exit brush
    fr.boxp((xc - 0.15, y1 - 0.25, H), (xc + 0.15, y1 - 0.12, H + 0.012), 'black', bev=0.003)
    fr.done()
    un = MB("NA_Rack_Instruments", "NAQC_Racks")
    kinds = ['controller', 'driver', 'driver', 'scope', 'psu', 'switch', 'vent', 'driver', 'controller', 'psu', 'vent']
    z = 0.16; yf = y0 + 0.058
    plan = [(1, 'switch'), (2, 'controller'), (1, 'vent'), (3, 'scope'), (2, 'driver'), (2, 'driver'), (1, 'controller'),
            (2, 'psu'), (1, 'vent'), (3, 'driver'), (2, 'controller'), (4, 'scope'), (1, 'switch'), (2, 'driver'),
            (2, 'psu'), (1, 'vent'), (3, 'driver'), (2, 'controller'), (2, 'psu'), (3, 'vent'), (2, 'driver')]
    for u, k in plan:
        if z + u * UH > H - 0.06: break
        instrument(un, xc, yf, z, u, k); z += u * UH + 0.0015
    un.done()
    # patch cables on the instrument fronts
    sp = []
    for i in range(14):
        za = rng.uniform(0.3, 2.0); zb_ = za + rng.uniform(-0.35, 0.35)
        xa = xc + rng.uniform(-0.18, 0.18); xb = xc + rng.choice([-0.24, 0.24])
        ya = yf - 0.015
        sp.append(([V((xa, ya, za)), V((xa, ya - 0.05, za - 0.04)), V(((xa + xb) / 2, ya - 0.09, (za + zb_) / 2 - 0.08)),
                    V((xb, ya - 0.05, zb_)), V((xb, ya + 0.02, zb_))], 1.0))
    curves("NA_Rack_PatchCables", "NAQC_Racks", sp, 0.0022, 'rubber')
    dr = MB("NA_Rack_Door", "NAQC_Racks")
    dy = y0 - 0.012
    dr.boxp((x0 + 0.03, dy - 0.003, 0.15), (x1 - 0.03, dy + 0.003, H - 0.07), 'glass_door')
    for (a, b) in (((x0, 0.12), (x1, 0.16)), ((x0, H - 0.08), (x1, H - 0.04)), ((x0, 0.12), (x0 + 0.035, H - 0.04)), ((x1 - 0.035, 0.12), (x1, H - 0.04))):
        dr.boxp((a[0], dy - 0.01, a[1]), (b[0], dy + 0.01, b[1]), 'extrusion', bev=0.002)
    dr.boxp((x1 - 0.025, dy - 0.04, 1.0), (x1 - 0.012, dy - 0.01, 1.3), 'stainless', bev=0.004, seg=2)
    dr.done()

def build_service_cabinet():
    x0, x1 = W2 + 0.02, W2 + 0.67; y0, y1 = -D2, D2; H = CZ
    cb = MB("NA_Service_Cabinet", "NAQC_Racks")
    cb.boxp((x0, y0, 0.08), (x1, y1, H), 'graphite', bev=0.006, seg=2)
    cb.boxp((x0 + 0.02, y0 + 0.02, 0.0), (x1 - 0.02, y1 - 0.02, 0.08), 'vent')
    # door
    cb.boxp((x0 + 0.015, y0 - 0.018, 0.1), (x1 - 0.015, y0, H - 0.04), 'graphite', bev=0.004, seg=2)
    for zc in (0.35, 1.95):  # louvre banks
        cb.boxp((x0 + 0.08, y0 - 0.019, zc - 0.17), (x1 - 0.08, y0 - 0.017, zc + 0.17), 'vent')
        for i in range(24):
            z = zc - 0.165 + i * 0.0142
            cb.box(T((x0 + x1) / 2, y0 - 0.022, z) @ R('X', 35), (x1 - x0 - 0.165, 0.002, 0.012), 'graphite')
    cb.boxp((x0 + 0.2, y0 - 0.021, 1.38), (x1 - 0.2, y0 - 0.018, 1.48), 'black')
    cb.boxp((x0 + 0.21, y0 - 0.022, 1.39), (x1 - 0.21, y0 - 0.021, 1.47), 'disp_amber')
    for i, m in enumerate(['led_green', 'led_green', 'led_amber']):
        cb.cyl(T(x0 + 0.24 + i * 0.03, y0 - 0.02, 1.33) @ AX['Y'], 0.004, 0.004, m, seg=10)
    cb.boxp((x0 + 0.04, y0 - 0.05, 0.95), (x0 + 0.055, y0 - 0.018, 1.25), 'stainless', bev=0.005, seg=2)
    cb.cyl(T(x0 + 0.048, y0 - 0.022, 1.3) @ AX['Y'], 0.009, 0.008, 'stainless', seg=16)
    # side logo panel (+X)
    cb.boxp((x1, y0 + 0.15, 0.6), (x1 + 0.005, y1 - 0.15, 2.0), 'logo_panel', bev=0.002)
    # top: fibre/cable exit + chiller fan
    cb.boxp(((x0 + x1) / 2 - 0.12, y1 - 0.3, H), ((x0 + x1) / 2 + 0.12, y1 - 0.1, H + 0.015), 'black', bev=0.003)
    cb.cyl(T((x0 + x1) / 2, -0.25, H + 0.01), 0.17, 0.02, 'vent', seg=40)
    cb.ring(T((x0 + x1) / 2, -0.25, H + 0.012), 0.17, 0.19, 0.024, 'stainless_b', seg=40)
    for k in range(6):
        cb.box(T((x0 + x1) / 2, -0.25, H + 0.024) @ R('Z', k * 30), (0.36, 0.004, 0.004), 'stainless_b')
    cb.done()

# ================================================================== OPTICAL TABLE
def build_table():
    t = MB("NA_Optical_Table", "NAQC_Table_Optics")
    t.boxp((-TX, -TY, TT - 0.008), (TX, TY, TT), 'table_top', bev=0.002)
    t.boxp((-TX, -TY, TT - 0.3), (TX, TY, TT - 0.008), 'graphite', bev=0.004)
    t.boxp((-TX - 0.001, -TY - 0.001, TT - 0.26), (TX + 0.001, TY + 0.001, TT - 0.05), 'black')
    for x in (-TX + 0.25, TX - 0.25):
        for y in (-TY + 0.2, TY - 0.2):
            t.cyl(T(x, y, 0.33), 0.09, 0.42, 'graphite', seg=32, bev=0.01)
            t.cyl(T(x, y, 0.56), 0.075, 0.06, 'black', seg=32)
            t.cyl(T(x, y, 0.11), 0.11, 0.03, 'graphite', seg=32, bev=0.005)
    # raised breadboard (front-left) on posts
    bx0, bx1, by0, by1, bz = -1.25, -0.62, -0.58, -0.3, 1.25
    t.boxp((bx0, by0, bz - 0.012), (bx1, by1, bz), 'table_top', bev=0.0015)
    t.boxp((bx0, by0, bz - 0.025), (bx1, by1, bz - 0.012), 'black')
    for x in (bx0 + 0.03, bx1 - 0.03):
        for y in (by0 + 0.025, by1 - 0.025):
            t.cyl(T(x, y, (TT + bz - 0.025) / 2), 0.019, bz - 0.025 - TT, 'stainless', seg=20)
            t.cyl(T(x, y, TT + 0.01), 0.03, 0.02, 'stainless_b', seg=20)
    # enclosed laser module on the breadboard
    t.boxp((-1.2, -0.55, bz), (-0.75, -0.34, bz + 0.13), 'panel_grey', bev=0.006, seg=2)
    t.boxp((-1.21, -0.56, bz + 0.13), (-0.74, -0.33, bz + 0.142), 'alu', bev=0.003)
    for i in range(16):
        x = -1.18 + i * 0.027
        t.boxp((x, -0.53, bz + 0.142), (x + 0.012, -0.36, bz + 0.17), 'alu')
    for i in range(3):
        t.cyl(T(-0.745, -0.5 + i * 0.05, bz + 0.05) @ AX['X'], 0.007, 0.03, 'stainless', seg=12)
    t.boxp((-1.15, -0.5505, bz + 0.03), (-0.95, -0.55, bz + 0.1), 'logo_panel')
    t.done()

# ================================================================== OPTICS + BEAMS
OP = None; BM = None
FIB = []   # fibre start points (world) with direction

def post_stack(M, h=BH, top=-0.012):
    OP.cyl(M @ T(0, 0, -h + 0.025), 0.0075, 0.05, 'black', seg=16)
    L = (top) - (-h + 0.03)
    if L > 0.002: OP.cyl(M @ T(0, 0, -h + 0.03 + L / 2), 0.006, L + 0.004, 'stainless', seg=14)
    OP.box(M @ T(0, 0, -h + 0.0035), (0.05, 0.022, 0.007), 'black', bev=0.0015)
    for sx in (-1, 1):
        OP.cyl(M @ T(sx * 0.018, 0, -h + 0.009), 0.004, 0.004, 'stainless_b', seg=10)
    OP.cyl(M @ T(0.009, 0, -h + 0.04) @ AX['X'], 0.0025, 0.008, 'stainless_b', seg=8)

def mirror_head(M, size=0.0127):
    OP.cyl(M @ T(0, 0.003, 0) @ AX['Y'], size, 0.006, 'mirror', seg=24)
    OP.ring(M @ T(0, 0.002, 0) @ AX['Y'], size, size + 0.003, 0.008, 'black', seg=24)
    OP.box(M @ T(0, -0.005, 0), (0.038, 0.008, 0.038), 'black', bev=0.002)
    OP.box(M @ T(0, -0.0165, 0), (0.038, 0.008, 0.038), 'black', bev=0.002)
    for (x, z) in ((0.013, 0.013), (-0.013, -0.013), (0.013, -0.013)):
        OP.cyl(M @ T(x, -0.028, z) @ AX['Y'], 0.002, 0.02, 'stainless', seg=8)
        if (x, z) != (0.013, -0.013):
            OP.cyl(M @ T(x, -0.04, z) @ AX['Y'], 0.0055, 0.008, 'black', seg=14, bev=0.001)

def mirror(p, n):
    M = orient(p, n)
    mirror_head(M)
    post_stack(orient(p, V((n.x, n.y, 0)) if abs(n.z) < 0.99 else V((1, 0, 0))))

def lens(M, size=0.0127):
    OP.ring(M @ AX['Y'], size, size + 0.007, 0.009, 'black', seg=24)
    OP.cyl(M @ AX['Y'], size, 0.003, 'optic', seg=24)
    OP.cyl(M @ T(0, 0, size + 0.009), 0.002, 0.006, 'stainless', seg=8)
    post_stack(M, top=-(size + 0.004))

def waveplate(M):
    OP.ring(M @ AX['Y'], 0.011, 0.026, 0.013, 'black', seg=28)
    OP.ring(M @ T(0, -0.004, 0) @ AX['Y'], 0.0255, 0.027, 0.004, 'alu', seg=28)
    OP.cyl(M @ AX['Y'], 0.011, 0.002, 'optic', seg=20)
    OP.cyl(M @ T(0.024, 0, 0.012) @ AX['X'], 0.003, 0.012, 'stainless', seg=8)
    post_stack(M, top=-0.026)

def iris(M):
    OP.ring(M @ AX['Y'], 0.004, 0.022, 0.006, 'black', seg=24)
    OP.cyl(M @ T(0.016, 0, 0.016) @ R('Y', 45), 0.0015, 0.016, 'stainless', seg=6)
    post_stack(M, top=-0.022)

def pbs(M):
    OP.box(M, (0.0127, 0.0127, 0.0127), 'optic')
    OP.box(M @ T(0, 0, -0.0095), (0.03, 0.03, 0.006), 'black', bev=0.001)
    L = BH - 0.0125
    OP.cyl(M @ T(0, 0, -BH + L / 2), 0.012, L, 'black', seg=20)

def aom(M):
    OP.box(M, (0.035, 0.045, 0.026), 'alu', bev=0.0015)
    for sy in (-1, 1): OP.cyl(M @ T(0, sy * 0.0228, 0) @ AX['Y'], 0.004, 0.001, 'vent', seg=12)
    OP.cyl(M @ T(0.008, 0, 0.019), 0.003, 0.012, 'gold', seg=10)
    OP.box(M @ T(0, 0, -(BH + 0.013) / 2), (0.04, 0.05, BH - 0.013), 'black', bev=0.002)
    for sx in (-1, 1): OP.cyl(M @ T(sx * 0.024, 0.0, -BH + 0.025) @ AX['X'], 0.003, 0.012, 'stainless', seg=8)

def laser_head(M):
    OP.box(M @ T(0, -0.14, -BH + 0.045), (0.11, 0.28, 0.09), 'panel_grey', bev=0.004, seg=2)
    for i in range(9):
        OP.box(M @ T(-0.044 + i * 0.011, -0.15, -BH + 0.098), (0.003, 0.22, 0.016), 'alu')
    OP.cyl(M @ T(0, 0.005, 0) @ AX['Y'], 0.009, 0.012, 'black', seg=16)
    OP.box(M @ T(0, -0.14, -BH + 0.002), (0.13, 0.3, 0.004), 'black')
    OP.box(M @ T(0.0555, -0.12, -BH + 0.05), (0.001, 0.1, 0.035), 'logo_panel')
    OP.cyl(M @ T(0, -0.285, -BH + 0.04) @ AX['Y'], 0.008, 0.012, 'stainless', seg=12)
    return M @ V((0, -0.295, -BH + 0.04))

def fibre_coupler(M):
    OP.cyl(M @ T(0, -0.012, 0) @ AX['Y'], 0.0127, 0.03, 'black', seg=20, bev=0.001)
    OP.ring(M @ T(0, 0.004, 0) @ AX['Y'], 0.004, 0.014, 0.004, 'stainless_b', seg=20)
    OP.cyl(M @ T(0, -0.034, 0) @ AX['Y'], 0.0045, 0.016, 'alu', seg=12)
    OP.box(M @ T(0, -0.015, -0.014), (0.03, 0.03, 0.005), 'black')
    post_stack(M, top=-0.017)
    return M @ V((0, -0.044, 0))

def beam_dump(M):
    OP.cyl(M @ T(0, -0.012, 0) @ AX['Y'], 0.0127, 0.03, 'black', seg=20)
    for i in range(4): OP.ring(M @ T(0, -0.02 + i * 0.006, 0) @ AX['Y'], 0.0127, 0.016, 0.002, 'black', seg=20)
    post_stack(M, top=-0.014)

def beam(p0, p1, r=0.0011):
    BM.seg(p0, p1, r, 'beam', seg=8)

COMPS = {'lens': lens, 'wp': waveplate, 'iris': iris, 'pbs': pbs, 'aom': aom, 'dump': beam_dump}

def beam_path(pts, comps=(), start='laser', end='coupler', branch=()):
    pts = [V((x, y, BZ)) for x, y in pts]
    for i in range(len(pts) - 1): beam(pts[i], pts[i + 1])
    for i in range(1, len(pts) - 1):
        din = (pts[i] - pts[i - 1]).normalized(); dout = (pts[i + 1] - pts[i]).normalized()
        mirror(pts[i], (dout - din).normalized())
    for si, t, kind in comps:
        a, b = pts[si], pts[si + 1]; d = (b - a).normalized()
        COMPS[kind](orient(a.lerp(b, t), d))
    d0 = (pts[1] - pts[0]).normalized()
    if start == 'laser':
        tail = laser_head(orient(pts[0], d0))
        FIB.append(('elec', tail, -d0))
    elif start == 'coupler':
        FIB.append(('fibre', fibre_coupler(orient(pts[0], d0)), -d0))
    de = (pts[-1] - pts[-2]).normalized()
    if end == 'coupler':
        FIB.append(('fibre', fibre_coupler(orient(pts[-1], -de)), de))
    elif end == 'dump':
        beam_dump(orient(pts[-1], -de))
    for si, t, side, L in branch:   # PBS side outputs into dumps
        a, b = pts[si], pts[si + 1]; d = (b - a).normalized()
        p = a.lerp(b, t); dd = V((-d.y, d.x, 0)) * side
        beam(p, p + dd * L); beam_dump(orient(p + dd * L, -dd))

def periscope(p, din, H, dout):
    p0 = V((p[0], p[1], BZ)); p1 = V((p[0], p[1], H)); up = V((0, 0, 1))
    beam(p0, p1)
    mirror_head(orient(p0, (up - din).normalized()))
    mirror_head(orient(p1, (dout - up).normalized()))
    back = (din - dout).normalized() * 0.045
    pp = V((p[0], p[1], 0)) + back
    OP.cyl(T(pp.x, pp.y, (TT + H + 0.04) / 2), 0.0127, H + 0.04 - TT, 'stainless', seg=20)
    OP.box(T(pp.x, pp.y, TT + 0.005), (0.07, 0.07, 0.01), 'black', bev=0.002)
    for q, z in ((p0, BZ), (p1, H)):
        OP.seg(V((pp.x, pp.y, z)), V((q.x, q.y, z)) + (pp - V((q.x, q.y, 0))).normalized() * 0.02, 0.008, 'black', seg=12)
        OP.box(T(pp.x, pp.y, z), (0.032, 0.032, 0.03), 'black', bev=0.002)

def build_optics():
    global OP, BM
    OP = MB("NA_Optics", "NAQC_Table_Optics")
    BM = MB("NA_Laser_Beams", "NAQC_Beams")
    # A: tweezer line -> periscope -> objective
    beam_path([(-1.15, 0.40), (-0.30, 0.40), (-0.30, 0.55), (0.35, 0.55)],
              comps=[(0, 0.22, 'aom'), (0, 0.4, 'lens'), (0, 0.55, 'wp'), (0, 0.75, 'iris'),
                     (1, 0.5, 'iris'), (2, 0.25, 'lens'), (2, 0.6, 'lens'), (2, 0.82, 'wp')],
              start='laser', end=None)
    periscope((0.35, 0.55), V((1, 0, 0)), C.z, V((0, -1, 0)))
    beam(V((0.35, 0.55, C.z)), V((0.35, 0.425, C.z)))  # stops at the dichroic (keeps the array clean)
    # C: front-left line under the breadboard -> fibre coupler
    beam_path([(-1.15, -0.45), (-0.25, -0.45), (-0.25, -0.22), (0.08, -0.22)],
              comps=[(0, 0.3, 'aom'), (0, 0.48, 'wp'), (0, 0.62, 'pbs'), (0, 0.85, 'lens'),
                     (1, 0.5, 'iris'), (2, 0.35, 'wp'), (2, 0.65, 'lens')],
              start='laser', end='coupler', branch=[(0, 0.62, -1, 0.11)])
    # D: right line fed by fibre from the service cabinet -> fibre coupler
    beam_path([(1.24, -0.1), (0.98, -0.1), (0.98, -0.45), (1.22, -0.45)],
              comps=[(0, 0.4, 'wp'), (0, 0.72, 'pbs'), (1, 0.3, 'aom'), (1, 0.55, 'lens'), (1, 0.78, 'lens'), (2, 0.5, 'wp')],
              start='coupler', end='coupler', branch=[(0, 0.72, 1, 0.09)])
    # F: back-right laser module -> fibre coupler (feeds the MOT fibres)
    OP.boxp((0.88, 0.36, TT), (1.26, 0.56, TT + 0.11), 'panel_grey', bev=0.006, seg=2)
    OP.boxp((0.87, 0.35, TT + 0.11), (1.27, 0.57, TT + 0.12), 'alu', bev=0.003)
    for i in range(12):
        OP.boxp((0.9 + i * 0.03, 0.38, TT + 0.12), (0.912 + i * 0.03, 0.54, TT + 0.145), 'alu')
    OP.boxp((1.0, 0.3595, TT + 0.03), (1.18, 0.36, TT + 0.08), 'logo_panel')
    OP.cyl(T(0.88, 0.40, BZ) @ AX['X'], 0.009, 0.014, 'black', seg=16)
    FIB.append(('elec', V((1.26, 0.5, TT + 0.05)), V((1, 0, 0))))
    beam_path([(0.873, 0.40), (0.66, 0.40), (0.66, 0.22), (1.18, 0.22)],
              comps=[(0, 0.35, 'iris'), (0, 0.65, 'wp'), (1, 0.5, 'pbs'), (2, 0.2, 'aom'), (2, 0.42, 'lens'), (2, 0.6, 'lens'), (2, 0.8, 'wp')],
              start=None, end='coupler', branch=[(1, 0.5, 1, 0.09)])
    # photodiodes / wavemeter pick-off on the right front
    for (x, y) in ((1.1, -0.25), (1.17, -0.3)):
        M = orient(V((x, y, BZ)), V((-1, 0.3, 0)))
        OP.box(M, (0.03, 0.012, 0.035), 'black', bev=0.002)
        OP.cyl(M @ T(0, 0.007, 0) @ AX['Y'], 0.004, 0.003, 'vent', seg=12)
        post_stack(M, top=-0.017)
        FIB.append(('elec', M @ V((0, -0.01, 0)), V((0, 1, 0))))
    # E: short back-left diagnostic line
    beam_path([(-1.2, 0.12), (-0.7, 0.12), (-0.7, 0.24), (-0.45, 0.24)],
              comps=[(0, 0.5, 'lens'), (2, 0.5, 'wp')], start='coupler', end='dump')
    # tweezer imaging: dichroic cube, tube lens, camera
    q = V((C.x, 0.40, C.z))
    OP.box(T(*q), (0.05, 0.05, 0.05), 'black', bev=0.003)
    OP.box(T(*q) @ R('Z', 45), (0.045, 0.002, 0.045), 'optic')
    OP.seg(q + V((0.025, 0, 0)), q + V((0.13, 0, 0)), 0.016, 'black', seg=20)
    OP.box(T(q.x + 0.19, q.y, q.z), (0.11, 0.1, 0.1), 'panel_grey', bev=0.005, seg=2)
    for i in range(7):
        OP.box(T(q.x + 0.16 + i * 0.01, q.y, q.z + 0.055), (0.004, 0.09, 0.012), 'alu')
    OP.cyl(T(q.x + 0.25, q.y, q.z) @ AX['X'], 0.012, 0.012, 'stainless', seg=12)
    OP.boxp((q.x + 0.135, q.y - 0.04, TT), (q.x + 0.245, q.y + 0.04, q.z - 0.05), 'black', bev=0.003)
    OP.cyl(T(q.x, q.y, (TT + q.z - 0.025) / 2), 0.0127, q.z - 0.025 - TT, 'stainless', seg=16)
    OP.box(T(q.x, q.y, TT + 0.005), (0.06, 0.06, 0.01), 'black')
    OP.seg(V((C.x, 0.55, C.z)) + V((0, -0.01, 0)), q + V((0, 0.025, 0)), 0.014, 'black', seg=20)
    FIB.append(('elec', V((q.x + 0.26, q.y, q.z)), V((1, 0, 0))))

# ================================================================== VACUUM SYSTEM
def cf_flange(mb, M, r_tube, ro, th, bolts, m='stainless'):
    """Flange pair at local origin, axis +Z (outward)."""
    mb.ring(M @ T(0, 0, -th / 2), r_tube, ro, th, m, seg=36)
    mb.ring(M @ T(0, 0, th / 2 + 0.0005), r_tube * 0.6, ro, th, m, seg=36)
    br = (r_tube + ro) / 2 + 0.002
    for k in range(bolts):
        a = 2 * math.pi * (k + 0.5) / bolts
        x, y = br * math.cos(a), br * math.sin(a)
        mb.cyl(M @ T(x, y, th + 0.004), 0.0035, 0.007, 'stainless_b', seg=6)
        mb.cyl(M @ T(x, y, -th - 0.003), 0.004, 0.005, 'stainless_b', seg=6)

def port_axis(theta):
    return V((math.cos(math.radians(theta)), 0, math.sin(math.radians(theta))))

def build_vacuum():
    vc = MB("NA_Vacuum_Chamber", "NAQC_Vacuum")
    # spherical octagon body: octagon outer, circular bore along Y
    a = 0.11; Rc = a / math.cos(math.radians(22.5)); rb = 0.064; hy = 0.045; N = 32
    bm = vc.bm; n0 = len(bm.verts)
    def octp(t):  # point on octagon perimeter, t in [0,1)
        k = int(t * 8) % 8; f = t * 8 - int(t * 8)
        a0 = math.radians(22.5 + 45 * k); a1 = math.radians(22.5 + 45 * (k + 1))
        p0 = V((Rc * math.cos(a0), Rc * math.sin(a0))); p1 = V((Rc * math.cos(a1), Rc * math.sin(a1)))
        return p0.lerp(p1, f)
    rows = []
    for i in range(N):
        t = (i / N) + (0.5 / N) * 0  # 4 points per side
        po = octp(i / N); ang = 2 * math.pi * (i / N) + math.radians(22.5)
        pi_ = V((rb * math.cos(ang), rb * math.sin(ang)))
        # map 2D (x, z) with Y as bore axis
        rows.append([bm.verts.new((po.x, -hy, po.y)), bm.verts.new((po.x, hy, po.y)),
                     bm.verts.new((pi_.x, hy, pi_.y)), bm.verts.new((pi_.x, -hy, pi_.y))])
    for i in range(N):
        A, B = rows[i], rows[(i + 1) % N]
        for j in range(4):
            j2 = (j + 1) % 4
            bm.faces.new((A[j], A[j2], B[j2], B[j]))
    vs = vc._new(n0)
    bmesh.ops.recalc_face_normals(bm, faces=list({f for v in vs for f in v.link_faces}))
    vc._fin(vs, 'stainless', T(*C), smooth=False)
    # small tapped holes / engraved ring on front & back faces
    for sy in (-1, 1):
        for k in range(8):
            ang = math.radians(45 * k + 22.5)
            vc.cyl(T(C.x + 0.098 * math.cos(ang), C.y + sy * (hy + 0.0004), C.z + 0.098 * math.sin(ang)) @ AX['Y'],
                   0.0035, 0.001, 'vent', seg=10)
    # big front/back viewports (CF100-ish)
    for sy in (-1, 1):
        M = T(C.x, C.y + sy * (hy + 0.009), C.z) @ AX['Y'] @ (R('X', 180) if sy < 0 else Mx())
        vc.ring(M, 0.05, 0.076, 0.018, 'stainless', seg=48)
        vc.ring(M @ T(0, 0, 0.0095), 0.05, 0.056, 0.003, 'gold', seg=48)
        for k in range(16):
            ang = 2 * math.pi * (k + 0.5) / 16
            vc.cyl(M @ T(0.066 * math.cos(ang), 0.066 * math.sin(ang), 0.012), 0.0042, 0.007, 'stainless_b', seg=6)
        vc.cyl(M @ T(0, 0, 0.002), 0.0505, 0.006, 'viewport', seg=48)
    vc.done()
    # interior: 7x7 tweezer array facing the dive camera (match-cut to the atoms shot) + faint halo
    at = MB("NA_Atom_Array", "NAQC_Beams")
    n_at, pitch = 7, 0.0011
    for i in range(n_at):
        for j in range(n_at):
            if rng.random() < 0.12: continue   # a few empty sites, like a real loaded array
            at.sphere(T(C.x + (i - 3) * pitch, C.y, C.z + (j - 3) * pitch), 0.00022, 'atoms', seg=8)
    at.sphere(T(*C), 0.007, 'atoms_halo', seg=40)
    at.done()
    # empties for the shot
    for name, p in (("NAQC_Atoms", C), ("NAQC_DiveTarget", C + V((0, -hy - 0.02, 0)))):
        e = bpy.data.objects.new(name, None); COLL["NAQC_Helpers"].objects.link(e)
        e.location = p; e.parent = ROOT; e.empty_display_size = 0.05; e.empty_display_type = 'SPHERE'

    pt = MB("NA_Vacuum_Ports", "NAQC_Vacuum")
    def port(theta, length=0.065):
        d = port_axis(theta)
        M = orient(C, V((0, 1, 0))) if False else None
        Mz = (Mx.Translation(C) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4())
        pt.cyl(Mz @ T(0, 0, a + length / 2 - 0.006), 0.019, length, 'stainless', seg=28)
        pt.cyl(Mz @ T(0, 0, a - 0.004), 0.024, 0.008, 'stainless', seg=28)  # weld collar
        fl = Mz @ T(0, 0, a + length + 0.0065)
        cf_flange(pt, fl, 0.019, 0.035, 0.013, 6)
        return Mz, a + length + 0.0195
    ports = {}
    for th in (0, 45, 90, 135, 180, 225, 270, 315):
        ports[th] = port(th)
    # MOT collimators on the four diagonals, red beams into the centre
    for th in (45, 135, 225, 315):
        Mz, rr = ports[th]
        pt.cyl(Mz @ T(0, 0, rr + 0.002), 0.017, 0.004, 'viewport', seg=24)
        pt.cyl(Mz @ T(0, 0, rr + 0.03), 0.017, 0.05, 'black', seg=24, bev=0.002)
        pt.ring(Mz @ T(0, 0, rr + 0.012), 0.017, 0.021, 0.01, 'black', seg=24)
        pt.cyl(Mz @ T(0, 0, rr + 0.062), 0.006, 0.014, 'alu', seg=12)
        for k in range(3):
            ang = 2 * math.pi * k / 3
            pt.cyl(Mz @ T(0.019 * math.cos(ang), 0.019 * math.sin(ang), rr + 0.045), 0.0025, 0.03, 'stainless', seg=8)
        d = port_axis(th)
        # (MOT beams inside the bore left out on purpose: they read as a red "X" in the dive)
        FIB.append(('fibre', C + d * (rr + 0.07), d))
    # top: small monitor camera on viewport
    Mz, rr = ports[90]
    pt.cyl(Mz @ T(0, 0, rr + 0.003), 0.019, 0.004, 'viewport', seg=24)
    pt.cyl(Mz @ T(0, 0, rr + 0.03), 0.014, 0.05, 'black', seg=20)
    pt.box(Mz @ T(0, 0, rr + 0.09), (0.06, 0.06, 0.07), 'alu', bev=0.004, seg=2)
    pt.cyl(Mz @ T(0.015, 0.031, rr + 0.1) @ AX['Y'], 0.005, 0.008, 'gold', seg=10)
    FIB.append(('elec', Mz @ V((0.015, 0.036, rr + 0.1)), V((0, 1, 0))))
    # bottom: pedestal to table
    Mz, rr = ports[270]
    z_top = C.z - rr
    pt.cyl(T(C.x, C.y, (TT + z_top) / 2), 0.03, z_top - TT, 'stainless_b', seg=28)
    pt.box(T(C.x, C.y, TT + 0.008), (0.12, 0.12, 0.016), 'stainless_b', bev=0.003)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pt.cyl(T(C.x + sx * 0.045, C.y + sy * 0.045, TT + 0.019), 0.005, 0.006, 'stainless', seg=6)

    pt.done()

    # ---- magnetic coils (front & back)
    co = MB("NA_Coils", "NAQC_Vacuum")
    for sy in (-1, 1):
        y0 = C.y + sy * 0.068; y1 = C.y + sy * 0.104
        Mc = lambda y: T(C.x, y, C.z) @ AX['Y']
        co.ring(Mc(y0), 0.08, 0.142, 0.005, 'black', seg=64)          # inner former plate
        co.ring(Mc((y0 + y1) / 2), 0.08, 0.086, abs(y1 - y0), 'black', seg=64)
        co.ring(Mc(y1 + sy * 0.0035), 0.0845, 0.088, 0.003, 'peek', seg=64)  # epoxy edge
        for k in range(6):  # retaining clips over the exposed windings
            ang = math.radians(30 + 60 * k)
            co.box(T(C.x + 0.112 * math.cos(ang), y1 + sy * 0.002, C.z + 0.112 * math.sin(ang)) @ R('Y', -math.degrees(ang)),
                   (0.06, 0.004, 0.012), 'black', bev=0.0015)
        nt, nl = 8, 7
        for i in range(nt):
            y = y0 + (y1 - y0) * (i + 0.5) / nt
            for j in range(nl):
                co.torus(Mc(y), 0.089 + j * 0.0068, 0.0033, 'copper', seg=56, seg2=6)
        for k in (-1, 1):  # leads
            xx = C.x + k * 0.012
            co.seg(V((xx, (y0 + y1) / 2, C.z + 0.135)), V((xx, (y0 + y1) / 2, C.z + 0.2)), 0.003, 'copper', seg=8)
        # mounting brackets
        for ang in (30, 150):
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            co.box(T(C.x + 0.13 * ca, (y0 + y1) / 2 - sy * 0.025, C.z + 0.13 * sa) @ R('Y', -ang), (0.03, 0.08, 0.012), 'black', bev=0.002)

    # ---- objective behind the back window
    ob = co
    yb = C.y + hy + 0.018
    stack = [(0.0, 0.02, 0.022, 'black'), (0.02, 0.1, 0.032, 'black'), (0.06, 0.075, 0.0355, 'alu'),
             (0.1, 0.13, 0.03, 'black'), (0.13, 0.15, 0.024, 'stainless'), (0.15, 0.33, 0.017, 'black')]
    for y0_, y1_, r, m in stack:
        ob.cyl(T(C.x, yb + (y0_ + y1_) / 2, C.z) @ AX['Y'], r, y1_ - y0_, m, seg=40, bev=0.0015)
    ob.cyl(T(C.x, yb + 0.0005, C.z) @ AX['Y'], 0.012, 0.002, 'optic', seg=24)
    # XYZ stage under the objective
    sy_ = yb + 0.11
    ob.boxp((C.x - 0.05, sy_ - 0.04, TT), (C.x + 0.05, sy_ + 0.04, C.z - 0.08), 'black', bev=0.003)
    ob.boxp((C.x - 0.045, sy_ - 0.035, C.z - 0.08), (C.x + 0.045, sy_ + 0.035, C.z - 0.06), 'alu', bev=0.002)
    ob.boxp((C.x - 0.012, sy_ - 0.02, C.z - 0.06), (C.x + 0.012, sy_ + 0.02, C.z - 0.03), 'alu')
    for (dx, dy, ax) in ((0.06, 0, 'X'), (0, 0.05, 'Y')):
        ob.cyl(T(C.x + dx, sy_ + dy, C.z - 0.07) @ AX[ax], 0.005, 0.03, 'stainless', seg=12)
        ob.cyl(T(C.x + dx * 1.45, sy_ + dy * 1.6, C.z - 0.07) @ AX[ax], 0.009, 0.02, 'stainless_b', seg=16, bev=0.001)
    co.done()

    # ---- right arm: nipple, 6-way cross, ion pump, gate valve, TSP
    va = MB("NA_Vacuum_Pumps", "NAQC_Vacuum")
    x_fl = C.x + ports[0][1]; xc = 0.76
    va.seg(V((x_fl, 0, C.z)), V((xc - 0.06, 0, C.z)), 0.019, 'stainless', seg=28)
    cf_flange(va, T(xc - 0.066, 0, C.z) @ AX['X'], 0.019, 0.035, 0.013, 6)
    for ax in ('X', 'Y', 'Z'):
        va.cyl(T(xc, 0, C.z) @ AX[ax], 0.019, 0.12, 'stainless', seg=28)
    for d in ((1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        dv = V(d); Mz = Mx.Translation(V((xc, 0, C.z)) + dv * 0.0665) @ dv.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        cf_flange(va, Mz, 0.019, 0.035, 0.013, 6)
    # front viewport on the cross
    va.cyl(T(xc, -0.082, C.z) @ AX['Y'], 0.019, 0.004, 'viewport', seg=24)
    # ion pump (+Y)
    va.seg(V((xc, 0.08, C.z)), V((xc, 0.13, C.z)), 0.019, 'stainless', seg=24)
    va.boxp((xc - 0.07, 0.13, C.z - 0.08), (xc + 0.07, 0.29, C.z + 0.08), 'stainless_b', bev=0.006, seg=2)
    for sx in (-1, 1):
        va.boxp((xc + sx * 0.07, 0.14, C.z - 0.07), (xc + sx * 0.1, 0.28, C.z + 0.07), 'magnet', bev=0.005, seg=2)
    va.cyl(T(xc, 0.25, C.z + 0.1), 0.012, 0.04, 'ceramic', seg=20)
    va.cyl(T(xc, 0.25, C.z + 0.13), 0.016, 0.025, 'stainless', seg=20)
    FIB.append(('elec', V((xc, 0.25, C.z + 0.145)), V((0, 0, 1))))
    for i in range(6):
        va.boxp((xc - 0.065 + i * 0.026, 0.292, C.z - 0.07), (xc - 0.055 + i * 0.026, 0.296, C.z + 0.07), 'stainless')
    # gate valve (+Z) and ion gauge
    z0 = C.z + 0.08
    va.boxp((xc - 0.05, -0.04, z0), (xc + 0.05, 0.04, z0 + 0.06), 'stainless_b', bev=0.004, seg=2)
    va.boxp((xc - 0.03, -0.03, z0 + 0.06), (xc + 0.12, 0.03, z0 + 0.04 + 0.04), 'stainless_b', bev=0.003)
    va.cyl(T(xc + 0.14, 0, z0 + 0.06) @ AX['X'], 0.006, 0.04, 'stainless', seg=12)
    va.torus(T(xc + 0.165, 0, z0 + 0.06) @ AX['X'], 0.03, 0.005, 'red_plastic', seg=32, seg2=8)
    for k in range(4):
        va.box(T(xc + 0.165, 0, z0 + 0.06) @ R('X', k * 45), (0.005, 0.06, 0.004), 'red_plastic')
    va.cyl(T(xc, 0, z0 + 0.075), 0.019, 0.03, 'stainless', seg=24)
    cf_flange(va, T(xc, 0, z0 + 0.095), 0.019, 0.035, 0.013, 6)
    va.cyl(T(xc, 0, z0 + 0.15), 0.013, 0.08, 'viewport', seg=24)
    va.cyl(T(xc, 0, z0 + 0.195), 0.016, 0.012, 'black', seg=20)
    va.cyl(T(xc, 0, z0 + 0.21), 0.008, 0.02, 'ceramic', seg=16)
    FIB.append(('elec', V((xc, 0, z0 + 0.22)), V((0, 0, 1))))
    # TSP (+X)
    va.seg(V((xc + 0.08, 0, C.z)), V((xc + 0.17, 0, C.z)), 0.019, 'stainless', seg=24)
    cf_flange(va, T(xc + 0.176, 0, C.z) @ AX['X'], 0.019, 0.035, 0.013, 6)
    va.cyl(T(xc + 0.2, 0, C.z) @ AX['X'], 0.024, 0.03, 'ceramic', seg=24)
    for k in range(3):
        ang = 2 * math.pi * k / 3
        va.cyl(T(xc + 0.225, 0.012 * math.cos(ang), C.z + 0.012 * math.sin(ang)) @ AX['X'], 0.003, 0.02, 'gold', seg=8)
    # support post under the cross
    va.cyl(T(xc, 0, (TT + C.z - 0.08) / 2), 0.0127, C.z - 0.08 - TT, 'stainless', seg=20)
    va.boxp((xc - 0.04, -0.04, TT), (xc + 0.04, 0.04, TT + 0.012), 'black', bev=0.002)
    va.boxp((xc - 0.03, -0.012, C.z - 0.09), (xc + 0.03, 0.012, C.z - 0.065), 'black', bev=0.002)

    # ---- left arm: Zeeman slower + oven
    x_fl = C.x - ports[180][1]
    x_z1 = x_fl - 0.03; x_z0 = -0.30
    va.seg(V((x_fl, 0, C.z)), V((x_z0 - 0.04, 0, C.z)), 0.012, 'stainless', seg=24)
    nseg = 12
    for i in range(nseg):
        xa = x_z0 + (x_z1 - x_z0) * i / nseg; xb = x_z0 + (x_z1 - x_z0) * (i + 1) / nseg
        rr = 0.055 - 0.028 * (i / (nseg - 1)) ** 0.7
        va.cyl(T((xa + xb) / 2, 0, C.z) @ AX['X'], rr - 0.003, (xb - xa) * 0.96, 'copper', seg=40)
        for k in range(4):
            va.torus(T(xa + (xb - xa) * (k + 0.5) / 4, 0, C.z) @ AX['X'], rr - 0.003, 0.0028, 'copper', seg=40, seg2=6)
    for x in (x_z0 - 0.004, x_z1 + 0.004):
        va.cyl(T(x, 0, C.z) @ AX['X'], 0.06, 0.006, 'black', seg=40, bev=0.001)
    # Zeeman supports
    for x in (x_z0 + 0.06, x_z1 - 0.08):
        va.cyl(T(x, 0, (TT + C.z - 0.06) / 2), 0.0127, C.z - 0.06 - TT, 'stainless', seg=16)
        va.boxp((x - 0.03, -0.03, TT), (x + 0.03, 0.03, TT + 0.01), 'black', bev=0.002)
        va.boxp((x - 0.015, -0.03, C.z - 0.075), (x + 0.015, 0.03, C.z - 0.05), 'black', bev=0.002)
    # oven cross
    xo = x_z0 - 0.1
    cf_flange(va, T(x_z0 - 0.046, 0, C.z) @ AX['X'], 0.019, 0.035, 0.013, 6)
    for ax in ('X', 'Y', 'Z'):
        va.cyl(T(xo, 0, C.z) @ AX[ax], 0.019, 0.1, 'stainless', seg=24)
    for d in ((-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)):
        dv = V(d); Mz = Mx.Translation(V((xo, 0, C.z)) + dv * 0.0565) @ dv.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        cf_flange(va, Mz, 0.019, 0.035, 0.013, 6)
    va.cyl(T(xo, -0.072, C.z) @ AX['Y'], 0.019, 0.004, 'viewport', seg=24)
    # oven body with heater tape and thermocouple
    va.cyl(T(xo - 0.12, 0, C.z) @ AX['X'], 0.022, 0.1, 'stainless', seg=28)
    for k in range(5):
        va.cyl(T(xo - 0.08 - k * 0.019, 0, C.z) @ AX['X'], 0.025, 0.012, 'kapton', seg=28)
    va.cyl(T(xo - 0.175, 0, C.z) @ AX['X'], 0.028, 0.01, 'stainless_b', seg=28)
    va.ring(T(xo - 0.13, 0, C.z) @ AX['X'], 0.025, 0.029, 0.006, 'stainless_b', seg=28)
    FIB.append(('elec', V((xo - 0.18, 0, C.z)), V((-1, 0, 0))))
    # small ion pump on oven (+Y)
    va.seg(V((xo, 0.07, C.z)), V((xo, 0.1, C.z)), 0.019, 'stainless', seg=20)
    va.boxp((xo - 0.05, 0.1, C.z - 0.055), (xo + 0.05, 0.2, C.z + 0.055), 'stainless_b', bev=0.005, seg=2)
    for sx in (-1, 1):
        va.boxp((xo + sx * 0.05, 0.11, C.z - 0.045), (xo + sx * 0.07, 0.19, C.z + 0.045), 'magnet', bev=0.004)
    va.cyl(T(xo, 0.17, C.z + 0.07), 0.01, 0.03, 'ceramic', seg=16)
    # angle valve (+Z)
    va.cyl(T(xo, 0, C.z + 0.09), 0.019, 0.04, 'stainless', seg=24)
    va.boxp((xo - 0.03, -0.03, C.z + 0.11), (xo + 0.03, 0.03, C.z + 0.17), 'stainless_b', bev=0.004)
    va.cyl(T(xo, 0, C.z + 0.19), 0.006, 0.04, 'stainless', seg=12)
    va.torus(T(xo, 0, C.z + 0.215), 0.025, 0.005, 'red_plastic', seg=28, seg2=8)
    va.cyl(T(xo - 0.12, 0, (TT + C.z - 0.03) / 2), 0.0127, C.z - 0.03 - TT, 'stainless', seg=16)
    va.boxp((xo - 0.15, -0.03, TT), (xo - 0.09, 0.03, TT + 0.01), 'black', bev=0.002)
    va.done()

# ================================================================== CABLES & FIBRES
def build_cables():
    fib, ele = [], []
    cab_exit = V((W2 + 0.34, D2 - 0.2, CZ + 0.015))
    rack_exit = V((-W2 - 0.345, D2 - 0.18, 2.262))
    duct_r = V((1.25, D2 - 0.06, HZ - 0.1)); duct_l = V((-1.25, D2 - 0.06, HZ - 0.1))
    lane = {'fibre': 0, 'elec': 0}
    for kind, p, d in FIB:
        p = V(p); d = V(d)
        lane[kind] += 1; L = lane[kind]
        ly = D2 - 0.11 - (L % 6) * 0.007            # cable lane along the back of the table
        tz = TT + 0.004 + (L % 3) * 0.003
        dx = 1.25 if kind == 'fibre' else -1.25     # fibres -> right duct, electrical -> left duct
        dxo = dx + ((L % 5) - 2) * 0.008
        exitp = cab_exit if kind == 'fibre' else rack_exit
        top = [V((dxo, D2 - 0.07, HZ - 0.13)), V((dxo + (0.06 if dx > 0 else -0.06), D2 - 0.12, HZ - 0.09)),
               V((dx + (0.15 if dx > 0 else -0.15), D2 - 0.2, CZ + 0.12)) + V((0, 0, (L % 4) * 0.01))]
        if p.z > 1.28:   # high devices: straight back to the overhead tray
            via = [p + d * 0.12 + V((0, 0, 0.08)), V((p.x, D2 - 0.12, HZ - 0.1)), V((dx * 0.9, D2 - 0.12, HZ - 0.1))] + top[1:]
        else:            # drop to the table, run back along the lane, up the duct
            q = p + V((d.x, d.y, 0)) * 0.1
            via = [V((q.x, q.y, tz + 0.02)), V((q.x, (q.y + ly) / 2, tz)), V((q.x + (dx - q.x) * 0.15, ly, tz)),
                   V((dxo - (0.1 if dx > 0 else -0.1), ly, tz)), V((dxo, D2 - 0.07, TT + 0.12))] + top
        pts = route(p, d, exitp, (0, 0, 1), via=via, lead=0.05)
        (fib if kind == 'fibre' else ele).append((pts, 1.0))
    # bundles on top of the crown
    for i in range(6):
        o = V((0, rng.uniform(-0.03, 0.03), rng.uniform(0, 0.02)))
        ele.append(([rack_exit + o, rack_exit + V((0.05, 0, 0.15)) + o, V((-W2 + 0.1, D2 - 0.15, CZ + 0.03)) + o,
                     V((-0.2, D2 - 0.12, CZ + 0.03)) + o, V((0.2, D2 - 0.12, CZ + 0.03)) + o,
                     V((W2 - 0.1, D2 - 0.15, CZ + 0.03)) + o, cab_exit + V((-0.05, 0, 0.12)) + o, cab_exit + o], 1.6))
    curves("NA_Fibres", "NAQC_Cables", fib, 0.0016, 'fibre')
    curves("NA_Cables", "NAQC_Cables", ele, 0.0035, 'rubber')
    # MOT fibres hang from the collimators into the tray via the coax curves: collimator tails
    # Coil leads to rack
    lead = []
    for sy in (-1, 1):
        y = C.y + sy * 0.086
        for k in (-1, 1):
            p = V((C.x + k * 0.012, y, C.z + 0.2))
            lead.append((route(p, (0, 0, 1), V((-1.25 + k * 0.01, D2 - 0.09, HZ - 0.15)), (0, -1, 0),
                               via=[p + V((0, 0.1 * sy, 0.25)), V((0.0, 0.5, HZ - 0.25))]), 1.0))
    curves("NA_Coil_Leads", "NAQC_Cables", lead, 0.004, 'cable_grey')

# ------------------------------------------------------------------ build
build_enclosure()
build_rack()
build_service_cabinet()
build_table()
build_optics()
build_vacuum()
OP.done(); BM.done()
build_cables()
for ob in COLL["NAQC_Beams"].objects:
    ob.visible_shadow = False
print("NAQC objects:", len(root_coll.all_objects),
      "verts:", sum(len(o.data.vertices) for o in root_coll.all_objects if o.type == 'MESH'))
if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
print("BUILT OK")
