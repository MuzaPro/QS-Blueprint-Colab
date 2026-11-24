"""SH_18 v11: replace the logic card's pop-up-from-the-floor with a feathered,
empty-driven alpha wipe (left -> right with a slight bottom-left lean).

Run:
  blender --factory-startup -b sh_18_architecture_intro_10.blend --python sh18_v11_card_reveal_build.py
  -> saves sh_18_architecture_intro_11.blend (v10 stays untouched)

Setup it creates
- Empty "Card_Reveal_Effector": follows the card with a Child Of constraint
  (location + rotation only, NO scale: the card is scaled 34.6 x 8.3 x 34.6,
  inheriting that would shear the wipe). So the wipe sits in the card's own
  plane and survives the 3069-3138 tilt.
  * its local X position is keyed: the wipe edge = the empty's YZ plane
  * rotate it about local Z to change direction (0 = pure left->right,
    -90 deg = bottom->top). Default lean is REVEAL_ANGLE_DEG.
  * custom props on the empty, driven (drivers) into both shaders:
      feather       width of the soft edge in metres
      edge_glow     strength of the faint bright line riding the edge
- Node group "CardRevealMask" (shader): outputs Mask (1 = visible) and Edge,
  used in materials "Card 18 Compute-B" (logic video) and "Material" (Card_bg).
- Card 18 Compute-B: the 2797 keys (below floor, the pop-up) are removed; the
  card now sits at its rest pose from the start. Keys 2835 / 3069 / 3138 kept.
"""
import bpy, math, os

HERE = os.path.dirname(bpy.data.filepath)
OUT = os.path.join(HERE, "sh_18_architecture_intro_11.blend")
O = bpy.data.objects
scene = bpy.context.scene

CARD = O["Card 18 Compute-B"]
BG = O["Card_bg"]
EMPTY_NAME = "Card_Reveal_Effector"

REVEAL_START, REVEAL_END = 2806, 2858   # old pop-up ran 2797-2835; card enters frame ~2814
REVEAL_ANGLE_DEG = -18.0                # lean: bottom edge leads (rises out of the architecture)
FEATHER = 9.0                           # metres of soft edge (card is ~63 m wide)
EDGE_GLOW = 0.25
X_START, X_END = -42.0, 44.0            # empty local X, relative to card centre (card spans ~ +-33)
EDGE_COLOR = (0.613, 0.947, 0.986, 1.0) # photon cyan


def fcurves_of(idb):
    ad = idb.animation_data
    if not ad or not ad.action:
        return []
    try:
        return list(ad.action.fcurves)
    except Exception:
        out = []
        for l in ad.action.layers:
            for s in l.strips:
                for cb in s.channelbags:
                    out += list(cb.fcurves)
        return out


# ---------------------------------------------------------------- 1. drop the pop-up keys
for fc in fcurves_of(CARD):
    for k in list(fc.keyframe_points):
        if abs(k.co[0] - 2797) < 0.5:
            fc.keyframe_points.remove(k)
    fc.update()
print("card keys now:", sorted({round(k.co[0]) for fc in fcurves_of(CARD) for k in fc.keyframe_points}))

# ---------------------------------------------------------------- 2. effector empty
emp = O.get(EMPTY_NAME)
if emp is None:
    emp = bpy.data.objects.new(EMPTY_NAME, None)
    CARD.users_collection[0].objects.link(emp)
emp.empty_display_type = 'SINGLE_ARROW'
emp.empty_display_size = 8.0
emp.rotation_euler = (0.0, 0.0, math.radians(REVEAL_ANGLE_DEG))
emp.hide_render = True
for c in list(emp.constraints):
    emp.constraints.remove(c)
con = emp.constraints.new('CHILD_OF')
con.name = "follow card (no scale)"
con.target = CARD
con.use_scale_x = con.use_scale_y = con.use_scale_z = False
con.set_inverse_pending = False
con.inverse_matrix.identity()
emp["feather"] = FEATHER
emp["edge_glow"] = EDGE_GLOW
emp.id_properties_ui("feather").update(min=0.01, soft_max=30.0, description="soft edge width (m)")
emp.id_properties_ui("edge_glow").update(min=0.0, soft_max=3.0, description="bright line on the wipe edge")

if emp.animation_data:
    emp.animation_data_clear()
emp.location = (X_START, 0, 0)
emp.keyframe_insert("location", index=0, frame=REVEAL_START)
emp.location = (X_END, 0, 0)
emp.keyframe_insert("location", index=0, frame=REVEAL_END)
for fc in fcurves_of(emp):
    kps = fc.keyframe_points
    kps[0].interpolation = 'SINE'; kps[0].easing = 'EASE_IN_OUT'   # gentle start + settle
    fc.update()

# ---------------------------------------------------------------- 3. mask node group
NG = "CardRevealMask"
ng = bpy.data.node_groups.get(NG)
if ng:
    bpy.data.node_groups.remove(ng)
ng = bpy.data.node_groups.new(NG, 'ShaderNodeTree')
ng.interface.new_socket("Feather", in_out='INPUT', socket_type='NodeSocketFloat').default_value = FEATHER
ng.interface.new_socket("Mask", in_out='OUTPUT', socket_type='NodeSocketFloat')
ng.interface.new_socket("Edge", in_out='OUTPUT', socket_type='NodeSocketFloat')
N, L = ng.nodes, ng.links
gi = N.new('NodeGroupInput'); gi.location = (-900, 0)
go = N.new('NodeGroupOutput'); go.location = (500, 0)
tc = N.new('ShaderNodeTexCoord'); tc.location = (-900, 250); tc.object = emp
sep = N.new('ShaderNodeSeparateXYZ'); sep.location = (-700, 250)
L.new(tc.outputs["Object"], sep.inputs[0])
half = N.new('ShaderNodeMath'); half.operation = 'MULTIPLY'; half.inputs[1].default_value = 0.5; half.location = (-700, 0)
L.new(gi.outputs["Feather"], half.inputs[0])
negh = N.new('ShaderNodeMath'); negh.operation = 'MULTIPLY'; negh.inputs[1].default_value = -1.0; negh.location = (-500, -100)
L.new(half.outputs[0], negh.inputs[0])
# x < 0 (behind the empty, already passed) -> visible
mr = N.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHERSTEP'; mr.location = (-300, 200)
L.new(sep.outputs["X"], mr.inputs["Value"])
L.new(negh.outputs[0], mr.inputs["From Min"])
L.new(half.outputs[0], mr.inputs["From Max"])
mr.inputs["To Min"].default_value = 1.0
mr.inputs["To Max"].default_value = 0.0
L.new(mr.outputs["Result"], go.inputs["Mask"])
# edge: 4*m*(1-m) peaks at the middle of the feather
inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; inv.location = (-100, 0)
L.new(mr.outputs["Result"], inv.inputs[1])
m1 = N.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.location = (100, 0)
L.new(mr.outputs["Result"], m1.inputs[0]); L.new(inv.outputs[0], m1.inputs[1])
m2 = N.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 4.0; m2.location = (300, 0)
L.new(m1.outputs[0], m2.inputs[0])
pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0; pw.location = (300, -150)
L.new(m2.outputs[0], pw.inputs[0])
L.new(pw.outputs[0], go.inputs["Edge"])


def drive(sock, prop):
    fc = sock.driver_add("default_value")
    d = fc.driver; d.type = 'AVERAGE'
    v = d.variables.new(); v.name = "v"; v.type = 'SINGLE_PROP'
    v.targets[0].id_type = 'OBJECT'; v.targets[0].id = emp
    v.targets[0].data_path = f'["{prop}"]'


def add_mask(mat_name, alpha_from, edge_mix):
    """alpha_from: socket currently feeding Alpha, or a constant if None."""
    mt = bpy.data.materials[mat_name].node_tree
    N, L = mt.nodes, mt.links
    for n in [n for n in N if n.name.startswith("REVEAL_")]:
        N.remove(n)
    bsdf = next(n for n in N if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    x, y = bsdf.location.x - 450, bsdf.location.y - 650
    g = N.new('ShaderNodeGroup'); g.node_tree = ng; g.name = g.label = "REVEAL_mask"; g.location = (x - 250, y)
    drive(g.inputs["Feather"], "feather")
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.name = mul.label = "REVEAL_alpha"; mul.location = (x, y)
    a_in = bsdf.inputs["Alpha"]
    if a_in.links:
        src = a_in.links[0].from_socket
        L.remove(a_in.links[0])
        L.new(src, mul.inputs[0])
    else:
        mul.inputs[0].default_value = a_in.default_value
    L.new(g.outputs["Mask"], mul.inputs[1])
    L.new(mul.outputs[0], a_in)
    if edge_mix:
        # faint cyan line on the wipe edge, added to whatever emission is there
        eg = N.new('ShaderNodeMath'); eg.operation = 'MULTIPLY'; eg.name = eg.label = "REVEAL_edge_strength"; eg.location = (x, y - 200)
        L.new(g.outputs["Edge"], eg.inputs[0]); drive(eg.inputs[1], "edge_glow")
        em = N.new('ShaderNodeEmission'); em.name = em.label = "REVEAL_edge_emit"; em.location = (x + 200, y - 200)
        em.inputs["Color"].default_value = EDGE_COLOR
        L.new(eg.outputs[0], em.inputs["Strength"])
        out = next(n for n in N if n.bl_idname == 'ShaderNodeOutputMaterial')
        surf_src = out.inputs["Surface"].links[0].from_socket
        add = N.new('ShaderNodeAddShader'); add.name = add.label = "REVEAL_edge_add"; add.location = (out.location.x - 200, out.location.y - 150)
        L.remove(out.inputs["Surface"].links[0])
        L.new(surf_src, add.inputs[0]); L.new(em.outputs[0], add.inputs[1])
        L.new(add.outputs[0], out.inputs["Surface"])


add_mask("Card 18 Compute-B", None, edge_mix=False)
add_mask("Material", None, edge_mix=True)    # edge line lives on the dark bg plate

scene.frame_set(scene.frame_start)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
