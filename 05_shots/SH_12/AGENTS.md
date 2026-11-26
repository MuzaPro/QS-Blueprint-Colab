# SH_12: notes for agents

Last updated: 2026-11-26 (v15). For the film's story and science, read the [project guide](../../AGENTS.md) first. Read this before touching any SH_12 .blend or script. **Keep it updated**: when you change the scene, add what you did, why, and how to undo or re-tune it.

Statements marked *(inferred)* are agent readings the user hasn't confirmed.

## The shot (user, Nov 26)

SH_12 comes right after the narration finishes describing PsiQuantum's huge photonic facility. It introduces Quantum Source's **compound architecture**: photonic qubits and atomic qubits combined, miniaturised, and built on wafer-manufactured photonic components. "Compound Architecture" is the term the company is coining in this video; it is the central concept of the production.

| Part | What we see | Narration (approved script, beat 3) |
|---|---|---|
| Logic card | Card 10: a LIGHT grid (photons) and a MATTER grid (atoms) merge into one lattice where **each photon is entangled with four atoms and each atom with four photons** ("PHOTON-ATOM GRID"). Same visual language as SH_02, now with photons in the grid | "Why choose light or matter when you can leverage the best of both?" |
| Title | **COMPOUND ARCHITECTURE**, large and celebratory, **above** the lattice. It appears as the grids begin merging, stays while the chip rises, slides up toward the top of the frame, then leaves | "Welcome to Quantum Source Compound Architecture." |
| Chip | The photonic chip comes in from the bottom, under the title, while the lattice is still on screen for a moment. Geometry nodes draw the waveguides over it, connecting the Fabry–Pérot cavities (the cylinders) | "We combine the effectively unrestricted connectivity of flying photonic qubits…" |
| Profile | The camera sees the chip edge-on; a wave of tiny atom glows runs through the cavities | "…with the stability of stationary atomic qubits." |
| Ending | A section breaks up, a **pentet** (5 cavities) lifts out, and v11's swift camera move dives into it, cutting to SH_15 (single-cavity mechanism) | |

**The lattice overlapping the chip is deliberate (user):** for about 12 frames the photon-atom grid sits over the rising chip before it fades. It implies the grid corresponds to what happens on the chip, which is correct. It must not last long: longer is visually disturbing.

## Timing (user's final draft, Nov 26)

The shot is exactly **18 s 12 f = 462 frames** at 25 fps. Frame 1 = 0 s.

| Time | Frame | Event |
|---|---|---|
| 0 s | 1 | The photonic (LIGHT) grid begins to appear on the left: Card 10 frame 1 |
| 3 s 12 f | 88 | The grids begin to merge → the title starts |
| 6 s | 150 | Merge done; the photonic chip starts to float in from below (v11 frame 1) |
| 10 s 11 f | 262 | Narration: "**flying**" (photonic qubits). The photonic callout must already be (mostly) up |
| 13 s 20 f | 346 | Narration: "**stationary**". The atomic callout appears |
| 18 s 12 f | 462 | End, on v11's last frame (313) |

The user also asked for "the card to start 5 s 8 f later". In Card 10's own timing the LIGHT grid appears in its first frames, merging starts at its frame ~88 and ends at ~150, so this matches the table above with card frame 1 = shot frame 1. The change is that the card's long hold after the merge (v12 kept it until frame 260) is gone. *(inferred: the 5 s 8 f is where the shot starts in the edit, not a trim of the card; confirm if the card looks wrong)*

## Science behind the pictures

- **Photon-atom grid (Card 10):** the compound cluster state. Photons (cyan dots, flying qubits) and atoms (dot + circle, stationary qubits) alternate; every photon is linked to four atoms and every atom to four photons. In the paper's lattice figures photons are cyan and atoms dark blue.
- **Waveguides = photonic qubits.** They are printed into the wafer and route single photons between cavities. Their appearance is tied to the word "photonic".
- **Atoms = atomic qubits.** One trapped rubidium-87 atom sits in each cavity, between the bottom mirror and the top fibre edge (`atom` in `unit_cell_v7.blend`, z = 0.962 in cell space; the gap is 0.684–1.253). In the film the atoms are normally **omitted for simplicity**. The glow wave says "the atoms are there, we just don't draw them" (user). It is not a physical process: no light travels between atoms and nothing is being computed by the wave. Keep it tiny, subtle and elegant, "like a tiny shine" (user).
- **Cavity = vertical Fabry–Pérot** (see SH_15 notes): top is an optical-fibre edge (glass cylinder), bottom is drawn as a round mirror for clarity.
- **Miniaturisation:** near-deterministic photon–atom gates mean far less hardware than linear-optics photonics, hence a chip instead of a facility.

## Files

| File | What it is |
|---|---|
| `sh_12_The_Turn_and_the_Reveal_15.blend` | **Current** (v15, awaiting review). v14 + the user's v14 notes: smaller, twice as many photons; photonic callout elbow on the right; atomic callout rides on the dive cavity and stays to 436; dark floor fades in during the dive. Frames 1–462 |
| `sh_12_The_Turn_and_the_Reveal_14.blend` | v14: "truly fantastic, we are almost there" (user). Rendered at 50 % in `Render/sh_12_v14/` |
| `sh_12_The_Turn_and_the_Reveal_13.blend` | v13: user's draft timing; "the timing is perfect and the story kind of works" (user). Rendered at 50 % in `Render/sh_12_v13/` |
| `sh_12_The_Turn_and_the_Reveal_12.blend` | v12 (frames 1–600, rendered in `Render/sh_12_v12/`). **Rejected parts:** its custom dive camera ruined the transition, the card ran too long, the chip timing didn't match the narration. Keep for reference |
| `sh_12_The_Turn_and_the_Reveal_11.blend` | User's last version (frames 1–313 in `Render/sh_12_chip_intro/`). Source of every build. Don't modify it |
| `_01` … `_10` | Earlier iterations |
| `sh12_v15_build.py` | Builds v15 from v11 (never writes v11; refuses to overwrite v15 without `--force`). **Don't re-run it over a hand-edited v15**: it rebuilds from v11 and would lose those edits |
| `sh12_v14_build.py` | Builds v14 (kept for reference) |
| `sh12_v13_build.py` | Builds v13 (kept for reference) |
| `sh12_v12_build.py`, `sh12_v12_sh15_camera.json`, `sh12_v12_build_log.txt` | v12's build, kept for reference (the JSON is SH_15's `Camera.001` at frames 50–60; v13 doesn't use it) |
| `sh12_v15_build_log.txt`, `sh12_v14_build_log.txt`, `sh12_v13_build_log.txt` | Output of the last builds (anchors, label widths, photon counts, anchor visibility checks) |
| `Sh_12_render_script.bat` | v11 render (1–313). Kept as it was |
| `Sh_12_v12_render_script.bat` | v12 render (1–600, the .blend's quality) |
| `Sh_12_v13/v14/v15_render_script.bat` | Draft renders: frames 1–462, 50 % resolution, 32 samples |

Build command (from this folder):

```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup sh_12_The_Turn_and_the_Reveal_11.blend --python sh12_v15_build.py -- --force
```

## Timeline (v15; 25 fps, 462 frames)

v11 frame *f* is v13 frame *f* + 149 (`OFFSET`), so v11 1–313 lands on 150–462. Timeline markers mark every beat (`MERGE_TITLE_in`, `CHIP_in_v11_f001`, `VO_flying`, `VO_stationary`…).

| v13 frames | v11 frames | What happens |
|---|---|---|
| 1–149 | — | Card 10 plays (card frame = shot frame); camera holds v11's first pose |
| 88–150 | — | Title: eyebrow "QUANTUM SOURCE" (88), letters converge from the outside in (96→), cyan rule grows from the centre (114–144), light sweep (128–166) |
| 150 | 1 | v11 starts: chip floats in from below. Card and title start sliding up together |
| 150–174 | 1–25 | Grid overlaps the rising chip, then fades (162–174) |
| 150–164 | 1–15 | Eyebrow fades (it would leave the frame) |
| 150–194 | 1–45 | Title slides up 130 px toward the top of the frame |
| 184–202 | 35–53 | Title leaves: letters drift apart and fade; rule retracts to the centre |
| 134 | — | Card mask hides "PHOTON- ATOM GRID" (v14) |
| 206–267 | 57–118 | Waveguides draw on, starting at the chip's right edge (centre bus) and growing left (v11 GN in `assable`) |
| 238–366 | 89–217 | PHOTONIC QUBITS callout, pointing at the draw start (text fully up ~262, "flying") |
| 248–375 | 99–226 | Photons flow in the waveguides (full by 262, dimmed to 15 % from 318–334) |
| 308–382 | 159–233 | Atomic-layer glow in the middle of the wafer sandwich (full 326–366) |
| 324–394 | 175–245 | Atom-glow wave, left to right across the screen in the profile view |
| 328–436 | 179–287 | ATOMIC QUBITS callout (text lands ~346, "stationary"), anchored on the dive cavity and carried up with it into the dive; overlaps the photonic one for ~38 frames, which the user allowed |
| 438–456 | 289–307 | Dark floor plane turns black, front travelling +X → −X (v15) |
| 375 | 226 | Section break-up (v11, unchanged) |
| 372–462 | 223–313 | **v11's own camera move into the pentet**; its tail runs 1 v11 frame further, so 462 shows v11's 314 pose (closer to the cavity) |

## What v13–v15 add to v11

### Card 10 (`SH12_Card10`, material `SH12_Card10`)

- Plays `04_assets/props/2D-Overlays_FrameK/03_Render/Card_10/Card_10_v1.mp4` (350 frames, 1920×1080, 25 fps), card frame 1 = scene frame 1 (`CARD_START`).
- **Colour as alpha (user):** alpha = max(R, G, B); shader = Emission(colour) + Transparent(1 − alpha), so black is fully transparent and lines are premultiplied.
- **Camera space (changed in v13):** the plane is a child of `SH12_Card_rig`, an empty parented to `Camera` whose location and scale are keyed every frame so it sits at the focus distance (≈466) and fills the frame. That keeps it sharp and lets it slide on cue. It is moved 220 px down (`CARD_Y_PX`, measured) so the title fits above the grid.
- Slides up 70 px (150–176) and fades (162–174, object property `fade`); hidden after 175. Camera rays only.
- **The "PHOTON- ATOM GRID" words are masked (v14, user):** they competed with the title. The material multiplies the alpha by 0 inside a UV box (`CARD_WORDS_UV` = u 0.660–0.805, v 0.815–0.905), switched on by the keyed object property `words_off` at 134. Measured on the MP4 itself: the words sit at u 0.670–0.795, v 0.829–0.892; the grid's right edge on those rows is ≤ 0.656, and nothing else enters the box after card frame 134. If the card is re-rendered without the words, set `words_off` to 0.

### Title (`SH12_Title`, `SH12_Title_Eyebrow`, `SH12_Title_Rule`)

- Overpass Light, caps, tracked (character spacing 1.28); cap height 56 px; baseline 270 px above frame centre, **above the grid** (as in the user's draft). Eyebrow in Overpass Mono, brand cyan. Hairline rule in brand cyan, 30 px under the baseline.
- All three are children of `SH12_Title_rig` (camera space, like the card). The rig slides 130 px up from 150 to 194 (`TITLE_SLIDE`) while the chip rises: "let it slide upward to the top of the screen while the chip is appearing from below in a matching fashion" (user).
- Per-character animation in geometry nodes (`SH12_Title_GN`): String to Curves → Fill Curve (**Triangles**: N-gons fills the counters of O, A, R…) → per-letter alpha, rise and spread, stored as attributes `alpha` and `glint` for the shader. Letters converge from the outside in, echoing the grids combining; on exit they drift apart again (`out_spread`) as they fade.
- The light sweep tints letters toward cyan as it passes.

### Callouts (`SH12_Photonic_*`, `SH12_Atomic_*`)

- Anchor ring + dot (brand cyan) on the chip, facing the camera. Leader (`*_leader`, GN) joins the anchor to the label every frame. Label (`*_label` empty) is parented to `Camera` in camera space, with its depth keyed every frame to the focus distance, so it stays sharp and keeps its pixel size.
- Text: main line Overpass SemiBold, white, 26 px cap; eyebrow Overpass Mono, cyan, 15 px cap; hairline under the main line.
- PHOTONIC QUBITS / "FLYING · CONNECTIVITY": anchor at **the right-hand end of the centre bus, where the waveguides start drawing** (user, v14): (109.1, 0.05, 2.16), found as the first tube vertices the draw-on shows at v11 frame 60. Label in the clear strip under the chip (screen y 0.085). **v15 (user): the elbow is on the right** (screen x = anchor x + `PH_ELBOW_DX` 0.085, ≤ 0.90), with the text right-aligned and ending at the elbow, so the leader runs out into the clear space right of the chip instead of mostly behind it (`callout(..., side=-1)`).
- ATOMIC QUBITS / "STATIONARY · STABILITY": **v15 (user): anchored on the atom of the very cavity the camera dives into**, (101.7, −67.7, 0.96), the atom nearest the camera's focus object `TrackTo`. The anchor empty is parented to `Unit_Anim` (the pentet that lifts out from ~376), so the callout rides up with it and can stay until 436 (was 398, about 1.5 s more). Its ring is keyed per frame by the anchor's depth and the leader radius follows the label's scale, so both keep their pixel size as the camera approaches (anchor depth 317 → 176). Label elbow at screen (0.60, 0.80) (`AT_LABEL`), above the chip's far edge through the dive.
- The build log checks that both anchors stay on screen for their whole span.
- Eyebrow words are taken from the narration ("flying photonic qubits", "stationary atomic qubits", "connectivity", "stability").

### Atom glow (`SH12_AtomGlow`, material `SH12_AtomGlow`)

- One static mesh: 600 small spheres (radius 0.32) at the atom position of every cavity (read from the evaluated `rails_pi_shape.001` instances at v11 frame 190). The linked `atom` in `unit_cell_v7.blend` is untouched and stays hidden.
- Per-vertex `wave_t` (0–1) = position along the camera's screen-right axis at v11 frame 190 (the profile view), so the wave runs left to right on screen.
- Shader: facing-ratio core (power 14 × 3.5) + halo (power 3 × 0.4), white, additive; envelope = rise 5, hold 9, fall 16 frames, starting at `WAVE_START + wave_t × WAVE_TRAVEL`. The frame comes from a driver (`frame`) on a Value node.
- Visible to camera, transmission (seen through the glass) and glossy (a tiny reflection in the mirror).

### Photons in the waveguides (`SH12_Photons`, `SH12_Photons_GN`, material `SH12_Photon`), v14–v15

- **v15 (user): "much smaller and maybe double the amount… smaller than the cavities", even if barely visible.** Head radius 0.26 (was 0.55), tail spacing 0.36 (was 0.75), `PH_PROB` 0.28 (was 0.14), strength 14 (was 9). About 35–43 on screen. The v14 figures below are superseded where they differ.

- The user asked for "not a lot, just enough to see that these are waveguides". Cyan comets (head radius 0.55, an 8-copy tail 0.75 apart) run along the chip's own waveguide curves: the same `Chip` collection that `assable`'s draw-on reads (realised: 864 splines).
- Only splines ≥ 30 units (`PH_MIN_LEN`; most are 6–7-unit stubs inside the tiles). One slot per spline; on each lap a slot carries a photon with chance 0.14 (`PH_PROB`), so arrivals are irregular, as single-photon events are (see SH_18). About 20 on screen at once. Speed 2.4 units/frame ± 15 %.
- Written from scratch in v14, in the spirit of the photon-on-curve groups in SH_7, SH_8 and SH_18 (v11's waveguide curves carry the same "movement progression / OBJ count" group, unused here).
- Fade (object property `fade`): 248 → full at 262, dimmed to 15 % for the atomic beat (318–334); hidden with `assable` at the break-up (376).
- Caveat: between 248 and ~265 the draw-on isn't quite finished, so a photon may briefly run on a not-yet-drawn stretch at the far left *(not seen in tests)*.

### Atomic-layer glow (`SH12_AtomLayerGlow`, material `SH12_AtomLayerGlow`), v14

- The user said the atom wave went unnoticed because the callout steals attention, and asked for a glow in the middle of the wafer sandwich "so people see we are now talking about that area".
- A volume box over the whole chip with emission only (no scattering): a Gaussian core at the atom plane (z 0.962, sigma 0.13, inside the 0.684–1.253 cavity gap) plus a faint halo (sigma 1.4, weight 0.1), so edge-on it reads as a glowing line through the sandwich. It brightens where the atom wave passes (same axis and timing as the wave; 35 % baseline).
- Colour: brand **P. 2716 C `#98A6F9`**, a soft blue for the atomic layer, kept apart from photonic cyan. In 308–326, out 366–382.
- A pointer, like the wave: not a physical process.

### Dark floor for the dive (`SH12_DiveDarkFloor`), v15

- The user: the cut to SH_15 flashed, because SH_12's last frame was bright (the chip filled the frame) and SH_15 is dark. Their suggestion: a horizontal plane with a dark material that turns from transparent to dark during the dive, from camera right toward camera left (into the screen), i.e. from +X to −X.
- An 800 × 800 plane, starting at z 3.2 (`DARK_Z`), just above everything left on the chip (router bars top out at 3.04; cavity tops 2.33). **It rises with the pentet (user: "pick up the dark plane so it covers all the irrelevant mesh")**: keyed per frame to stay `DARK_GAP` 0.4 under the pentet's lowest point (never below 3.2), ending at z 26.6. Everything else, including the larger piece that lifts to z ~17.6 under the pentet, ends up below it, so the shot ends on the pentet alone over black. Black emission mixed with transparent; the dark front's x moves from 125 to −150 over 438–456 (`DARK_SWEEP`, `DARK_X`, smoothstep; the visible wipe is ~440–449). User: the wipe should take under 19 frames and start when the camera is closer to the pentet (it was 400–452, then 416–456) with a 45-unit soft edge (`DARK_SOFT`). The pentet (`Unit_Anim`) has cleared z 3.2 by ~401, so it's never cut.
- Visible to camera, glossy and transmission rays (so the glass doesn't show the bright chip), no shadow or diffuse.
- The v15 render was stopped three times (after frames 111, 115 and 146) for these changes and resumed; the plane is hidden before 437, so the frames already rendered were unaffected.

### Ending: v11's camera (tail slightly extended in v14)

- **Don't replace v11's camera move (user, Nov 26).** v12 swapped it for a Hermite dive that matched SH_15 frame 50 exactly, and the user said it ruined the transition: the swift original move and its blur already sell the cut. Removing the rest of the chip from the background isn't important, so v13 has no chip drop either.
- Marker `CAM_main` at frame 1 binds `Camera` before v11's shifted `F_00` marker at 149.
- **v14: closer at the end (user).** v11's move keeps going to v11 frame 316 (465 here), past the shot's end. The keys of `Armature.001Action` (the camera rig `CAM`) and `CameraAction` after v11 193 are time-compressed by `END_PUSH` = 1 v11 frame, so the same path is reached slightly sooner and 462 shows v11's 314 pose: a close, shallow-focus view of a cavity. 1 frame is the useful limit: by v11's 315 pose the camera has already flown past the pentet.
- Motion blur is **off** in v11's scene settings (and so in v13); the blur the user mentions may come from the edit or grade *(inferred)*. Don't turn it on without asking.

## Colour (brand guide)

- Accent = logo colour **P. 319 C, `#4DDDEC`** (RGB 77/221/236); key colour white on this dark scene. Full palette in the [project guide](../../AGENTS.md#brand-colours).
- **Trap: v11 (and v12, v13) use ACEScg as the file's working colour space** (`bpy.data.colorspace.working_space`). Node colours are scene-linear in that space, so a brand hex must be converted sRGB → linear Rec.709 → ACEScg (`brand_color()` in the build script). Typing sRGB values into a colour socket renders a paler cyan. Checked in render: the rule comes out ≈ (70, 221, 236).
- Card 10's own cyan comes from the MP4: its lines render as about (89, 235, 233) and some dots as (0, 255, 255). That's in the card render, not in this scene.

## Re-timing

Everything is in the parameter block at the top of `sh12_v15_build.py`: `OFFSET` (where the chip starts), `END_PUSH`, `PH_ELBOW_DX`, `AT_LABEL`, `DARK_*` (dark floor), `CARD_WORDS_*`, `PH_*` (photons), `LAYER_*` (layer glow), `CARD_Y_PX`, `CARD_FADE`, `CARD_SLIDE`, `TITLE_IN`, `TITLE_Y_PX`, `TITLE_SLIDE`, `EYEBROW_OUT`, `TITLE_OUT`, `PHOTONIC_IN/OUT`, `ATOMIC_IN/OUT`, `WAVE_*`, `ATOM_R/CORE/HALO`. Slides are `(start, end, px)`. Change, rebuild with `--force`, and re-check. Callout anchors are chosen automatically from screen targets (`PH_TARGET`, `AT_TARGET`).

Hand-tuning in the .blend instead: card fade = `SH12_Card10["fade"]` keys; slides = location keys on `SH12_Card_rig` / `SH12_Title_rig` (keyed every frame; the y value holds the slide); text timing lives in each `*_GN` node group (Map Range from/to values); atom wave in material `SH12_AtomGlow` (Multiply Add node = travel and start; Map Range nodes = envelope).

## Render

- `Sh_12_v15_render_script.bat` (same as v13's and v14's, which came from SH_15's v22): frames 1–462, output `Render\sh_12_v15\sh_12_v15_####.exr` (also the .blend's own path). v14's draft is in `Render/sh_12_v14/` (5.0 s per frame). v13's draft is in `Render/sh_12_v13/` (4.7 s per frame on average).
- **Quality (user, Nov 26): render it "safely at 50 % and a low sample rate".** The bat passes `SAMPLES=32`, `RES_PCT=50` with `--python-expr`; the .blend keeps its own settings (128 samples, 75 % in v11's file). Test stills at 24 samples took about 2 s each.
- **Breaks by time, not frame count (user):** frames render until `RENDER_WINDOW_SEC` = 120 s of wall time has passed, then the GPU rests `COOLDOWN_SEC` = 60 s. A frame that starts inside the window finishes. Resume (`RESUME=1`) and `FRAME_LIST` work as in SH_15.
- v12's full render (600 frames, 128 samples, 1 h 15 min of render time) finished on 2026-11-26 in `Render/sh_12_v12/`.

## Change log

- **2026-11-26, v15** (agent, user's v14 review: "truly fantastic, we are almost there"): photons smaller (r 0.26) and twice as many; photonic callout elbow flipped to the right; atomic callout anchored on the dive cavity (rides with `Unit_Anim`) and kept to 436; dark floor plane sweeps +X → −X over 438–456 and rises with the pentet so only the pentet remains, so the cut to SH_15 doesn't flash.

- **2026-11-26, v14** (agent, user's v13 review: "much much better", "the timing is perfect"): Card 10 words masked; photonic callout re-anchored at the draw start; sparse photons in the waveguides; atomic-layer glow in the wafer sandwich; camera tail compressed by 1 v11 frame so the shot ends closer to the cavity.

- **2026-11-26, v13** (agent, user's review of v12): user's draft timing (462 frames; chip at 150; callouts on "flying" 262 and "stationary" 346); v11's original ending camera restored (v12's dive and chip drop removed); card and title moved into camera space; title above the grid from the start of the merge, sliding up with the rising chip and leaving with a drift-apart fade; grid overlaps the chip ~12 frames before fading. The user liked v12's titles, callouts and Card 10 integration: those designs are unchanged.
- **2026-11-26, v12** (agent, user's brief): Card 10 prelude (+260 frames, all keys shifted), Compound Architecture title, photonic and atomic callouts, atom-glow wave, dive to SH_15 frame 50 with chip drop. Accent checked against the brand guide (ACEScg conversion fixed after the first test).
