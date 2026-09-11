# Working on this repository

## The workflow the owner expects

This is the workflow for work the **owner** drives. Design sessions are the one
exception and are covered in the next section.

For every change, in this order:

1. **Do the work on the branch** `claude/cool-dijkstra-7ycja1`, never directly on `main`.
2. **Run the checks** — see below. Do not offer work that has not passed them.
3. **Ask before merging to `main`.** The owner confirms each merge; do not merge unprompted.
4. **After merging, deploy and hand back a Vercel link** they can share for review.

Steps 3 and 4 are the parts most easily forgotten. A change that is committed but not merged,
or merged but not deployed, is not finished from the owner's point of view.

## Design sessions

A designer drives design work through this same Claude account, **directly on
`main`**. The owner chose that deliberately, over a sandbox branch.

That means every push is a publication: Vercel deploys on push, and the GitHub
CI check runs *after* the deploy, not before it. The checks below are the only
gate that happens before the public sees a change, so run them every time, and
load https://cirs-website.vercel.app afterwards to confirm the change is what
was intended.

Say so before pushing, not after, when a change is large or you are unsure.
`DESIGNING.md` is the designer's full brief — keep it accurate if the workflow
changes.

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
