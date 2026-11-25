"""SH_02 v03: one continuous shot. Tweezers -> climb -> flat logic with errors -> logical qubit -> "WHAT WE HAVE".
Builds v03 from v02. Scene.001 (the old logic layer) is left in the file, untouched and unused.

    blender -b --factory-startup --python sh02_v03_build.py [-- output.blend]

All timing is in keyframed custom properties on SH02_CTRL; the camera is the CamRig > CamPitch > Camera_v03 rig.
The last frame is pixel-aligned with the chasm card (12c): dots at x = 120 + 30 c, y = 650 - 30 r, 1920x1080.
DON'T re-run over v03 once the user has edited it by hand.
"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "SH_02_Tweezers_and_logic_grid_v02.blend")
DST = os.path.join(HERE, "SH_02_Tweezers_to_logic_v03.blend")
if "--" in sys.argv and sys.argv[sys.argv.index("--") + 1:]:
    DST = sys.argv[sys.argv.index("--") + 1]

bpy.ops.wm.open_mainfile(filepath=SRC)
D = bpy.data
S = D.scenes["Scene"]
bpy.context.window.scene = S
END = 250
S.frame_start, S.frame_end = 1, END

Z, TRACK_Z = 1.78, 1.854           # atom plane, height the camera looks at (as in v02)
N, HALF = 12, 2.44
SP = 2 * HALF / (N - 1)
R = 0.105                          # radius of an atom's circle
PITCH = 6.2                        # distance between patches
COLS, ROWS, HC, HR = 8, 6, 3, 2    # the "what we have" grid and the hero patch in it (from bottom left)
LENS = 85.0
PX = 36.0 / LENS / 1920            # world size of one pixel, per unit of distance
D_HERO = 27.7                      # distance that frames the hero patch
D_END = PITCH / 30.0 / PX          # distance at which patches are 30 px apart
# hero patch on the 12c card: (120 + 30 HC, 650 - 30 HR); offset of the frame centre from it, in pixels
PAN_X, PAN_Y = 960 - (120 + 30 * HC), (650 - 30 * HR) - 540

# which atoms fail and when (i = column, j = row)
ERRORS = [((5, 4), 70), ((7, 6), 80), ((3, 7), 93), ((8, 3), 108), ((4, 9), 117),
          ((6, 7), 126), ((2, 4), 133), ((9, 8), 139), ((6, 2), 145)]

col = D.collections.new("SH02_v03")
S.collection.children.link(col)

# ------------------------------------------------------------------ controls
ctrl = D.objects.new("SH02_CTRL", None)
ctrl.empty_display_size = 0.4
ctrl.location = (0, 0, 6)
col.objects.link(ctrl)
CTRL = {  # name: (tooltip, [(frame, value), ...])
    "quantum":   ("Clouds around the atoms and drifting background atoms. 1 = physics, 0 = diagram", [(82, 1), (114, 0)]),
    "beams":     ("Brightness of the tweezers", [(4, 2), (18, 1), (54, 1), (70, .5), (104, 0)]),
    "beam_len":  ("How far the tweezers reach above and below the atoms. Long at the start, to continue SH_1", [(14, 14.5), (40, 5)]),
    "haze":      ("Glow of the residual atom cloud. 1 = as in v02", [(82, .3), (112, 0)]),
    "beam_far":  ("Brightness of the far rows of tweezers, relative to the nearest", [(20, .012), (84, .3)]),
    "atom_far":  ("Opacity of the far rows of atoms, relative to the nearest", [(40, .14), (84, 1)]),
    "dark":      ("Covers the chamber with black", [(66, 0), (104, 1)]),
    "links":     ("Nearest-neighbour links grow from the centre", [(98, 0), (128, 1)]),
    "boundary":  ("The line around the patch = one logical qubit", [(148, 0), (164, 1)]),
    "err_fixed": ("Errors inside the patch go back to white", [(163, 0), (174, 1)]),
    "patches":   ("Other patches appear, from the hero outwards", [(166, 0), (208, 1)]),
    "collapse":  ("Each patch becomes a circle, then a dot", [(194, 0), (234, 1)]),
    "grid":      ("Links between the dots, as on card 12c", [(226, 0), (242, 1)]),
}
for nm, (tip, keys) in CTRL.items():
    ctrl[nm] = float(keys[0][1])
    ctrl.id_properties_ui(nm).update(min=0.0, max=20.0, description=tip)
    for f, v in keys:
        ctrl[nm] = float(v)
        ctrl.keyframe_insert('["%s"]' % nm, frame=f)
for k, (_, f) in enumerate(ERRORS, 1):
    ctrl["err_%d" % k] = float(f)
    ctrl.id_properties_ui("err_%d" % k).update(min=0.0, max=1000.0, description="Frame at which error %d starts" % k)


# ------------------------------------------------------------------ node helper
class NT:
    def __init__(s, name, mat=None):
        s.mat = mat or D.materials.new(name)
        s.t = s.mat.node_tree
        if not mat:
            s.mat.use_nodes = True
            s.t = s.mat.node_tree
            s.t.nodes.clear()
        s.k = 0
        s.cache = {}

    def n(s, kind, label="", **kw):
        x = s.t.nodes.new(kind)
        x.label = label
        x.location = ((s.k % 12) * 190, -(s.k // 12) * 240)
        s.k += 1
        for a, b in kw.items():
            setattr(x, a, b)
        return x

    def put(s, sock, v):
        if hasattr(v, "links"):
            s.t.links.new(v, sock)
        else:
            sock.default_value = v

    def m(s, op, a, b=None, c=None, clamp=False, label=""):
        x = s.n("ShaderNodeMath", label, operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b, c)):
            if v is not None:
                s.put(x.inputs[i], v)
        return x.outputs[0]

    def mul(s, *a):
        r = a[0]
        for b in a[1:]:
            r = s.m("MULTIPLY", r, b)
        return r

    def v(s, op, a, b=None, scale=None):
        x = s.n("ShaderNodeVectorMath", operation=op)
        s.put(x.inputs[0], a)
        if b is not None:
            s.put(x.inputs[1], b)
        if scale is not None:
            s.put(x.inputs["Scale"], scale)
        return x.outputs["Value"] if op in {"LENGTH", "DOT_PRODUCT"} else x.outputs["Vector"]

    def step(s, x, lo, hi, label=""):
        """1 below lo, 0 above hi"""
        k = s.n("ShaderNodeMapRange", label, interpolation_type="SMOOTHSTEP")
        s.put(k.inputs["Value"], x)
        s.put(k.inputs["From Min"], lo)
        s.put(k.inputs["From Max"], hi)
        k.inputs["To Min"].default_value, k.inputs["To Max"].default_value = 1.0, 0.0
        return k.outputs["Result"]

    def xyz(s, a):
        x = s.n("ShaderNodeSeparateXYZ")
        s.put(x.inputs[0], a)
        return x.outputs

    def prop(s, nm, ob=None):
        """value of a control, through a driver"""
        if nm in s.cache:
            return s.cache[nm]
        x = s.n("ShaderNodeValue", nm)
        d = x.outputs[0].driver_add("default_value").driver
        if nm == "frame":
            d.expression = "frame"
        else:
            d.type = "AVERAGE"
            w = d.variables.new()
            w.targets[0].id = ob or ctrl
            w.targets[0].data_path = '["%s"]' % nm
        s.cache[nm] = x.outputs[0]
        return x.outputs[0]

    def pixel(s):
        """size of one pixel on the atom plane, in world units (follows CamRig's zoom)"""
        x = s.n("ShaderNodeValue", "one pixel, world units")
        d = x.outputs[0].driver_add("default_value").driver
        w = d.variables.new()
        w.name = "z"
        w.targets[0].id = rig
        w.targets[0].data_path = '["zoom"]'
        d.expression = "exp(z) * %.9f" % PX
        return x.outputs[0]

    def far_lod(s, pxw):
        return s.step(s.m("DIVIDE", SP, pxw, label="pixels between atoms"), 5.0, 15.0, "1 = too small for circles and links")

    def attr(s, nm):
        x = s.n("ShaderNodeAttribute", nm, attribute_type="GEOMETRY", attribute_name=nm)
        return x.outputs

    def out(s, shader):
        s.put(s.n("ShaderNodeOutputMaterial").inputs[0], shader)

    def alpha_emission(s, color, strength, alpha):
        em = s.n("ShaderNodeEmission")
        s.put(em.inputs[0], color)
        s.put(em.inputs[1], strength)
        mx = s.n("ShaderNodeMixShader")
        s.put(mx.inputs[0], alpha)
        s.put(mx.inputs[1], s.n("ShaderNodeBsdfTransparent").outputs[0])
        s.put(mx.inputs[2], em.outputs[0])
        s.out(mx.outputs[0])
        s.mat.cycles.emission_sampling = "NONE"

    def errors(s, lead=0.0):
        """(0..1 failed, 0..1 flicker just after it fails) for this atom"""
        eid, fr = s.attr("err_id")["Fac"], s.prop("frame")
        age = None
        for k in range(1, len(ERRORS) + 1):
            hit = s.m("COMPARE", eid, float(k), 0.1)
            a = s.mul(hit, s.m("SUBTRACT", fr, s.prop("err_%d" % k)))
            age = a if age is None else s.m("ADD", age, a)
        bad = s.m("GREATER_THAN", eid, 0.5)
        age = s.m("ADD", age, lead, label="frames since the error")
        on = s.mul(s.m("SUBTRACT", 1.0, s.step(age, 0.0, 7.0)), bad)
        live = s.mul(on, s.m("SUBTRACT", 1.0, s.prop("err_fixed")))
        pulse = s.mul(s.m("SUBTRACT", 1.0, s.step(age, -3.0, 1.0)), s.step(age, 3.0, 18.0), bad)
        return live, pulse


WHITE, RED = (.95, .97, 1.0, 1), (1.0, .012, .012, 1)
W_STR, R_STR = 3.2, 1.5


def color_mix(q, e):
    c = q.n("ShaderNodeMix", data_type="RGBA")
    q.put(c.inputs["Factor"], e)
    c.inputs["A"].default_value, c.inputs["B"].default_value = WHITE, RED
    st = q.m("ADD", W_STR, q.mul(e, R_STR - W_STR))
    return [o for o in c.outputs if o.type == "RGBA"][0], st


rig = D.objects.new("CamRig", None)
rig["zoom"] = 0.0

# ------------------------------------------------------------------ atoms (hero patch)
def joined(name, make, seed=3):
    rnd = random.Random(seed)
    me = D.meshes.new(name)
    bm = bmesh.new()
    lc = bm.verts.layers.float_vector.new("site")
    le = bm.verts.layers.float.new("err_id")
    lr = bm.verts.layers.float.new("rnd")
    err = {ij: k for k, (ij, _) in enumerate(ERRORS, 1)}
    for i in range(N):
        for j in range(N):
            c = Vector((-HALF + i * SP, -HALF + j * SP, Z))
            rr = rnd.random()
            for v in make(bm):
                v.co += c
                v[lc], v[le], v[lr] = c, float(err.get((i, j), 0)), rr
    bm.to_mesh(me)
    bm.free()
    ob = D.objects.new(name, me)
    col.objects.link(ob)
    ob.visible_shadow = ob.visible_diffuse = ob.visible_glossy = False
    return ob


q = NT("sh02_atom")
geo = q.n("ShaderNodeNewGeometry")
e = geo.outputs["Incoming"]
P = q.v("SUBTRACT", geo.outputs["Position"], q.attr("site")["Vector"])
mid = q.v("SUBTRACT", P, q.v("SCALE", e, scale=q.v("DOT_PRODUCT", P, e)))
live, pulse = q.errors()
size = q.mul(q.m("ADD", q.m("SUBTRACT", 1.0, q.mul(q.prop("quantum"), .28)), q.mul(live, .22)), R)  # the circle grows into the icon
mid = q.v("SCALE", mid, scale=q.m("DIVIDE", 1.0, size))
b = q.v("LENGTH", mid)
w = q.m("ADD", q.mul(q.prop("frame"), 0.004), q.mul(q.attr("rnd")["Fac"], 40.0))
wob = q.n("ShaderNodeTexNoise", "breaks the circle while an atom fails", noise_dimensions="4D")
q.put(wob.inputs["Vector"], mid)
q.put(wob.inputs["W"], q.mul(q.prop("frame"), 0.22))
wob.inputs["Scale"].default_value = 1.6
bj = q.m("ADD", b, q.mul(pulse, q.m("SUBTRACT", wob.outputs["Fac"], 0.5), 0.9))
nr = q.m("ADD", .26, q.mul(live, .16))
nuc = q.step(bj, nr, q.m("ADD", nr, .06), "nucleus")
rw = q.m("ADD", 1.0, q.mul(live, .9))
ring = q.mul(q.step(q.m("ABSOLUTE", q.m("SUBTRACT", bj, 1.0)), q.mul(rw, .025), q.mul(rw, .06), "circle"),
             q.m("SUBTRACT", 1.0, q.mul(q.prop("quantum"), q.m("SUBTRACT", 0.62, q.mul(live, .62)))))
cl = None
for t in (-.7, -.35, 0, .35, .7):
    Q = q.v("ADD", mid, q.v("SCALE", e, scale=t))
    vo = q.n("ShaderNodeTexVoronoi", "cloud %+.2f" % t, voronoi_dimensions="4D")
    q.put(vo.inputs["Vector"], Q)
    vo.inputs["Scale"].default_value = 7
    q.put(vo.inputs["W"], w)
    lay = q.mul(q.m("EXPONENT", q.mul(q.v("LENGTH", Q), -1 / .3)), q.m("ADD", q.mul(q.step(vo.outputs["Distance"], .12, .48), 2.9), .05))
    cl = lay if cl is None else q.m("ADD", cl, lay)
cl = q.mul(cl, q.m("ADD", q.prop("quantum"), q.mul(pulse, 1.8)), q.step(b, .72, .97))
fade = q.mul(q.step(q.prop("collapse"), .10, .42, "hero atoms go with the patch"), q.m("SUBTRACT", 1.0, q.far_lod(q.pixel())))
row = q.m("DIVIDE", q.m("ADD", q.xyz(q.attr("site")["Vector"])[1], HALF), 2 * HALF, clamp=True)
depth = q.m("POWER", q.prop("atom_far"), row, label="far rows are fainter while the view is low")
a = q.mul(q.m("ADD", q.m("ADD", nuc, ring), cl, clamp=True), fade, depth, q.m("SUBTRACT", 1.0, geo.outputs["Backfacing"]))
halo = q.mul(q.m("EXPONENT", q.mul(q.m("MAXIMUM", q.m("SUBTRACT", b, 1.0), 0.0), -4.0)), q.m("GREATER_THAN", b, 1.0), live, q.m("ADD", .06, q.mul(q.prop("quantum"), .24)), fade,
             q.step(b, 1.2, 1.75), q.m("SUBTRACT", 1.0, geo.outputs["Backfacing"]))
lit = q.m("MAXIMUM", a, halo)
disc = q.mul(q.step(b, 1.15, 1.75, "dark disc behind a failed atom"), live, .85, fade, q.m("SUBTRACT", 1.0, geo.outputs["Backfacing"]))
al = q.m("MAXIMUM", lit, disc)
c, st = color_mix(q, live)
q.alpha_emission(c, q.mul(st, q.m("DIVIDE", lit, q.m("MAXIMUM", al, .0001))), al)
atoms = joined("sh02_atoms", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=2, radius=R * 2.05)["verts"])
atoms.data.materials.append(q.mat)

# ------------------------------------------------------------------ tweezers (hero patch)
W0, ZR, HL, BR = 0.030, 0.95, 14.5, 0.40
q = NT("sh02_tweezers")
geo = q.n("ShaderNodeNewGeometry")
e = geo.outputs["Incoming"]
P = q.v("SUBTRACT", geo.outputs["Position"], q.attr("site")["Vector"])
s_, ex = q.xyz(P), q.xyz(e)
ee = q.m("MAXIMUM", q.m("ADD", q.mul(ex[0], ex[0]), q.mul(ex[1], ex[1])), .0025)
t = q.m("DIVIDE", q.m("ADD", q.mul(s_[0], ex[0]), q.mul(s_[1], ex[1])), ee)
cc = q.xyz(q.v("SUBTRACT", P, q.v("SCALE", e, scale=t)))
b2, z = q.m("ADD", q.mul(cc[0], cc[0]), q.mul(cc[1], cc[1])), cc[2]
wz = q.mul(W0, q.m("SQRT", q.m("ADD", 1.0, q.m("POWER", q.m("ABSOLUTE", q.m("DIVIDE", z, ZR)), 2.0))))
wz = q.m("MINIMUM", wz, .15)
g = q.m("EXPONENT", q.m("DIVIDE", q.mul(b2, -2.0), q.mul(wz, wz)))
g = q.mul(g, q.m("DIVIDE", W0, wz), q.step(q.m("SQRT", b2), .6 * BR, .98 * BR))
g = q.mul(g, q.step(q.m("DIVIDE", q.m("ABSOLUTE", z), q.prop("beam_len")), .02, .9))
hot = q.m("EXPONENT", q.mul(z, z, -10.0))
g = q.mul(g, q.m("ADD", .75, q.mul(hot, 1.3)), q.m("MINIMUM", q.m("DIVIDE", 1.0, q.m("SQRT", ee)), 3.0))
row = q.m("DIVIDE", q.m("ADD", q.xyz(q.attr("site")["Vector"])[1], HALF), 2 * HALF, clamp=True, label="0 near row, 1 far row")
far = q.m("POWER", q.prop("beam_far"), row)
live, pulse = q.errors(lead=6.0)
g = q.mul(g, far, q.prop("beams"), q.m("SUBTRACT", 1.0, q.mul(live, .9)), q.m("SUBTRACT", 1.0, geo.outputs["Backfacing"]), 1.0)
em = q.n("ShaderNodeEmission")
em.inputs[0].default_value = (1.0, .075, .03, 1)
q.put(em.inputs[1], q.mul(g, .52))
ad = q.n("ShaderNodeAddShader")
q.put(ad.inputs[0], q.n("ShaderNodeBsdfTransparent").outputs[0])
q.put(ad.inputs[1], em.outputs[0])
q.out(ad.outputs[0])
q.mat.cycles.emission_sampling = "NONE"
beams = joined("sh02_tweezers", lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=BR, radius2=BR, depth=2 * HL)["verts"])
beams.data.materials.append(q.mat)
for f, h in ((1, False), (106, True)):
    beams.hide_render = h
    beams.keyframe_insert("hide_render", frame=f)
beams.hide_render = False

# ------------------------------------------------------------------ camera rig
old = S.camera
tp = D.objects["tracking_point"]
pit = D.objects.new("CamPitch", None)
cam = D.objects.new("Camera_v03", old.data.copy())
for o in (rig, pit, cam):
    col.objects.link(o)
pit.parent, cam.parent = rig, pit
cam.data.name = "Camera_v03"
cam.data.clip_end = 5000
rig.location = (0, 0, TRACK_Z)
for nm, v, tip in (("zoom", 0.0, "log of the distance to the atoms. Keyed"),
                   ("pan_x", 0.0, "How far the hero patch sits left of the frame centre, in pixels"),
                   ("pan_y", 0.0, "How far the hero patch sits below the frame centre, in pixels")):
    rig[nm] = v
    rig.id_properties_ui(nm).update(min=-2000.0, max=2000.0, description=tip)


def drive(owner, path, idx, expr, **props):
    d = owner.driver_add(path, idx).driver
    for nm in props:
        w_ = d.variables.new()
        w_.name = nm
        w_.targets[0].id = rig
        w_.targets[0].data_path = '["%s"]' % props[nm]
    d.expression = expr


drive(cam, "location", 2, "exp(z)", z="zoom")
drive(rig, "location", 0, "p * exp(z) * %.9f" % PX, p="pan_x", z="zoom")
drive(rig, "location", 1, "p * exp(z) * %.9f" % PX, p="pan_y", z="zoom")


def key_pose(f, az, el, dist):
    rig.rotation_euler = (0, 0, math.radians(az))
    rig.keyframe_insert("rotation_euler", index=2, frame=f)
    pit.rotation_euler = (math.radians(90 - el), 0, 0)
    pit.keyframe_insert("rotation_euler", index=0, frame=f)
    rig["zoom"] = math.log(dist)
    rig.keyframe_insert('["zoom"]', frame=f)


# the dive and the first drift are v02's, sampled
pose = {}
for f in list(range(1, 19)) + [22, 27, 33, 40]:
    S.frame_set(f)
    d = old.matrix_world.translation - tp.matrix_world.translation
    pose[f] = (math.degrees(math.atan2(d.x, -d.y)), math.degrees(math.asin(d.z / d.length)), d.length)
for f, p in pose.items():
    key_pose(f, *p)
for f, az, el, dist in ((56, 6.2, 15.5, 13.9), (72, 7.2, 35.0, 15.6), (90, 4.4, 67.0, 20.0), (116, 0, 90, 26.2),
                        (158, 0, 90, D_HERO + 1.2), (236, 0, 90, D_END), (END, 0, 90, D_END)):
    key_pose(f, az, el, dist)
for f, u in ((160, 0), (236, 1), (END, 1)):
    rig["pan_x"], rig["pan_y"] = u * float(PAN_X), u * float(PAN_Y)
    rig.keyframe_insert('["pan_x"]', frame=f)
    rig.keyframe_insert('["pan_y"]', frame=f)

foc = D.objects.new("focus_v03", None)
foc.empty_display_size = .2
col.objects.link(foc)
for f, p in ((40, (.65, -2.36, 1.85)), (72, (.1, -.9, Z)), (90, (0, 0, Z))):
    foc.location = p
    foc.keyframe_insert("location", frame=f)
cam.data.dof.focus_object = foc
for f, v in ((1, .15), (48, .17), (72, .45), (92, 1.6), (112, 22)):
    cam.data.dof.aperture_fstop = v
    cam.data.dof.keyframe_insert("aperture_fstop", frame=f)
for mk in S.timeline_markers:          # v02's markers switch back to the old camera
    if mk.camera:
        print("MARKER", mk.name, mk.frame, mk.camera.name)
        mk.camera = None
S.camera = cam



# ------------------------------------------------------------------ patches (diagram plane)
q = NT("sh02_patch")
oi = q.n("ShaderNodeObjectInfo")
hero = q.m("COMPARE", oi.outputs["Object Index"], 1.0, 0.1, label="1 on the hero patch")
other = q.m("SUBTRACT", 1.0, hero)
x, y, _ = q.xyz(q.n("ShaderNodeTexCoord").outputs["Object"])
pxw = q.pixel()
coll = q.prop("collapse")

# nearest atom site
def near(u):
    k = q.m("ROUND", q.m("DIVIDE", q.m("ADD", u, HALF), SP))
    k = q.m("MINIMUM", q.m("MAXIMUM", k, 0.0), float(N - 1))
    return k, q.m("SUBTRACT", u, q.m("SUBTRACT", q.mul(k, SP), HALF))
ki, du = near(x)
kj, dv = near(y)
bb = q.m("DIVIDE", q.m("SQRT", q.m("ADD", q.mul(du, du), q.mul(dv, dv))), R, label="b")
ax, ay = q.m("ABSOLUTE", x), q.m("ABSOLUTE", y)
r0 = q.m("SQRT", q.m("ADD", q.mul(x, x), q.mul(y, y)))
icon = q.m("ADD", q.step(bb, .26, .32), q.step(q.m("ABSOLUTE", q.m("SUBTRACT", bb, 1.0)), .025, .06), clamp=True)
lod = q.far_lod(pxw)
icon = q.m("ADD", q.mul(icon, q.m("SUBTRACT", 1.0, lod)), q.mul(q.step(bb, .45, 1.15), lod, .75))
lw = 0.0055
hl = q.mul(q.step(q.m("ABSOLUTE", dv), lw * .6, lw * 1.4), q.step(ax, HALF, HALF + .004))
vl = q.mul(q.step(q.m("ABSOLUTE", du), lw * .6, lw * 1.4), q.step(ay, HALF, HALF + .004))
grow = q.m("SUBTRACT", q.mul(q.prop("links"), 4.6), r0)
grow = q.m("SUBTRACT", 1.0, q.step(grow, 0.0, .6))
link = q.mul(q.m("MAXIMUM", hl, vl), q.m("SUBTRACT", 1.0, q.step(bb, 1.04, 1.08)), grow, .42, q.m("SUBTRACT", 1.0, lod))

# other patches appear from the hero outwards
wp = q.xyz(oi.outputs["Location"])
dist = q.m("SQRT", q.m("ADD", q.mul(wp[0], wp[0]), q.mul(wp[1], wp[1])))
jit = q.m("ADD", q.m("DIVIDE", dist, 5 * PITCH), q.mul(oi.outputs["Random"], .10))
seen = q.m("SUBTRACT", q.mul(q.prop("patches"), 1.35), jit)
seen = q.m("SUBTRACT", 1.0, q.step(seen, 0.0, .18))
seen = q.m("MAXIMUM", seen, hero, label="patch visible")

# a few blinking errors on the other patches
wn = q.n("ShaderNodeTexWhiteNoise", "errors elsewhere", noise_dimensions="4D")
cb = q.n("ShaderNodeCombineXYZ")
q.put(cb.inputs[0], ki)
q.put(cb.inputs[1], kj)
q.put(cb.inputs[2], q.mul(oi.outputs["Random"], 97.0))
q.put(wn.inputs["Vector"], cb.outputs[0])
q.put(wn.inputs["W"], q.m("FLOOR", q.mul(q.prop("frame"), 1 / 9)))
err2 = q.mul(q.m("GREATER_THAN", wn.outputs["Value"], .972), other)

# boundary: rounded square -> circle -> gone
k1 = q.m("SUBTRACT", 1.0, q.step(coll, 0.0, .62))                  # square -> circle
hs = q.m("ADD", 2.80, q.mul(k1, 1.35 - 2.80), label="half size")
rc = q.m("ADD", .34, q.mul(k1, 1.35 - .34), label="corner radius")
ox = q.m("MAXIMUM", q.m("ADD", q.m("SUBTRACT", ax, hs), rc), 0.0)
oy = q.m("MAXIMUM", q.m("ADD", q.m("SUBTRACT", ay, hs), rc), 0.0)
sdf = q.m("SUBTRACT", q.m("SQRT", q.m("ADD", q.mul(ox, ox), q.mul(oy, oy))), rc, label="distance to the boundary")
bw = q.mul(pxw, .95)
line = q.step(q.m("ABSOLUTE", sdf), q.mul(bw, .5), q.mul(bw, 1.3), "boundary line")
# drawn around, from the top, both ways
ang = q.m("DIVIDE", q.m("ABSOLUTE", q.m("ARCTAN2", x, y)), math.pi)
bnd = q.m("SUBTRACT", q.mul(q.prop("boundary"), 1.04), ang)
bnd = q.m("SUBTRACT", 1.0, q.step(bnd, 0.0, .03))
line = q.mul(line, bnd, q.step(coll, .72, .98))
inside = q.mul(q.step(coll, .10, .42, "contents fade"), q.step(sdf, q.mul(pxw, -1.0), 0.0))
glow = q.mul(q.m("EXPONENT", q.m("DIVIDE", q.m("MINIMUM", sdf, 0.0), .55)), q.step(sdf, -.001, .001), q.m("SUBTRACT", 1.0, q.step(q.prop("boundary"), .75, 1.0)), .006,
             q.step(coll, .3, .7))
dr = q.mul(pxw, q.m("ADD", .6, q.mul(q.m("SUBTRACT", 1.0, q.step(coll, .35, .8)), 1.9)))
dot = q.mul(q.step(r0, q.m("SUBTRACT", dr, q.mul(pxw, .5)), q.m("ADD", dr, q.mul(pxw, .5))), q.m("SUBTRACT", 1.0, q.step(coll, .35, .62)))

body = q.m("MAXIMUM", q.mul(icon, q.m("MAXIMUM", other, lod)), link)
al = q.m("MAXIMUM", q.mul(body, inside), q.m("MAXIMUM", line, q.m("MAXIMUM", dot, glow)))
al = q.mul(al, seen)
c, st = color_mix(q, q.mul(err2, q.m("SUBTRACT", 1.0, q.m("MAXIMUM", line, dot))))
st = q.m("ADD", st, q.mul(dot, 9.0))          # the final dots are as white as the card's
q.alpha_emission(c, st, al)
h = PITCH / 2
me = D.meshes.new("sh02_patch")
me.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
me.materials.append(q.mat)
for cx in range(COLS):
    for cy in range(ROWS):
        ob = D.objects.new("sh02_patch_%d_%d" % (cx, cy), me)
        ob.location = ((cx - HC) * PITCH, (cy - HR) * PITCH, Z)
        ob.visible_shadow = ob.visible_diffuse = ob.visible_glossy = False
        col.objects.link(ob)
        is_hero = (cx, cy) == (HC, HR)
        ob.pass_index = int(is_hero)
        if is_hero:
            ob.name = "sh02_patch_HERO"
        for f, hid in ((1, True), (96 if is_hero else 165, False)):
            ob.hide_render = hid
            ob.keyframe_insert("hide_render", frame=f)

# links between the dots (card 12c: 1 px, 22 %)
q = NT("sh02_grid_links")
x, y, _ = q.xyz(q.n("ShaderNodeTexCoord").outputs["Object"])
x, y = q.m("ADD", x, HC * PITCH), q.m("ADD", y, HR * PITCH)
def offline(u):
    return q.m("ABSOLUTE", q.m("SUBTRACT", u, q.mul(q.m("ROUND", q.m("DIVIDE", u, PITCH)), PITCH)))
hw = D_END * PX * .5
ln = q.m("MAXIMUM", q.step(offline(x), hw * .8, hw * 1.2), q.step(offline(y), hw * .8, hw * 1.2))
q.alpha_emission(WHITE, W_STR, q.mul(ln, q.prop("grid"), .022))
X0, X1, Y0, Y1 = -HC * PITCH, (COLS - 1 - HC) * PITCH, -HR * PITCH, (ROWS - 1 - HR) * PITCH
me = D.meshes.new("sh02_grid_links")
me.from_pydata([(X0 - hw, Y0 - hw, 0), (X1 + hw, Y0 - hw, 0), (X1 + hw, Y1 + hw, 0), (X0 - hw, Y1 + hw, 0)], [], [(0, 1, 2, 3)])
me.materials.append(q.mat)
ob = D.objects.new("sh02_grid_links", me)
ob.location = (0, 0, Z - .3)
ob.visible_shadow = ob.visible_diffuse = ob.visible_glossy = False
col.objects.link(ob)
for f, hid in ((1, True), (224, False)):
    ob.hide_render = hid
    ob.keyframe_insert("hide_render", frame=f)

# ------------------------------------------------------------------ black cover over the chamber
q = NT("sh02_dark")
em = q.n("ShaderNodeEmission")
em.inputs[0].default_value, em.inputs[1].default_value = (0, 0, 0, 1), 0.0
mx = q.n("ShaderNodeMixShader")
q.put(mx.inputs[0], q.prop("dark"))
q.put(mx.inputs[1], q.n("ShaderNodeBsdfTransparent").outputs[0])
q.put(mx.inputs[2], em.outputs[0])
q.out(mx.outputs[0])
me = D.meshes.new("sh02_dark")
L = 2500
me.from_pydata([(-L, -L, 0), (L, -L, 0), (L, L, 0), (-L, L, 0)], [], [(0, 1, 2, 3)])
me.materials.append(q.mat)
ob = D.objects.new("sh02_dark", me)
ob.location = (0, 0, .9)
ob.visible_shadow = ob.visible_diffuse = ob.visible_glossy = False
col.objects.link(ob)
for f, hid in ((1, True), (66, False)):
    ob.hide_render = hid
    ob.keyframe_insert("hide_render", frame=f)

# ------------------------------------------------------------------ v02 objects
for n in ("atoms-geo-nodes", "tweezers", "objective_upper", "objective_upper_lens", "atomic-logic"):
    S.objects[n].hide_render = True
for o in S.objects:
    if o.name.startswith(("chamber_shell", "port_", "objective_lower", "untrapped", "trap_cloud")):
        for f, hid in ((1, False), (116, True)):
            o.hide_render = hid
            o.keyframe_insert("hide_render", frame=f)
        o.hide_render = False


def fade_out(mat, socket, nm):
    """multiply a shader's output by a control: mix it with transparent"""
    q = NT("", mat)
    q.k = 60
    out = next(n for n in mat.node_tree.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
    src = out.inputs[socket].links[0].from_socket
    mx = q.n("ShaderNodeMixShader", "v03 fade")
    q.put(mx.inputs[0], q.prop(nm))
    if socket == "Surface":
        q.put(mx.inputs[1], q.n("ShaderNodeBsdfTransparent").outputs[0])
    q.put(mx.inputs[2], src)
    q.put(out.inputs[socket], mx.outputs[0])


mats = set()
gn = S.objects["untrapped_atoms"].modifiers[0].node_group
for nd in gn.nodes:
    if nd.bl_idname == "GeometryNodeSetMaterial" and nd.inputs["Material"].default_value:
        mats.add(nd.inputs["Material"].default_value)
for m_ in mats:
    fade_out(m_, "Surface", "quantum")
fade_out(D.materials["trap_cloud_haze"], "Volume", "haze")
print("FADED", [m_.name for m_ in mats])

# ------------------------------------------------------------------ compositor: grain and lens fade into the diagram
ng = S.compositing_node_group
ng = S.compositing_node_group = ng.copy()
ld = next(n for n in ng.nodes if n.bl_idname == "CompositorNodeLensdist")
gr = next(n for n in ng.nodes if n.bl_idname == "CompositorNodeGroup")
for sock, keys in ((ld.inputs["Distortion"], ((76, .02), (112, 0.0))), (ld.inputs["Dispersion"], ((76, .02), (112, 0.0))),
                   (gr.inputs["Luminance Noise"], ((80, .1), (118, .03), (210, .03), (240, 0.0))),
                   (gr.inputs["Chroma Noise"], ((80, .05), (118, .01), (210, .01), (240, 0.0)))):
    for f, v in keys:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)

S.cycles.transparent_max_bounces = 128
S.render.filepath = "//../../08_renders/Final_draft/sh_02_v03/SH_02_v03_"
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=DST)
print("BUILT OK", DST, "D_END", D_END, "PAN", PAN_X, PAN_Y)
