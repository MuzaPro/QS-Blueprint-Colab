"""SH_02 logic layer (Scene.001): wireframe 'blueprint' of the atomic chamber.

The wireframe lights up as a scan wave travelling outward from the qubit grid,
then decays to black, leaving only the logic layer.

Timing is controlled by ONE custom property on Scene.001:
    Scene.001["wire_reveal_frame"]   (frame the scan starts; set it to your cut frame)
Shape of the pulse: see node group values in material 'logic_wireframe'
(WIRE_SPEED, WIRE_DECAY, WIRE_GAIN).
"""
import bpy, math
from mathutils import Vector, Matrix

SC = bpy.data.scenes['Scene.001']
CENTER = Vector((0.0, 0.0, 1.8))
R_SHELL = 32.0          # sits inside the Cube.001 room (the atomic chamber is r=140; the lens blur hides the difference)
REVEAL_FRAME = 108

def get_coll(name, parent):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in parent.children:
        parent.children.link(c)
    return c

# NOTE: Cube.001 (room) and bg.001 (floor) are kept as they are: they stay black during the
# transition and set up the pull-back reveal at the end of the shot. Undo an earlier retire if present.
old = bpy.data.collections.get('old_bg_RETIRED.001')
if old:
    for o in list(old.objects):
        old.objects.unlink(o)
        if o.name not in SC.collection.children['Collection.001'].objects:
            bpy.data.collections['Collection.001'].objects.link(o)
    bpy.data.collections.remove(old)

coll = get_coll('logic_wireframe', SC.collection)
for o in list(coll.objects):
    bpy.data.objects.remove(o, do_unlink=True)

SC['wire_reveal_frame'] = REVEAL_FRAME
SC.id_properties_ui('wire_reveal_frame').update(min=1, max=400, description='Frame where the wireframe scan starts (match your cut to the logic layer)')

# ---------------------------------------------------------------- material
# One material per layer (object-attribute lookups were unreliable on curves).
# Every layer shares the same scan timing via the driver on 'wire_t'.
def build_mat(mat_name, layer_gain, layer_decay, layer_zfall):
    m = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    m.use_nodes = True
    m.cycles.emission_sampling = 'NONE'   # pure graphic: must not light the room / grid
    nt = m.node_tree; nt.nodes.clear()
    def N(t, loc, **kw):
        n = nt.nodes.new(t); n.location = loc
        for k, v in kw.items(): setattr(n, k, v)
        return n
    def M(op, a, b=None, loc=(0, 0), clamp=False):
        n = N('ShaderNodeMath', loc, operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: nt.links.new(v if isinstance(v, bpy.types.NodeSocket) else v.outputs[0], n.inputs[i])
        return n
    def V(name, val, loc):
        n = N('ShaderNodeValue', loc); n.name = n.label = name; n.outputs[0].default_value = val; return n

    out = N('ShaderNodeOutputMaterial', (1600, 0))
    t_node = V('wire_t', 0.0, (-1200, 300))           # frames since reveal (driven)
    fc = t_node.outputs[0].driver_add('default_value')
    drv = fc.driver; drv.type = 'SCRIPTED'
    var = drv.variables.new(); var.name = 'r'; var.type = 'SINGLE_PROP'
    var.targets[0].id_type = 'SCENE'; var.targets[0].id = SC; var.targets[0].data_path = '["wire_reveal_frame"]'
    drv.expression = 'frame - r'

    speed = V('WIRE_SPEED', 2.5, (-1200, 150))        # scene units per frame (~13 frames to reach the wall)
    decay = V('WIRE_DECAY', 9.0, (-1200, 0))          # afterglow time constant, frames
    gain = V('WIRE_GAIN', 1.0, (-1200, -150))         # overall brightness

    og = V('LAYER_GAIN', layer_gain, (-1200, -600))
    odk = V('LAYER_DECAY_SCALE', layer_decay, (-1200, -800))
    geo = N('ShaderNodeNewGeometry', (-1200, -350))
    sub = N('ShaderNodeVectorMath', (-1000, -350), operation='SUBTRACT'); sub.inputs[1].default_value = CENTER
    nt.links.new(geo.outputs['Position'], sub.inputs[0])
    dist = N('ShaderNodeVectorMath', (-850, -350), operation='LENGTH'); nt.links.new(sub.outputs[0], dist.inputs[0])

    arrive = M('DIVIDE', dist.outputs['Value'], speed, (-650, -300))       # frame the wave reaches this point
    tl = M('SUBTRACT', t_node, arrive, (-450, 100))                          # local time since the crest
    tl_pos = M('MAXIMUM', tl, 0.0, (-300, 100))
    attack = N('ShaderNodeMapRange', (-300, 300)); attack.inputs['From Min'].default_value = 0.0; attack.inputs['From Max'].default_value = 1.5
    attack.interpolation_type = 'SMOOTHSTEP'; nt.links.new(tl.outputs[0], attack.inputs['Value'])
    # crest: sharp flash
    crest = M('EXPONENT', M('MULTIPLY', M('DIVIDE', tl_pos, 2.0, (-150, 0)), -1.0, (0, 0)), None, (150, 0))
    crest = M('MULTIPLY', crest, 2.2, (300, 0))
    # afterglow: soft decay that reveals the space for a moment
    dk = M('MULTIPLY', decay, odk.outputs[0], (-300, -250))
    aft = M('EXPONENT', M('MULTIPLY', M('DIVIDE', tl_pos, dk, (-150, -200)), -1.0, (0, -200)), None, (150, -200))
    aft = M('MULTIPLY', aft, 0.55, (300, -200))
    pulse = M('ADD', crest, aft, (450, -100))
    pulse = M('MULTIPLY', pulse, attack.outputs['Result'], (600, -100))
    # hard safety fade: whole wireframe is fully black 60 frames after reveal
    kill = N('ShaderNodeMapRange', (600, 200)); kill.inputs['From Min'].default_value = 40; kill.inputs['From Max'].default_value = 60
    kill.inputs['To Min'].default_value = 1.0; kill.inputs['To Max'].default_value = 0.0; kill.interpolation_type = 'SMOOTHSTEP'
    nt.links.new(t_node.outputs[0], kill.inputs['Value'])
    pulse = M('MULTIPLY', pulse, kill.outputs['Result'], (800, -100))
    pulse = M('MULTIPLY', pulse, gain, (950, -100)); pulse.name = 'WIRE_STRENGTH'
    pulse = M('MULTIPLY', pulse, og.outputs[0], (1050, -100))
    # optional vertical falloff around the qubit plane (used by the ghost tweezers)
    ozf = V('LAYER_Z_FALLOFF', layer_zfall, (-1200, -1000))
    sepz = N('ShaderNodeSeparateXYZ', (-850, -550)); nt.links.new(sub.outputs[0], sepz.inputs[0])
    zf = M('EXPONENT', M('MULTIPLY', M('POWER', M('DIVIDE', sepz.outputs['Z'], 0.55, (-650, -550)), 2.0, (-500, -550)), -1.0, (-350, -550)), None, (-200, -550))
    zmix = N('ShaderNodeMix', (0, -600)); zmix.data_type = 'FLOAT'
    nt.links.new(ozf.outputs[0], zmix.inputs['Factor']); zmix.inputs['A'].default_value = 1.0
    # depth weighting: keep the in-focus band, suppress rows that the f/0.15 lens smears into haze
    cam = N('ShaderNodeCameraData', (-1200, -1200))
    vd = M('DIVIDE', M('SUBTRACT', cam.outputs['View Distance'], 11.6, (-1000, -1200)), 2.2, (-850, -1200))
    vd = M('EXPONENT', M('MULTIPLY', M('POWER', vd, 2.0, (-700, -1200)), -1.0, (-550, -1200)), None, (-400, -1200))
    zf = M('MULTIPLY', zf, vd, (-150, -700))
    nt.links.new(zf.outputs[0], zmix.inputs['B'])
    pulse = M('MULTIPLY', pulse, zmix.outputs['Result'], (1100, -150))

    em = N('ShaderNodeEmission', (1150, 0)); em.inputs['Color'].default_value = (0.80, 0.78, 1.0, 1)   # lavender-white, ties to the atomic chamber violet
    nt.links.new(pulse.outputs[0], em.inputs['Strength'])
    tr = N('ShaderNodeBsdfTransparent', (1150, 150))
    add = N('ShaderNodeAddShader', (1350, 0)); nt.links.new(em.outputs[0], add.inputs[0]); nt.links.new(tr.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs['Surface'])    # additive, never occludes the logic grid
    return m

# ---------------------------------------------------------------- curve builders
def curve_obj(name, polylines, width, cyclic=True, gain=1.0, decay=1.0, zfall=0.0):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = width; cu.bevel_resolution = 0; cu.use_fill_caps = False
    for pts in polylines:
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for p, co in zip(sp.points, pts): p.co = (co[0], co[1], co[2], 1.0)
        sp.use_cyclic_u = cyclic
    cu.materials.append(build_mat('wire_' + name.replace('wire_', ''), gain, decay, zfall))
    o = bpy.data.objects.new(name, cu); coll.objects.link(o)
    o.visible_shadow = False; o.visible_diffuse = False; o.visible_glossy = False
    o.visible_transmission = False; o.visible_volume_scatter = False
    return o

def circle(center, normal, r, seg=128):
    q = Vector(normal).normalized().to_track_quat('Z', 'Y')
    return [Vector(center) + q @ Vector((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), 0)) for i in range(seg)]

def sph(az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    return Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))

# shell: latitude rings every 10 deg (same as the glowing ribs in the atomic scene)
lat = []
for el in range(-80, 81, 10):
    e = math.radians(el)
    lat.append(circle(CENTER + Vector((0, 0, R_SHELL * math.sin(e))), (0, 0, 1), R_SHELL * math.cos(e), 192))
curve_obj('wire_shell_latitudes', lat, 0.04, gain=1.1)
# sparse meridians every 30 deg
mer = []
for az in []:
    n = Vector((math.cos(math.radians(az)), -math.sin(math.radians(az)), 0))
    mer.append(circle(CENTER, n, R_SHELL, 256))
pass  # meridians dropped: vertical bands fought the ghost tweezers

# viewports: same layout as atomic_chamber
PS = R_SHELL / 140.0
ports = [(sph(0, -4), 16.0 * PS)]
ports += [(sph(az, 0), 9.0 * PS) for az in range(45, 360, 45)]
for az in range(0, 360, 30):
    ports += [(sph(az + 15, -34), 5.5 * PS), (sph(az + 15, 34), 5.5 * PS)]
rings = []
for d, r in ports:
    c = CENTER + d * (R_SHELL - 0.1)
    rings += [circle(c, d, r, 96), circle(c, d, r * 1.3, 96)]
curve_obj('wire_ports', rings, 0.04, gain=0.2)
# bolt circle detail on the main window only
d, r = ports[0]; c = CENTER + d * (R_SHELL - 0.1)
q = d.to_track_quat('Z', 'Y')
bolts = [circle(c + q @ Vector((r * 1.15 * math.cos(a), r * 1.15 * math.sin(a), 0)), d, 0.08, 12)
         for a in [2 * math.pi * (i + 0.5) / 16 for i in range(16)]]
bolts = [[c2 for c2 in b] for b in bolts]
curve_obj('wire_port_main_bolts', bolts, 0.03, gain=0.2)

# objectives: step outlines + a few vertical edges so they read as volumes
def objective(top_z, flip):
    s = 1 if flip else -1          # lower objective grows downward from its top face
    loops, edges = [], []
    steps = [(9.0, 1.2), (13.0, 1.6), (19.0, 2.2), (26.0, 6.0)]   # from the lens outward
    z = top_z
    for r, h in steps:
        z0, z1 = z, z + s * h
        loops += [circle((0, 0, z0), (0, 0, 1), r, 160), circle((0, 0, z1), (0, 0, 1), r, 160)]
        for i in range(12):
            a = 2 * math.pi * i / 12
            edges.append([(r * math.cos(a), r * math.sin(a), z0), (r * math.cos(a), r * math.sin(a), z1)])
        z = z1
    loops.append(circle((0, 0, top_z), (0, 0, 1), 6.5, 128))   # front lens
    loops.append(circle((0, 0, top_z), (0, 0, 1), 3.2, 96))
    return loops, edges

lo_loops, lo_edges = objective(-11.4, flip=False)
hi_loops, hi_edges = objective(15.6, flip=True)
curve_obj('wire_objective_lower', lo_loops, 0.02, gain=1.5)
pass
pass  # upper objective dropped: sits right above the camera and blooms into a blob
pass

# ghost tweezers: hairline columns through every qubit site (crisp at the focal plane,
# melting into blur above/below). They hand over from the red beams of the atomic scene.
n, half = 12, 2.44
cols = []
for i in range(n):
    for j in range(n):
        x = -half + 2 * half * i / (n - 1); y = -half + 2 * half * j / (n - 1)
        cols.append([(x, y, -11.4), (x, y, CENTER.z - 0.12)])
        cols.append([(x, y, CENTER.z + 0.12), (x, y, 15.6)])   # gap so lines never cross the glyphs
curve_obj('wire_ghost_tweezers', cols, 0.0022, cyclic=False, gain=0.9, decay=2.2, zfall=1.0)

old_m = bpy.data.materials.get('logic_wireframe')
if old_m and old_m.users == 0: bpy.data.materials.remove(old_m)
print('LOGIC WIREFRAME OK, reveal frame', SC['wire_reveal_frame'])
