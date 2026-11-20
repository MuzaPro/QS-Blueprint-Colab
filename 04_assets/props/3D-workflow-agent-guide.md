# 3D Workflow — Agent Guide

For AI agents helping build geometry-nodes setups and editing `.blend` files in this repo.
This replaces `PROPS_AGENT_GUIDE.md` for 3D work; that guide only covers HTML screen props.

Add to this file whenever you learn something that would have saved you time.

> **⚠️ ALWAYS STATE THE BLEND FILE.** Every summary you give after touching a `.blend` must open with a clear, prominent line naming the full path of each file you worked on and whether you saved it, e.g.
>
> **📁 Blend file: `04_assets/props/ai_models/trays_setup.blend` (saved)**
>
> Put it at the top of the summary, not buried in the text. If you only read a file or rendered from it without saving, say that instead.

---

## 1. How we work together

- **Ask before you build.** For any new setup, ask focused questions first: axes, spacing, what the animation is for, which object is the hero, and where the controls should live. The user answers in one batch, often with reference images. Grouping questions by topic works well.
- **Keep node trees simple.** The user prefers a small, readable tree that works first time over a clever one. Start minimal and offer extras afterwards.
- **Put controls on the modifier panel.** Expose them as group inputs, grouped into panels (e.g. *Stack*, *Effector*), with tooltips (`description`) on anything not obvious.
- **Hero objects stay real objects.** When one unit gets hand-animated (a chip landing on it, a camera focusing on it), keep it as a normal object. The geo-nodes array leaves an empty slot for it (a *Hide Hero Slot* toggle) instead of instancing it.
- **Make models swappable.** The user often swaps in a more detailed model later. Read dimensions from the instanced object's bounding box rather than hard-coding them.
- **Shots are short (often under 4 s at 25 fps).** Pick defaults (falloff widths, distances) so motion reads quickly.
- **Reference, don't copy.** Competitor references (e.g. PsiQuantum renders) show *what* the hardware is. Our models must be recognisable to engineers but clearly our own design: change the palette, layout, part shapes and details. Never reproduce their logos, text, colour scheme or an artist's specific composition.
- **Cyan is reserved for the client.** Never use cyan or teal on competitor hardware.
- **Report honestly.** Say what was verified (logic checks, grey renders) and what wasn't (Cycles look, the shot camera).

## 2. Project conventions

| Item | Value |
|---|---|
| Blender | 5.2 LTS — `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (3.6–5.1 also installed; don't use them) |
| Final render engine | Cycles (some files are saved with EEVEE set; leave the engine alone unless asked) |
| Render device | **GPU, not CPU.** The machine has an NVIDIA RTX 3080: use `OPTIX` (CUDA as fallback). In scripts, set `prefs.compute_device_type='OPTIX'`, call `prefs.get_devices()`, enable the devices, and set `scene.cycles.device='GPU'` for every Cycles render, including previews |
| Frame rate | 25 fps |
| Units | metres, scale 1.0; props are real-world sized (e.g. one tray is about 0.146 × 0.29 × 0.017 m) |
| Visual style | Dark, premium tech look. Ask about colour schemes; don't invent a brand palette |
| Asset location | `04_assets/props/ai_models/` |

Record per-file axis conventions here as you learn them:
- `trays_setup.blend`: trays lie flat in XY and stack up along +Z. The tray's back faces −X. The effector pushes trays along −X.
- `chandelier-holder.blend` (built by `build_chandelier_holder.py`): asset origin = the chandelier (`Quantum_Comp`) origin, so place both at the same point. Floor is at z = −1.55, the chandelier top plate (r 1.51) sits at z = 3.35 under the deck beams, and the front faces −Y (rack on −X, compressor and gas cabinets on +X). The linked `REF_chandelier` collection is only there to check the fit. Link or append the `chandelier-holder` collection, not the REF one.

- `neutral_atom_qc.blend` (built by `build_neutral_atom_qc.py`): SH_1 competitor mockup, so red lasers only and no cyan. Floor at z = 0, front faces −Y, root empty `NAQC_root` at the origin. The main body is 2.9 × 1.5 m (x ±1.45), with the rack on −X and the service cabinet on +X (4.2 m wide overall, 2.45 m tall). The table top is at z = 0.90 and beams run at z = 0.975. The chamber centre is (0.35, 0, 1.15): empty `NAQC_Atoms`, with `NAQC_DiveTarget` just in front of the big front viewport. The interior MOT beams were removed on purpose (they read as a red "X" in the dive). Blank `NA_logo_panel` areas mark where the logo goes: the plinth centre door, the crown fascia, the service-cabinet side and the laser modules.
  - **Don't re-run `build_neutral_atom_qc.py` on it any more.** The user has since added cameras (`Dive-Cam`, `Wide-shot`, timeline marker F_124), lights, the logo and bevel modifiers by hand, and a rebuild would wipe them. Edit the saved file instead. Its materials carry the subtle `clean` level of `na_material_detail.py`. The file is meant to be shared with the Blender community as the "aesthetic" version.
- `neutral_atom_qc_fugly.blend` (built by `build_neutral_atom_qc_fugly.py`, which reads the clean file and never writes to it): this is the SH_1 version, "a lab setup forced into a box". It uses institutional-grey powder coat, clear-anodised extrusions, a yellowed `NA_panel_replaced` panel, dull accent strips and cool fluorescent hood light. It adds blackout cloth, tape, stickers and labels, an open rack door, `NA_Door_R` slid 0.24 m to the left, and cable spaghetti, all as `NAF_*` objects in `NAQC_Fugly`. Materials use the `fugly` level (dust and AO grime). The Dive-Cam path (frames 103–168) was checked clear of the clutter.
- `neutral_atom_qc_cables.blend` (built by `build_neutral_atom_qc_cables.py`): the in-between version, which is the elegant file plus only the cable spaghetti (`NAQC_Cable_Mess` collection, with the rack door open and `NA_Door_R` ajar). The wrapper runs the fugly builder with `PARTS = ("cables",)`. The fugly builder's layers (`palette`, `screws`, `cloth`, `tape`, `cables`) can each be toggled through `PARTS`. Because the random sequence shifts when layers are skipped, cable layouts differ slightly between the variants.
- SH_1 shot file (`05_shots/SH_1/sh_01_04quantum_computers_room-AI-assisted.blend`): the cables version is **appended** (not linked) as collection `NAQC`. `NAQC_root` sits at (4.991, −2.902, −1.242), which is the floor under the centre of the hidden marker cube `Neutral_atoms_Quantum_computer-placement`. It is at real scale and faces −Y. The atoms are at world (5.341, −2.902, −0.092). The logo was parented to `NAQC_root`, so the whole machine moves and scales from the root.
- `na_material_detail.py`: rebuilds the bulk NA_ materials with object-space noise roughness, smudges, sparse rotated-Voronoi scratches, an orange-peel bump and, at the `fugly` level, dust and grime. Base values are cached in `m["na_base"]`, so it's idempotent. `OVERRIDES` recolours materials for one run. Glass gets no bump, because bump makes it look rippled.

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

**Mesh materials: append the slots *before* `bm.to_mesh(me)`.** Calling `me.materials.clear()` after writing the geometry resets every face's `material_index` to 0, so the whole model renders in the first material.

**bmesh bevel scrambles "new verts by index".** Collecting a part's vertices as `bm.verts[n:]` after `bmesh.ops.bevel` picks the wrong set, so transforms hit only part of the mesh and you get shards. Build each primitive in a scratch bmesh, transform it there, then copy its verts and faces into the object's bmesh (see `MB._fin` in `build_neutral_atom_qc.py`).

**Timeline markers bound to cameras override `scene.camera`.** If every preview comes out from the same camera, check `scene.timeline_markers` for `.camera` bindings. Set `mk.camera = None` in the preview script only (never save it).

**Add-on noise when opening user files.** Opening a `.blend` without `--factory-startup` loads the user's add-ons (Bagapie, population, AI-Render, rbc), which print tracebacks that look like failures. Prefer `--factory-startup` and call `bpy.ops.wm.open_mainfile()` inside the script, or filter for your own markers.

**No system Python on this machine.** `python` opens the Microsoft Store stub. Edit script files with the Edit tool or `sed`, and run Python only through Blender.

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
3. **Look-dev check.** For materials, use a Cycles preview: about 48 samples, denoise, GPU, a near-black world, and temporary area lights (key about 7 W, rim about 4 W warm, fill about 1 W at prop scale). Brighter lights wash blacks to grey and desaturate emissive parts. Run the build script with `SAVE = False` inside the preview script (`exec(open(build).read())`), so you can iterate without touching the file and save only once the look is approved.
4. Look for things that seem like bugs but aren't. For example, the tray model is two halves, so a stack can look like two columns from some angles.

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

### Swapping a placeholder for a detailed model (`build_tray_connector_v3.py`)
- v3 is the current tray: a satin-nickel cold plate and back rail, gold-plated chip carrier and thermal-link pads, a navy soldermask board, grey connectors with gold contact rows, a violet silicon die, and yellow single-mode fibres with clips. It has no LEDs (a cryo board wouldn't), plus surface-mount parts, traces, vias, a datamatrix, and tapped holes and seams on the outer faces for the stacked look. It's about 23k verts.
- Re-running the script rebuilds the meshes in place (`TrayConnector_v3*`, `PhotonicChip_v3`), deletes older generated meshes and unused `TC_` materials, and keeps the original placeholders in `spare_parts`.
- Helpers worth reusing: `side_xf(face, a, b)` places parts on the outer faces (back, front, sides); `strip()` draws PCB traces; `tube()` with `smooth_path()` (Catmull-Rom) makes cables, fibres and leads; `socket_screw()`, `round_rect()`, `chamfer_rect()`.
- Check medium close-ups from several angles (hero, mid, chip, back of stack). The back view matters because the box shot shows the trays from behind.
- Model procedurally with bmesh helpers (extruded outline `prism`, `box`, rounded box, cylinder, swept `ribbon`), each part beveled and given a material index. Keep the model inside the placeholder's bounding box so stack spacing doesn't change.
- Swap by assigning `ob.data = new_mesh`. This keeps the object's name, animation, parenting and any geo-nodes references.
- Move the old mesh onto a hidden `<name>_placeholder` object in `spare_parts`, so nothing is lost.
- The `Tray-connector-with_chip` instance source is the tray plus the chip joined into one mesh. The hero tray and `photonic_chip` (its child) stay separate so the chip can be animated landing on it.
- Prefix materials with `TC_`. Avoid real company logos and text: use generic white silkscreen blocks instead.

---

## 7. Open questions / to learn
- How the user prefers camera rigs (the files contain a `Dolly_Rig` armature with `WGT-*` widgets).
- Material and lighting conventions for Cycles finals.
