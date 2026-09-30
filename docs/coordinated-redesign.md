# Coordinated CIRS redesign

> These notes record the earlier isolated implementation and checks. The combined release, upstream reconciliation and fresh verification are documented in `docs/merged-redesign-release.md`.

Local worktree: `D:/CIRS-Coordinated-20260930`, branch `codex/coordinated-redesign-20260930`, based on main fetched for this task, `ce976d57`. School History source work ported from `46c0d4b5`; template conflicts resolved and generated output rebuilt. The user's primary checkout and its other ongoing edits were not modified. No merge or publication performed.

Spiritual Life is excluded at the user's explicit request. Its template, scripts and generated HTML match the worktree baseline; the coordinated stylesheet and script are not loaded on that route. The earlier isolated draft edits were removed.

Local preview: http://127.0.0.1:8917/math-challenge.html. Screenshot review: http://127.0.0.1:8917/review/coordinated/index.html.

## Inspection and implementation notes

Browser captures and forward/reverse scroll observations are in `review/coordinated/references.json`, `references-deep.json`, and `ref-*.png`.

* [Momento Legal](https://momentolegal.com/): a gold watch occupies the opening against a dark ground; oversized object details dominate the hero, then a column becomes secondary to an offset reading composition. Adapt the object scale, depth and move-aside behaviour to an original illustrative CIRS ₹1 coin. Never present it as a photographed historical coin.
* [Curve Gallery](https://tympanus.net/Tutorials/CurveGallery/) and the [mask tutorial](https://tympanus.net/codrops/2026/03/11/svg-mask-transitions-on-scroll-with-gsap-and-scrolltrigger/): direct browser visits show “Just a moment…” and cannot scroll. The [camera tutorial](https://tympanus.net/codrops/2026/07/07/building-a-scroll-driven-3d-gallery-using-a-blender-camera-path-with-three-js-and-gsap/) is readable as text. Retain the existing independently authored finite open Catmull–Rom journey and reversible SVG strips. Direct demo comparison remains blocked; do not claim exact reproduction.
* [Hex Pens](https://www.hexpens.com/): clear hand, pen and paper fill the photographic hero; serif display and handwritten linking word sit over it. No suitable CIRS close-up writing film is identified in the repository. Use an original ink-and-paper composition containing only supplied poem text; no stock footage.
* [Benxrun](https://www.benxrun.com/01-look/): cinematic illustrated opening reduces toward a luminous object on scrolling; subsequent reading is a still, narrow serif column with persistent left chapter navigation. Custom entry scroll initially holds the page at zero; continued wheel input eventually exposes the reading column. Adapt the opening-to-reading rhythm, readable width and chapter navigation using campus images and real article sections, without the long dark pause or illustrated fictional assets.
* [OpenHome](https://openhome.com/): the left headline stays fixed while right feature panels tilt/change; a 1–4 indicator changes beside the panels. Adapt to four academic chapters with stable reading intervals and original image transitions. Mobile becomes normal flow.
* [Lee Holmes](https://www.leeholmes.uk/): pixelated display type resolves; project images and small compositions overlap the opening and continue in irregular project spreads. Use one brief fragmented title entrance, actual student-art layers spreading apart, then an undistorted gallery.
* [Magic Receipt AI](https://magic-receipt.ai/): a paper arrives inside a bracketed grid workspace, a scanning line crosses it, analysis advances and the result follows. Adapt the workspace, scan and ordered reveal to accessible mathematical construction, without financial language. Preserve the existing sculpture scene.
* [Webtactics](https://webtactics.org/): this inspection renders the concept-work cards and numbered process, but has not demonstrated a numbered archival image-transition sequence. Use the numbered archive direction with a clearly original vertical wipe between achievement photographs. Do not attribute this wipe to Webtactics.

## Scoped visual system

Existing Bodoni Moda for object/feature display, Literata and EB Garamond for reading, Mona Sans for controls. No new font. Purple `#2b2037`, deep purple `#1e1626`, warm ivory `#faf9f3`, paper `#f4f0e6`, restrained gold `#d8b76a`. Math uses charcoal `#0D0E12`, secondary `#15161C`, ivory `#F4EFE5`, supporting `#BEB8AD`, gold `#D4AF62`, highlight `#F2D697` and a subtle radial centre `#242017`. Page identities: monumental object/archive; ruled manuscript; numbered photographic split; artwork collage; geometric scan; magazine/essay reading; achievement archive. Spiritual Life remains with its other contributor.

All enhancements use the existing `cirs.js` scroll controller. No second Lenis instance or duplicate library. Normal-flow HTML is the source of content; motion is enabled only after setup and media checks. Body paragraphs do not animate during reading. Native links/disclosures/dialogs retain fallbacks.

## Licence boundary

Original page implementation; no source copied from reference repositories, branding or media. Existing vendored Three.js MIT runtime, repository GSAP/ScrollTrigger 3.12.5 retained under their bundled GreenSock standard-licence notices; the existing Lenis runtime is unchanged. Existing self-hosted fonts retain their bundled licences. The new coin is authored SVG illustration.

## Delivered routes and source

| Route | Treatment | Main source |
| --- | --- | --- |
| `school-history.html` | Illustrative ₹1 object; existing finite 3D photo journey, masks and complete source archive | `tools/pages/school-history.html`, ported `history-cinematic-*.js/css`, `coordinated.*` |
| `creative-writing.html` and its edition/reader routes | Paper and pen opening with actual student verse; calm edition list, intact stanza reading | `tools/creativewriting.py`, `assets/js/cwriting.js`, `coordinated.*` |
| `curriculum.html` | Four academic chapters: stable desktop text, photographic transitions; normal mobile order | `tools/pages/curriculum.html`, `assets/js/curriculum.js`, `coordinated.*` |
| `art-attack.html` | Brief title fragmentation, original student-work collage spreading to a gallery; controllable, uncropped film | `tools/artattack.py`, `tools/pages/art-attack.html`, `coordinated.*` |
| `math-challenge.html` | Charcoal studio with preserved 216-block cube/field/torus and a source-backed 1729 demonstration | `assets/css/matharena.css`, `assets/js/matharena.js`, `assets/js/math-sculpture.js`, `tools/pages/math-challenge.html`, `coordinated.*` |
| `crossroads.html` | Original title/intro and complete archive; genuine Issue 32 cover and contents paper reveal | `tools/pages/crossroads.html`, `assets/img/crossroads/issue-32-inside.webp`, `coordinated.*` |
| `anakin-skywalker.html`, `death-of-rationalism.html`, `voyages-in-the-yuva-kendra.html` | Relevant supplied image and excerpt, still reading; chapter navigation uses only printed section headings | `tools/build-site.py:article_html`, `coordinated.*` |
| `our-laurels.html` | Genuine achievement opening and eight numbered category chapters; source stories expand; complete archive remains | `tools/laurels.py`, `tools/pages/our-laurels.html`, `assets/js/laurels.js`, `coordinated.*` |

`tools/build-site.py` owns asset inclusion, header mode, selected-essay rendering and generation. All root and nested HTML changes were generated. Unselected essays, the Blog newspaper landing, ordinary News reports, Home, Sports and Spiritual Life are byte-identical to the worktree baseline.

The original Art Attack opening address and title address still resolve. History record addresses, all writing poem/edition addresses, curriculum routes, results filters, magazine PDFs, and achievement record addresses remain available. The removed `lr-points` and `art-attack-critical` IDs belonged to a JSON data script and a stylesheet, respectively, rather than reading destinations.

## Math hero refinement

Before screenshots capture the brown/gold rendered worktree state immediately before the user's refinement request, rather than an inferred reconstruction of an attachment. After screenshots show the actual Chrome page at 1440×900, 1024×768 and 390×844.

The sculpture keeps its geometry, bevels and cube→field→torus correspondences. Physical material uses metalness 0.85, roughness 0.30 and per-block base variations around `#C49A48`. An original 256×128 HDR studio environment is generated locally and prefiltered once by PMREM. Broad warm reflections, neutral fill and restrained rim lighting create dimensional faces and edge highlights. Existing inner-layer occlusion remains. No downloaded environment, external licence dependency, bloom or shadow postprocessor was added.

Native shape buttons work with pointer and keyboard. Manual changes settle smoothly; real scrolling resumes the existing progression. The field receives a centred, text-free stage, including hidden/inert hero links, following the user's correction. Cube and torus restore the opening. Motion control exposes its active state for one gentle pulse and resets afterward. Desktop pointer movement restores the original local block response through the existing damped springs, alongside slight whole-sculpture rotation; the blocks settle back when the pointer leaves. Touch does not scatter blocks. Mobile uses normal flow. Reduced motion selects complete static poses, removes pulse and pinning, and works when toggled during a visit. Idle rendering stops until interaction, resize or scene progression requires it; no frame-rate measurement is claimed.

The demonstration is sourced from `pdf/maths newsletter dec 2016.pdf`, PDF page 2 / printed page 1, visually inspected before implementation. A deployable identical copy is linked at `assets/documents/math-challenge/december-2016-newsletter.pdf`. Independent calculation verifies `1³ + 12³ = 9³ + 10³ = 1729`. Four stages and the full static solution remain accessible.

## Verification evidence

* Build, repository HTML/a11y lint, JS syntax and `git diff --check` pass. `check-links.py`: 95 pages and 14,724 references, all resolve. Repeat build: all 140 tracked HTML source/output files have identical SHA-256 before and after rebuilding.
* Local staging succeeds: 95 public pages, 2,128 assets, about 603 MB (including the existing PDF/media archives). Review material is excluded from deployment. No deployment was made.
* Responsive browser captures cover 1440×900, 1024×768 and 390×844 for each treatment; there is no horizontal overflow or captured runtime/missing-asset error. Reduced-motion, disabled-JS and failed-WebGL checks keep reading content available. Desktop WebGL failure and dynamic reduced motion were additionally exercised for Math.
* Actual interaction evidence: all three sculptures render differently; keyboard Enter selects poses; Space activates pulse and its pressed state returns to false; results search produces its empty state and reset restores 25 bulletins. The field hides hero copy and links at every requested viewport.
* History record dialog, later-record control, Escape, focus restoration and a direct 2025 report address work. The illustrative coin returns exactly to its initial transform after forward/reverse scrolling. The 3D scene's existing readable fallback is retained.
* Another-line preserves focus and attribution; edition next-poem and Back work. The four academic chapters update their active index in both directions. Art expansion, next artwork, Escape, restored focus and native film playback work; the film remains `object-fit: contain`.
* Magazine contents reveal from 100% clipped to 0% and reverse to 100% on desktop; mobile shows both genuine pages in document order. All 32 issue PDFs remain in the archive. Essay section links reach the supplied headings and update their index.
* Laurels native story disclosure, category filtering (12 sport entries), dialog/Escape/focus and a chapter link that clears a hiding filter work; all 56 records return. There are no starfield canvases. Its old perpetual loop now updates on scroll/resize.
* Shared menu keyboard open/Escape/return focus pass at all three viewports. Home, News, Blog and Sports smoke checks show no overflow or runtime errors. The 200% equivalent desktop layout (720×450 CSS viewport at DPR 2) has no horizontal overflow across all redesigned primary routes and a selected essay; this is an emulated layout check, not a claim of native-browser zoom or screen-reader certification.
* Math text contrast: ivory on charcoal 16.83:1, supporting text on the radial centre 8.23:1, gold on charcoal 9.28:1, primary-button text 9.01:1.

Machine-readable evidence and original captures live in `review/coordinated/`: `*-results.json`, `content-preservation.json`, `math-hero-verification.json`, `integration-verification.json`, `final-motion.json`, `accessibility-smoke.json`, `repeat-build.json`, and the validator logs. `final-motion.json` uses the site's existing scroll bridge to complete and reverse transitions; it supersedes premature native-scroll captures taken while Lenis was still settling.

## Content reconciliation and limits

The baseline comparison preserves all published stanza markup, all complete article paragraphs (including the 17 supplied student essays), 227 artworks and credits, 56 laurels and their names/results/sources, 31 history records, and 25 winners' bulletins. No existing PDF/PPT link is lost. The maths newsletter and magazine preview page are the only new sourced document/image copies.

Creative Writing's supplied data contains five published three-poem editions (15 poems, 14 distinct writers), plus six July/August/September 2026 junior/senior slots awaiting material. No master collection or original PPT/PPTX is registered or found in the supplied repository. Existing replacement characters in poem punctuation were preserved instead of guessing corrections. This verifies preservation of the repository collection; it cannot certify that every school poem has been supplied. Missing dates, grades and titles remain missing.

Laurels source gaps remain held back as recorded in `tools/laurels.py:HELD`; no unsupported ranking, placing, year or attribution was promoted. Generic classroom/sports photographs explicitly identify their relationship to the listed results. The Issue 32 preview is a faithful rendered contents page, with all printed imagery and spelling retained.

Browser evidence is local Chrome/Playwright, with software WebGL enabled for deterministic scene checks. Physical iOS/Android devices, Safari, Firefox, screen readers, production deployment, and measured GPU frame rates are not tested. Direct Curve Gallery and mask demo inspection remain blocked as recorded above; there is no exact-reproduction claim. A documentary pen close-up and complete writing master archive would need authentic supplied material.

## Cursor interaction follow-up

Restored the original pointer source in the existing block-spring system, retaining the metallic treatment and smoother damping. Rendered checks at 1440x900, 1024x768, 768x1024 and 390x844 passed for all three shapes, settling after pointer exit, keyboard pulse, initial reduced motion, stable touch interaction, field copy hiding and overflow. No page errors were recorded. Test-only observations are injected by the review script; no debug hook ships in the asset. Evidence: `review/coordinated/math-pointer-verification.json`.

## Art Attack video-first follow-up

The initial title composition has been replaced by the supplied, uncropped film with muted autoplay and native controls. The five selected student artworks remain below the video as a normal gallery section, followed by the existing art-room photograph, text and complete collection. The original title fragmentation and collage pinning no longer precede the film. The page retains one real accessible h1, all media files, captions and 227 collection works. Desktop/tablet/mobile checks passed at 1440x900, 768x1024 and 390x844, covering video playback, keyboard pause/play, manual pause retention, offscreen pause, gallery keyboard controls, reduced motion and overflow. Evidence is in the companion Art worktree at `review/art-backgrounds/video-start/verification.json`. This follow-up supersedes the earlier title/collage opening description.
