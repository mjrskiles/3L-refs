# 3L-refs — Implementation Plan

**Rev 1.1 — SETTLED.** Amends `HANDOFF.md` per planning discussion of 2026-07-22/23.
Markup of Rev 0.1 is folded in; §6 records the resolutions (R1–R5). Where this plan
and the handoff conflict, this plan wins.

**Rev 1.1 changes (2026-07-24):** first concept is **rectangle armature**, not spirals
(§4 P2; spirals moves to the P3 queue) · rebrand to **Three Lakes** · repo renamed
**3L-refs**, hosted personally for now (D9) · development is **cross-platform** —
macOS and Raspberry Pi 5 / arm64 Linux (D14).

**Rev 1.2 changes (2026-08-02):** the site is **one site at the apex**,
`threelakesarts.com`, with refs under `/refs/` — supersedes D4's flat namespace and
D9's `refs.` subdomain (see D15) · `.music` dropped as a restricted TLD · a **wiki
layer** is adopted as a second content type alongside refs (D16) · near-term priority
is a **landing page**, ahead of any ref (§4 P0.5).

---

## 1. What changed since the handoff

The handoff planned a batch refactor: port everything, then polish. Two planning
decisions reshape it:

1. **Organic authoring.** Content is authored one concept at a time, each landing
   finished (math + figure + prose + tier + tests). The pipeline and authoring
   tooling are built early and completely; content flows through indefinitely.
   The original datasheet demotes from "migration source" to "verified reference."
2. **First concept: rectangle armature**, not perspective. It is the material most
   relevant to current sketching practice, its math is self-contained, and it seeds
   the spirals ref that follows (the nesting sequence *is* a log spiral).

Everything else in the handoff's locked-decision list stands: all-light theme from
the datasheet's `:root` tokens, Python kernel (Path B), no external runtime origins,
committed generated SVGs + drift check, kernel works in drawing inches, scene/render
import boundary enforced by a failing build.

---

## 2. Decision record (from planning rounds)

### 2.1 Content & authoring

- **D1. Ref object model.** Each topic is a Hugo page bundle: `content/<slug>/index.md`
  + local resources. Frontmatter: `title`, `tags`, `status`
  (`draft` | `prelim` | `current`), `thumbnail` (a figure name). Body is
  the whole document. Drafts live in the repo unshipped via `status`/`draft`.
  Doc IDs deferred entirely (R1).
- **D2. Markdown is the authoring format.** Prose in Markdown; figures via
  `{{< fig "name" >}}`; computed numbers via `{{< v "path.to.value" >}}`. Raw HTML
  passthrough stays enabled as an escape hatch, not a habit.
- **D3. Page-or-card.** Whole-page layout now. A future card partial renders
  metadata + thumbnail from the same bundle; mix-and-match composition on listing
  pages later. No authoring change when that arrives.
- **D4. No hierarchy in URLs.** ~~Refs live at `refs.threelakes.music/<slug>/`.~~
  **Superseded by D15** — refs live at `threelakesarts.com/refs/<slug>/`. The
  principle survives inside that namespace: subject areas, document kinds, and themes
  are **tags**, not path segments, and document identity (PSP-001 etc.) lives in
  frontmatter, never the URL. `/refs/` is a content-type boundary, not a taxonomy.
- **D5. Tag registry.** `data/tags.yaml`: every tag has slug, display name, one-line
  charter. CI fails on unregistered tags. Starter vocabulary (R2): `composition`,
  `curves`, `visual-art`, `drawing`.
- **D6. Landing page.** Flat tiled list of every ref. Client-side tag filtering
  (build-emitted JSON index + small vanilla JS) is **deferred** until the ref count
  makes browsing annoying. Hugo's built-in per-tag listing pages come free before that.

### 2.2 Platform

- **D7. Hugo, with strict thinness.** Templates and shortcodes stay dumb; all data
  transformation happens in the Python generator. This keeps Hugo the most
  disposable layer and preserves the documented escape hatch: **Django-as-baker**
  (admin + models + Jinja at authoring time, baked to static, same hosting) if
  authoring in files ever becomes the bottleneck. No dynamic serving on the roadmap.
- **D8. Python environment.** `uv`-managed, `pyproject.toml`, committed lockfile,
  always a venv. Runtime deps stay minimal (`pytest`, `hypothesis`; `cairosvg` +
  `pypdf` as build-only deps for the print target).
- **D9. Repo and domain.** This checkout is the project, renamed **`3L-refs`** and
  pushed to `git@github.com:mjrskiles/3L-refs.git` (personal account while the Three
  Lakes org is sorted; the remote can move later without touching the tree). Site URL
  is `https://threelakesarts.com/` per D15. The repo name still says "refs" and is
  now narrower than the site; renaming it is cosmetic and deferred.
- **D15. One site at the apex.** `threelakesarts.com` serves everything: the landing
  page at `/`, reference sheets at `/refs/<slug>/`, wiki concept nodes at `/c/<slug>/`
  (D16), tag pages at `/tags/<slug>/`. Not a `refs.` subdomain — the site is an
  umbrella (who I am, Sound Byte Labs, instruments, reference material), and splitting
  it would mean two repos, two CI configs, two deploys, and a duplicated token set,
  while making links between the wiki and the rest cross-origin.
  - **Staging:** the Pages project URL `mjrskiles.github.io/3L-refs/` until DNS
    resolves. CI derives `baseURL` from `actions/configure-pages`, so the cutover is a
    repo setting, not a commit. **Asset URLs must survive a subpath** — use `relURL`/
    `relref` in templates and *relative* `url()` in CSS, never root-absolute.
  - **No `CNAME` file until DNS resolves.** With one present, Pages redirects the
    working `.io` URL to a dead host and the site is unreachable from anywhere.

- **D16. Wiki layer alongside refs.** Two content types, deliberately different:
  refs are few, large, and finished; wiki nodes are many, small, and permanently
  partial. A concept like the log spiral is load-bearing in armature, spirals, and eye
  path — refs-only forces either triplicated definitions or fragile deep links into
  section anchors. A node gives it one address.
  - **Static, not an engine.** Authoring stays git + editor, so no server, no DB, and
    D7's "no dynamic serving" holds. The `[[wikilink]]` syntax keeps the content
    directory Obsidian-compatible.
  - **Backlinks are generated, not templated.** Hugo cannot index link targets; the
    Python generator walks content and emits a link graph to `data/`, and a dumb
    partial renders "what links here." Same division of labor as D7.
  - **`data/tags.yaml` is the seed.** A tag already carries a slug, a display name, and
    a charter, and its term page already renders name + definition + inbound refs —
    structurally a concept node. Nodes grow out of the registry rather than replacing
    it, so nothing built in P0 is thrown away.

- **D14. Cross-platform development.** The same checkout must work on macOS and on
  a Raspberry Pi 5 (arm64 Linux). Toolchain fetchers detect OS/arch; nothing is
  installed system-wide (`tools/get_hugo.sh` handles darwin-universal `.pkg` and
  linux arm64/armv7/amd64 tarballs; `uv` provides a project-local CPython on both).
  Non-extended Hugo is deliberate — no SCSS, so no libsass/CGO portability cost.

### 2.3 Figure authoring

- **D10. Figures are Python compositions** (L4) over kernel math (L1), emitting
  scene primitives (L2), rendered to SVG (L3). No coordinate literals; labels
  anchor to computed points with manual `dx`/`dy` offsets only.
- **D11. Workbench: in.** Dev-only per-figure pages (never shipped): context widths,
  true grayscale rendering via a gray role map, per-role isolation views, parameter
  + computed-value tables, contrast results, and **inspectability** (data attributes:
  hover → role/anchor/source; click a point → copy its reference name).
- **D12. Watch loop: in.** `generate.py --watch` regenerates only the changed
  figure's SVG; the workbench page auto-refreshes (polling, a few lines of JS).
  `hugo server` already live-reloads prose/CSS natively — nothing to build there.
- **D13. Dropped:** drag-to-nudge write-back, hand-drawn-scan comparison view, and
  any graphical figure editor. Geometry stays code; annotation nudging happens at
  1-second regen cycles.

### 2.4 Deferred with options noted (no decision needed now)

- **Roll-your-own templates** (visitor-parameterized generation): pre-rendered
  parameter grid vs. Pyodide/WASM kernel-in-browser vs. the Django jump. First
  genuinely dynamic-ish feature on the roadmap; nothing in this plan forecloses any option.
- **Search**: prebuilt static index when needed.
- **Cards / mix-n-match layouts** (per D3).

---

## 3. Target layout (delta from handoff §4)

```
3L-refs/
├── hugo.toml                 # baseURL threelakesarts.com; taxonomies: tags
├── content/
│   ├── _index.md             # landing page (D15)
│   ├── refs/
│   │   ├── _index.md         # refs index (tiled list)
│   │   └── armature/index.md # first ref (P2)
│   └── c/                    # wiki concept nodes (D16, later)
├── data/
│   ├── tags.yaml             # tag registry (D5)
│   └── computed/             # per-ref computed.json emitted by generator
├── assets/css/               # tokens.css (from datasheet :root) + roles.css (role→token map)
├── static/
│   ├── fonts/                # subset IBM Plex (build-scripted, not manual)
│   └── print/                # generated print PDFs (committed, drift-checked)
├── layouts/                  # shell: baseof, ref single page, landing list, fig/v shortcodes
├── figures/                  # Python package (uv). NOT shipped.
│   ├── constants/            # L0
│   ├── kernel/               # L1: armature/, spiral/ (grown per concept)
│   ├── scene/                # L2: primitives + Scene (imports nothing from L0/L1)
│   ├── render/               # L3: scene → SVG; web target + print target (physical scale)
│   ├── figures/              # L4: per-ref compositions
│   ├── workbench/            # dev-only workbench page emitter
│   ├── generate.py           # + --watch
│   └── tests/
├── tools/                    # toolchain fetchers (get_hugo.sh, subset_fonts.py) +
│                             #   CI checks: no-external-origins, tag-registry,
│                             #   import-boundary, contrast, drift
├── docs/                     # handoff, brief, this plan; misc/ (original spiral tool)
└── .github/workflows/ci.yml  # test → generate → drift → hugo build → origin check
```

Naming note: generated figure SVGs land under `layouts/_partials/figures/<ref>/`
(inlined by the `fig` shortcode); print sheets under `static/print/<ref>/` (R5).

---

## 4. Phases

Each phase ends green (CI passing). Feature branch per phase.

### P0 — Scaffold ✅ complete

- [x] Hugo skeleton: `hugo.toml` (tags taxonomy, Goldmark raw-HTML on, baseURL),
      `layouts/` shell (baseof, home, single, list, tile partial), `content/_index.md`
- [x] `assets/css/tokens.css` from the datasheet `:root`; `roles.css` stub; `site.css`
- [x] Font subsetting script + subset IBM Plex into `static/fonts/`; no Google Fonts
- [x] `data/tags.yaml` with starter vocabulary (R2); registry names drive display
- [x] `tools/check_origins.py` (no external origins in built `public/`)
- [x] `tools/check_tags.py` (frontmatter tags ⊆ registry; status vocabulary valid)
- [x] `figures/` package skeleton under `uv` (pyproject, lockfile, pytest + hypothesis)
- [x] CI workflow: uv sync → pytest → hugo build → origin + tag checks
- [x] Landing page renders a tiled list
- [x] Project-local toolchain, no system installs: `tools/get_hugo.sh` (pinned,
      checksummed, macOS + Linux arm64/armv7/amd64), `Makefile` wrapper
- [x] `{{< fig >}}` / `{{< v >}}` shortcode stubs that fail loudly until fed

**Ended when:** empty-but-real site built green locally (`make check`); conventions in place.

### P0.5 — Landing page + deploy ✅ complete (2026-08-02)

Inserted ahead of P1: a live site is needed for the Asheville trip (~2026-08-16),
and none of it depends on the figure pipeline.

- [x] Apex restructure per D15 — landing at `/`, refs under `/refs/`
- [x] Landing page: intro, Sound Byte Labs, instruments, reference sheets, contact
- [x] P0 defect fixes (relative font `url()`, `--cleanDestinationDir`, `lang` from
      config, protocol-relative origins, `status: draft` ⇒ `draft: true` enforced)
- [x] Pages deploy job on `main`, `baseURL` derived from `configure-pages`
- [ ] **DNS** — apex records for `threelakesarts.com`, then set the custom domain in
      repo Pages settings. Not code; the long pole. Cert issuance can take 24h.

**Ends when:** the landing page is live, first on the `.io` URL, then on the domain.

### P1 — Scene, render, workbench

- [ ] L2 scene DSL: `seg`, `poly`, `circle`, `ellipse`, `marker`, `label`,
      `path` (point-list curves — the armature nesting spiral needs it);
      `plot`/`node`/`link` deferred to the concepts that force them
- [ ] Scene frame modes `fit`/`fixed`; scale in px-per-inch; roles per the brief
- [ ] L3 web renderer: scene → SVG, one class per role, `aria-label`, no color knowledge
- [ ] `tools/check_imports.py`: scene/render import nothing from kernel/constants — failing build
- [ ] Contrast check over `roles.css` (WCAG luminance, ~20 lines)
- [ ] Workbench emitter (D11): per-figure dev pages incl. grayscale + role isolation
      + inspect attributes; excluded from production build
- [ ] `generate.py --watch` + workbench auto-refresh (D12)
- [ ] One trivial test figure exercising the whole loop end to end

**Ends when:** test figure visible in workbench in all views; edit→see under ~2s;
boundary and contrast checks enforce in CI.

### P2 — Rectangle armature, end to end

Source of record for the math: `source/perspective-datasheet.html` §8 (verified;
reproduce its numbers, don't reinvent them). Its defect list applies — brief §12
item 10 (ugly fraction reduction in the calculator) gets fixed here.

- [ ] `kernel/armature/`: diagonals · eyes both ways (closed form `p²/(p²+q²)`
      **and** perpendicular-foot construction) · reciprocals · rabatment · medians ·
      nesting sequence · pole. Property tests: **dual-derivation** (the handoff's
      must-have) · nesting contains the pole and alternates proportion ∀ `n ≤ 12` ·
      rabatment coincides with thirds iff `p:q = 2:3` · pole = eye in the limit
- [ ] L4 figures: armature families (one per family + composite) · nesting sequence
      converging on the pole (the log spiral, seeding the later spirals ref) ·
      thirds-vs-armature comparison at 2:3 and φ — the figure the prose argues from
- [ ] `data/computed/armature.json`: every number the prose cites (4/13, 9/13, the
      0.026 miss, 0.62″ at 16×24, φ eyes at 0.276/0.724, plate-seam example)
- [ ] Armature calculator: inline JS per handoff decision 2, with the fraction
      reduction defect fixed; values cross-checked against the kernel in tests
- [ ] Snapshot tests on emitted SVGs; drift check in CI
- [ ] `content/armature/index.md`: authored prose (yours), figures inline via
      `{{< fig >}}`, numbers via `{{< v >}}`, frontmatter complete incl. thumbnail.
      Structure per R4's spirit: theory upfront, prominent links at the top jumping
      to the practical/how-to sections
- [ ] Landing tile shows the armature ref

**Ends when:** the armature ref is a finished page on the built site, all figures
generated from tested math, no coordinate literals, drift check green.

**Optional P2b — printable armature sheets.** True-scale overlay sheets for common
plate sizes (8×10 sketchbook, 16×24). Pulls the L3 print target forward from the
spirals ref: physical-scale renderer (1 unit = 1 inch), calibration bars, PDF
assembly (`cairosvg` + `pypdf`, build-only deps), output to `static/print/armature/`.
Decide at P2 start (OPEN-6) — worth doing if bench-usable templates are the point,
worth deferring if shipping the ref sooner matters more.

### P3+ — The concept loop (steady state)

Per concept: pick → port/author kernel math (+ property tests) → compose figures →
write prose → tag + tier + status → extract data → snapshot → ship. Queue, in rough
order:

- **Spirals** — log-spiral theory + printable true-scale templates, adapting
  `docs/misc/gen_spirals.py`. Follows armature naturally (shares the pole/nesting
  math) and brings the L3 print target if P2b didn't. Structure per R4.
- **Perspective** — the PSP-001 material, section by section.
- **Gestalt** — still the scene-DSL purity proof (imports no kernel at all).
- **Edges** (forces `plot`) · **elements graph** (forces `node`/`link`) · **notan** ·
  **eye path** (reuses the armature spiral as a candidate path).

Tier chrome (T1/T2/T3) enters the shell when the first tiered concept ships.

---

## 5. Per-concept definition of done

A concept ships when: kernel math has property tests · figures emit from math with
no coordinate literals · prose is finished (en-US, register per brief §7) · numbers
in prose resolve from computed data · tags registered · status honest · grayscale
legible · contrast passes · snapshots current · drift check green.

---

## 6. Resolutions (markup of Rev 0.1)

- **R1 — Doc IDs:** deferred entirely. No `id` frontmatter until a concept needs it.
- **R2 — Starter tags:** `composition`, `curves`, `visual-art`, `drawing`.
- **R3 — Landing tile:** title, status chip, tags, thumbnail figure — as proposed.
- **R4 — Ref structure:** theory upfront, with prominent links at the top jumping to
  the templates / how-to sections. (Stated for spirals; adopted as the house pattern.)
- **R5 — Print PDFs:** committed + drift-checked as proposed; directory named
  `static/print/` (not `downloads`).

### Open

- **OPEN-6 — P2b printable armature sheets:** in scope for the armature ref, or
  deferred to the spirals ref? Decide at P2 start.

- **OPEN-7 — lab notebook.** Raised 2026-08-02, deliberately *not* decided. Two
  separate needs were conflated here, and they have different answers:
  1. **A tool for working math out interactively** (Jupyter). A tooling detail, not
     an architecture question — answerable in an afternoon whenever a derivation
     actually gets hard. If adopted: notebooks import `kernel/`, never define math;
     jupytext-paired so `.py` is committed and `.ipynb` is ignored; its own
     dependency group so CI never installs it. **Skipped for now.**
  2. **A place to keep a chronological record** — a fourth content type (`log`),
     organized by time rather than topic, where being dated and provisionally wrong
     is the point. This needs no Jupyter at all; most lab-log entries are prose, a
     number, and a photo. It sits beside refs (canonical) and wiki nodes (topical,
     D16), and material migrates: log → wiki node → ref section.

  Decide (2) with the D16 wiki work after the Asheville trip. (1) can wait for a
  concrete need.
