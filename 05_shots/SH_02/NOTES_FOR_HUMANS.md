# SH_02: notes for humans

Last updated: 2026-11-25. Current file: `SH_02_Tweezers_to_logic_v03.blend`, scene **Scene**, frames 1–250. (`SH_02_ANIMATOR_NOTES.md` describes v02.)

## Timing

Select **`SH02_CTRL`** (Outliner) → **Object Properties** → **Custom Properties**. Hover over a value for an explanation.

| Control | Keys now | What it does |
|---|---|---|
| `err_1` … `err_9` | 70, 80, 93, 108, 117, 126, 133, 139, 145 | Frame at which each error starts. No keyframes: just type |
| `quantum` | 82 → 114 | Clouds and drifting atoms fade: physics to diagram |
| `haze` | 0.3 until 82, 0 at 112 | Glow of the residual atom cloud (1 = as in v02; it washes out the contrast) |
| `beam_len` | 14.5 → 5 over 14–40 | Length of the tweezers. Long at the start to continue SH_1 |
| `beams` | 2 at 4, 1 at 18, then 54 → 70 → 104 | Tweezers fade out |
| `beam_far`, `atom_far` | up to 84 | How faint the far rows are while the camera is low |
| `dark` | 66 → 104 | The chamber goes black |
| `links` | 98 → 128 | Links grow |
| `boundary` | 148 → 164 | Line around the logical qubit |
| `err_fixed` | 163 → 174 | Errors go back to white |
| `patches` | 166 → 208 | Other patches appear |
| `collapse` | 194 → 234 | Patch → circle → dot |
| `grid` | 226 → 242 | Links between the dots |

To keep the errors red to the end, delete the `err_fixed` keys and set it to 0.

## Camera

`CamRig`: rotation Z turns around the atoms; `zoom` is the distance; `pan_x` and `pan_y` place the patch in the frame. `CamPitch`: rotation X, where 0 is straight down.

**Don't move the last keys of `zoom`, `pan_x` and `pan_y`:** the last frame lines up with the chasm card to the pixel.
