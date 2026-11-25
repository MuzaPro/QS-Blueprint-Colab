# QS Blueprint film: guide for agents

Last updated: 2026-11-25. Start here, then read the `AGENTS.md` (or context file) in the folder of the shot you're working on.

- **This file** holds the story, the science and what each shot is for.
- **Shot files** hold the technical detail: objects, node groups, bakes, render scripts, change log.

**How to read it:** plain statements come from the user, the script or the project's own sources. *(inferred)* marks an agent's reading that the user hasn't confirmed. Don't build on an inferred point without asking.

## What we're making

A short 3D explainer film (Blender, 25 fps) for **Quantum Source**, presenting its **compound photon–atom quantum computing architecture**. The scientific basis is the company's paper, *Blueprint for a compound photon–atom fault-tolerant quantum architecture*.

The film argues one thing: **to scale, a quantum computer needs huge numbers of qubits and unrestricted connectivity. Matter alone and light alone each fall short, and combining them gets there.**

## The story

The narration is in [02_script/Approved_script.md](02_script/Approved_script.md). **It's a bit outdated but has most of the right beats (user, Nov 25).** Use it for the argument, not for exact wording or timing. If it disagrees with the user or a shot's own notes, they win.

| Beat | What it says | What the visuals need to make the viewer feel |
|---|---|---|
| 1. The chasm | Today's machines make too many errors. Bundling hundreds of physical qubits into one logical qubit pushes the need from thousands to about a million. Crossing that gap takes connectivity as well as numbers | The scale of the gap |
| 2. Neither platform gets there alone | Matter qubits have limited connectivity, or pay a speed penalty for moving qubits around. Photons connect at light speed, but entangling them with linear optics succeeds at most 50 % of the time, so the hardware overhead explodes | Two good ideas, each hitting a wall |
| 3. The turn | Why choose? The compound architecture joins **flying photonic qubits** (connectivity) with **stationary atomic qubits** (stability) | Relief, a new idea |
| 4. The unit cell | A high-cooperativity optical cavity holds one trapped atom. Light is squeezed into a tiny volume where the atom sits, so the photon almost certainly interacts with it: a **near-deterministic entangling gate** | Precision, intimacy, one photon meeting one atom |
| 5. The architecture | Thousands of unit cells. Photons are generated, routed between cells, entangled with atoms and measured. A classical system coordinates everything and corrects errors in real time: reliable computing from imperfect hardware | A well-oiled machine |

The right-hand column is *(inferred)*, except "well-oiled machine", which is the user's phrase for SH_18. The script's outline also ends on a small form factor: server-room size rather than a large facility.

## The science behind the visuals

Enough to judge whether an image is truthful. Sources, most authoritative first:

1. **The user**, who relays the client's notes.
2. **The Blueprint paper** in `11_reference/research_papers/` (Fig. 4 is the architecture; sections II–III cover the unit cell and hardware).
3. [QS_Complete_Reading_Guide.md](11_reference/research_papers/QS_Complete_Reading_Guide.md), a plain-language companion. Part VIII is an animation-accuracy checklist: read it before designing anything that depicts physics.

| Idea | What it is | What it means on screen |
|---|---|---|
| Photon = flying qubit | Carries information and connectivity. Dual-rail: one photon in one of two paths | One at a time, never a continuous beam. Fragile: its main failure is simply being lost |
| Atom = stationary qubit | A single rubidium-87 atom held in the cavity. Reset and reused | Stays put. Recycled, not consumed |
| Unit cell | Atom plus cavity. Generates photons, entangles them and prepares/measures the atom, at different moments | One kind of node doing several jobs |
| Entangling gate | A photon–atom CZ gate. The photon goes in, meets the atom and comes back out (single-sided cavity) | The photon **enters the cavity in the shape of the photonic mode** (user). SH_15 shows exactly this. Photons aren't entangled by meeting each other at a beam splitter; that's the competitors' route |
| Entanglement | Correlation, not a signal | No energy or light pulses travelling along a link |
| Photon cycle | Generate → a chain of CZ gates (four for a bulk photon) → measure. Repeated endlessly | The core motif of the film's second half *(inferred)* |
| Cluster state | A large web of entangled qubits, built continuously and measured away layer by layer to compute | Dots and lines that appear, then become 0s and 1s |
| Router | Reconfigurable switches linking cells, delay lines and detectors; they change between photon cycles | Many possible paths, few in use at any moment |
| Delay lines | Long fibre spools that hold a photon so it can be entangled later | Photons taking a detour, then coming back |
| Detectors | Superconducting nanowires (SNSPDs). Absorbing a photon destroys it and gives a click | A sudden flash and a quick recovery. These stay cryogenic, so don't imply there's no cold hardware at all |
| Classical control | Routing, timing and real-time error decoding from the stream of clicks | Bits flowing from detectors to processor |
| Error correction | Many imperfect qubits encode one reliable one; errors are found and fixed as they happen | Errors are visible but handled, not a disaster |

The paper draws photons cyan and atoms dark blue in its lattice figures.

## Film-wide visual rules

- **Cyan/teal belongs to the client's photonic technology.** Never use it on competitor hardware.
- **Competitor hardware is generic.** Show what kind of machine it is without copying anyone's design, logo or palette. Red lasers belong there.
- **Aesthetic:** dark, restrained, precise, elegant. "Simple but complex" data-vis graphic design rather than sci-fi spectacle.
- **Motivated by the physics.** If a simplification is needed for readability, make it deliberately and record it in the shot's notes.
- **Readability comes first.** If viewers can't follow individual photons, the idea is lost, however accurate the system is.
- **Brand:** `04_assets/brand/` (quick brand guide, colour palette, Jura for the logo, Overpass for text).

## Working here

| Where | What |
|---|---|
| `02_script/` | Approved script |
| `04_assets/` | Brand, props, environments, textures, reusable node setups (`tools/`), paper figures (`figures/`) |
| `05_shots/SH_*/` | One folder per shot: .blend versions, scripts, notes, often a local `Render/` |
| `06_audio/` | Narration and pacing tracks |
| `08_renders/` | Final drafts, stills, previews, `rendering_guide/` |
| `11_reference/` | Research papers, CTO references, competitor references |

- **Blender 5.2** (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`), Cycles on GPU (OptiX, RTX 3080). Some older guides still mention 5.0.
- **3D and geometry-nodes work:** read [3D-workflow-agent-guide.md](04_assets/props/3D-workflow-agent-guide.md). HTML screen props: [PROPS_AGENT_GUIDE.md](04_assets/props/PROPS_AGENT_GUIDE.md).
- **Render scripts:** [BAT_RENDERING_GUIDE.md](08_renders/rendering_guide/BAT_RENDERING_GUIDE.md) plus the shot's notes, which override it.
- **The user edits .blend files by hand between sessions.** Inspect the current file before relying on notes, and never overwrite hand edits by re-running an old build script.
- **Respect the user's render choices.** Samples, time limits and output folders are often deliberate. Ask before changing them, and check whether a render is running before touching its .blend or .bat.
- **Git:** .blend and video files go through LFS; EXRs and .blend1 are ignored. Commit only when asked.
- **Keep notes current.** After changing a shot, update its notes, including any science the user explained. Update this file when a shot's purpose or the film's story changes.

## Shot by shot

**Rule:** only describe a shot here once the user has discussed it in detail. Don't fill gaps from file names or from this index. The order below is by number; folder numbers don't necessarily match the script's beat numbers.

| Shot | Described below | Notes in the shot folder |
|---|---|---|
| SH_1 | Not yet | [AGENTS.md](05_shots/SH_1/AGENTS.md) |
| SH_02 | Not yet | [SH_02_CONTEXT_FOR_AGENTS.md](05_shots/SH_02/SH_02_CONTEXT_FOR_AGENTS.md), [SH_02_ANIMATOR_NOTES.md](05_shots/SH_02/SH_02_ANIMATOR_NOTES.md) |
| SH_4, SH_7, SH_8, SH_9, SH_11, SH_12, SH_17 | Not yet | None |
| SH_15 | Not yet. Known so far (user, Nov 25): it shows the photon entering the cavity in the shape of the photonic mode, and it shows the dual rail. It shows a vertical Fabry–Pérot cavity: the top is the edge of an optical fibre; the bottom, in reality another fibre edge, is a reflective round mirror for clarity. Horizontal laser tweezers (horizontal so viewers don't confuse them with the vertical photonic mode) hold the atom floating in space, then fade out by frame 185 in a way that implies they are still there but omitted to simplify the visuals | [AGENTS.md](05_shots/SH_15/AGENTS.md) |
| **SH_18** | **Yes** | [AGENTS.md](05_shots/SH_18/AGENTS.md) |
| SH_20 | Not yet | None |

### SH_18: the architecture

**File:** `05_shots/SH_18/sh_18_architecture_intro_14.blend`. **Frames:** 2744–3278 (535 frames, 21.4 s). **Script:** beat 5 *(inferred from content)*. Creative work is finished; final rendering was under way on Nov 25. The user calls it one of the most important shots in the film.

#### What it's for

It's where the film moves from one unit cell to the whole computer, and shows that the pieces form a working system. The viewer should come away with two things:

1. **It flows in one direction, left to right:** make photons → entangle them → detect them → compute.
2. **It's a well-oiled machine:** single photons take turns visiting the entangling cells, and each cell switches on as a photon passes.

#### What we see

A dark, gridded blueprint floor with a white line drawing of the architecture. Physical components sit on top of the drawing, and labels name each station.

| Station (on-screen label) | On screen | Science |
|---|---|---|
| **01 Single-photon generators** | A wafer with 3 glass cells; one waveguide starts in each | Unit cells making single photons |
| **02 Entangling unit cells** | A wafer with 12 glass cavities, 4 per row in 3 rows. Each has a glowing diagram circle under it | Photon meets atom; the atoms create the entanglement gates |
| **03 Single-photon detectors** | 4 nanowire meanders (3 of them receive photons) | SNSPDs. Absorbing a photon makes a click |
| **04 Classical processor** | A chip marked QS, with readout bits running into it from the detectors | Control, readout and error decoding |
| **Router** | A long wafer bar below the stations, drawn as a dense mesh of switches | Steers photons between sections. It's printed into the silicon wafer, like the waveguides and some of the unit cells |
| **Delay lines** | Three nested loops, each with a row of fibre-spool circles, below the router | Kilometres of fibre, off the wafer |
| **Logic card** | A translucent panel above the hardware with an animated diagram, also running left to right | The computation that runs on this hardware |

**How to read the logic card** (confirmed by the user): photons stream in on the left, become a grid of linked dots (the cluster state), cross a **vertical line that represents the "reading" by the single-photon detectors**, and turn into columns of 0s and 1s (measurement results) with a few in red (detected errors). It's the same journey as the hardware below, in the language of information.

#### How it unfolds

| Frames | Camera | What happens |
|---|---|---|
| 2744–2805 | Low three-quarter view across the floor, moving | The generator wafer (settles at 2777) and the entangling wafer (2804) fly in and land on their outlines. First photons leave at 2777 |
| 2806–2858 | Same move, closing in on the entangling cells | The logic card is revealed by a soft wipe, left to right with the bottom leading. Cells start to light up teal as photons pass |
| 2859–2978 | Same camera, pulling back | The whole layout comes into view. Photons reach the first detector around 2892, and the detectors flash |
| 2979–3069 | Cut: close on the processor | Detectors, readout bits and processor, with the card's columns of 0s and 1s above. Photons in, classical data out |
| 3070–3278 | Cut: wide, rising to a frontal view | The full architecture as a clean diagram, card on top, everything running. The card tilts to face the camera (3069–3138); **keep that tilt** |

#### Why it looks this way

- **Few, irregular photons.** The original even stream was dull and unreadable. Spacing is now random, with single photons taking turns, which also suits the randomness of single-photon events. The shot's photon positions drive baked glows, so see the shot notes before touching their timing.
- **Detectors glow momentarily and subtly.** Fast rise, short decay, like a nanowire absorbing a photon and recovering.
- **Cells switch on with photon proximity,** left to right, so viewers understand what the cells do without narration. The glow of the timed circles under the cells **stands for the photon entering the cavity** (user); SH_15 shows that event up close.
- **Glass must read as glass.** The cavities had gone grey and plastic-looking. They now have clear glass, reflections to catch and a teal light inside while a photon visits, matching SH_15's look.
- **The router suggests a vast number of possible paths.** It looks like a real wafer component: a mesh of optical switches (a Mach–Zehnder mesh; agent knowledge). Our photons deliberately use only a few of those paths, to keep the left-to-right motion clear.
- **Delay lines always carry a few photons.** The client asked to show them in use. A photon goes down a spool so it can be entangled with the **next clock cycle** of photons, which makes cluster generation more efficient. There are 2–7 on the loops at any frame.
- **The card fades in instead of popping up.** Its first animation rose from the floor and felt cheap. The wipe is subtle and follows the direction of the logic.

#### Simplifications

Don't "fix" these. They're deliberate choices confirmed by the user, except where marked *(inferred)*.

- **Small numbers:** the generators were cut to 3 to match the three photon paths. The 12 entangling cells stand in for thousands *(inferred from the script)*.
- **Few paths:** the router shows far more routes than the photons ever use.
- **Delay-line photons appear and vanish** inside the entangling wafer. They aren't connected to the main photon paths.
- **Separate generator station:** in the paper, the same kind of unit cell generates, entangles and measures. Generators stand apart here for visual clarity, as a simplified linear process.
- **The photon–cavity interaction is implied, not shown.** Photons don't pass through the cells: they enter the cavity in the shape of the photonic mode. SH_15 shows it; here the glow below each cell implies it. Never describe or animate it as a photon flying through a cell.
- **One comet per photon:** the dual rail is left out for simplicity. SH_15 shows it.
- **Four cells per row:** chosen to connect easily to the simple cluster of **four atoms and one photon**. Keep rows of four.
- **Detector cryogenics** aren't shown *(inferred)*.

#### Before editing

Read [05_shots/SH_18/AGENTS.md](05_shots/SH_18/AGENTS.md) for object names, node groups, bake commands, Blender 5.2 API traps and render rules. The main ones:

- The main photons drive **baked** glows; re-bake after changing them.
- Renders and playblasts share one folder, and the low sample count is deliberate.
- Don't recreate the old card pop-up, and don't delete the card's tilt.

### Template for the next shot

```markdown
### SH_XX: short name
**File / Frames / Script beat / Status**
#### What it's for        (the one or two things the viewer should take away)
#### What we see          (objects, and the science each one stands for)
#### How it unfolds       (frame ranges, camera, events)
#### Why it looks this way (decisions and the user's reasons)
#### Simplifications      (deliberate departures from the science)
#### Before editing       (link to the shot's notes, main traps)
```
