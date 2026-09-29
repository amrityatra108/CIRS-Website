# Broken-Experience Report

Part of the [Full Site Audit](FULL_SITE_AUDIT.md). Audit only — nothing here was fixed.

## Method

- `python tools/check-links.py` — the repository's own link/asset resolver, run unmodified
  against all 58 generated pages.
- `npx html-validate@11 *.html curriculum/*.html` — the repository's own documented
  pre-push check, run unmodified.
- Direct console inspection (`read_console_messages`) on every page navigated to during this
  audit — see the list in `FULL_SITE_AUDIT.md`'s Broken-Experience Report section.
- Direct DOM measurement of horizontal overflow at 390×844 on all 30 primary routes.

## Results

### Broken links / missing assets

```
check-links: 58 pages, 10,119 references, all resolve
```

**Zero.** Every `href`, `src`, `srcset` and `poster` reference across all 58 pages resolves
to a real file. This includes internal page links, image/video/font assets, and the PDF
documents referenced from School Information and Important Documents.

### HTML validity

`html-validate@11` against all 58 pages (56 root `.html` + `curriculum/cbse.html` +
`curriculum/ib-diploma.html`): **zero errors, zero warnings reported.**

### Console errors

No JavaScript console errors or warnings were observed on any of the ~36 pages this audit
navigated to. Console was explicitly spot-checked (not just silently assumed clean) on
`school-history.html` and `spiritual-life.html` — both of which load the heaviest
page-specific script sets (`history.js`; `spiritual.js` + `spiritual-opening.js` + a
Three.js canvas) — and both returned "No console logs." This is not a claim that **no**
route anywhere can ever throw a console error (interaction paths not exercised, e.g. the
Founder WebGL portrait's pointer-follow, were not stress-tested), but no error surfaced on
any page load in this audit.

### 404 handling

`404.html` is confirmed served with a fully designed page (see `FULL_SITE_AUDIT.md`'s page
audit) rather than a bare browser/host error. `netlify.toml` and `vercel.json` both route
unmatched paths to it (per CLAUDE.md/HOSTING.md — not independently re-verified against a
live deploy in this audit, since this audit ran against a local static server, not the
production host).

### Placeholder / under-construction content

Exactly one: **`our-laurels.html`**, which explicitly and honestly states it is a
placeholder (`soon_html()` output: "[Placeholder — competition names, years, placings and
the students involved, to be supplied by the sports office and the activities office.]")
and links onward to `sports.html` rather than dead-ending. This is disclosed, not hidden —
listed here for completeness, not as a defect.

### Empty sections that are not placeholders

The 9 photo-less News-archive reports (see `FULL_SITE_AUDIT.md`) are **not** broken or
placeholder pages — every link/image on them resolves and validates. They are simply
text-only content. Recorded in the [Content Credibility](FULL_SITE_AUDIT.md#content-credibility--underdesigned-pages)
section, not here, since nothing on them is actually broken.

### What was not checked

- External links (mailto:, tel:, the `easycollege.in` application portal, YouTube embeds,
  social links) were not individually pinged — `check-links.py`'s scope is internal
  references and local assets, confirmed by reading the script's behaviour, not by
  independently re-testing every external URL.
- Live production deploy (Vercel) was not checked in this session — this audit ran against
  the local static build, not `cirs-website.vercel.app`.
- Form submission paths — there are no on-page forms found on any of the 30 primary routes
  checked (`forms: 0` everywhere probed), so there is nothing of this kind to test.

## Conclusion

This is, on the evidence gathered, a clean bill on the traditional "broken experience"
categories: no dead links, no missing assets, no HTML errors, no console errors observed,
one honestly disclosed placeholder, and a correctly designed 404. The site's real gaps are
content-population (see main report), not breakage.
