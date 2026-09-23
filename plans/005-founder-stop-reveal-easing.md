# 005 — Put the founder chapter reveal on the repo's easing token

- **Status**: TODO
- **Commit**: a3a6ac2
- **Severity**: MEDIUM
- **Category**: Easing & duration / Cohesion
- **Estimated scope**: 1 file, 2 lines

## Problem

The reveal that carries every chapter of the founder journey uses the
browser's built-in `ease`, in a file whose every other value is deliberate.

```css
/* assets/css/founder-journey.css:61 — current */
  .founder .founders-journey.is-enhanced .founder-stop .fcopy,
  .founder .founders-journey.is-enhanced .founder-stop h2,
  .founder .founders-journey.is-enhanced .founder-stop h3,
  .founder .founders-journey.is-enhanced .founder-stop figure{transition:transform .35s ease,opacity .35s ease}
  .founder .founders-journey.is-enhanced .founder-stop:not(.is-seen) .fcopy,
  .founder .founders-journey.is-enhanced .founder-stop:not(.is-seen) h2,
  .founder .founders-journey.is-enhanced .founder-stop:not(.is-seen) h3,
  .founder .founders-journey.is-enhanced .founder-stop:not(.is-seen) figure{transform:translateY(18px)!important;opacity:.55!important}
```

Two things are wrong with it.

**The curve.** This is an entrance: content rises 18px and lifts from 0.55
opacity to 1 as the camera arrives at a chapter. AUDIT §2 puts entrances on
`ease-out`, and notes that CSS's built-in curves are too weak for deliberate
motion. `ease` is `cubic-bezier(.25,.1,.25,1)` — nearly symmetric, so the
content drifts in with no attack. Everything it moves against is strongly
eased: the camera interpolation, the route draw, the background crossfades.

**The token.** `assets/css/cirs.css:79` defines `--e` and `--e2` on `:root`,
and `founder-journey.css` loads after `cirs.css` on this page, so both are in
scope. Using a built-in here is the one place in the journey that opts out of
the site's motion vocabulary.

`.35s` is fine and stays — it is inside AUDIT §2's budget for an element of
this weight and matches the pace of the camera move it accompanies.

## Target

```css
/* assets/css/founder-journey.css:64 — target */
  .founder .founders-journey.is-enhanced .founder-stop figure{transition:transform .35s var(--e2),opacity .35s var(--e2)}
```

`--e2` is `cubic-bezier(.16,1,.3,1)` — a strong ease-out. It is the curve this
codebase already reaches for when something arrives: the nav drawer
(`assets/css/cirs.css:315`), the admissions rail fill
(`assets/css/admissions.css:123`), the programme card zoom
(`assets/css/cirs.css:466`).

Additionally, close the seam this rule leaves open. `.flife__yr` — the 6rem
year that is the loudest element in most chapters — is not in the selector
list, so it has no transition at all while the copy and figures beside it
fade. Add it:

```css
/* assets/css/founder-journey.css:61 — target: one selector added to the list */
  .founder .founders-journey.is-enhanced .founder-stop .fcopy,
  .founder .founders-journey.is-enhanced .founder-stop .flife__yr,
  .founder .founders-journey.is-enhanced .founder-stop h2,
  .founder .founders-journey.is-enhanced .founder-stop h3,
  .founder .founders-journey.is-enhanced .founder-stop figure{transition:transform .35s var(--e2),opacity .35s var(--e2)}
```

Do **not** add `.flife__yr` to the `:not(.is-seen)` block below it. The year
should fade with its chapter, not start displaced — adding it to the offset
rule would make the largest element on screen the one that moves furthest,
which inverts the hierarchy.

## Repo conventions to follow

- Easing tokens on `:root` at `assets/css/cirs.css:79`:
  `--e: cubic-bezier(.22,.61,.36,1)` (general), `--e2: cubic-bezier(.16,1,.3,1)`
  (arrivals, stronger). Never a literal curve, never a built-in keyword for
  movement.
- Exemplar: `assets/css/cirs.css:315` — the drawer, `--e2` on both `opacity`
  and `transform` at the same duration.
- `founder-journey.css` is written compactly: one selector per line, no space
  after colons or commas inside a declaration block, no trailing semicolon
  before `}`. Match it exactly and do not reformat neighbouring rules.
- `.flife__yr` is already styled inside this same media query at
  `assets/css/founder-journey.css:74`, so the class is in scope here.

## Steps

1. In `assets/css/founder-journey.css`, replace `ease` with `var(--e2)` in
   both places on line 64 — the rule ending
   `figure{transition:transform .35s ease,opacity .35s ease}`.
2. In `assets/css/founder-journey.css`, add the line
   `  .founder .founders-journey.is-enhanced .founder-stop .flife__yr,`
   to the selector list immediately above it, between the `.fcopy` selector on
   line 61 and the `h2` selector on line 62.

## Boundaries

- Do NOT change the `.35s` duration.
- Do NOT change the `translateY(18px)` or `opacity:.55` values in the
  `:not(.is-seen)` block at lines 65–68, and do NOT add `.flife__yr` to it.
- Do NOT touch the `:not(.is-active)` block at lines 69–71, which hard-hides
  non-current chapters — that is what stops adjacent dates bleeding through
  the enlarged photographs, and it is deliberate.
- Do NOT touch `.founder-stop{...transition:none!important}` at line 53. The
  container must stay uncontrolled by CSS; its opacity is driven by
  `--stop-opacity` from `assets/js/founder-journey.js:243`.
- Do NOT change `.route-base{transition:opacity .25s ease}` at line 29. `ease`
  on a pure opacity fade is correct per AUDIT §2 and is out of scope.
- Do NOT edit any root `.html` file — they are generated (see CLAUDE.md).
- If a step does not match the code you find, STOP and report rather than
  improvising.

## Verification

- **Mechanical**:
  - `npx --yes html-validate@11 *.html` and `python3 tools/check-links.py` — pass.
  - `python3 tools/build-site.py` then `git diff --stat -- '*.html'` — no
    change beyond the `founder.html` drift that already exists on this branch.
  - `grep -c 'ease}' assets/css/founder-journey.css` returns 1 — the remaining
    one is `.route-base` at line 29, which is out of scope and stays.
- **Feel check**: serve the repo root (`python3 -m http.server 8000`), open
  `http://localhost:8000/founder.html` wider than 900px, and scroll into the
  journey:
  - Chapter copy should now **arrive** — moving fastest at the start of its
    18px rise and settling — rather than drifting in at an even rate. Compare
    directly: in DevTools, set the transition back to `ease` on one element and
    scrub past two chapters to feel the difference.
  - In DevTools → Animations, set playback to 10% and pass a milestone. The
    year, heading, copy and photograph must all move on the same curve and
    land together; nothing should still be settling after the others have
    stopped.
  - Watch `.flife__yr` specifically. Before this change it cut; it should now
    fade with its chapter and must **not** slide up from 18px — if it moves
    vertically, step 2 was applied to the wrong selector list.
  - Scrub **backwards** through several chapters quickly. Because these are
    transitions rather than keyframes they must retarget from wherever they
    are; nothing should restart from 0.55 opacity mid-flight.
  - Toggle `prefers-reduced-motion: reduce` and reload: the journey renders
    `is-static` and none of this applies.
- **Done when**: no `ease` keyword remains on a transform in
  `assets/css/founder-journey.css` (only the `.route-base` opacity fade at
  line 29 still uses it), chapter content arrives on `--e2`, and the
  year fades with its chapter instead of cutting.
