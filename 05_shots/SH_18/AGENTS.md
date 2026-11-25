# SH_18: notes for agents

Last updated: 2026-11-25. For the film's story, science and this shot's role in it, read the [project guide](../../AGENTS.md) first. Read this before touching any SH_18 .blend or script. **Keep it updated**: when you change the scene, add what you did, why, and how to undo or re-tune it.

## The shot

- **What it shows:** the architecture intro of the client's photonic quantum computer, drawn as a blueprint-style chip layout. From left to right:
  - 01 single-photon generators (`Plane.003`, glass cylinders `Cylinder.001`, cut to 3 cells by the user on Nov 24: one array column removed, one guide re-routed to start in a cell)
  - 02 entangling unit cells (`entangling-cells-wafer`, renamed from `Plane.002` by the user on Nov 24; 12 glass cavities `optic-fiber-cavity` in a 4 × 3 array, renamed from `Cylinder`)
  - 03 single-photon detectors (SNSPDs, the four `snspd*` objects)
  - 04 classical processor (`Plane`)
  - Below them sit the router (`photonic-router-wafer`, renamed from `Plane.004` in v13) and delay lines (drawn in the sketch texture).

  Above all of that floats the **logic card** (`Card 18 Compute-B`, with a video texture showing a left-to-right logic/circuit animation) on its dark backing plate `Card_bg`.
- Photons (cyan comets) run along waveguide curves from the generators, by way of the unit cells (where they enter the cavities; see Meaning below), to the detectors.
- **Colour rule:** cyan/teal = the client's photonic tech (photons, nanowire glow, card edge). Don't introduce competitor-style red lasers here; SH_1 is the competitor shot.
- **This is one of the most important shots in the film.** It's being polished for final post and delivery. The user gives tweaks one at a time, so iterate and verify each with renders.

## Meaning and scientific context

Record here what the user explains about the science, so the animation stays truthful. Statements marked *(inferred)* are agent guesses and haven't been confirmed by the user.

- **The story:** single photons are generated, travel along waveguides, and **take turns visiting the entangling unit cells**. They're then counted by single-photon detectors, and a classical processor reads the results out. The shot should read as **"a well-oiled machine"**: one photon at a time, each cell switching on in turn, left to right.
- **Detectors** are **superconducting nanowire single-photon detectors (SNSPDs)**. The meander on each `snspd*` object is the nanowire. Absorbing a photon breaks superconductivity locally (a "hotspot"), which produces a click, and the wire then recovers. That's why the glow is a fast rise followed by a short decay.
- **Photon timing:** single-photon sources emit at random times, so irregular (Poisson-like) spacing between photons is physically right as well as more readable than a uniform stream.
- **Unit cells:** each one is an optical cavity, shown as a glass cylinder (`optic-fiber-cavity`) with a glowing diagram circle under it. A cell "turns on" while a photon is in it. Photons don't pass through the cell: they **enter the cavity in the shape of the photonic mode** (user, Nov 25). Shot 15 shows exactly that, and shows the dual rail only from above, in its wider view of several cavities (user); here the timed circles' glow implies it, and the dual rail is left out for simplicity. Shot 15 shows the same unit cells up close (`04_assets/props/unit_cell_v7.blend`, linked into SH_15). *(inferred from SH_15 object names: the cell holds a trapped atom (`atom`, `tweezers`) that the photon entangles with, and the cavity has a mirror below. Ask before relying on this.)*
- **Router (user, Nov 24):** it steers photons between the sections. In reality it's built into the printed silicon wafer, just like the waveguides and some of the unit cells. It should convey **complexity: the great number of possible paths** a photon could take. The scene's photons deliberately use only a few paths for a clear left→right motion. The v13 design is a programmable Mach–Zehnder interferometer mesh, which is how real photonic routers switch any input to any output; that part is agent knowledge, so check with the user before over-claiming.
- **Aesthetic the user likes:** "simple but complex", elegant data-vis graphic design (`ref/feeling-of-elegant-complexity.jpg`). Router style refs: `ref/router-material-style-inspiration.jpg` and `ref/router-material-style-inspiration2.jpg` (#2 is the favourite): frosted translucent layers, dark orthogonal structures blurred at different depths, pale cool palette.
- **Qubits and gates (user, Nov 24):** the photons are the qubits of this quantum computer. The atoms in the entangling unit cells are used to create entanglement gates.
- **Delay lines (user, Nov 24):** the system has long spools of optical fibre, off the wafer and several km long. A photon can be sent down a spool so that it gets entangled with the **next clock cycle** of photons, which makes cluster generation more efficient. The client asked to show photons going down these lines every now and then.
- **The logic card** above the chip shows the computation that runs on this architecture. Its logic reads left to right, the same direction as the hardware flow: photons, then the cluster state, then a **vertical line that represents the "reading" by the single-photon detectors**, then 0s and 1s with errors in red (confirmed by the user, Nov 25).
- **Layout choices (user, Nov 25):** the generators are a separate station for visual clarity, as a simplified linear process. There are four cells per row for an easy logical connection to the simple cluster of four atoms and one photon; keep that.

## Files

| File | What it is |
|---|---|
| `sh_18_architecture_intro_14.blend` | **Current / final.** User's v13 edit + waveguide fixes + delay-line photons, glows re-baked. Frames 2744–3278, output `//Render/sh_18_architecture_v14/` |
| `sh_18_architecture_intro_13.blend` | v12 + photonic router wafer material (router renamed). Then hand-edited by the user (Nov 24, 14:37): 3 generator cells, re-routed guide |
| `sh_18_architecture_intro_12.blend` | v11 + unit-cell switch-on glow + glass cavity lighting |
| `sh_18_architecture_intro_11.blend` | v10 + feathered logic-card reveal. Then hand-edited by the user (Nov 24, 13:35): added the 12 `glowing-diagram-circle*` planes, renamed the wafer and cavities, and added duplicates `Card 18 Compute-B.001` and `08b_Card_Architecture-simplified_still_v3_4K.001/.002` |
| `sh_18_architecture_intro_10.blend` | v09 + irregular photon spacing + SNSPD click glow |
| `sh_18_architecture_intro_09.blend` | User's last hand-edited version (Nov 22). Don't modify it |
| `_08` and older, `_07G` | Earlier iterations. `_08` is what the render script still points at |
| `sh_18_architecture_slide_*.blend` | Still slides built from `_09` (or `slide_base`, a copy of `_09`) by `sh18_slide_variants_build.py`. Separate deliverable, not the animation |
| `sh18_v10_photons_snspd_build.py` | Builds v10 from v09. With `-- rebake` it only re-bakes the SNSPD glow in an existing v10+ file |
| `sh18_v11_card_reveal_build.py` | Builds v11 from v10 |
| `sh18_v12_cells_glass_build.py` | Builds v12 from v11. With `-- rebake` it only re-bakes the unit-cell glow in v12+ |
| `sh18_router_layout_gen.py` | Plain Python (Pillow + numpy). Writes the router layout textures to `tex/router_*.png` |
| `sh18_v13_router_build.py` | Builds v13 from v12 (router material + rename) |
| `sh18_v14_delaylines_build.py` | Builds v14 from v13. Afterwards run both `-- rebake` scripts on v14 (see its docstring), then `sh18_v14_delay_density.py` |
| `sh18_v14_delay_density.py` | Edits v14 in place: dense random delay-line photons (only touches `DelayLine_*`) |
| `Sh_18_v14_render_script.bat` | **Final render script.** v14, frames 2744–3278. Output `Render/sh_18_architecture_v14/` (the .blend's path, also forced with `-o`); **the user wants renders and playblasts in this one folder, with renders overwriting playblasts**. `RESUME=1` skips only real renders: an EXR whose header contains Cycles' `RenderTime` stamp (viewport playblasts lack it, so they get overwritten). `FRAME_LIST` (e.g. `2900 2950-2975`) renders only those frames, for re-render passes; pair with `RESUME=0` to overwrite. Full-res frames take ~33–41 s |
| `tex/` | Router layout textures, referenced relatively (`//tex/...`), **not packed**. Keep them next to the .blend |
| `ref/` | User's style references for this shot |
| `sh18_slide_variants_build.py`, `sh18_slide_feather.py` | Slide stills (see their docstrings) |
| `Sh_18_render_script.bat` | Old render loop, set to `_08.blend`. Superseded by `Sh_18_v14_render_script.bat` |
| `Render/` | `Render/sh_18_architecture/` = old v08 frames. **Final v14 frames and playblasts both live in `Render/sh_18_architecture_v14/sh_18_architecture_v14_####.exr`** (keep it that way; don't split folders). Frame 2744 there predates the delay-density change; re-render it in the second pass |

Convention so far: each change round is saved as a **new version number** by a build script run on the previous version, so every step can be reproduced or rolled back. The `.blend1` files are Blender autosave backups.

## Running Blender headless

- Use **Blender 5.2** (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`). The files are saved with 5.2 (zstd-compressed, so you can't grep them).
- `--factory-startup` resets the render device to CPU. Set OptiX in your script (see `sh18_slide_variants_build.py`, or the test render recipe below).
- **Blender 5.2 API gotchas:**
  - GN modifier inputs are no longer `mod["Socket_6"]`. Use `mod.properties.inputs["Socket_6"]["value"]` (read and write). The RNA path for keyframes is `modifiers["GeometryNodes"].properties.inputs.Socket_6.value`.
  - Actions are layered: `action.fcurves` may not exist. Walk `action.layers[].strips[].channelbags[].fcurves`. The build scripts have a `fcurves_of()` helper.
  - `obj.evaluated_get(depsgraph).evaluated_geometry().instances_pointcloud()` gives you GN instances with their attributes. **Don't trust `pc.points[i].co`**: it returns garbage. Take positions from the `instance_transform` attribute (`m.value.translation`, object space → multiply by `matrix_world`).
  - Drivers: simple expressions like `g * w` run without Python auto-exec, which is needed under `--factory-startup`. Don't use function calls in driver expressions.
- **Test renders are fast.** At 50 % resolution and 48 samples on the RTX 3080, a frame takes about 1–2 s, so render strips of frames and look at them rather than guessing.

## Scene facts

- **Frames:** the delivery range is **2744–3278** at 25 fps (user, Nov 24). It covers the chip fly-ins and the logic-card reveal (2806–2858). Scene range was set to match in v14.
- **Render settings (in the .blend):** 1920×1080 at 100 %, Cycles 64 samples adaptive (0.01), time limit 47 s (Nov 25), OIDN, motion blur on (shutter 0.5), EXR 32-bit. The bat runs `blender -b file -f N` **without** `--factory-startup`, so GPU and OptiX come from the user's preferences.
- **Cameras** are switched by timeline markers:
  - `F_2722` → `Dolly_Camera` (low angle, rig `Dolly_Rig`)
  - `F_2979` → `Camera.001` (parented to the animated empty `CAM_middle`)
  - `F_3070` → `Dolly_Camera.001` (rises to a frontal view of the whole layout)

  Markers override `scene.camera`; the slide script clears them.
- **Chip cards fly in:** `Plane.003` animates 2715→2777 and `Plane.002` 2754→2804 (location and rotation from above).
- `processor_flashing_glow` (in the excluded `Hidden` collection) has scale flashes at 2927–2951. It's currently not rendered.
- **Collections:** `cntrl_OBJ`, `Hidden` and `archive` are excluded from the view layer. `Widgets` is render-hidden.

## Photons on the waveguides (changed in v10)

- **Active guides:** `Curve_Waveguide.001`, `.002` and `.004` (collection `Collection`). They use node group **"Curve waveguide fixed"**. The `.003/.005/.006` guides (`Curve_Waveguides_Deko`) use "Curve waveguide fixed.001" with OBJ count 0, so they're glass tubes with no photons. Leave that group alone.
- **How the group works:**
  1. A Points node makes N photons. Photon *i* gets `progression = movement progression − offset_i`.
  2. Photons with progression outside [0, 1] are deleted.
  3. The rest sample the filleted curve and get the `photon` collection (an `Icosphere`) instanced on them.
  4. A repeat zone (7 iterations) adds the comet tail.
  5. The tube mesh is a Curve to Mesh boolean-intersected with `Guides_Boolean`, cached in a simulation zone.
- **Animation:** `movement progression` is keyframed per guide (Bezier, extrapolated past the second key):

  | Guide | Keys (0 → 1) | Ends on detector |
  |---|---|---|
  | `.001` | 2777 → 2892 | `snspd.002` |
  | `.002` | 2847 → 2992 | `snspd.003` |
  | `.004` | 2874 → 3011 | `snspd` |

  `snspd.001` has no guide.
- **Before v10:** `offset_i = i × 0.017` with 1173 photons, i.e. a uniform stream about 1.4 m apart. The user found it boring, ugly and unreadable.
- **Since v10:** `offset_i` = trailing cumulative sum of random gaps (nodes named `PH_*`). Each gap is a shifted exponential, `min gap + (−ln u) × (mean − min gap)`, clamped to `max gap`. That gives Poisson-like single-photon arrivals with no two photons closer than `min gap`. Modifier inputs:
  - `OBJ count` 60
  - `distance between OBJ` = **mean gap** 0.11 (sign ignored)
  - `spacing randomness` 1 (0 is the old even spacing)
  - `min gap` 0.045
  - `max gap` 0.32
  - `spacing seed` 11 / 23 / 37 per guide, so the guides take turns

  The per-photon offset is also stored as the attribute `photon_offset`. The result is about 25 photons per guide, arriving 5–35 frames apart.
- **Check the counts if you change speed or range:** 60 photons cover the shot at the current speeds. If you slow the photons down or extend the frame range, check that the train doesn't run out (`photon_offsets()` in the build script prints how many were seen).

## SNSPD click glow (added in v10)

- **Shader:** material `snspd-nano-wire` (the meander wire on all four `snspd*` objects, which share mesh `Plane.019`) gets emission from an **Object-type Attribute node `snspd_glow`**. That's a custom property on each snspd object, so each detector glows on its own. Emission colour is the photon cyan. Strength = `snspd_glow` × 1.4 (node `SNSPD_glow_strength`).
- **Keys:** `snspd_glow` is keyframed per frame with a 1-frame rise at each photon arrival and an exponential decay (tau 2.2 frames, visible ~6 frames). The user asked for a *momentary, subtle* glow, and longer decays made several detectors glow at once.
- **The keys are baked, not live.** After changing seeds, gaps, count or photon speed, re-run:
  `blender --factory-startup -b sh_18_architecture_intro_14.blend --python sh18_v10_photons_snspd_build.py -- rebake`
  and the cell glow: `... --python sh18_v12_cells_glass_build.py -- rebake`
  (it re-saves the file it opened). Arrival = when the photon reaches curve factor 0.99, which is where it drops into the detector.

## Logic card reveal (changed in v11)

- **Before:** `Card 18 Compute-B` (with child `Card_bg`) popped up out of the floor via location/rotation keys at 2797 → 2835. The user found it lame.
- **Now:**
  - The 2797 keys are deleted, so the card sits at its rest pose from the start.
  - **Keys at 2835 / 3069 / 3138 are kept.** The 3069→3138 move tilts the card (rot X 0.586 → 0.099) to face the camera as it rises. **That animation is important; don't remove it.**
- **Wipe:** a feathered alpha wipe driven by the empty **`Card_Reveal_Effector`**.
  - **How the empty is attached:** it has a Child Of constraint to the card with location and rotation but **no scale**. The card is scaled 34.6 × 8.3 × 34.6, and inheriting that would shear the wipe. So the wipe lives in the card plane and follows the later tilt.
  - **Wipe edge** = the empty's local YZ plane. Its local X is keyed −42 → +44 over **2806 → 2858** with sine ease-in-out. Everything on the −X side is visible.
  - **Direction:** rotate the empty about local Z. It's currently −18°, a left→right sweep with the bottom leading (it "rises out of" the architecture below). −90° would be a pure bottom→up wipe.
  - **Custom props on the empty:** `feather` (9 m soft edge) and `edge_glow` (0.25, a faint cyan line on the edge, only on `Card_bg`). Drivers feed them into the shaders.
- **Shaders:** node group `CardRevealMask` (Object texture coordinates of the empty → smootherstep). It's used in materials `Card 18 Compute-B` (multiplies the video-derived alpha) and `Material` (Card_bg, alpha 0.796 × mask, plus the edge emission). All added nodes are named `REVEAL_*`.
- The card enters camera view around 2814, so the wipe start is partly off-screen on purpose.

## Unit cells switch on as photons pass (added in v12)

- **Circles:** the 12 `glowing-diagram-circle*` planes (collection `glowing-circle-diagram`, z −0.06, under the wafer) are pieces of the architecture texture that the user placed under each cavity.
  - Grid: x −12.95 / −11.34 / −9.74 / −8.14.
  - Row y 1.40 (`.000–.003`) is fed by guide `.004`. Row y 5.06 (`.004–.007`) by `.001`. Row y 8.74 (`.008–.011`) by `.002`. The guides zig-zag down into each cell.
- **Material:** each circle's slot 0 is object-linked to material **`uc-circle-glow`**, a copy of `08b_Card_Architecture-simplified_still_v3_4K`. The original stays on the main sketch plane. Nodes `UC_*`:
  - emission = original × (0.15 + 3.0 × `uc_glow`)
  - colour tints white → photon cyan as `uc_glow` rises
- **`uc_glow`:** a custom property on each circle, baked per frame from **real photon positions**. The script sampled at half-frames: the distance (XY) from the circle centre to the nearest photon instance, Gaussian falloff (sigma 0.6 m), instant attack, release tau 2 frames. Re-bake after any photon change with `sh18_v12_cells_glass_build.py -- rebake`.
- **Cell lights:** `UC_light*` (collection `UC_lights`) are teal point lights, one per cell, at z 0.25 between the circle and the wafer. Radius 0.25, energy = `uc_glow` × `max_watts` (25 W, a custom property on each light) via driver. This mimics shot 15's `PhotonMode_Light`, which lights the glass from inside/below.
- **Timing:** neighbouring cells in a row switch on about 5 frames apart, left to right. Guide `.001` (middle row) is fast and dense, so 2–3 consecutive cells can be lit at once, like a travelling wave. Fewer at once would need a lower photon rate on that guide (bigger `distance between OBJ`), followed by a re-bake of both glows.

## Glass cavity lighting (v12)

- **Problem:** the cavities read as grey plastic. Two reasons:
  1. `Photon_Glass` had Volume Scatter **density 3.43**, which makes it milky. The shot-15 asset `unit_cell_v7.blend` has **0.4**.
  2. SH_18 has nothing bright for the glass to reflect: a flat 0.05 grey world and three tiny overhead area lights. The glass just refracts the grey floor.
- **Shot 15's recipe:** black world; a big emissive sphere `Icosphere.002` (camera-invisible) carrying two packed studio HDRIs (window light + "wedding rings" ring strips, ×4.3 via colour ramp, strength 1.2); a key point light; a cool low rim area light; teal point lights per cell.
- **What v12 does:**
  - Volume density → 0.4. `Photon_Glass` is shared by `optic-fiber-cavity`, `Cylinder.001` and wafer slot 2.
  - Appends shot 15's sphere as **`GlassEnv_Sphere`** (material `GlassEnv_HDRI`, collection `GlassEnv`), centred on the wafer, radius 22 m. Visibility: camera, diffuse, shadow and volume off; glossy and transmission on.
  - **Light linking:** the sphere's receiver collection is **`GlassEnv_receivers`** (cavities, generator cylinders, deko glass guides). The floor, sketch and cards are unaffected. The wafer slabs (`entangling-cells-wafer`, `Plane.003`) were tried as receivers and went milky white, so they're left out.
  - Adds the teal cell lights above.
- **Result:** cavities are see-through with crisp highlights and glow teal when a photon is inside. In the frontal camera (3070+), the generator cylinders show small bright highlight dots from the env sphere.
- **Possible next steps** (not done): darker overall exposure or world to get closer to shot 15's low-key look; a cool rim light linked to the glass only.

## Photonic router (v13)

- **Before:** `Plane.004` was a placeholder: rough glass whose roughness came from a brick texture (material `decorative-texture-1`, now unassigned and kept with a fake user).
- **Now:** the object is **`photonic-router-wafer`** (mesh renamed too). It's a rounded slab 38.5 × 1.9 × 0.25 m, axis-aligned, with object-space footprint x −10.78…27.71 and y ±0.954. It sits under the horizontal run of the photon guides, whose lanes at world y −6.5 / −6.9 / −7.3 are the router lanes +4 / 0 / −4.
- **Layout** (`sh18_router_layout_gen.py` → `tex/`, 200 px/m, 7698 × 382):
  - 13 waveguide lanes, 0.10 m apart.
  - Three switch blocks: SW-A (6 columns), SW-B (5) and SW-C (6). Each is a brick-wall MZI mesh, 102 MZIs in total, each with S-bends, couplers and a heater bar.
  - Two "XBAR" crossing regions between the blocks.
  - Metal: heaters, contacts, traces to the edges, and bond-pad rows plus ground rails along both long edges.
  - Deep layer: dark trenches under each block, plus near-black bands per mesh column.
  - Small labels (SW-A MZI MESH 13x13, C01…, XBAR, lane numbers) and grating-coupler ticks at both ends.
  - `router_active.png` = the 3 lanes the photons use.
- **Material `photonic-router-wafer`:**
  - Three grey layers multiply the base. L3 (deep) and L2 (metal) are sampled with a **parallax offset** (view vector in object space, z clamped ≥ 0.2) at depths 0.16 m and 0.05 m. L1 (waveguides) is on the surface.
  - Principled with coat 0.6 (polished cladding); roughness 0.42, lower on metal.
  - Faint cyan emission on the active lanes.
  - Tweak via the named Value nodes `ROUTER_*`: base 0.74, deep 0.72, metal 0.80, line 0.85, depth_L2 0.05, depth_L3 0.16, active_glow 0.15.
- **Why it's bold:** in the frontal camera (3070+) the router is only about 900 px wide (~23 px/m), so fine lanes average out. The readable rhythm comes from the dark per-column bands and the block/XBAR alternation. In the low Dolly shot it's in the defocused foreground, so only big shapes survive there too. A first pass with thin lines and active_glow 0.6 read as a flat grey bar with three cyan stripes.
- **To change the design:** edit the generator, re-run it, and re-render. The .blend picks up the PNGs (reload images if the file is open).

## Waveguide fixes and delay lines (v14)

- **User edit in v13:** the generator chip has 3 cells now (`Cylinder.001` keeps only its row Array, count 3). One guide was re-routed so it starts in a cell. Photon timing at the detectors didn't change, because arrival = reaching 99 % of the curve, which is independent of length. The cell glows shifted by about 1–4 frames, and both glows were re-baked.
- **Darker guide:** `Curve_Waveguide.001`'s tube used `Glass_Mat` (Principled transmission, volume density 5.6, empty image on base colour, viewport colour 0.52). It's switched to `Photon_Glass` like the others. The target-less `Hook-Curve_Parent_01` modifiers on `.001` and `.004` are deleted. The 3 active guides were added to `GlassEnv_receivers`.
- **`end fade`:** a new input on the node group "Curve waveguide fixed", in curve-factor units (0 = off, the default, used by the main guides). Photons scale from 0 to full over that length at both ends of the curve (node `EF_scale`, Scale Instances after Delete Geometry). The photon shader reads `fade` (= instance scale), so they fade as well as shrink.
- **Delay-line guides:** `DelayLine_Outer / _Middle / _Inner` (collection `DelayLines`). They're copies of `Curve_Waveguide.002`'s modifier setup with their own POLY curves. Each follows one nested U of the sketch's "DELAY LINES" drawing; coordinates were measured from the 4K texture:

  | Loop | Right x | Left x | Bottom y |
  |---|---|---|---|
  | Outer | −6.91 | −14.24 | −13.08 |
  | Middle | −8.02 | −13.13 | −11.97 |
  | Inner | −9.13 | −12.02 | −10.85 |

  - Spool circles: centres x −10.06 / −10.58 / −11.10, radius 0.43, on each U's bottom.
  - Path: start inside the entangling wafer (y 0.9) on the right → down → one full turn around each of the 3 spool circles (right to left) → left → up → end inside the wafer.
  - Photons fade over 1 m at each end. No tube is drawn, because the group's tube only exists inside `Guides_Boolean` (generator chip).
- **Delay density (changed later on Nov 24, in place in v14, no new version):** the user wanted many more photons, always 2–3 or more somewhere on the loops. Nobody will notice that they appear from and vanish into the wafer, as long as the paths start and end in the entangling area. `sh18_v14_delay_density.py` rewrites only the `DelayLine_*` modifiers and keys; the main guides and glow bakes are untouched:
  - random spacing (randomness 1)
  - mean interval 48 frames, min 14, max 110 (converted to curve factor via traversal time)
  - seeds 101 / 202 / 303
  - 24 photons per loop
  - linear movement from frame 2560, so the loops are already busy at 2744

  Result over 2744–3278: **2–7 photons on the loops at every frame, mean 4.3** (the script prints the histogram). **The table below is superseded.**
- **Delay timing (original v14 build, superseded):** explicit and deterministic. Linear `movement progression` keys (0→1 over length / 0.6 m/frame, linear extrapolation). `spacing randomness` 0 with gap = interval / traversal.

  | Loop | Photons enter at | Traversal | Photons |
  |---|---|---|---|
  | Outer | 2850, 3020, 3190 | 72 f | 3 |
  | Middle | 2905, 3075, 3245 | 65 f | 3 |
  | Inner | 2960, 3130 | 57 f | 2 |

  Edit `DELAY` in the build script to change these.
- **Delay photons are not part of the glow bakes.** They don't reach cells or detectors, and the bake scripts list only the 3 main guides. They're the same size as main photons, so they're tiny in the wide view and read best in the frontal camera.
- **Known leftover:** the architecture texture under the generator chip still shows 8 drawn circles, even though the model now has 3 cells.

## Test render recipe

```python
# blender -b --factory-startup <blend> --python test_render.py -- <tag> 2818,2826 <outdir>
p = bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type = 'OPTIX'; p.get_devices()
for d in p.devices: d.use = d.type == 'OPTIX'
sc.cycles.device = 'GPU'; sc.render.resolution_percentage = 50; sc.cycles.samples = 48
sc.render.image_settings.file_format = 'PNG'
# frame_set + render(write_still=True) per frame
```

Write test output to the scratchpad or `08_renders/stills/sh18_v1x_tests/`, never to `Render/sh_18_architecture/` (the real frame output).

## Change log

- **2026-11-24 (v10):** irregular Poisson photon spacing, 60 photons per guide; SNSPD nanowire click glow baked from photon arrivals.
- **2026-11-24 (v11):** logic card pop-up replaced with an empty-driven feathered wipe (2806–2858); the 3069–3138 tilt is kept.
- **2026-11-24 (v11, user):** added the glowing-diagram circles under the cells; renamed `Plane.002` → `entangling-cells-wafer` and `Cylinder` → `optic-fiber-cavity`.
- **2026-11-24 (v12):** cell circles and teal cell lights driven by photon proximity; glass volume density 3.43 → 0.4; shot-15 HDRI reflection sphere, light-linked to the glass only.
- **2026-11-24 (v13):** router `Plane.004` → `photonic-router-wafer`, with a layered MZI-mesh wafer material that replaces the brick placeholder.
- **2026-11-24 (v13, user):** generator cut to 3 cells; one guide re-routed.
- **2026-11-24 (v14):** `.001` tube → `Photon_Glass`; dead hooks removed; `end fade` added to the guide group; 3 delay-line loop guides; both glows re-baked; range 2744–3278 with a new output folder; `Sh_18_v14_render_script.bat`.
- **2026-11-24 (v14, in place):** denser delay-line traffic (random spacing, mean 48 f per loop, 2–7 photons on screen) via `sh18_v14_delay_density.py`.
- **2026-11-24 (render):** a viewport playblast (2875–3278) overwrote the same output path, so resume thought the job was done. Splitting them into separate folders was rejected by the user, so everything is back in `Render/sh_18_architecture_v14/`. Resume now skips only EXRs with a `RenderTime` header stamp, so renders overwrite playblasts. The bat also gained a `FRAME_LIST` for re-render passes.
- **2026-11-24 (render, full pass):** bat set to the whole range 2744–3278 with `FRAME_LIST` empty and `RESUME=0`, for the user's high-quality overnight render (overwrites every existing EXR). If it stops partway, move `START_FRAME` to the next unfinished frame; `RESUME=1` would skip older-quality frames. It replaces the 2744–2875 pass, which the user stopped after 2809. The user raised the Cycles time limit to 90 s/frame in the .blend (was 20).
- **2026-11-25 (render, resumed):** the overnight pass stopped at about 00:30 when Windows Update restarted the PC (not a power cut). Frames 2744–2787 are done at 256 samples (90 s limit). Frames 2788–2813 followed on Nov 25, also at 256. The user then saved the .blend with 64 samples and a 47 s limit (10:16): **a deliberate choice, confirmed by the user; don't raise it back**. 2814–2878 were rendered that way on Nov 25; the script was stopped at about 11:03 (no crash logged). The bat is now `START_FRAME=2879`, batch 6, cooldown 60 s, `FRAME_LIST` empty, `RESUME=0`: **keep `RESUME=0`**, because the files at 2879+ are older renders or playblasts and older renders would count as done. If it stops again, move `START_FRAME` to the next unfinished frame (see the render log). Restore `START_FRAME=2744` and `RESUME=1` afterwards. **Keep the .bat CRLF and plain ASCII**: it was LF with em dashes, which made cmd lose the `get_cs` label in a test copy and fail outright under code page 65001. Converted Nov 25. Don't edit a .bat while it runs.
