# School History cinematic redesign

Initial implementation branch: `codex/school-history-cinematic`. The owner
subsequently authorised merge and deployment. The release is integrated in
`codex/school-history-release-20260930` from current main, preserving other
routes and resolving the generated page from its template.

## Implementation

The route keeps the existing Python-generated static architecture and shared
navigation, footer, film player and Lenis owner. Its opening is an immediately
visible school campus photograph. The title is exactly “A vision. A school. A
living legacy.” A portrait expands through “The beginning of CIRS” before a
single Three.js scene takes over the archival journey on desktop.

The camera follows an open descending Catmull-Rom curve with a restrained
lateral arc. Native document progress drives it; it does not capture wheel or
touch input, loop, snap chapters or create another smooth scroller. Each chapter
gets 2.1 viewport heights, with substantial stationary intervals. Photographs
retain their recorded aspect ratios, grow through perspective and fade before
the camera can intersect them. Text and sources remain HTML in a stable reading
column. The inauguration photograph opens through ten paired horizontal SVG
mask bands, with overlap to avoid hairline gaps, and then yields to later
chapters. Its text enters after the image becomes legible. The journey releases
into a contemporary campus photograph and links to Experience and Admissions.

The complete chronological register has **31 records**: all 24 original records
and the seven sourced records from the latest remote main's 2025 Annual Report
update. The content verification compares every original date, period, title,
summary and full account and confirms none changed. Existing `#record-*` and
`#chapter-*` links remain. Search, decade and period filters combine; Reset
restores the collection. Record dialogs retain Escape, previous/next, Back and
focus return. Longer accounts also have native inline disclosures.

Mobile, reduced motion, unavailable WebGL, texture failure and context loss use
the readable photograph-and-text document. A successful texture load precedes
enabling the enhanced layout. Pixel ratio is capped at 1.5; textures load around
the active chapter, every photographic plane has a distinct source, and rendering stops
offscreen, while idle and in hidden tabs. Page exit disposes textures,
geometries, materials, the renderer, observers and page listeners. Font loading
and viewport changes refresh geometry. Changing reduced motion clears the
enhancement and motion transforms. Direct chapter hashes work during first
load and after geometry changes.

### Files

- `tools/pages/school-history.html`: photographic shell, expansion, scene,
  present-day arrival and complete archive controls.
- `tools/history.py`: source dataset, sourced additions, image provenance,
  chapter generation, decade data, record summaries and disclosures.
- `tools/build-site.py`: scoped stylesheet and controller loading/cache suffix.
- `assets/css/history-cinematic.css`: scoped composition and responsive states.
- `assets/css/history.css`: archive/dialog/film styles; obsolete journey styles
  removed because they hid the new timeline.
- `assets/js/history-cinematic-journey.js`: document progress, active navigation,
  camera enhancement, expansion, masks, keyboard/deep links and teardown.
- `assets/js/history-cinematic-world.js`: the one Three.js scene and shared
  progressive textures.
- `assets/js/history.js`: combined archive search/filtering, retaining the
  existing record interaction controller.
- `tools/stage-deploy.py`: explicitly includes the dynamically imported scene.
- `tools/make-history-supplied.py`: repeatable proportion-preserving JPEG cuts.
- `tools/make-history-distinct.py`: distinct official-source photographs and
  an unaltered first-page rendering of the 2025 Annual Report.
- `assets/img/history/supplied-{rupee,opening,isa,poland}-{sm,lg}.jpg`.
- `assets/documents/school-info/annual-report-2019.pdf`: the historical report
  from remote main, preserving the original 2019 citation now that the current
  report filename points to the 2025 report.
- `school-history.html`: rebuilt generated output, never edited by hand.

## References and permission boundaries

All effect implementation is independently authored. **No reference repository
code, demo assets, branding, navigation or analytics is incorporated.**

| Effect | Reference studied | Adaptation |
| --- | --- | --- |
| Spatial photographic journey | [CurveGallery tutorial](https://tympanus.net/codrops/2026/07/07/building-a-scroll-driven-3d-gallery-using-a-blender-camera-path-with-three-js-and-gsap/) and [source](https://github.com/gaspoorf/curve-gallery) | Open chronological path and perspective depth; native scroll replaces the demo's unlimited Observer input; reading pauses, upright camera and safe photo retirement replace looping close passes. |
| Image between moving words | [Typography tutorial](https://tympanus.net/codrops/2024/04/02/on-scroll-expanding-image-animation-within-typography/) and [source](https://github.com/codrops/ImageExpansionTypography) | Measured word travel and reversible clipping; one portrait, CIRS words, 1.5 viewport heights of desktop travel; mobile keeps the heading above the image. |
| Inauguration horizontal blinds | [SVG mask tutorial](https://tympanus.net/codrops/2026/03/11/svg-mask-transitions-on-scroll-with-gsap-and-scrolltrigger/) and [source](https://github.com/Hiro-kiii/Scroll-Transition/) | Paired white SVG rectangles expand from each band's centre; height-based overlap prevents seams; viewBox follows viewport; the image uses `xMidYMid meet` and the underlying canvas fades away. |
| Composition benchmark | [Lusion](https://lusion.co/) | Homepage viewed; no proprietary implementation or branding accessed or reused. |

The CurveGallery repository tree had no explicit licence file; its code was
read for understanding and not reused. ImageExpansionTypography's
[licence](https://github.com/codrops/ImageExpansionTypography/blob/main/LICENSE)
and Scroll-Transition's [licence](https://github.com/Hiro-kiii/Scroll-Transition/blob/main/LICENSE)
are MIT. Their implementation was also not copied. The pre-existing vendored
Three.js runtime carries an MIT notice; existing GSAP, ScrollTrigger and Lenis
files and their notices are unchanged.

The live CurveGallery and ImageExpansionTypography demo URLs opened to a
Cloudflare “Just a moment...” verification screen in Chrome. The tutorials,
repository trees and relevant source files were accessible and inspected before
implementation. An attempted Scroll-Transition GitHub Pages URL returned “Site
not found”; its tutorial and `js/script.js` horizontal-blind source were read.
These screenshots are access evidence, **not evidence of having seen those
blocked live animations**. Lusion's homepage opened in Chrome. Direct motion
equivalence to the blocked demos is unverified; no pixel-perfect claim is made.

## Photograph provenance

Source folder supplied by the user:
[school archive](https://drive.google.com/drive/folders/1udKHVQydLyfSdiO0ILlTW6_sKpOr2iSJ).
Originals used by the image cutting tool remain in the local review directory;
they and the review evidence are excluded from staged deployment.

| Photograph | Grounding and public caption boundary |
| --- | --- |
| [Collection on foot](https://drive.google.com/file/d/1hwLnhl-qm21F-NUtLYMaAdZan2G4BESe/view) | Visually inspected. Supplied for the fundraising chapter. The caption does not identify the people or infer the photo date. The 1984 account and Swami Sahayanandaji's one rupee from each individual are grounded separately in [the school's published history](https://cirschool.org/history.html). |
| [Inauguration](https://drive.google.com/file/d/1XvYfF_NTKD1TYHTh5cIyUqWU_FSrGLcM/view) | The photograph's legible plaque names Thursday, 6 June 1996, Pujya Swami Chidanandaji and the presence of Swami Tejomayananda. This corroborates the published history. After inspecting that evidence, the user explicitly approved using this supplied photograph. |
| [British Council award](https://drive.google.com/file/d/113adXqrb5_9xUv9lZbs_NOcps9MFcRG3/view) | The certificate visibly names CIRS and the award. The existing school-supplied 2011 record is retained. The caption explicitly leaves the photograph's date and pictured people's identities unrecorded; it does not derive them from the filename. |
| [Poland collaboration](https://drive.google.com/file/d/1sbEgPvkKlsMM9_MO_ys1gvk1x1IUnCsM/view) | A readable classroom whiteboard names the CIRS–Poland advertising project and February 2014, corroborating the existing newsletter record. |
| Existing Gurudev, Vision Award and document exhibits | Existing source records and captions retained. Undated portraits are labelled as such. Historical document pages remain documents, not invented event photographs. |
| Campus opening/arrival | Existing school assets `forest-air.jpg` and `campus-band.jpg`. Presented as the campus today, never as 1970s or 1984 photographs. |
| Gurudev with Guruji and fellow students | [Chinmaya Mission's Guruji biography](https://www.chinmayamission.com/global/swami-tejomayananda). Context for the founding vision; photograph date unrecorded, with no school occasion inferred. |
| Sidhbari memorial | [Chinmaya Archives](https://archives.chinmayamission.com/sidhbari-samadhi-sthal). Explicitly captioned as Gurudev's Samadhi Sthal at Sidhbari; not presented as a photograph of the 1993 ceremony. |
| Guruji portrait | The official Guruji biography above. Context portrait of the project leader; not presented as a construction photograph from 1994. |
| 2025 chapter | First page of the school's published Annual Report, 7 October 2025. Replaces the repeated contemporary campus image. |
| Archive closing | The existing `campus-lawn.jpg` courtyard photograph, on every viewport. Distinct from the arrival and opening photographs. |

Other inspected supplied files were not assigned to an event solely by their
filenames. No historical photographs were generated or fabricated. No unsupported
1979 land-identification claim was introduced.

## Verification evidence

Evidence lives in `review/school-history-cinematic/`.

- Full site build completed. School History's generated output equals a fresh
  call to the generator and is stable on repeat generation.
- Repository-wide `html-validate@11 *.html`: passed.
- Syntax checks on both new modules and the archive controller: passed.
- `git diff --check`: passed (Git notes only normal Windows line-ending conversion).
- Record preservation and every link/anchor on the History page: passed;
  `content-results.json` reports 24 original, 31 current and 31 remote-main
  records, with no scoped link errors.
- Staging completed with 71 pages and 2002 assets. A staged-site browser visit
  to `#chapter-opening` loaded the 3D scene with no missing assets or page errors.
- Chrome at **1440×900**, **1024×768** and **390×844**: hero, expansion,
  photographic chapters, fundraising, inauguration, arrival, complete record,
  backward navigation, search, filtering and dialogs inspected. All report no
  horizontal overflow and no page/network errors. Direct navigation lands at
  the correct chapter. Tablet text fits above the timeline.
- Reduced motion, WebGL creation failure, lost context and JavaScript disabled:
  same 31 records and readable HTML/photo content. Direct chapter and record
  links checked. Keyboard Enter activates chapter navigation and returns focus
  to its reading panel. Escape closes record dialogs. Native disclosures work.
- Forward/reverse partial-mask screenshots exist. Corresponding SVG segment
  heights matched exactly after settling (0px difference); bands overlap at
  full opening. Zero world draw calls occurred during the checked idle interval.
- Conservative desktop hero background-pixel contrast after the gradient fix:
  label **7.61:1**, heading **7.13:1**, introduction **8.96:1**, links **8.71:1**.
  These readings concern the sampled desktop composition, not every viewport.
  The final scene caption also has a local dark backdrop to keep it readable
  against the inauguration photograph's pale stone.
- A 720×450 CSS viewport provides a 200%-zoom layout equivalent for the 1440×900
  layout: no overflow and normal-flow content. Browser UI zoom itself was not tested.
- A three-second diagnostic scroll sampled 301 browser animation callbacks,
  median 10ms/p95 10.1ms intervals, on Chrome's NVIDIA GeForce GT 710 renderer.
  This is a browser callback diagnostic, **not a representative-device rendered
  frame-rate guarantee**. Mobile device hardware, Firefox and Safari were not tested.

Main evidence: `1440-hero.png`, `1440-expansion.png`,
`1440-chapter-rupee.png`, `1440-chapter-opening.png`,
`1440-chapter-later.png`, `1440-present.png`, `1440-archive.png`,
tablet/mobile equivalents, `mask-partial-forward.png`,
`mask-partial-reverse.png`, `reduced.png`, `webgl-failure.png`,
`no-js.png`, `context-loss.png`, `deep-link.png`, `staged-inauguration.png`
and **`desktop-motion.webm`**. Exact browser results are in
`browser-results.json` and `motion-accessibility-results.json`.

### Existing repository check limitations

On the initial implementation checkout, the full link checker reported
**41 unused Experience image derivatives**.
All are already tracked in HEAD, outside this change, and none is a School
History broken link. They are preserved; the check is not weakened. See
`link-check.txt`.

The initial working tree was clean, but a full build also changed `why-cirs.html`
because its checked-in output does not match this branch's generator settings
(cache suffix, jump control and script inclusion). That unrelated generated
change was restored. Why CIRS sources and other routes remain untouched.
That initial checkout had a whole-repository generated-output discrepancy;
School History's repeat-build check passed. The authorised release integrates
the scoped change onto current main. Its full link check passes: **95 pages,
14,563 references**, with no orphan errors. Why CIRS and other generated routes
remain unchanged from current main after the release build.

## Distinct-image correction

The owner reported the portrait repeated on neighboring planes. The controller
had borrowed the first chapter's portrait for chapters with no image and also
reused the arrival campus image in the recent chapter. The correction removes
both overrides and supplies the distinct, attributed exhibits listed above.
The original close portrait appears only in the typography expansion. Source
generation asserts unique chapter assignments; the WebGL scene rejects repeated
image assignments, including small/large aliases, and uses the readable fallback.

Archive records retain every original account, exhibit caption and citation.
Where an exhibit already appears in a chapter, its record links to the full image
instead of displaying it again. Other exhibits appear once in the archive; the
dialog moves that original figure into its view and restores it on close or
previous/next navigation. Thumbnail copies are removed. The site's repeated
brand emblem is outside this photographic rule. The SVG inauguration mask and
its normal-flow fallback are two rendering modes of the same presentation.

Official source masters and exact URLs are retained in
`assets/source/history-distinct/provenance.json`; source masters stay outside
the deployment. The cutting tool requires Pillow and PyMuPDF only when remaking
images; the site's build retains its existing dependencies.

Correction evidence is in `review/school-history-cinematic/distinct-images/`.
The rendered page has 21 distinct image elements excluding the brand emblem,
with distinct normalized pixel fingerprints and a visually inspected contact
sheet. All nine chapters have distinct exhibits. Browser checks cover 1440×900,
1024×768, 390×844 and 768×1024, search/reset, Escape/Back, modal figure identity,
previous/next restoration, reduced motion, no JavaScript, WebGL failure, context
loss and chapter deep links. All 31 complete record objects match the previous
release, including captions and citations. Build, link, HTML and JS checks pass;
staging includes all 21 images and the dynamically imported scene.
