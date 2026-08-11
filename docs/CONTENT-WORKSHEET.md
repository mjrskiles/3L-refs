# Landing page — content worksheet

**Everything here is a suggestion.** Section list, order, names, lengths — all of it is
a starting point to react to, not a structure to fill. Cut sections, add sections,
reorder them, rename them. The only things that aren't suggestions are the three
mechanical notes under "How the page is wired," because those describe how Markdown
turns into layout.

The page currently ships scaffold copy I wrote as a placeholder. **Replace all of it.**
Where I didn't know something I left the field blank rather than inventing it.

Fill this in however suits you — bullets, fragments, voice memo transcribed, whatever.
Hand it back and I'll transcribe it into `content/_index.md` and check the rendering.

---

## How the page is wired

Three couplings between the Markdown and the CSS. They're worth knowing before you
restructure, because breaking one fails silently — it just looks slightly wrong.

1. **The first paragraph is the lede.** It renders larger, in italic Literata, with a
   rule under it. That's `.landing > p:first-of-type`. If you add a paragraph above
   your intro, the treatment moves onto the wrong sentence.
2. **`## Heading` starts a section.** Each gets a rule above it and the heading green.
3. **`**Status:**` renders as a small uppercase label**, not bold body text. Useful for
   any short label-value line. Anything you bold gets that treatment, so use `*italic*`
   for ordinary emphasis inside prose.

Links are `[text](url)`. Fine to use raw HTML if you want something the Markdown can't
express — it's enabled deliberately.

---

## 1. Lede

One or two sentences. The whole thing in miniature, read by someone who has your card
in their hand and thirty seconds of attention.

Prompts, if useful: What would you say if someone at a party asked what you do and you
had one sentence? What connects the instruments, the firmware, and the drawing — or is
the connection not the point?

> **Your text:**
>
>

---

## 2. Who you are

A short paragraph or two. Enough that a stranger knows who they're reading.

Things you've mentioned that *could* belong here — include or ignore freely: senior
software engineer in embedded; the German-major-then-music-then-PLC-programmer path;
guitar as home base, plus piano, keys, modular; the farm in the Ozarks; drawing.

Worth deciding: is this page written in first person? The scaffold assumes yes.

> **Your text:**
>
>

---

## 3. Where the name comes from

**Open question from the scaffold.** One sentence. It's the first thing anyone will ask
you about, and right now the site doesn't answer it.

Could fold into §2 rather than standing alone.

> **Your text:**
>
>

---

## 4. Sound Byte Labs

Suggested: what it is, who it's for, and honestly what state it's in.

Your framing so far has been an open-source ARM firmware library for embedded audio,
positioned as the future DSP division of Three Lakes. Worth deciding how much of that
umbrella structure to say out loud on a public page versus just describing the thing.

Also worth deciding: does the Mutable Instruments acknowledgment belong here? The
scaffold includes one. It reads well to people who know the lineage — and Make Noise
would.

- **What it is (1–2 sentences):**
- **Who it's for:**
- **Status — honest:** `draft` / `in development` / `alpha` / other:
- **Link, if there's a repo to point at:**

> **Anything else:**
>
>

---

## 5. Instruments

**The thinnest section, and probably the one Make Noise actually reads.**

Suggested: name two or three, even prototypes, even unfinished. A specific
half-finished module says more than a general statement about building modules.

**One photo of a built module would do more than any paragraph here.** If you have a
bench shot, that's the highest-value addition to this page. Drop the file anywhere in
the repo and tell me where.

| Module | One line — what it does or what's interesting about it | Built / breadboard / design |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |

> **Anything else:**
>
>

---

## 6. Reference sheets

Suggested: what they are and why they exist. Currently the least concrete section,
since nothing has shipped yet.

Worth deciding whether to mention it at all before the first sheet is live, or leave it
out until the armature ref lands. An empty promise on a landing page is a small cost; a
missing one is no cost.

> **Your text:**
>
>

---

## 7. Contact

**Open question from the scaffold.** The section currently has a heading and nothing
under it.

- **Address:** — a plain personal address on a public page collects scrapers; a
  forwarding alias on the domain avoids that. Your call.
- **Anywhere else to link?** GitHub, Instagram, anything else:

---

## 8. Anything missing?

Sections I didn't suggest because I don't know whether you want them: music/listening,
writing, a now page, commissions or availability, a colophon about how the site is
built.

> **Your notes:**
>
>

---

## For later pages

Once this is settled the same shape generalizes: lede → sections with `##` →
label-value lines in bold. Ref pages add frontmatter (`title`, `status`, `tags`,
`thumbnail`), where `tags` must already exist in `data/tags.yaml` with a charter — CI
enforces it — and `status: draft` also needs `draft: true` or the page ships.

---

## What's there now (mine — for reference, replace it)

Sections currently live: lede, unnamed intro paragraph, `## Sound Byte Labs`,
`## Instruments`, `## Reference sheets`, `## Contact`. Three open `TODO` comments in
`content/_index.md` correspond to §3, §5, and §7 above.
