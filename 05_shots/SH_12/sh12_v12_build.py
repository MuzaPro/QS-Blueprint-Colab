"""
SH_12 v12 build: v11 + logic-card prelude, Compound Architecture title,
photonic / atomic callouts, atom-glow wave, and a dive that lands on SH_15's
first frame.

Run (never writes v11):
  blender -b sh_12_The_Turn_and_the_Reveal_11.blend --python sh12_v12_build.py
  blender -b sh_12_The_Turn_and_the_Reveal_11.blend --python sh12_v12_build.py -- <out.blend> [--force]

Do NOT re-run it over a v12 that has been edited by hand: it rebuilds from v11.
All timings below are in v12 frame numbers. OFFSET maps old frame f to f + OFFSET.
"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view

# ---------------------------------------------------------------- parameters
OFFSET = 260                 # v11 frame 1 becomes v12 frame OFFSET+1
CARD_REL = "../../04_assets/props/2D-Overlays_FrameK/03_Render/Card_10/Card_10_v1.mp4"
CARD_LEN = 350
CARD_START = 1               # scene frame that shows card frame 1
CARD_OUT = (OFFSET + 6, OFFSET + 40)

TITLE_IN = 212               # eyebrow starts; main title follows
TITLE_OUT = (OFFSET + 8, OFFSET + 30)
TITLE_CAP_PX = 56            # cap height of COMPOUND ARCHITECTURE in px (1080p)
TITLE_Y_PX = -250            # baseline, px from frame centre (+ = up)

PHOTONIC_IN, PHOTONIC_OUT = OFFSET + 62, OFFSET + 136
ATOMIC_IN, ATOMIC_OUT = OFFSET + 162, OFFSET + 222

WAVE_START = OFFSET + 170    # first atom starts to glow
WAVE_TRAVEL = 40             # frames for the wave to cross the chip
WAVE_RISE, WAVE_HOLD, WAVE_FALL = 5, 9, 16
ATOM_R = 0.32                # glow sphere radius (cavity gap is 0.57 tall)
ATOM_CORE, ATOM_HALO = 3.5, 0.4

DIVE_T0 = OFFSET + 280       # Camera_Dive takes over (matches Camera exactly here)
DIVE_LEN = 60                # frames to land on SH_15 frame 50
PENTET_OFFSET = Vector((99.1, -67.7, 26.834))   # SH_15 world -> SH_12 pentet (checked)

def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# Brand guide (04_assets/brand/Quantum Source Quick Brand Guide 8-11-2023.pdf, p.8):
# accent = logo colour P. 319 C, #4DDDEC, RGB 77/221/236. Node colours are linear,
# so convert; with the Standard view transform it renders back to exactly #4DDDEC.
CYAN_HEX = "#4DDDEC"
REC709_TO_AP1 = Matrix(((0.6130974, 0.3395231, 0.0473795),
                        (0.0701937, 0.9163539, 0.0134524),
                        (0.0206156, 0.1095698, 0.8698146)))


def brand_color(hexstr):
    """sRGB hex -> scene-linear in this file's working space (v11 is ACEScg)."""
    lin = Vector(tuple(srgb_to_linear(int(hexstr[i:i + 2], 16) / 255) for i in (1, 3, 5)))
    ws = getattr(getattr(bpy.data, "colorspace", None), "working_space", "")
    if "ACES" in ws and "cg" in ws.lower():
        lin = REC709_TO_AP1 @ lin
    return tuple(lin)


CYAN = brand_color(CYAN_HEX)
WHITE = (1.0, 1.0, 1.0)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FONT_DIR = os.path.join(ROOT, "04_assets", "brand")
F_LIGHT = os.path.join(FONT_DIR, "Overpass", "static", "Overpass-Light.ttf")
F_REG = os.path.join(FONT_DIR, "Overpass", "static", "Overpass-Regular.ttf")
F_SEMI = os.path.join(FONT_DIR, "Overpass", "static", "Overpass-SemiBold.ttf")
F_MONO = os.path.join(FONT_DIR, "Overpass_Mono", "static", "OverpassMono-Regular.ttf")
SH15_CAM_JSON = os.path.join(HERE, "sh12_v12_sh15_camera.json")

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.join(HERE, "sh_12_The_Turn_and_the_Reveal_12.blend")
FORCE = "--force" in argv
for a in argv:
    if a.endswith(".blend"):
        OUT = os.path.abspath(a)
if os.path.abspath(bpy.data.filepath) == OUT:
    raise SystemExit("Refusing to overwrite the source file")
if os.path.exists(OUT) and not FORCE:
    raise SystemExit("%s exists; pass --force to rebuild it" % OUT)

S = bpy.context.scene
CAM = S.camera
COLL = bpy.data.collections.new("SH12_v12_overlays")
S.collection.children.link(COLL)
log = []


def say(*a):
    t = " ".join(str(x) for x in a)
    print("[v12]", t)
    log.append(t)


# ---------------------------------------------------------------- 1. shift time
def action_fcurves(act):
    out = []
    try:
        out += list(act.fcurves)
    except Exception:
        pass
    try:
        for l in act.layers:
            for st in l.strips:
                for cb in st.channelbags:
                    out += list(cb.fcurves)
    except Exception:
        pass
    seen, uniq = set(), []
    for fc in out:
        if id(fc) not in seen:
            seen.add(id(fc)); uniq.append(fc)
    return uniq


n_keys = 0
for act in bpy.data.actions:
    if act.library:
        continue
    for fc in action_fcurves(act):
        for kp in fc.keyframe_points:
            kp.co.x += OFFSET; kp.handle_left.x += OFFSET; kp.handle_right.x += OFFSET
            n_keys += 1
        for m in fc.modifiers:
            say("fcurve modifier", act.name, fc.data_path, m.type)
            if getattr(m, "use_restricted_range", False):
                m.frame_start += OFFSET; m.frame_end += OFFSET
        if fc.extrapolation != 'CONSTANT':
            say("note: linear extrapolation on", act.name, fc.data_path)
        fc.update()
for idb in list(bpy.data.objects) + list(bpy.data.node_groups) + list(bpy.data.materials) + list(bpy.data.cameras):
    ad = getattr(idb, "animation_data", None)
    if ad and ad.nla_tracks:
        for tr in ad.nla_tracks:
            for st in reversed(list(tr.strips)):
                st.frame_end += OFFSET; st.frame_start += OFFSET
        say("NLA shifted on", idb.name)
for m in S.timeline_markers:
    m.frame += OFFSET
say("shifted", n_keys, "keys by", OFFSET)

S.frame_start = 1
S.frame_end = DIVE_T0 + DIVE_LEN
S.render.filepath = "//Render\\sh_12_v12\\sh_12_v12_"


def cam_at(f, cam=None):
    cam = cam or CAM
    S.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    ce = cam.evaluated_get(dg)
    return ce.matrix_world.copy(), ce.data.lens, ce.data.dof.focus_distance


def focus_dist(f):
    m, _, fd = cam_at(f)
    fo = CAM.data.dof.focus_object
    if fo:
        S.frame_set(f)
        p = fo.matrix_world.translation
        return (p - m.translation).dot(-m.col[2].xyz.normalized())
    return fd


def px_units(depth):
    """world units per pixel at a depth (sensor fit horizontal, 1920 wide)."""
    d = CAM.data
    return depth * d.sensor_width / d.lens / S.render.resolution_x


# ---------------------------------------------------------------- materials
def new_mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    return m, nt


def ui_material(name, color, geom_alpha):
    """Emission + premultiplied transparency. alpha = geometry 'alpha' (text)
    x object property 'fade'. 'glint' tints toward cyan and brightens."""
    m, nt = new_mat(name)
    N, L = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial")
    fade = N.new("ShaderNodeAttribute"); fade.attribute_type = 'OBJECT'; fade.attribute_name = "fade"
    if geom_alpha:
        ga = N.new("ShaderNodeAttribute"); ga.attribute_type = 'GEOMETRY'; ga.attribute_name = "alpha"
        gl = N.new("ShaderNodeAttribute"); gl.attribute_type = 'GEOMETRY'; gl.attribute_name = "glint"
        a = N.new("ShaderNodeMath"); a.operation = 'MULTIPLY'
        L.new(ga.outputs["Fac"], a.inputs[0]); L.new(fade.outputs["Fac"], a.inputs[1])
        alpha = a.outputs[0]
        mix = N.new("ShaderNodeMix"); mix.data_type = 'RGBA'
        mix.inputs[6].default_value = (*color, 1); mix.inputs[7].default_value = (*CYAN, 1)
        g2 = N.new("ShaderNodeMath"); g2.operation = 'MULTIPLY'; g2.inputs[1].default_value = 0.85
        L.new(gl.outputs["Fac"], g2.inputs[0]); L.new(g2.outputs[0], mix.inputs[0])
        col = mix.outputs[2]
        st = N.new("ShaderNodeMath"); st.operation = 'MULTIPLY_ADD'
        L.new(gl.outputs["Fac"], st.inputs[0]); st.inputs[1].default_value = 0.5; st.inputs[2].default_value = 1.0
        stren = N.new("ShaderNodeMath"); stren.operation = 'MULTIPLY'
        L.new(st.outputs[0], stren.inputs[0]); L.new(alpha, stren.inputs[1])
        strength = stren.outputs[0]
    else:
        alpha = fade.outputs["Fac"]
        rgb = N.new("ShaderNodeRGB"); rgb.outputs[0].default_value = (*color, 1)
        col = rgb.outputs[0]
        strength = alpha
    em = N.new("ShaderNodeEmission")
    L.new(col, em.inputs["Color"]); L.new(strength, em.inputs["Strength"])
    inv = N.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    L.new(alpha, inv.inputs[1])
    tr = N.new("ShaderNodeBsdfTransparent")
    L.new(inv.outputs[0], tr.inputs["Color"])
    add = N.new("ShaderNodeAddShader")
    L.new(em.outputs[0], add.inputs[0]); L.new(tr.outputs[0], add.inputs[1])
    L.new(add.outputs[0], out.inputs["Surface"])
    return m


def camera_only(ob, transmission=True, glossy=False):
    ob.visible_camera = True
    ob.visible_diffuse = False
    ob.visible_glossy = glossy
    ob.visible_transmission = transmission
    ob.visible_volume_scatter = False
    ob.visible_shadow = False


def link(ob):
    COLL.objects.link(ob)
    return ob


def key_fade(ob, pts):
    if "fade" not in ob:
        ob["fade"] = 0.0
    for f, v in pts:
        ob["fade"] = v
        ob.keyframe_insert('["fade"]', frame=f)


def key_visible(ob, f_on, f_off):
    for f, h in ((1, True), (f_on, False), (f_off, True)):
        ob.hide_render = h; ob.keyframe_insert("hide_render", frame=f)
        ob.hide_viewport = h; ob.keyframe_insert("hide_viewport", frame=f)


M_TXT_W = ui_material("SH12_Text_White", WHITE, True)
M_TXT_C = ui_material("SH12_Text_Cyan", CYAN, True)
M_SHP_W = ui_material("SH12_Shape_White", WHITE, False)
M_SHP_C = ui_material("SH12_Shape_Cyan", CYAN, False)


# ---------------------------------------------------------------- animated text (GN)
def font(path):
    f = bpy.data.fonts.load(path, check_existing=True)
    return f


def set_in(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value
        return True
    return False


def text_object(name, text, fpath, size, spacing, mat, t_in, stagger, dur,
                rise=0.0, spread=0.0, order="LTR", t_out=None, sweep=None, align='LEFT'):
    """Per-character reveal. alpha/glint stored per character for the shader."""
    ng = bpy.data.node_groups.new(name + "_GN", 'GeometryNodeTree')
    ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")

    def math(op, a, b=None, c=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def mrange(v, a, b, smooth=True):
        n = N.new("ShaderNodeMapRange"); n.data_type = 'FLOAT'
        n.interpolation_type = 'SMOOTHSTEP' if smooth else 'LINEAR'; n.clamp = True
        for i, x in ((0, v), (1, a), (2, b)):
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                L.new(x, n.inputs[i])
        n.inputs[3].default_value = 0.0; n.inputs[4].default_value = 1.0
        return n.outputs[0]

    s2c = N.new("GeometryNodeStringToCurves")
    s2c.inputs["String"].default_value = text
    s2c.inputs["Size"].default_value = size
    s2c.inputs["Character Spacing"].default_value = spacing
    vf = font(fpath)
    if hasattr(s2c, "font"):
        s2c.font = vf
    else:
        s2c.inputs["Font"].default_value = vf
    for prop, val in (("align_x", align), ("align_y", 'BASELINE')):
        if hasattr(s2c, prop):
            setattr(s2c, prop, val)
        else:
            nm = "Align X" if prop == "align_x" else "Align Y"
            menu = {"LEFT": "Left", "CENTER": "Center", "RIGHT": "Right", "BASELINE": "Bottom Baseline"}[val]
            if nm in s2c.inputs:
                s2c.inputs[nm].default_value = menu
    inst = s2c.outputs["Curve Instances"]
    fill = N.new("GeometryNodeFillCurve")
    # Triangles + even-odd keeps the counters of O, A, R, P... (N-gons fills them)
    if "Mode" in fill.inputs:
        fill.inputs["Mode"].default_value = 'Triangles'
    else:
        fill.mode = 'TRIANGLES'
    L.new(inst, fill.inputs["Curve"])

    frame = N.new("GeometryNodeInputSceneTime").outputs["Frame"]
    idx = N.new("GeometryNodeInputIndex").outputs[0]
    pos = N.new("GeometryNodeInputPosition").outputs[0]
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(pos, sep.inputs[0])
    x = sep.outputs["X"]
    stat = N.new("GeometryNodeAttributeStatistic"); stat.data_type = 'FLOAT'; stat.domain = 'INSTANCE'
    L.new(inst, stat.inputs["Geometry"]); L.new(x, stat.inputs["Attribute"])
    xmin, xmax = stat.outputs["Min"], stat.outputs["Max"]
    width = math('MAXIMUM', math('SUBTRACT', xmax, xmin), 1e-4)
    u = math('DIVIDE', math('SUBTRACT', x, xmin), width)
    centre = math('MULTIPLY', math('ADD', xmin, xmax), 0.5)
    count = N.new("GeometryNodeAttributeDomainSize"); count.component = 'INSTANCES'
    L.new(inst, count.inputs[0])
    if order == "OUTSIDE_IN":
        rank = math('SUBTRACT', 1.0, math('MULTIPLY', math('ABSOLUTE', math('SUBTRACT', u, 0.5)), 2.0))
        delay = math('MULTIPLY', rank, math('MULTIPLY', count.outputs["Instance Count"], stagger * 0.5))
    else:
        delay = math('MULTIPLY', idx, stagger)
    t0 = math('ADD', delay, float(t_in))
    t = mrange(frame, t0, math('ADD', t0, float(dur)))
    alpha = t
    if t_out:
        alpha = math('MULTIPLY', t, math('SUBTRACT', 1.0, mrange(frame, float(t_out[0]), float(t_out[1]))))
    inv_t = math('SUBTRACT', 1.0, t)
    dx = math('MULTIPLY', math('MULTIPLY', math('SUBTRACT', x, centre), spread), inv_t)
    dy = math('MULTIPLY', -rise, inv_t)
    comb = N.new("ShaderNodeCombineXYZ"); L.new(dx, comb.inputs[0]); L.new(dy, comb.inputs[1])
    tr = N.new("GeometryNodeTranslateInstances")
    L.new(fill.outputs[0], tr.inputs["Instances"]); L.new(comb.outputs[0], tr.inputs["Translation"])

    st_a = N.new("GeometryNodeStoreNamedAttribute"); st_a.data_type = 'FLOAT'; st_a.domain = 'INSTANCE'
    st_a.inputs["Name"].default_value = "alpha"
    L.new(tr.outputs[0], st_a.inputs["Geometry"]); L.new(alpha, st_a.inputs["Value"])
    if sweep:
        sp = N.new("ShaderNodeMapRange"); sp.data_type = 'FLOAT'; sp.clamp = True
        L.new(frame, sp.inputs[0]); sp.inputs[1].default_value = sweep[0]; sp.inputs[2].default_value = sweep[1]
        sp.inputs[3].default_value = -0.25; sp.inputs[4].default_value = 1.25
        d = math('SUBTRACT', u, sp.outputs[0])
        glint = math('EXPONENT', math('MULTIPLY', math('MULTIPLY', d, d), -1.0 / (0.09 ** 2)))
    else:
        glint = None
    st_g = N.new("GeometryNodeStoreNamedAttribute"); st_g.data_type = 'FLOAT'; st_g.domain = 'INSTANCE'
    st_g.inputs["Name"].default_value = "glint"
    L.new(st_a.outputs[0], st_g.inputs["Geometry"])
    if glint:
        L.new(glint, st_g.inputs["Value"])
    else:
        st_g.inputs["Value"].default_value = 0.0
    real = N.new("GeometryNodeRealizeInstances"); L.new(st_g.outputs[0], real.inputs[0])
    sm = N.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = mat
    L.new(real.outputs[0], sm.inputs["Geometry"])
    L.new(sm.outputs[0], go.inputs[0])

    me = bpy.data.meshes.new(name)
    ob = link(bpy.data.objects.new(name, me))
    ob.data.materials.append(mat)
    mod = ob.modifiers.new("Text", 'NODES'); mod.node_group = ng
    ob["fade"] = 1.0
    camera_only(ob)
    return ob


# ---------------------------------------------------------------- shapes
def line_curve(name, pts, radius, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (*q, 1)
    cu.bevel_depth = radius; cu.bevel_resolution = 2; cu.use_fill_caps = True
    cu.bevel_factor_mapping_start = 'SPLINE'; cu.bevel_factor_mapping_end = 'SPLINE'
    ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(mat)
    ob["fade"] = 1.0
    camera_only(ob)
    return ob


def draw_on(ob, f0, f1, out0=None, out1=None):
    cu = ob.data
    for f, v in ((f0, 0.0), (f1, 1.0)):
        cu.bevel_factor_end = v; cu.keyframe_insert("bevel_factor_end", frame=f)
    cu.bevel_factor_start = 0.0; cu.keyframe_insert("bevel_factor_start", frame=f0)
    if out0 is not None:
        cu.bevel_factor_start = 0.0; cu.keyframe_insert("bevel_factor_start", frame=out0)
        cu.bevel_factor_start = 1.0; cu.keyframe_insert("bevel_factor_start", frame=out1)


def disc_mesh(name, r_out, r_in=0.0, seg=48):
    import bmesh
    bm = bmesh.new()
    if r_in <= 0:
        bmesh.ops.create_circle(bm, cap_ends=True, radius=r_out, segments=seg)
    else:
        outer = [bm.verts.new((r_out * math.cos(a), r_out * math.sin(a), 0)) for a in np.linspace(0, 2 * math.pi, seg, endpoint=False)]
        inner = [bm.verts.new((r_in * math.cos(a), r_in * math.sin(a), 0)) for a in np.linspace(0, 2 * math.pi, seg, endpoint=False)]
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((outer[i], outer[j], inner[j], inner[i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return me


def facing_empty(name, loc):
    e = link(bpy.data.objects.new(name, None))
    e.empty_display_size = 1.0
    e.location = loc
    c = e.constraints.new('COPY_ROTATION'); c.target = CAM
    return e


# ---------------------------------------------------------------- 2. card plane
m_card, F1_FD = None, None
cm, lens, _ = cam_at(OFFSET + 1)
fd = focus_dist(OFFSET + 1)
cam_rot = cm.to_quaternion()
fwd = -(cm.col[2].xyz).normalized()
card_centre = cm.translation + fwd * fd
W = fd * CAM.data.sensor_width / lens
H = W * S.render.resolution_y / S.render.resolution_x
UPP = W / S.render.resolution_x            # units per pixel on the card plane
say("card depth", round(fd, 2), "size", round(W, 2), round(H, 2))

me = bpy.data.meshes.new("SH12_Card10")
me.from_pydata([(-W / 2, -H / 2, 0), (W / 2, -H / 2, 0), (W / 2, H / 2, 0), (-W / 2, H / 2, 0)], [], [(0, 1, 2, 3)])
uv = me.uv_layers.new(name="UVMap")
for li, (u, v) in zip(range(4), ((0, 0), (1, 0), (1, 1), (0, 1))):
    uv.data[li].uv = (u, v)
card = link(bpy.data.objects.new("SH12_Card10", me))
card.matrix_world = Matrix.Translation(card_centre) @ cam_rot.to_matrix().to_4x4()
camera_only(card)

mc, nt = new_mat("SH12_Card10")
N, L = nt.nodes, nt.links
img = bpy.data.images.load(os.path.normpath(os.path.join(HERE, CARD_REL)), check_existing=True)
img.source = 'MOVIE'
img.filepath = "//" + CARD_REL.replace("/", "\\")
img.colorspace_settings.name = 'sRGB'
tex = N.new("ShaderNodeTexImage"); tex.image = img; tex.interpolation = 'Linear'
iu = tex.image_user
iu.frame_duration = CARD_LEN; iu.frame_start = CARD_START; iu.frame_offset = 0
iu.use_auto_refresh = True; iu.use_cyclic = False
fade = N.new("ShaderNodeAttribute"); fade.attribute_type = 'OBJECT'; fade.attribute_name = "fade"
sep = N.new("ShaderNodeSeparateColor"); L.new(tex.outputs["Color"], sep.inputs[0])
mx1 = N.new("ShaderNodeMath"); mx1.operation = 'MAXIMUM'
L.new(sep.outputs[0], mx1.inputs[0]); L.new(sep.outputs[1], mx1.inputs[1])
mx2 = N.new("ShaderNodeMath"); mx2.operation = 'MAXIMUM'
L.new(mx1.outputs[0], mx2.inputs[0]); L.new(sep.outputs[2], mx2.inputs[1])
a = N.new("ShaderNodeMath"); a.operation = 'MULTIPLY'; a.use_clamp = True
L.new(mx2.outputs[0], a.inputs[0]); L.new(fade.outputs["Fac"], a.inputs[1])
em = N.new("ShaderNodeEmission"); L.new(tex.outputs["Color"], em.inputs["Color"]); L.new(fade.outputs["Fac"], em.inputs["Strength"])
inv = N.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; L.new(a.outputs[0], inv.inputs[1])
trn = N.new("ShaderNodeBsdfTransparent"); L.new(inv.outputs[0], trn.inputs["Color"])
add = N.new("ShaderNodeAddShader"); L.new(em.outputs[0], add.inputs[0]); L.new(trn.outputs[0], add.inputs[1])
out = N.new("ShaderNodeOutputMaterial"); L.new(add.outputs[0], out.inputs["Surface"])
card.data.materials.append(mc)
key_fade(card, [(CARD_OUT[0], 1.0), (CARD_OUT[1], 0.0)])
key_visible(card, 1, CARD_OUT[1] + 1)


def on_card(name, x_px, y_px, z_px=2.0):
    """matrix for an object lying in the card plane at pixel offsets from centre."""
    return card.matrix_world @ Matrix.Translation((x_px * UPP, y_px * UPP, z_px * UPP))


# ---------------------------------------------------------------- 3. title
CAP = 0.70                                # Overpass cap height / em
t_size = TITLE_CAP_PX / CAP * UPP
eye_size = 20 / CAP * UPP
title = text_object("SH12_Title", "COMPOUND ARCHITECTURE", F_LIGHT, t_size, 1.28, M_TXT_W,
                    TITLE_IN + 8, 1.6, 18, rise=0.25 * t_size, spread=0.35, order="OUTSIDE_IN",
                    t_out=TITLE_OUT, sweep=(TITLE_IN + 40, TITLE_IN + 78), align='CENTER')
title.matrix_world = on_card("t", 0, TITLE_Y_PX)
eyebrow = text_object("SH12_Title_Eyebrow", "QUANTUM SOURCE", F_MONO, eye_size, 1.9, M_TXT_C,
                      TITLE_IN, 0.9, 12, rise=0.3 * eye_size, t_out=TITLE_OUT, align='CENTER')
eyebrow.matrix_world = on_card("e", 0, TITLE_Y_PX + TITLE_CAP_PX + 40)
rule_w = 0.5 * 1.2 * W * 0.30
rule = line_curve("SH12_Title_Rule", [(-rule_w, 0, 0), (rule_w, 0, 0)], 0.9 * UPP, M_SHP_C)
rule.matrix_world = on_card("r", 0, TITLE_Y_PX - 42)
rule.data.bevel_factor_mapping_start = 'SPLINE'
# grows from the centre: animate both factors symmetrically
cu = rule.data
for f, s_, e_ in ((TITLE_IN + 26, 0.5, 0.5), (TITLE_IN + 56, 0.0, 1.0)):
    cu.bevel_factor_start = s_; cu.keyframe_insert("bevel_factor_start", frame=f)
    cu.bevel_factor_end = e_; cu.keyframe_insert("bevel_factor_end", frame=f)
key_fade(rule, [(TITLE_OUT[0], 1.0), (TITLE_OUT[1], 0.0)])
for ob in (title, eyebrow, rule):
    key_visible(ob, TITLE_IN - 1, TITLE_OUT[1] + 1)


# ---------------------------------------------------------------- 4. atom positions
S.frame_set(OFFSET + 190)
dg = bpy.context.evaluated_depsgraph_get()
atoms = []
for inst in dg.object_instances:
    if inst.object.name.startswith("rails_pi_shape") and inst.matrix_world.translation.z < 10:
        atoms.append(inst.matrix_world @ Vector((0, 0, 0.962 - 2.263)))
atoms = np.array([tuple(a) for a in atoms])
# dedupe (several GN paths can emit the same cell)
atoms = np.unique(np.round(atoms, 3), axis=0)
say("atoms", len(atoms))
cm190, _, _ = cam_at(OFFSET + 190)
right = cm190.col[0].xyz.normalized()
proj = atoms @ np.array(right)
wave_t = (proj - proj.min()) / (proj.max() - proj.min())

# ---------------------------------------------------------------- 5. atom glow
import bmesh
bm = bmesh.new()
lay = bm.verts.layers.float.new("wave_t")
for p, wt in zip(atoms, wave_t):
    r = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=ATOM_R)
    for v in r["verts"]:
        v.co += Vector(p)
        v[lay] = float(wt)
for f in bm.faces:
    f.smooth = True
me = bpy.data.meshes.new("SH12_AtomGlow"); bm.to_mesh(me); bm.free()
atom_ob = link(bpy.data.objects.new("SH12_AtomGlow", me))
camera_only(atom_ob, transmission=True, glossy=True)

ma, nt = new_mat("SH12_AtomGlow")
N, L = nt.nodes, nt.links


def m_(op, a, b=None, clamp=False):
    n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            L.new(v, n.inputs[i])
    return n.outputs[0]


def mr_(v, a, b, smooth=True):
    n = N.new("ShaderNodeMapRange"); n.clamp = True
    n.interpolation_type = 'SMOOTHSTEP' if smooth else 'LINEAR'
    L.new(v, n.inputs[0]); n.inputs[1].default_value = a; n.inputs[2].default_value = b
    return n.outputs[0]


fr = N.new("ShaderNodeValue"); fr.label = "frame (driver)"
drv = fr.outputs[0].driver_add("default_value").driver
drv.type = 'SCRIPTED'; drv.expression = "frame"
wt = N.new("ShaderNodeAttribute"); wt.attribute_type = 'GEOMETRY'; wt.attribute_name = "wave_t"
start = m_('MULTIPLY_ADD', wt.outputs["Fac"], float(WAVE_TRAVEL))
start.node.inputs[2].default_value = float(WAVE_START)      # wave_t * TRAVEL + START
local = m_('SUBTRACT', fr.outputs[0], start)
env = m_('MULTIPLY', mr_(local, 0.0, float(WAVE_RISE)),
         m_('SUBTRACT', 1.0, mr_(local, float(WAVE_RISE + WAVE_HOLD), float(WAVE_RISE + WAVE_HOLD + WAVE_FALL))))
geo = N.new("ShaderNodeNewGeometry")
dot = N.new("ShaderNodeVectorMath"); dot.operation = 'DOT_PRODUCT'
L.new(geo.outputs["Normal"], dot.inputs[0]); L.new(geo.outputs["Incoming"], dot.inputs[1])
facing = m_('ABSOLUTE', dot.outputs["Value"])
core = m_('MULTIPLY', m_('POWER', facing, 14.0), ATOM_CORE)
halo = m_('MULTIPLY', m_('POWER', facing, 3.0), ATOM_HALO)
inten = m_('MULTIPLY', m_('ADD', core, halo), env)
emA = N.new("ShaderNodeEmission"); emA.inputs["Color"].default_value = (1.0, 0.98, 0.95, 1)
L.new(inten, emA.inputs["Strength"])
trA = N.new("ShaderNodeBsdfTransparent")
adA = N.new("ShaderNodeAddShader"); L.new(emA.outputs[0], adA.inputs[0]); L.new(trA.outputs[0], adA.inputs[1])
oA = N.new("ShaderNodeOutputMaterial"); L.new(adA.outputs[0], oA.inputs["Surface"])
atom_ob.data.materials.append(ma)
wave_end = WAVE_START + WAVE_TRAVEL + WAVE_RISE + WAVE_HOLD + WAVE_FALL
key_visible(atom_ob, WAVE_START - 1, wave_end + 2)
say("atom wave", WAVE_START, "->", wave_end)


# ---------------------------------------------------------------- 6. callouts
def project(f, p):
    S.frame_set(f)
    v = world_to_camera_view(S, CAM, Vector(p))
    return v


def leader_gn(name, ob_a, ob_b, radius, f_in, f_out, mat):
    """Line from ob_a to ob_b, re-evaluated every frame (both can move).
    Draws on over f_in..f_in+10 and retracts toward the anchor over f_out-10..f_out."""
    ng = bpy.data.node_groups.new(name + "_GN", 'GeometryNodeTree')
    ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links
    N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    oa = N.new("GeometryNodeObjectInfo"); oa.inputs["Object"].default_value = ob_a; oa.transform_space = 'RELATIVE'
    ob_ = N.new("GeometryNodeObjectInfo"); ob_.inputs["Object"].default_value = ob_b; ob_.transform_space = 'RELATIVE'
    line = N.new("GeometryNodeCurvePrimitiveLine")
    L.new(oa.outputs["Location"], line.inputs["Start"]); L.new(ob_.outputs["Location"], line.inputs["End"])
    fr = N.new("GeometryNodeInputSceneTime").outputs["Frame"]

    def mr(a, b):
        n = N.new("ShaderNodeMapRange"); n.clamp = True; n.interpolation_type = 'SMOOTHSTEP'
        L.new(fr, n.inputs[0]); n.inputs[1].default_value = a; n.inputs[2].default_value = b
        return n.outputs[0]
    trim = N.new("GeometryNodeTrimCurve")
    L.new(line.outputs[0], trim.inputs["Curve"])
    fac_s = [s for s in trim.inputs if s.name == "Start" and s.bl_idname.startswith("NodeSocketFloatFactor")]
    fac_e = [s for s in trim.inputs if s.name == "End" and s.bl_idname.startswith("NodeSocketFloatFactor")]
    L.new(mr(f_out - 10, f_out), fac_s[0]); L.new(mr(f_in, f_in + 10), fac_e[0])
    prof = N.new("GeometryNodeCurvePrimitiveCircle"); prof.inputs["Resolution"].default_value = 8
    prof.inputs["Radius"].default_value = radius
    c2m = N.new("GeometryNodeCurveToMesh")
    L.new(trim.outputs[0], c2m.inputs["Curve"]); L.new(prof.outputs["Curve"], c2m.inputs["Profile Curve"])
    if "Fill Caps" in c2m.inputs:
        c2m.inputs["Fill Caps"].default_value = True
    sm = N.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = mat
    L.new(c2m.outputs[0], sm.inputs["Geometry"]); L.new(sm.outputs[0], go.inputs[0])
    ob = link(bpy.data.objects.new(name, bpy.data.meshes.new(name)))
    ob.data.materials.append(mat)
    ob.modifiers.new("Leader", 'NODES').node_group = ng
    ob["fade"] = 1.0
    camera_only(ob)
    return ob


def callout(tag, anchor, ref_f, label_xy, main, eyebrow_txt, f_in, f_out):
    """Anchor ring on the chip (world). The label lives in camera space at
    label_xy (normalised screen, y up); its depth follows the focus distance
    every frame so it stays sharp and keeps its pixel size. A GN leader joins
    anchor and label; a hairline runs under the label."""
    fd_ref = focus_dist(ref_f)
    upp = px_units(fd_ref)
    A = Vector(anchor)
    m, _, _ = cam_at(ref_f)
    depth_a = (A - m.translation).dot(-m.col[2].xyz.normalized())
    upp_a = px_units(depth_a)
    size_main = 26 / CAP * upp
    size_eye = 15 / CAP * upp
    lab = link(bpy.data.objects.new("SH12_%s_label" % tag, None))
    lab.parent = CAM
    lab.matrix_parent_inverse = Matrix()
    d = CAM.data
    for f in range(f_in - 1, f_out + 2):
        fdf = focus_dist(f)
        wd = fdf * d.sensor_width / d.lens
        hd = wd * S.render.resolution_y / S.render.resolution_x
        lab.location = ((label_xy[0] - 0.5) * wd, (label_xy[1] - 0.5) * hd, -fdf)
        k = fdf / fd_ref
        lab.scale = (k, k, k)
        lab.keyframe_insert("location", frame=f); lab.keyframe_insert("scale", frame=f)
    ring_e = facing_empty("SH12_%s_anchor" % tag, A)
    ring = link(bpy.data.objects.new("SH12_%s_ring" % tag, disc_mesh("SH12_ring", 7 * upp_a, 5.4 * upp_a)))
    ring.parent = ring_e; ring.data.materials.append(M_SHP_C); camera_only(ring)
    dot_ = link(bpy.data.objects.new("SH12_%s_dot" % tag, disc_mesh("SH12_dot", 2.2 * upp_a)))
    dot_.parent = ring_e; dot_.data.materials.append(M_SHP_C); camera_only(dot_)
    lead = leader_gn("SH12_%s_leader" % tag, ring_e, lab, 0.75 * upp_a, f_in + 4, f_out, M_SHP_W)
    t_main = text_object("SH12_%s_text" % tag, main, F_SEMI, size_main, 1.22, M_TXT_W,
                         f_in + 14, 0.7, 9, rise=0.2 * size_main, t_out=(f_out - 12, f_out))
    t_eye = text_object("SH12_%s_eyebrow" % tag, eyebrow_txt, F_MONO, size_eye, 1.6, M_TXT_C,
                        f_in + 18, 0.5, 8, rise=0.2 * size_eye, t_out=(f_out - 12, f_out))
    pad = 12 * upp
    side = 1
    for t, y in ((t_main, 11 * upp), (t_eye, -11 * upp - size_eye * CAP)):
        t.parent = lab
        t.location = (pad, y, 0)
    # label width from the evaluated text, then the horizontal hairline
    S.frame_set(f_out - 14)
    dgx = bpy.context.evaluated_depsgraph_get()
    wmax = 0.0
    for t in (t_main, t_eye):
        ev = t.evaluated_get(dgx)
        xs = [v[0] for v in ev.bound_box]
        wmax = max(wmax, max(xs) - min(xs))
    say(tag, "label width px", round(wmax / upp))
    hl = line_curve("SH12_%s_rule" % tag, [(0, 0, 0), (side * (wmax + 2 * pad), 0, 0)], 0.75 * upp, M_SHP_W)
    hl.parent = lab
    # timing
    for f, s in ((f_in, 0.0), (f_in + 8, 1.0)):
        ring_e.scale = (s, s, s); ring_e.keyframe_insert("scale", frame=f)
    draw_on(hl, f_in + 12, f_in + 24, f_out - 14, f_out - 2)
    for ob in (ring, dot_, lead, hl):
        key_fade(ob, [(f_out - 10, 1.0), (f_out, 0.0)])
    for ob in (ring, dot_, lead, hl, t_main, t_eye):
        key_visible(ob, f_in - 1, f_out + 1)
    return fd_ref


# photonic: anchor on a printed waveguide, picked near a screen target
S.frame_set(OFFSET + 125)
dg = bpy.context.evaluated_depsgraph_get()
wg = []
for inst in dg.object_instances:
    ob = inst.object
    if ob.type != 'MESH':
        continue
    mats = [m.name if m else "" for m in ob.data.materials]
    if "wave-guide-printed.001" not in mats:
        continue
    me_ = ob.data
    n = len(me_.vertices)
    if n == 0:
        continue
    co = np.zeros(n * 3); me_.vertices.foreach_get("co", co); co = co.reshape(-1, 3)[::7]
    mw = np.array(inst.matrix_world)
    wg.append((np.c_[co, np.ones(len(co))] @ mw.T)[:, :3])
wg = np.concatenate(wg)
wg = wg[wg[:, 2] > wg[:, 2].max() - 0.02]          # top surface of the guides
PH_REF = OFFSET + 100
PH_TARGET = (0.60, 0.40)                             # normalised screen (x right, y up)
S.frame_set(PH_REF)
best, bd = None, 1e9
for p in wg[::max(1, len(wg) // 40000)]:
    v = world_to_camera_view(S, CAM, Vector(p))
    d = (v.x - PH_TARGET[0]) ** 2 + (v.y - PH_TARGET[1]) ** 2
    if d < bd:
        bd, best = d, p
say("photonic anchor", np.round(best, 2), "screen", project(PH_REF, best))
callout("Photonic", best, PH_REF, (project(PH_REF, best).x, 0.085), "PHOTONIC QUBITS", "FLYING  ·  CONNECTIVITY",
        PHOTONIC_IN, PHOTONIC_OUT)

# atomic: a front-row atom near a screen target in the profile view
AT_REF = OFFSET + 195
AT_TARGET = 0.60
S.frame_set(AT_REF)
front = atoms[atoms[:, 1] < atoms[:, 1].min() + 0.5]
sx = np.array([world_to_camera_view(S, CAM, Vector(p)).x for p in front])
anchor_atom = front[int(np.argmin(abs(sx - AT_TARGET)))]
say("atomic anchor", np.round(anchor_atom, 2), "screen", project(AT_REF, anchor_atom))
callout("Atomic", anchor_atom, AT_REF, (project(AT_REF, anchor_atom).x, 0.70), "ATOMIC QUBITS", "STATIONARY  ·  STABILITY",
        ATOMIC_IN, ATOMIC_OUT)


# ---------------------------------------------------------------- 7. dive camera
with open(SH15_CAM_JSON) as fh:
    c15 = json.load(fh)


def m15(f):
    return PENTET_OFFSET_M @ Matrix(c15["frames"][str(f)]["m"])


PENTET_OFFSET_M = Matrix.Translation(PENTET_OFFSET)
F15 = c15["frames"]["50"]
cell15 = PENTET_OFFSET + Vector((2.6, 0.0, 0.962))      # SH_15's hero cell (atom height)
e0 = m15(50); e1 = m15(51)
fwd_e = -(e0.col[2].xyz).normalized()
fd_e = (cell15 - e0.translation).dot(fwd_e)
LENS1 = F15["lens"]
FSTOP1 = F15["fstop"] if F15["use_dof"] else 64.0          # SH_15 opens without DOF
say("SH_15 landing camera", F15["cam"], "lens", LENS1, "dof", F15["use_dof"])
P1, V1 = e0.translation, (e1.translation - e0.translation)
T1 = P1 + fwd_e * fd_e
T1n = e1.translation + (-(e1.col[2].xyz).normalized()) * fd_e
TV1 = T1n - T1

a0, _, _ = cam_at(DIVE_T0 - 1)
b0, lens0, _ = cam_at(DIVE_T0)
fd0 = focus_dist(DIVE_T0)
fd_m1 = focus_dist(DIVE_T0 - 1)
P0, V0 = b0.translation, b0.translation - a0.translation
T0p = P0 + (-(b0.col[2].xyz).normalized()) * fd0
T0m = a0.translation + (-(a0.col[2].xyz).normalized()) * fd_m1
TV0 = T0p - T0m
say("dive: start", tuple(round(v, 2) for v in P0), "speed", round(V0.length, 2), "u/f; dist", round((P1 - P0).length, 1))


def hermite(p0, m0, p1, m1, t):
    t2, t3 = t * t, t * t * t
    return (2 * t3 - 3 * t2 + 1) * p0 + (t3 - 2 * t2 + t) * m0 + (-2 * t3 + 3 * t2) * p1 + (t3 - t2) * m1


cd = bpy.data.cameras.new("Camera_Dive")
src = CAM.data
cd.lens = src.lens; cd.sensor_width = src.sensor_width; cd.sensor_fit = src.sensor_fit
cd.clip_start = 0.01; cd.clip_end = src.clip_end
cd.dof.use_dof = True
cdive = link(bpy.data.objects.new("Camera_Dive", cd))
cdive.rotation_mode = 'QUATERNION'
q_end = e0.to_quaternion()
fs0, fs1 = src.dof.aperture_fstop, FSTOP1
prev_q = None
for i in range(DIVE_LEN + 1):
    t = i / DIVE_LEN
    p = hermite(P0, V0 * DIVE_LEN, P1, V1 * DIVE_LEN, t)
    tg = hermite(T0p, TV0 * DIVE_LEN, T1, TV1 * DIVE_LEN, t)
    q = (tg - p).to_track_quat('-Z', 'Y')
    w = max(0.0, (t - 0.7) / 0.3); w = w * w * (3 - 2 * w)
    q = q.slerp(q_end, w)
    if prev_q is not None:
        q.make_compatible(prev_q)
    prev_q = q
    f = DIVE_T0 + i
    cdive.location = p; cdive.keyframe_insert("location", frame=f)
    cdive.rotation_quaternion = q; cdive.keyframe_insert("rotation_quaternion", frame=f)
    fwd_i = (q @ Vector((0, 0, -1)))
    cd.dof.focus_distance = max(0.05, (tg - p).dot(fwd_i)); cd.dof.keyframe_insert("focus_distance", frame=f)
    s = t * t * (3 - 2 * t)
    cd.dof.aperture_fstop = math.exp(math.log(fs0) * (1 - s) + math.log(fs1) * s)
    cd.dof.keyframe_insert("aperture_fstop", frame=f)
    cd.lens = lens0 + (LENS1 - lens0) * s; cd.keyframe_insert("lens", frame=f)
for fc in action_fcurves(cdive.animation_data.action) + action_fcurves(cd.animation_data.action):
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'
m_main = S.timeline_markers.new("CAM_main", frame=1); m_main.camera = CAM
m_dive = S.timeline_markers.new("CAM_dive", frame=DIVE_T0); m_dive.camera = cdive
S.camera = CAM
# check start continuity
mA, _, _ = cam_at(DIVE_T0)
S.frame_set(DIVE_T0)
say("dive start pos error", round((cdive.matrix_world.translation - mA.translation).length, 4))
S.frame_set(DIVE_T0 + DIVE_LEN)
say("dive end pos error vs SH_15 f50", round((cdive.matrix_world.translation - P1).length, 4))

# the rest of the chip sinks into the dark so the pentet floats alone, as SH_15 opens.
# delta_location only: the objects' own location keys are untouched.
DROP_START, DROP_Z = DIVE_T0 + 12, -160.0
dropped = []
for ob in bpy.data.collections["Chip_anim"].all_objects:
    if ob.name == "Unit_Linked.019" or (ob.parent and ob.parent.name in [o.name for o in bpy.data.collections["Chip_anim"].all_objects]):
        continue
    for f, z in ((DROP_START, 0.0), (DIVE_T0 + DIVE_LEN - 4, DROP_Z)):
        ob.delta_location = (0, 0, z); ob.keyframe_insert("delta_location", index=2, frame=f)
    for fc in action_fcurves(ob.animation_data.action):
        if fc.data_path == "delta_location":
            k0 = fc.keyframe_points[0]; k0.interpolation = 'CUBIC'; k0.easing = 'EASE_IN'
    dropped.append(ob.name)
say("chip drop on", len(dropped), "objects from", DROP_START)

# ---------------------------------------------------------------- 8. beat markers + notes
for name, f in (("CARD_10_start", CARD_START), ("TITLE_in", TITLE_IN), ("CHIP_v11_f001", OFFSET + 1),
                ("PHOTONIC_callout", PHOTONIC_IN), ("ATOMIC_callout", ATOMIC_IN), ("ATOM_wave", WAVE_START),
                ("BREAKUP_v11_f226", OFFSET + 226), ("LAND_on_SH15_f050", DIVE_T0 + DIVE_LEN)):
    S.timeline_markers.new(name, frame=f)
S["sh12_v12_build"] = json.dumps({k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float, str))})

S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT, relative_remap=True, compress=False)
say("saved", OUT, "frames", S.frame_start, "-", S.frame_end)
with open(os.path.join(HERE, "sh12_v12_build_log.txt"), "w") as fh:
    fh.write("\n".join(log) + "\n")
