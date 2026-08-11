# PSP-001 — Refactor & Expansion Brief

**Rev 2.0** — supersedes Rev 1.0. Changes: content expansion is now in scope (§9), and it is what drives the reuse architecture rather than competing with it.

**Target:** move `perspective-datasheet.html` into the `3L-refs` Hugo site as a generated, tested, themed document — expand it past pure perspective — and fall out of it with a reusable figure-rendering library.

**Input artifact:** the single-file `perspective-datasheet.html`. Read it first, in full. It is correct and it works; this is a refactor, not a rewrite.

---

## 0. Read before starting

1. `perspective-datasheet.html` — the current artifact.
2. ~~Its `:root` block — **that is the palette.**~~ **SUPERSEDED by plan D17** — the
   palette now comes from the 3L design system (`github.com/mjrskiles/3L-design`),
   vendored into `assets/css/ds/`. "Do not invent new hues" still holds; the set of
   legitimate hues just moved. Original text: Its `:root` block — that is the palette. The site is greenfield and all-light, so there is no existing theme to pull tokens from and nothing to reconcile against. Lift the light token set from the artifact (`--paper`, `--plate`, `--ink`, `--graphite`, `--mars`, `--con`, …) and map it to the L2 roles in §4. You are the source of truth for it. Do not invent new hues.
3. §11 of the artifact — the caveats section already flags what's uncertain.

---

## 1. Goals

1. **No hardcoded geometry.** Every coordinate in every figure is currently a constant computed by hand. Replace with real math, executed at build time. Accept build/CI complexity to get this.
2. **Modular figure rendering.** The scene and render layers must be domain-agnostic — reusable for an audio/DSP version of this document with zero changes.
3. **Expand past perspective** into edges, notan, gestalt, and eye path (§9). The document currently covers geometry and calls itself a drawing reference; that's a gap.
4. **Coherent light theming**, subject to hard readability floors (§8).
5. **Prose register:** approachable technical reference. Textbook, not essay (§7).

## 2. Non-goals

- Do not re-derive the existing math. It's verified — the fence-post construction, the armature eye formula, the inscribed-conic center, and the 3-point orthocenter relation were each checked numerically before they were drawn. Port them; don't rediscover them.
- Do not restructure the existing section order beyond the insertions specified in §9.4.
- Do not build a label auto-placement solver.
- **Do not build a saliency model.** The eye-path section is a schematic and a reuse of the armature spiral. Predicting gaze is a research project, not a section.
- Do not attempt to synthesize convincing hatched ink from a lighting model. The edge section is a value-profile argument, not a renderer.

---

## 3. Decision required up front: kernel language

The interactive figures (the lens slider in Fig. 1, the armature calculator) run math in the browser. The static figures run the same math at build time. **These must not be two implementations** — that's how the document silently goes wrong.

### Path A — TypeScript kernel (recommended)

One module, executed under Node at build time to emit SVG, and shipped to the browser for the interactive figures. Same code, provably.

- Toolchain stays small: `typescript`, `esbuild` or `tsx`, `vitest`, `fast-check`. No framework, no bundler config beyond a few lines.
- **Cost: npm.** Mitigate — pin exact versions, commit the lockfile, `npm ci` in CI, direct deps ≤ 6, `--ignore-scripts`.

### Path B — Python kernel + pre-rendered frames

Kernel in Python (`pytest`, `hypothesis`), SVG emitted at build time. For the lens demo, **pre-render ~30 frames** across `d ∈ [2.5, 15]` and have the slider swap between them. Zero browser math, one source of truth, no npm.

- The armature calculator survives this: `p²/(p²+q²)` is ten lines of JS and needs no kernel.
- Cost: ~60KB of frames, and continuous parameters become discrete.

**Recommendation: A**, because PSP-002 will want live parameter sweeps (cutoff, Q) where pre-rendering gets ugly. B is a real contender and the frame trick is legitimate.

Everything below is path-agnostic.

---

## 4. Architecture

```
L0  constants/     Single-source physical constants. No magic numbers anywhere else.
L1  kernel/        Domain math. Pure functions. No I/O, no SVG, no styling.
L2  scene/         Declarative figure description. Domain-agnostic.
L3  render/        Scene → SVG. Domain-agnostic.
L4  figures/       Document-specific compositions built on L1–L3.
L5  hugo/          Shortcodes, partials, layouts, data.
```

### L0 — constants

The current file hardcodes `0.58` and `1.72`. These are `tan(30°) = 0.5774` and `cot(30°) = 1.7321`, both falling out of the 60° cone — and they're rounded inconsistently (`1/0.58 = 1.724`, not `1.72`).

```
CONE_HALF_ANGLE = 30°                       // the only input
CONE_RATIO      = tan(CONE_HALF_ANGLE)      // R ≤ CONE_RATIO · d
MIN_DIST_RATIO  = cot(CONE_HALF_ANGLE)      // d ≥ MIN_DIST_RATIO · R
```

Every appearance of 0.58 or 1.72 — figures, tables, prose — resolves to these. Template for the whole refactor.

### L1 — kernel

Pure, testable, **works in drawing inches, not pixels.** CV is the origin. The renderer applies scale and translation; the kernel never knows about a viewBox.

**`kernel/perspective/`**

| Module | Provides |
|---|---|
| `project` | Point/direction projection, `vp(direction, d)`, image coords from `(X, Y, Z)` |
| `cone` | `coneRadius(d)`, `minDistance(R)`, `extent(points)`, `withinCone(points, d)` |
| `twoPoint` | VP positions from `(d, azimuth)`; `d = √(ab)` inverse |
| `threePoint` | VPs from `(d, tilt, azimuth)`; orthocenter; `d² = \|HV\|·\|Hfoot\|` check |
| `depth` | Fence-post construction; rail intersection; tile grid |
| `ellipse` | Perspective square → true center; inscribed conic; 8-point set; minor-axis-from-revolution-axis |
| `shadow` | Light VP / shadow VP; shadow tip from base + top |
| `incline` | `h = \|SP→V\| · tan θ`; stacked VP |
| `armature` | Eyes (formula **and** perpendicular-foot construction — both, so tests compare them); reciprocals; rabatment; nesting sequence; spiral pole |

**`kernel/tone/`** — new, drives §9

| Module | Provides |
|---|---|
| `edge` | `profile(width, amplitude) → value curve`; sweep a profile along a contour |
| `notan` | `quantize(valueField, levels)` |

Gestalt needs **no kernel** — it's parametric figure composition only. That's the point; see §5.2.

### L2 — scene (domain-agnostic)

Primitives carry **semantic roles, never colors**:

```ts
type Role =
  | 'field'         // ambient reference: horizon, ground, plate border, axes
  | 'given'         // what the reader is handed
  | 'construction'  // scaffolding that produces the result
  | 'derived'       // what the construction produced
  | 'subject'       // the thing being drawn
  | 'hidden'        // occluded edges
  | 'ghost'         // de-emphasized / sight lines
  | 'annotation'    // labels, dimensions, callouts

type Prim =
  | { k: 'seg';     a: Pt; b: Pt; role: Role }
  | { k: 'poly';    pts: Pt[]; role: Role; close?: boolean; fill?: boolean }
  | { k: 'circle';  c: Pt; r: number; role: Role; fill?: boolean }
  | { k: 'ellipse'; c: Pt; rx: number; ry: number; rot: number; role: Role }
  | { k: 'marker';  at: Pt; kind: 'vp'|'point'|'cross'|'foot'; role: Role }
  | { k: 'label';   at: Pt; text: string; role: Role;
                    anchor?: 'start'|'middle'|'end'; dx?: number; dy?: number }
  // --- new in Rev 2.0, see §9.1 ---
  | { k: 'plot';    axes: Axes; series: Series[]; role: Role }
  | { k: 'node';    at: Pt; label: string; shape: 'box'|'round'; role: Role }
  | { k: 'link';    from: NodeRef; to: NodeRef; role: Role; arrow?: boolean }

type Scene = {
  prims: Prim[]
  frame: { mode: 'fit'; pad: number } | { mode: 'fixed'; rect: Rect }
  scale: number   // px per drawing inch
  clip?: boolean
}
```

`frame: 'fit'` computes the bbox from the primitives — this kills the bug where Fig. 1's `d = 16` preset is disabled because the slider caps at 15 for viewBox reasons. **Interactive figures use `frame: 'fixed'`**, rect computed once at the extreme parameter, or the frame jitters while dragging.

### L3 — render (domain-agnostic)

`Scene → SVG string`. One CSS class per role. Applies scale and origin. Handles clipping and `aria-label` generation.

Knows nothing about perspective, nothing about tone, nothing about color — it emits `class="r-construction"` and the stylesheet decides what that means.

### L4 — figures

`figures/lensCube`, `figures/fencePosts`, `figures/armature`, `figures/edgeProfiles`, `figures/gestalt/*`, `figures/elementsGraph`, … Each maps parameters → `Scene`. Each is a thin composition of L1 + L2. **If a figure function is long, math has leaked into it** — push it down to L1.

### L5 — Hugo

- Generator writes `layouts/partials/psp/figures/*.svg` and `data/psp/computed.json`.
- **Commit the generated SVGs.** Reviewable in PRs; figure diffs are exactly what you want to see. CI enforces currency (§11).
- `{{< psp-fig "lensCube" >}}` inlines the partial with its caption.
- `{{< v "drills.D1.diagonalVP" >}}` inlines a computed number into prose.

---

## 5. The reusability constraint

### 5.1 Import boundary

> **`scene/` and `render/` must import nothing from `kernel/` or `constants/`.**

Enforce mechanically — eslint `no-restricted-imports`, `dependency-cruiser`, or a ten-line import-graph walk. Not a convention; a failing build.

### 5.2 Proof of reuse — now in-domain

Rev 1.0 made this speculative: build one audio figure and hope the abstraction held. **Rev 2.0 makes it concrete, because the new content needs the same two capabilities PSP-002 needs most:**

| Capability | Forced by (PSP-001) | Needed by (PSP-002) |
|---|---|---|
| **Plot** — axes, ticks, plotted function | Edge value-profile figure (§9.2) | Bode magnitude/phase, spectra, envelopes |
| **Graph** — nodes, links, layout | Elements-dependency figure (§9.5) | Block diagrams, signal-flow graphs |

So the plot and graph primitives get built, used, and tested **inside this document** rather than speculated about for the next one. That is a much stronger position than Rev 1.0 was in.

Acceptance (§13) requires the edge-profile figure and a Bode plot to share the same plot code, and the elements graph and a block diagram to share the same link code.

**Still ship the audio smoke test** in `examples/` — one Bode plot and one two-block diagram. If either needs a change to `scene/` or `render/`, the abstraction is wrong. Fix it before shipping.

### 5.3 Gestalt as the purity test

The gestalt figures (§9.3) are **parametric dot arrays with no kernel at all** — pure L2/L3. That makes them the best available proof that the scene layer isn't secretly shaped around perspective drawings.

**Port one gestalt figure in P2, before any perspective figure.** If the scene DSL can't express a proximity grid cleanly, it's wrong, and you want to know that before porting ten figures onto it.

### 5.4 Labels

Manual `dx`/`dy` offsets are fine, but anchored to a **computed point**, never an absolute coordinate. `{ at: vpRight, dx: 8, dy: -6 }` survives a geometry change; `x="612" y="50"` does not.

### 5.5 Document shell + tiers

Promote the masthead, title block, TOC, section chrome, parameter tables, and callouts into a **Hugo layout + archetype**, so `hugo new psp/002-filter-design.md` inherits the format.

**The tier taxonomy (§9.1) lives in the shell, not in the perspective content.** PSP-002 has the identical split — filter math is determined, "does this patch sound good" isn't. Every document of this type needs it.

---

## 6. Data extraction inventory

| Now | After |
|---|---|
| All SVG coordinates | Computed by L1, emitted by L3 |
| `0.58`, `1.72` | Derived from `CONE_HALF_ANGLE` |
| Table 1 (parameters) | `data/psp/parameters.yaml` |
| Table 2 (media tests) | `data/psp/media-tests.yaml` |
| Table 3 (drills) | `data/psp/drills.yaml` |
| Table 4 (D2 angles) | **Computed from the D2 drill spec.** Not typed. |
| Caption numbers (`15.6 apart`, `34.4`/`65.6`, `86.6`, `65.5`) | `{{< v >}}` against `computed.json` |
| Prose numbers (`4/13`, `9/13`, `0.62″`, `32° versus 9°`, `8.66 × 2.89 = 25.0`) | Same |
| Figure numbers (`Fig. 7`) | Auto-numbered from document order |

New data files for §9:

- `data/psp/tiers.yaml` — tier definitions and descriptions
- `data/psp/edges.yaml` — the four edge types as `(width, amplitude)` pairs
- `data/psp/gestalt.yaml` — five principles + figure parameters
- `data/psp/elements-graph.yaml` — nodes and links for the critique figure

Drill spec shape — everything else is derived:

```yaml
- id: D1
  title: Corridor
  plate: { w: 10, h: 8 }
  d: 7
  vp: { x: 2.5, y: 3.5 }
  teaches: >
    Depth rate. Angles are free in 1-point; the foreshortening rate is the whole test.
  pass: >
    Tile diagonals collinear across three tiles under a straightedge.
```

From that, compute: the 45° diagonal VP position, whether it lands on the plate, the cone radius, and the on-plate/off-plate flags.

---

## 7. Prose register

Target: **approachable technical reference.** Keep the directness and the honesty about failure modes. Lose the essay rhythm and the winking.

1. **en-US throughout.** The current file mixes `centre` and `characterization`. Fix.
2. **Per-concept structure:** state the rule → give the derivation → name the failure mode → give the pass criterion.
3. **Define each term once**, at first use. Glossary in `data/psp/glossary.yaml`.
4. **Cut rhetorical setup.** "Here's the thing", "Now you can see the trick", "This is the part that breaks people", "Underrated, and".
5. **Second person for procedures, not for claims.** "Drop a perpendicular onto the diagonal" — yes. "You're positioning a skull" — no.
6. **Captions state what the figure shows and what to take from it.** No zingers.
7. **Every number in prose traces to a formula in the document.**

### Register examples

> **Before:** "This is the part that breaks people's intuition. Stand up: it rises. Sit: it drops. Walk toward it and *nothing happens*."
>
> **After:** "The horizon's height tracks eye height and nothing else — it rises when you stand and drops when you sit. It has no distance: walking toward it changes nothing, because it lies at infinity."

> **Before:** "Everyone gets this wrong forever."
>
> **After:** "Any construction that treats the ellipse's center as the circle's center inherits this error."

Concreteness stays. Performance goes.

---

## 8. Theming — constraints, not colors

~~Take the light tokens from the artifact's `:root` block (§0.2).~~ **SUPERSEDED by plan D17** — tokens come from the vendored 3L design system (`assets/css/ds/tokens.css`), and its floors (prose ≥4.5:1, large ≥3:1) govern instead of the AAA numbers below. Map them to L2 roles. **The role → token map is the only place color appears** — now CI-enforced by `tools/check_hexes.py`. The grayscale test below is unchanged and is what made this swap cheap.

### Hard floors

- Body text vs. page: **≥ 7:1** (WCAG AAA).
- `subject`, `given`, `derived` strokes vs. figure background: **≥ 4.5:1**.
- `construction`, `ghost`: **≥ 3:1**.
- In-figure labels: **≥ 4.5:1**.
- **CI contrast check.** WCAG relative-luminance math is ~20 lines; no dependency needed.

### The grayscale test

> Roles must be distinguishable **without color** — stroke weight and dash pattern alone.

Print a figure in grayscale. If construction isn't distinguishable from subject, it fails regardless of contrast numbers. Buys accessibility, print fidelity, and freedom to change the palette later — because color becomes redundant rather than load-bearing.

**Note for §9.2:** the edge-profile figures are *about* value. They must not rely on hue at all; they're the strictest case of this rule in the document.

### Additional

- **At most two accent hues in figures.**
- If a role has no token equivalent, **derive** it (desaturate/lighten an existing token). Don't import a foreign hue.
- Readability wins every conflict with brand.

### Fonts

Drop the Google Fonts link. IBM Plex is OFL — self-host. Subset with `pyftsubset`/`glyphhanger`; 150–250KB across four families. Add a CI check that the built HTML references **no external origins** — grep `<link>`, `<script>`, `@import` in `public/`.

---

## 9. Content expansion — NEW IN REV 2.0

The document currently covers perspective geometry and calls itself a drawing reference. It isn't one yet. This section closes that, and — see §5.2 — it's what makes the reuse architecture real rather than speculative.

### 9.1 Tier metadata (shell-level)

The document currently presents everything with the same certainty. It shouldn't. Add a tier to every section's frontmatter, rendered as a marker in the section head:

| Tier | Meaning | In PSP-001 |
|---|---|---|
| **T1 — Determined** | Provably right or wrong | Perspective geometry, optics, gestalt grouping, armature *construction* |
| **T2 — Craft** | Strong heuristics, no proofs | Composition, notan, edges, eye path, armature *application* |
| **T3 — Undetermined** | Neither | What the piece is about; whether it's any good |

Notes:

- **Armature spans tiers.** The construction is T1 — the eye is at `p²/(p²+q²)`, provably. Whether to place anything there is T2, which is exactly why the Hambidge caveat exists. If the tier system can't express that, it's too coarse.
- The document is currently ~all T1 with a little T2 hiding inside the media-characterization section. Making it explicit is honest and it's a forcing function: **if you can't assign a tier, the section isn't clear about what it's claiming.**
- Lives in the shell (§5.5). PSP-002 inherits it unchanged.

### 9.2 New section — Edges (T2 with a T1 core)

Not on any standard elements list, and arguably more powerful than value. This is the highest-value addition in the expansion.

**The core claim, which is T1 and precise:**

> An edge is a value transition across a boundary. It has exactly two parameters: **transition width** and **transition amplitude**.

| Traditional name | Width | Amplitude |
|---|---|---|
| Hard | → 0 (step) | full |
| Firm | narrow ramp | full |
| Soft | wide ramp | full |
| Lost | any | → 0 |

That turns four vocabulary words into a two-parameter space, exactly. It also means **an edge is a step response, and hardness is bandwidth** — a soft edge is a low-pass-filtered step.

**This is the strongest cross-document tie in the whole project.** The same math is PSP-002's §on filter response. Build it deliberately: `kernel/tone/edge` should be shaped so the DSP document can import the concept, not just the code.

**Figure — edge taxonomy.** For each of the four types: the value profile across the boundary plotted as a curve, beside the rendered edge. Forces the `plot` primitive (§5.2). Fully computable — the profile is a parameterized ramp/sigmoid, the edge is that profile swept along a contour.

**Prose to carry:**
- The eye goes to the hardest edge at the highest contrast, first, every time. That's the control mechanism, and it's why edge is more actionable than value.
- Lost edges are how peripheral vision is rendered, and peripheral vision is most of an actual visual field.
- **Ink is hard-edged by default.** Every mark is a step. Soft and lost have to be manufactured — density gradients, broken contour, hatching dissolved at the boundary. Colored pencil gives them cheaply. This is a *characterization* item, not a computable one: it goes in the media section as a swatch test.

### 9.3 New section — Gestalt grouping (T1)

Proximity, similarity, closure, continuity, prägnanz. The actual perceptual mechanism sitting under the traditional "unity" and "pattern" principles. Mechanisms, not heuristics — which is why this is T1 and belongs with the geometry.

**Figures:** one parametric array per principle. Dot grids with varying spacing, varying fill, interrupted contours. **No kernel required** — see §5.3, these are the domain-agnostic purity test and get ported first.

### 9.4 New section — Notan (T2), and Eye path (T2)

**Notan** — the dark-light pattern read as abstract design, independent of subject. Currently a one-line afterthought at the end of the media section. Promote it to its own section.

Figure: the same composition at 2, 3, 4, and continuous values, generated by quantizing an assigned-value shape scene. `kernel/tone/notan`. Fully computable.

**Eye path** — a static image is experienced in time: entry, path, rest points, exit. Only weakly captured by the traditional "movement" principle.

Figure: **reuse the log spiral from the armature nesting sequence.** Same kernel function, framed as a candidate path rather than a construction artifact. That reuse is the section's whole argument — the armature already generates a closed path, so the geometry and the composition are the same object seen twice. No new kernel. No saliency model (§2).

### 9.5 Caveats addition — the elements-and-principles critique

The canonical list (line, shape, form, value, color, texture, space / balance, contrast, emphasis, movement, rhythm, pattern, proportion, unity) is a **teaching scaffold, not a theory**. Lineage: Dow's *Composition* (1899, three elements: line, notan, color) → Bauhaus systematization → mid-century US school curricula. No single agreed list exists; textbooks differ.

It doesn't factor, and the document should say so plainly:

- Value and color aren't independent — two projections of one 3D space (hue/value/chroma).
- Shape and space are figure/ground: one operation, two names.
- Form is shape + value. Not primitive.
- Texture becomes value at viewing distance — so the element depends on a parameter absent from the model.
- Line is a convention, not a perceptual primitive.

**Figure — dependency graph.** Nodes for each element, links showing which are primitive and which are compositions. Forces the `node`/`link` primitives (§5.2).

Frame it fairly: useful vocabulary, tier-two, wearing a tier-one costume. Handy for naming a problem ("the value structure is fine, the edges are all the same"); useless for generating anything.

### 9.6 Resulting section order

```
 1  Key parameters
 2  Vanishing points            T1
 3  The horizon                 T1
 4  Inclined planes             T1
 5  Depth spacing               T1
 6  Circles & ellipses          T1
 7  Cast shadows                T1
 8  Gestalt grouping            T1   ← new
 9  Armature                    T1 construction / T2 application
10  Notan                       T2   ← promoted
11  Edges                       T2   ← new
12  Eye path                    T2   ← new
13  Media characterization      T2
14  Drills
15  Caveats (+ elements critique)
```

Rationale: tier order is the spine. Gestalt sits between the geometry and the composition sections because it's the T1 perceptual basis for the T2 material that follows — it's the bridge from determined to craft.

---

## 10. Testing

The tests are the actual deliverable. The current document is correct because it was checked by hand; the refactored one should be correct because CI says so.

### Property tests

| Invariant | Test |
|---|---|
| 2-point | ∀ `d ∈ [1,100]`, `α ∈ (0°,90°)`: assert `\|d − √(a·b)\| < ε` |
| 3-point | ∀ `d`, `φ ∈ (0°,60°)`, `α`: orthocenter ≈ CV, and `d² ≈ \|HV\|·\|Hfoot\|` |
| Fence-post | Generate N posts by construction → invert image x to depth via `x = x_v − K/z` → assert `Δz` constant within ε |
| Ellipse | Perspective center ≠ ellipse center for any non-degenerate square; tangent slope at the side-tangent point ≈ the side's slope |
| Armature | ∀ `p,q > 0`: eye from the closed form ≈ eye from the perpendicular-foot construction |
| Nesting | ∀ `p,q`, ∀ `n ≤ 12`: `R_n` contains the pole; proportion alternates |
| Cone | `extent/d ≈ tan(CONE_HALF_ANGLE)` at the boundary |
| **Edge** | `profile(width→0)` → step; `profile(amplitude→0)` → constant; profile is monotone across the transition for all params |
| **Notan** | `quantize(field, n)` yields exactly ≤ n distinct values; ordering preserved; `quantize(field, ∞) ≈ field` |

The fence-post and armature tests remain the two that matter most — both were hand-verified once and would silently rot otherwise.

### Other

- **Snapshot tests** on each figure's SVG. Regenerate behind a flag.
- **Contrast test** over the role → token map.
- **Import-boundary test** (§5.1).
- **Shared-primitive tests:** edge-profile figure and the example Bode plot resolve to the same plot code path; elements graph and the example block diagram resolve to the same link code path.
- **Drift check:** `git diff --exit-code` after regenerating figures.

---

## 11. Build & CI

```
build:figures   → layouts/partials/psp/figures/*.svg + data/psp/computed.json
test            → unit + property + snapshot + contrast + boundary
build           → hugo --minify
```

Action: setup runtime → `test` → `build:figures` → `git diff --exit-code` → setup Hugo → `build` → check no external origins in `public/` → deploy Pages.

---

## 12. Known defects in the current file

1. **Mixed en-GB/en-US spelling.** `centre` throughout the figures; `characterization` in §9.
2. **`0.58` / `1.72` rounded inconsistently** and not derived. See §4/L0.
3. **Fig. 1's `d = 16` preset is disabled** because the slider caps at 15 to fit the viewBox. `frame: 'fit'` removes the constraint.
4. **Fig. 7 left panel is parallel projection, not perspective.** The cylinder's silhouette lines are tangent at the ellipses' major-axis endpoints, exact only in parallel projection. Draw it properly or say it's a schematic. Currently it says neither.
5. **Fig. 3's figures are hand-tuned.** Head offset uses `0.06h` rather than the 5.66% falling out of the 5'6" eye / 5'10" figure ratio. Derive it.
6. **Fig. 5's `θ` is ambiguous to a reader.** The caption warns θ is the real incline, not the on-paper angle; a small plan inset would carry it better.
7. **Interactive SVG `aria-label` is static** — doesn't update as `d` changes.
8. **Figure numbers are manual.**
9. **Google Fonts** external dependency.
10. **Armature calculator's fraction reduction** produces ugly output for large integer inputs.
11. **Notan is buried** as a one-liner at the end of §9 despite being a T2 headline. Fixed by §9.4.

---

## 13. Phasing

Correctness first, appearance last. Each phase ends green.

| Phase | Work | Done when |
|---|---|---|
| P0 | Scaffolding, self-hosted fonts, defects triaged | No visual change; build passes |
| P1 | L0 + L1 perspective kernel + tests | Tests green; nothing rendered |
| P2 | L2 + L3 + role map, current colors. **Port one gestalt figure first** (§5.3) | Scene layer proven domain-agnostic before any perspective figure |
| P3 | Port existing 10 figures, snapshot-diff each | All render from math |
| P4 | Interactive figures onto the shared kernel | Fig. 1 + calculator use L1 |
| P5 | **`plot` + `link` primitives**, driven by edge-profile and elements-graph | Both live in `scene/`, not `figures/` |
| P6 | `kernel/tone/` + new content sections + tier metadata | §9 complete |
| P7 | Hugo integration, data extraction, `{{< v >}}` | No literal numbers in content |
| P8 | Light theme finalize | Contrast + grayscale pass |
| P9 | Prose pass (§7) | — can run parallel with P2–P8 |
| P10 | Audio smoke test + document archetype | `scene/`+`render/` untouched by it |

---

## 14. Acceptance criteria

- [ ] No coordinate literal in any figure source.
- [ ] `0.58` and `1.72` appear nowhere; both derive from `CONE_HALF_ANGLE`.
- [ ] `scene/` and `render/` import nothing domain-specific; enforced by a failing test.
- [ ] Gestalt figures import no kernel at all.
- [ ] `plot` and `link` live in `scene/`/`render/`, not `figures/`.
- [ ] **The edge-profile figure and a Bode plot share the same plot code.**
- [ ] **The elements graph and a block diagram share the same link code.**
- [ ] Every property test in §10 passes, including fence-post depth-inversion, armature dual-derivation, and the edge/notan invariants.
- [ ] Every section carries a tier; tier lives in the shell, not the content.
- [ ] All prose and caption numbers resolve from `computed.json`.
- [ ] Contrast floors met; figures legible in grayscale; edge figures use no hue.
- [ ] No external origins in the built output.
- [ ] Regenerating figures produces no git diff.
- [ ] en-US throughout.
- [ ] Document shell is a reusable Hugo layout + archetype.

---

## 15. Later

- **PSP-002, audio/DSP.** `kernel/dsp/`: transfer functions, pole-zero, filter topologies, envelopes. Figures: Bode, pole-zero, block diagram, signal-flow graph, ADSR, spectrum, waveform. Everything from L2 up is shared — and after this pass, the plot and graph primitives are already proven.
- **PSP-001 further expansion:** atmospheric perspective, reflection geometry, curvilinear/fisheye projection, the measuring-point method, color as a 3D space (hue/value/chroma) done properly.
- **Media characterization** stays uncharacterized until the swatches exist. Leave the status line honest.
