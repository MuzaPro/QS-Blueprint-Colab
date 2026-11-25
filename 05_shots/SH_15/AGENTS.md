# SH_15: notes for agents

Last updated: 2026-11-25 (v20). For the film's story and science, read the [project guide](../../AGENTS.md) first. Read this before touching any SH_15 .blend or script. **Keep it updated**: when you change the scene, add what you did, why, and how to undo or re-tune it.

Statements marked *(inferred)* are agent readings of the file. The user hasn't confirmed them.

## The shot

- **What it shows** *(inferred from the scene and file name, except where marked)*: the unit cell up close. An atom is carried into an optical cavity and held there, then a photon enters the cavity **in the shape of the photonic mode** (user), the **dual rail** is shown (user), and the camera later pulls back over a row of cells building the first cluster tile.
- Being polished for the final version (user, Nov 25). Tweaks come one at a time.
- **The atom** is `Icosphere.001` (rubidium-87). It travels along Y during frames 124–152 and then stays at (2.6, −0.073, 0.976). Its sparkle is the `atom` material (animated Voronoi).
- **The cell is a vertical Fabry–Pérot cavity (user).** The top part (`rails_pi_shape.001`, glass) is the **edge of an optical fibre**. In reality the bottom is another fibre edge too, but the film uses a **very reflective round mirror** (`mirror`) so viewers read it clearly. Don't "correct" it.
- **The laser tweezers hold the atom floating in space (user).** After they are introduced they are **omitted to simplify the visuals, and the fade must imply they are still there (user)**. They have to be completely gone by **frame 185** (user).

### Science notes on the tweezers

- **The tweezers are horizontal on purpose (user):** the team chose the simpler horizontal beam so viewers don't confuse it with the **vertical photonic mode**. In the paper (section II.A, Fig. 1) the trap is a far-detuned 1D optical lattice formed by a TEM00 mode of the cavity itself, so this is a deliberate simplification. Don't re-orient it.
- **Approved (user, Nov 25):** the dashed-outline fade ("exactly what was missing") and the lobes, which make it look like the sophisticated (if not novel) laser technology it is.
- The fringes near the atom come from that paper: a standing wave, with the atom sitting in the central bright fringe. (For red-detuned light, atoms are trapped at intensity maxima: agent knowledge.)
- The beam is brightest at its focus and opens into an hourglass, as a real focused Gaussian beam does. v18's cone was dimmest at the focus.
- **Colour:** rose-copper, kept from the user's old beam. Pure red lasers belong to the competitor machines and cyan/teal to the photon, so stay away from both.

## Files

| File | What it is |
|---|---|
| `sh_15_positioning_and_first_cluster_tile_20.blend` | **Current.** v19 + studio lighting for the single-cell part |
| `sh_15_positioning_and_first_cluster_tile_19.blend` | v18 + new laser tweezers and fade |
| `sh_15_positioning_and_first_cluster_tile_18.blend` | User's last version. Don't modify it |
| `_11` … `_17` | Earlier iterations |
| `sh15_v19_tweezers_build.py` | Builds v19 from v18 (never writes v18). **Don't re-run it once v19 has been edited by hand**: it would overwrite those edits. Pass another output path after `--` to build elsewhere |
| `sh15_v20_studio_light_build.py` | Builds v20 from v19 (never writes v19). Same rule: don't re-run it over a hand-edited v20 |
| `Sh_15_render_script.bat` | Render loop. **Still points at `_18`, frames 213–850** (user's setting, untouched) |
| `Render/sh_15_cavities/` | EXR output of the .blend. At the time of writing, these frames predate v19 and v20 |
| `Render/sh_15_v20_lighting_preview_*.mp4` | Low-res Cycles previews of the v20 light: 52–230 (every 2nd frame, at real speed) and the hand-over 566–606. Rendered just before the cards were hidden from reflections |
| `Render/sh_15_v19_tweezers_preview_138-192.mp4` | Half-res Cycles preview of the new tweezers (64 samples, 25 fps) |

## Scene facts

- **Blender 5.2.** Scene range 50–850, 25 fps, 1920×1080, Cycles 256 samples adaptive 0.01, 45 s limit, OIDN, 32-bit EXR, motion blur off, view transform Standard, no compositor. The colour grade happens outside Blender *(inferred: the user's screenshot is warmer/teal-graded compared to a raw render)*.
- **Cameras** are switched by timeline markers: `F_00` → `Camera.001` (rig `Armature`), `F_218` (at frame **228**, not 218) → `Camera`, `F_431` → `Camera.001`.
- `unit-cell-Linked*` are instances of a collection **linked** from `04_assets/props/unit_cell_v7.blend` (glass fibre cavity `rails_pi_shape.001`, curved `mirror`). Edit them there.
- `Card_13-14_v2` is the diagram card next to the atom; its graphics start to appear around frame 160.
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

Not driven: `Card_13-14_v2` and `Card_15` have Ray Visibility → Glossy off.

**How the fibre/mirror split works:** from these cameras the fibre reflects slightly *up* and the mirror slightly *down*. Glass reflects only about 4 %, so only the part of the bands above the horizon is boosted, and only for reflections. If a camera moves below the mirror's top, lower `glass_boost` there.

**Traps:** bands behind the cell (more than about 140° from the camera) show through the rough glass ceiling as big grey patches; keep rim bands at 130° or less. The linked `mirror` and `Photon_Glass` materials weren't touched, because other shots use them. The small notch on the mirror's right edge around 205 is the neighbouring cell's real reflection. During 586–597 the first cell briefly goes back to the original lighting as it leaves the frame.

**Checked:** with the lighting change alone, frames 598, 600, 640, 700 and 845 are pixel-identical to v19. With the cards hidden from reflections, the mean difference there is at most 0.011 of 255. Render time is about the same as v19 (18–38 s for frames 160, 205, 300 and 520, full res at the shot's settings).

## Rendering notes

- **v20 changes frames 50–597**, so the whole single-cell part needs re-rendering, plus a few pixels of mirrored card text after that.

- Frames that changed from v18 to v19: 138–211. 138–185 show the new beam; 186–211 no longer show the old one (it used to disappear at 211). Frames 52, 60, 186, 240 and 300 were compared with v18: they match apart from the old beam being gone in 186. Safe re-render range for v19 alone: 124–211 (v20 supersedes this).
- A full-res frame with the beam takes about 21 s on the RTX 3080 at the shot's own settings, with another render sharing the GPU.
- `--factory-startup` resets the device to CPU: set OptiX in test scripts.

## Change log

- **2026-11-25, v20:** studio lighting for the single-cell part (see above), fading back to the original lighting by 598. Cards hidden from reflections. Recorded the user's explanations of the horizontal tweezers, the Fabry–Pérot cavity and the mirror.
- **2026-11-25, v19:** copied v18. Replaced the mirrored cone with `LaserTweezers` (Gaussian-beam volume with lattice fringes), and replaced the 205–211 fade with the 154–185 glow → dashed outline → nothing fade. Nothing else in the scene changed (checked with an object, animation and material-user dump of both versions).
