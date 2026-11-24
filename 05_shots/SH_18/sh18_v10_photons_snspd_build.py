"""SH_18 v10: irregular single-photon spacing + SNSPD nanowire click glow.

Run:
  blender --factory-startup -b sh_18_architecture_intro_09.blend --python sh18_v10_photons_snspd_build.py
  -> saves sh_18_architecture_intro_10.blend next to it (v09 stays untouched)

Re-bake only the glow after you tweak spacing/seeds/speed in v10:
  blender --factory-startup -b sh_18_architecture_intro_10.blend --python sh18_v10_photons_snspd_build.py -- rebake

What it does
1. Node group "Curve waveguide fixed" (drives Curve_Waveguide .001/.002/.004):
   the old uniform offset  index * distance  is replaced by a cumulative sum of
   random gaps (Poisson-like, i.e. exponential gaps = how single photons really
   arrive). New modifier inputs:
     distance between OBJ  -> now the MEAN gap (curve factor, sign ignored)
     spacing randomness     0 = even spacing, 1 = fully Poisson
     min gap / max gap      clamp so photons never overlap / no endless holes
     spacing seed           different per guide so the guides take turns
   The per-photon offset is also stored as attribute "photon_offset".
2. Material "snspd-nano-wire": emission driven by the OBJECT attribute
   "snspd_glow" (a custom property on each snspd object).
3. Bake: for every photon that reaches the end of a guide, keys a short
   click on the detector that guide ends on (fast rise, exponential decay,
   like an SNSPD hotspot recovering).
"""
import bpy, math, os, sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
REBAKE_ONLY = "rebake" in argv

HERE = os.path.dirname(bpy.data.filepath)
OUT = os.path.join(HERE, "sh_18_architecture_intro_10.blend")
scene = bpy.context.scene
O = bpy.data.objects

GROUP = "Curve waveguide fixed"
GUIDES = ["Curve_Waveguide.001", "Curve_Waveguide.002", "Curve_Waveguide.004"]
DETECTORS = ["snspd", "snspd.001", "snspd.002", "snspd.003"]

# ---- look settings (edit these) -------------------------------------------
PHOTON_COUNT = 60            # was 1173; only needs to cover the shot
MEAN_GAP = 0.11              # curve factor (~9-10 m on an ~85 m guide); was 0.017 uniform
RANDOMNESS = 1.0
MIN_GAP = 0.045
MAX_GAP = 0.32
SEEDS = {"Curve_Waveguide.001": 11, "Curve_Waveguide.002": 23, "Curve_Waveguide.004": 37}

GLOW_PEAK = 1.0              # value of snspd_glow at the click (shader scales it)
GLOW_EMISSION = 1.4          # emission strength at glow = 1 (node "SNSPD_glow_strength")
GLOW_COLOR = (0.613, 0.947, 0.986, 1.0)   # same cyan as the photon material
GLOW_DECAY_FRAMES = 2.2      # e-folding time of the fade (visible ~6 frames)
ARRIVE_FACTOR = 0.99         # curve factor where the photon drops into the detector


def iface_socket(ng, name):
    for it in ng.interface.items_tree:
        if it.item_type == 'SOCKET' and it.in_out == 'INPUT' and it.name == name:
            return it
    return None


def ensure_input(ng, name, stype, default, minv=None, maxv=None):
    it = iface_socket(ng, name)
    if it is None:
        it = ng.interface.new_socket(name=name, in_out='INPUT', socket_type=stype)
    it.default_value = default
    if minv is not None:
        it.min_value = minv
    if maxv is not None:
        it.max_value = maxv
    return it


def sock(node, name, outputs=False):
    socks = node.outputs if outputs else node.inputs
    for s in socks:
        if s.name == name and s.enabled:
            return s
    raise KeyError(f"{node.name}: no enabled socket {name}")


# ---------------------------------------------------------------- 1. geometry nodes
def build_spacing(ng):
    N, L = ng.nodes, ng.links
    if "PH_accumulate" in N:
        print("spacing nodes already present")
        return
    math_add = N["Math"]          # progression = movement + offset
    old = N["Math.001"]           # index * distance (old uniform spacing)

    ensure_input(ng, "spacing randomness", 'NodeSocketFloat', 1.0, 0.0, 1.0)
    ensure_input(ng, "min gap", 'NodeSocketFloat', 0.035, 0.0, 1.0)
    ensure_input(ng, "max gap", 'NodeSocketFloat', 0.30, 0.0, 10.0)
    ensure_input(ng, "spacing seed", 'NodeSocketInt', 0)

    x0, y0 = old.location.x, old.location.y - 400
    gi = N.new('NodeGroupInput'); gi.location = (x0 - 900, y0)

    def node(t, name, dx, dy=0, **kw):
        n = N.new(t); n.name = n.label = name; n.location = (x0 + dx, y0 + dy)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    idx = node('GeometryNodeInputIndex', "PH_index", -700, -150)
    rnd = node('FunctionNodeRandomValue', "PH_random", -500, 0, data_type='FLOAT')
    sock(rnd, "Min").default_value = 0.0005
    sock(rnd, "Max").default_value = 1.0
    L.new(idx.outputs[0], sock(rnd, "ID"))
    L.new(gi.outputs["spacing seed"], sock(rnd, "Seed"))

    absd = node('ShaderNodeMath', "PH_mean_abs", -500, 200, operation='ABSOLUTE')
    L.new(gi.outputs["distance between OBJ"], absd.inputs[0])

    ln = node('ShaderNodeMath', "PH_ln", -300, 0, operation='LOGARITHM')
    ln.inputs[1].default_value = math.e
    L.new(sock(rnd, "Value", True), ln.inputs[0])
    # shifted exponential: gap = min + (-ln u) * (mean - min)  -> mean stays = mean,
    # never closer than min, and no pile-up of identical gaps at the clamp
    span = node('ShaderNodeMath', "PH_mean_minus_min", -400, 300, operation='SUBTRACT')
    L.new(absd.outputs[0], span.inputs[0])
    L.new(gi.outputs["min gap"], span.inputs[1])
    neg = node('ShaderNodeMath', "PH_neg_span", -300, 200, operation='MULTIPLY')
    neg.inputs[1].default_value = -1.0
    L.new(span.outputs[0], neg.inputs[0])
    expg = node('ShaderNodeMath', "PH_exp_gap", -100, 0, operation='MULTIPLY_ADD')
    L.new(ln.outputs[0], expg.inputs[0])
    L.new(neg.outputs[0], expg.inputs[1])
    L.new(gi.outputs["min gap"], expg.inputs[2])

    mix = node('ShaderNodeMix', "PH_mix", 100, 100, data_type='FLOAT')
    L.new(gi.outputs["spacing randomness"], sock(mix, "Factor"))
    L.new(absd.outputs[0], sock(mix, "A"))
    L.new(expg.outputs[0], sock(mix, "B"))

    clamp = node('ShaderNodeClamp', "PH_clamp", 300, 100)
    L.new(sock(mix, "Result", True), clamp.inputs["Value"])
    L.new(gi.outputs["min gap"], clamp.inputs["Min"])
    L.new(gi.outputs["max gap"], clamp.inputs["Max"])

    acc = node('GeometryNodeAccumulateField', "PH_accumulate", 500, 100,
               data_type='FLOAT', domain='POINT')
    L.new(clamp.outputs[0], acc.inputs[0])
    trail = sock(acc, "Trailing", True)      # photon 0 = head of the train

    negoff = node('ShaderNodeMath', "PH_offset_neg", 700, 100, operation='MULTIPLY')
    negoff.inputs[1].default_value = -1.0
    L.new(trail, negoff.inputs[0])

    # swap the old uniform offset for the random one
    for lk in list(L):
        if lk.from_node == old and lk.to_node == math_add:
            L.remove(lk)
    L.new(negoff.outputs[0], math_add.inputs[1])

    # store photon_offset next to progression (propagates to the instances)
    store_prog = N["Store Named Attribute"]
    src = store_prog.inputs["Geometry"].links[0].from_socket      # Points
    st = node('GeometryNodeStoreNamedAttribute', "PH_store_offset", 900, 100,
              data_type='FLOAT', domain='POINT')
    st.inputs["Name"].default_value = "photon_offset"
    for lk in list(L):
        if lk.to_socket == store_prog.inputs["Geometry"]:
            L.remove(lk)
    L.new(src, st.inputs["Geometry"])
    L.new(trail, sock(st, "Value"))
    L.new(st.outputs[0], store_prog.inputs["Geometry"])
    print("spacing nodes built")


def set_mod_input(mod, name, value):
    it = iface_socket(mod.node_group, name)
    g = mod.properties.inputs[it.identifier]
    g["value"] = value


# ---------------------------------------------------------------- 2. nanowire shader
def build_glow_shader():
    mat = bpy.data.materials["snspd-nano-wire"]
    N, L = mat.node_tree.nodes, mat.node_tree.links
    if "SNSPD_glow_attr" in N:
        return
    bsdf = next(n for n in N if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    at = N.new('ShaderNodeAttribute'); at.name = at.label = "SNSPD_glow_attr"
    at.attribute_type = 'OBJECT'; at.attribute_name = "snspd_glow"
    at.location = (bsdf.location.x - 500, bsdf.location.y - 500)
    mul = N.new('ShaderNodeMath'); mul.name = mul.label = "SNSPD_glow_strength"
    mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = GLOW_EMISSION
    mul.location = (bsdf.location.x - 250, bsdf.location.y - 500)
    L.new(at.outputs["Fac"], mul.inputs[0])
    L.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
    bsdf.inputs["Emission Color"].default_value = GLOW_COLOR
    print("glow shader built")


# ---------------------------------------------------------------- 3. bake clicks
def fcurves_of(idb):
    ad = idb.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    try:
        return list(act.fcurves)
    except Exception:
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out += list(cb.fcurves)
        return out


def photon_offsets(obj, frames):
    """id -> offset, read from the evaluated instances over several frames."""
    offs = {}
    for f in frames:
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(dg)
        gs = ev.evaluated_geometry()
        pc = gs.instances_pointcloud()
        if pc is None:
            continue
        a_off = pc.attributes.get("photon_offset")
        a_id = pc.attributes.get("id")
        if a_off is None:
            continue
        for i, d in enumerate(a_off.data):
            key = a_id.data[i].value if a_id else round(d.value, 5)
            offs[key] = d.value
    return offs


def nearest_detector(obj):
    sp = obj.data.splines[0]
    end = obj.matrix_world @ sp.points[-1].co.xyz
    return min((O[d] for d in DETECTORS),
               key=lambda d: (d.matrix_world.translation.xy - end.xy).length)


def pulse(dt):
    """SNSPD click envelope: 1-frame rise, exponential recovery."""
    if dt < -1.0:
        return 0.0
    if dt < 0.0:
        return GLOW_PEAK * (1.0 + dt)
    return GLOW_PEAK * math.exp(-dt / GLOW_DECAY_FRAMES)


def glow_fcurve(det):
    det["snspd_glow"] = 0.0
    det.keyframe_insert('["snspd_glow"]', frame=scene.frame_start)
    fc = next(f for f in fcurves_of(det) if f.data_path == '["snspd_glow"]')
    fc.keyframe_points.clear()
    return fc


def bake_glow():
    f0, f1 = scene.frame_start - 150, scene.frame_end

    clicks = {d: [] for d in DETECTORS}
    sample = list(range(f0, f1 + 1, 4))
    for gname in GUIDES:
        g = O[gname]
        mod = g.modifiers["GeometryNodes"]
        ident = iface_socket(mod.node_group, "movement progression").identifier
        fc = next(fc for fc in fcurves_of(g) if ident in fc.data_path)
        offs = sorted(set(photon_offsets(g, sample).values()))
        det = nearest_detector(g)
        # arrival: movement(t) - offset == ARRIVE_FACTOR  (sub-frame search)
        t, step = f0, 0.25
        arrivals = []
        for off in offs:
            target = ARRIVE_FACTOR + off
            if fc.evaluate(f1) < target:
                break
            while t <= f1 and fc.evaluate(t) < target:
                t += step
            if t <= f1:
                arrivals.append(t)
        clicks[det.name] += arrivals
        print(f"{gname} -> {det.name}: {len(offs)} photons seen, arrivals {[round(a,1) for a in arrivals]}")

    for dname, times in clicks.items():
        fc = glow_fcurve(O[dname])
        keys = []
        for f in range(f0, f1 + 1):
            v = max((pulse(f - t) for t in times), default=0.0)
            keys.append((f, v if v > 0.005 else 0.0))
        # drop redundant zeros (keep the ones bordering a pulse)
        kept = [k for i, k in enumerate(keys)
                if k[1] > 0 or i in (0, len(keys) - 1)
                or keys[i - 1][1] > 0 or keys[i + 1][1] > 0]
        fc.keyframe_points.add(len(kept))
        for kp, (f, v) in zip(fc.keyframe_points, kept):
            kp.co = (f, v)
            kp.interpolation = 'LINEAR'
        fc.update()
        print(f"{dname}: {len(times)} clicks at {[round(t, 1) for t in sorted(times)]}")


# ---------------------------------------------------------------- run
ng = bpy.data.node_groups[GROUP]
if not REBAKE_ONLY:
    build_spacing(ng)
    for gname in GUIDES:
        mod = O[gname].modifiers["GeometryNodes"]
        set_mod_input(mod, "OBJ count", PHOTON_COUNT)
        set_mod_input(mod, "distance between OBJ", -MEAN_GAP)
        set_mod_input(mod, "spacing randomness", RANDOMNESS)
        set_mod_input(mod, "min gap", MIN_GAP)
        set_mod_input(mod, "max gap", MAX_GAP)
        set_mod_input(mod, "spacing seed", SEEDS[gname])
        O[gname].update_tag()
    build_glow_shader()

bake_glow()
scene.frame_set(scene.frame_start)
bpy.ops.wm.save_as_mainfile(filepath=OUT if not REBAKE_ONLY else bpy.data.filepath)
print("SAVED", OUT if not REBAKE_ONLY else bpy.data.filepath)
