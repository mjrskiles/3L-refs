# sbl-refs

Sound Byte Labs' static **reference / datasheet site** — served at
**https://refs.soundbytelabs.net**.

Built with [Hugo](https://gohugo.io/), deployed via GitHub Pages. Light theme,
self-hosted fonts, no external runtime origins. Figures are generated from a Python
math kernel at build time (no hand-placed coordinates).

Its first document is **PSP-001 — Perspective & Composition**, a working datasheet of
constructions, constants, and pass criteria for pen-and-ink and colored-pencil
drawing.

## Status

Bootstrapping. This repo was split out of `soundbytelabs/blog` after an evaluation.
**If you are an agent or contributor starting here, read [`docs/HANDOFF.md`](docs/HANDOFF.md) first** —
it is the self-contained plan, decision record, and phase roadmap.

## Layout (target)

```
content/psp/     # datasheet content (Markdown + shortcodes)
data/psp/        # extracted tables + computed numbers
assets/css/      # light token set + role→token map
static/fonts/    # self-hosted, subset IBM Plex
layouts/psp/     # document shell (masthead, TOC, tier chrome) + generated figures
figures/         # Python figure generator (build-time only; not shipped)
tools/           # CI checks (contrast, no-external-origins, import-boundary, drift)
docs/            # handoff, brief, evaluation
source/          # the original single-file artifact, for reference
```

## Local development

```bash
# Generate figures (writes SVGs + computed.json into the Hugo tree)
python figures/generate.py

# Run the site
hugo server

# Build
hugo --gc --minify
```

## Deployment

GitHub Pages, custom domain `refs.soundbytelabs.net` (`CNAME`). One repo → one domain.
The `blog.soundbytelabs.net` site is a separate repo (`soundbytelabs/blog`) and is
unaffected.

## License

Content: All rights reserved. Code/config: MIT.
