# SH_15: notes for humans

Last updated: 2026-11-25. Current file: `sh_15_positioning_and_first_cluster_tile_22.blend`.

## The photonic mode's resonance

The lobes of the photonic mode stay where they are, while a soft bright region travels up and down between the mirror and the fibre. It implies a single photon bouncing between the two. It is meant to stay subtle.

Only the hero cell has it, between frames **276 and 578**. The other cells are unaffected.

### Where the controls are

1. Select **`PhotonMode.004`** (search for it in the Outliner).
2. Open **Object Properties** (orange square) → **Custom Properties**.

| Control | Now | What it does |
|---|---|---|
| `res_round_trip` | **45** | **Speed.** Frames for one trip up and back down (45 = 1.8 s). Lower is faster |
| `res_depth` | **0.68**, then **0.34** from 431 | **Strength.** How much the lobes dim and brighten |
| `res_width` | **0.30** | **Size** of the bright region. 1 = the whole height of the cavity |
| `resonance` | 0 → 1 over 276–300, 1 → 0 over 560–578 | **Fade in and out.** 0 = the still mode, without the effect |

`resonance` and `res_depth` have keyframes. Typing a new value isn't enough, because it resets when the frame changes: go to the key's frame, type the value, then hover over it and press **I**. The other two have no keys, so just type.

### Changing the speed

The first close-up shows the effect from 276 to 430. The fade-in uses the first second of that.

| `res_round_trip` | One trip | Trips in the first close-up |
|---|---|---|
| 56 (first version) | 2.2 s | 2.8 |
| **45 (now, about 25 % faster)** | **1.8 s** | **3.4** |
| 37 | 1.5 s | 4.2 |
| 30 | 1.2 s | 5.1 |

Don't keyframe `res_round_trip`: the motion would jump. Use one value for the whole shot.

### Changing the strength

- **First close-up (key at 276):** 0.35 is invisible, 0.6 barely visible, 0.8 plainly visible. At 0.95 the centre dims, which is wrong: the intensity should be highest there.
- **After the cut (key at 431):** kept lower on purpose. From that camera, 0.68 turns the mode into a funnel just as the card shows the probability peaking in the centre.

Only the outer parts of the lobes can show the change. The core is far brighter than white on screen, so it always looks the same.

### Other changes

- **Fade it in sooner or later:** move the `resonance` keys (276 and 300, or 560 and 578). Keep the end before 579, so the part with several cells stays still.
- **Turn it off:** delete the `resonance` keys and set the value to 0.
- **See how it works:** the material `Photon_Volume_hero_resonance` (Shader Editor), in the frame labelled "v21 resonance". The trip always starts at frame 276.

### After a change

- Re-render **277–577**; no other frame changes.
- Judge it at full frame rate. It's slow and soft, so a single still won't show it.
- Don't re-run `sh15_v21_resonance_build.py`: it overwrites v21 and doesn't know about later edits.

## The atom

A dot (nucleus), a ball of points (the S-orbital cloud) and a circle (the edge of the ball). Select **`Icosphere.001`** → **Object Properties** → **Custom Properties**. None of these has keyframes, so just type.

| Control | Now | What it does |
|---|---|---|
| `atom_radius` | 0.0325 | Size of the whole atom. Above 0.034 it touches the tweezers' dashed lines. Keep it below 0.07 |
| `atom_nucleus` | 0.27 | Size of the dot, relative to the circle |
| `atom_ring` / `atom_ring_width` | 0.8 / 0.036 | How strong and how thick the circle is |
| `atom_rim` | 0.25 | Soft glow just inside the circle |
| `atom_cloud` / `atom_cloud_size` | 2.6 / 0.28 | How bright the cloud is and how far it spreads |
| `atom_grain` / `atom_grain_scale` | 0.94 / 8 | 0 = fog, 1 = points / how many points |
| `atom_twinkle` | 0.6 | How fast the points change. 0 = still |

- **Closer to the card's icon:** lower `atom_cloud`, raise `atom_ring` to 1 and `atom_nucleus` to 0.29.
- **More like a cloud:** lower `atom_ring`, raise `atom_cloud_size`.
- After a change, re-render **124–597**.

The technical details are in [AGENTS.md](AGENTS.md).
