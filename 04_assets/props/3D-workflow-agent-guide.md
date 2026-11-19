# 3D Workflow — Agent Guide

For AI agents helping build geometry-nodes setups and editing `.blend` files in this repo.
This replaces `PROPS_AGENT_GUIDE.md` for 3D work; that guide only covers HTML screen props.

Add to this file whenever you learn something that would have saved you time.

---

## 1. How we work together

- **Ask before you build.** For any new setup, ask focused questions first: axes, spacing, what the animation is for, which object is the hero, and where the controls should live. The user answers in one batch, often with reference images. Grouping questions by topic works well.
- **Keep node trees simple.** The user prefers a small, readable tree that works first time over a clever one. Start minimal and offer extras afterwards.
- **Put controls on the modifier panel.** Expose them as group inputs, grouped into panels (e.g. *Stack*, *Effector*), with tooltips (`description`) on anything not obvious.
- **Hero objects stay real objects.** When one unit gets hand-animated (a chip landing on it, a camera focusing on it), keep it as a normal object. The geo-nodes array leaves an empty slot for it (a *Hide Hero Slot* toggle) instead of instancing it.
- **Make models swappable.** The user often swaps in a more detailed model later. Read dimensions from the instanced object's bounding box rather than hard-coding them.
- **Shots are short (often under 4 s at 25 fps).** Pick defaults (falloff widths, distances) so motion reads quickly.
- **Report honestly.** Say what was verified (logic checks, grey renders) and what wasn't (Cycles look, the shot camera).

## 2. Project conventions

| Item | Value |
|---|---|
| Blender | 5.2 LTS — `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (3.6–5.1 also installed; don't use them) |
| Final render engine | Cycles (some files are saved with EEVEE set; leave the engine alone unless asked) |
| Frame rate | 25 fps |
| Units | metres, scale 1.0; props are real-world sized (e.g. one tray is about 0.146 × 0.29 × 0.017 m) |
| Visual style | Dark, premium tech look. Ask about colour schemes; don't invent a brand palette |
| Asset location | `04_assets/props/ai_models/` |

Record per-file axis conventions here as you learn them:
- `trays_setup.blend`: trays lie flat in XY and stack up along +Z. The tray's back faces −X. The effector pushes trays along −X.

## 3. Driving Blender headlessly

There is no live Blender connection. Work by running Python scripts in background mode:

```bash
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b "<file>.blend" --python script.py 2>&1 | grep -iE "error|traceback|line [0-9]|<your marker>"
```

- Blender prints a lot of add-on noise (blendkit etc.), so always filter the output. Print your own marker (e.g. `BUILT OK`) at the end of the script.
- Keep scripts in the session scratchpad, not in the repo, unless the user wants them kept.
- To test an API quickly without touching a file, add `--factory-startup` and leave out the `.blend`.

### Safety
- **Back up before saving:** `cp file.blend <scratchpad>/file_backup.blend`. Saving also rotates `.blend1`, which overwrites the user's previous backup.
- **The user may have the file open in the Blender UI.** After you save, tell them to use **File → Revert** before saving. Otherwise their open copy will overwrite your changes.
- Use `bpy.ops.wm.save_mainfile()` only in the build script. Verification scripts must never save, so throwaway cameras and render settings stay out of the file.
- Make build scripts idempotent: reuse objects and node groups if they exist (`D.objects.get(...) or ...new(...)`), and clear the group (`ng.nodes.clear(); ng.interface.clear()`) before rebuilding.

### Start by inspecting the file
Dump every object's name, type, parent, transform, world bounding box, collections and modifiers, plus the scene's engine, frame range and fps, and the existing node groups. This answers most questions (sizes, origins, hierarchy) before you build anything. Names are case- and hyphen-sensitive (e.g. `Tray-connector-with_chip`).

## 4. Blender 5.2 API gotchas (learned the hard way)

**Setting geometry-nodes modifier inputs.** `mod["Socket_1"] = value` **no longer works** in 5.2; it raises *id properties not supported*. Use:
```python
sid = next(i.identifier for i in ng.interface.items_tree
           if i.item_type == 'SOCKET' and i.in_out == 'INPUT' and i.name == "Tray")
getattr(mod.properties.inputs, sid).value = some_object
```

**Compare node.** After setting `data_type='INT'`, only two inputs are listed, named `"A"` and `"B"`. Index-based access like `inputs[2]` fails. Always refer to sockets by name.

**Interface panels.** Create with `ng.interface.new_panel("Name")`, then `ng.interface.move_to_parent(socket, panel, index)`.

**Object Info `transform_space`:**
- Use `ORIGINAL` for the object being instanced, so its scene position doesn't matter.
- Use `RELATIVE` for effector or controller objects, so their location is in the modifier object's space.

**Probe before guessing.** When a socket name or attribute is uncertain, run a 5-line `--factory-startup` script that prints `[(s.name, s.identifier) for s in node.inputs]` or `dir(obj)`. This is much cheaper than a failed build.

## 5. Verifying your work

1. **Logic check without rendering.** Evaluate the depsgraph and read instance transforms:
   ```python
   dg = bpy.context.evaluated_depsgraph_get()
   pts = [i.matrix_world.translation for i in dg.object_instances
          if i.is_instance and i.parent and i.parent.original == stack_obj]
   ```
   Test several controller positions (before, during and after the effect) and print counts and offsets.
2. **Quick visual check.** Use a Workbench render (`BLENDER_WORKBENCH`, studio light, `file_format='PNG'`, view transform `Standard`) from a temporary camera, saved to the scratchpad, then view the PNG. Without `file_format='PNG'` it writes EXR, which can't be viewed directly. Renders take about 3 s.
3. Look for things that seem like bugs but aren't. For example, the tray model is two halves, so a stack can look like two columns from some angles.

## 6. Pattern library

### Instance stack with hero slot and linear effector (`trays_setup.blend` → node group `TrayStack`)
- **Mesh Line** in Offset mode:
  - Count = *Count*.
  - Offset Z = pitch, where pitch = bounding-box Z size + *Gap*.
  - Start Z = −*Hero Slot* × pitch, so the hero slot lands at the object's origin and changing Count only adds or removes trays at the top.
- **Delete Geometry** on the point where `index == Hero Slot` AND *Hide Hero Slot* is on.
- **Set Position** offset X = −*Distance* × MapRange(**smootherstep**, clamped)(point.z, effZ → effZ + *Falloff*, 0 → 1). A *Flip* toggle swaps To Min and To Max.
- **Instance on Points** with Object Info (*As Instance*, `ORIGINAL`).
- Animate the effector's Z to sweep the effect through the stack.
- Hide the source object in the viewport and in renders.

---

## 7. Open questions / to learn
- How the user prefers camera rigs (the files contain a `Dolly_Rig` armature with `WGT-*` widgets).
- Material and lighting conventions for Cycles finals.
