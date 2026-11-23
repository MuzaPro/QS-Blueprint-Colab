# SH_02 — Shot context for AI agents

Read this before editing `SH_02_Tweezers_and_logic_grid_v02.blend` or the scripts in this folder.

## The film and where this shot sits

An explainer about neutral-atom quantum computing, aimed at engineers and investors (35–60). The tone is
restrained, precise and elegant. It is not sci-fi spectacle; every visual idea should be physically
motivated or a clean graphic abstraction.

- **SH_1** dives through the front viewport of a vacuum chamber. Its last frame shows a column of red
  tweezer beams standing in front of a dark circular aperture with a violet ring
  (`11_reference/vacuum_chamber/vacuum_chamber_fron_window_right_before_transition2.jpg`).
  SH_1 shows generic technology: red lasers, no cyan, no photonics, no Pasqal branding.
- **SH_02** (this shot) continues inside the chamber at atomic scale. A 12×12 grid of atoms is held by
  vertical red optical tweezers. The camera dives in (frames 1–16), then drifts slowly around and above
  the array.
- Partway through SH_02 the edit **crossfades from the atomic layer to the logic layer** (around frame
  100–120; the director picks the exact frame after seeing both renders). The logic layer is a 2D visual
  language (each qubit drawn as a dot inside a ring, plus lines between them) used to explain errors in the
  surface code. Red glyphs mark errors.

## File structure

One blend, two scenes. **The camera animation must stay identical in both**, because they are rendered
separately and crossfaded in the edit.

| Scene | Role | Frames | Camera |
|---|---|---|---|
| `Scene` | Atomic layer: beams, atoms, vacuum chamber | 1–177 | `Camera` (tracks `tracking_point`) |
| `Scene.001` | Logic layer: qubit icons, error glyphs, wireframe reveal | 1–250 | `Camera.001`: same keys to 178, then pulls back to frame 247 |

Lens: 85 mm, **f/0.15**, focused on the grid about 11–12 units away. Depth of field is extreme: anything more
than a few units off the focal plane becomes bokeh. Fine detail far from the grid can't be seen. Far
geometry only contributes soft light and colour. Design for that.

Scale: the atom grid spans ±2.44 units at z = 1.78. Beams run from about z −12.7 to +16.2. Atom radius is 0.05.

## The atomic scene (`Scene`)

Built by `sh02_atomic_chamber_build.py` (re-runnable; it rebuilds its own objects).

- `atomic_chamber` collection:
  - `chamber_shell`: inward-facing sphere, r = 140, centred on the grid. Material `chamber_wall`: dark
    violet metallic steel, faint latitude ribs every 10° (emission), an equator glow, and slight gloss
    that smears beam reflections.
  - `port_*`: viewport windows on the shell (dark glass, a violet halo ring, a steel flange with bolts),
    all instances of one unit-radius mesh scaled per port. `port_main` sits directly behind the array
    at the start, so frame 1 echoes SH_1's last frame.
  - `objective_lower` / `objective_upper` and their front lenses: stacked objective housings below and
    above the array. The beam ends are buried inside them.
  - `untrapped_atoms`: 260 faint background atoms (geometry nodes group `UntrappedAtoms`) that drift
    with a 4D noise driven by scene time. Their material is emission plus transparent, so they only add
    light and never occlude the beams. They're kept away from the trapped plane so they can't be read
    as grid sites.
  - `trap_cloud_haze`: a faint emission-only volume, a residual cold-atom glow around the array.
- `tweezers_atomic`: a render-hidden copy of `tweezers` with material `tweezers-atomic`
  (brightest at the focal plane, a small hot spot at each atom, 45% at the beam ends). The `Tweezers`
  node group points at this copy. **The original `tweezers` object is also instanced by the logic scene,
  so don't change the original.**
- The old background (`Cube`, `bg`) is in `old_bg_RETIRED`, which is excluded from the view layer.

## The logic scene (`Scene.001`)

Built by `sh02_logic_wireframe_build.py` (re-runnable; it replaces the `logic_wireframe` collection).

- Concept: when we cross into the logic layer, a wireframe ghost of the physical chamber glows
  briefly and then fades to black, leaving only the information layer.
- `logic_wireframe` collection (curve objects, emission plus transparent, no light emission sampling, no
  shadows):
  - `wire_ghost_tweezers`: hairline columns through every qubit site, faded vertically and by camera
    distance so only the in-focus band shows. This layer takes over from the red beams during the
    crossfade.
  - `wire_shell_latitudes`, `wire_ports`, `wire_port_main_bolts`, `wire_objective_lower`: the chamber
    outline. The shell is **r = 32 here, not 140**, so it fits inside the existing room (see below).
    Through the lens blur it only reads as a soft streak of light.
- Timing is driven by the Scene.001 custom property `wire_reveal_frame` (see `SH_02_ANIMATOR_NOTES.md`).
- **Don't remove `Cube.001` (room) or `bg.001` (huge floor).** They render pure black during the
  transition, but they hide far-away arrays (`atoms-geo-nodes.002`–`.005`, `Text`) and set up the
  pull-back reveal at frames ~180–247. Removing them exposes a grey curtain of beams.
- The material `bg` is shared with `atomic-logic.001`, so don't edit it for background purposes.

## Gotchas learned the hard way

- Batch renders need `--factory-startup`. The user's add-ons (AI-Render, rbc_addon_free, Bagapie,
  population) throw errors on load and on every frame. Factory startup resets Cycles to CPU;
  `render_gpu_setup.py` turns OptiX back on.
- To render a specific scene from Python in background mode, `frame_set` + `render.render(scene=...)`
  on a non-active scene silently renders the wrong camera state. Use the command line instead:
  `blender -b file -S "Scene.001" -o ... -f N`.
- Object-type Attribute nodes reading custom properties were unreliable on curve objects here. Use
  per-layer materials with Value nodes instead.
- Port meshes are unit radius: geometry offsets are multiplied by the object scale, so keep depth
  offsets proportional, or the window ends up outside the shell.

## Rendering

`render_SH_02.bat` renders `Scene` (1–177) and then `Scene.001` (1–250) to
`08_renders/Final_draft/sh_02_tweezers_v02/` and `.../sh_02_logic_v02/` (32-bit EXR). It skips frames
that already exist, so re-running resumes. The older renders in `sh_02_tweezers/` and `sh_02_logic/` are
kept for comparison. Low-res previews are in `previews/`.
