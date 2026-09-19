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

Arts, Music & Theatre is the one page that is not a document. It is a full-window field of
photographs — `"wall": True` in that page list — so it wears the header but no footer, no
banner and no scroll. Its photographs are listed in `tools/artswall.py` and cut by
`tools/make-arts-wall.py`; its sheet and script are `assets/css/artswall.css` and
`assets/js/artswall.js`, both scoped to `body.wall`.

## Checks, before every push

```sh
npx --yes html-validate@11 *.html      # structure and accessibility
python3 tools/check-links.py           # every link and asset reference resolves
python3 tools/build-site.py            # then: git diff --quiet -- '*.html'
```

`tools/check-contrast.py` additionally measures banner text against the pixels actually behind
it, seeking through the hero video. It takes the page as an argument and defaults to
Admissions — `news.html` for the other hero, `crossroads.html` for the drifting covers,
`arts.html` for the fold over the photograph wall. Run it after touching any hero, a scrim
or the honeycomb. It needs playwright-core, which is not in the repository: point
`CIRS_BROWSER_DIR` at the directory holding it.

## Things that are deliberate, not oversights

- `assets/source/` holds 150 MB of unedited camera originals. They are **never** deployed —
  `tools/stage-deploy.py` copies only assets a page references. Do not "tidy" them into
  `assets/img`; that would break the orphan check in `check-links.py`.
- Placeholder copy says plainly that it is waiting for the school. Do not replace a bracketed
  placeholder with invented content — particularly not testimonials.
- `netlify.toml` and `vercel.json` both exist during the move to Vercel and must be changed
  together until Netlify is retired. See HOSTING.md.

## What is not verifiable from a sandbox session

**Motion now is.** GSAP, ScrollTrigger and Lenis are served from `assets/vendor/` rather than
from a CDN, so a sandbox session loads them and the reveals, the pinned sections and the smooth
scroll can be checked before a change ships. This used to be the largest blind spot here.

**Type now is, too.** Newsreader, Literata, EB Garamond and Tiro Devanagari Hindi are served
from `assets/fonts/` rather than from fonts.googleapis.com, so a sandbox session renders the
real lettering and line lengths, headline breaks and small caps can all be checked before a
change ships. `tools/make-fonts.py` mirrors them; re-run it after changing a weight or adding
a family and commit what changes.

The cause, for anyone who meets it again elsewhere: it was never the certificate. The browser
a session drives does not use `$HTTPS_PROXY`, which is what `curl` reads — so the request to
fonts.googleapis.com was never made at all rather than being refused. Anything else loaded
from a third-party origin in a page under test will behave the same way.
