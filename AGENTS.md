# QS Blueprint film: guide for agents

Last updated: 2026-11-26. Start here, then read the `AGENTS.md` (or context file) in the folder of the shot you're working on.

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
- **Brand:** `04_assets/brand/` (quick brand guide, colour palette, Jura for the logo, Overpass for text). On-screen text: Overpass (Light, Regular, Medium, SemiBold); the cards' small labels use Overpass Mono. Accent is the logo cyan; on dark scenes the key colour is white.

### Brand colours

From `04_assets/brand/Quantum Source Quick Brand Guide 8-11-2023.pdf`, page 8 (Pantone / sRGB hex):

| Group | Colours |
|---|---|
| **Logo colour (accent)** | **P. 319 C `#4DDDEC`** (RGB 77/221/236) |
| Neutrals | P. Black C `#000000` · P. 432 C `#3D3D3D` · P. 431 C `#595959` · P. 427 C `#E2E2E2` |
| Deep teals | P. 3035 C `#0F3843` · P. 548 C `#165065` · P. 549 C `#2D8FAC` |
| Blues | P. 281 C `#04224E` · P. 2748 C `#03397A` · P. 297 C `#597EFF` · P. 2716 C `#98A6F9` · P. 285 C `#057BCC` · P. 2995 C `#00B7FF` · P. 305 C `#00CFFF` · P. 2975 C `#A9ECFC` |
| Greens / aquas | P. 3252 C `#36E0D4` · P. 561 C `#1C726A` · P. 563 C `#2FBCAE` · P. 566 C `#B5F7ED` |

**Colour-space trap:** these hex values are sRGB. Blender node colours are scene-linear in the file's working space, and some of our files use **ACEScg** (check `bpy.data.colorspace.working_space`). Convert sRGB → linear Rec.709 (→ ACEScg if needed) before typing a brand colour into a node, or it renders paler. `05_shots/SH_12/sh12_v12_build.py` has a `brand_color()` helper.

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
| SH_02 | Not yet. Known so far (user, Nov 25): the competing neutral-atom shot. It teaches "dot and circle = atom", the red circles are errors, and the errors (not the narration) move us to the diagram, which must be truly flat. It ends on the "WHAT WE HAVE" grid of the chasm, planned as a 2D card. Crisp is reserved for the diagram: the real-world atoms stay hazy, noisy and quantum-like. v04 is under review | [SH_02_CONTEXT_FOR_AGENTS.md](05_shots/SH_02/SH_02_CONTEXT_FOR_AGENTS.md), [NOTES_FOR_HUMANS.md](05_shots/SH_02/NOTES_FOR_HUMANS.md), [SH_02_ANIMATOR_NOTES.md](05_shots/SH_02/SH_02_ANIMATOR_NOTES.md) |
| SH_4, SH_7, SH_8, SH_9, SH_11, SH_17 | Not yet | None |
| **SH_12** | **Yes** | [AGENTS.md](05_shots/SH_12/AGENTS.md) |
| SH_15 | Not yet. Known so far (user, Nov 25): it shows the photon entering the cavity in the shape of the photonic mode. The dual rail is only seen **from above**, in the wider view showing several cavities; the photon in the \|0⟩ rail is **not shown**, because that was the focus of the second Quantum Source movie. It shows a vertical Fabry–Pérot cavity: the top is the edge of an optical fibre; the bottom, in reality another fibre edge, is a reflective round mirror for clarity. Horizontal laser tweezers (horizontal so viewers don't confuse them with the vertical photonic mode) hold the atom floating in space, then fade out by frame 185 in a way that implies they are still there but omitted to simplify the visuals. The mode's lobes stay put while their intensity subtly moves up and down, implying the single photon resonating between the mirrors; that detail belongs only to the single-cell part | [AGENTS.md](05_shots/SH_15/AGENTS.md) |
| **SH_18** | **Yes** | [AGENTS.md](05_shots/SH_18/AGENTS.md) |
| SH_20 | Not yet | None |

### SH_12: the turn and the reveal (compound architecture)

**File:** `05_shots/SH_12/sh_12_The_Turn_and_the_Reveal_15.blend` (v15, awaiting review; built from v11, the user's version; v13's timing was approved). **Frames:** 1–462 (exactly 18 s 12 f, the user's final-draft length). **Script:** beat 3, "the turn". **Status:** v15 draft render (50 %, 32 samples) under way.

#### What it's for

It comes right after the narration describes PsiQuantum's huge photonic facility, and introduces Quantum Source's answer: the **compound architecture**, photonic and atomic qubits combined, miniaturised onto wafer-made photonic components. "Compound Architecture" is the term the company is coining; it is the central concept of the production (user). The viewer should take away:

1. Light and matter, combined into one lattice: each photon entangled with four atoms, each atom with four photons.
2. That lattice runs on a small chip: waveguides (photonic qubits) connecting cavities that each hold an atom (atomic qubits).

#### What we see

| Element | On screen | Science |
|---|---|---|
| Logic card (Card 10) | LIGHT and MATTER grids merge into the photon-atom grid; SH_02's visual language, now with photons. The card's own "PHOTON- ATOM GRID" words are masked so they don't compete with the title (user) | Compound cluster state |
| Title | **COMPOUND ARCHITECTURE**, large and celebratory, above the lattice; it slides up as the chip rises, then leaves | The coined term |
| Photonic chip | Rises from the bottom; waveguides draw over it from the right edge, connecting the Fabry–Pérot cavities (cylinders); a few single photons (cyan comets) then run through them | Waveguides route single photons: the photonic qubits |
| Callouts | PHOTONIC QUBITS (pinned where the waveguides start drawing, elbow on the right so the leader stays clear of the chip) and ATOMIC QUBITS (pinned to the atom of the cavity the camera later dives into, and carried up with it), timed to the narration | |
| Atom glow wave + layer glow | In the profile view, tiny shines turn on and off cavity by cavity, left to right, inside a soft brand-blue glow along the middle of the wafer sandwich | One trapped atom per cavity: the atomic qubits |
| Pentet | A section breaks up, a 5-cavity sub-unit lifts out, and v11's swift camera move dives into it | Hands over to SH_15's single cavity |

#### How it unfolds

Timing is the user's final draft (Nov 26).

| Frames | What happens | Narration |
|---|---|---|
| 1–149 | Card 10 plays from its first frame: the LIGHT grid appears, then MATTER | "Why choose light or matter when you can leverage the best of both?" |
| 88 (3 s 12 f) | The grids begin to merge; the title builds above them | "Welcome to Quantum Source Compound Architecture." |
| 150 (6 s) | Merge done; the chip floats in from below. The grid overlaps it ~12 frames, then fades; the title slides up and leaves by ~202 | |
| 238–366 | Waveguides draw; PHOTONIC QUBITS callout, up by "flying" (262, 10 s 11 f) | "We combine the … connectivity of flying photonic qubits…" |
| 324–398 | Profile view, atom wave, ATOMIC QUBITS callout on "stationary" (346, 13 s 20 f); the two callouts overlap briefly | "…with the stability of stationary atomic qubits." |
| 375–462 | Break-up, pentet lifts, v11's own camera move dives in, ending close on a cavity. The ATOMIC callout rides the pentet up until 436; a dark floor sweeps in under it (438–456, +X → −X) and rises with it, leaving only the pentet so the cut to the darker SH_15 doesn't flash | |

#### Why it looks this way

- **The card is in the scene, not composited:** a plane at the focus distance, with colour as alpha (user's preference), so black is transparent. It floats above the hardware like SH_18's logic card. Briefly overlapping the rising chip says the lattice corresponds to what happens on the chip (user).
- **Title letters converge from the outside in**, echoing the grids combining. Overpass Light, white, with a brand-cyan rule and eyebrow.
- **Callouts are elegant data-vis labels** in the brand style (user): Overpass white, cyan accent, hairline leaders. Their placement follows the chip architecture; their timing follows the narration.
- **Atoms are tiny and subtle, "like a tiny shine" (user).** They turn on, then off as the wave passes, to say "the atoms are there, we just omit them for simplicity" (user).
- **The ending is v11's own swift camera move (user).** A custom dive that matched SH_15's first frame exactly (v12) ruined the transition; the speed and blur of the original sell the cut. Don't replace it.

#### Simplifications

- Atoms are normally omitted; the glow wave is a reminder, not a physical process. Never animate light travelling between atoms.
- The chip shows a handful of tiles; the real machine has thousands of unit cells *(inferred from the script)*.
- Photons are tiny, few and irregular (about 40 on the chip at once, smaller than a cavity) and only on the longer guides; the real chip would carry many more. They dim during the atomic beat.

#### Before editing

Read [05_shots/SH_12/AGENTS.md](05_shots/SH_12/AGENTS.md). Main traps: v15 is built by `sh12_v15_build.py` from v11 (don't re-run it over hand edits); all v11 keys are shifted by +149; the file's working colour space is ACEScg; the frame timings above are the user's and are parameters of the script.

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
- **One comet per photon:** the dual rail is left out for simplicity. SH_15 shows it, only from above in its wider view of several cavities (user).
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
