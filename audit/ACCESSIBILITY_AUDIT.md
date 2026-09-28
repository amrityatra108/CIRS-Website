# Accessibility Audit

Part of the [Full Site Audit](FULL_SITE_AUDIT.md). Audit only — nothing here was fixed.
Findings are labelled OBSERVED (directly seen in the DOM/CSS), MEASURED (a specific
computed number), or PLAUSIBLE (inferred, not yet confirmed live) per the brief's own
confidence system. Nothing below is asserted as a WCAG compliance claim; this is a
practical review, not a certification.

## Site-wide strengths (OBSERVED)

1. **Global `:focus-visible`.** `assets/css/cirs.css:174` —
   `:focus-visible{ outline:2px solid var(--focus); outline-offset:3px; }`. `--focus` is
   `#8F6E2F`, a deliberately chosen colour (not the browser default), and it is
   **contextually overridden** at line 1158 for dark/photo grounds
   (`.on-dark :focus-visible, .filmsec :focus-visible, .footer :focus-visible, .finalcta
   :focus-visible, .band :focus-visible{ outline-color:var(--gold-lit); }`) so the focus
   ring stays visible against both ivory and dark/photographic backgrounds. This is real,
   deliberate engineering, not a browser default left untouched.
2. **`prefers-reduced-motion` handled in at least 5 separate rule blocks** in `cirs.css`
   alone (lines 153, 360, 620, 1179, 1255, 1370), each scoped to a specific
   component (scroll-behaviour, hero scroll-cue SVG animation, float controls, etc.)
   rather than one blanket rule — suggesting deliberate per-component consideration.
3. **Colour contrast is designed-for, not checked after the fact.** Every core text/ground
   token in `cirs.css`'s `:root` carries its measured contrast ratio as an inline comment:
   `--ink: #1F1F1B; /* 15.68:1 on ivory */`, `--ink-soft: #54534D; /* 7.32:1 */`,
   `--campus: #2E5D3A; /* 7.26:1 on ivory */`, `--on-dark-soft: #D6D3CA; /* 9.73:1 on
   --dark */`. CLAUDE.md's explicit rule ("Gold is never lettering on ivory, text on a gold
   fill is `--on-gold`, not white") was independently confirmed on `404.html`
   (screenshot-verified: dark text on the gold "Return Home" button).
4. **Zero missing `alt` attributes** (`imgsNoAlt: 0`) on every one of the ~36 pages probed
   in this audit. High `alt=""` counts (e.g. 429/440 images on the homepage) were sampled
   and verified as legitimately decorative content (ambient photo-wall thumbnails, the
   header logo next to visible text) rather than missing descriptions.
5. **Zero unlabelled interactive elements found:** every `<button>` checked had either text
   content or an `aria-label`; every external `target="_blank"` link checked carried
   `rel="noopener"`.
6. **A genuinely well-built accessible motion technique** on `houses.html`: each house
   name renders as one real, visible `<span>` (the accessible content) plus a
   `<div class="house-title-slices" aria-hidden="true" inert>` carrying the decorative
   clip-path reveal slices. `inert` additionally removes the decorative slices from the
   tab order and hit-testing, not just the accessibility tree — a more complete treatment
   than `aria-hidden` alone. This is a genuine "steal from ourselves" candidate.
7. **Correct accessible-name-via-image pattern** on `crossroads.html`: the H1 wraps an
   `<img>` with `alt="The Crossroads"` rather than live text — verified this resolves to a
   correct accessible name despite `textContent` reading empty (a limitation of naive
   text-based auditing this audit corrected for after the first false positive).

## Retracted finding — verified false positive

### ~~A11Y-001 — Drawer headings (H2) precede the page H1 in reading order~~ — RETRACTED

The original report of this audit stated, with HIGH confidence, that four drawer/enquire-
panel headings ("Talk to CIRS", "Portals", "Follow CIRS", "Site navigation") were exposed
to assistive technology before the page's H1, because a raw `document.querySelectorAll
('h1,h2,...')` found them earlier in DOM order than the H1. **That was wrong, and has been
withdrawn.** On direct follow-up — walking each heading's ancestor chain and checking
`getComputedStyle` (not just the `hidden` attribute) — both containers are genuinely
removed from the accessibility tree in their default state:

- `#drawer` (holds "Site navigation"): `hidden` attribute present, computed
  `display: none`.
- `#enqPanel` (holds "Talk to CIRS" / "Portals" / "Follow CIRS"): the static `hidden`
  attribute is removed by JS on load, but the panel's actual closed state is enforced by
  computed `visibility: hidden`, `opacity: 0`, and `max-height: 0px` — all of which also
  remove descendant content from the accessibility tree (`visibility: hidden` is inherited
  by children and is one of the standard ways a browser excludes content from AT, exactly
  like `display: none`).

A live check of exactly which headings are actually exposed (walking the ancestor chain
for `display`/`visibility`/`hidden`, not a flat `querySelectorAll`) confirms these four
headings are excluded, and the page's real headings — starting with the H1 — are the first
thing a screen-reader's heading list reports. **There is no bug, and no fix was made.**

This is recorded here, rather than silently deleted, for the same reason the original
report recorded the Houses.html `Vasishta`-slices false lead: it is evidence the
methodology is being held to its own standard, including when that means retracting a
previously "confirmed" finding. The original audit correctly caught this exact class of
error on Houses.html (`aria-hidden`+`inert` slices) but did not apply the same
computed-style rigor to this finding when it was first written — a gap in the audit's own
consistency, now corrected.

## Verified live — A11Y-002 resolved

### A11Y-002 — Cultural Gallery's 180-button field: keyboard/focus behaviour — VERIFIED, mostly strong

**Original confidence: PLAUSIBLE, rated P1. Now: CONFIRMED live, downgraded to P2** (one
real, moderate finding survives; everything else checked out well). This was audited by
actually driving the page with the keyboard (real Tab/Enter/Escape key presses, not just
reading the DOM), and by reading `assets/js/artswall.js`'s interaction code.

**Confirmed working correctly, live:**

1. A **"Skip to main content" skip link** is the very first focusable element on the page
   (`href="#main"`) and is visibly styled on focus (screenshot-confirmed: a high-contrast
   pill appears top-left) — this was missed entirely in the original pass.
2. The photo dialog is a real `role="dialog" aria-modal="true" aria-labelledby="m-title"`
   element, `inert` + `aria-hidden="true"` + `display:none` when closed (confirmed via
   `getComputedStyle`, not just the attribute).
3. **Keyboard activation of a tile works correctly.** The wall separates mouse/touch
   interaction (`pointerdown`/`pointerup`, with drag-vs-click disambiguation for panning)
   from keyboard/AT activation (a `click` listener gated on `e.detail === 0`, which is 0 for
   a synthetic/keyboard-triggered click and ≥1 for a real mouse click) — a deliberate,
   correct pattern for exactly this kind of draggable interface, and it works: pressing
   Enter on a focused tile opens the dialog.
4. On open, focus moves to the close button (confirmed live via `document.activeElement`).
5. **The Tab-trap holds.** With the dialog open, pressing Tab was confirmed, live, to leave
   focus on the close button rather than escaping to the wall behind it.
6. Escape closes the dialog (confirmed live: `display` returns to `none`, `inert` and
   `aria-hidden="true"` are restored).
7. **Focus restoration on close is correct, and matches its unusually careful source code.**
   After closing, focus was confirmed, live, to land back on the exact tile that had been
   opened (same `aria-label`), not merely "some" element — this matters specifically because
   the wall recycles a limited pool of DOM tiles across many photos, and a naive
   `previousActiveElement.focus()` could easily restore focus to a tile now showing a
   different photo. It didn't.

**One real, moderate finding that survives — downgraded to P2, not P1:** all 168 tile
buttons at 1440×900 are genuine, simultaneous native Tab stops (confirmed: no `tabindex`
management anywhere in `artswall.js`). Arrow keys pan the visual camera but do not move
keyboard focus between tiles — there is no roving-tabindex/grid-navigation pattern. A
keyboard-only user wanting to reach, say, the 100th tile in sequence must press Tab roughly
100 times. Nothing is unreachable or broken — every tile is a real, individually-labelled
stop, and the skip link at least removes the header's ~15 stops from that count — but it is
a genuine, real UX cost specific to keyboard/switch users that a roving-tabindex pattern
(Home/End/Arrow-key focus movement across tiles, one tile in the natural Tab sequence)
would meaningfully reduce. **Recommendation, not implemented in this pass:** add a
roving-tabindex grid pattern to the tile field if/when this page next receives engineering
attention — worthwhile, but not urgent, since the page is fully operable as-is.

### A11Y-003 — New finding from this verification: ~45% of visible Cultural Gallery photos carry a generic accessible name — and this is deliberate, not an oversight

While checking tile labels for the check above, roughly **30 of the 67 unique photographs**
visible in one viewport carry a generic accessible name — `"CIRS cultural gallery
photograph 12 — CIRS Cultural Gallery"` — rather than a real caption, while the rest carry
specific ones (`"Mime, in white masks — Theatre"`, `"Tabla and percussion — Music"`). This
traces directly to `tools/artswall.py`'s own header comment: *"CIRS Cultural Gallery —
filenames are retained where they carry a title; camera filenames are given neutral labels
rather than invented context."* **This is the site's own stated content-integrity
discipline working as intended** (the same principle documented elsewhere: don't invent
what the school hasn't supplied) — not an accessibility bug, and not something to fix in
code. It is, however, a legitimate **content-completeness item**: real captions for these
photographs are the school's to supply, the same category as the captions/credits already
tracked as owed elsewhere on this site. Recorded here as a content note, not a P-severity
code defect.

## Not verified in this audit (explicitly, not silently skipped)

- No screen reader (NVDA/VoiceOver/JAWS) was used — all findings above come from DOM/ARIA
  inspection, not live AT output.
- Zoom-to-400% reflow was not tested on any page.
- Colour-vision-deficiency simulation was not run against the four house colours
  specifically, though their contrast ratios against ivory/dark grounds are documented in
  `cirs.css`'s comments.
- Modal/dialog focus-trap behaviour was verified live on Cultural Gallery (above) but not
  exercised on any other lightbox/gallery/video modal site-wide (Art Attack, Captures,
  Festivals, Theatre all carry galleries per the main report) — the same open question
  applies in principle to those, though Cultural Gallery's result is a reasonable
  positive signal for the shared engineering culture behind them.
- Form accessibility: no on-page forms were found on any of the 30 primary routes checked
  (Admissions correctly routes to an external portal instead), so there is nothing of this
  category to audit on this site.
