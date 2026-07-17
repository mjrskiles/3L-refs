# sbl-refs — Agent Handoff & Execution Plan

**Read this first. It is self-contained: it assumes no prior conversation.**

You are picking up a greenfield project. This directory (`sbl-refs/`) is the seed
for a new repository, `soundbytelabs/sbl-refs`, which will host **`refs.soundbytelabs.net`**
— Sound Byte Labs' static reference/datasheet site. Its first and only initial
tenant is **PSP-001**, a "Perspective & Composition" working datasheet that is being
refactored from a single hand-authored HTML file into a generated, tested, themed
Hugo document.

This project was split out of the `soundbytelabs/blog` repo after an evaluation.
The blog stays where it is (its own repo, `blog.soundbytelabs.net`, dark theme);
`sbl-refs` is a **separate, independent repo and subdomain**, built light.

---

## 1. Inputs (both in this seed)

| File | What it is | How to treat it |
|------|-----------|-----------------|
| `source/perspective-datasheet.html` | The current single-file artifact. ~1080 lines, self-contained, correct, and working. | **Read it in full first.** This is a *refactor*, not a rewrite. Its math is hand-verified. Port it; do not re-derive it. |
| `docs/PSP-001-brief.md` | The refactor brief (Rev 2.0). Defines the target architecture, content expansion, testing, theming, phasing, and acceptance criteria. | Your spec. Follow it **as amended by §3 of this handoff** — several of its assumptions came from the old blog repo and do not apply here. |

---

## 2. Locked decisions (do not re-litigate)

These were decided during the evaluation. They override anything in the brief that
conflicts.

1. **All light.** The site is built on the datasheet's light "engineering-paper"
   palette from the start. There is no dark theme to reconcile — `sbl-refs` is
   greenfield. The light tokens are already in `source/perspective-datasheet.html`
   (`:root` block: `--paper:#EAEBE6`, `--plate:#F4F5F1`, `--ink:#14171A`,
   `--graphite:#5F6469`, `--mars:#1B4B8F`, `--con:#B23A2B`, etc.). These become the
   single source of color, mapped to the brief's L2 semantic roles. Color appears
   nowhere else. Honor the brief's §8 contrast floors and grayscale test.

2. **Kernel language: Path B (Python), not TypeScript.** The brief recommends Path A
   (a TS kernel shared with the browser). We chose **Path B**: the figure math is a
   Python package (`pytest` + `hypothesis`), executed at build time to emit SVG.
   - The Fig. 1 lens slider is served as **~30 pre-rendered SVG frames** across
     `d ∈ [2.5, 15]`; the slider swaps between them. No browser math for it.
   - The armature calculator (§8 of the datasheet) stays as its existing ~10 lines of
     inline JS — it needs no kernel.
   - **Rationale:** keeps the repo npm-free. There is no committed follow-on document
     that needs live parameter sweeps, so Path A's main advantage doesn't apply yet.

3. **Self-host, don't ban (no external runtime origins).** The built site must load
   nothing from a third-party origin.
   - **Fonts:** self-host and subset IBM Plex (it's OFL). The datasheet currently
     pulls it from Google Fonts — drop that `<link>`.
   - **Mermaid** (if any diagrams are used): vendor `mermaid.min.js` as a static
     asset; do not use a CDN. (Mermaid may not be needed for PSP-001 at all.)
   - Enforce with a CI check that greps the built `public/` for external origins in
     `<link>`, `<script>`, `@import`, and `src=`/`href=` to other hosts.

4. **Single Hugo site, bespoke light theme.** `sbl-refs` is one Hugo site at
   `baseURL = https://refs.soundbytelabs.net/`. It does **not** use the `terminal`
   theme (that's a blog theme; this is a datasheet site). Build a minimal custom
   light layout — no theme submodule.

5. **Hosting: GitHub Pages, one repo → one domain.** `sbl-refs` deploys to its own
   Pages site with `CNAME = refs.soundbytelabs.net`. Nothing is shared with the blog
   repo.

---

## 3. Amendments to the brief (it was written against the old blog repo)

The brief's §0/§8 tell you to "find the real palette tokens in the repo
(`assets/css/`, `data/`, theme config)." That instruction described the old blog
repo and is void here. Corrections:

- **There is no existing theme to pull tokens from.** Define the light token set from
  the datasheet's `:root` block (see decision 1). You are the source of truth.
- **Ignore the brief's dark-vs-light reconciliation concerns.** Greenfield + all-light
  removes them.
- **Path A specifics in the brief** (TypeScript, esbuild/tsx, vitest, fast-check,
  `--ignore-scripts`, the shared browser/build kernel) are **superseded by Path B**
  (Python, `pytest`, `hypothesis`, pre-rendered frames). Everything the brief says
  above the kernel language — the L0–L5 layering, the reuse constraints, the scene/
  render import boundary, the testing *invariants*, the phasing — still applies.
- **The brief's "audio smoke test" / PSP-002 reuse proof (§5.2, §10, P10)** is
  **optional** and deprioritized under Path B unless PSP-002 is actually committed.
  Still keep `scene/` and `render/` domain-agnostic (the import-boundary test is
  cheap and worth it), but don't build a Bode-plot example just to prove it.

Everything the brief says *about the datasheet artifact itself* is accurate and was
verified: the disabled `d=16` preset, the hardcoded `0.58`/`1.72`, en-GB/en-US
spelling mix, the reusable log spiral in Fig. 10, etc. Trust its defect list (§12).

---

## 4. Target repo layout

```
sbl-refs/                      # repo root
├── config.toml               # baseURL = https://refs.soundbytelabs.net/
├── content/
│   └── psp/                  # datasheets → /psp/... (PSP-001 → /psp/perspective)
├── data/psp/                 # parameters.yaml, drills.yaml, edges.yaml,
│                             #   gestalt.yaml, tiers.yaml, computed.json, ...
├── assets/css/               # light token set + role→token map (single source of color)
├── static/fonts/             # self-hosted, subset IBM Plex
├── layouts/
│   ├── psp/                  # document shell: masthead, title block, TOC, tier chrome
│   └── partials/psp/figures/*.svg   # generated by figures/, committed, reviewed in PRs
├── figures/                  # Python figure generator (brief L0–L4). Build-time only; NOT shipped.
│   ├── constants/            # L0: CONE_HALF_ANGLE → CONE_RATIO, MIN_DIST_RATIO
│   ├── kernel/               # L1: pure math — perspective/ (project, cone, twoPoint,
│   │                         #   threePoint, depth, ellipse, shadow, incline, armature)
│   │                         #   and tone/ (edge, notan)
│   ├── scene/                # L2: domain-agnostic scene DSL (imports NOTHING from kernel/constants)
│   ├── render/               # L3: scene → SVG string (knows no domain, no color)
│   ├── figures/              # L4: document-specific compositions (thin; math lives in L1)
│   ├── frames/               # ~30 pre-rendered lens frames for Fig. 1
│   ├── generate.py           # writes layouts/partials/psp/figures/*.svg + data/psp/computed.json
│   ├── pyproject.toml        # deps: pytest, hypothesis (pin exact; commit lockfile)
│   └── tests/                # property + snapshot tests (see brief §10)
├── tools/                    # CI checks: contrast, no-external-origins, import-boundary, drift
├── docs/                     # this handoff, the brief, the evaluation
├── source/                   # the original artifact, kept for reference
├── .github/workflows/pages.yml
└── README.md
```

Key invariants (from brief §4–§5, still in force):

- **No coordinate literal in any figure.** Every SVG coordinate is emitted by L3 from
  L1 math. No hand-tuned geometry.
- **`0.58`/`1.72` appear nowhere.** Both derive from `CONE_HALF_ANGLE = 30°`
  (`CONE_RATIO = tan 30°`, `MIN_DIST_RATIO = cot 30°`).
- **`scene/` and `render/` import nothing from `kernel/` or `constants/`.** Enforce
  with a ~10-line import-graph check in `tools/`. This is a failing build, not a
  convention.
- **Commit the generated SVGs.** CI regenerates and runs `git diff --exit-code` to
  prove currency (the "drift check").
- **The kernel works in drawing inches, origin at CV.** The renderer applies scale +
  translation; the kernel never sees a viewBox.

---

## 5. Phase plan (P0–P10, adapted for greenfield + Path B)

Each phase ends green (builds + tests pass). Correctness first, appearance last.

- **P0 — Scaffold.** `hugo new site`; `config.toml` with `baseURL` + light setup;
  `CNAME` = `refs.soundbytelabs.net`; self-host + subset IBM Plex; add the
  no-external-origins CI check; stand up the Pages workflow. A near-empty site that
  builds and deploys. *(No terminal theme, no submodule.)*
- **P1 — L0 + L1 perspective kernel** in Python with `hypothesis` property tests
  (brief §10 table). Nothing rendered yet. The fence-post depth-inversion and armature
  dual-derivation tests are the two that matter most.
- **P2 — L2 scene + L3 render + role→token map** (light). **Port one gestalt figure
  first** (brief §5.3) — it uses no kernel, so it's the purity test for the scene DSL.
- **P3 — Port the datasheet's existing figures** (Figs 2–10) from math; snapshot-diff
  each against the original as a sanity check.
- **P4 — Interactive figures.** Fig. 1 as ~30 pre-rendered frames + a swapping slider;
  the armature calculator stays inline JS.
- **P5 — `plot` + `link` scene primitives** (needed by the edge-profile and
  elements-graph figures in the content expansion). Keep them in `scene/`, not
  `figures/`.
- **P6 — `kernel/tone/` (edge, notan) + the new content sections** (brief §9: Edges,
  Gestalt, Notan, Eye path) + the tier metadata (T1/T2/T3) in the document shell.
- **P7 — Hugo integration + data extraction.** Move Tables 1–4 and every prose number
  into `data/psp/*.yaml` + `computed.json`; add a `{{< v >}}` shortcode so no literal
  numbers live in content.
- **P8 — Light theme finalize.** Contrast floors + grayscale test pass; edge figures
  use no hue.
- **P9 — Prose pass** (brief §7: en-US throughout, "textbook not essay" register).
  Parallelizable with P2–P8.
- **P10 — Document archetype** so `hugo new psp/002-*.md` inherits the shell.
  (Audio/PSP-002 smoke test optional — see §3.)

---

## 6. Acceptance criteria (from brief §14, adapted)

- [ ] No coordinate literal in any figure source; all SVG emitted from L1 math.
- [ ] `0.58` and `1.72` appear nowhere; both derive from `CONE_HALF_ANGLE`.
- [ ] `scene/` and `render/` import nothing domain-specific; enforced by a failing test.
- [ ] Gestalt figures import no kernel at all.
- [ ] Every property test in brief §10 passes (fence-post depth-inversion, armature
      dual-derivation, edge/notan invariants included).
- [ ] Every section carries a tier (T1/T2/T3); tier lives in the shell, not the content.
- [ ] All prose/caption numbers resolve from `computed.json`.
- [ ] Contrast floors met; figures legible in grayscale; edge figures use no hue.
- [ ] **No external origins in the built output** (fonts self-hosted, nothing CDN).
- [ ] Regenerating figures produces no git diff.
- [ ] en-US throughout.
- [ ] Deploys to `refs.soundbytelabs.net` via GitHub Pages.

---

## 7. Working conventions for the new agent

- Develop on a feature branch, not `main`. Commit in phase-sized, green increments.
- Pin exact Python dependency versions; commit the lockfile; `pip install`/`uv` with
  no network surprises. Direct deps should be few (`pytest`, `hypothesis`, an SVG/
  math helper only if truly needed).
- The generator is a build tool. Python is never served; only its SVG/JSON output is.
- When in doubt about math, the datasheet (`source/`) is the verified reference —
  reproduce its numbers, don't invent new ones.
- The brief's §12 defect list is your bug backlog; fix each as its phase comes up.

---

## 8. First actions when the repo exists

1. Confirm `source/perspective-datasheet.html` and `docs/PSP-001-brief.md` are present
   (they ship in this seed).
2. Read both in full.
3. Execute **P0**. It should end with a near-empty light Hugo site building locally
   (`hugo`) and deploying to `refs.soundbytelabs.net`, with the no-external-origins
   check wired into CI.
