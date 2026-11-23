"""Build slide-ready variants of the SH_18 architecture scene.

Run (one variant per call):
  blender --factory-startup -b sh_18_architecture_slide_base.blend --python sh18_slide_variants_build.py -- <variant> [preview]

variants: topdown | stack | hero
Each call saves sh_18_architecture_slide_<variant>.blend next to the base file (so the
relative texture paths keep working) and renders a transparent PNG to
08_renders/stills/slide/arch_slide_<variant>.png. "preview" renders at 35% with low samples.
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
VARIANT = argv[0] if argv else "topdown"
PREVIEW = "preview" in argv
FRAME = 3146

HERE = os.path.dirname(bpy.data.filepath)
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "08_renders", "stills", "slide"))
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
O = bpy.data.objects

# ---------------------------------------------------------------- GPU (factory startup resets it)
try:
    p = bpy.context.preferences.addons['cycles'].preferences
    p.compute_device_type = 'OPTIX'
    p.get_devices()
    for d in p.devices:
        d.use = d.type == 'OPTIX'
    scene.cycles.device = 'GPU'
except Exception as e:
    print("GPU setup failed:", e)

scene.frame_set(FRAME)
scene.frame_current = FRAME

# ---------------------------------------------------------------- common cleanup
# Timeline markers are bound to the animation cameras and would override scene.camera.
for mk in scene.timeline_markers:
    mk.camera = None

# Architecture sketch: over transparency its thin anti-aliased lines read faint.
# Boost alpha (x3, clamped) and emission so lines stay crisp on the slide black.
sk = bpy.data.materials['08b_Card_Architecture-simplified_still_v3_4K'].node_tree
img = next(n for n in sk.nodes if n.bl_idname == 'ShaderNodeTexImage')
bsdf = next(n for n in sk.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
amul = sk.nodes.new('ShaderNodeMath'); amul.name = 'SLIDE_alpha_boost'
amul.operation = 'MULTIPLY'; amul.use_clamp = True; amul.inputs[1].default_value = 2.0
sk.links.new(img.outputs['Color'], amul.inputs[0])
sk.links.new(amul.outputs[0], bsdf.inputs['Alpha'])
emul = next(n for n in sk.nodes if n.bl_idname == 'ShaderNodeMath' and n.name != 'SLIDE_alpha_boost')
emul.inputs[1].default_value = 10.0
for n in ['dashed-line', 'dashed-line.001', 'dashed-line.002', 'dashed-line.003']:
    O[n].hide_render = O[n].hide_viewport = True

O['Plane.009'].hide_render = True   # stray animated lattice above the logic card

# Logic card: freeze it (drop its fly-in animation) so we can place it per variant
card = O['Card 18 Compute-B']
card.animation_data_clear()
card.location = (2.646, 21.131, 2.695)
card.rotation_euler = (0.099, 0, 0)

scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '16'
scene.cycles.samples = 24 if PREVIEW else 256
scene.cycles.use_denoising = True
scene.render.use_motion_blur = False


def get_mat(name, color=(0.25, 0.9, 1.0), strength=3.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1)
    em.inputs['Strength'].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def new_camera(name, loc, target, lens=50.0, ortho_scale=None):
    cd = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(cam)
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if ortho_scale:
        cd.type = 'ORTHO'
        cd.ortho_scale = ortho_scale
    else:
        cd.lens = lens
    cd.clip_end = 1000
    scene.camera = cam
    return cam


def dashed_riser(name, x, y, z0, z1, dash=0.45, gap=0.35, radius=0.035, mat=None):
    """Vertical dashed light line built from thin boxes (one mesh)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    z = z0
    while z < z1:
        top = min(z + dash, z1)
        r = bmesh.ops.create_cube(bm, size=1.0)
        verts = r['verts']
        bmesh.ops.scale(bm, vec=(radius * 2, radius * 2, top - z), verts=verts)
        bmesh.ops.translate(bm, vec=(0, 0, (z + top) / 2), verts=verts)
        z = top + gap
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = (x, y, 0)
    scene.collection.objects.link(ob)
    if mat:
        me.materials.append(mat)
    ob.visible_shadow = False
    return ob


def fade_grid(inner=0.10, outer=0.42):
    """Radial alpha fade on the blueprint grid floor so it dissolves into the slide black."""
    m = bpy.data.materials['Blueprint Grid']
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial')
    bsdf = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    comb = nt.nodes.new('ShaderNodeCombineXYZ')
    ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = inner
    mr.inputs['From Max'].default_value = outer
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    mr.interpolation_type = 'SMOOTHSTEP'
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader')
    mix.name = 'SLIDE_grid_fade'
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    nt.links.new(sep.outputs['X'], comb.inputs['X'])
    nt.links.new(sep.outputs['Y'], comb.inputs['Y'])
    nt.links.new(comb.outputs[0], ln.inputs[0])
    nt.links.new(ln.outputs['Value'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(bsdf.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])


grid = O['Plane.001']

# ---------------------------------------------------------------- variants
if VARIANT == 'topdown':
    # Clean flat orthographic plan of the full system, no floor. Wide aspect.
    grid.hide_render = True
    new_camera('SLIDE_cam_topdown', (2.5, 5.6, 150), (2.5, 5.6, 0), ortho_scale=74)
    scene.render.resolution_x, scene.render.resolution_y = 3200, 1900

elif VARIANT == 'stack':
    # Exploded "hardware stack": logic layer floats above the hardware layer,
    # dashed risers tie each component to its part of the logic readout.
    grid.hide_render = True
    LIFT = 15.0
    card.location = (2.646, 12.0, LIFT)
    card.rotation_euler = (0.6, 0, 0)   # tilted toward camera so the readout stays legible
    riser_mat = get_mat('SLIDE_riser', strength=2.5)
    for nm, x, y in [('gen', -27.3, 9.0), ('cells', -10.5, 9.0), ('snspd', 4.0, 7.0), ('cpu', 21.3, 9.0)]:
        dashed_riser('SLIDE_riser_' + nm, x, y, 1.2, LIFT - 3.6, mat=riser_mat)
    for l in ('Area', 'Area.001', 'Area.002'):
        O[l].data.energy *= 0.3
    new_camera('SLIDE_cam_stack', (1.0, -66.0, 58.0), (1.0, 4.5, 7.0), lens=45)
    scene.render.resolution_x, scene.render.resolution_y = 2900, 2000

elif VARIANT == 'hero':
    # Low, grazing 3/4 view across the hardware with shallow depth of field;
    # grid floor kept but fades out radially into transparency.
    fade_grid(inner=0.04, outer=0.30)
    for l in ('Area', 'Area.001', 'Area.002'):
        O[l].data.energy *= 0.3
    card.hide_render = True
    O['Card_bg'].hide_render = True
    cam = new_camera('SLIDE_cam_hero', (-24.0, -46.0, 34.0), (-1.0, 4.0, 0.0), lens=50)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = O['Plane.002']   # entangling unit cells
    cam.data.dof.aperture_fstop = 2.0
    scene.render.resolution_x, scene.render.resolution_y = 2560, 2000

else:
    raise SystemExit("unknown variant " + VARIANT)

scene.render.resolution_percentage = 35 if PREVIEW else 100
tag = '_preview' if PREVIEW else ''
scene.render.filepath = os.path.join(OUT_DIR, f"arch_slide_{VARIANT}{tag}.png")

blend_out = os.path.join(HERE, f"sh_18_architecture_slide_{VARIANT}.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out, copy=True)
print("SAVED BLEND", blend_out)
bpy.ops.render.render(write_still=True)
print("RENDERED", scene.render.filepath)
