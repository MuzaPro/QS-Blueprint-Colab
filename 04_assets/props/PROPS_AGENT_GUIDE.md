# Props Creation — Agent Guide

**Project:** Rice WaTER Institute — Muza Productions  
**Scope:** Creating animated and still 2D screen assets for use as Blender image planes

---

## What these assets are for

This project produces visual props for a 3D animated film being rendered in **Blender (Cycles)**. The props in `05_assets/props/` are screen displays — things like monitor readouts, data visualisations, and UI overlays — that appear as physical screens inside the 3D scene.

Each prop is authored as a self-contained **HTML file**, exported to a **JPG** (still) or **MP4** (animation), then imported into Blender as a texture on a flat plane mesh.

---

## How props are used in Blender

This is the most important thing to understand before designing any asset.

**The black background is transparent.** In Blender's material node editor, the image texture's Color output is routed through an **Emission shader** (not Principled BSDF). Black (`#000000`) registers as zero emission strength and becomes fully transparent. All non-black elements glow as self-illuminating light sources.

```
Image Texture → Emission (Strength: 5–20) → Material Output
```

Render engine: **Cycles**. Emission strength is set high (5–20+) so elements bloom and look like they are genuinely emitting light in the scene.

For animated props, Blender imports the MP4 as a video texture with **Auto Refresh** enabled so it plays in the timeline.

**Design consequences:**
- Background must always be pure `#000000` — never near-black, never `#0a0a0a`
- There is no concept of a "dark UI chrome" — anything you want visible must be clearly non-black
- Dark brand colours like `#303B61` (slate) or `#00205B` (navy) are nearly invisible on black unless used at high opacity (40%+) or replaced with lighter variants
- Glows, halos, and bloom effects look intentional and good in this workflow — lean into them
- White and light colours emit strongly; use them for text, detail lines, and accents

---

## Asset types and canvas sizes

| Type | Canvas | Format | Export tool |
|---|---|---|---|
| Still card / label | varies (set explicit width on `.card`) | JPG | `export.js` (Puppeteer) |
| Animated screen | 1280 × 720 | MP4 | `export-video.js` or `export-video-idle.js` (Playwright) |

Animated assets should always be **1280 × 720**. Stills can be any size appropriate to the prop — set an explicit pixel width on the root `.card` element.

For animated props:
- **One-shot sequences** (things that play through once): record duration = full sequence length + 1–2 s tail buffer
- **Idle loops** (background ambience): design as a mathematically seamless loop; set all oscillation periods and spawn intervals to integer divisors of the total loop duration; record exactly one loop + ~200 ms

---

## Folder structure

Each prop type lives in its own subfolder under `05_assets/props/`:

```
05_assets/
├── brand/
│   ├── font/                     ← Rice WaTER brand fonts (see below)
│   └── Rice_Owl_Flat_White.svg   ← owl watermark asset
└── props/
    └── my-new-prop/              ← one folder per prop
        ├── my-new-prop_v1.html
        ├── my-new-prop_v1.mp4
        ├── export-video.js       ← Playwright export script
        ├── package.json
        ├── AGENT_GUIDE.md        ← per-prop context file
        └── node_modules/         ← created by npm install, do not commit
```

File naming: `{prop-name}_{descriptor}_v{nn}.html / .mp4 / .jpg`

---

## Rice WaTER brand style guide

### Colour palette

These are the **only** colours to use. Do not introduce off-brand colours.

| Variable | Hex | Role |
|---|---|---|
| `green` | `#A5C151` | Hero colour — primary glowing elements, hub nodes |
| `blue` | `#0A509E` | Secondary — dependent nodes, data streams |
| `blueLt` | `#6b9fd4` | Light blue — tertiary nodes, fine detail |
| `slate` | `#303B61` | Dark background texture — **use with caution on black** (see above) |
| `slateLt` | `#4a5a8a` | Visible slate — use this for grid lines, orbit paths, chrome elements |
| `navy` | `#00205B` | Deep navy — nearly invisible on black; use for very subtle fills only |
| `deep` | `#13133E` | Deepest — essentially invisible on black; avoid |
| `greenLt` | `#c8dc8a` | Light green — glow halos, data packets, accent lines |
| `white` | `#ffffff` | White — text, fine outlines, competition edges |

**Opacity rule:** If using `slate` (`#303B61`) or any navy colour, opacity must be 40%+ to be visible. Prefer `slateLt` (`#4a5a8a`) for anything that needs to be seen at moderate opacity. For all text and important details, use `slateLt` or `white`.

### Typography

Fonts live at `../../brand/font/` relative to any file in `05_assets/props/*/`.

```css
@font-face {
  font-family: 'Cormorant Garamond';
  src: url('../../brand/font/CormorantGaramond-Italic.ttf');
  font-style: italic;
}
@font-face {
  font-family: 'Lato';
  src: url('../../brand/font/Lato-Bold.ttf');
  font-weight: 700;
}
```

- **Cormorant Garamond Italic** — species labels, system labels, academic accent text; use with generous letter-spacing (2–4px)
- **Lato Bold** — wordmarks, overlays, status readouts, UI chrome
- **monospace** (system) — sequence data, hex values, computational readouts

### Visual language — computational biology

These are the established motifs. New props should feel like they belong to the same visual family:

- **Orbital systems** — nodes orbiting a central hub on tilted ellipses (like a network topology scanner)
- **Pulse rings** — concentric circles expanding from a central node, fading as they grow
- **Drifting sequence characters** — A T G C · 32 64 128 0x4A floating slowly across the background
- **Spectral bars** — short vertical bars with oscillating heights (gene expression / signal readout)
- **Data packets** — small glowing dots travelling along paths between nodes
- **Academic chrome** — corner L-brackets, thin horizontal rules, wordmark in lower-right, italic system label near centre
- **SVG glow filters** — feGaussianBlur + feMerge halos on all primary elements; do not use CSS box-shadow

### Glow filter template

Include these in the SVG `<defs>` block and reference via `filter="url(#glow-g)"` etc.:

```html
<defs>
  <filter id="glow-g" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="10" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-gm" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-b" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-sm" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
```

### Owl watermark

The Rice Owl (`05_assets/brand/Rice_Owl_Flat_White.svg`, viewBox `0 0 176.54 210.52`) should appear in the bottom-right corner of screen props where appropriate.

**Critical:** render the owl paths with `fill:none; stroke:#ffffff` — NOT `fill:#ffffff`. The SVG contains multiple subpaths per element; fill collapses them into a flat silhouette. Stroke rendering exposes all the internal feather and detail lines, which is the correct look for an emission shader.

```javascript
// embed as a nested <svg> element
const owlSvg = mk("svg", {
  x: W - 110, y: H - 125,
  width: 88, height: 105,
  viewBox: "0 0 176.54 210.52",
  opacity: "0.42",
  filter: "url(#glow-sm)",
}, staticLayer);

[OWL_BODY, OWL_EYE_L, OWL_EYE_R].forEach(d => {
  mk("path", {
    d, fill: "none",
    stroke: "#ffffff", "stroke-width": "3",
    "stroke-linejoin": "round", "stroke-linecap": "round",
    transform: "translate(-69.99 -56.92)",
  }, owlSvg);
});
```

The three path `d` strings can be copied from `05_assets/brand/Rice_Owl_Flat_White.svg`.

---

## HTML animation architecture

All animated props use the same structure:

```html
<!DOCTYPE html>
<html>
<head>
  <!-- @font-face declarations -->
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#000; width:1280px; height:720px; overflow:hidden; }
  </style>
</head>
<body>
<svg id="stage" width="1280" height="720" style="display:block;background:#000">
  <defs><!-- glow filters --></defs>
  <!-- named layer groups, back to front -->
  <g id="bg-layer"></g>
  <g id="anim-layer"></g>
  <g id="chrome-layer"></g>
</svg>
<script>
  // all animation logic here
</script>
</body>
</html>
```

### Animation rules

- **Use `requestAnimationFrame` exclusively.** No CSS animation, no `setInterval`. All motion is driven by `performance.now()` in the rAF callback.
- **Never use IIFEs inside animation functions.** Define a named function `f(t)` and call `requestAnimationFrame(f)`. Do not both call a function immediately AND register it with rAF — this creates doubled animation.
- **For one-shot sequences** (fire-and-forget events at specific times), use a `setTimeout` registry:
  ```javascript
  const _timers = [];
  function after(ms, fn) { _timers.push(setTimeout(fn, ms)); }
  function killAll() { _timers.forEach(clearTimeout); _timers.length = 0; }
  // allow replay on click:
  document.getElementById("stage").addEventListener("click", () => { killAll(); init(); });
  ```
- **For seamless loops**, make every oscillation period and spawn interval an integer divisor of `LOOP_MS`. Drift character speeds should equal `H_WRAP / (LOOP_MS * n)` where n is a positive integer.
- **Helper function** for creating SVG elements:
  ```javascript
  const NS = "http://www.w3.org/2000/svg";
  function mk(tag, attrs, parent) {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
    if (parent) parent.appendChild(el);
    return el;
  }
  ```
- **Easing functions** used in this project:
  ```javascript
  const easeOut3  = t => 1 - (1 - t) ** 3;
  const easeIn3   = t => t ** 3;
  const easeInOut = t => -(Math.cos(Math.PI * t) - 1) / 2;
  const easeBack  = t => 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2;
  ```

---

## Export scripts

Every animated prop folder needs two files: `export-video.js` and `package.json`.

### package.json

```json
{
  "type": "module",
  "devDependencies": {
    "playwright": "^1.44.0",
    "puppeteer": "^22.0.0"
  }
}
```

`"type": "module"` is required for ES module syntax (`import`/`export`). After creating this file, the user runs `npm install` and `npx playwright install chromium` once from inside the folder.

### export-video.js — template

Copy and adapt from `bacterial_network_bioinformatics/export-video.js`. The key sections are:

1. **Config block** — set `STEM` (filename base), `RECORD_MS` (how long to record), and `W`/`H` (canvas size)
2. **Playwright launch** — `chromium.launch()` with `recordVideo` context option
3. **Navigation** — `page.goto(`file:///${INPUT.replace(/\\/g, "/")}`)` — forward slashes required on all platforms
4. **Wait** — `page.waitForLoadState("networkidle")` for fonts, then `page.waitForTimeout(RECORD_MS)`
5. **Finalise** — grab `page.video()` reference, close page/context/browser, then `await video.path()`
6. **ffmpeg conversion** — `spawnSync("ffmpeg", ["-y", "-i", webmPath, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4Path])` — delete WebM on success, keep and warn on failure

See `bacterial_network_bioinformatics/export-video.js` for the complete working implementation.

---

## Existing assets — reference implementations

| File | What it demonstrates |
|---|---|
| `bacterial_network_bioinformatics/phage-network-anim-v4-rice.html` | One-shot narrative sequence: network build → hub recognition → destruction → collapse. setTimeout registry, text overlays, particle explosions. |
| `bacterial_network_bioinformatics/biofilm-idle-v1-rice.html` | Seamless idle loop: orbital satellites, pulse rings, drifting sequence chars, spectral bars, data packets. All periods divide LOOP_MS = 12 000. |

When creating a new prop, read the most relevant existing asset first to understand the established code patterns before writing new code.

---

## Checklist before delivering a new prop

- [ ] Background is pure `#000000` — verified in browser
- [ ] All visible elements use brand palette colours only
- [ ] Dark slate colours (`#303B61`, `#00205B`) are at 40%+ opacity OR replaced with `#4a5a8a`/`#ffffff`
- [ ] Fonts load correctly from `../../brand/font/` relative paths
- [ ] No CSS animation — only `requestAnimationFrame`
- [ ] No duplicate rAF calls (no IIFE + rAF on the same function)
- [ ] For loops: all periods are integer divisors of `LOOP_MS`
- [ ] `export-video.js` and `package.json` are present in the folder
- [ ] HTML file is self-contained (no external CDN dependencies — fonts and owl are local)
- [ ] File is saved to `05_assets/props/{prop-name}/` following naming convention
