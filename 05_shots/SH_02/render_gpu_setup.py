"""Used by render_SH_02.bat.

The .bat starts Blender with --factory-startup so user add-ons (AI-Render, rbc_addon_free,
Bagapie, ...) don't load in the background render (they throw errors on load / every frame).
Factory startup also resets the Cycles device preference to CPU, so this turns
OptiX (RTX 3080) back on before the frame renders.
"""
import bpy

p = bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type = 'OPTIX'
p.get_devices()
for d in p.devices:
    d.use = d.type == 'OPTIX'
bpy.context.scene.cycles.device = 'GPU'
print("RENDER GPU:", [d.name for d in p.devices if d.use] or "NONE - falling back to CPU",
      "| scene:", bpy.context.scene.name)
