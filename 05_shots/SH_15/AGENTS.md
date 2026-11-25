# SH_15: notes for agents

Last updated: 2026-11-25 (v22). For the film's story and science, read the [project guide](../../AGENTS.md) first. Read this before touching any SH_15 .blend or script. **Keep it updated**: when you change the scene, add what you did, why, and how to undo or re-tune it.

Statements marked *(inferred)* are agent readings of the file. The user hasn't confirmed them.

## The shot

- **What it shows** *(inferred from the scene and file name, except where marked)*: the unit cell up close. An atom is carried into an optical cavity and held there, then a photon enters the cavity **in the shape of the photonic mode** (user), and the camera later pulls back over a row of cells building the first cluster tile.
- **Dual rail (user, Nov 25):** it is only seen **from above**, when we look at the bigger picture showing several cavities. The close-up part doesn't show it. **The photon in the |0⟩ rail is not shown**: that was the focus of the second Quantum Source movie. Don't add it here.
- Being polished for the final version (user, Nov 25). Tweaks come one at a time.
- **The atom** is `Icosphere.001` (rubidium-87). It travels along Y during frames 124–152 and then stays at (2.6, −0.073, 0.976). Up to v21 it was a 0.02 sparkling shell (`atom` material) with a 0.0035 nucleus; v22 replaces its look (see "The atom").
- **The cell is a vertical Fabry–Pérot cavity (user).** The top part (`rails_pi_shape.001`, glass) is the **edge of an optical fibre**. In reality the bottom is another fibre edge too, but the film uses a **very reflective round mirror** (`mirror`) so viewers read it clearly. Don't "correct" it.
- **The laser tweezers hold the atom floating in space (user).** After they are introduced they are **omitted to simplify the visuals, and the fade must imply they are still there (user)**. They have to be completely gone by **frame 185** (user).

### Science notes on the photonic mode

- **What it stands for (user):** the cavity traps a single photon that resonates back and forth between the two mirrors, which raises the chance of interacting with the atom in the middle. The lobes show the probability distribution. The highest intensity is in the centre; keep it that way.
- **Resonance (user, v21):** the lobes keep their position and their intensity changes up and down along Z, to imply that the photon isn't exactly a standing wave. It must be a **very subtle detail, never dominant or annoying**. It belongs only to the detailed single-cell part; **not** to the cluster part with several cells.
- **Visual metaphor (agent knowledge):** a 25 µm cavity's round trip takes about 0.17 picoseconds, far shorter than the photon's own duration, so a real photon fills the cavity evenly instead of appearing as a spot that travels. The moving brightness shows "it bounces many times"; don't describe it to the client as literal dynamics.

### Science notes on the tweezers

- **The tweezers are horizontal on purpose (user):** the team chose the simpler horizontal beam so viewers don't confuse it with the **vertical photonic mode**. In the paper (section II.A, Fig. 1) the trap is a far-detuned 1D optical lattice formed by a TEM00 mode of the cavity itself, so this is a deliberate simplification. Don't re-orient it.
- **Approved (user, Nov 25):** the dashed-outline fade ("exactly what was missing") and the lobes, which make it look like the sophisticated (if not novel) laser technology it is.
- The fringes near the atom come from that paper: a standing wave, with the atom sitting in the central bright fringe. (For red-detuned light, atoms are trapped at intensity maxima: agent knowledge.)
- The beam is brightest at its focus and opens into an hourglass, as a real focused Gaussian beam does. v18's cone was dimmest at the focus.
- **Colour:** rose-copper, kept from the user's old beam. Pure red lasers belong to the competitor machines and cyan/teal to the photon, so stay away from both.

## Files

| File | What it is |
|---|---|
| `sh_15_positioning_and_first_cluster_tile_22.blend` | **Current** (look awaiting the user's approval). v21 + new hero atom |
| `sh_15_positioning_and_first_cluster_tile_21.blend` | v20 + resonance in the photonic mode, cards 13 and 14 split and re-timed |
| `sh_15_positioning_and_first_cluster_tile_20.blend` | v19 + studio lighting for the single-cell part (look approved by the user) |
| `sh_15_positioning_and_first_cluster_tile_19.blend` | v18 + new laser tweezers and fade |
| `sh_15_positioning_and_first_cluster_tile_18.blend` | User's last version. Don't modify it |
| `_11` … `_17` | Earlier iterations |
| `sh15_v19_tweezers_build.py` | Builds v19 from v18 (never writes v18). **Don't re-run it once v19 has been edited by hand**: it would overwrite those edits. Pass another output path after `--` to build elsewhere |
| `sh15_v20_studio_light_build.py` | Builds v20 from v19 (never writes v19). Same rule: don't re-run it over a hand-edited v20 |
| `sh15_v21_resonance_build.py` | Builds v21 from v20 (never writes v20). Same rule: don't re-run it over a hand-edited v21 |
| `sh15_v22_atom_build.py` | Builds v22 from v21 (never writes v21). Don't re-run it over a hand-edited v22 |
| [NOTES_FOR_HUMANS.md](NOTES_FOR_HUMANS.md) | The user's own guide to the controls (asked for on Nov 25). Plain language; keep its values in step with the .blend |
| `Sh_15_v22_render_script.bat` | **Current render script** (Nov 25, based on SH_18's v14 bat). v22, frames 50–850, batch 4, cooldown 60 s, `RESUME=1` (skips finished EXRs; unlike SH_18's, it zero-pads the frame number, needed because the range starts at 0050). `FRAME_LIST` for re-render passes. Forces OptiX with `--cycles-device OPTIX`, because the Blender preferences were on CUDA on Nov 25; frames 160, 474 and 700 match within noise and OptiX takes 12–15 % less time. Stops if a frame's EXR is missing. Keep it CRLF and plain ASCII, and don't edit it while it runs |
| `Sh_15_render_script.bat` | Old render loop. **Still points at `_18`, frames 213–850** (user's setting, untouched) |
| `Render/sh_15_v22/` | **EXR output of v22** (`sh_15_v22_####.exr`), full re-render started on Nov 25 at 20:44. Progress: `sh_15_positioning_and_first_cluster_tile_22_render_log.txt` |
| `Render/sh_15_cavities/` | EXR output of v18–v21, kept. At the time of writing, these frames predate v19–v21. **The user plans to re-render everything in higher quality** (Nov 25) |
| `Render/sh_15_v21_resonance_preview_*.mp4` | Low-res Cycles previews of the resonance, 270–428 and 432–590 (every 2nd frame, at real speed). The first predates the depth change at 431, which doesn't affect it |
| `Render/sh_15_v21_resonance_45f_preview_270-430.mp4` | **Current speed** (45 frames), every frame, low-res Cycles. The two above show the old 56-frame speed |
| `Render/sh_15_v22_atom_preview_143-280.mp4`, `Render/sh_15_v22_atom_still_0220.png` | v22's atom: every frame at half size, and one full-size still at the shot's 45 s limit (took 20 s). `atom-card.jpg` is the user's render of the old atom |
| `Render/sh_15_v20_lighting_preview_*.mp4` | Low-res Cycles previews of the v20 light: 52–230 (every 2nd frame, at real speed) and the hand-over 566–606. Rendered just before the cards were hidden from reflections |
| `Render/sh_15_v19_tweezers_preview_138-192.mp4` | Half-res Cycles preview of the new tweezers (64 samples, 25 fps) |

## Scene facts

- **Blender 5.2.** Scene range 50–850, 25 fps, 1920×1080, Cycles **128 samples** adaptive 0.01, **90 s limit** (user, Nov 25; up to v21: 256 and 45 s), OIDN, EXR 16-bit half DWAB (read from the file; an earlier note said 32-bit), motion blur off, view transform Standard, no compositor. The colour grade happens outside Blender *(inferred: the user's screenshot is warmer/teal-graded compared to a raw render)*.
- **Cameras** are switched by timeline markers: `F_00` → `Camera.001` (rig `Armature`), `F_218` (at frame **228**, not 218) → `Camera`, `F_431` → `Camera.001`.
- `unit-cell-Linked*` are instances of a collection **linked** from `04_assets/props/unit_cell_v7.blend` (glass fibre cavity `rails_pi_shape.001`, curved `mirror`). Edit them there.
- **Cards 13 and 14:** `Card_13-14_v2` is now two objects (user, Nov 25): `Card_13_v2` (atom only, until 227) and its duplicate `Card_14_v2` (228–430; the photon arrives and is eventually entangled). Both play `Card_13-14_v2.mp4`; the graphics start around clip frame 160. `Card_14_v2` plays **40 frames later** (material `Card_14_v2`, image node: Start Frame 40; Card 13 has 0) so it fits the photon reaching the mode.
- **Trap:** `Card_14_v2` needs **its own image datablock** (`Card_14_v2.mp4`, same file). When both cards shared one, EEVEE and Material Preview showed the same clip frame on both, so changing Start Frame or Offset looked like it did nothing. Cycles was right either way. Use Start Frame, not Offset: the clip is 425 frames and cyclic, so with Offset it goes blank at scene frame 425, before the cut at 431. Only `hide_render` is keyed, so both cards show in the viewport.
- **Side effect:** the delayed clip starts in the middle of the ATOM label being typed, so the label types on again after the cut, about 228–240.
- The objects `tweezers`, `atoms-geo-nodes` and the node group `Tweezers`, far from the set at y ≈ −60…−78, are a **different, older setup** with the `tweezers-volume` material. Nothing in v19 uses them.

## Laser tweezers (v19)

One object, `LaserTweezers`, parented to the atom with the old cone's transform. Its local **Z is the beam axis** (world X) and its origin is the focus, so it follows the atom. The mesh itself is empty: the modifier `LaserTweezersGeo` generates everything.

| Part | Where | What it does |
|---|---|---|
| Volume domain | GN, material `LT_beam_volume` | Closed hourglass, 1.75 × the beam radius, so the Gaussian has died out before the edge. Emission-only volume: Gaussian profile + hot core + dimming as it opens + standing-wave fringes + slow 4D-noise shimmer (Scene Time) |
| Dashed outline | GN, material `LT_envelope` | Two thin tubes at 1.15 × the beam radius, turned to face the **active camera** (Active Camera node), so they're always the beam's contour. Dash length is in the material |

**Controls** are custom properties on the object (Object Properties → Custom Properties), read by both the geometry (simple drivers) and the shaders (Attribute nodes of type *Object*):

| Property | Value | Meaning |
|---|---|---|
| `beam` | keyed | Visibility of the glow |
| `ghost` | keyed | Visibility of the dashed outline |
| `waist` / `rayleigh` | 0.034 / 0.48 | Focus radius / how fast the beam opens (smaller = stronger hourglass) |
| `half_length` | 4 | Length on each side of the atom |
| `strength` | 21 | Overall brightness |
| `lattice`, `lattice_period`, `lattice_extent` | 0.75, 0.085, 0.34 | Fringe depth (0 = plain beam), spacing, how far they reach |

Colours are the two swatches of the Mix node in `LT_beam_volume`.

### The fade

Idea: the light drains out and leaves a **dashed outline, the drafting convention for "there but not shown"**, which then dissolves. It also echoes the card's dotted line. (Approved by the user, Nov 25.)

| Frames | What happens |
|---|---|
| to 154 | Full beam (atom settles at 152) |
| 154–173 | `beam` 1 → 0 |
| 158–168 | `ghost` 0 → 0.6, held to 173 |
| 173–185 | `ghost` 0.6 → 0. **Nothing visible at 185** |
| 186 on | `hide_render` / `hide_viewport` keyed on, so later frames don't pay for the volume |

To retime, move the keys of `beam` and `ghost` together and keep the hide keys after the last one. For a plain fade without the outline, set the `ghost` keys to 0.

### Traps

- **The beam sweeps past the lens at frames 140–143** while the atom flies in. Without protection the camera sits in the glow and the frame fogs red. Two Map Range nodes in `LT_beam_volume` prevent it: *fade far ends* (|z| 1.7 → 3.3) and *fade near camera* (2.2 → 4.6 from the lens). If the camera or the atom's move changes, check 138–146 again.
- The outline can't be a shell with a facing-ratio line: front and back dashes cross-hatch. That was tried.
- The old cone is kept as `Cone_OLD_tweezers` in the `archive` collection, hidden. Its material `Material` still has the old fade (205–211). To go back: unhide it and hide `LaserTweezers`.

## Studio lighting for the single cell (v20)

**Why (user):** in the early part the mirror's reflections were confusing and poor. References: a monochrome still with soft vertical bands on the mirror and crisp lines on the fibre, and `08_renders/stills/cavity_cover_B_clean.png` (from `05_shots/assets/cavity_stills.blend`). The later part, with several cells, has its own lighting and must stay as it is.

**What was wrong in v18/v19:**

| Symptom | Cause |
|---|---|
| Solid white blob in the fibre, white crescent under it, white mirror rim | Spot `Point.001` (radius 0.51) right beside the cell: its disc was seen directly |
| Grey half-disc on the mirror | The reflected **outline of the floor panel** `Cube.001` against the environment dome |
| "0.73" mirrored in the metal (f433) | The cards were visible to glossy rays |

**One control: the empty `StudioLight_CTRL`** (above the cell).

| Property | Keys | Meaning |
|---|---|---|
| `early` | 1 until 572 → 0 at 598 | 1 = studio look, 0 = the user's original lighting |
| `glass_boost` | 7.5 until 430, 1 from 431 (constant) | Brightness of the bands just above the horizon, i.e. of the lines on the fibre. From the 431 cut the camera is below the mirror's top, so a boost would blow out the mirror |

It drives:

- **Dome `Icosphere.002`, material `Material.004`:** mixes the original environment with procedural vertical bands (node frame "v20 studio bands"). The bands are placed by azimuth **as seen from the cell** (2.6, 0, 0.6), because the dome isn't centred on it. Band table: `BANDS` in the build script; each band's *Map Range* node holds its width, softness and strength, and its *colour* node the tint. On the cylinder, a band at offset d° from the camera's azimuth (about −58°) appears at screen position sin(d/2).
- **`Point.001`:** energy 200 × (1 − early)⁴, so it's off in the single-cell part and only returns late in the pull-out.
- **`Point.001_floor_only`:** a copy of the spot, light-linked to the floor panel only (collection `Studio floor light linking`), 150 W × early. It keeps the pools of light on the floor.
- **Floor `Cube.001`, material `Material.006`:** transparent to glossy rays while early, so the cylinder shows the bands down its full height.

Not driven: `Card_13_v2`, `Card_14_v2` (both formerly `Card_13-14_v2`) and `Card_15` have Ray Visibility → Glossy off.

**How the fibre/mirror split works:** from these cameras the fibre reflects slightly *up* and the mirror slightly *down*. Glass reflects only about 4 %, so only the part of the bands above the horizon is boosted, and only for reflections. If a camera moves below the mirror's top, lower `glass_boost` there.

**Traps:** bands behind the cell (more than about 140° from the camera) show through the rough glass ceiling as big grey patches; keep rim bands at 130° or less. The linked `mirror` and `Photon_Glass` materials weren't touched, because other shots use them. The small notch on the mirror's right edge around 205 is the neighbouring cell's real reflection. During 586–597 the first cell briefly goes back to the original lighting as it leaves the frame.

**Checked:** with the lighting change alone, frames 598, 600, 640, 700 and 845 are pixel-identical to v19. With the cards hidden from reflections, the mean difference there is at most 0.011 of 255. Render time is about the same as v19 (18–38 s for frames 160, 205, 300 and 520, full res at the shot's settings).

## The atom (v22)

**Goal (user):** slightly hint at a nucleus with an atom cloud in the shape of an S orbital (a sphere), and at the same time register as the logic card's atom: **a dot and a circle**. It should still look artistically interesting.

**How both are reconciled:** the nucleus is the dot. The cloud is a ball of points, thickest at the nucleus and thinning outwards as in a 1s orbital. The circle is the edge of that ball, with a soft glow on its inside so it reads as a sphere's rim. The points slowly come and go. White like the card's atom, not cyan.

**How it's built:** `Icosphere.001` keeps its name, animation and children, but its mesh is now a bounding sphere (`Atom_bounds`, radius 0.085; the old mesh is kept as `Atom_OLD_v21_mesh`). The material `Atom_orbital` is one surface shader (emission and transparency) computed from the distance at which the line of sight passes the centre, so the dot and circle face every camera. The points are 4D Voronoi in five slices along the line of sight. Shadow visibility is off.

| Property on `Icosphere.001` | Value | Meaning |
|---|---|---|
| `atom_radius` | 0.0325 | Radius of the circle. Chosen to sit **inside the tweezers' dashed outline** (0.034 waist); 0.045 crossed the dashes. Keep below 0.07 |
| `atom_nucleus` | 0.27 | Dot, as a fraction of the circle (about 0.29 on the card) |
| `atom_ring`, `atom_ring_width` | 0.8, 0.036 | Opacity and half thickness of the circle |
| `atom_rim` | 0.25 | Glow inside the circle |
| `atom_cloud`, `atom_cloud_size` | 2.6, 0.28 | Brightness and spread of the cloud |
| `atom_grain`, `atom_grain_scale` | 0.94, 8 | Points instead of fog; number of points |
| `atom_twinkle` | 0.6 | How fast the points change |

- It's about 46 px wide at 1080p in the first close-up (the old ball was 28) and about 37 px after the cut at 228, where the camera's depth of field softens it.
- Only the hero changes. The cluster's four atoms (`Icosphere.003`–`.006`) and `atoms-geo-nodes` keep the old `atom` material; they're only a few pixels wide.
- **Checked (40 % size):** 60, 120, 598, 640 and 780 match v21 (max 3 of 255). Inside the photonic mode (276–578) the atom is hidden by the white core, as before; the small differences there are sampling noise, smaller than changing the render seed. Safe re-render range: **124–597**.

## Photonic mode and its resonance (v21)

**How a mode is built:** `PhotonMode*` is a cylinder turned into a volume by geometry nodes (`Geometry Nodes.003`: Mesh to Volume, lobes cut by a Wave texture). The material scatters light from the point light at the focus (`PhotonMode_Light*`), so the inner lobes are 4–300 times brighter than display white. Only the outer parts of the lobes can show a change.

**What v21 adds:** only the hero, `PhotonMode.004`, has its own copies: node group `PhotonMode_hero` and material `Photon_Volume_hero_resonance`. The other four still share the originals. In the hero's material (frame "v21 resonance"), the scatter density is multiplied by a gain. A soft bright region travels at constant speed from mirror to fibre and back, overlapping with its own reflection at each end; the rest dims. Lobe positions and the light aren't touched.

| Property on `PhotonMode.004` | Value | Meaning |
|---|---|---|
| `resonance` | 0 at 276 → 1 at 300, 1 at 560 → 0 at 578 | Overall amount. 0 = the old static mode |
| `res_depth` | 0.68; 0.34 from 431 (constant key) | Dimming/brightening. 0.35 is invisible in the wide part, 0.8 plainly readable, 0.95 dims the centre (wrong) |
| `res_round_trip` | 45 frames (1.8 s) | One trip up and down. Was 56; the user asked for about 25 % faster (Nov 25) so viewers see more trips in the first close-up (3.4 instead of 2.8) |
| `res_width` | 0.30 | Length of the bright region, in cavity lengths |

**Why less depth from 431:** the camera then sees the mode as one solid shape. At 0.68 it became a funnel while the card shows that the probability is highest in the centre.

**Traps:**
- When testing property values in a script, **turn off `use_persistent_data`**: un-keyed custom properties read by shader Attribute nodes stay at their old values. Keyed and driven values update correctly.
- The travel is driven by `(frame - 276) / res_round_trip`, so keying `res_round_trip` would make the motion jump.

**Checked:** frames 160, 272, 276, 579, 584, 610, 640, 694, 710 and 845 match v20 to within 1/255. Full-res frames 334 and 474 take 29 and 38 s (v20: 26 and 37 s).

## Rendering notes

- **v21 changes frames 277–577** (on top of v20).

- **v20 changes frames 50–597**, so the whole single-cell part needs re-rendering, plus a few pixels of mirrored card text after that.

- Frames that changed from v18 to v19: 138–211. 138–185 show the new beam; 186–211 no longer show the old one (it used to disappear at 211). Frames 52, 60, 186, 240 and 300 were compared with v18: they match apart from the old beam being gone in 186. Safe re-render range for v19 alone: 124–211 (v20 supersedes this).
- A full-res frame with the beam takes about 21 s on the RTX 3080 at the shot's own settings, with another render sharing the GPU.
- `--factory-startup` resets the device to CPU: set OptiX in test scripts.

## Change log

- **2026-11-25, v22 render:** on the user's request, set v22 to 128 samples, 90 s limit, 1920×1080 and output `//Render\sh_15_v22\sh_15_v22_`, edited in place. Nothing else was changed. `sh15_v22_atom_build.py` doesn't set these, so re-running it would lose them. Added `Sh_15_v22_render_script.bat` and started the full render, 50–850.
- **2026-11-25, v22:** new hero atom: nucleus, S-orbital cloud and circle (see above). User feedback: "a very (simple) but interesting idea - to make the atom highly resemble its 2D representation"; they want to introduce the same atom in SH_02 first, so that SH_15 is easier to digest.
- **2026-11-25, v21 card 14:** the user duplicated the card; its clip now starts 40 frames later, with its own image datablock (edited in place, still v21). It also no longer goes blank at 425.
- **2026-11-25, notes only:** corrected the dual rail (seen only from above, with several cavities; no photon in the |0⟩ rail), from the user. Earlier notes said the shot simply shows it.
- **2026-11-25, v21 speed:** `res_round_trip` 56 → 45, edited in place (still v21). User feedback: looks great and should stay subtle, but at 56 it was so subtle that it almost looked like a render issue. Added NOTES_FOR_HUMANS.md. Checked at every frame 270–430: no jump from the resonance (the card disappears in a single frame at 425, as in v18 and v20).
- **2026-11-25, v21:** subtle resonance in the hero's photonic mode, 276–578 (see above). The user approved v20's look; main cause of the old bad reflection: the floor panel's outline in the mirror, plus the spot's visible disc in the glass.
- **2026-11-25, v20:** studio lighting for the single-cell part (see above), fading back to the original lighting by 598. Cards hidden from reflections. Recorded the user's explanations of the horizontal tweezers, the Fabry–Pérot cavity and the mirror.
- **2026-11-25, v19:** copied v18. Replaced the mirrored cone with `LaserTweezers` (Gaussian-beam volume with lattice fringes), and replaced the 205–211 fade with the 154–185 glow → dashed outline → nothing fade. Nothing else in the scene changed (checked with an object, animation and material-user dump of both versions).
