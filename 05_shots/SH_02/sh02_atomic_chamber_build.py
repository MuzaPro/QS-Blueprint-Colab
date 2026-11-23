"""SH_02 atomic-scale chamber build. Only touches the atomic scene ('Scene')."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

SC = bpy.data.scenes['Scene']
CENTER = Vector((0.0, 0.0, 1.8))   # atom plane centre
R_SHELL = 140.0
rng = random.Random(7)

# ---------------------------------------------------------------- helpers
def get_coll(name, parent):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in parent.children:
        parent.children.link(c)
    return c

def new_obj(name, mesh, coll):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    o = bpy.data.objects.new(name, mesh)
    coll.objects.link(o)
    return o

def mesh_from_bm(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me

def mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    return m, nt, out

def N(nt, t, loc=(0, 0), **kw):
    n = nt.nodes.new(t); n.location = loc
    for k, v in kw.items():
        setattr(n, k, v)
    return n

def L(nt, a, b):
    if isinstance(a, bpy.types.Node): a = a.outputs[0]
    if isinstance(b, bpy.types.Node): b = b.inputs[0]
    nt.links.new(a, b)

def math_node(nt, op, a=None, b=None, c=None, loc=(0, 0), clamp=False):
    n = N(nt, 'ShaderNodeMath', loc, operation=op, use_clamp=clamp)
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: L(nt, v, n.inputs[i])
    if isinstance(c, (int, float)): n.inputs[2].default_value = c
    elif c is not None: L(nt, c, n.inputs[2])
    return n

# ---------------------------------------------------------------- 1. retire old background
retired = get_coll('old_bg_RETIRED', SC.collection)
for name in ('Cube', 'bg'):
    o = bpy.data.objects.get(name)
    if not o: continue
    for c in list(o.users_collection):
        c.objects.unlink(o)
    retired.objects.link(o)
lc = SC.view_layers[0].layer_collection.children.get('old_bg_RETIRED')
if lc: lc.exclude = True

chamber = get_coll('atomic_chamber', SC.collection)

# ---------------------------------------------------------------- 2. materials
# Chamber wall: dark violet-steel, slightly glossy so beams leave soft smeared reflections,
# plus faint latitude ribs so the far wall reads as a curved vessel, not a flat void.
m_wall, nt, out = mat('chamber_wall')
tc = N(nt, 'ShaderNodeTexCoord', (-1200, 0))
sep = N(nt, 'ShaderNodeSeparateXYZ', (-1000, 0)); L(nt, tc.outputs['Object'], sep.inputs[0])
norm = N(nt, 'ShaderNodeVectorMath', (-1000, -200), operation='NORMALIZE'); L(nt, tc.outputs['Object'], norm.inputs[0])
sepn = N(nt, 'ShaderNodeSeparateXYZ', (-800, -200)); L(nt, norm.outputs[0], sepn.inputs[0])
lat = math_node(nt, 'ARCSINE', sepn.outputs['Z'], loc=(-600, -200))
ribs = math_node(nt, 'MULTIPLY', lat, 18.0, loc=(-400, -200))          # one rib every 10 deg
ribs = math_node(nt, 'COSINE', ribs, loc=(-250, -200))
ribs = math_node(nt, 'POWER', math_node(nt, 'ABSOLUTE', ribs, loc=(-100, -200)), 120.0, loc=(50, -200))
# equator band glow, fading toward the poles
eq = math_node(nt, 'ABSOLUTE', sepn.outputs['Z'], loc=(-600, -450))
eq = math_node(nt, 'SUBTRACT', 1.0, eq, loc=(-450, -450))
eq = math_node(nt, 'POWER', eq, 6.0, loc=(-300, -450))
noise = N(nt, 'ShaderNodeTexNoise', (-600, 250)); noise.inputs['Scale'].default_value = 0.05
noise.inputs['Detail'].default_value = 4
L(nt, tc.outputs['Object'], noise.inputs['Vector'])
glow = math_node(nt, 'MULTIPLY', ribs, 0.35, loc=(200, -200))
glow = math_node(nt, 'ADD', glow, math_node(nt, 'MULTIPLY', eq, 0.25, loc=(-150, -450)), loc=(350, -300))
glow = math_node(nt, 'MULTIPLY', glow, noise.outputs['Fac'], loc=(500, -300))
glow = math_node(nt, 'MULTIPLY', glow, 0.3, loc=(650, -300))
glow.name = 'WALL_GLOW_STRENGTH'
bsdf = N(nt, 'ShaderNodeBsdfPrincipled', (600, 150))
bsdf.inputs['Base Color'].default_value = (0.018, 0.014, 0.024, 1)
bsdf.inputs['Metallic'].default_value = 0.85
bsdf.inputs['Roughness'].default_value = 0.32
bsdf.inputs['Emission Color'].default_value = (0.32, 0.16, 0.55, 1)
L(nt, glow.outputs[0], bsdf.inputs['Emission Strength'])
L(nt, bsdf.outputs[0], out.inputs['Surface'])

# Port window: dark centre, violet halo toward the rim (echoes the SH_1 window look).
m_port, nt, out = mat('chamber_port_glass')
tc = N(nt, 'ShaderNodeTexCoord', (-900, 0))
off = N(nt, 'ShaderNodeVectorMath', (-700, 0), operation='SUBTRACT'); off.inputs[1].default_value = (0.0, 0.0, 0.0)
L(nt, tc.outputs['Object'], off.inputs[0])  # port mesh is unit radius
sepg = N(nt, 'ShaderNodeSeparateXYZ', (-550, 0)); L(nt, off.outputs[0], sepg.inputs[0])
cmb = N(nt, 'ShaderNodeCombineXYZ', (-400, 0)); L(nt, sepg.outputs['X'], cmb.inputs['X']); L(nt, sepg.outputs['Y'], cmb.inputs['Y'])
rad = N(nt, 'ShaderNodeVectorMath', (-250, 0), operation='LENGTH'); L(nt, cmb.outputs[0], rad.inputs[0])
rad2 = math_node(nt, 'MULTIPLY', rad.outputs['Value'], 1.0, loc=(-100, 0))
ramp = N(nt, 'ShaderNodeValToRGB', (50, 0)); L(nt, rad2.outputs[0], ramp.inputs[0])
e = ramp.color_ramp.elements
e[0].position = 0.0;  e[0].color = (0, 0, 0, 1)
e[1].position = 1.0;  e[1].color = (0.05, 0.03, 0.08, 1)
el = e.new(0.55); el.color = (0.02, 0.01, 0.03, 1)
el = e.new(0.86); el.color = (0.42, 0.22, 0.7, 1)
em = N(nt, 'ShaderNodeEmission', (350, 0)); em.inputs['Strength'].default_value = 3.5
em.name = 'PORT_EMISSION'
L(nt, ramp.outputs['Color'], em.inputs['Color'])
gl = N(nt, 'ShaderNodeBsdfGlossy', (350, 200)); gl.inputs['Color'].default_value = (0.02, 0.02, 0.025, 1); gl.inputs['Roughness'].default_value = 0.08
add = N(nt, 'ShaderNodeAddShader', (600, 0)); L(nt, em.outputs[0], add.inputs[0]); L(nt, gl.outputs[0], add.inputs[1])
L(nt, add.outputs[0], out.inputs['Surface'])

# Flange: brushed steel, dark.
m_flange, nt, out = mat('chamber_flange')
b = N(nt, 'ShaderNodeBsdfPrincipled', (500, 0))
b.inputs['Base Color'].default_value = (0.09, 0.08, 0.1, 1); b.inputs['Metallic'].default_value = 1.0
b.inputs['Roughness'].default_value = 0.28
L(nt, b.outputs[0], out.inputs['Surface'])

# Objective housing: black anodised.
m_obj, nt, out = mat('objective_housing')
b = N(nt, 'ShaderNodeBsdfPrincipled', (500, 0))
b.inputs['Base Color'].default_value = (0.03, 0.025, 0.03, 1); b.inputs['Metallic'].default_value = 0.6
b.inputs['Roughness'].default_value = 0.22
L(nt, b.outputs[0], out.inputs['Surface'])

# Objective front lens: dark glass with a faint warm glow where the beams leave it.
m_lens, nt, out = mat('objective_lens')
tc = N(nt, 'ShaderNodeTexCoord', (-700, 0))
grad = N(nt, 'ShaderNodeTexGradient', (-500, 0), gradient_type='SPHERICAL')
mp = N(nt, 'ShaderNodeMapping', (-600, 0)); mp.inputs['Scale'].default_value = (0.18, 0.18, 0.18)
L(nt, tc.outputs['Object'], mp.inputs['Vector']); L(nt, mp.outputs[0], grad.inputs['Vector'])
g2 = math_node(nt, 'POWER', grad.outputs['Fac'], 2.5, loc=(-300, 0))
g2 = math_node(nt, 'MULTIPLY', g2, 0.8, loc=(-150, 0))
b = N(nt, 'ShaderNodeBsdfPrincipled', (300, 0))
b.inputs['Base Color'].default_value = (0.01, 0.01, 0.012, 1); b.inputs['Roughness'].default_value = 0.05
b.inputs['Coat Weight'].default_value = 1.0
b.inputs['Emission Color'].default_value = (1.0, 0.12, 0.08, 1)
L(nt, g2.outputs[0], b.inputs['Emission Strength'])
L(nt, b.outputs[0], out.inputs['Surface'])

# Untrapped background atoms: per-instance brightness from attribute 'glow'.
m_free, nt, out = mat('untrapped_atom')
at = N(nt, 'ShaderNodeAttribute', (-400, 0), attribute_type='INSTANCER', attribute_name='glow')
st = math_node(nt, 'MULTIPLY', at.outputs['Fac'], 1.1, loc=(-150, 0)); st.name = 'FREE_ATOM_STRENGTH'
em = N(nt, 'ShaderNodeEmission', (200, 0)); em.inputs['Color'].default_value = (1.0, 0.78, 0.72, 1)
L(nt, st.outputs[0], em.inputs['Strength'])
tr = N(nt, 'ShaderNodeBsdfTransparent', (200, 150))
ad = N(nt, 'ShaderNodeAddShader', (450, 0)); L(nt, em.outputs[0], ad.inputs[0]); L(nt, tr.outputs[0], ad.inputs[1])
L(nt, ad.outputs[0], out.inputs['Surface'])  # additive only: never occludes the beams

# Trap-cloud haze (faint residual MOT glow around the array).
m_haze, nt, out = mat('trap_cloud_haze')
tc = N(nt, 'ShaderNodeTexCoord', (-900, 0))
ln = N(nt, 'ShaderNodeVectorMath', (-700, -150), operation='LENGTH'); L(nt, tc.outputs['Object'], ln.inputs[0])
fall = math_node(nt, 'DIVIDE', ln.outputs['Value'], 5.0, loc=(-550, -150))
fall = math_node(nt, 'POWER', fall, 2.0, loc=(-400, -150))
fall = math_node(nt, 'MULTIPLY', fall, -1.0, loc=(-250, -150))
fall = math_node(nt, 'EXPONENT', fall, loc=(-100, -150))
tm = N(nt, 'ShaderNodeValue', (-900, 250)); tm.name = 'haze_time'
nz = N(nt, 'ShaderNodeTexNoise', (-500, 150), noise_dimensions='4D'); nz.inputs['Scale'].default_value = 0.35; nz.inputs['Detail'].default_value = 3
L(nt, tc.outputs['Object'], nz.inputs['Vector'])
den = math_node(nt, 'MULTIPLY', fall, math_node(nt, 'POWER', nz.outputs['Fac'], 2.0, loc=(-300, 150)), loc=(50, 0))
den = math_node(nt, 'MULTIPLY', den, 0.025, loc=(200, 0)); den.name = 'HAZE_STRENGTH'
vol = N(nt, 'ShaderNodeEmission', (450, 0)); vol.inputs['Color'].default_value = (1.0, 0.25, 0.15, 1)
L(nt, den.outputs[0], vol.inputs['Strength'])
L(nt, vol.outputs[0], out.inputs['Volume'])
# animate noise W with frames (slow churn)
w = nz.inputs['W']
fc = w.driver_add('default_value'); fc.driver.expression = 'frame*0.004'

# ---------------------------------------------------------------- 3. chamber shell (sphere, inward)
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=48, radius=R_SHELL)
bmesh.ops.reverse_faces(bm, faces=bm.faces)
shell = new_obj('chamber_shell', mesh_from_bm('chamber_shell', bm), chamber)
shell.location = CENTER
shell.data.materials.append(m_wall)

# ---------------------------------------------------------------- 4. viewports on the shell
def port_mesh(r):
    bm = bmesh.new()
    # recessed window disc
    bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=r, matrix=Matrix.Translation((0, 0, -0.05)))
    disc_faces = list(bm.faces)
    # flange ring = torus-ish tube built from a lathe
    prof = [(r * 1.0, -0.05), (r * 1.0, 0.0), (r * 1.22, 0.0), (r * 1.22, 0.025), (r * 1.3, 0.025), (r * 1.3, -0.04)]
    verts_ring = []
    seg = 64
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ca, sa = math.cos(a), math.sin(a)
        verts_ring.append([bm.verts.new((pr * ca, pr * sa, pz)) for pr, pz in prof])
    for i in range(seg):
        A, B = verts_ring[i], verts_ring[(i + 1) % seg]
        for j in range(len(prof) - 1):
            bm.faces.new((A[j], B[j], B[j + 1], A[j + 1]))
    # bolt heads on flange
    for i in range(16):
        a = 2 * math.pi * (i + 0.5) / 16
        m = Matrix.Translation((r * 1.26 * math.cos(a), r * 1.26 * math.sin(a), 0.03))
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=r * 0.035, radius2=r * 0.035, depth=r * 0.03, matrix=m)
    me = bpy.data.meshes.new(f'port_r{r}')
    bm.to_mesh(me)
    for i, p in enumerate(me.polygons):
        p.material_index = 0 if i < len(disc_faces) else 1
        p.use_smooth = i >= len(disc_faces)
    bm.free()
    me.materials.append(m_port); me.materials.append(m_flange)
    return me

def place_on_shell(o, direction, inset=0.0):
    inset = o.get('inset', inset)
    d = direction.normalized()
    o.location = CENTER + d * (R_SHELL - inset)
    # local +Z points to the centre
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = (-d).to_track_quat('Z', 'Y')

def sph(az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    return Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))

unit = port_mesh(1.0)
def port(name, r):
    o = new_obj(name, unit, chamber); o.scale = (r, r, r); o['inset'] = 0.07 * r + 0.25; return o
# main window straight behind the array in the opening frames (echo of SH_1's last frame)
place_on_shell(port('port_main', 16.0), sph(0, -4), 0.3)
k = 0
for az in range(45, 360, 45):
    place_on_shell(port(f'port_eq_{k:02d}', 9.0), sph(az, 0), 0.3); k += 1
for az in range(0, 360, 30):
    place_on_shell(port(f'port_low_{k:02d}', 5.5), sph(az + 15, -34), 0.3); k += 1
    place_on_shell(port(f'port_high_{k:02d}', 5.5), sph(az + 15, 34), 0.3); k += 1

# ---------------------------------------------------------------- 5. objectives above / below the array
def objective_mesh(flip=False):
    bm = bmesh.new()
    s = -1 if flip else 1
    steps = [(26.0, 6.0), (19.0, 2.2), (13.0, 1.6), (9.0, 1.2)]   # (radius, height)
    z = 0.0
    for r, h in steps:
        bmesh.ops.create_cone(bm, cap_ends=True, segments=96, radius1=r, radius2=r * 0.985, depth=h,
                              matrix=Matrix.Translation((0, 0, s * (z + h / 2))) @ (Matrix.Rotation(math.pi, 4, 'X') if flip else Matrix()))
        # fine knurl/groove ring near each step edge
        bmesh.ops.create_cone(bm, cap_ends=True, segments=96, radius1=r * 1.01, radius2=r * 1.01, depth=0.12,
                              matrix=Matrix.Translation((0, 0, s * (z + h * 0.8))))
        z += h
    me = bpy.data.meshes.new('objective_flip' if flip else 'objective')
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    me.materials.append(m_obj)
    return me, z

def lens_mesh(r, sag):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=24, radius=1.0)
    for v in bm.verts:
        v.co.x *= r; v.co.y *= r; v.co.z *= sag
    me = bpy.data.meshes.new('objective_front_lens'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(m_lens)
    return me

lo_me, lo_h = objective_mesh(False)
lo_top = -11.4                       # beams end at ~-12.7, buried inside
lo = new_obj('objective_lower', lo_me, chamber); lo.location = (0, 0, lo_top - lo_h)
bev = lo.modifiers.new('bevel', 'BEVEL'); bev.width = 0.08; bev.segments = 2; bev.limit_method = 'ANGLE'
lens_lo = new_obj('objective_lower_lens', lens_mesh(6.5, 0.7), chamber); lens_lo.location = (0, 0, lo_top)

hi_me, hi_h = objective_mesh(True)
hi_bot = 15.6                        # beams end at ~16.2, buried inside
hi = new_obj('objective_upper', hi_me, chamber); hi.location = (0, 0, hi_bot + hi_h)
bev = hi.modifiers.new('bevel', 'BEVEL'); bev.width = 0.08; bev.segments = 2; bev.limit_method = 'ANGLE'
lens_hi = new_obj('objective_upper_lens', lens_mesh(6.5, 0.7), chamber); lens_hi.location = (0, 0, hi_bot)

# ---------------------------------------------------------------- 6. untrapped atoms (geo nodes)
pts = []
while len(pts) < 260:
    p = Vector((rng.gauss(0, 3.6), rng.gauss(0, 3.6), rng.gauss(0, 2.4)))
    if p.y < -3.0 and rng.random() > 0.15:   # keep the camera side sparse (avoids huge bokeh)
        continue
    # keep a little clearance around the trapped plane so they don't read as grid sites
    if abs(p.z) < 0.8 and abs(p.x) < 3.4 and abs(p.y) < 3.4:
        continue
    if p.length > 8.0:        # camera never comes closer than ~11 to centre
        continue
    pts.append(p)
me = bpy.data.meshes.new('untrapped_atoms_pts'); me.from_pydata([tuple(p) for p in pts], [], [])
free = new_obj('untrapped_atoms', me, chamber); free.location = CENTER

ng = bpy.data.node_groups.get('UntrappedAtoms')
if ng: bpy.data.node_groups.remove(ng)
ng = bpy.data.node_groups.new('UntrappedAtoms', 'GeometryNodeTree')
ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
s_amp = ng.interface.new_socket('Drift', in_out='INPUT', socket_type='NodeSocketFloat'); s_amp.default_value = 0.6
s_spd = ng.interface.new_socket('Drift Speed', in_out='INPUT', socket_type='NodeSocketFloat'); s_spd.default_value = 0.08
s_rad = ng.interface.new_socket('Atom Radius', in_out='INPUT', socket_type='NodeSocketFloat'); s_rad.default_value = 0.026
gn = ng.nodes
def set_rv(n, lo, hi):
    f = [i for i in n.inputs if i.type == 'VALUE' and i.name in ('Min', 'Max')]
    f[0].default_value = lo; f[1].default_value = hi
def fval(n):
    return next(o for o in n.outputs if o.type == 'VALUE' and o.enabled)
gi = gn.new('NodeGroupInput'); gi.location = (-1200, 0)
go = gn.new('NodeGroupOutput'); go.location = (900, 0)
m2p = gn.new('GeometryNodeMeshToPoints'); m2p.location = (-1000, 0)
pos = gn.new('GeometryNodeInputPosition'); pos.location = (-1200, -300)
tim = gn.new('GeometryNodeInputSceneTime'); tim.location = (-1200, -450)
mul_t = gn.new('ShaderNodeMath'); mul_t.operation = 'MULTIPLY'; mul_t.location = (-1000, -450)
nz = gn.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.location = (-800, -300)
nz.inputs['Scale'].default_value = 0.6; nz.inputs['Detail'].default_value = 1.0
sub = gn.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.location = (-600, -300); sub.inputs[1].default_value = (0.5, 0.5, 0.5)
scl = gn.new('ShaderNodeVectorMath'); scl.operation = 'SCALE'; scl.location = (-450, -300)
setp = gn.new('GeometryNodeSetPosition'); setp.location = (-400, 0)
ico = gn.new('GeometryNodeMeshIcoSphere'); ico.location = (-400, -550); ico.inputs['Subdivisions'].default_value = 2
rsc = gn.new('FunctionNodeRandomValue'); rsc.location = (-400, -750); rsc.data_type = 'FLOAT'; set_rv(rsc, 0.55, 1.25)
inst = gn.new('GeometryNodeInstanceOnPoints'); inst.location = (-150, 0)
rgl = gn.new('FunctionNodeRandomValue'); rgl.location = (-150, -350); rgl.data_type = 'FLOAT'; set_rv(rgl, 0.08, 1.0)
rgl.inputs['Seed'].default_value = 3
pw = gn.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.location = (50, -350); pw.inputs[1].default_value = 2.2
store = gn.new('GeometryNodeStoreNamedAttribute'); store.location = (250, 0)
store.data_type = 'FLOAT'; store.domain = 'INSTANCE'; store.inputs['Name'].default_value = 'glow'
smat = gn.new('GeometryNodeSetMaterial'); smat.location = (550, 0)
lk = ng.links.new
lk(gi.outputs['Geometry'], m2p.inputs['Mesh'])
lk(m2p.outputs['Points'], setp.inputs['Geometry'])
lk(pos.outputs['Position'], nz.inputs['Vector'])
lk(tim.outputs['Seconds'], mul_t.inputs[0]); lk(gi.outputs['Drift Speed'], mul_t.inputs[1])
lk(mul_t.outputs[0], nz.inputs['W'])
lk(nz.outputs['Color'], sub.inputs[0])
lk(sub.outputs[0], scl.inputs[0]); lk(gi.outputs['Drift'], scl.inputs['Scale'])
lk(scl.outputs[0], setp.inputs['Offset'])
lk(gi.outputs['Atom Radius'], ico.inputs['Radius'])
lk(setp.outputs['Geometry'], inst.inputs['Points'])
lk(ico.outputs['Mesh'], inst.inputs['Instance'])
lk(fval(rsc), inst.inputs['Scale'])
lk(inst.outputs['Instances'], store.inputs['Geometry'])
lk(fval(rgl), pw.inputs[0]); lk(pw.outputs[0], store.inputs['Value'])
lk(store.outputs['Geometry'], smat.inputs['Geometry'])
smat.inputs['Material'].default_value = m_free
lk(smat.outputs['Geometry'], go.inputs['Geometry'])
mod = free.modifiers.new('UntrappedAtoms', 'NODES'); mod.node_group = ng


# ---------------------------------------------------------------- 7. trap-cloud haze volume
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=10.0)
haze = new_obj('trap_cloud_haze', mesh_from_bm('trap_cloud_haze', bm), chamber)
haze.location = CENTER; haze.data.materials.append(m_haze)
haze.visible_shadow = False

# ---------------------------------------------------------------- 8. tweezer beam profile (atomic scene only)
# Scene.001 also instances the 'tweezers' object, so give 'Scene' its own copy.
src = bpy.data.objects['tweezers']
tw = bpy.data.objects.get('tweezers_atomic')
if tw: bpy.data.objects.remove(tw, do_unlink=True)
tw = src.copy(); tw.data = src.data.copy(); tw.name = 'tweezers_atomic'; tw.data.name = 'tweezers_atomic'
for c in src.users_collection: c.objects.link(tw)
tw.hide_render = True; tw.hide_viewport = False
m_tw = bpy.data.materials['tweezers-volume'].copy(); m_tw.name = 'tweezers-atomic'
nt = m_tw.node_tree
em = next(n for n in nt.nodes if n.type == 'EMISSION')
base_strength = em.inputs['Strength'].default_value
tc = N(nt, 'ShaderNodeTexCoord', (-900, -200))
sz = N(nt, 'ShaderNodeSeparateXYZ', (-700, -200)); L(nt, tc.outputs['Object'], sz.inputs[0])
az = math_node(nt, 'DIVIDE', sz.outputs['Z'], 9.0, loc=(-550, -200))
az = math_node(nt, 'POWER', math_node(nt, 'ABSOLUTE', az, loc=(-420, -200)), 2.0, loc=(-300, -200))
az = math_node(nt, 'EXPONENT', math_node(nt, 'MULTIPLY', az, -1.0, loc=(-180, -200)), loc=(-60, -200))
prof = math_node(nt, 'MULTIPLY_ADD', az, 0.55, loc=(80, -200)); prof.inputs[2].default_value = 0.45   # 0.45 at ends -> 1.0 at focus
# tight hot spot at the focus (where the atom sits)
hz = math_node(nt, 'DIVIDE', sz.outputs['Z'], 0.35, loc=(-550, -420))
hz = math_node(nt, 'POWER', math_node(nt, 'ABSOLUTE', hz, loc=(-420, -420)), 2.0, loc=(-300, -420))
hz = math_node(nt, 'EXPONENT', math_node(nt, 'MULTIPLY', hz, -1.0, loc=(-180, -420)), loc=(-60, -420))
prof = math_node(nt, 'MULTIPLY_ADD', hz, 0.6, prof, loc=(230, -300))
st = math_node(nt, 'MULTIPLY', prof, base_strength, loc=(380, -300)); st.name = 'BEAM_STRENGTH'
L(nt, st.outputs[0], em.inputs['Strength'])
tw.data.materials.clear(); tw.data.materials.append(m_tw)
for n in bpy.data.node_groups['Tweezers'].nodes:
    if n.type == 'OBJECT_INFO' and n.inputs['Object'].default_value == src:
        n.inputs['Object'].default_value = tw

print('BUILD OK', len(pts), 'free atoms')
