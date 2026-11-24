"""Used by Sh09_v05_render_script.bat (via render_frame_watchdog.ps1).

The .bat starts Blender with --factory-startup so user add-ons don't load in the
background render (they hung SH_1 renders). Factory startup also resets the Cycles
device preference to CPU, so this turns OptiX back on before the frame renders.

It also forces "Overwrite" on: the playblast EXRs already sit in the output folder,
and with Overwrite off Blender would silently skip every frame.
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

print("RENDER GPU:", [d.name for d in p.devices if d.use] or "NONE - falling back to CPU")
