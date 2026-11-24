"""Used by the shot render .bat files (via render_frame_watchdog.ps1).

The .bat starts Blender with --factory-startup so user add-ons don't load in the
background render (they hung SH_1 renders). Factory startup also resets the Cycles
device preference to CPU, so this turns OptiX back on before the frame renders.

It also forces "Overwrite" on: old EXRs (playblasts, earlier renders) may already sit in the output folder,
and with Overwrite off Blender would silently skip those frames.
"""
import bpy

p = bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type = 'OPTIX'
p.get_devices()
for d in p.devices:
    d.use = d.type == 'OPTIX'

scene = bpy.context.scene
scene.cycles.device = 'GPU'
scene.render.use_overwrite = True
scene.render.use_placeholder = False

# Denoise on the GPU. With CPU denoising the post-sampling phase is CPU-bound, and when
# Windows throttles the background render onto E-cores it went from ~9 s to ~50 s,
# pushing frames past the watchdog timeout (SH_1 frames 52-54 on 2026-11-24).
scene.cycles.denoising_use_gpu = True

print("RENDER GPU:", [d.name for d in p.devices if d.use] or "NONE - falling back to CPU")
