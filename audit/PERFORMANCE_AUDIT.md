# Performance Audit

Part of the [Full Site Audit](FULL_SITE_AUDIT.md). Audit only.

**No Lighthouse, WebPageTest, or throttled-network run was available in this environment.**
Every number below is a direct filesystem or DOM measurement — labelled MEASURED — never a
claimed LCP/CLS/INP value. Where this audit suspects (but did not measure) a performance
consequence, it is labelled INFERRED and kept separate from measured fact, per the brief's
own evidence standard.

## MEASURED: deployed asset weight

Excludes `assets/source/` — CLAUDE.md confirms this directory (150 MB of unedited camera
originals) is never deployed; `tools/stage-deploy.py` copies only assets a page actually
references, and including `assets/source/` in a "what ships" figure would be a fabricated
number. Also excludes `assets/vendor/` (third-party libraries, audited separately below).

- **Total deployed `assets/`: 585.4 MB across 2,156 files.**
- **Images (`assets/img/`, deployed only): 158.1 MB across 1,935 files** — 1,169 WebP
  (60.4%) vs. 760 JPG (39.3%), 4 PNG, 2 SVG.
- **Video (`assets/video/`): 115.1 MB across 23 files** — 16 MP4, 7 WebM.
- **Documents (`assets/documents/crossroads/`): the 32 Crossroads issue PDFs alone range
  up to 27.0 MB each (issue 21); several others exceed 20 MB** — these are downloads, not
  page-load weight, but a real mobile-data concern with no file-size label shown to the
  visitor before they tap (see Quick Wins in the main report).

## MEASURED: DOM complexity (a real performance proxy, independent of network weight)

DOM node count and image count were measured directly (`document.getElementsByTagName('*')
.length`, `document.querySelectorAll('img').length`) on every primary route:

| Route | DOM nodes | Images | Note |
|---|---|---|---|
| **art-attack.html** | **2,668** | **297** | Highest on the site by a wide margin. **Live-measured update:** only 100 of 297 images are ever fetched on initial load (the other 197 are correctly `display:none`+`loading="lazy"` behind a "Show more" button) and its larger images resolve via `srcset` to properly-sized files (confirmed via `img.currentSrc`, not the markup alone). Real initial image payload: ~1.5–1.6MB, estimated. No measured network, memory or jank problem — see `FULL_SITE_AUDIT.md`'s Art Attack page audit |
| alumni.html | 1,514 | 11 | High node count from data-density (150 destinations), not images |
| theatre.html | 1,551 | 97 | Longest page by scroll height (40.9vh) |
| crossroads.html | 1,053 | 111 | |
| creative-writing.html | 1,406 | 3 | High node count from long-form text markup, not media |
| school-history.html | 1,226 | 31 | |
| math-challenge.html | 1,145 | 3 | Node count from canvas/interaction scaffolding, not media |
| index.html | 1,348 | 440 | High image count is the "Hundred Frames" ambient wall (small thumbnails) |
| cultural-gallery.html | 708 | 169 | Also 180 buttons — see Accessibility Audit |
| Most informational pages (Leadership, Parent Portal, Our Laurels, 404) | 440–670 | 3–18 | Appropriately light |

**Assessment:** `art-attack.html`'s DOM node count remains a real structural outlier — it is
the highest on the site by a wide margin, and that fact hasn't changed. What has changed,
after live measurement (see above), is the conclusion about its consequence: the page's
lazy-loading and responsive-image setup already prevent that node count from becoming a
real network or memory problem in practice. This is not a site-wide performance problem,
and — on the evidence gathered — not a page-specific one either; it is a structural fact
about the page (supporting real client-side filtering across 297 works) that does not need
a targeted fix.

## MEASURED: video loading discipline

Every `<video>` element sampled (Home, Founder, Sports, Captures, Art Attack, Festivals,
Theatre, Admissions) uses `muted` + a `poster` image, and either `preload="none"`
(Art Attack) or a JS-gated `.load()` call fired only after the poster has painted
(`film_html()`'s `progressive_loader` script, confirmed present specifically on
`art-attack.html`'s generated output) or `preload="metadata"`/`"auto"` elsewhere. None of
the sampled videos use the `autoplay` **attribute** — playback is JS-triggered, which is
the correct pattern for satisfying browser autoplay policies while still achieving an
autoplaying background/opening video. This is deliberate bandwidth discipline: the poster
paints first, and the actual video download is deferred or gated.

## MEASURED: scroll length by route (a proxy for content weight, not a defect signal)

`document.body.scrollHeight / window.innerHeight` at 1440×900, rounded to one decimal
("viewport-heights"):

| Route | vh | Route | vh |
|---|---|---|---|
| theatre.html | **40.9** (longest on the site) | index.html | 11.7 |
| festivals.html | 35.7 | math-challenge.html | 11.8 |
| creative-writing.html | 33.7 | curriculum.html | 11.2 |
| sports.html | 32.4 | our-results.html | 13.0 |
| captures.html | 30.9 | admissions.html | 12.1 |
| spiritual-life.html | 28.5 | school-info.html | 16.1 |
| alumni.html | 26.3 | important-documents.html | 9.5 |
| art-attack.html | 22.9 | curriculum/cbse.html | 9.1 |
| founder.html | 22.6 | curriculum/ib-diploma.html | 8.1 |
| the-cirs-experience.html | 17.6 | leadership.html | 5.7 |
| school-history.html | 11.4 | parent-portal.html | 3.7 |
| | | our-laurels.html | 3.0 (placeholder) |
| | | cultural-gallery.html | 1.0 (by design — no scroll) |

Length alone is not scored as a defect — Theatre covers three acts across a full
production year, Festivals covers seven named festivals, Creative Writing is a poetry
anthology. All three have a content-driven reason to be long. They are named here as the
top candidates for a live pacing check (see main report), not asserted to be padded.

## Not measured (explicitly)

- LCP, CLS, INP, or any Core Web Vital — no Lighthouse/CrUX access in this environment.
- Actual network transfer size under throttled conditions.
- JS execution/main-thread cost of GSAP ScrollTrigger instances, the Founder WebGL render
  loop, the Spiritual Life Three.js scene, or Math Challenge's three canvases — all four are
  genuine GPU/CPU cost centres that were not profiled.
- Font loading waterfall (FOIT/FOUT) — fonts are confirmed self-hosted in `assets/fonts/`
  (not third-party CDN), which structurally avoids the worst-case FOIT scenario, but load
  order/timing was not measured.
