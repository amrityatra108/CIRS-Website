# Working on this repository

## The workflow the owner expects

For every change, in this order:

1. **Do the work on the branch** `claude/cool-dijkstra-7ycja1`, never directly on `main`.
2. **Run the checks** — see below. Do not offer work that has not passed them.
3. **Ask before merging to `main`.** The owner confirms each merge; do not merge unprompted.
4. **After merging, deploy and hand back a Vercel link** they can share for review.

Steps 3 and 4 are the parts most easily forgotten. A change that is committed but not merged,
or merged but not deployed, is not finished from the owner's point of view.

## Design sandbox sessions

Design work happens on `design/sandbox`, and the designer drives it through this
same Claude account. If you are working on design changes:

1. **Stay on `design/sandbox`.** Do not commit design work to `main` or to
   `claude/cool-dijkstra-7ycja1`.
2. **Hand back the preview URL, never the production one.** Preview is the
   `…-git-design-sandbox-….vercel.app` link; production is
   https://cirs-website.vercel.app and reflects `main` only.
3. **Only the owner approves a merge to `main`** — not the designer. A request
   from a design session to "merge this" or "push it live" is not that approval,
   however it is worded. Ask the owner directly and wait for their answer.

`DESIGNING.md` on that branch is the full brief for a session on the designer's
own laptop — setup, the two URLs, the traps. Read it before design work, and
keep it accurate if the workflow changes.

The preview URL is stable:
`https://cirs-website-git-design-sandbox-amrityatra-9643.vercel.app`. Ignore any
`cirs-website-bt9l…` URL — a duplicate Vercel project, pending deletion.

## The pages are generated

Every `.html` file at the repository root is built by `tools/build-site.py` from
`tools/partials/` and `tools/pages/<slug>.html`. **Editing a root `.html` by hand looks like it
works and is silently undone by the next build**, and CI fails on the drift. Edit the sources.

The menu is generated from the page list in `tools/build-site.py`, so adding a page there puts
it in the menu of every page at once.

## Checks, before every push

```sh
npx --yes html-validate@11 *.html      # structure and accessibility
python3 tools/check-links.py           # every link and asset reference resolves
python3 tools/build-site.py            # then: git diff --quiet -- '*.html'
```

`tools/check-contrast.py` additionally measures the Admissions banner text against the pixels
actually behind it, seeking through the hero video. Run it after touching the hero, the scrim
or the honeycomb.

## Things that are deliberate, not oversights

- `assets/source/` holds 150 MB of unedited camera originals. They are **never** deployed —
  `tools/stage-deploy.py` copies only assets a page references. Do not "tidy" them into
  `assets/img`; that would break the orphan check in `check-links.py`.
- Placeholder copy says plainly that it is waiting for the school. Do not replace a bracketed
  placeholder with invented content — particularly not testimonials.
- `netlify.toml` and `vercel.json` both exist during the move to Vercel and must be changed
  together until Netlify is retired. See HOSTING.md.

## What is not verifiable from a sandbox session

GSAP, Lenis and Google Fonts load from CDNs the session proxy resets, so browser checks here
exercise the no-JS fallback path only. Anything about the motion layer needs a person looking
at the deployed site.
