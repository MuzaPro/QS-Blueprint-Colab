# The Complete Guide
## Quantum Source's Compound Photon–Atom Architecture, and the photonic quantum computing it's built on

*A single, organized reference that replaces the earlier two companions. It builds the physics bedrock first, then walks the Quantum Source machine layer by layer — drawing on both the short white paper and the full technical Blueprint — and ends with the field landscape, a consolidated animation-accuracy checklist, and a glossary. The aim is one in-depth reading experience that prepares you for the creative work without sending you chasing concepts across three files.*

---

### How to use this guide

It's built as a narrative, not a reference dump, so reading start-to-finish pays off — each part assumes the one before it. But it's also navigable: the parts are self-contained enough to jump back into, and the glossary and script-map at the end are for quick lookups during production.

Three threads run through it, marked where useful:
- **Why it matters** — the practical "so what" of an idea.
- **Animation note** — something easy to get subtly wrong on screen, or a strong visual hook.
- **From the Blueprint** — detail that lives only in the full technical paper, not the short white paper.

A reading rhythm that works: skim Parts I–III to refresh the universal concepts, then read Parts IV–VI slowly alongside the white paper (and the Blueprint figures), since that's where Quantum Source's actual machine lives.

---

# PART I — THE BEDROCK: HOW QUANTUM COMPUTING ACTUALLY WORKS

Everything downstream rests on a handful of ideas that popular explanations tend to fumble. Get these right and the rest of the architecture reads cleanly.

### 1. A qubit, and the thing everyone skips: phase

A classical bit is 0 or 1. A qubit's state is a combination (superposition) of |0⟩ and |1⟩, described by two numbers called amplitudes. The famous phrase "both at once" captures half of it and hides the important half: each amplitude carries a **phase** — an angle, like the position of a clock hand. Two qubits can have identical odds of reading 0 or 1 and still be completely different states because their phases differ.

The standard picture is the **Bloch sphere**: every single-qubit state is a point on a ball. The poles are |0⟩ and |1⟩; the equator is equal superposition, and *where* on the equator you sit is the phase. Gates are rotations of this sphere.

**Animation note:** if superposition is drawn only as flickering between 0 and 1, you've shown the part that's basically classical randomness and omitted the quantum part. A truer metaphor is an arrow on a sphere, or a wave with a definite point in its cycle — something with an *orientation*.

### 2. Interference is the engine

Because amplitudes are wave-like, they can add or cancel — constructive and destructive interference, like overlapping ripples. A quantum algorithm is a choreographed interference pattern: arrange for the amplitudes leading to wrong answers to cancel and the right ones to reinforce. The speed-up is *not* "trying all answers in parallel" (a stubborn myth); it's interference sculpting the probabilities before you measure. For photonics this is doubly literal — the qubits are light and the gates are interference.

### 3. Measurement: probabilistic, destructive, one-shot

Reading a qubit doesn't gently reveal it. Measurement forces the superposition to **collapse** to 0 or 1, with probabilities equal to the *square* of the amplitudes (the **Born rule**). The delicate phase information is gone, and you get one classical bit. You cannot peek without disturbing.

**Animation note:** measurement is a sudden, irreversible, random projection — never a soft readout or a value you can re-check. It's also where randomness genuinely enters; everything before it is, in principle, deterministic wave evolution.

### 4. No-cloning, and why it makes everything hard

You **cannot copy an unknown quantum state**. No quantum photocopier exists. This one fact shapes the field: you can't back up a qubit, you can't fix errors by keeping spares, and (the upside) you can't eavesdrop without leaving traces. Error correction therefore has to protect information *without copying or directly reading it* — which is why it's so much subtler than the classical kind (Part VI).

### 5. Entanglement, properly

Two qubits are **entangled** when their joint state can't be split into "this one is X and that one is Y" — the state only makes sense for the pair. The result is correlations *stronger than anything classical*: measure one and you instantly know something about the other, and the strength of those correlations provably exceeds any "decided in advance" explanation.

The misconceptions worth not animating:
- **Nothing travels between entangled qubits.** The correlation shows up when you compare results later; no signal, nothing moving. You cannot send information with entanglement alone. Resist the "glowing wire that pulses when you wiggle one end."
- **Entanglement is consumable.** In the computing model we'll use, it's fuel — each measurement burns some of it.
- **"Spooky action" is a quip, not a mechanism.** The honest version is correlation without communication.

The **Bell states** are the four maximally entangled two-qubit states — the unit cells everything is built from. Identifying which one a pair is in (a **Bell-state measurement**) is a recurring operation, and — crucial for photonics — it's exactly the thing plain optics can only do half the time (Part II).

### 6. Cluster and graph states: the fabric

Scale entanglement to many qubits and you get **graph states** (and the special case **cluster states**): qubits are dots, entangling links are edges. These big entangled webs are the raw material of the computing model photonics uses. The RHG lattice at the heart of the Quantum Source machine is one of these — a specific 3-D cluster state.

**Animation note:** a node-and-edge web is the *right* instinct for a cluster state — but edges are established relationships (entanglement), not pipes carrying anything, and they're cut as qubits get measured and consumed.

### 7. Two ways to run a quantum computer

This distinction is the hinge of why photonics looks the way it does.

**Circuit model (gate model).** Qubits persist for the whole computation, and you apply a timed sequence of gates, like notes on a score. Matter platforms — superconducting, trapped-ion, neutral-atom — work this way, because their qubits sit still and can be operated on repeatedly. Error correction here means *repeatedly* measuring parity checks on living qubits, round after round.

**Measurement-based model (MBQC, "one-way").** A different choreography: first build a big entangled cluster state — all the entangling work done up front — then compute by *measuring* the qubits one at a time, in chosen directions. There are no entangling gates during the computation; the entanglement was pre-loaded, and measurement consumes it. Information **teleports forward** from measured qubits to unmeasured ones. The load-bearing subtlety most summaries omit: the measurements are **adaptive** — the direction you measure a qubit depends on earlier outcomes, via a fast classical feedback loop called **feed-forward**. That's what makes MBQC a controllable computer rather than a random readout of an entangled blob.

The two models compute the same things. Photonics gravitates to MBQC for a blunt practical reason: **photons don't sit still.** They fly at light speed and are hard to store, so you can't keep returning to the same photon. It's far more natural to make a big entangled state of flying photons and measure it on the fly. Quantum Source lives entirely in this measurement-based world.

---

# PART II — THE PROBLEM QUANTUM SOURCE IS SOLVING

### 8. The quantum chasm

A useful quantum computer will need on the order of a *million* physical qubits. Today's best qubits err roughly once every thousand to ten-thousand operations (error rates of 10⁻³–10⁻⁴); useful algorithms need around 10⁻¹² — about ten orders of magnitude better. That gap is the **quantum chasm**.

You cross it not by building one perfect qubit but by bundling many imperfect ones into a single well-behaved **logical qubit** via **quantum error correction (QEC)** — often 100–1000 physical qubits per logical qubit. So an algorithm that "really" needs a few thousand qubits balloons to ~10⁶ physical qubits. This is the canyon in scene 1 of your script.

### 9. Connectivity: the second axis everyone underweights

A million good qubits is necessary but not sufficient. You also need **connectivity** — the ability to perform a two-qubit entangling gate between *any* two qubits, ideally regardless of distance. High connectivity makes efficient error-correcting codes possible and gives freedom in laying out a computation. This word is the throughline of the entire Quantum Source pitch; hold onto it.

### 10. Why matter-based platforms stall

- **Superconducting** qubits are wired on a flat chip, so each mostly talks only to its nearest neighbors; reaching a distant qubit means routing through everything between.
- **Trapped ions** can entangle distant ions in a chain in principle, but as the chain grows the shared vibrational modes get crowded and gates degrade.
- **Neutral atoms** get reconfigurable connectivity by physically shuttling atoms around — but slowly. **From the Blueprint:** shuttling and mid-circuit measurement push error-correction round times into the *milliseconds*, roughly three orders of magnitude slower than superconducting, with overhead that grows with transport distance.
- And only so many matter qubits fit in one controlled box (vacuum chamber, cryostat), so millions means many boxes — and reliably linking boxes is its own hard problem.

### 11. Why pure photonics stalls

Photons are gorgeous carriers — no cryogenics or vacuum needed, single-qubit operations are just passive optics, and they barely interact with their environment so they resist decoherence; optical-fibre delay lines even serve as near-noise-free short-term memory. The catch is entanglement.

With ordinary optics you **cannot entangle two photons deterministically**. The standard move — a **fusion** (a Bell-state measurement on a beam splitter) — succeeds at best **50%** of the time, because plain optics can only tell apart two of the four Bell states. That's the "50% Max Success" in your trade-off scene. To build the large entangled states a real computer needs, you boost that success rate, and the boosting cost explodes. **From the Blueprint:** the need to herald probabilistic sources and gates, with active multiplexing, runs to roughly **five to six orders of magnitude** of overhead in photons and hardware. On top of that, fusion requires photons from independent sources to be mutually **indistinguishable** (more on why in Part III), a punishing demand on source quality.

The prize, though, is real: once entanglement is solved, photonic connectivity is effectively unlimited. Quantum Source's whole reason for existing is a way to get that prize without paying the boosting bill.

---

# PART III — THE PHOTONICS YOU NEED TO READ THE HARDWARE

Before the machine itself, the optical vocabulary — so Part IV reads as engineering rather than magic.

### 12. Turning a photon into a qubit

Several encodings exist, and the choice ripples through the whole design:
- **Path / dual-rail** — the photon is in one of two waveguides or modes ("which lane"). This is what Quantum Source uses. Its great virtue: if the photon is *lost*, you find none in either lane and you *know* it's gone — which matters enormously for error correction (Part VI).
- **Polarization** — horizontal vs. vertical; common in communication, harder to keep stable on a chip.
- **Time-bin** — early vs. late arrival.
- **Continuous-variable** — a different philosophy entirely: encode in the amplitude and phase of a light *field* across many photons, not in single photons. (This is a rival camp's route; see Part VII.)

**Animation note:** these aren't interchangeable eye-candy. A dual-rail photon is one particle choosing between two paths; a polarization qubit is one particle with an orientation; a continuous-variable mode is a field, better drawn as a fuzzy distribution than a dot. Quantum Source = single photons, dual-rail.

### 13. The linear-optics toolbox

- **Beam splitter** — a half-silvered mirror that sends a photon two ways in superposition; the site of two-photon interference.
- **Phase shifter** — delays the light's cycle, i.e. sets the phase (§1); with beam splitters, this steers interference.
- **Mach–Zehnder interferometer** — two beam splitters with a phase shifter between; the tunable building block of programmable photonic chips.
- **Polarizing beam splitter (PBS)** — sorts photons by polarization; it appears all over the Quantum Source figures, separating the cavity's two modes.

### 14. The Hong–Ou–Mandel effect, and why QS escapes it

Send two **indistinguishable** photons into a 50:50 beam splitter from opposite sides and — against classical intuition — they always leave together through the same port ("bunching"). This **Hong–Ou–Mandel (HOM) effect** is pure two-photon interference, and it underlies every linear-optical entangling operation, including fusion. The snag: it only works if the photons are truly identical (same color, timing, shape). If they differ, no interference, gate fails — which is *the* reason indistinguishability is an obsession in photonic hardware.

**Why it matters:** Quantum Source's entanglement runs through an atom, not through photon–photon interference, so it **does not require indistinguishable photons** at all. That's not a footnote — it removes one of the field's hardest requirements, and it's a genuine differentiator to keep straight on screen.

### 15. Sources and detectors

Single photons must arrive **on demand**, **one at a time** (purity), and **identical** (indistinguishability), at high **efficiency** — hitting all four at once is the field's central struggle. **Probabilistic sources** (e.g. spontaneous parametric down-conversion) only fire *sometimes* and you herald success by catching a partner photon — cheap but wasteful, with efficiencies around a percent. **Deterministic sources** are the frontier; Quantum Source's atom-cavity node is one of them (Part IV).

Detection is **destructive** — the photon is absorbed and ceases to exist. The best detectors (superconducting nanowire single-photon detectors) are highly efficient but must sit near absolute zero. This is the **"room-temperature" asterisk**: the optics genuinely run warm, but the *detectors* are cryogenic, so a fully accurate scene wouldn't show zero cold hardware.

### 16. Loss, and bulk vs. integrated

For matter qubits the enemies are bit- and phase-flips; for photons the dominant failure is simply **losing the photon** — absorbed or scattered, information gone. Every serious photonic effort fights loss hardest. The redeeming twist (developed in Part VI): in dual-rail, a lost photon is a *detectable* failure, which is unusually tractable. Finally, early experiments used **bulk optics** on a table; scaling means **integrated photonic chips** — waveguides etched in silicon or silicon nitride, made in ordinary chip foundries. Quantum Source traps its atoms on such a photonic chip.

---

# PART IV — THE QUANTUM SOURCE MACHINE, LAYER BY LAYER

This is the heart, and where the Blueprint adds the most. Read it slowly alongside the papers.

### 17. The big idea: route entanglement through an atom

Instead of entangling photon-with-photon (the ≤50% trap), Quantum Source introduces two kinds of qubit and entangles *them*: **photonic (flying)** qubits for long-range connectivity, and **atomic (stationary)** qubits as reusable, controllable anchors and short-term memories. The link is a near-deterministic **CZ gate** between a photon and an atom. The hard problem of photon–photon entanglement is never solved head-on; it's circumvented by making every entanglement pass through an atom. The compound name is apt: photons carry information *and* connectivity, atoms carry information *and* control.

### 18. The unit cell

**From the Blueprint, with specifics worth rendering accurately.** One node is a single **rubidium-87 atom** trapped inside a **single-sided Fabry–Pérot cavity** — two facing micro-mirrors, one *flat* (the input/output coupler) and one *curved* (radius ~30 µm), separated by ~25 µm. The cavity is locked to the rubidium **D1 transition at 795 nm** (the short white paper hedged "D1 or D2"; the Blueprint commits to D1). The atom is held in a **1D optical-lattice dipole trap**, loaded by first cooling atoms in a magneto-optical trap (MOT) and then a polarization-gradient-cooling beam. Around the cavity sit several control beams — cooling, a π-polarized excitation beam, and a 1324 nm "level-engineering" laser (§23).

The figure of merit is **cooperativity**, C = g²/(κγ), comparing how strongly the atom and a cavity photon interact (g) against how fast either is lost (κ, γ). The system is engineered into the **high-cooperativity regime** (with atom–cavity coupling g/2π on the order of hundreds of MHz), where the photon–atom interaction probability approaches one.

**Why it matters / the intuition:** the mirrors trap light so it bounces many times through the tiny gap where the atom sits, so even a single photon effectively passes the atom over and over until it almost certainly interacts. That's what makes the gate **near-deterministic** rather than probabilistic — the cavity-QED move you already had a feel for, now with the actual hardware behind it.

### 19. The atom's many roles — one node, reused

Said plainly because it's the conceptual center: the *same* atom in the *same* cavity performs, at different moments,
- single-photon **generation** (via vSTIRAP, §21),
- the photon–atom **entangling gate** (Duan–Kimble CZ, §20),
- **state preparation and measurement** (SPAM, §22),

…and then, once measured out, it is **reset and reused** for the next round. **From the Blueprint:** because the simplest design needs comparable numbers of photons and atoms but atoms can be recycled, smart scheduling cuts the number of cavities — the expensive part — by more than an order of magnitude. When a scene shows one atom-cavity making photons, entangling them, and being measured, it's depicting this multi-tasking, recycled node — not three different devices.

### 20. The entangling gate (the CZ)

This is your "Engine" scene. It's a **dual-rail variant of the Duan–Kimble protocol**. The clean mechanism: the photon's **|1⟩ rail is routed into the cavity** and can interact with the atom, while the **|0⟩ rail bypasses the cavity entirely**. A photon reflected from the cavity picks up a phase that *depends on the atom's state*: when the atom is in |1⟩, the reflected photon gains a half-turn (π) phase relative to the |0⟩ case. The net effect is the textbook **controlled-Z**: the combined |1,1⟩ component flips sign, everything else is untouched. That sign-flip is the entanglement your animation forges between photon and atom.

**From the Blueprint:** the robust version they actually build is the **symmetrized CZ**, in which both atomic states interact with the cavity symmetrically. This cancels errors from *loss imbalance* between the two outcomes regardless of the exact cavity parameters — which is why it's called the central primitive. Per-gate efficiency lands around **98%**.

**Animation note:** the |1⟩-into-cavity / |0⟩-bypasses split is a strong, accurate visual for "the atom only feels one rail." And the photon **reflects** off the single-sided cavity rather than passing through.

### 21. Photon generation (vSTIRAP)

The same node makes single photons by **vacuum-stimulated Raman adiabatic passage (vSTIRAP)** in a Λ-shaped level configuration. **From the Blueprint, the concrete path:** the atom is prepared in one ground level, a π-polarized control pulse drives it up to an excited state, and it then transfers coherently to another ground level while emitting exactly one photon into a cavity mode. Because the start and end ground levels differ in energy by about 6.8 GHz, the atom can't easily get re-excited, so the photon comes out clean and single. Done "adiabatically" (smoothly), it's forgiving about pulse shape — which, again, relaxes the indistinguishability demands that haunt fusion-based schemes. Pulse lengths land around **10 ns**, the same timescale as all the other operations, since it's the same hardware.

### 22. State preparation and measurement (SPAM)

Both work by having the atom emit a photon and then measuring *that photon* — turning atomic operations into photonic ones.
- **Preparation** is measurement-based: the atom emits a photon so the two become entangled (a photon–atom Bell state), and measuring the photon *projects* the atom into the desired state. The photon doubles as a **herald** — its detection confirms success, so failures are discarded. By choosing the photon's measurement basis you can prepare arbitrary atomic states (even the special "T-state") without ever doing a direct rotation on the atom.
- **Measurement** maps the atom's state onto a photon and measures that — a step the Blueprint names **STAP** (State Transfer from Atom to Photon). The emitted photon can even be routed into more gates before being detected.
- The two are **complementary by design**: they share the same optical path (fewer phase errors), and the atom's state right after a measurement is the starting point for the next preparation — which fits MBQC's endless prepare–entangle–measure rhythm perfectly. Cavity-limited efficiencies are around **97%**.

### 23. Level engineering

A practical wrinkle: in this atom, the qubit states couple not only to the levels you want but also to an unwanted shared excited state. **From the Blueprint:** a 1324 nm control laser couples the relevant excited manifold to a higher one, reshaping the level structure so the unwanted transition is suppressed while the wanted coupling survives. It's the quiet fix that lets the clean CZ work in a real rubidium atom — worth knowing exists, rarely something to foreground visually.

---

# PART V — FROM ONE NODE TO A MACHINE

The Blueprint fills in the layer the short white paper skipped: how unit cells become a computer.

### 24. The photon cycle — the core repeating motif

**From the Blueprint, and the single most useful framing for animation.** The machine runs the same loop over and over: a photon is **generated** on demand, runs through a **sequence of photon–atom CZ gates** (a bulk photon does four), and is **measured in the X basis** at a single-photon detector. Generate → entangle-along-a-chain → measure, endlessly. That cycle *is* the computer. (A bulk photon thus passes through six lossy steps in its life: one generation, four gates, one measurement — a number that comes back in the error analysis.)

**Animation note:** if you animate one thing faithfully, make it this. Follow a single photon born at a node, threading through several atom-cavity nodes that stamp entanglement onto it, then landing at a detector and vanishing.

### 25. The system architecture

**From the Blueprint (Fig. 4).** Between the single node and the abstract lattice sits real plumbing: many **unit cells** feed into reconfigurable **routers** and **optical delay lines** that dynamically wire up whatever connectivity the cluster state needs; photons end at **single-photon detectors**; and a **classical control-and-compute layer** coordinates everything *and runs real-time error-correction decoding* on the flood of detector outcomes. This is a legitimate "machine room" scene — distinct from both the cavity close-up and the glowing 3-D lattice — and it's where the routers, fibre loops, and a humming classical computer belong.

### 26. Building the cluster state, and the recycling trick

The target cluster state (the RHG lattice, Part VI) is assembled from the native operations. The Blueprint gives two **generation schemes**:
- **Bipartite** — straightforward, uses on the order of d² active atoms (d is the code distance), recycling measured atoms as it goes.
- **Interleaved** — a resource-optimized version that drops the active-atom count to ~d by storing photons in **delay lines** between interactions; conceptually, an atom that finishes its job in one row is reused in the next. The trade is more optical delay (and delay lines are lossy), so you exchange fewer atoms for more photon loss.

**From the Blueprint:** the long atomic coherence also gives a **timing degree of freedom** — an atom can hold its state briefly as short-term memory, so generation and routing don't all have to happen at full speed. That buffering *relaxes the switching and classical-processing rates* the rest of the system must hit, which is a quiet but real engineering advantage.

---

# PART VI — MAKING IT FAULT-TOLERANT

The most abstract part, scaffolded so the visuals can be right about *why* it works.

### 27. Why error correction is subtle, and the escape hatch

No-cloning (§4) forbids copies, and measurement destroys superpositions, so the classical "keep three copies and vote" is impossible. The escape: encode one **logical** qubit across many **physical** ones in an entangled state, then measure cleverly chosen parity checks — **stabilizers** — that reveal *whether and where* an error happened (the **syndrome**) **without** revealing the encoded information. You learn about the errors while staying blind to the data. That is the central trick of QEC.

### 28. Flips, the surface code, distance, and the threshold

Quantum errors look continuous, but a stabilizer measurement **projects** any error into a discrete set: a **bit-flip** (X), a **phase-flip** (Z, invisible classically — it scrambles the phase of §1), or both. The leading code, the **surface code**, lays physical qubits on a 2-D grid: **data qubits** hold information, interleaved **ancilla qubits** repeatedly run the parity checks, and a classical **decoder** infers the most likely error from the syndrome. The **code distance d** is essentially the grid size — bigger d means more protection and quadratically more qubits.

The single most important idea in the whole subject is the **threshold theorem**: if physical components are good enough — below a certain error threshold — then enlarging the code (bigger d) drives the *logical* error rate as low as you like. Below threshold, scaling up helps; above it, scaling up hurts. Every hardware roadmap is, at bottom, a race to get under threshold and then scale.

### 29. Foliation and the RHG lattice

Recall (§7) that the circuit model corrects errors as *repeated rounds over time*, while MBQC measures a pre-built entangled state. **Foliation** is the bridge: it flattens those repeated-in-time rounds into stacked spatial **layers** of a single 3-D cluster state, which you consume by measuring layer by layer. The canonical foliated structure is the **Raussendorf–Harrington–Goyal (RHG) lattice** — a 3-D cluster state that realizes the surface code in measurement-based form. It's your outro's glowing lattice, and one of its three axes is *time* (successive measured layers), so a zoom-out can read as growth over time rather than a static crystal.

**The QS-specific flavor:** because every CZ links a *photon to an atom*, the RHG cluster state is naturally **bipartite** — it alternates photons and atoms, and the Blueprint colors the lattice exactly that way (cyan photons, dark-blue atoms). Both species take turns as data qubits and as check ("syndrome-like") qubits. The one asymmetry: a measured photon is gone forever, while a measured atom is reset and reused — which is what lets the lattice be generated continuously, layer after layer.

### 30. The QS error model: loss, erasure, and the bond-loss nuance

**From the Blueprint, and an important refinement.** The dominant error is photon loss, and in dual-rail a lost photon is **heralded** — you know it happened — which makes it an **erasure**, the easy kind of error to correct. That's the optimistic half.

The half that's easy to miss: a lost photon doesn't just remove *itself*. Because it was scheduled to perform CZ gates with several atoms, its loss silently removes those **bonds**, corrupting neighboring stabilizer checks *through the absence of gates that never happened* — and, unlike the photon's own loss, the *location* of that induced damage isn't directly flagged. The Blueprint calls this **bond-loss propagation**, and it's exactly why the numbers split: a correlation surface carried by *photons* tolerates more loss (threshold ~4.7% per gate, since photon loss is heralded) than one carried by *atoms* (~2.6% per gate, because the induced bond loss on atoms is not). The headline figure is the binding one: **~2.6% loss per physical gate, equivalent to ~15% total loss over a photon's trajectory**. (For reference, the *abstract* RHG code can tolerate ~25% measurement loss; the hardware number is lower because real loss is correlated, not idealized.)

**Why it matters:** so "photonic loss is the easy erasure error" is half-true. State it carefully — the photon's loss is clean, but the damage it leaves on its atomic neighbors is the hard part, and it's the binding constraint on the whole architecture.

### 31. Logical gates by re-wiring, and the road to universality

**From the Blueprint.** Storing a logical qubit (a memory channel) isn't computing — you also need logical *gates*. The elegant part: in this architecture they're done by **changing the connectivity pattern**, not by moving qubits. The logical **Hadamard** inserts a layer with its links rotated 90° (a "domain wall"); the **phase gate** folds the lattice and adds diagonal links with special measurements; the **CNOT** adds a single layer of links between two logical blocks. All three reach the same threshold as plain memory and need no extra logical qubits or rounds.

**Why it matters:** because connectivity is unrestricted, these gates are **transversal** (cheap — one layer, O(1) time), whereas locally-connected platforms must use **lattice surgery**, which costs an O(d²) ancilla patch and O(d) extra rounds per gate. This is the "connectivity is the prize" theme reaching all the way up into the compute layer — and a sharp contrast to neutral-atom *shuttling*.

One last completion: these cheap gates (the **Clifford** set) aren't enough to compute everything. Universality needs one more, non-Clifford gate — the **T gate** — supplied by distilled **magic states** (the Blueprint gives two recipes, "code teleportation" and "magic-state cultivation"). You likely won't animate this, but it's the piece that makes the machine a *universal* computer rather than just an error-corrected memory.

### 32. The throughline

Notice how one idea — unrestricted connectivity — pays off at every level: it lets near-deterministic atom-photon CZ gates build cluster states without exponential overhead (Part IV–V), it enables cheap transversal logical gates (§31), and it opens the door to next-generation **qLDPC codes** that need long-range checks and promise far fewer physical qubits per logical qubit (the Blueprint's stated future direction). Connectivity isn't a feature of this architecture; it's the spine.

---

# PART VII — WHERE QUANTUM SOURCE SITS IN THE FIELD

*A current snapshot (early 2026); the specifics here are the most time-sensitive content in this guide, so treat funding figures, chip names, and milestones as a moment-in-time picture rather than fixed facts.*

The field splits first into **discrete-variable** (single-photon) and **continuous-variable** (field/squeezed-light) photonics. Within that, the players are pursuing four broad ways out of the entanglement bottleneck:

- **Brute-force the probabilistic gates — fusion-based (PsiQuantum).** Accept that fusions are probabilistic and design the whole machine around making failures cheap. PsiQuantum assembles small entangled "resource states" into a big fault-tolerant cluster via fusion gates, on silicon photonics (fabricated with GlobalFoundries; its Omega chipset was announced in early 2025), aiming at roughly a million photons. Encoding: dual-rail single photons, like QS — but the entanglement is photon–photon, with loss-tolerance pushed above ~18%.
- **Change the qubit — continuous-variable / GKP (Xanadu).** Encode qubits in squeezed light using GKP states that build error resilience into the physical qubit, sidestepping unreliable single photons; Xanadu has shown GKP states on-chip and became the first publicly traded pure-play photonic company in early 2026.
- **Fix the source — deterministic emitters (Quandela, Aegiq, Sparrow).** Keep single-photon dual-rail computing but replace the probabilistic source with engineered quantum-dot emitters that fire identical photons on command.
- **Don't entangle photons at all — matter-mediated (Quantum Source).** Route entanglement through a single atom in a cavity, making the gate near-deterministic and the same atom the photon source. Others in the broader space include ORCA (time-domain multiplexing), QuiX (continuous-variable on silicon nitride), and Photonic Inc (a spin–photon hybrid using silicon T-centres).

**The one-line placement:** everyone here uses light for connectivity; Quantum Source is the one using a single atom as the deterministic switchboard that makes the light entangle. Its signature image — the photon meeting the atom in the cavity — is unique to it.

Honest caveats to carry: no modality has won as of 2026; timelines (million-qubit machines) are roadmap targets, not products; and "room-temperature" has the cryogenic-detector asterisk (§15).

---

# PART VIII — ANIMATION ACCURACY: THE CONSOLIDATED CHECKLIST

The distilled list of what's easy to get subtly wrong, or worth getting right:

- **Superposition** is an arrow on a sphere / a wave with a phase — not just a flickering 0/1 coin. The phase is the quantum part.
- **Computation** is interference (amplitudes reinforcing and cancelling), not parallel trial of all answers.
- **Measurement** is sudden, random, destructive collapse — never a soft or repeatable readout.
- **Entanglement** is correlation, not a wire. Nothing travels along the link; you can't signal through it; it gets consumed.
- **A cluster state** is a node-and-edge web that's *measured away* layer by layer; edges are relationships, not conduits.
- **The 3-D RHG lattice has a time axis** — one dimension is successive measured layers, so a zoom-out reads as growth over time. Color it bipartite: photons and atoms alternating.
- **The photon cycle is the core motif** — born at a node, threaded through several atom-cavity CZ gates, then detected and gone. Animate this faithfully above all.
- **The CZ gate**: the |1⟩ rail enters the cavity and feels the atom; the |0⟩ rail bypasses it; the photon **reflects** off the single-sided cavity.
- **The cavity is a single-sided Fabry–Pérot** — one flat mirror (in/out coupler), one curved — with the Rb-87 atom held in an optical-lattice trap, on the D1 line (795 nm), surrounded by control beams. Not a generic mirror box.
- **One node, many jobs, recycled** — generation, gating, and SPAM happen at the same atom-cavity site at different moments; don't split it into separate machines.
- **Photons interfering directly at a beam splitter implies a *competitor's* route** (fusion), not QS's atom-mediated one — and QS pointedly does *not* need indistinguishable photons.
- **Loss is the photonic error** — a photon simply vanishing — and in dual-rail it's a *flagged* disappearance; but a lost photon also quietly severs its scheduled bonds to neighboring atoms (bond-loss propagation).
- **Logical gates are done by re-wiring connectivity**, not by physically shuttling qubits — a clean contrast with neutral-atom machines.
- **There's a system layer** worth showing — unit cells, routers, fibre delay loops, single-photon detectors, and a classical computer doing live decoding.
- **Some cold hardware remains** (detectors), even though the optics run warm.
- **Render architecture, not a finished product** — the science is mid-flight.

---

# GLOSSARY

- **Amplitude / phase** — the two parts of a qubit's state; phase is the wave-cycle angle that drives interference and is invisible to a single measurement.
- **Bloch sphere** — the geometric picture of a single qubit as a point on a ball.
- **Interference** — amplitudes adding or cancelling; the actual computational engine.
- **Born rule** — measurement probabilities equal amplitudes squared.
- **No-cloning theorem** — you cannot copy an unknown quantum state.
- **Entanglement** — correlations between qubits that can't be described independently; stronger than any classical explanation; consumable in MBQC.
- **Bell states** — the four maximally entangled two-qubit states; the unit cells of entanglement.
- **Bell-state measurement** — identifying which Bell state a pair is in; plain optics manages this only ≤50% of the time.
- **Graph / cluster state** — a large multi-qubit entangled web; the raw resource for MBQC.
- **Circuit model (CBQC)** — computing by timed gates on persistent qubits.
- **Measurement-based (MBQC / one-way)** — computing by adaptively measuring a pre-built cluster state; entanglement is consumed.
- **Feed-forward** — using earlier measurement outcomes to choose later measurement settings; what makes MBQC controllable.
- **Fusion** — an entangling measurement on photons at a beam splitter; probabilistic (≤50%); the competitor route QS avoids.
- **Quantum chasm** — the ~10-order-of-magnitude gap between current and required error rates.
- **Logical vs physical qubit** — a reliable encoded qubit built from many error-prone physical ones.
- **Quantum error correction (QEC)** — encoding + parity-checking that turns noisy physical qubits into reliable logical ones.
- **Connectivity** — which qubits can be directly entangled; "unrestricted" means any-to-any; the spine of the QS pitch.
- **Cavity QED** — the physics of a single atom interacting with light trapped between mirrors; QS's core mechanism.
- **Cooperativity (C)** — figure of merit for atom–cavity interaction strength vs. losses; high C → near-deterministic interaction.
- **Fabry–Pérot cavity** — two facing mirrors forming an optical resonator; QS uses a single-sided one (one flat, one curved mirror).
- **Dual-rail encoding** — a photonic qubit defined by which of two paths a single photon occupies; makes loss detectable.
- **CZ (controlled-Z) gate** — the entangling gate; flips the sign of the |1,1⟩ component, leaves the rest unchanged.
- **Duan–Kimble protocol** — the reflection-based method turning the atom's state into a conditional phase on a photon; QS uses a symmetrized dual-rail variant.
- **vSTIRAP** — the smooth, laser-driven process the node uses to emit single photons on demand.
- **SPAM** — State Preparation And Measurement.
- **STAP** — State Transfer from Atom to Photon; how the atom's state is read out (mapped onto a photon, then measured).
- **Level engineering** — using an auxiliary laser (1324 nm) to reshape the atom's levels and suppress unwanted transitions.
- **Hong–Ou–Mandel (HOM) effect** — two indistinguishable photons bunching at a beam splitter; the basis of fusion and the reason indistinguishability matters (and which QS doesn't need).
- **Indistinguishability / purity / efficiency** — the quality metrics a single-photon source must hit at once.
- **Single-photon detector (SNSPD)** — highly efficient photon detector; destructive and cryogenic.
- **Photon loss** — the dominant photonic error; a photon absorbed or scattered away.
- **Erasure error** — an error whose location is known (e.g. a heralded lost photon); easier to correct than an unknown error.
- **Bond loss / bond-loss propagation** — when a lost photon removes the entangling links it was scheduled to make, corrupting neighboring checks without a direct signature; the binding error mechanism in QS.
- **Stabilizer / syndrome** — parity checks that reveal errors without revealing the data.
- **Bit-flip (X) / phase-flip (Z)** — the two discrete error types all quantum errors are projected into.
- **Surface code** — the leading 2-D stabilizer code; data + ancilla qubits, code distance d.
- **Code distance (d)** — how much error a code absorbs; bigger d = more protection and more qubits.
- **Threshold theorem** — below a physical error threshold, enlarging the code drives logical errors arbitrarily low.
- **Foliation** — recasting repeated-in-time stabilizer rounds as stacked layers of a 3-D cluster state.
- **RHG lattice** — the 3-D cluster state realizing the surface code in MBQC; bipartite (photons/atoms) in QS hardware.
- **Transversal / fold-transversal gate** — a cheap logical gate done by local/pairwise interactions or a single re-wired layer; enabled by unrestricted connectivity.
- **Lattice surgery** — the expensive alternative for logical gates on locally-connected hardware (O(d²) ancilla, O(d) rounds).
- **Clifford+T / magic state** — the gate set for universality; the non-Clifford T gate comes from distilled magic states.
- **qLDPC codes** — efficient error-correcting codes needing long-range connectivity; QS's stated future direction.
- **Continuous-variable / GKP** — encoding qubits in a light field's quadratures; a rival photonic route (Xanadu).

---

# APPENDIX — SCRIPT ↔ GUIDE ↔ SOURCE PAPERS

| Animation scene | This guide | White paper | Blueprint |
| --- | --- | --- | --- |
| 0:00–0:20 *The Chasm* | §8–9 | Background | §I.A |
| 0:20–0:45 *The Trade-off* | §10–11, §14 | Background | §I.A |
| 0:45–1:10 *The Hybrid Breakthrough* | §17–18 | QS solution | §I.B, §II.A |
| 1:10–1:35 *The Engine (CZ Gate)* | §19–20, §24 | Entangling gate | §II.C |
| 1:35–2:00 *Scaling & Outro* | §25–26, §29–32 | Fault tolerance & MBQC | §III, §IV |

For the deeper background that won't appear literally on screen but guards against subtle errors: the bedrock (Parts I, III), the error model and bond loss (§30), the logical-gate layer (§31), and the competitive landscape (Part VII).
