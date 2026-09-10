# Working on the design sandbox

This branch, `design/sandbox`, is where design changes are tried. It is a copy of
`main` and nothing on it reaches the live site until the owner approves it. Push
here as freely as you like — you cannot break production from this branch.

**Two URLs, and they are not the same thing:**

| | URL | What it is |
|---|---|---|
| Preview | the `…-git-design-sandbox-….vercel.app` link | this branch. Yours to break. |
| Production | https://cirs-website.vercel.app | `main`. The owner approves every change that lands here. |

Always share the preview link for review. Never point a reviewer at production
and describe unmerged work.

## The one thing that will waste your afternoon

**Every `.html` file in the repository root is generated.** Editing `index.html`
or `admissions.html` by hand appears to work, survives a refresh, and is then
silently erased by the next build — and CI fails on the drift.

The sources are:

- `tools/partials/` — the shared head, header, footer
- `tools/pages/<slug>.html` — the body of one page
- `tools/build-site.py` — the `PAGES` manifest: titles, menu labels, banner copy

Adding a page to that manifest puts it in the menu of every page at once. Edit
the source, run the build, commit both.

## Where the design actually lives

Most visual change needs no markup at all.

- `assets/css/cirs.css` — the design system. The tokens are at the top of the
  file: palette, type scale, spacing steps, measure. **Change the token, not the
  fifty places that use it.** Deep purple, gold, dark red, black and white are
  the identity; red on purple was deliberately replaced with gold for legibility,
  so don't reintroduce it.
- `assets/css/pages.css` — per-page components: the header tabs, the page hero,
  the jump menu, tables, the news list.

The spacing scale (`--space-1` … `--space-10`) exists so new components are built
on the same steps rather than one-off pixel values. Please keep to it.

## Before you push

```sh
npx --yes html-validate@11 *.html      # structure and accessibility
python3 tools/check-links.py           # every link and asset reference resolves
python3 tools/build-site.py            # then: git diff --quiet -- '*.html'
```

That last pair is the drift check: build, then confirm no root `.html` changed
unexpectedly. If it did, you edited a generated file.

`tools/check-contrast.py` measures the Admissions banner text against the pixels
actually behind it, seeking through the hero video. Run it if you touch the hero,
the scrim or the honeycomb.

## Things that are deliberate, not oversights

- `assets/source/` is a 171 MB photograph library that is **never deployed**.
  `tools/stage-deploy.py` copies only assets a page actually references — that
  rule is what keeps a 7.6 MB deploy from becoming a 153 MB one. Do not move
  these into `assets/img`; it would break the orphan check in `check-links.py`.
  Derive a cropped, sized image into `assets/img` and reference it from a page.
- Placeholder copy says plainly that it is waiting for the school. **Do not
  replace a bracketed placeholder with invented content — particularly not
  testimonials.** A plausible invented quote from a real school is worse than an
  obvious gap.
- `netlify.toml` and `vercel.json` both exist during the move to Vercel and must
  be changed together until Netlify is retired. See HOSTING.md.

## What cannot be checked from a sandbox session

GSAP, Lenis and Google Fonts load from CDNs the session proxy resets, so
automated browser checks here only ever exercise the no-JS fallback path.
**Anything about motion, scroll behaviour or webfont rendering needs a person
looking at the deployed preview.** If a change is about motion, say so when you
hand over the preview link, so it gets human eyes rather than a green checkmark.

## Open questions the owner has already flagged

- Primary buttons are white-on-gold at **1.61:1** — below the 4.5:1 minimum. Dark
  purple text on the same gold gives 12.15:1. The owner has not yet decided.
- A rewritten "CIRS is a family" passage is drafted but not yet placed on the
  Why CIRS page.
