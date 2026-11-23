"""Build the interior racks, low-poly tray columns and heavy door hinge for the
animated RSG monster (SH_9).

Runs on any file that contains RSG_MONSTER_ANIMATED, psi_RSG.DOOR and Tray_Stack:
  - 04_assets/props/ai_models/RSG_MONSTER_ANIMATED.blend  (the asset / work-up file)
  - 05_shots/SH_9/SH_09_factory_lights_reveal_v05.blend    (the shot)
Idempotent: everything it makes is prefixed RSGI_ and rebuilt in place.

Usage (headless):
  blender -b --factory-startup --python build_rsg_monster_animated.py -- <file.blend> [--nosave]

Spaces used below
  box-local : RSG_MONSTER_ANIMATED's local space (x = depth, -x is the open face,
              y = width, z = up; scaled 1.252 in world).
  rack space: same axes, metres, origin = Tray_Stack origin (hero tray slot).
"""
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if argv and argv[0].endswith(".blend"):
    bpy.ops.wm.open_mainfile(filepath=argv[0])
SAVE = globals().get("SAVE", "--nosave" not in argv)

D = bpy.data
S = bpy.context.scene
box = D.objects["RSG_MONSTER_ANIMATED"]
door = D.objects["psi_RSG.DOOR"]
stack = D.objects["Tray_Stack"]
coll = box.users_collection[0]

# ----------------------------------------------------------------- settings
COL_Y = (-0.64, 0.0, 0.64)      # column centres across the width (rack space, m)
ROW_X = (0.0, 0.42)             # front row (animated stack) and back row (depth)
TOP_Z = 1.83                    # highest tray top allowed (rack space)
HINGE_P = (-1.12, 1.25)         # door pivot in box-local XY (just outside the +Y front corner)
DOOR_FACE = -1.041              # closed door slab outer face, box-local x (slab edge at y 1.177)
HINGE_Z = (0.45, 1.20, 1.95)    # hinge centres, box-local z
OPEN_DEG = -125.0               # door angle while open (negative swings it out)

# ----------------------------------------------------------------- helpers
def mat(name):
    m = D.materials.get(name)
    if m is None:
        raise KeyError("material missing: " + name)
    return m

def get_obj(name, data=None):
    ob = D.objects.get(name)
    if ob is None:
        ob = D.objects.new(name, data)
        coll.objects.link(ob)
    elif data is not None:
        old = ob.data
        ob.data = data
        if old and old.users == 0:
            D.meshes.remove(old)
    return ob

class MB:
    """Tiny mesh builder: boxes and cylinders with a material index each."""
    def __init__(self):
        self.bm = bmesh.new()
        self.mats = []

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _tag(self, verts, m):
        mi = self._mi(m)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = mi

    def box(self, lo, hi, m):
        lo, hi = Vector(lo), Vector(hi)
        size, c = hi - lo, (hi + lo) / 2
        M = Matrix.Translation(c) @ Matrix.Diagonal((size.x, size.y, size.z, 1))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)
        self._tag(r["verts"], m)

    def cyl(self, c, r, z0, z1, m, seg=16, axis='Z'):
        M = Matrix.Translation((c[0], c[1], (z0 + z1) / 2))
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg,
                                    radius1=r, radius2=r, depth=z1 - z0, matrix=M)
        self._tag(res["verts"], m)

    def mesh(self, name):
        me = D.meshes.get(name) or D.meshes.new(name)
        me.clear_geometry()
        me.materials.clear()
        for m in self.mats:           # slots BEFORE to_mesh (see agent guide)
            me.materials.append(m)
        self.bm.to_mesh(me)
        self.bm.free()
        for p in me.polygons:
            p.use_smooth = False
        return me

def add_bevel(ob, width):
    bv = ob.modifiers.get("RSGI_Bevel") or ob.modifiers.new("RSGI_Bevel", 'BEVEL')
    bv.width = width; bv.segments = 1; bv.limit_method = 'ANGLE'
    bv.harden_normals = False

def parent_keep(ob, parent, world):
    ob.parent = parent
    ob.matrix_parent_inverse = parent.matrix_world.inverted() @ world
    ob.matrix_basis = Matrix.Identity(4)

M_METAL = mat("Old Metal")
M_BLACK = mat("Plastic Black 5")
M_NICKEL = mat("TC3_Nickel_Satin")
M_NAVY = mat("TC3_Soldermask_Navy")
M_GOLD = mat("TC3_Gold_Plate")

S.frame_set(S.frame_start)
bpy.context.view_layer.update()

# rack space = Tray_Stack's world frame (stack itself is static in this shot)
RACK_W = stack.matrix_world.copy()
box_to_rack = RACK_W.inverted() @ box.matrix_world
def b2r(p):
    return box_to_rack @ Vector(p)

# stack pitch / slot 0 from the TrayStack modifier inputs
mod = next(m for m in stack.modifiers if m.type == 'NODES')
def gn_in(m, name):
    sid = next(i.identifier for i in m.node_group.interface.items_tree
               if i.item_type == 'SOCKET' and i.in_out == 'INPUT' and i.name == name)
    return getattr(m.properties.inputs, sid).value
src = gn_in(mod, "Tray")
zs = [v.co.z for v in src.data.vertices]
TRAY_H = max(zs) - min(zs)
PITCH = TRAY_H + gn_in(mod, "Gap")
COUNT = gn_in(mod, "Count")
HERO = gn_in(mod, "Hero Slot")
Z0 = -HERO * PITCH                       # slot 0 centre, rack space
N_FULL = int((TOP_Z - Z0 - max(zs)) // PITCH) + 1
print("@@stack pitch %.4f count %d hero %d full column %d" % (PITCH, COUNT, HERO, N_FULL))

# interior bounds (box-local -> rack space)
FLOOR = b2r((0, 0, 0.353)).z
CEIL = b2r((0, 0, 2.211)).z
WALL_LO = b2r((0, -0.964, 0)).y
WALL_HI = b2r((0, 0.964, 0)).y

# ============================================================ TASK 2: trays
# low-poly tray (same axes/size as Tray-connector: rail on -X, ~0.146 x 0.29)
mb = MB()
mb.box((-0.073, -0.145, -0.0084), (-0.059, 0.145, 0.0084), M_NICKEL)   # back rail
mb.box((-0.059, -0.145, -0.0084), (0.073, 0.145, -0.0030), M_NICKEL)   # cold plate
mb.box((-0.056, -0.140, -0.0030), (0.068, -0.016, -0.0014), M_NAVY)    # board A
mb.box((-0.056, 0.016, -0.0030), (0.068, 0.140, -0.0014), M_NAVY)      # board B
mb.box((-0.052, -0.015, -0.0030), (-0.004, 0.015, 0.0006), M_GOLD)     # chip carrier
tray_lp = get_obj("RSGI_Tray_LowPoly", mb.mesh("RSGI_Tray_LowPoly_mesh"))
tray_lp.parent = None
tray_lp.matrix_world = Matrix.Translation((src.matrix_world.translation.x + 0.4,
                                           src.matrix_world.translation.y, 0))
tray_lp.hide_render = True
tray_lp.hide_set(True)

# points: one per static tray, rack space
pts = []
for cx in ROW_X:
    for cy in COL_Y:
        hero_col = (cx == 0.0 and cy == 0.0)
        first = COUNT if hero_col else 0      # hero column: only above the animated stack
        for k in range(first, N_FULL):
            pts.append((cx, cy, Z0 + k * PITCH))
pme = D.meshes.get("RSGI_TrayColumns_pts") or D.meshes.new("RSGI_TrayColumns_pts")
pme.clear_geometry()
pme.from_pydata(pts, [], [])
cols = get_obj("RSGI_TrayColumns", pme)
parent_keep(cols, box, RACK_W)

# node group: instance a tray on every point
ng = D.node_groups.get("RSGI_TrayColumns") or D.node_groups.new("RSGI_TrayColumns", 'GeometryNodeTree')
ng.nodes.clear(); ng.interface.clear()
ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
s_tray = ng.interface.new_socket("Tray", in_out='INPUT', socket_type='NodeSocketObject')
s_tray.description = "Object instanced on every point (swap for a more detailed tray if needed)"
s_show = ng.interface.new_socket("Show", in_out='INPUT', socket_type='NodeSocketBool')
s_show.default_value = True
ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
n_in = ng.nodes.new("NodeGroupInput"); n_out = ng.nodes.new("NodeGroupOutput")
n_oi = ng.nodes.new("GeometryNodeObjectInfo"); n_oi.transform_space = 'ORIGINAL'
n_oi.inputs["As Instance"].default_value = True
n_iop = ng.nodes.new("GeometryNodeInstanceOnPoints")
n_sw = ng.nodes.new("GeometryNodeSwitch"); n_sw.input_type = 'GEOMETRY'
L = ng.links.new
L(n_in.outputs["Tray"], n_oi.inputs["Object"])
L(n_in.outputs["Geometry"], n_iop.inputs["Points"])
L(n_oi.outputs["Geometry"], n_iop.inputs["Instance"])
L(n_in.outputs["Show"], n_sw.inputs["Switch"])
L(n_iop.outputs["Instances"], n_sw.inputs["True"])
L(n_sw.outputs[0], n_out.inputs["Geometry"])
for i, n in enumerate((n_in, n_oi, n_iop, n_sw, n_out)):
    n.location = (i * 220, 0)
gm = cols.modifiers.get("RSGI_TrayColumns") or cols.modifiers.new("RSGI_TrayColumns", 'NODES')
gm.node_group = ng
sid = next(i.identifier for i in ng.interface.items_tree
           if i.item_type == 'SOCKET' and i.in_out == 'INPUT' and i.name == "Tray")
getattr(gm.properties.inputs, sid).value = tray_lp

# ============================================================ TASK 1: racks
mb = MB()
T_HALF_Y, T_HALF_X = 0.145, 0.074
UP_T = 0.012          # upright plate thickness
UP_D = 0.034          # angle flange depth
base_top = Z0 - 0.0084 - 0.004
top_bot = Z0 + (N_FULL - 1) * PITCH + 0.0084 + 0.004
x_lo = min(ROW_X) - T_HALF_X - 0.03
x_hi = max(ROW_X) + T_HALF_X + 0.03
y_lo = min(COL_Y) - T_HALF_Y - UP_T - 0.03
y_hi = max(COL_Y) + T_HALF_Y + UP_T + 0.03

# base plate + feet, top cold plate + hangers
mb.box((x_lo, y_lo, FLOOR), (x_hi, y_hi, base_top - 0.03), M_METAL)
mb.box((x_lo + 0.01, y_lo + 0.01, base_top - 0.03), (x_hi - 0.01, y_hi - 0.01, base_top), M_NICKEL)
mb.box((x_lo, y_lo, top_bot + 0.008), (x_hi, y_hi, top_bot + 0.045), M_METAL)
mb.box((x_lo + 0.01, y_lo + 0.01, top_bot), (x_hi - 0.01, y_hi - 0.01, top_bot + 0.008), M_NICKEL)
for hx in (x_lo + 0.06, x_hi - 0.06):
    for hy in (y_lo + 0.06, (y_lo + y_hi) / 2, y_hi - 0.06):
        mb.cyl((hx, hy), 0.022, top_bot + 0.045, CEIL, M_METAL, seg=10)

# per column: two L-angle uprights on the short ends; flange at the back so
# trays can slide in from the open (-X) face
for cx in ROW_X:
    for cy in COL_Y:
        for sgn in (-1, 1):
            y_in = cy + sgn * (T_HALF_Y + 0.004)
            y_out = y_in + sgn * UP_T
            ya, yb = sorted((y_in, y_out))
            mb.box((cx - T_HALF_X - 0.004, ya, base_top), (cx + T_HALF_X + 0.004, yb, top_bot), M_METAL)
            # back flange (tray stop)
            fa, fb = sorted((y_in - sgn * UP_D, y_out))
            mb.box((cx + T_HALF_X + 0.004, fa, base_top), (cx + T_HALF_X + 0.004 + UP_T, fb, top_bot), M_METAL)
        # tie bars between the two uprights at the back
        for tz in (base_top + 0.35, (base_top + top_bot) / 2, top_bot - 0.35):
            mb.box((cx + T_HALF_X + 0.004, cy - T_HALF_Y, tz - 0.015), (cx + T_HALF_X + 0.004 + UP_T, cy + T_HALF_Y, tz + 0.015), M_METAL)

# services chase on the free +Y side: vertical pipes + clamp bands
chase_y0 = y_hi + 0.06
chase_y1 = WALL_HI - 0.05
pipes = [(0.05, 0.055, M_METAL), (0.20, 0.040, M_METAL), (0.33, 0.060, M_METAL),
         (0.12, 0.030, M_BLACK), (0.26, 0.030, M_BLACK), (0.40, 0.025, M_BLACK)]
for i, (dx, r, m) in enumerate(pipes):
    py = chase_y0 + r + (i * 0.37) % max(chase_y1 - chase_y0 - 2 * r, 0.1)
    mb.cyl((x_lo + dx, py), r, FLOOR, CEIL, m, seg=12)
for bz in (FLOOR + 0.35, (FLOOR + CEIL) / 2, CEIL - 0.35):
    mb.box((x_lo - 0.01, chase_y0 - 0.02, bz - 0.025), (x_lo + 0.48, chase_y0 + 0.01, bz + 0.025), M_METAL)

# backplane bulkhead behind the back row
bk_x = max(ROW_X) + T_HALF_X + 0.09
mb.box((bk_x, WALL_LO, FLOOR), (bk_x + 0.03, WALL_HI, CEIL), M_METAL)
for sz in (FLOOR + 0.5, (FLOOR + CEIL) / 2, CEIL - 0.5):
    mb.box((bk_x - 0.04, WALL_LO, sz - 0.03), (bk_x, WALL_HI, sz + 0.03), M_METAL)

rack = get_obj("RSGI_Rack", mb.mesh("RSGI_Rack_mesh"))
parent_keep(rack, box, RACK_W)
add_bevel(rack, 0.004)

# ============================================================ TASK 3: door
hinge = D.objects.get("RSGI_Door_Hinge")
if hinge is None:
    # first run: capture the closed pose, drop the old keys, hinge the door
    S.frame_set(498)
    bpy.context.view_layer.update()
    closed_w = door.matrix_world.copy()
    if door.animation_data and door.animation_data.action:
        door.animation_data.action.use_fake_user = True      # keep the original keys
        door.animation_data.action.name = "psi_RSG.DOOR_original_keys"
        door.animation_data.action = None
    hinge = D.objects.new("RSGI_Door_Hinge", None)
    coll.objects.link(hinge)
    hinge.empty_display_type = 'SINGLE_ARROW'; hinge.empty_display_size = 0.6
else:
    hinge.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    closed_w = door.matrix_world.copy()
hinge.parent = box
hinge.matrix_parent_inverse = Matrix.Identity(4)
hinge.location = (HINGE_P[0], HINGE_P[1], 0.0)
hinge.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()
door.parent = hinge
door.matrix_parent_inverse = Matrix.Identity(4)
door.matrix_basis = hinge.matrix_world.inverted() @ closed_w
bpy.context.view_layer.update()

# hinge keys: hold open, slow heavy start, accelerate into the slam,
# small rebound, settle. Latches (DOOR.001 / .002) keep their own keys (469-496).
o = math.radians(OPEN_DEG)
keys = [(275, o, 'AUTO_CLAMPED'), (392, o, 'AUTO_CLAMPED'),
        (420, o * 0.86, 'AUTO'), (442, o * 0.45, 'AUTO'),
        (456, 0.0, 'VECTOR'), (461, math.radians(-2.4), 'AUTO_CLAMPED'),
        (466, 0.0, 'VECTOR'), (470, math.radians(-0.6), 'AUTO_CLAMPED'),
        (474, 0.0, 'AUTO_CLAMPED')]
if hinge.animation_data and hinge.animation_data.action:
    act = hinge.animation_data.action
    D.actions.remove(act)
hinge.animation_data_create()
for f, v, _ in keys:
    hinge.rotation_euler.z = v
    hinge.keyframe_insert("rotation_euler", index=2, frame=f)
act = hinge.animation_data.action
act.name = "RSGI_Door_Hinge_swing"
fcs = []
for l in act.layers:
    for s in l.strips:
        for cb in s.channelbags:
            fcs += list(cb.fcurves)
fc = next(c for c in fcs if c.data_path == "rotation_euler")
for kp, (_, _, ht) in zip(fc.keyframe_points, keys):
    kp.interpolation = 'BEZIER'
    kp.handle_left_type = ht; kp.handle_right_type = ht
fc.update()

# hinge hardware, modelled in box-local space at the closed pose
px, py = HINGE_P
KN_R, PIN_R = 0.075, 0.032
fixed = MB()
moving = MB()
for zc in HINGE_Z:
    for z0, z1 in ((zc - 0.17, zc - 0.075), (zc + 0.075, zc + 0.17)):      # frame knuckles
        fixed.cyl((px, py), KN_R, z0, z1, M_METAL, seg=20)
        fixed.box((px, py - 0.05, z0), (-0.93, py + 0.07, z1), M_METAL)          # bracket arm
        fixed.box((-0.99, 1.0, z0 - 0.03), (-0.84, py + 0.07, z1 + 0.03), M_METAL)  # weld pad
    fixed.cyl((px, py), PIN_R, zc - 0.21, zc + 0.21, M_NICKEL, seg=16)     # pin
    fixed.cyl((px, py), 0.05, zc + 0.21, zc + 0.235, M_NICKEL, seg=6)      # nut
    fixed.cyl((px, py), 0.05, zc - 0.235, zc - 0.21, M_NICKEL, seg=6)
    # door knuckle + strap arm that wraps onto the door face
    moving.cyl((px, py), KN_R, zc - 0.07, zc + 0.07, M_METAL, seg=20)
    moving.box((DOOR_FACE - 0.07, 0.55, zc - 0.07), (DOOR_FACE, py, zc + 0.07), M_METAL)
# continuous hinge stile on the door face, hinge side
moving.box((DOOR_FACE - 0.045, 0.95, 0.10), (DOOR_FACE, 1.177, 2.25), M_METAL)
# hinge post welded to the frame
fixed.box((-0.99, 1.137, 0.05), (-0.80, 1.20, 2.33), M_METAL)

hw_fixed = get_obj("RSGI_Hinge_Frame", fixed.mesh("RSGI_Hinge_Frame_mesh"))
parent_keep(hw_fixed, box, box.matrix_world)
add_bevel(hw_fixed, 0.006)

hw_door = get_obj("RSGI_Hinge_Door", moving.mesh("RSGI_Hinge_Door_mesh"))
# closed pose: door world = closed_w, so door-relative = closed_w^-1 @ box world
hw_door.parent = door
hw_door.matrix_parent_inverse = closed_w.inverted() @ box.matrix_world
hw_door.matrix_basis = Matrix.Identity(4)
add_bevel(hw_door, 0.006)

S.frame_set(S.frame_start)
print("@@ points", len(pts), "rack verts", len(rack.data.vertices))
if SAVE:
    bpy.ops.wm.save_mainfile()
    print("@@ SAVED", bpy.data.filepath)
print("BUILT OK")
