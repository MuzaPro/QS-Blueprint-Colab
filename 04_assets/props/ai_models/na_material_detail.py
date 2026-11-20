"""Procedural surface detail for the neutral-atom QC materials (NA_*).

Usage inside Blender (file already open):
    LEVEL = 'clean'   # or 'fugly'
    OVERRIDES = {}    # optional {mat_name: dict(col=(r,g,b), metal=.., rough=..)}
    exec(open(".../na_material_detail.py").read())

Each target material is rebuilt from scratch. The original base values (colour,
metallic, roughness, ...) are stored once in m["na_base"], so re-running is
idempotent. OVERRIDES replace the base for this run only.

Layers (all in object space, so the stacked parts share one consistent pattern):
  macro roughness noise | smudges / fingerprints | sparse fine scratches
  orange-peel bump | (fugly) dust on upward faces | (fugly) AO grime in corners
"""
import bpy

LEVEL = globals().get("LEVEL", "clean")
OVERRIDES = globals().get("OVERRIDES", {})

LEVELS = {
    'clean': dict(rv=0.07, smudge=0.55, scratch=0.4, dust=0.0, grime=0.0, peel=0.012),
    'fugly': dict(rv=0.10, smudge=0.75, scratch=0.8, dust=0.55, grime=0.7, peel=0.03),
}
# material -> (kind, pattern scale multiplier)
TARGETS = globals().get("TARGETS") or {
    'NA_graphite': ('paint', 1.0), 'NA_logo_panel': ('paint', 1.3), 'NA_panel_grey': ('paint', 2.0),
    'NA_black': ('paint', 3.0), 'NA_extrusion': ('metal', 1.5), 'NA_stainless': ('metal', 3.0),
    'NA_stainless_b': ('metal', 3.0), 'NA_alu': ('metal', 3.0), 'NA_panel_alu': ('metal', 2.0),
    'NA_glass_door': ('glass', 1.0), 'NA_panel_replaced': ('paint', 1.0),
}

def _base(m):
    if "na_base" not in m:
        p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        g = lambda k: p.inputs[k].default_value
        m["na_base"] = [*g('Base Color')[:3], g('Metallic'), g('Roughness'),
                        g('Transmission Weight'), g('IOR'), g('Coat Weight')]
    return list(m["na_base"])

def build(m, kind, sc, P, seed):
    b = _base(m)
    col, metal, rough, trans, ior, coat = b[0:3], b[3], b[4], b[5], b[6], b[7]
    ov = OVERRIDES.get(m.name, {})
    col = ov.get('col', col); metal = ov.get('metal', metal); rough = ov.get('rough', rough)
    coat = ov.get('coat', coat)
    nt = m.node_tree; N = nt.nodes; L = nt.links
    N.clear()
    out = N.new('ShaderNodeOutputMaterial'); p = N.new('ShaderNodeBsdfPrincipled')
    p.inputs['IOR'].default_value = ior; p.inputs['Coat Weight'].default_value = coat
    L.new(p.outputs[0], out.inputs['Surface'])
    co = N.new('ShaderNodeTexCoord').outputs['Object']

    def link(sock, v):
        if isinstance(v, bpy.types.NodeSocket): L.new(v, sock)
        else: sock.default_value = v
    def noise(scale, detail=3.0, rgh=0.5, dist=0.0, vec=co):
        n = N.new('ShaderNodeTexNoise'); n.noise_dimensions = '4D'
        n.inputs['W'].default_value = seed
        n.inputs['Scale'].default_value = scale * sc; n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = rgh; n.inputs['Distortion'].default_value = dist
        L.new(vec, n.inputs['Vector']); return n.outputs['Factor']
    def mr(v, a, b_, c, d):
        n = N.new('ShaderNodeMapRange'); link(n.inputs[0], v)
        for i, x in zip((1, 2, 3, 4), (a, b_, c, d)): link(n.inputs[i], x)
        return n.outputs['Result']
    def op(o, a, b_=0.0):
        n = N.new('ShaderNodeMath'); n.operation = o; link(n.inputs[0], a); link(n.inputs[1], b_)
        return n.outputs[0]
    def vop(o, a, b_):
        n = N.new('ShaderNodeVectorMath'); n.operation = o; link(n.inputs[0], a); link(n.inputs[1], b_)
        return n.outputs[0]
    def mixf(f, a, b_):
        n = N.new('ShaderNodeMix'); n.data_type = 'FLOAT'
        link(n.inputs[0], f); link(n.inputs[2], a); link(n.inputs[3], b_); return n.outputs[0]
    def mixc(f, a, b_):
        n = N.new('ShaderNodeMix'); n.data_type = 'RGBA'
        link(n.inputs[0], f); link(n.inputs[6], a); link(n.inputs[7], b_); return n.outputs[2]

    glossy = rough < 0.4 or kind in ('metal', 'glass')
    # macro roughness variation
    r = mr(noise(2.5, 4), 0.3, 0.7, max(0.0, rough - P['rv']), rough + P['rv'])
    # smudges / fingerprints (raise roughness on glossy, lower it on matte = greasy)
    sm = op('MULTIPLY', mr(noise(6.0, 6, 0.6, 0.6), 0.55, 0.75, 0.0, 1.0), P['smudge'])
    r = op('ADD', r, op('MULTIPLY', sm, 0.16 if glossy else -0.14))
    # scratches: thin Voronoi edges in stretched coordinates, three orientations, sparse mask
    lines = None
    # each layer: rotate the coordinates by an odd angle (no grid), stretch one axis, take thin Voronoi edges
    for k, (rot, st) in enumerate((((0.3, 0.7, 0.2), (1.0, 45, 45)), ((1.1, 0.2, 0.9), (45, 45, 1.0)),
                                   ((0.6, 1.3, 2.1), (45, 1.0, 45)))):
        mp = N.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = rot
        mp.inputs['Scale'].default_value = st; L.new(co, mp.inputs['Vector'])
        v = N.new('ShaderNodeTexVoronoi'); v.feature = 'DISTANCE_TO_EDGE'
        v.inputs['Scale'].default_value = sc * (1.0 + 0.37 * k)
        L.new(mp.outputs['Vector'], v.inputs['Vector'])
        ln = mr(v.outputs['Distance'], 0.0, 0.02, 1.0, 0.0)
        # per-layer sparse mask so each orientation only shows in patches
        ln = op('MULTIPLY', ln, mr(noise(1.6 + 0.9 * k, 2, 0.5, 0.3), 0.58, 0.68, 0.0, 1.0))
        lines = ln if lines is None else op('MAXIMUM', lines, ln)
    scr = op('MULTIPLY', lines, P['scratch'])
    r = op('ADD', r, op('MULTIPLY', scr, -0.12 if kind == 'metal' else 0.2))
    # colour: scratches show lighter primer / bright metal
    c = (*col, 1.0)
    lighter = tuple(min(1.0, x * 1.25 + 0.06) for x in col) + (1.0,)
    cc = mixc(op('MULTIPLY', scr, 0.8), c, lighter)
    met = metal
    if P['grime'] > 0:   # dirt in corners and crevices
        ao = N.new('ShaderNodeAmbientOcclusion'); ao.only_local = True; ao.samples = 8
        ao.inputs['Distance'].default_value = 0.06
        gm = op('MULTIPLY', op('MULTIPLY', op('SUBTRACT', 1.0, ao.outputs['AO']),
                               mr(noise(8.0, 4), 0.3, 0.7, 0.4, 1.0)), P['grime'])
        cc = mixc(gm, cc, tuple(x * 0.3 for x in col) + (1.0,))
        r = op('ADD', r, op('MULTIPLY', gm, 0.15))
    if P['dust'] > 0:    # dust settles on upward faces, a little everywhere
        nz = N.new('ShaderNodeSeparateXYZ'); L.new(N.new('ShaderNodeNewGeometry').outputs['Normal'], nz.inputs[0])
        up = mr(nz.outputs['Z'], 0.4, 0.95, 0.12, 1.0)
        dm = op('MULTIPLY', op('MULTIPLY', up, mr(noise(18.0, 4, 0.6), 0.3, 0.75, 0.25, 1.0)), P['dust'])
        cc = mixc(dm, cc, (0.36, 0.345, 0.32, 1.0))
        r = mixf(dm, r, 0.92)
        met = op('MULTIPLY', metal, op('SUBTRACT', 1.0, dm))
        if kind == 'glass':
            link(p.inputs['Transmission Weight'], op('SUBTRACT', trans, op('MULTIPLY', dm, 0.7)))
    if kind == 'glass':
        link(p.inputs['Base Color'], c)
        link(p.inputs['Roughness'], op('MAXIMUM', op('MULTIPLY', sm, 0.35), 0.0))
        if P['dust'] <= 0: p.inputs['Transmission Weight'].default_value = trans
        if P['dust'] > 0: link(p.inputs['Base Color'], cc)
    else:
        link(p.inputs['Base Color'], cc)
        link(p.inputs['Roughness'], op('MINIMUM', op('MAXIMUM', r, 0.02), 1.0))
        p.inputs['Transmission Weight'].default_value = trans
    link(p.inputs['Metallic'], met)
    m.diffuse_color = (*col, 1.0)
    if kind == 'glass':
        return  # no bump on glass: it reads as rippled / frosted
    # bump: orange peel + scratch grooves
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 1.0
    bump.inputs['Distance'].default_value = 0.0004
    h = op('SUBTRACT', op('MULTIPLY', noise(260.0, 2), P['peel'] * 10), op('MULTIPLY', scr, 0.6))
    L.new(h, bump.inputs['Height']); L.new(bump.outputs['Normal'], p.inputs['Normal'])
    m.diffuse_color = (*col, 1.0)

P = LEVELS[LEVEL]
for i, (name, (kind, sc)) in enumerate(TARGETS.items()):
    m = bpy.data.materials.get(name)
    if m: build(m, kind, sc, P, seed=1.7 * i + 0.3)
print("MATERIAL DETAIL OK", LEVEL)
