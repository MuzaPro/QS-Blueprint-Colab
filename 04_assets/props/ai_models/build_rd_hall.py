"""Industrial R&D hall that replaces 'Walls and cieling' in the SH_1 shot.

Run:  blender -b --factory-startup --python build_rd_hall.py
Writes 04_assets/props/ai_models/rd_hall.blend. Built directly in SH_1 world
coordinates (append with no transform): floor z = -1.24, same footprint as the old
room, front (-Y) left open for the camera. Objects RDH_*, collection RD_Hall,
parented to empty RDH_root at the origin. No floor (the shot keeps its own).
Light fixtures are mostly off; a few are dim. Exit signs are green, no cyan.
"""
import bpy, bmesh, math, random
from mathutils import Vector as V, Matrix as Mx

SAVE = globals().get("SAVE", True)
DIR = r"C:\Users\mrgav\Documents\GitHub\QS-Blueprint-Colab\04_assets\props\ai_models"
OUT = globals().get("OUT", DIR + r"\rd_hall.blend")
rng = random.Random(5)
if not globals().get("NO_RESET"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.render.fps = 25

F = -1.24                      # floor
X0, X1, Y0, Y1 = -30.65, 39.92, -22.9, 47.6
EAVE = F + 8.0                 # truss bottom chord
TOP = F + 9.4                  # truss top chord
ROOF = TOP + 0.25

# ------------------------------------------------------------------ materials
MAT = {}
def mat(key, col, metal=0.0, rough=0.5, emit=None, estr=0.0, trans=0.0):
    m = bpy.data.materials.new("RDH_" + key); p = m.node_tree.nodes["Principled BSDF"]
    p.inputs['Base Color'].default_value = (*col, 1); p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough; p.inputs['Transmission Weight'].default_value = trans
    if emit:
        p.inputs['Emission Color'].default_value = (*emit, 1); p.inputs['Emission Strength'].default_value = estr
    m.diffuse_color = (*(emit or col), 1); MAT[key] = m; return m
mat('steel', (0.12, 0.122, 0.125), 0.3, 0.5)
mat('wall', (0.11, 0.112, 0.115), 0.2, 0.55)
mat('seam', (0.03, 0.03, 0.032), 0.0, 0.7)
mat('concrete', (0.16, 0.155, 0.15), 0.0, 0.9)
mat('galv', (0.42, 0.43, 0.44), 1.0, 0.45)
mat('deck', (0.3, 0.305, 0.31), 0.7, 0.55)
mat('red', (0.38, 0.02, 0.02), 0.0, 0.45)
mat('cabinet', (0.36, 0.37, 0.36), 0.2, 0.45)
mat('door', (0.18, 0.19, 0.2), 0.3, 0.45)
mat('black', (0.015, 0.015, 0.017), 0.3, 0.5)
mat('rubber', (0.02, 0.02, 0.022), 0.0, 0.65)
mat('glass_dark', (0.05, 0.055, 0.06), 0.0, 0.05, trans=0.0)
mat('lens_off', (0.55, 0.55, 0.53), 0.0, 0.35)
mat('lens_dim', (1.0, 0.95, 0.86), emit=(1.0, 0.95, 0.86), estr=4.0)
mat('exit', (0.1, 0.85, 0.3), emit=(0.1, 0.85, 0.3), estr=5.0)
mat('emerg', (0.9, 0.9, 0.85), emit=(0.9, 0.9, 0.85), estr=1.5)
mat('led_red', (1.0, 0.03, 0.0), emit=(1.0, 0.03, 0.0), estr=6.0)
mat('led_green', (0.2, 1.0, 0.1), emit=(0.2, 1.0, 0.1), estr=6.0)
mat('white', (0.75, 0.75, 0.72), 0.0, 0.6)

def hazard():
    """Yellow/black diagonal stripes for column guards."""
    m = mat('hazard', (0.85, 0.6, 0.02), 0.0, 0.5)
    nt = m.node_tree; N = nt.nodes; p = N["Principled BSDF"]
    tc = N.new('ShaderNodeTexCoord'); wv = N.new('ShaderNodeTexWave')
    wv.wave_type = 'BANDS'; wv.bands_direction = 'DIAGONAL'; wv.wave_profile = 'SIN'
    wv.inputs['Scale'].default_value = 2.5
    nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.48; mr.inputs['From Max'].default_value = 0.52
    nt.links.new(wv.outputs['Fac'] if 'Fac' in wv.outputs else wv.outputs[1], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], mx.inputs[0])
    mx.inputs[6].default_value = (0.85, 0.6, 0.02, 1); mx.inputs[7].default_value = (0.015, 0.015, 0.015, 1)
    nt.links.new(mx.outputs[2], p.inputs['Base Color'])
hazard()

# ------------------------------------------------------------------ collection + builder
COLL = bpy.data.collections.new("RD_Hall"); sc.collection.children.link(COLL)
ROOT = bpy.data.objects.new("RDH_root", None); COLL.objects.link(ROOT)

def T(x, y, z): return Mx.Translation((x, y, z))
def R(axis, deg): return Mx.Rotation(math.radians(deg), 4, axis)
AX = {'X': R('Y', 90), 'Y': R('X', -90), 'Z': Mx()}

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
    def boxp(s, p0, p1, m):
        c = [(a + b) / 2 for a, b in zip(p0, p1)]; sz = [max(abs(b - a), 1e-4) for a, b in zip(p0, p1)]
        s.box(T(*c), sz, m)
    def cyl(s, Mt, r, h, m, seg=16):
        v = [(r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z) for z in (-h / 2, h / 2) for k in range(seg)]
        f = [tuple(range(seg))[::-1], tuple(range(seg, 2 * seg))] + [(k, (k + 1) % seg, seg + (k + 1) % seg, seg + k) for k in range(seg)]
        s.add(v, f, m, Mt, smooth=True)
    def seg(s, p0, p1, r, m, seg=12):
        p0, p1 = V(p0), V(p1); d = p1 - p0
        Mt = Mx.Translation((p0 + p1) / 2) @ d.normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()
        s.cyl(Mt, r, d.length, m, seg)
    def segbox(s, p0, p1, w, h, m):
        p0, p1 = V(p0), V(p1); d = p1 - p0
        Mt = Mx.Translation((p0 + p1) / 2) @ d.normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()
        s.box(Mt, (w, h, d.length), m)
    def torus(s, Mt, Rr, r, m, seg=32, seg2=6):
        v = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            for j in range(seg2):
                b = 2 * math.pi * j / seg2; rr = Rr + r * math.cos(b)
                v.append((rr * math.cos(a), rr * math.sin(a), r * math.sin(b)))
        f = [(k * seg2 + j, ((k + 1) % seg) * seg2 + j, ((k + 1) % seg) * seg2 + (j + 1) % seg2, k * seg2 + (j + 1) % seg2)
             for k in range(seg) for j in range(seg2)]
        s.add(v, f, m, Mt, smooth=True)
    def done(s):
        me = bpy.data.meshes.new(s.name)
        for m in s.mats: me.materials.append(m)
        s.bm.normal_update(); s.bm.to_mesh(me); s.bm.free()
        me.set_sharp_from_angle(angle=math.radians(35))
        ob = bpy.data.objects.new(s.name, me); COLL.objects.link(ob); ob.parent = ROOT
        return ob

def ibeam(mb, p0, p1, h=0.3, b=0.3, tf=0.016, tw=0.01, web_axis='X', m='steel'):
    """I-section between p0, p1 (axis-aligned). web_axis: direction the web spans."""
    p0, p1 = V(p0), V(p1); L = p1 - p0; ax = max(range(3), key=lambda i: abs(L[i]))
    c = (p0 + p1) / 2; ln = abs(L[ax])
    wa = 'XYZ'.index(web_axis)
    fa = [i for i in range(3) if i not in (ax, wa)][0]   # flange width axis
    def sz(a_len, w_len, f_len):
        s_ = [0, 0, 0]; s_[ax] = a_len; s_[wa] = w_len; s_[fa] = f_len; return s_
    mb.box(T(*c), sz(ln, h - 2 * tf, tw), MAT[m])
    for sgn in (-1, 1):
        cc = c.copy(); cc[wa] += sgn * (h / 2 - tf / 2)
        mb.box(T(*cc), sz(ln, tf, b), MAT[m])

# ------------------------------------------------------------------ grid
YS = [Y0 + 0.6 + k * 7.0 for k in range(11) if Y0 + 0.6 + k * 7.0 < Y1 - 0.5]   # truss / column lines
XS = [X0 + 0.35 + k * 7.0 for k in range(11) if X0 + 0.35 + k * 7.0 < X1 - 0.5]
print("grid", len(YS), "truss lines,", len(XS), "back columns")

# ================================================================== walls
def build_walls():
    w = MB("RDH_Walls")
    t = 0.2
    # side walls and back wall (inner face at X0, X1, Y1)
    w.boxp((X0 - t, Y0, F), (X0, Y1 + t, ROOF + 0.3), MAT['wall'])
    w.boxp((X1, Y0, F), (X1 + t, Y1 + t, ROOF + 0.3), MAT['wall'])
    w.boxp((X0 - t, Y1, F), (X1 + t, Y1 + t, ROOF + 0.3), MAT['wall'])
    # concrete upstand
    up = 0.45
    w.boxp((X0, Y0, F), (X0 + 0.08, Y1, F + up), MAT['concrete'])
    w.boxp((X1 - 0.08, Y0, F), (X1, Y1, F + up), MAT['concrete'])
    w.boxp((X0, Y1 - 0.08, F), (X1, Y1, F + up), MAT['concrete'])
    # vertical panel seams every 1.0 m, horizontal joints at 4 m and 7.5 m
    for y in [Y0 + 0.5 + i for i in range(int(Y1 - Y0))]:
        for x, d in ((X0, 1), (X1, -1)):
            w.boxp((x, y - 0.006, F + up), (x + d * 0.006, y + 0.006, ROOF), MAT['seam'])
    for x in [X0 + 0.5 + i for i in range(int(X1 - X0))]:
        w.boxp((x - 0.006, Y1 - 0.006, F + up), (x + 0.006, Y1, ROOF), MAT['seam'])
    for z in (F + 4.0, F + 7.5):
        for x, d in ((X0, 1), (X1, -1)):
            w.boxp((x, Y0, z - 0.01), (x + d * 0.012, Y1, z + 0.01), MAT['seam'])
        w.boxp((X0, Y1 - 0.012, z - 0.01), (X1, Y1, z + 0.01), MAT['seam'])
    w.done()

# ================================================================== structure
def build_structure():
    st = MB("RDH_Steel")
    gd = MB("RDH_Column_Guards")
    def column(x, y, web):
        ibeam(st, (x, y, F), (x, y, TOP), web_axis=web)
        st.box(T(x, y, F + 0.01), (0.45, 0.45, 0.02), MAT['steel'])
        for sx in (-1, 1):
            for sy in (-1, 1):
                st.cyl(T(x + sx * 0.17, y + sy * 0.17, F + 0.035), 0.012, 0.03, MAT['galv'], 6)
        if rng.random() < 0.6:   # bolted-on impact guard with hazard stripes
            gd.boxp((x - 0.24, y - 0.24, F), (x + 0.24, y + 0.24, F + 1.0), MAT['hazard'])
    for y in YS:
        column(X0 + 0.35, y, 'X'); column(X1 - 0.35, y, 'X')
    for x in XS[1:-1]:
        column(x, Y1 - 0.35, 'Y')
    # trusses spanning X on every column line
    for y in YS:
        xa, xb = X0 + 0.35, X1 - 0.35
        ibeam(st, (xa, y, TOP), (xb, y, TOP), h=0.2, b=0.18, web_axis='Z')
        ibeam(st, (xa, y, EAVE + 0.1), (xb, y, EAVE + 0.1), h=0.2, b=0.18, web_axis='Z')
        n = int((xb - xa) / 2.0); dx = (xb - xa) / n
        for i in range(n + 1):
            x = xa + i * dx
            st.segbox((x, y, EAVE + 0.2), (x, y, TOP - 0.1), 0.1, 0.08, MAT['steel'])
            if i < n:
                a, b = (x, EAVE + 0.2), (x + dx, TOP - 0.1)
                if i % 2: a, b = (x, TOP - 0.1), (x + dx, EAVE + 0.2)
                st.segbox((a[0], y, a[1]), (b[0], y, b[1]), 0.09, 0.07, MAT['steel'])
                st.box(T(x + dx / 2, y, TOP - 0.02) @ R('Y', 0), (0.25, 0.012, 0.18), MAT['steel'])  # gusset
    # eave beams along the side walls and back
    for x in (X0 + 0.35, X1 - 0.35):
        ibeam(st, (x, Y0, TOP), (x, Y1, TOP), h=0.25, b=0.15, web_axis='Z')
    ibeam(st, (X0, Y1 - 0.35, TOP), (X1, Y1 - 0.35, TOP), h=0.25, b=0.15, web_axis='Z')
    # purlins along Y every 2.5 m, sitting on the top chords
    xp = X0 + 1.2
    while xp < X1 - 1.0:
        ibeam(st, (xp, Y0, TOP + 0.2), (xp, Y1, TOP + 0.2), h=0.16, b=0.07, web_axis='Z')
        xp += 2.5
    # X-bracing in the end bays of the side walls
    for x in (X0 + 0.25, X1 - 0.25):
        for (ya, yb) in ((YS[0], YS[1]), (YS[-2], YS[-1])):
            st.seg((x, ya, F + 1.0), (x, yb, TOP - 0.3), 0.02, MAT['steel'], 8)
            st.seg((x, yb, F + 1.0), (x, ya, TOP - 0.3), 0.02, MAT['steel'], 8)
    st.done(); gd.done()
    # corrugated roof deck (ribs run along Y)
    rd = MB("RDH_Roof_Deck")
    prof = []
    p = 0.2; x = X0
    while x < X1:
        prof += [(x, 0.0), (x + 0.05, 0.0), (x + 0.08, 0.045), (x + 0.15, 0.045), (x + 0.18, 0.0)]
        x += p
    nx = len(prof)
    verts = [(px, Y0, ROOF + pz) for px, pz in prof] + [(px, Y1, ROOF + pz) for px, pz in prof]
    faces = [(i + 1, i, nx + i, nx + i + 1) for i in range(nx - 1)]
    rd.add(verts, faces, MAT['deck'])
    rd.done()

# ================================================================== services
def build_services():
    sv = MB("RDH_Services")
    # cable ladders along Y, hung from the trusses on threaded rods
    zt = F + 5.4
    for xl in (-8.0, 13.0, 30.0):
        for sx in (-1, 1):
            sv.boxp((xl + sx * 0.3 - 0.01, Y0 + 1, zt), (xl + sx * 0.3 + 0.01, Y1 - 1, zt + 0.1), MAT['galv'])
        y = Y0 + 1.15
        while y < Y1 - 1:
            sv.boxp((xl - 0.3, y - 0.012, zt), (xl + 0.3, y + 0.012, zt + 0.02), MAT['galv']); y += 0.3
        for k in range(rng.randint(4, 7)):   # cables lying on the ladder
            xo = xl + rng.uniform(-0.24, 0.24); r = rng.uniform(0.012, 0.03)
            sv.seg((xo, Y0 + 1, zt + 0.02 + r), (xo, Y1 - 1, zt + 0.02 + r), r, MAT['rubber' if k % 3 else 'black'], 8)
        for y in YS:
            for sx in (-1, 1):
                sv.seg((xl + sx * 0.33, y, zt - 0.05), (xl + sx * 0.33, y, EAVE + 0.1), 0.006, MAT['galv'], 6)
            sv.boxp((xl - 0.36, y - 0.02, zt - 0.06), (xl + 0.36, y + 0.02, zt - 0.02), MAT['galv'])
    # spiral ducts with seams, straps and diffusers
    zd = F + 6.4
    for xd in (2.0, 21.0):
        sv.seg((xd, Y0 + 0.5, zd), (xd, Y1 - 0.5, zd), 0.45, MAT['galv'], 40)
        y = Y0 + 0.8
        while y < Y1 - 0.5:
            sv.torus(T(xd, y, zd) @ AX['Y'], 0.452, 0.006, MAT['galv'], 40, 4); y += 0.6
        for y in YS:
            sv.torus(T(xd, y + 0.4, zd) @ AX['Y'], 0.47, 0.012, MAT['steel'], 40, 4)
            for sx in (-1, 1):
                sv.seg((xd + sx * 0.47, y + 0.4, zd), (xd + sx * 0.47, y + 0.4, EAVE + 0.1), 0.006, MAT['galv'], 6)
            # diffuser drop
            sv.seg((xd, y + 3.5, zd - 0.45), (xd, y + 3.5, zd - 0.9), 0.15, MAT['galv'], 20)
            sv.boxp((xd - 0.3, y + 3.2, zd - 0.98), (xd + 0.3, y + 3.8, zd - 0.9), MAT['galv'])
            for i in range(5):
                sv.boxp((xd - 0.27, y + 3.25 + i * 0.12, zd - 0.985), (xd + 0.27, y + 3.28 + i * 0.12, zd - 0.98), MAT['black'])
    # red sprinkler mains with drop heads
    zs = EAVE - 0.15
    for xs in (-15.0, 6.0, 27.0):
        sv.seg((xs, Y0 + 0.5, zs), (xs, Y1 - 0.5, zs), 0.05, MAT['red'], 12)
        y = Y0 + 2
        while y < Y1 - 1:
            for sx in (-1, 1):
                xx = xs + sx * 1.8
                sv.seg((xs, y, zs), (xx, y, zs), 0.02, MAT['red'], 8)
                sv.seg((xx, y, zs), (xx, y, zs - 0.25), 0.015, MAT['red'], 8)
                sv.cyl(T(xx, y, zs - 0.27), 0.03, 0.02, MAT['galv'], 10)
            y += 3.5
        for y in YS:
            sv.seg((xs, y, zs), (xs, y, EAVE + 0.1), 0.006, MAT['galv'], 6)
    sv.done()
    # high-bay linear fixtures under the trusses: most off, a few dim
    lt = MB("RDH_Light_Fixtures")
    zl = EAVE - 0.9
    for y in YS:
        for x in XS[1:-1] + [X1 - 3.5]:
            on = rng.random() < 0.3
            lt.boxp((x - 0.7, y - 0.13, zl), (x + 0.7, y + 0.13, zl + 0.09), MAT['galv'])
            lt.boxp((x - 0.66, y - 0.1, zl - 0.005), (x + 0.66, y + 0.1, zl), MAT['lens_dim' if on else 'lens_off'])
            for sx in (-1, 1):
                lt.seg((x + sx * 0.6, y, zl + 0.09), (x + sx * 0.6, y, EAVE + 0.1), 0.004, MAT['galv'], 6)
    lt.done()

# ================================================================== wall equipment
def build_equipment():
    eq = MB("RDH_Wall_Equipment")
    def exit_sign(x, y, z, face):   # face: direction the sign faces (unit vector in XY)
        Mt = T(x, y, z) @ R('Z', math.degrees(math.atan2(face[1], face[0])) - 90 + 180)
        eq.box(Mt, (0.38, 0.06, 0.16), MAT['white'])
        eq.box(Mt @ T(0, 0.031, 0), (0.34, 0.003, 0.12), MAT['exit'])
    def door_pair(cx, y, w=1.8, h=2.3, face=-1):
        # face=-1: door on the back wall facing -Y
        eq.boxp((cx - w / 2 - 0.08, y + face * 0.02, F), (cx + w / 2 + 0.08, y, F + h + 0.08), MAT['steel'])
        for sx in (-1, 1):
            x0 = cx + (0 if sx > 0 else -w / 2); x1 = x0 + w / 2
            eq.boxp((x0 + 0.01, y + face * 0.05, F + 0.01), (x1 - 0.01, y + face * 0.02, F + h), MAT['door'])
            eq.boxp((x0 + 0.25, y + face * 0.052, F + 1.4), (x1 - 0.25, y + face * 0.05, F + 1.9), MAT['glass_dark'])
            eq.boxp((x0 + 0.1, y + face * 0.12, F + 1.0), (x1 - 0.1, y + face * 0.09, F + 1.06), MAT['galv'])
        exit_sign(cx, y + face * 0.05, F + h + 0.35, (0, face))
    # back wall: roller shutter
    cx, wdt, hgt = 10.0, 6.0, 5.2
    y = Y1
    eq.boxp((cx - wdt / 2, y - 0.04, F), (cx + wdt / 2, y, F + hgt), MAT['galv'])
    for i in range(int(hgt / 0.1)):
        eq.boxp((cx - wdt / 2, y - 0.06, F + i * 0.1 + 0.02), (cx + wdt / 2, y - 0.04, F + i * 0.1 + 0.035), MAT['steel'])
    for sx in (-1, 1):
        eq.boxp((cx + sx * (wdt / 2 + 0.1) - 0.1, y - 0.2, F), (cx + sx * (wdt / 2 + 0.1) + 0.1, y, F + hgt + 0.3), MAT['steel'])
    eq.seg((cx - wdt / 2 - 0.2, y - 0.35, F + hgt + 0.45), (cx + wdt / 2 + 0.2, y - 0.35, F + hgt + 0.45), 0.32, MAT['galv'], 24)
    eq.boxp((cx + wdt / 2 + 0.25, y - 0.4, F + hgt + 0.2), (cx + wdt / 2 + 0.75, y - 0.1, F + hgt + 0.7), MAT['cabinet'])
    eq.boxp((cx + wdt / 2 + 0.4, y - 0.15, F + 1.3), (cx + wdt / 2 + 0.6, y - 0.05, F + 1.6), MAT['cabinet'])
    for i, m in enumerate(('led_green', 'led_red')):
        eq.cyl(T(cx + wdt / 2 + 0.5, y - 0.16, F + 1.5 - i * 0.06) @ AX['Y'], 0.015, 0.01, MAT[m], 10)
    # hazard stripe frame on the floor-side posts
    for sx in (-1, 1):
        eq.boxp((cx + sx * (wdt / 2 + 0.1) - 0.11, y - 0.21, F), (cx + sx * (wdt / 2 + 0.1) + 0.11, y - 0.19, F + 1.2), MAT['hazard'])
    # personnel doors
    door_pair(-14.0, Y1, face=-1); door_pair(29.0, Y1, face=-1)
    # side-wall door on +X wall (faces -X)
    sx_ = X1
    eq.boxp((sx_ - 0.02, 9.0, F), (sx_, 11.0, F + 2.4), MAT['steel'])
    eq.boxp((sx_ - 0.05, 9.05, F + 0.01), (sx_ - 0.02, 10.95, F + 2.3), MAT['door'])
    eq.boxp((sx_ - 0.12, 9.3, F + 1.0), (sx_ - 0.09, 10.7, F + 1.06), MAT['galv'])
    exit_sign(sx_ - 0.05, 10.0, F + 2.75, (-1, 0))
    # electrical distribution cabinets with conduits up to the ladders
    for i in range(5):
        x = -6.0 + i * 0.85
        h = 2.0 if i != 2 else 1.6
        eq.boxp((x, Y1 - 0.5, F), (x + 0.8, Y1, F + h), MAT['cabinet'])
        eq.boxp((x + 0.03, Y1 - 0.505, F + 0.1), (x + 0.77, Y1 - 0.5, F + h - 0.05), MAT['cabinet'])
        eq.boxp((x + 0.68, Y1 - 0.53, F + 0.9), (x + 0.71, Y1 - 0.505, F + 1.2), MAT['black'])
        for k in range(3):
            eq.cyl(T(x + 0.15 + k * 0.05, Y1 - 0.51, F + h - 0.2) @ AX['Y'], 0.008, 0.01, MAT[rng.choice(['led_green', 'led_green', 'led_red'])], 8)
        eq.boxp((x + 0.15, Y1 - 0.51, F + 1.3), (x + 0.35, Y1 - 0.505, F + 1.42), MAT['white'])
        for k in range(3):
            xc = x + 0.2 + k * 0.2
            eq.seg((xc, Y1 - 0.25, F + h), (xc, Y1 - 0.25, F + 5.4), 0.025, MAT['galv'], 8)
    eq.seg((-6.2, Y1 - 0.25, F + 5.4), (-6.2, Y1 - 0.25, F + 5.5), 0.02, MAT['galv'], 8)
    # horizontal trunking along the back wall at 5.4 m, then to the ladder
    eq.boxp((-8.3, Y1 - 0.35, F + 5.35), (-1.6, Y1 - 0.15, F + 5.55), MAT['galv'])
    # wall cabinets on the -X wall
    for y in (4.0, 4.9, 18.0):
        eq.boxp((X0, y, F + 0.9), (X0 + 0.3, y + 0.8, F + 2.0), MAT['cabinet'])
        eq.seg((X0 + 0.15, y + 0.4, F + 2.0), (X0 + 0.15, y + 0.4, F + 5.4), 0.025, MAT['galv'], 8)
    # fire extinguishers + sign plates at some columns, emergency lights, louvres
    for (x, y, nx) in [(X0 + 0.6, YS[2] + 0.4, 1), (X1 - 0.6, YS[3] + 0.4, -1), (X0 + 0.6, YS[5] + 0.4, 1),
                       (X1 - 0.6, YS[6] + 0.4, -1), (XS[3], Y1 - 0.6, 0), (XS[7], Y1 - 0.6, 0)]:
        eq.cyl(T(x, y, F + 0.55), 0.09, 0.55, MAT['red'], 16)
        eq.cyl(T(x, y, F + 0.86), 0.03, 0.08, MAT['black'], 10)
        eq.boxp((x - 0.12, y - 0.12, F + 1.6), (x + 0.12, y + 0.12, F + 1.85), MAT['red'])
    for y in YS[1::2]:
        for xw, d in ((X0, 1), (X1, -1)):
            eq.boxp((xw, y + 3.0, F + 3.1), (xw + d * 0.07, y + 3.35, F + 3.25), MAT['white'])
            eq.boxp((xw + d * 0.07, y + 3.05, F + 3.12), (xw + d * 0.075, y + 3.3, F + 3.18), MAT['emerg'])
        for xw, d in ((X0, 1), (X1, -1)):   # high-level louvres
            eq.boxp((xw, y + 1.0, F + 6.0), (xw + d * 0.05, y + 2.6, F + 6.9), MAT['steel'])
            for i in range(8):
                eq.boxp((xw + d * 0.05, y + 1.05, F + 6.05 + i * 0.11), (xw + d * 0.1, y + 2.55, F + 6.09 + i * 0.11), MAT['black'])
    eq.done()

build_walls(); build_structure(); build_services(); build_equipment()

# procedural surface detail (noise roughness, smudges, scratches) on the big materials
LEVEL = 'clean'
TARGETS = {'RDH_steel': ('paint', 0.3), 'RDH_wall': ('paint', 0.25), 'RDH_galv': ('metal', 0.5),
           'RDH_deck': ('metal', 0.3), 'RDH_cabinet': ('paint', 1.0), 'RDH_door': ('paint', 1.0),
           'RDH_concrete': ('paint', 0.4)}
exec(open(DIR + r"\na_material_detail.py").read())
TARGETS = None

print("RDH objects:", len(COLL.objects), "verts:", sum(len(o.data.vertices) for o in COLL.objects if o.type == 'MESH'))
if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
print("RDH OK")
