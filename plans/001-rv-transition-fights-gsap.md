# 001 — Stop the `.rv` CSS transition fighting the GSAP reveal tween

- **Status**: TODO
- **Commit**: a3a6ac2
- **Severity**: HIGH
- **Category**: Performance / Cohesion
- **Estimated scope**: 2 files, ~6 lines

## Problem

Every reveal on the site is smeared by a CSS transition that duplicates the
GSAP tween on the same two properties.

```css
/* assets/css/cirs.css:1199 — current */
.rv{ transition:opacity .8s var(--e), transform .8s var(--e); }
```

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

`gsap.from()` writes inline `opacity` and `transform` on every frame. Because
`.rv` declares a transition on exactly those two properties, each of those
~57 per-second writes starts a fresh 800ms transition from the element's
current computed value. The element never tracks the tween: it lags behind it,
and the `power3.out` curve the author chose is re-filtered through
`cubic-bezier(.22,.61,.36,1)` on every frame, so the reveal neither lands when
GSAP thinks it has landed nor carries the easing it was given.

The declaration is vestigial. The comment two lines above it says so:

```css
/* assets/css/cirs.css:1197 — current */
/* GSAP sets the start state itself via from(), so nothing is hidden in CSS.
   If the library never loads, the page simply renders. */
```

Nothing in CSS hides `.rv`, so there is no state for a CSS transition to
animate — except on one path, which this plan preserves. `startSweep()` and
`failOpen()` (`assets/js/cirs.js:1502` and `:1548`) are fail-safes that make
stranded elements visible with a synchronous `gsap.set()`. Today the `.rv`
transition softens that into a fade; deleting it outright would make those
rescues pop. So the transition moves behind a class that only those two
fail-safes apply.

54 elements on `founder.html` carry `.rv`, and the class is used on every page
of the site.

## Target

```css
/* assets/css/cirs.css:1199 — target */
/* GSAP owns the reveal: it writes inline opacity and transform every frame,
   so a transition on those properties here would retarget once per frame and
   smear the tween. The only path that needs a transition is the fail-safe
   sweep below, which reveals a stranded element with a synchronous set() —
   startSweep() and failOpen() in cirs.js add .is-shown for exactly that. */
.rv.is-shown{ transition:opacity .45s var(--e); }
```

```js
/* assets/js/cirs.js — target, inside startSweep() */
    function show(el) {
      el.classList.add("is-shown");
      gsap.set(el, { opacity: 1, y: 0, yPercent: 0, clearProps: "clipPath" });
    }
```

```js
/* assets/js/cirs.js — target, inside failOpen() */
    $$(".rv, .img-reveal, .facilities > div").forEach(function (e) {
      e.classList.add("is-shown");
      e.style.opacity = "1"; e.style.transform = "none"; e.style.clipPath = "none";
    });
```

The new transition covers `opacity` only. Transform is deliberately left out:
a fail-safe is an emergency reveal, and AUDIT §6's principle — keep the
opacity feedback, drop the movement — applies to it as much as to reduced
motion.

## Repo conventions to follow

- Easing tokens live at `assets/css/cirs.css:79`: `--e: cubic-bezier(.22,.61,.36,1)`
  and `--e2: cubic-bezier(.16,1,.3,1)`. Use `var(--e)`, never a literal curve.
- State classes in this codebase are `is-`-prefixed: `is-stuck`, `is-open`,
  `is-big`, `is-on`, `is-seen`, `is-active`. `is-shown` matches.
- Exemplar of a transition correctly owned by CSS alone (no GSAP writes to the
  same properties): `assets/css/cirs.css:315`, the drawer.

## Steps

1. In `assets/css/cirs.css`, replace line 1199 with the target block above —
   the four comment lines and the `.rv.is-shown` rule. Leave the reduced-motion
   block at lines 1200–1203 exactly as it is.
2. In `assets/js/cirs.js`, in `startSweep()`, add
   `el.classList.add("is-shown");` as the first statement of `show()` (the
   function at line 1519), before the existing `gsap.set(...)` call.
3. In `assets/js/cirs.js`, in `failOpen()`, add `e.classList.add("is-shown");`
   as the first statement inside the `$$(".rv, .img-reveal, .facilities > div")
   .forEach` callback at line 1554, before the three `e.style` assignments.

## Boundaries

- Do NOT touch the reduced-motion block at `assets/css/cirs.css:1200–1203`.
  Its `.rv{opacity:1!important;transform:none!important}` is what makes the
  page complete without motion, and its `transition-duration:.001ms!important`
  correctly neutralises the new `.is-shown` transition too.
- Do NOT touch `assets/css/founder-journey.css:60`
  (`.founder-stop .rv{opacity:1!important;…}`). It is a separate concern,
  handled by plan 002.
- Do NOT change the GSAP tween at `assets/js/cirs.js:550–556` — not its
  duration, easing, `y` distance, or trigger. This plan removes the thing
  fighting that tween; it does not retune it.
- Do NOT add `.is-shown` anywhere else, and do not add it to `choreograph()`.
- Do NOT add dependencies. Do not edit any root `.html` file — they are
  generated (see CLAUDE.md).
- If a step does not match the code you find, STOP and report rather than
  improvising.

## Verification

- **Mechanical**:
  - `npx --yes html-validate@11 *.html` — passes.
  - `python3 tools/check-links.py` — passes.
  - `python3 tools/build-site.py` then `git diff --stat -- '*.html'`. This plan
    touches no HTML source, so the build must not change any root `.html`
    beyond what was already drifting before you started. **Note the
    pre-existing drift**: on this branch the build already rewrites
    `founder.html` (cache-buster `89-founder-15` → `94-founder-16`, and it
    drops a `<div class="progress">`). That drift is not yours. Run
    `git stash && python3 tools/build-site.py && git diff --stat -- '*.html'`
    first to record the baseline if you need to be sure.
- **Feel check**: serve the repo root (`python3 -m http.server 8000`) and open
  `http://localhost:8000/why-cirs.html`, which has `.rv` elements outside any
  journey. Scroll slowly and confirm:
  - Each block fades up and **settles**, rather than easing toward its final
    opacity for about a second after it has stopped moving.
  - In DevTools → Performance, record a scroll through the page. Selecting a
    revealing element during the tween shows inline `opacity`/`transform`
    changing with **no** entry in the Transitions track for it.
  - With the page open, run `document.querySelector('.rv').classList.add('is-shown')`
    in the console and confirm nothing visually changes (the class is inert
    until an element is actually hidden).
  - Toggle `prefers-reduced-motion: reduce` in DevTools → Rendering, reload,
    and confirm every `.rv` block is visible immediately and nothing moves.
- **Done when**: `grep -n '^\.rv{' assets/css/cirs.css` returns nothing,
  `grep -c 'is-shown' assets/js/cirs.js` returns 2, and a scrolled reveal
  visibly completes within its 0.95s tween instead of trailing past it.
