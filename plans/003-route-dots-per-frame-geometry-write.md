# 003 — Stop rewriting the route dots' geometry on every scroll frame

- **Status**: TODO
- **Commit**: a3a6ac2
- **Severity**: MEDIUM
- **Category**: Performance (also closes a hard cut)
- **Estimated scope**: 2 files, ~10 lines

## Problem

The founder journey's `render()` runs on a GSAP scrub — once per frame for the
whole 19000px scroll — and writes an SVG geometry attribute on all 14 route
dots every time.

```js
/* assets/js/founder-journey.js:314 — current */
    state.dots.forEach((dot,index)=>{
      dot.classList.toggle("is-passed",index<=active);
      dot.classList.toggle("is-current",index===active);
      dot.setAttribute("r",index===active?"11":"8");
    });
```

`r` on an SVG `<circle>` is geometry, not a composited property. Setting it
invalidates the element's layout box and forces a repaint of that region of a
12200×6900 `<svg>`, and `setAttribute` writes unconditionally — the browser
cannot elide it even though the value is identical on all but one frame in
hundreds. That is 14 forced geometry invalidations per frame for a value that
changes only when the active chapter changes, roughly 13 times in the entire
page.

The same loop is also the reason the dots snap. `r` jumps 8 → 11 with nothing
to carry it, so each milestone marker pops to its new size in a single frame
while everything around it — the route draw, the camera, the backgrounds — is
continuous.

```css
/* assets/css/founder-journey.css:37 — current */
  .founders-journey__route .route-point{fill:var(--j-ivory);stroke:var(--j-gold-dark);stroke-width:2;vector-effect:non-scaling-stroke}
  .founders-journey__route .route-point.is-passed{fill:var(--j-gold)}
  .founders-journey__route .route-point.is-current{fill:var(--j-gold);stroke:var(--j-ivory);stroke-width:4}
```

## Target

`r` stays at the authored 8 forever. Size becomes a transform, which is
composited and can be transitioned, and the whole update moves into
`setActive()`, which already early-returns when the chapter has not changed.

```css
/* assets/css/founder-journey.css:37 — target */
  .founders-journey__route .route-point{fill:var(--j-ivory);stroke:var(--j-gold-dark);stroke-width:2;vector-effect:non-scaling-stroke;transform-box:fill-box;transform-origin:center;transition:transform .22s var(--e2),fill .22s var(--e2)}
  .founders-journey__route .route-point.is-passed{fill:var(--j-gold)}
  .founders-journey__route .route-point.is-current{fill:var(--j-gold);stroke:var(--j-ivory);stroke-width:4;transform:scale(1.375)}
```

`1.375` is `11 / 8` — the marker reaches exactly the size it reaches today.
`vector-effect:non-scaling-stroke` is already on the rule, so the 2px and 4px
strokes stay 2px and 4px through the scale; `transform-box:fill-box` is
required for `transform-origin:center` to mean the circle's own centre rather
than the SVG user-space origin.

```js
/* assets/js/founder-journey.js — target, inside setActive() */
  function setActive(index){
    index=Math.max(0,Math.min(stops.length-1,index));
    if(index===state.active) return;
    state.active=index;
    stops.forEach((stop,i)=>{
      stop.classList.toggle("is-active",i===index);
      if(i===index) stop.classList.add("is-seen");
    });
    // The dots change only with the chapter. Writing them from render() cost
    // 14 SVG geometry invalidations a frame for a value that changes 13 times
    // in the whole page.
    if(state.dots) state.dots.forEach((dot,i)=>{
      dot.classList.toggle("is-passed",i<=index);
      dot.classList.toggle("is-current",i===index);
    });
    period.textContent=periodFor(stops[index]);
    title.textContent=labelFor(stops[index],index);
    count.textContent=String(index+1).padStart(2,"0");
  }
```

```js
/* assets/js/founder-journey.js:314 — target: the forEach block is deleted */
    const active=activeForPosition(position,direction);
    setActive(active);
    setStopOpacities(position,progress);
    setIntroReveal(progress);
    if(progress<MAIN_START){period.textContent="1996";title.textContent="CIRS begins";count.textContent="00";}
    meter.style.transform="scaleX("+mainProgress+")";
    setBackground(mainProgress);
```

## Repo conventions to follow

- Easing tokens are on `:root` at `assets/css/cirs.css:79`:
  `--e: cubic-bezier(.22,.61,.36,1)` and `--e2: cubic-bezier(.16,1,.3,1)`.
  `founder-journey.css` is loaded after `cirs.css` on this page, so both are in
  scope. Never write a literal curve.
- `founder-journey.css` is written one rule per line with no spaces after
  colons or commas inside a declaration block. Match that — do not reformat
  the surrounding rules.
- Exemplar of the pattern this replaces: `assets/js/founder-journey.js:184`,
  `setActive()` itself, which is already the file's "only on change" seam and
  already owns the HUD's period, title and count text.
- Exemplar of a composited per-frame write done right, three lines below the
  block being deleted: `meter.style.transform="scaleX("+mainProgress+")"`.

## Steps

1. In `assets/js/founder-journey.js`, add the two-line comment and the
   `if(state.dots) state.dots.forEach(...)` block shown above to `setActive()`,
   immediately after the existing `stops.forEach(...)` block and before
   `period.textContent=periodFor(stops[index]);`.
2. In `assets/js/founder-journey.js`, delete the four-line
   `state.dots.forEach((dot,index)=>{...});` block at lines 314–318 in
   `render()`. Leave the `const active=` / `setActive(active)` lines above it
   and the `meter.style.transform` line below it untouched.
3. In `assets/css/founder-journey.css`, replace line 37 with the target
   `.route-point` rule (adding `transform-box`, `transform-origin` and the
   `transition`).
4. In `assets/css/founder-journey.css`, append `;transform:scale(1.375)` to
   the `.route-point.is-current` rule at line 39, inside its closing brace.

## Boundaries

- Do NOT change the `r="8"` written in `buildRoute()` at
  `assets/js/founder-journey.js:126`. The dots must still be authored at 8.
- Do NOT change `cx`/`cy`, the `viewBox`, `roundedPath()`, `nearestLength()`
  or anything else in `buildRoute()`.
- Do NOT remove `vector-effect:non-scaling-stroke` — without it the scale
  would thicken the ring as well as widen it.
- Do NOT touch `stroke-dashoffset` on `.route-progress`. Driving the route
  draw per frame is the section's core mechanic and is out of scope.
- Do NOT touch `setStopOpacities()`. Its per-frame writes are a separate
  finding, deliberately not in this plan.
- Do NOT edit any root `.html` file — they are generated (see CLAUDE.md).
- If a step does not match the code you find, STOP and report rather than
  improvising.

## Verification

- **Mechanical**:
  - `node --check assets/js/founder-journey.js` — passes.
  - `npx --yes html-validate@11 *.html` and `python3 tools/check-links.py` — pass.
  - `python3 tools/build-site.py` then `git diff --stat -- '*.html'` — no
    change beyond the `founder.html` drift that already exists on this branch.
- **Feel check**: serve the repo root (`python3 -m http.server 8000`), open
  `http://localhost:8000/founder.html` wider than 900px, and scroll the
  journey:
  - Every milestone dot still fills gold as it is passed, and the current one
    is still visibly the largest. Measure it: with a dot at `is-current`,
    DevTools should report a painted diameter of ~22 user units (8 × 2 ×
    1.375), matching `r="11"` before the change.
  - The dot now **grows into** its new size rather than popping. In
    DevTools → Animations, set playback to 10% and step past a milestone to
    watch the scale settle.
  - The ring around the current dot stays visually the same thickness as
    before while it grows — if it thickens, `vector-effect` was lost.
  - In DevTools → Performance, record a 5-second scrub through the middle of
    the journey. Compare against a recording from before the change: the
    per-frame "Recalculate Style" / "Paint" work attributed to the `<svg>`
    should fall noticeably, and no frame should show 14 separate geometry
    invalidations.
  - Scroll **backwards** through a milestone and confirm the dot shrinks
    smoothly and `is-passed` clears correctly.
  - Toggle `prefers-reduced-motion: reduce` and reload: the journey renders
    `is-static`, the route SVG is `display:none`, and none of this is visible.
- **Done when**: `grep -n 'setAttribute("r"' assets/js/founder-journey.js`
  returns only the line in `buildRoute()`, a Performance recording of a scrub
  shows no per-frame SVG geometry invalidation, and the active dot transitions
  between sizes instead of snapping.
