# SH_02 — Animator notes

What you need to know to adjust timing in `SH_02_Tweezers_and_logic_grid_v02.blend`.
Everything else animates by itself.

## The one control that matters: when the logic-layer wireframe fires

**`Scene.001` → Scene Properties → Custom Properties → `wire_reveal_frame`** (default **108**)

Set it to the frame where your crossfade from the atomic layer to the logic layer **starts**. The whole
wireframe sequence moves with it. After changing it, re-render `Scene.001` only from that frame to about
60 frames later. Before and after that window the logic scene is unchanged.

What happens relative to `wire_reveal_frame` (R):

| Frames | What you see |
|---|---|
| before R | nothing (as before) |
| R → R+5 | the ghost tweezers (hairlines through each qubit) flash on; the scan spreads outward from the grid |
| R+5 → R+30 | the hairlines fade; a soft light streak (the chamber outline) drifts through the upper frame |
| R+40 → R+60 | everything is forced down to black |
| after R+60 | only the logic layer, plus the original pull-back at the end |

Tip: the hairlines should be visible *during* your crossfade, so the red beams appear to turn into
white lines. If your dissolve is long, set R a few frames before its midpoint.

## Fine-tuning the wireframe (optional)

Each wireframe layer has its own material in `Scene.001` (Shader editor, select the object):

| Material | Layer | Node to adjust |
|---|---|---|
| `wire_ghost_tweezers` | hairlines through the qubits | `LAYER_GAIN` 0.9 (brightness), `LAYER_DECAY_SCALE` 2.2 (how long they linger) |
| `wire_shell_latitudes` | soft light streak | `LAYER_GAIN` 1.1. Set it to 0 if the streak distracts. |
| `wire_ports` / `wire_port_main_bolts` | viewport rings (very faint) | `LAYER_GAIN` 0.2 |
| `wire_objective_lower` | objective lens outline under the grid | `LAYER_GAIN` 1.5 |

Each material also has `WIRE_SPEED` (2.5 units/frame, how fast the scan spreads outward from the grid)
and `WIRE_DECAY` (9 frames, the afterglow length). They're set separately per material, so change all of them
together if you change pacing. Re-running `sh02_logic_wireframe_build.py` resets everything to the
defaults above.

## Do not touch

- **The camera keys** on `Camera` and `Camera.001` must stay identical up to frame 178, or the crossfade
  will break.
- **`Cube.001` and `bg.001`** in `Scene.001`: they look unused (black), but they hide extra arrays and
  set up the end pull-back.
- **The `tweezers` object** is used by both scenes. The atomic scene's beams come from
  `tweezers_atomic` (hidden from render; that's intended).

## Things that animate automatically (no keys)

- Atomic scene: the background atoms (`untrapped_atoms`) drift slowly, using scene time. The haze
  (`trap_cloud_haze`) churns through a driver (`frame * 0.004`). The atoms' shimmer was already there.
- Logic scene: the wireframe, driven only by `wire_reveal_frame` as described above.

## Rendering

Double-click `render_SH_02.bat`. It renders the atomic scene (1–177), then the logic scene (1–250):

- `08_renders/Final_draft/sh_02_tweezers_v02/SH_02_tweezers_####.exr`
- `08_renders/Final_draft/sh_02_logic_v02/SH_02_logic_space_####.exr`

If you stop it, run it again and it continues where it left off (existing frames are skipped). To redo
frames, delete those EXRs first. Frame ranges and output folders are set at the top of the `.bat`
(STEP 2). The earlier renders in `sh_02_tweezers/` and `sh_02_logic/` are left as they were.
