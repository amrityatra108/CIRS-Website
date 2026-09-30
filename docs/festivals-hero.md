# Festivals opening hero

> These notes record the earlier isolated implementation and checks. The combined release, upstream reconciliation and fresh verification are documented in `docs/merged-redesign-release.md`.

Implemented locally on `codex/festivals-hero-20260930`, based on `origin/main` at `c839b961`. No merge or production deployment was performed.

The opening now uses the requested real two-line heading, eyebrow, paragraph and scroll link. Compact Bodoni typography, warm ivory text and a directional lower-left shade preserve the supplied warm scene. The native, muted, inline film plays once, then holds its final frame. The supplied final rangoli image is already visible underneath; video failure, reduced motion and JavaScript failure retain that image and readable copy.

Desktop uses a left-aligned cover crop selected against decoded film frames. Tablet and mobile contain the full 16:9 scene above the copy, with restrained edge fades. The hero uses `100svh`; short mobile viewports can scroll normally. A single 1.31-second entrance fades the eyebrow, raises the two masked heading lines by 24px, then reveals the paragraph and link. No character animation, new scroll controller or decorative imagery was added.

The shared header controller accepts an optional `data-header-hero` boundary. Only Festivals supplies it, keeping the original navigation transparent and ivory while over the hero, then restoring the existing scrolled treatment. Other pages retain their existing thresholds. The obsolete opening curtain and 460vh scroll-scrub runway are removed only from Festivals. The first introduction follows immediately with a plum transition, and the scroll link lands below the header.

## Preservation and verification

- The seven existing content sections have identical rendered markup and factual copy. The seven festival chapters, 22 archive photographs, filters and viewer remain intact.
- SHA checks confirm the MP4, WebM, original poster and final still are unchanged.
- Chromium checks at 1440 × 900, 768 × 1024 and 390 × 844 passed: heading layout, no horizontal overflow, transparent/scrolled navigation, keyboard focus, scroll-link landing, menu open/Escape, gallery filtering and viewer next/Escape/focus return.
- Muted autoplay/playsinline playback, pause when fully offscreen, completed-film hold, reduced motion, disabled JavaScript, blocked video and blocked page script were checked. No runtime errors or failed normal asset responses were recorded.
- Actual poster and decoded video frames at 0, 1.2, 2.5 and 4.95 seconds were sampled for contrast. Minimum sampled contrast was 3.79:1 for the large heading and 11.23:1 for supporting text/navigation. See `review/festivals-hero/contrast.json` for the method and per-viewport results; this is sampled image contrast, not a certification for every frame or device.
- A 200% desktop zoom layout equivalent (720 × 450 CSS pixels at device scale 2, representing a 1440 × 900 display) passed without overflow. This was a viewport simulation, not native browser zoom. The screenshot review's links and mobile layout also passed.
- Generated build, repository link checking, HTML validation, JavaScript syntax and whitespace checks passed. Repeat-build results are recorded in `review/festivals-hero/repeat-build.json`.
- Shared-header regression checks passed on Art Attack, Math Challenge and School Information. Spiritual Life and the primary checkout's unrelated edits were untouched.

Review the actual preview at `http://127.0.0.1:8919/festivals.html` and the screenshot index at `http://127.0.0.1:8919/review/festivals-hero/`.

Evidence is local Chromium testing. Physical mobile devices and production deployment were not tested.
