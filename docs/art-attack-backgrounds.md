# Art Attack backgrounds and decorative graphics

> These notes record the earlier isolated implementation and checks. The combined release, upstream reconciliation and fresh verification are documented in `docs/merged-redesign-release.md`.

Local branch `codex/art-backgrounds-20260930` in `D:/CIRS-Art-Backgrounds-20260930`, based on fetched `origin/main` at `cc805a95`. The dirty primary checkout and earlier coordinated worktree were left untouched. No merge, push or deployment.

Live inspection: `https://cirs-website.vercel.app/art-attack`, browser captures at 1440×900, 768×1024 and 390×844. The page has the supplied six-second scrubbed film, Made by Hand opening, artwork wall, warm/cool artwork ribbons, studio, Wall Magazines, stage, exhibition and closing links. This pass preserves that sequence. Live navigation/assets were inspected; the text-extraction web tool could not access the URL, so Chrome supplied the live evidence.

Preview: http://127.0.0.1:8918/art-attack.html
Screenshot review: http://127.0.0.1:8918/review/art-backgrounds/index.html

## Changes

* Rich plum `#21132F` for the title and selected text sections; warm cream `#F5EBDD` and calm near-cream around artwork; muted lilac for the studio and artwork ribbons. Selective lilac `#BDA1E5`, coral `#EF806E`, ochre `#D8A43B` and teal `#427E80` studio marks replace the previous coloured washes and rainbow ribbon gradients.
* Original SVG paper shapes, broad paint marks, daubs, charcoal curves, pencil hatching and registration details. The strongest composition frames the existing Art Attack title; smaller marks occupy introduction padding and gallery margins; a fuller closing composition stays away from link text.
* Hero decoration fades out at the start of the existing film scrub and returns over its completed title composition. Film files, timing and seeking controller are unchanged. Selected SVG layers move only 4–6 px. Three brush reveals and two curve draws use the existing GSAP/ScrollTrigger instance. No new scroll controller or library.
* Decorative wrappers and SVGs are aria-hidden, unfocusable and pointer-transparent. Absolute, reserved layers do not change content geometry. Mobile has its own hero composition, hides gallery hatching and the secondary opening decoration, and simplifies the closing marks. CSS remains static if scripts fail; GSAP matchMedia restores complete decoration for reduced motion, including a change during a visit.

## Sources and scope

`assets/css/artattack.css`: scoped surface, contrast and decorative positioning rules.
`assets/js/artattack.js`: original interaction code retained; separate decorative motion block appended.
`tools/pages/art-attack.html`: decoration placeholders only; all existing markup and copy remain.
`tools/art-decor/*.svg`: nine original authored source graphics, inlined at build time; no third-party illustrations, emoji, art replacements or new image downloads. Grain uses SVG turbulence. These are build sources, not unreferenced public artwork assets.
`tools/artattack.py`: whitelisted SVG expansion only; original source manifest and gallery generators unchanged.
`tools/build-site.py`: Art Attack-only title/seam hooks and asset cache suffix.
`art-attack.html`: generated output. Every other generated page is unchanged.

## Verification

* Build, JS syntax, repository HTML/a11y lint and `git diff --check` pass. Link check: 95 pages, 14,546 references, all resolve. Rebuild preserves SHA-256 for all 140 tracked HTML files.
* Browser comparison against baseline HTML/CSS/JS: identical section widths, heights and document positions at all three viewports. No overflow, runtime error or failed asset response in the verified states.
* Main text, main links and complete artwork/photo markup remain identical after removing decoration. All 294 original image elements and all 227 collection works remain; the larger introductory total is existing supplied copy. Source artwork/photo files and proportions are unchanged.
* Gallery: Show More goes from 30 to 60; painting and Issue 32 filtering work; Enter opens the viewer, ArrowRight changes artwork, Escape closes it and restores focus at all three widths.
* Film seeking reaches approximately 3 seconds midway and 5.97 seconds at the final hold. Decorative opacity is 0 during the film and 1 at the final title and after reversing to the opening; the existing film remains visible.
* All 12 decorative wrappers are aria-hidden and pointer-transparent. Dynamic reduced motion restores full strokes and the static hero; initial reduced-motion and disabled-JS mobile fallbacks retain the title and all artwork content.

Evidence: `review/art-backgrounds/verification.json`, `preservation.json`, `repeat-build.json`, `build.log` and actual before/after viewport PNGs. Local Chrome/Playwright responsive checks, not physical-device or screen-reader certification. The agent-browser CLI was unavailable in this runtime, so the installed Playwright/Chrome browser was used.

## Video-first follow-up

The title/decorative starting screen and scroll-scrub runway have been removed at the user’s request. The supplied six-second film now starts immediately with muted autoplay, playsinline and native keyboard-accessible controls. Its existing poster is preloaded; the film is contained rather than cropped. Reduced motion pauses autoplay while leaving explicit playback available. Offscreen playback pauses, and a visitor’s manual pause is retained after scrolling. No media file was changed. The previous verification above records the original background-only pass; the current opening is verified separately at `review/art-backgrounds/video-start/verification.json`. The 227-work collection, existing first content section, photographs and decorations below the film remain. Current preview: http://127.0.0.1:8921/art-attack.html. The coordinated preview has the same direct opening, with its original selected artworks retained below the film instead of a title preface. No merge or deployment was performed.
