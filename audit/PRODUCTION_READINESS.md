# Production Readiness

Part of the [Full Site Audit](FULL_SITE_AUDIT.md). Audit only.

## Debug/placeholder markers in shipped code

`grep`-equivalent scan for `TODO`, `FIXME`, `XXX`, `localhost`, `console.log(`, `debugger;`
across every `.html`/`.js`/`.css` file in the repository: **zero matches in any first-party
file.** The only 4 matches anywhere in the tree are inside vendored, unmodified third-party
library files (`three.module.min.js`, `three.core.js` under `assets/founder-opening/vendor/`
and `previews/founder-opening/vendor/`) — expected and irrelevant; nothing here is a
first-party debug leftover.

## Placeholder / unfinished content

Exactly one page: `our-laurels.html`, explicitly and honestly labelled as in preparation
(see main report). No other page carries bracketed placeholder text.

## Review-preview gate

The entire site is currently served `X-Robots-Tag: noindex` (Vercel) and a matching
`Disallow: /` `robots.txt` (both hosts), by deliberate, documented design
(`tools/stage-deploy.py`) — see the Route Inventory section of the main report for the full
context. **This is not a readiness defect; it is the owner's pre-launch switch, currently
in the "not yet launched" position.**

## Legacy/orphaned content

`Digital/`, `docs/`, `pdf/`, `previews/`, `review/`, `scrollcraft/` at the repository root
hold old-website or design-review material and are confirmed (by reading
`tools/stage-deploy.py`'s source, not by assumption) to never be copied into the deploy
directory. No action needed for launch readiness; flagged only as repository housekeeping.

## Automated checks (repository's own, run unmodified)

| Check | Result |
|---|---|
| `python tools/check-links.py` | 58 pages, 10,119 references, all resolve |
| `npx html-validate@11 *.html curriculum/*.html` | Zero errors across 58 pages |
| Console errors on ~36 pages navigated in this audit | None observed |
| Horizontal overflow at 390×844 on 30 primary routes | 0px on every route measured |

## Not run in this audit (documented CI/pre-push steps this session did not execute)

- `python3 tools/build-site.py` followed by `git diff --quiet -- '*.html'` (the drift check)
  — not run, since this was a read-only audit and re-running the generator, even though its
  output should be identical to committed files, was avoided to guarantee zero risk of
  touching tracked files during an audit-only session.
- `tools/check-contrast.py` — requires `playwright-core` via `CIRS_BROWSER_DIR`, not
  available in this environment; not run. Colour-contrast evidence in this audit instead
  comes from the inline ratio comments already present in `cirs.css` (see Accessibility
  Audit), which is a weaker form of evidence than a live pixel-sampling check.

## Verdict

On every check this audit could run, the site is technically production-ready **as a
pre-launch preview** — no broken links, no validation errors, no console errors, no mobile
overflow, no debug leftovers in first-party code. The only genuine blocker to a *content*
launch (as opposed to a *technical* one) is the 9 photo-less News reports and the Our
Laurels placeholder — both content-population tasks the school owns, not engineering work.
