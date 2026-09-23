# 002 — Skip the scroll reveals the founder journey throws away

- **Status**: TODO
- **Commit**: a3a6ac2
- **Severity**: MEDIUM
- **Category**: Performance
- **Estimated scope**: 1 file, ~12 lines

## Problem

On a desktop founder page, `cirs.js` builds 14 ScrollTrigger instances and 14
tweens whose visual result is discarded before the visitor sees any of it.

```js
/* assets/js/cirs.js:550 — current */
    $$(".rv").filter(function (el) { return !el.classList.contains("crcard"); })
      .forEach(function (el) {
        gsap.from(el, {
          opacity: 0, y: 24, duration: .95, ease: "power3.out",
          scrollTrigger: { trigger: el, start: "top 90%", once: true }
        });
      });
```

`founder.html` carries 54 `.rv` elements. 14 of them sit inside the journey
section (lines 329–528 of the generated page); 13 of those 14 *are* the
chapter stops. Once `founder-journey.js` enhances, every one of them is
overridden:

```css
/* assets/css/founder-journey.css:60 — current */
  .founder .founders-journey.is-enhanced .founder-stop .rv{opacity:1!important;visibility:visible!important;transform:none!important}
```

So the tween runs and its output is thrown away. Worse than the wasted tween
is where the triggers live. `founder-journey.js` re-parents the stops into an
absolutely positioned 12200×6900 world inside a `position:sticky`,
19000px-tall container, and moves that world by transform:

```css
/* assets/css/founder-journey.css:24 — current */
  .founder .founders-journey.is-enhanced .founders-journey__world{position:absolute;left:0;top:0;width:12200px;height:6900px;z-index:1;transform:translate3d(0,0,0);transform-origin:0 0}
```

A `start:"top 90%"` computed against an element inside that world is
meaningless, and it is recomputed on every `ScrollTrigger.refresh()` — which
`founder-journey.js` fires on `load` (line 369), on `document.fonts.ready`
(line 370), and after every debounced resize (line 365). Each refresh
re-measures 14 elements that are `visibility:hidden` and positioned by a
transform the refresh cannot see through.

The reveals are also pointless *before* enhancement: the journey sets
`--stop-opacity` itself and `is-opening` forces the stops to `opacity:0` until
the camera reaches them.

## Target

A module-scope helper in `boot()`, used by both consumers of `.rv`. It repeats
the same test `founder-journey.js` makes, so the two cannot disagree:

```js
/* assets/js/cirs.js — target, immediately after the $$ definition at line 35 */
  // The founder journey re-parents its chapters into an absolutely positioned
  // world and overrides their reveals with !important (founder-journey.css:60),
  // so a ScrollTrigger built for one measures a position that does not exist
  // and re-measures it on every refresh. Skip them on exactly the viewports
  // the journey enhances — assets/js/founder-journey.js:10 makes the same test.
  // `animate` already covers the reduced-motion and missing-GSAP halves of it.
  var journeyRoot = document.querySelector("[data-founder-journey]");
  var journeyEnhances = !!journeyRoot && window.matchMedia("(min-width: 900px)").matches;
  function inEnhancedJourney(el) {
    return journeyEnhances && journeyRoot.contains(el);
  }
```

```js
/* assets/js/cirs.js:550 — target */
    $$(".rv").filter(function (el) {
        return !el.classList.contains("crcard") && !inEnhancedJourney(el);
      })
      .forEach(function (el) {
        gsap.from(el, {
          opacity: 0, y: 24, duration: .95, ease: "power3.out",
          scrollTrigger: { trigger: el, start: "top 90%", once: true }
        });
      });
```

```js
/* assets/js/cirs.js:1505 — target */
    var targets = $$(".rv, .img-reveal, .facilities > div, .line-mask > span, .fig-mask > span")
      .filter(function (el) { return !el.closest(".hero, .hseq") && !inEnhancedJourney(el); });
```

## Repo conventions to follow

- `cirs.js` gates every enhancement on capability flags computed once at the
  top of `boot()` (`reduced`, `hasGSAP`, `hasST`, `animate` — lines 27–30).
  `journeyEnhances` is another one of those and belongs beside them.
- Exemplar of the same pattern already in the file: `assets/js/cirs.js:43`,
  where Lenis is skipped for `body.wall` because the photograph wall owns its
  own scroll surface. Same shape of decision — one page's bespoke mechanism
  opts out of the shared one.
- `matchMedia("(min-width: 900px)")` must match `assets/js/founder-journey.js:10`
  character for character, including the space after the colon.

## Steps

1. In `assets/js/cirs.js`, insert the `journeyRoot` / `journeyEnhances` /
   `inEnhancedJourney` block from the target above directly after the `$$`
   definition at line 35 and before the `/* Smooth scroll */` comment block at
   line 37.
2. In `choreograph()`, change the filter callback at line 550 to the target
   form — add `&& !inEnhancedJourney(el)` to the existing `crcard` test.
3. In `startSweep()`, change the filter callback at line 1506 to the target
   form — add `&& !inEnhancedJourney(el)` to the existing `.hero, .hseq` test.

## Boundaries

- Do NOT change the `[data-split]`, `.img-reveal`, `.crcard`, `.fig-mask` or
  `.facilities` passes in `choreograph()`. The founder page has none of those
  elements inside the journey (verified at this commit), so filtering them
  would be dead code.
- Do NOT touch `assets/js/founder-journey.js`. This plan makes `cirs.js` stop
  doing work; it does not change what the journey does.
- Do NOT touch `assets/css/founder-journey.css:60`. The `!important` overrides
  stay — they are still needed for the window between `cirs.js` running and
  the journey enhancing, and for the 40 `.rv` elements outside the journey.
- Do NOT remove `.rv` from the founder page markup in `tools/pages/founder.html`.
  Those elements must still reveal normally on the mobile and reduced-motion
  path, where the journey renders as `is-static`.
- Do NOT edit any root `.html` file — they are generated (see CLAUDE.md).
- Do NOT add dependencies.
- If a step does not match the code you find, STOP and report rather than
  improvising.

## Verification

- **Mechanical**:
  - `node --check assets/js/cirs.js` — passes.
  - `npx --yes html-validate@11 *.html` and `python3 tools/check-links.py` — pass.
  - `python3 tools/build-site.py` then `git diff --stat -- '*.html'` — no
    change beyond the `founder.html` drift that already exists on this branch
    (cache-buster `89-founder-15` → `94-founder-16` plus a dropped
    `<div class="progress">`). That drift is not yours.
- **Feel check**: serve the repo root (`python3 -m http.server 8000`) and open
  `http://localhost:8000/founder.html` in a window **wider than 900px**:
  - In the console, `ScrollTrigger.getAll().length` should drop by 14 compared
    with the same page before the change. Record both numbers.
  - Scroll the whole journey. Every chapter must still appear, the camera must
    still track the route, and the year, heading, copy and photograph must
    behave exactly as before — this plan must be invisible.
  - Resize the window horizontally several times and confirm no chapter is
    left blank or stuck, and no console error appears.
  - Now narrow the window below 900px and reload. The journey renders
    `is-static`, and every chapter **must** fade up on scroll as an ordinary
    reveal — if they appear instantly, `journeyEnhances` is wrong.
  - Toggle `prefers-reduced-motion: reduce`, reload wide. The journey is
    `is-static` and everything is visible immediately.
- **Done when**: `ScrollTrigger.getAll().length` on a >900px `founder.html` is
  14 lower than before, the journey is visually unchanged, and the <900px and
  reduced-motion paths still reveal.
