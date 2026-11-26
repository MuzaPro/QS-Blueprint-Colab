# SH_12: notes for agents

Last updated: 2026-11-26 (v12). For the film's story and science, read the [project guide](../../AGENTS.md) first. Read this before touching any SH_12 .blend or script. **Keep it updated**: when you change the scene, add what you did, why, and how to undo or re-tune it.

Statements marked *(inferred)* are agent readings the user hasn't confirmed.

## The shot (user, Nov 26)

SH_12 comes right after the narration finishes describing PsiQuantum's huge photonic facility. It introduces Quantum Source's **compound architecture**: photonic qubits and atomic qubits combined, miniaturised, and built on wafer-manufactured photonic components. "Compound Architecture" is the term the company is coining in this video; it is the central concept of the production.

| Part | What we see | Narration (approved script, beat 3) |
|---|---|---|
| Logic card | Card 10: a LIGHT grid (photons) and a MATTER grid (atoms) merge into one lattice where **each photon is entangled with four atoms and each atom with four photons** ("PHOTON-ATOM GRID"). Same visual language as SH_02, now with photons in the grid | "Why choose light or matter when you can leverage the best of both?" |
| Title | **COMPOUND ARCHITECTURE**, large and celebratory, under the finished lattice | "Welcome to Quantum Source Compound Architecture." |
| Chip | The photonic chip comes in from the bottom. Geometry nodes draw the waveguides over it, connecting the Fabry–Pérot cavities (the cylinders) | "We combine the effectively unrestricted connectivity of flying photonic qubits…" |
| Profile | The camera sees the chip edge-on; a wave of tiny atom glows runs through the cavities | "…with the stability of stationary atomic qubits." |
| Ending | A section breaks up, a **pentet** (5 cavities) lifts out, and the camera dives into one cavity in a zoom transition to SH_15 (single-cavity mechanism) | |

The narration timing is **not** in the project in a readable form (no transcript; `06_audio/QS-blueprint-narration-time_nov-05.mp3` only). All v12 beat frames are estimates and are parameters of the build script (see "Re-timing").

## Science behind the pictures

- **Photon-atom grid (Card 10):** the compound cluster state. Photons (cyan dots, flying qubits) and atoms (dot + circle, stationary qubits) alternate; every photon is linked to four atoms and every atom to four photons. In the paper's lattice figures photons are cyan and atoms dark blue.
- **Waveguides = photonic qubits.** They are printed into the wafer and route single photons between cavities. Their appearance is tied to the word "photonic".
- **Atoms = atomic qubits.** One trapped rubidium-87 atom sits in each cavity, between the bottom mirror and the top fibre edge (`atom` in `unit_cell_v7.blend`, z = 0.962 in cell space; the gap is 0.684–1.253). In the film the atoms are normally **omitted for simplicity**. The glow wave says "the atoms are there, we just don't draw them" (user). It is not a physical process: no light travels between atoms and nothing is being computed by the wave. Keep it tiny, subtle and elegant, "like a tiny shine" (user).
- **Cavity = vertical Fabry–Pérot** (see SH_15 notes): top is an optical-fibre edge (glass cylinder), bottom is drawn as a round mirror for clarity.
- **Miniaturisation:** near-deterministic photon–atom gates mean far less hardware than linear-optics photonics, hence a chip instead of a facility.

## Files

| File | What it is |
|---|---|
| `sh_12_The_Turn_and_the_Reveal_12.blend` | **Current** (v12, awaiting the user's review). v11 + everything below. Frames 1–600 |
| `sh_12_The_Turn_and_the_Reveal_11.blend` | User's last version, already rendered (frames 1–313 in `Render/sh_12_chip_intro/`). Don't modify it |
| `_01` … `_10` | Earlier iterations |
| `sh12_v12_build.py` | Builds v12 from v11 (never writes v11; refuses to overwrite v12 without `--force`). **Don't re-run it over a hand-edited v12**: it rebuilds from v11 and would lose those edits |
| `sh12_v12_sh15_camera.json` | SH_15's render camera (`Camera.001`, marker `F_00`) at frames 50–60, read from `sh_15_positioning_and_first_cluster_tile_22.blend`. The dive lands on frame 50 |
| `sh12_v12_build_log.txt` | Output of the last build (anchors, label widths, dive checks) |
| `Sh_12_render_script.bat` | v11 render (1–313). Kept as it was |
| `Sh_12_v12_render_script.bat` | v12 render: same safety settings (batch 5, cooldown 30 s), frames 1–600 |

Build command (from this folder):

```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup sh_12_The_Turn_and_the_Reveal_11.blend --python sh12_v12_build.py -- --force
```

## v12 timeline (25 fps, 600 frames = 24 s)

Old v11 frame *f* is v12 frame *f* + 260 (`OFFSET`). Timeline markers mark every beat.

| v12 frames | v11 frames | What happens |
|---|---|---|
| 1–260 | — | Card 10 plays on `SH12_Card10` (camera holds v11's first pose) |
| 212–290 | — | Title: eyebrow "QUANTUM SOURCE" (212), letters of COMPOUND ARCHITECTURE converge from the outside in (220→), cyan rule grows from the centre (238–268), light sweep (252–290) |
| 261 | 1 | v11 starts: camera moves, chip rises from the bottom; card and title drift up out of frame (world-space) and fade (card 266–300, title 268–290) |
| 278–378 | 18–118 | Waveguides draw (v11 GN animation, unchanged) |
| 322–396 | 62–136 | PHOTONIC QUBITS callout |
| 422–482 | 162–222 | ATOMIC QUBITS callout |
| 430–500 | 170–240 | Atom-glow wave, left to right across the screen in the profile view |
| 486 | 226 | Section break-up (v11, unchanged) |
| 540–600 | 280–340 | `Camera_Dive` takes over and lands on SH_15 frame 50; the rest of the chip sinks away (552–596) |

## What v12 adds

### Card 10 (`SH12_Card10`, material `SH12_Card10`)

- Plays `04_assets/props/2D-Overlays_FrameK/03_Render/Card_10/Card_10_v1.mp4` (350 frames, 1920×1080, 25 fps), card frame 1 = scene frame 1 (`CARD_START`).
- **Colour as alpha (user):** alpha = max(R, G, B); shader = Emission(colour) + Transparent(1 − alpha), so black is fully transparent and lines are premultiplied.
- The plane exactly fills the frame of the camera's first pose, at the focus distance (479 units), so it's sharp and looks like the 2D card. It is in world space, so when v11's camera move starts it drifts up and out like a logic layer floating above the hardware.
- Camera rays only (no reflections in the glass, no lighting).
- Object property `fade` (keyed) dims it; hidden after frame 301.

### Title (`SH12_Title`, `SH12_Title_Eyebrow`, `SH12_Title_Rule`)

- Overpass Light, caps, tracked (character spacing 1.28); cap height 56 px; baseline 250 px below frame centre, under the lattice. Eyebrow in Overpass Mono, brand cyan. Hairline rule in brand cyan.
- Per-character animation in geometry nodes (`SH12_Title_GN`): String to Curves → Fill Curve (**Triangles**: N-gons fills the counters of O, A, R…) → per-letter alpha, rise and spread, stored as attributes `alpha` and `glint` for the shader. Letters converge from the outside in: the two words come together, echoing the grids combining.
- The light sweep tints letters toward cyan as it passes.

### Callouts (`SH12_Photonic_*`, `SH12_Atomic_*`)

- Anchor ring + dot (brand cyan) on the chip, facing the camera. Leader (`*_leader`, GN) joins the anchor to the label every frame. Label (`*_label` empty) is parented to `Camera` in camera space, with its depth keyed every frame to the focus distance, so it stays sharp and keeps its pixel size.
- Text: main line Overpass SemiBold, white, 26 px cap; eyebrow Overpass Mono, cyan, 15 px cap; hairline under the main line.
- PHOTONIC QUBITS / "FLYING · CONNECTIVITY": anchor on a printed waveguide (43.15, −27.71, 2.16), label in the clear strip under the chip (screen y 0.085).
- ATOMIC QUBITS / "STATIONARY · STABILITY": anchor on a front-row atom (77.7, −67.7, 0.96), label above the chip line (screen y 0.70). The atom wave passes this anchor.
- Eyebrow words are taken from the narration ("flying photonic qubits", "stationary atomic qubits", "connectivity", "stability").

### Atom glow (`SH12_AtomGlow`, material `SH12_AtomGlow`)

- One static mesh: 600 small spheres (radius 0.32) at the atom position of every cavity (read from the evaluated `rails_pi_shape.001` instances at v12 frame 450). The linked `atom` in `unit_cell_v7.blend` is untouched and stays hidden.
- Per-vertex `wave_t` (0–1) = position along the camera's screen-right axis at frame 450 (the profile view), so the wave runs left to right on screen.
- Shader: facing-ratio core (power 14 × 3.5) + halo (power 3 × 0.4), white, additive; envelope = rise 5, hold 9, fall 16 frames, starting at `WAVE_START + wave_t × WAVE_TRAVEL`. The frame comes from a driver (`frame`) on a Value node.
- Visible to camera, transmission (seen through the glass) and glossy (a tiny reflection in the mirror); hidden outside 429–502.

### Dive into SH_15 (`Camera_Dive`)

- SH_15's pentet is SH_12's flying pentet (`Unit_Linked.019`) translated by exactly **(99.1, −67.7, 26.834)**, no rotation (checked on all five cavity positions). So SH_15's render camera maps straight into SH_12.
- **SH_15 renders frame 50 with `Camera.001` (85 mm, no DOF)**, not `Camera`: its timeline markers switch cameras. Read the marker-bound camera after `frame_set`.
- `Camera_Dive` is keyed every frame (linear) from 540 to 600: Hermite position and look-at paths that match `Camera`'s position, velocity and aim at 540, and SH_15's pose (velocity 0) at 600. Lens 50 → 85 mm; f-stop 0.05 → 64 (no visible blur, as in SH_15); focus distance follows the look-at target. Checks in the build log: start and end position error 0.0.
- Camera markers: `CAM_main` (1, `Camera`), `CAM_dive` (540, `Camera_Dive`).
- **Chip drop:** every top-level object in collection `Chip_anim` except `Unit_Linked.019` sinks 160 units (`delta_location` z, ease-in, 552–596), so the pentet ends alone on black as SH_15 opens. Their own location keys are untouched.
- Lighting and materials still differ from SH_15's studio lighting; geometry and framing match. A short dissolve in the edit may still help.

## Colour (brand guide)

- Accent = logo colour **P. 319 C, `#4DDDEC`** (RGB 77/221/236); key colour white on this dark scene. Full palette in the [project guide](../../AGENTS.md#brand-colours).
- **Trap: v11 (and v12) use ACEScg as the file's working colour space** (`bpy.data.colorspace.working_space`). Node colours are scene-linear in that space, so a brand hex must be converted sRGB → linear Rec.709 → ACEScg (`brand_color()` in the build script). Typing sRGB values into a colour socket renders a paler cyan. Checked in render: the rule comes out ≈ (70, 221, 236).
- Card 10's own cyan comes from the MP4: its lines render as about (89, 235, 233) and some dots as (0, 255, 255). That's in the card render, not in this scene.

## Re-timing

Everything is in the parameter block at the top of `sh12_v12_build.py`: `OFFSET` (prelude length), `TITLE_IN`, `TITLE_OUT`, `CARD_OUT`, `PHOTONIC_IN/OUT`, `ATOMIC_IN/OUT`, `WAVE_*`, `ATOM_R/CORE/HALO`, `DIVE_T0`, `DIVE_LEN`. Change, rebuild with `--force`, and re-check. Callout anchors are chosen automatically from screen targets (`PH_TARGET`, `AT_TARGET`).

Hand-tuning in the .blend instead: card fade = `SH12_Card10["fade"]` keys; text timing lives in each `*_GN` node group (Map Range from/to values); atom wave in material `SH12_AtomGlow` (Multiply Add node = travel and start; Map Range nodes = envelope).

## Render

- **Purpose (user, Nov 26):** advanced draft, almost final; changes may still be requested. Final quality goes to a render farm once approved.
- `Sh_12_v12_render_script.bat` (based on SH_15's v22 bat), frames 1–600, output `Render\sh_12_v12\sh_12_v12_####.exr` (also the .blend's own path; a new folder because frame numbers shifted, so v11's frames in `Render/sh_12_chip_intro/` stay valid for v11).
- **Breaks by time, not frame count (user):** frames render until `RENDER_WINDOW_SEC` = 120 s of render time (wall time per frame, including Blender's start-up) has passed, then the GPU rests `COOLDOWN_SEC` = 60 s. A frame that starts inside the window finishes. Resume (`RESUME=1`) and `FRAME_LIST` work as in SH_15.
- **Quality:** the .blend's settings (128 samples, 30 s limit, 100 %, OptiX). Measured on heavy frames 380 and 585: ~10.4 s render, ~13.5 s per frame with start-up, so ~9 frames per window (the user hoped for 3–6). If frames get slower, the user approved `SAMPLES=64` and `RES_PCT=75` for drafts: set them at the top of the bat (passed with `--python-expr`, the .blend is not changed); measured ~8 s per frame.
- Estimate at current speed: ~600 × 13.5 s ≈ 2 h 15 min rendering + ~65 breaks of 60 s ≈ 3 h 20 min in total.
- Tested on 2026-11-26 with frames 300–302 (shortened window): breaks and resume work; those three EXRs are valid v12 output and are kept.

## Change log

- **2026-11-26, v12** (agent, user's brief): Card 10 prelude (+260 frames, all keys shifted), Compound Architecture title, photonic and atomic callouts, atom-glow wave, dive to SH_15 frame 50 with chip drop. Accent checked against the brand guide (ACEScg conversion fixed after the first test). User feedback so far: "looks good so far".
