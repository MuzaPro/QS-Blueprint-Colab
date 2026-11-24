# SH_1: notes for agents

Last updated: 2026-11-24. Read this before touching the SH_1 .blend, the render script or its helpers.

## The shot

- **What it shows:** the opening room of the film, a quantum-computing R&D hall. The camera dollies forward through the hall and ends up diving towards the neutral-atom computer's vacuum chamber.
- **Content rule:** SH_1 shows **competitor tech only**. The models are generic mockups of competing approaches (neutral atoms, superconducting, linear photonics). Use red lasers, **no cyan or teal anywhere**, and no photonic-chip features. Pasqal is a direct competitor, so use it only as a reference: the layout, enclosure colour and chamber shape must differ. Leave blank panels where the "Generic Quantum" ψ logo goes. Cyan is reserved for the client's tech, which appears in later shots.
- **Current file:** `sh_01_04quantum_computers_room-AI-assisted.blend`. The `.blend1` next to it is the Nov 22 version. `sh_01_05..._BACKUP.blend` is a backup from Nov 21. `sh_01_02/03` and the older files are earlier iterations; don't render them.
- **Linked libraries:** `04_assets/props/Generic Superconducting Quantum Computer.blend`, `RSG_MONSTER.blend` and `ai_models/chandelier-holder.blend`. Blender reports 3 libraries / 3 linked data-blocks missing. These are the compositing/geometry "essentials" node assets linked from Blender install paths, one of them from the old Blender **5.0** folder. It's harmless for rendering, but relink or localise them if they cause trouble.
- **Animation:** `Camera` is keyed from frame 4 to 203. It moves smoothly from (-6.1, -39.9, 0.9) to (5.3, -3.0, -0.1) with no cuts and a 50 mm lens. `NA_Door_R` slides open over frames 4–172. `QC_C_Original_Cube.001/.004` are animated over frames 65–118. `focus_point`/`tracking_point` are keyed near the end (frames 174–189). Nothing changes abruptly around frames 50–55.

## Render setup (as of Nov 24)

| Setting | Value | Note |
|---|---|---|
| Engine | Cycles, GPU (OptiX, RTX 3080 10 GB) | `render_gpu_setup.py` forces OptiX, because `--factory-startup` resets the device to CPU |
| Resolution | 1920×1080 at **150 %** = 2880×1620 | was 100 % on Nov 22 |
| Samples | **256** adaptive (threshold 0.01) | was 128 on Nov 22 |
| Time limit | **180 s** per frame | was 0 (off) on Nov 22 |
| Denoiser | OpenImageDenoise. The .blend says `denoising_use_gpu = False` (CPU) | CPU denoising was the root of the failure below. `render_gpu_setup.py` now forces it onto the GPU |
| Tiling | auto tile, 2048 px, so a frame is **2 tiles** | tiles are written to `%TEMP%\blender_*` and read back from disk |
| Frames | 1–200 at 25 fps | |
| Output | `08_renders/Final_draft/sh_01_QS_lab_polished/sh_01_QC_lab_polished####.exr` | OpenEXR, combined + cryptomatte |

Typical frame on an idle machine: about 7 s scene sync, about 38 s GPU sampling (2 tiles), **8–25 s CPU denoise**, under 1 s for compositing and saving. That comes to **50–75 s wall time** per frame. The Nov 22 settings rendered at about 22 s per frame.

## Render pipeline

- `Sh01_render_script.bat` is the frame loop. It handles resume (via `..._done_frames.txt`), cooldowns every `BATCH_SIZE` frames, and stops after `MAX_FAILS_IN_ROW` consecutive failures. It logs to `..._render_log.txt`.
- `render_frame_watchdog.ps1` renders a single frame: it starts `blender -b --factory-startup <blend> --python render_gpu_setup.py -f N`, kills Blender if it runs past `-TimeoutSec`, and retries. It exits with 3 on a timeout and 4 if no new EXR was written. **Blender's own console output is not written to the log.**
- `render_gpu_setup.py` switches the render to OptiX GPU and forces overwrite on, with placeholders off.
- `Sh1_render_script.bat` (no zero) is the older script. Use `Sh01_render_script.bat`.

## Problem: run stopped on Nov 24 at frames 52, 53, 54

### What the log shows
- Frames 1–51 rendered fine at a steady **53–54 s**.
- Frames 52, 53 and 54 each failed 3 times with "hung for over 100 s" (code 3). Three failures in a row tripped the stop at 10:38.
- The same thing happened once earlier that day: frame 2 timed out at 09:08 (while `BATCH_SIZE` was 5).

### Cause: the frames weren't hanging, they were too slow for a 100 s watchdog
1. **Sampling finished every time.** Each killed attempt left a ~185 MB `cycles-tile-buffer-*.exr` in `%TEMP%\blender_a*`. Tile 1 was written about 40 s after the attempt started and tile 2 about 52 s after. That matches a healthy run, so all GPU sampling was done. The process then sat in the CPU phase (reading the buffer back, **CPU OIDN denoise**, compositing) for another ~48 s until the watchdog killed it at 100 s.
2. **The trigger was user activity on the PC.** New Chrome tabs were opened at **10:19:03**, two seconds after frame 52 started (10:19:01). Every attempt after that failed. The machine has a hybrid **i7-12700KF** (8 P-cores and 4 E-cores). When another app is in the foreground, Windows 11 throttles background processes and moves them onto E-cores. The GPU part doesn't care, but CPU denoising at 2880×1620 does.
3. **Reproduced.** Frame 52 was rendered standalone into the scratchpad, not the real output:
   - Idle machine: **55 s** total, 8.5 s of it denoising, exit 0.
   - Same frame **pinned to the 4 E-cores** (affinity `0xF0000`): **106 s** total, **50.4 s** denoising. Sync time doubled from 7 to 14 s. That exceeds the 100 s timeout, and the tile timing (tile 1 at 42 s, tile 2 at 53 s) matches the failed attempts.
4. There's **no thin safety margin built in on purpose.** A normal frame takes 55–75 s against a 100 s timeout, and `cycles.time_limit = 180` means a frame is *allowed* to sample for up to 180 s. Any slowdown in the CPU phase, or a slower shot section, kills good frames.
5. Ruled out:
   - GPU driver resets (no TDR or `nvlddmkm` events in the System log 09:00–10:45)
   - Out of VRAM (peak about 1.6 GB of 10 GB)
   - Out of RAM (64 GB, mostly free)
   - Something in the scene at frame 52 (the camera moves smoothly, and frame 52 renders fine when idle)

### Related findings
- Earlier sessions also saw genuine hangs past 300 s on single frames (Nov 20: frames 72, 113, 132 and 137). A retry fixed each one. The watchdog comment describes this as "one core at 100 %, GPU idle while loading or finishing". That's a separate, intermittent Blender issue. The watchdog is still worth keeping, just with a realistic timeout.
- **Disk C: is 99 % full (about 19 GB free).** Every killed attempt leaves a ~185 MB tile buffer in `%TEMP%\blender_a*` that nobody cleans up: 10 of them (~1.85 GB) are from Nov 24 alone. Dozens of other empty `blender_a*` folders exist too.
- The `.blend` has 136 objects in its data but only 93 in the scene (orphans), plus packed images from foreign paths (`E:\3D\...`, `C:\Users\BAHA-LAPTOP\...`). That's harmless, but it bloats the file.

## Fixes applied (2026-11-24)

1. **Denoising runs on the GPU.** `render_gpu_setup.py` now sets `scene.cycles.denoising_use_gpu = True`. The .blend itself still says CPU, so the override only applies to renders started through the script. The denoiser is still OIDN; only the device changed.
2. **`FRAME_TIMEOUT_SEC` is now 240** in `Sh01_render_script.bat`. It has to stay above `cycles.time_limit` (180) plus sync and denoise time. If you lower the timeout, lower `time_limit` too.
3. **Blender runs at full speed in the background.** `render_frame_watchdog.ps1` (`Set-FullSpeed`) starts Blender at `High` priority and turns off Windows power throttling for it (`SetProcessInformation` with `ProcessPowerThrottling`, `EXECUTION_SPEED` off). That keeps Windows from parking it on E-cores while you use the PC.
4. **Tile buffers are cleaned up after a kill.** After killing Blender, the watchdog (`Remove-TileBuffers`) deletes `cycles-tile-buffer-*.exr` files in `%TEMP%\blender_*` folders created during that attempt, then removes the folder if it's empty. Older folders are left alone.
5. Not done: Blender's stdout still isn't written to the render log.

The other shots (e.g. `SH_9`) have **their own copies** of the watchdog and setup scripts, and those were **not** changed.

## Resuming the render
- Frames 1–51 are listed in `sh_01_04quantum_computers_room-AI-assisted_done_frames.txt`. Frames 52–200 still hold old playblast EXRs.
- Double-click `Sh01_render_script.bat`. It resumes from frame 52. Don't delete the done-frames file unless you want to re-render everything.
- Frames 1–51 were denoised on the CPU and frames 52 onward on the GPU. OIDN gives essentially the same result on both, but check for a visible seam at frames 51/52.
