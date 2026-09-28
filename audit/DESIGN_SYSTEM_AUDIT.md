# Design System & Technical Architecture Audit

Part of the [Full Site Audit](FULL_SITE_AUDIT.md). Audit only.

## Does the site have a real design system, or merely visual similarity?

**A real design system**, on the evidence:

### Colour

`assets/css/cirs.css`'s `:root` defines colour as named **roles**, not raw values reused by
copy-paste: `--paper` (ivory ground), `--dark`/`--dark-mid`/`--dark-deep` (the plum/aubergine
dark grounds seen on School History, Spiritual Life, Sports, 404), `--gold`/`--gold-lit`/
`--gold-pale`/`--gold-ink`/`--on-gold`, `--campus` (the house-adjacent green), house/status/
focus colours. Every core text-on-ground pairing carries its **measured contrast ratio as an
inline CSS comment** (`--ink: #1F1F1B; /* 15.68:1 on ivory */`, etc.) — evidence contrast was
designed for, not retrofitted. No page-local file sampled in this audit declared a raw hex
colour duplicating a root token; page sheets read the shared roles.

### Motion

`:focus-visible` and `prefers-reduced-motion` are each defined **once**, globally, with
targeted contextual overrides (dark-ground focus-ring colour swap) rather than redefined per
component. The film-opening pattern (`assets/css/filmintro.css` + `assets/js/filmintro.js`)
is **one shared implementation** reused across 5 pages (Sports, Captures, Art Attack,
Festivals, Theatre) with page-specific footage/title/timing data passed in — confirmed by
reading `film_html()` in `tools/build-site.py`, which generates all 5 from one function.

### Typography

Per CLAUDE.md and confirmed by font files present in `assets/fonts/`: Mona Sans (body/UI),
Bodoni Moda/Literata/EB Garamond (display/editorial/quotation), Tiro Devanagari Hindi
(Devanagari — used precisely on Home's motto and Spiritual Life's Sanskrit terms, confirmed
via rendered screenshots showing correct diacritics: "Swādhyāya", "Sādhanā", "Sevā"). All
self-hosted, not CDN-loaded — confirmed in the first page-load network log
(`assets/fonts/monasans-normal.woff2` etc. served from the same origin).

### Component reuse

The header, drawer, footer and button primitives are byte-identical in structure across all
58 generated pages (they come from `tools/partials/` and the shared `nav_html()`/build
functions in `tools/build-site.py` — there is no per-page fork of this markup to check).

## Confirmed technical debt

### TECH-001 — Script fragmentation on the two most complex pages

**Founder** loads **11 distinct scripts**: the 7 shared site-wide (`navigation.js`, `gsap`,
`ScrollTrigger`, `lenis`, `cirs.js`, `pages.js`, `footer.js`) plus 4 page-specific
(`founder-liquid-sound.js`, `founder-portrait.js`, `founder-opening.js`,
`founder-gurudev-journey.js`). **Crossroads** loads the 7 shared plus 4 page-specific
(`crossroads-intro.js`, `crossroads-archive.js`, `crossroads-stories.js`,
`crossroads-manuscript.js`). Both pages' current execution is strong (see main report's page
audits) — this is a **future maintainability risk**, not a present defect: four
page-specific scripts each owning a slice of one page's behaviour is more surface area to
keep synchronised than one page-specific module would be, but nothing observed suggests
they conflict today.

### ~~TECH-002 — art-attack.html's single-page DOM weight~~ — RESOLVED, no fix needed

2,668 DOM nodes, 297 `<img>` elements, 363 `<a>` elements — real, measured, and still the
highest on the site. Originally flagged as a performance risk from the raw counts alone.
Live network/resource measurement (see `PERFORMANCE_AUDIT.md` and `FULL_SITE_AUDIT.md`'s
Art Attack page audit) found the architecture already handles this well: only 100 of 297
images are ever fetched (the rest sit behind a "Show more" button, correctly hidden and
lazy), and larger images resolve via `srcset` to properly-sized variants — confirmed via
`img.currentSrc`, which caught a false lead of its own (the fallback `src` attribute
pointed at a much larger master file that turned out never to be the one actually
downloaded). One flat page rendering an entire collection's markup at once is real, but not
a demonstrated problem.

### ~~DESIGN-001 — Drawer heading order~~ — RETRACTED

Withdrawn after live follow-up verification. See `ACCESSIBILITY_AUDIT.md`'s "Retracted
finding" section: the drawer and Enquire-panel headings are genuinely removed from the
accessibility tree in their default state (`display:none` / `visibility:hidden`), not
merely visually hidden. No fix was needed or made.

### DESIGN-003 — houses.html missing Lenis

`houses.html` is the only page in its visual/interaction family (the dark-ground,
photo-heavy pages that also load `filmintro.js` or similar choreography) that does not load
`lenis.min.js`, while `ScrollTrigger` is still present. Every other checked page in this
audit that loads GSAP/ScrollTrigger also loads Lenis. This is either a deliberate choice
(a colour-panel stack may read better on native scroll) or a regression — **not determined
in this audit**, flagged for confirmation.

## What is NOT technical debt (checked and cleared)

- `netlify.toml` and `vercel.json` coexisting: **documented, deliberate** transitional state
  during the Netlify→Vercel move (per CLAUDE.md/HOSTING.md), not drift.
- `curriculum/ib-diploma.html` and `curriculum/cbse.html` sharing the `"ibdp"` sheet and
  near-identical structure: **documented, deliberate** twin-page architecture (confirmed in
  `tools/build-site.py`'s own comments), not accidental duplication.
- News-archive and Blog posts sharing one `"blog"` sheet: **deliberate, sensible**
  architecture (one reading template for all long-form text), confirmed by source — the
  content gap on 9 News reports (see main report) is a content problem on top of a sound
  template, not a template problem.
- `assets/source/` sitting outside the deployed tree: **deliberate**, protected by
  `check-links.py`'s orphan check per CLAUDE.md.

## Design system coverage estimate

Based on the evidence above (shared colour roles with zero observed page-local overrides,
one global focus/motion-safety implementation, one shared film-opening component across 5
pages, one shared curriculum-family sheet across 3 pages, byte-identical header/footer/drawer
across all 58 pages): **coverage is high** across colour, motion-safety and cross-page
chrome. The main area of *legitimate, deliberate* non-coverage is the three advanced-motion
techniques (WebGL, Three.js, canvas) that are each intentionally page-specific, one-off
implementations rather than shared components — correctly so, since each is used exactly
once, on the one page whose subject justifies it (see main report's Motion Audit).
