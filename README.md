# 3L-refs

The **Three Lakes Arts** site — landing page, reference sheets, and (later) a wiki
layer. Served at **https://threelakesarts.com** once DNS lands; until then at the
GitHub Pages project URL.

Built with [Hugo](https://gohugo.io/) on the
[3L design system](https://github.com/mjrskiles/3L-design) — nine Cretacolor pastel
voices, Lora/Literata/IBM Plex, day and night themes following the visitor's OS
preference. Self-hosted fonts, no external runtime origins. Figures are generated at
build time from a tested Python math kernel — no hand-placed coordinates.

The design system is **vendored at a pinned commit** (`data/design-system.yaml`) by
`make design`, and CI fails on drift. Edit it upstream, never in `assets/css/ds/`.

The repo name predates the site's scope (plan D9): it holds the whole site now, not
just the refs.

## Status

Landing page built and deploying (plan phase P0.5); **DNS is the open item.** First
ref in progress: **Rectangle Armature** — diagonals, eyes, reciprocals, rabatment, and
the nesting sequence whose pole is the eye.

**Start here:** [`docs/IMPLEMENTATION-PLAN.md`](docs/IMPLEMENTATION-PLAN.md) —
the settled plan (Rev 1.3). Copy for the landing page is drafted in
[`docs/CONTENT-WORKSHEET.md`](docs/CONTENT-WORKSHEET.md).
Background: [`docs/HANDOFF.md`](docs/HANDOFF.md) and
[`docs/PSP-001-brief.md`](docs/PSP-001-brief.md), both predating the rebrand and
amended by the plan.

## Layout

```
content/          # _index.md (landing) · refs/<slug>/ (page bundle per ref)
data/             # tags.yaml registry + computed/ (generator-emitted numbers)
assets/css/       # ds/ (vendored design system) + base, site chrome, figure roles
static/fonts/     # self-hosted woff2, vendored from 3L-design
static/print/     # generated print-true PDFs (when a ref needs them)
layouts/          # shell, tiles, fig/v shortcodes; _partials/figures/ (generated SVGs)
figures/          # Python figure generator — build-time only, never shipped
tools/            # toolchain fetchers, design sync + CI checks (origins, tags,
                  #   hexes, contrast, design drift; imports to come with P1)
docs/             # plan, handoff, brief; misc/ (spiral tool, for a later ref)
source/           # the original PSP-001 datasheet artifact, verified reference
```

## Local development

Everything is project-local — no system installs. Tooling lives in `.venv/`,
`bin/`, and `.uv/` (all gitignored, all disposable). Works on macOS and on
Linux/arm64 (Raspberry Pi 5).

```bash
make setup    # bootstrap: venv + uv, pinned Hugo into ./bin, python deps
make serve    # hugo server -D (drafts visible)
make test     # pytest (figure kernel)
make serve-lan # same, bound to the LAN (headless Pi + browser elsewhere)
make check    # build + tests + origin/tag/hex/contrast checks (what CI runs)
make build    # production build into public/
make design   # re-vendor CSS + fonts from the pinned 3L-design commit
```

**Requirements:** `python3` (3.9+ to bootstrap; uv fetches its own 3.12), `curl`,
`tar`, `git`. On Debian/Raspberry Pi OS the venv module is packaged separately:
`sudo apt install python3-venv`.

## License

Content: All rights reserved. Code/config: MIT.

(C) Michael Skiles 2026
