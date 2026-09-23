# 004 — Let the header slide out of the founder journey instead of teleporting

- **Status**: TODO
- **Commit**: a3a6ac2
- **Severity**: MEDIUM
- **Category**: Missed opportunity / Physicality
- **Estimated scope**: 2 files, 2 lines

## Problem

Entering the founder journey removes the site header in a single frame, and
leaving it puts the header back the same way.

```css
/* assets/css/founder-journey.css:125 — current */
  .founder-journey-active .header{transform:translateY(-115%);pointer-events:none}
```

The class is toggled by ScrollTrigger as the journey pins and unpins:

```js
/* assets/js/founder-journey.js:344 — current */
      onEnter:()=>document.body.classList.add("founder-journey-active"),
      onEnterBack:()=>document.body.classList.add("founder-journey-active"),
      onLeave:()=>{document.body.classList.remove("founder-journey-active");root.classList.remove("is-camera-moving");},
      onLeaveBack:()=>{document.body.classList.remove("founder-journey-active");root.classList.remove("is-camera-moving");},
```

The header declares a transition, but not on the property that changes:

```css
/* assets/css/cirs.css:208 — current */
.header{
  position:fixed; top:0; left:0; right:0; z-index:100;
  /* Keep the fixed chrome on its own compositor layer. Without this,
     Chromium can briefly paint a transformed pinned section over part of the
     header during a fast pin handoff even though the DOM stacking order is
     correct. */
  transform:translateZ(0); backface-visibility:hidden; isolation:isolate;
  /* Layout containment keeps the chrome independent without clipping the
     Enquire panel when it opens below the floating bar. */
  will-change:transform; contain:layout style;
  background:transparent;
  border-bottom:1px solid transparent;
  transition:box-shadow .35s var(--e), background .35s var(--e), border-color .35s var(--e);
}
```

`box-shadow`, `background` and `border-color` are covered; `transform` is not.
So the school's name vanishes and reappears with no explanation of where it
went — the one hard cut in a section that is otherwise entirely continuous
motion, and the boundary a visitor crosses twice on every visit to the page.

The journey rule also overwrites the base `transform:translateZ(0)` outright.
That `translateZ(0)` is there on purpose — the comment above it says it stops
Chromium painting a transformed pinned section over the header during a pin
handoff, which is precisely the handoff this rule participates in.

## Target

```css
/* assets/css/cirs.css:220 — target */
  transition:box-shadow .35s var(--e), background .35s var(--e), border-color .35s var(--e), transform .34s var(--e2);
```

```css
/* assets/css/founder-journey.css:125 — target */
  .founder-journey-active .header{transform:translate3d(0,-115%,0);pointer-events:none}
```

`.34s` with `var(--e2)` — `cubic-bezier(.16,1,.3,1)`, a strong ease-out. This
sits inside AUDIT §2's 200–500ms budget for a drawer-scale element and matches
the site's existing full-width overlay, the nav drawer, which uses `.42s
var(--e2)` at `assets/css/cirs.css:315`. The header travels a shorter distance
than the drawer, so it is a little quicker.

`translate3d(0,-115%,0)` is the same movement as `translateY(-115%)` while
keeping the Z component the base rule's comment asks for.

## Repo conventions to follow

- Easing tokens are on `:root` at `assets/css/cirs.css:79`:
  `--e: cubic-bezier(.22,.61,.36,1)`, `--e2: cubic-bezier(.16,1,.3,1)`.
- Exemplar to imitate: `assets/css/cirs.css:315`, the drawer —
  `transition:opacity .42s var(--e2), transform .42s var(--e2), visibility .42s;`
  with `transform:translate3d(0,-10px,0)` for the closed state and
  `translate3d(0,0,0)` for open. Full-bleed chrome, `--e2`, `translate3d`.
- `cirs.css` puts one declaration group per line with a space after each
  colon; `founder-journey.css` is written compactly with none. Match whichever
  file you are editing.

## Steps

1. In `assets/css/cirs.css`, append `, transform .34s var(--e2)` to the
   `transition` declaration on line 220, inside the `.header{...}` rule.
   Change nothing else in that rule — not `will-change`, not `contain`, not
   `transform:translateZ(0)`, not the two comments.
2. In `assets/css/founder-journey.css`, change `transform:translateY(-115%)`
   to `transform:translate3d(0,-115%,0)` on line 125. Leave
   `pointer-events:none` and the selector as they are.

## Boundaries

- Do NOT add a transform transition scoped to `body.founder` instead. The
  header's transform is static on every other page — `translateY(-115%)` at
  `founder-journey.css:125` is the only rule in the repository that changes it
  (verified at this commit) — so the base rule is the right home and a scoped
  duplicate of the whole transition list would drift.
- Do NOT touch `will-change:transform` or `contain:layout style` on `.header`.
- Do NOT touch the `onEnter` / `onLeave` callbacks in
  `assets/js/founder-journey.js`. The class toggle is already correct; only
  the CSS response to it changes.
- Do NOT add a transition to `pointer-events` — it must switch instantly so
  the header cannot swallow a click while it is on its way out.
- Do NOT change the `-115%` distance.
- Do NOT edit any root `.html` file — they are generated (see CLAUDE.md).
- If a step does not match the code you find, STOP and report rather than
  improvising.

## Verification

- **Mechanical**:
  - `npx --yes html-validate@11 *.html` and `python3 tools/check-links.py` — pass.
  - `python3 tools/build-site.py` then `git diff --stat -- '*.html'` — no
    change beyond the `founder.html` drift that already exists on this branch.
- **Feel check**: serve the repo root (`python3 -m http.server 8000`), open
  `http://localhost:8000/founder.html` wider than 900px:
  - Scroll slowly down into the journey. The header **rises out of frame**
    rather than disappearing. Scroll back up past the boundary and it drops
    back in.
  - In DevTools → Animations, set playback to 10% and cross the boundary in
    both directions. The header should travel at a constant-looking start and
    decelerate into place — no bounce, no overshoot.
  - Cross the boundary fast, repeatedly, with the scroll wheel. The header
    must **retarget** mid-flight and never restart from off-screen or stutter
    — this is what makes a transition the right tool here rather than a
    keyframe animation.
  - In DevTools → Rendering, enable "Layer borders" and confirm `.header`
    still has its own compositor layer while it moves, and that no part of the
    pinned journey paints over it during the handoff.
  - Confirm the header is not clickable while off-screen: hover where it used
    to be mid-journey and check nothing highlights.
  - Open a page that is **not** the founder page (`index.html`), scroll until
    `.header.is-stuck` engages, and confirm the sticky header's
    background/shadow change is unaffected and the header itself does not move.
  - Toggle `prefers-reduced-motion: reduce`, reload. The journey is
    `is-static`, `founder-journey-active` is never applied, and the header
    stays put. The global reduced-motion rule at `assets/css/cirs.css:1201`
    neutralises the new transition anyway.
- **Done when**: crossing the journey boundary in either direction moves the
  header over ~340ms instead of in one frame, fast repeated crossings retarget
  cleanly, and no other page's header behaviour changes.
