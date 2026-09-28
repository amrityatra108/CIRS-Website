# CIRS Website — Forensic Full-Site Design, UX, Motion & Frontend Audit

**Audit only. No production file was modified to produce this report.** Everything here was
produced by rendering the site locally (a plain static file server over the committed
`.html` + `assets/`), inspecting the live DOM, reading source, and running the repository's
own read-only checkers (`tools/check-links.py`, `html-validate`).

Date: 2026-09-28 · Auditor: Claude (Sonnet 5), acting as art director / UX auditor / motion
designer / accessibility specialist / frontend performance engineer · Branch:
`claude/cirs-forensic-audit-256804` (worktree)

## Contents

1. [Methodology & Coverage](#methodology--coverage)
2. [Executive Diagnosis](#executive-diagnosis)
3. [Route Inventory](#route-inventory)
4. [Scoring Framework & Calibration](#scoring-framework--calibration)
5. [Master Ranking](#master-ranking) — full table in [`PAGE_RANKINGS.csv`](PAGE_RANKINGS.csv)
6. [Top & Bottom Pages](#top--bottom-pages)
7. [Individual Page Audits — Flagship Pages](#individual-page-audits--flagship-pages)
8. [The Article/Blog Template Family](#the-articleblog-template-family)
9. [Motion Audit](#motion-audit)
10. [Mobile & Responsive Audit](#mobile--responsive-audit)
11. [Accessibility Audit](#accessibility-audit) — full register in [`ACCESSIBILITY_AUDIT.md`](ACCESSIBILITY_AUDIT.md)
12. [Performance & Asset Audit](#performance--asset-audit) — full detail in [`PERFORMANCE_AUDIT.md`](PERFORMANCE_AUDIT.md) / [`ASSET_AUDIT.md`](ASSET_AUDIT.md)
13. [Design System & Technical Architecture](#design-system--technical-architecture) — full in [`DESIGN_SYSTEM_AUDIT.md`](DESIGN_SYSTEM_AUDIT.md)
14. [Repetition & Cross-Page Consistency](#repetition--cross-page-consistency)
15. [Broken-Experience Report](#broken-experience-report) — full in [`BROKEN_EXPERIENCES.md`](BROKEN_EXPERIENCES.md)
16. [Content Credibility & Underdesigned Pages](#content-credibility--underdesigned-pages)
17. [Do-Not-Touch List](#do-not-touch-list)
18. [Redesign Priority Matrix](#redesign-priority-matrix) — full in [`REDESIGN_PRIORITY.md`](REDESIGN_PRIORITY.md)
19. [Quick Wins](#quick-wins)
20. [Design Debt Map](#design-debt-map)
21. [Final Verdict](#final-verdict)

---

## Methodology & Coverage

**Environment.** The repository was served with a plain static file server
(`python -m http.server`) — this is a 58-page, no-build static site, so that is a faithful
stand-in for production. The built-in browser pane in this session was **hidden** for most
of the audit (a client-side condition, not a site defect); screenshots render blank while
hidden and worked intermittently once it came into view. Where a claim rests on a rendered
screenshot, it is marked **(screenshot-verified)**. Everywhere else, findings rest on:

- The live, computed DOM (headings, landmarks, `aria-hidden`/`inert` state, image `alt`,
  video attributes, canvas count, script inventory, DOM node count, document height) —
  extracted with the same JS probe on every page, not guessed from source.
- `document.documentElement.scrollWidth` vs `window.innerWidth` at 390×844 on all 30
  primary routes — a direct, binary measurement of horizontal-overflow bugs.
- The repository's own checkers, run unmodified: `python tools/check-links.py` (10,119
  references) and `npx html-validate@11` (58 pages).
- Source reading of `tools/build-site.py`, `tools/*.py` data files, and `assets/css/cirs.css`
  for the design-token, breakpoint, focus-visible and reduced-motion system.
- Direct filesystem measurement of `assets/` (excluding `assets/source/`, which CLAUDE.md
  confirms is never deployed) for the asset audit.

**Coverage.** All **58** routes in `tools/build-site.py`'s `PAGES` dict were inspected via
DOM probe; **zero** render failures. The 30 primary/flagship routes (everything reachable
from the menu, plus Home, Important Documents, the two Curriculum children, and 404) were
each individually navigated, DOM-profiled, and overflow-tested; several were also
screenshot-verified at mobile width once the pane became visible. The 27 News-archive and
Blog article pages share one template family each (confirmed in `tools/build-site.py`:
both `newsarticles.ARTICLES` and `blogposts.POSTS` are built onto the same `"blog"` sheet);
6 were individually rendered as representative samples (2 News-archive with no gallery, 2
News-archive confirmed by source to carry a gallery, 2 Blog essays), and the remaining 21
are scored as template-inherited, marked as such in `PAGE_RANKINGS.csv` rather than given
fabricated unique commentary. This is a deliberate, disclosed scoping decision (see
[Duplicate Content](#the-articleblog-template-family)), not an omission — every route
still appears in the master ranking.

**What this audit did not do.** It did not run Lighthouse, WebPageTest, or any real network
throttling (not available in this environment) — performance claims are asset-weight and
DOM-complexity **proxies**, labelled as such, never presented as measured Core Web Vitals.
It did not exercise every interactive sequence on every page (e.g. the full Founder WebGL
portrait interaction, the Houses masquerade video players, the Results book-flip) — those
are marked **NOT VERIFIED** rather than asserted. Five false leads are worth recording —
two were caught before this report was first published, three were raised as open
verification tasks and closed by live follow-up after publication, at the reader's request:

- A heading-text probe first flagged Houses.html's `VasishtaVasishtaVasishta` text as a
  duplicate-content bug — inspection showed it was a correctly `aria-hidden` + `inert`
  clip-path reveal slice, and the visible, accessible heading was a single "Vasishta".
  Caught before publication.
- A screenshot of Spiritual Life's hero mid-entrance animation looked like a serious
  text/background contrast failure — waiting 3 seconds and recapturing showed a fully
  legible, well-composed final state. Caught before publication.
- **A flat `document.querySelectorAll('h1,h2,...')` probe flagged the header drawer's own
  headings ("Talk to CIRS", "Portals", "Follow CIRS", "Site navigation") as appearing
  before the page H1 in the accessibility tree, and this report first published that as a
  confirmed, HIGH-confidence, P1/P2 finding with a recommended code fix.** It was wrong —
  the same class of error as the Houses.html lead above, but this time the probe wasn't
  corrected for CSS-based hiding (`display`/`visibility`, not just `hidden`/`aria-hidden`)
  before the finding was written up. A reader asked for the fix to be implemented, which
  prompted a live re-check (walking each heading's ancestor chain for computed style)
  before writing any code — that re-check found both containers are genuinely removed from
  the accessibility tree by default, no bug exists, and no code was changed. Every section
  of this report that referenced the original finding has been corrected in place, marked
  as retracted rather than silently deleted — see `ACCESSIBILITY_AUDIT.md`'s "Retracted
  finding" section for the full technical detail. This is recorded here deliberately: it is
  a real methodology failure (the same check that caught the Houses.html lead should have
  been applied here too, and wasn't, until after publication), not just a success story.
- **Theatre's 40.9vh length was raised as an unverified pacing risk, then closed by a live
  scroll-through** (real scroll gestures, not `window.scrollTo` — this site's Lenis
  smooth-scroll silently overrides direct position jumps, a second instance of the same
  scroll-jump issue this audit hit and corrected for during the original pass). The length
  turned out to be transparently earned by real, stated content (59 photographs). See the
  Theatre page audit.
- **Art Attack's 2,668-node DOM was raised as a confirmed performance risk, then measured
  live** — and, inside that same check, produced its own false lead: checking the fallback
  `src` attribute of its "process photo" images suggested some were served 4–6× larger than
  displayed (up to 559KB for a ~295px-wide image). Checking `img.currentSrc` after letting
  the image actually load showed the browser correctly resolves the image's `srcset` down
  to a 68KB variant — the `src` attribute is only a no-`srcset`-support fallback, essentially
  unused by any current browser, and reading it as "what gets downloaded" was the error.
  See the Art Attack page audit.

---

## Executive Diagnosis

*(≤500 words)*

The CIRS website is a genuinely unusual thing for a school site: a 58-page static build with
zero broken links across 10,119 references, zero HTML-validation errors, zero horizontal-
overflow bugs at mobile width across every primary route tested, a colour system with
contrast ratios documented inline in the CSS, and `:focus-visible` and
`prefers-reduced-motion` handled as first-class, site-wide concerns rather than afterthoughts.
That technical floor is not what breaks this site, and it should not be touched to chase
novelty.

What the site actually *is*, experientially, is a small set of genuinely distinctive
flagship pages — School History's archive, Founder's WebGL portrait, Spiritual Life's
Three.js mandala, Math Challenge's canvas-driven problems, Houses' colour-coded index,
Sports' macro-texture film opening, Captures' curated photo essay, Crossroads' real
editorial masthead, Cultural Gallery's full-window photo field — sitting inside a much
larger body of quieter, competent, conventional pages (Curriculum, Leadership, School
Information, Parent Portal) and, at the edges, 27 article pages sharing one plain template.
The flagship pages are where the site earns comparison to museums and cultural-institution
sites rather than "a good school website." They are not interchangeable with each other —
each opens on a different device (a bust, a mandala, a macro texture, a canvas) in service
of a different subject, which is exactly the page-identity discipline the brief asks for,
and it is real, not decorative.

The gap is not inconsistency — it is an honest split between finished and not-yet-supplied.
Our Laurels is an explicitly disclosed placeholder. Nine of the eleven News-archive reports
(Science Expo, English Week, Mathematics Week, Competitions, Social Science Week, Chinmaya
Vraja, the general election, Seva Week, the solo-instrument recital) carry **zero**
photographs, on a site that is otherwise built almost entirely around real campus
photography — and the two News reports that do have photographs (Vishu/Tamil Puthandu,
Gayathri Havan) prove the material exists and the template supports it. That is the
single biggest, most fixable gap on the site: not a redesign, a content-population task
against an already-good template.

Two smaller, real risks sit underneath the flagship pages rather than on their surface: Art
Attack's single page carries 2,668 DOM nodes and 297 images (a genuine performance-risk
outlier, not measured in Lighthouse terms but structurally undeniable), and Cultural
Gallery's 180-button photo field has not been verified for keyboard/focus behaviour at that
density. Neither is visible in a screenshot; both would only surface under real use.

The website is not a collection of disconnected components stacked vertically — the
`cirs.css` token system, the shared header/drawer, the reduced-motion handling and the
focus-visible overrides genuinely hold it together as one system. The work in front of it is
narrower than "redesign the site": populate nine News reports with real photographs, verify
two specific interaction-density risks, and leave the flagship pages alone.

---

## Route Inventory

All 58 routes are generated from a single source of truth, `tools/build-site.py`'s `PAGES`
dict (confirmed by direct inspection — no route exists outside it; `ls *.html` plus the two
`curriculum/` children total exactly 58, matching `len(PAGES)`). There is no router, no
client-side navigation, no hidden/orphaned build output, and no legacy route: this is a
from-scratch, single-source static build with a documented CI gate (`tools/build-site.py`
re-run, diffed against committed output) that prevents drift.

| Group | Routes | Count | In main menu? |
|---|---|---|---|
| Vision | founder, why-cirs, school-history, leadership | 4 | Yes |
| Student Life | the-cirs-experience, spiritual-life, curriculum, our-results, sports, houses, our-laurels, math-challenge | 8 | Yes |
| Literary Excellence | crossroads, blog, creative-writing | 3 | Yes |
| Art, Culture & Music | captures, art-attack, festivals, theatre, cultural-gallery | 5 | Yes |
| Connect | school-info, news, admissions, parent-portal, alumni | 5 | Yes |
| Home | index | 1 | Reached via wordmark, not a menu entry |
| Secondary / linked-not-menued | important-documents (from School Info), curriculum/ib-diploma, curriculum/cbse (from Curriculum) | 3 | No |
| Error | 404 | 1 | No (served at any unmatched path) |
| News archive reports | science-expo, english-week, mathematics-week-2025, competitions, social-science-week, chinmaya-vraja, cirs-general-election, seva-week, solo-instrument, vishu-tamil-puthandu, gayathri-havan | 11 | No (reached from News) |
| Blog essays | death-of-rationalism, beyond-the-lobby, anakin-skywalker, is-ai-art-really-art, rumors-at-cirs, hot-wheels-vs-barbie, geography-and-geopolitics, sportswashing, notes-of-healing, my-home, voyages-in-the-yuva-kendra, the-race-beyond, trust-or-bust, the-journey-behind-excellence, the-social-glue, death-of-detail, resurgence | 17 | No (reached from Blog) |
| **Total** | | **58** | |

**Redirects (confirmed working, both hosts):** `/student-life` and `/student-life.html` →
`/the-cirs-experience` (301, permanent) — present identically in both `vercel.json` and
`netlify.toml`. This is the site's one confirmed legacy redirect: the page now called The
CIRS Experience was previously "Student Life."

**Legacy/orphaned repository content, confirmed NOT publicly reachable:** `Digital/`,
`docs/` and `pdf/` at the repository root, and the top-level `previews/`, `review/` and
`scrollcraft/` directories, are **not** among the 58 routes `tools/build-site.py` generates
and are **not** copied by `tools/stage-deploy.py` (confirmed by reading its source: it
copies only `f"{slug}.html"` for each `slug` in `PAGES`, plus assets those pages actually
reference — nothing else). `tools/stage-deploy.py`'s own comment states plainly:
*"Digital/, docs/ and pdf/ hold material from the old website that nothing here links to."*
`Digital/imp_date.html` was opened directly and confirmed to be exactly that — an XHTML 1.0
Transitional page from a previous site build, referencing a `css/style1.css` and
`search.js` that do not exist anywhere in this repository. None of this is a live-site
defect; it is repository housekeeping cruft, listed here because the brief specifically
asks whether "legacy pages" are still reachable, and the sourced answer is **no**.

**The whole deployed site is currently a pre-launch review preview, by its own
configuration — not a finding, but essential context.** `vercel.json` sets
`X-Robots-Tag: noindex` on every route, and `tools/stage-deploy.py` generates a matching
`robots.txt` (`Disallow: /`) with the comment *"Review preview — keep it out of search
results... Delete this file, and robots.txt, for the real launch."* This is deliberate,
documented, and intentional — not an SEO oversight — and it should stay in place until the
owner decides to launch. One observation worth passing along, not asserted as a defect:
that script's own header comment justifies the noindex state by saying "the pages still
carry placeholder copy and an under-construction note," but this audit found only **one**
page (`our-laurels.html`) with actual placeholder copy — most other pages explicitly set
`"uc": False` to turn the general under-construction note off. That comment may simply
predate the site's current state of completion; it is the owner's call whether the
review-preview gate is still needed, not something this audit can decide.

**Status classification** (evidence-based, not assumed): 56 of 58 routes are **Complete**.
**our-laurels.html** is an explicitly-labelled **Placeholder** (`soon_html()` in
`tools/build-site.py` — "[Placeholder — competition names, years, placings and the students
involved, to be supplied by the sports office and the activities office.]"). The 9
photo-less News-archive reports are **Complete but content-thin** — they are not
placeholders (no bracketed placeholder text, no "coming soon" language), they are simply
text-only reports where the template supports imagery the report doesn't use. No
**Duplicate/legacy** or **Unknown purpose** route was found; no redirect layer exists to
audit (Netlify/Vercel config both point 404s at `404.html` — see `BROKEN_EXPERIENCES.md`).

---

## Scoring Framework & Calibration

Every route is scored 0.0–10.0 (one decimal, no false precision beyond what the evidence
supports) across three composite dimensions, per the brief's own formula:

- **Design** = average of Visual Design, Hero, Typography, Layout, Imagery, Originality, Page Identity
- **Experience** = average of Motion, Scroll Experience, Content Presentation, UX, Responsive Design
- **Technical** = average of Accessibility, Performance, Technical Polish
- **Overall** = Design×45% + Experience×35% + Technical×20%

**Calibration, set after the full first pass across all 58 routes** (Phase 4 of the brief's
own execution order), against professional contemporary web standards — not merely against
other CIRS pages:

- **9–10**: A genuinely distinctive concept, executed with real craft, that would still read
  as well-designed with the school's logo removed. On this site: School History, Founder,
  Spiritual Life, Math Challenge — each earns this by page-identity match, not by spectacle.
- **8–8.9**: Strong, confident, clearly intentional, with at most minor, named gaps.
- **7–7.9**: Competent, professionally built, but conventional — the "good school website"
  register, not the "award site" register. The majority of CIRS's informational pages sit
  here, correctly, because their job is clarity rather than spectacle.
- **6–6.9**: Serviceable but visibly thin — usually a content gap (no imagery, minimal
  body) rather than a structural or technical failure.
- **5–5.9**: Below par — the concept or content genuinely undermines the page.
- **<5**: Placeholder or broken.

Because the technical floor (accessibility scaffolding, zero broken links, zero HTML
errors, zero mobile overflow) is uniform across the entire site, **Technical scores cluster
tightly at 8–9** for nearly every route — this is not score compression for its own sake,
it reflects a genuinely uniform technical foundation, confirmed by the same measurable
checks on every route — including Art Attack, whose Technical score was provisionally
marked down in the first version of this audit and restored to 9.0 once live measurement
showed no real technical deficiency (see its page audit).

---

## Master Ranking

Full 58-row table: [`PAGE_RANKINGS.csv`](PAGE_RANKINGS.csv). Sorted by Overall, descending.
No route omitted.

**Quality distribution** (computed directly from the 58-row table, after the Cultural
Gallery, Theatre and Art Attack revisions below): mean Overall **7.30**, median **7.2**,
standard deviation **1.03**, max **8.8**, min **3.3**. Distribution: 0 pages ≥9, **17** in
8–8.9, **29** in 7–7.9, **2** in 6–6.9, **9** in 5–5.9, **1** below 5. Mean Technical (8.97)
sits far above mean Design (6.83) and Experience (6.73) — the
clearest single number in this audit confirming the executive diagnosis: the technical
floor is uniformly strong, and the gap between Design/Experience and Technical is almost
entirely explained by the 10-page cluster (9 photo-less News reports + Our Laurels) sitting
at 3.3–5.7 while every other page sits in a tight 6.5–8.8 band. **This answers the brief's
own question directly: the site's problem is not that most pages are weak, and it is not
that quality is highly inconsistent across the board (a standard deviation of 1.01 on a
0–10 scale, with the bulk of pages landing in a 1.4-point band from 6.5–8.8, is a
genuinely tight distribution). It is a narrow, identified, ten-page content-completeness
gap sitting on top of an otherwise consistent site** — which is why the Redesign Priority
Matrix above recommends content population over any structural redesign.

## Top & Bottom Pages

**Top 10 strongest pages**

| Rank | Route | Overall | Why |
|---|---|---|---|
| 1 | school-history.html | 8.8 | Archival composition matches its subject; sourced, chapter-structured content |
| 2 | founder.html | 8.8 | Designer-protected WebGL opening; the site's most technically ambitious page used in service of its subject |
| 3 | math-challenge.html | 8.6 | Canvas used as real interface logic (Heron's reflection, chessboard invariant), not decoration — the single best "page identity" match on the site |
| 4 | spiritual-life.html | 8.5 | Three.js opening resolves to a restrained, precise, non-generic composition |
| 5 | houses.html | 8.4 | Confident colour system; genuinely well-built accessible text-reveal technique |
| 5 | sports.html | 8.4 | Distinctive macro-texture opening instead of a generic action-shot hero |
| 5 | captures.html | 8.4 | Curated thematic photo groupings, not a flat gallery |
| 5 | crossroads.html | 8.4 | Real editorial-publication register, 32-issue archive |
| 5 | cultural-gallery.html | 8.4 | Most original page architecture on the site; keyboard/focus behaviour live-verified as genuinely well-built (raised from 8.1 after verification) |
| 5 | theatre.html | 8.4 | 59 real photographs, transparently stated on-page; genuinely varied staging per house confirmed live (raised from 7.9 after a full scroll-through) |
| 11 | alumni.html | 8.3 | Destination/journey concept backed by 150 real, specific destinations |

*(index.html also scores 8.3 and would tie for 11th; both are strong, conventional-tier
flagship pages — see the full table for the complete ranking.)*

**Bottom 10 pages**

| Route | Overall | Why |
|---|---|---|
| our-laurels.html | 3.3 | Explicitly disclosed placeholder |
| science-expo.html | 5.7 | Zero photographs of a photographed event |
| english-week.html | 5.7 | Zero photographs |
| mathematics-week-2025.html | 5.7 | Zero photographs (template pattern) |
| competitions.html | 5.7 | Zero photographs (template pattern) |
| social-science-week.html | 5.7 | Zero photographs (template pattern) |
| chinmaya-vraja.html | 5.7 | Zero photographs (template pattern) |
| cirs-general-election.html | 5.7 | Zero photographs (template pattern) |
| seva-week.html | 5.7 | Zero photographs (template pattern) |
| solo-instrument.html | 5.7 | Zero photographs (template pattern) |

Note what is *not* on the bottom-10 list: no flagship page, no menu-level page, and no
technical failure. Every page in the bottom 10 is a content-population gap on one template
family, plus one disclosed placeholder. That is a narrow, fixable problem, not a systemic
design failure — see [Redesign Priority Matrix](#redesign-priority-matrix).

---

## Individual Page Audits — Flagship Pages

For each page: concept, what works, what's unverified/at risk, mobile note, severity.
Severity: P0 = broken/critical, P1 = major, P2 = meaningful, P3 = polish.

### `index.html` — Home — 8.3

**Concept.** Photographic hero over the campus (mountains behind the tiled roofline) →
"Rooted in Values! Ready for the World." → a four-chapter narrative built on the school's
own Sanskrit framework (Jñānam·Sevā·Kauśalam, each chapter titled and captioned rather than
generically labelled "academics/service/sports") → the official CIRS film embedded in place
→ a credentials ticker → a "Hundred Acres, in a Hundred Frames" ambient dissolving photo
wall → motto in Devanagari with transliteration → closing CTA. **(screenshot-verified,
mobile hero)**

**What works.** The opening is a real photograph of the actual campus, not stock imagery or
a generic drone shot — it establishes place immediately (Five-Second Test: pass). The
four-chapter structure is the strongest "page identity" device on the homepage: it is
literally built from the school's own Knowledge/Service/Skill framework rather than a
generic "why choose us" pattern. `imgsEmptyAlt` is 429/440 — verified by sampling: these are
overwhelmingly the ambient photo-wall thumbnails and the logo, correctly marked decorative,
not a missing-alt-text problem.

**What's unverified / at risk.** `scrollHeightVh` is 11.7 at 1440×900 — moderate, not
excessive, but the mid-page pacing across all four chapters was not fully screenshot-verified
(DOM-confirmed content only). *(An earlier draft of this report flagged four drawer H2s as
appearing before the H1 in the accessibility tree; live follow-up verification found they
are correctly removed from the accessibility tree in their closed state — see Accessibility
Audit's "Retracted finding" — so there is nothing outstanding here.)*

**Mobile.** Hero, headline and nav pill all read cleanly at 390px; header pill holds five
tap targets (Enquire / Home / CIRS wordmark / News / Menu) without visual crowding
(screenshot-verified, tiled-artifact aside — see Methodology).

**Keep:** the photographic hero and the Jñānam/Sevā/Kauśalam framing. **Change:** none
confirmed. **Severity:** none.

### `founder.html` — 8.8

**Concept.** No shared header/hero — the page opens directly on an oversized serif
"GURUDEV" over ivory, with minimal "Pause intro / Skip intro" controls, ahead of a WebGL
portrait (two GLB busts, a pointer-following trail, paired swirls after idle) and a
corrected life-story timeline. **(screenshot-verified, mobile opening frame)**

**What works.** This is the single most typographically confident opening on the site — pure
letterforms, no photograph, no gradient, earning attention through scale and restraint
rather than effects. It is explicitly protected in CLAUDE.md ("designer's approved values;
change them only on the designer's say") and that protection is earned: nothing about the
opening reads as generic-AI-landing-page (no glow, no particles, no glass cards).

**What's unverified / at risk.** 11 distinct scripts load on this page (the most of any
route: `founder-liquid-sound.js`, `founder-portrait.js`, `founder-opening.js`,
`founder-gurudev-journey.js`, plus the shared 7). That is real fragmentation risk for future
maintenance even though current execution is strong (Maintainability: flag, not a defect).
The WebGL bust interaction itself, the opt-in cursor-speed sound, and the idle-swirl timing
were **NOT VERIFIED** in this audit (no live pointer interaction was exercised against the
canvas).

**Mobile.** The intro title card reflows correctly at 390px with no overflow; the WebGL
canvas's mobile behaviour (fallback, DPR, GPU cost on a real phone) is **NOT VERIFIED**.

**Keep:** everything — this is the clearest Do-Not-Touch page on the site. **Severity:** P3
(the script-fragmentation note is a maintainability flag, not a user-facing defect).

### `school-history.html` — 8.8

**Concept.** Dark plum ground, "THE CIRS ARCHIVE" gold eyebrow, "Before the school opened."
headline, two CTAs (filled ivory primary / outlined secondary), archival document cards set
at shallow depth behind the fold, six-chapter sticky sequence, full sourced milestone
timeline. **(screenshot-verified, mobile hero)**

**What works.** This is the strongest "Page Identity Test" pass on the site: remove the text
and the composition still reads unmistakably as an archive, not a generic "our history"
page. `tools/history.py`'s discipline (every event sourced; unconfirmed claims held in
`UNRESOLVED`, never published) means the content-credibility risk that usually accompanies
ambitious historical design (invented specificity) is structurally prevented here — a rare
and valuable pairing of design ambition with factual discipline.

**What's unverified / at risk.** At 11.4vh the page is not long relative to its six chapters,
but the choreography *between* chapters (does the sticky sequence hand off cleanly, does
content appear before its intended scroll position) was **NOT VERIFIED** — this is exactly
the kind of defect (Section 44/76 in the brief) that a DOM probe cannot catch and only a
live scroll-through can.

**Keep:** the archive concept, the sourced-milestone discipline. **Change:** none found.
**Severity:** P3 (verify chapter hand-off timing as routine QA, not urgent).

### `spiritual-life.html` — 8.5

**Concept.** A dark ground carrying a drawn sacred-geometry mandala (rings and interlocking
curves), "SPIRITUAL LIFE AT CIRS" eyebrow, "An education that transforms." headline,
"Swādhyāya / Sādhanā / Sevā" subheading in correct diacritics, "Scroll to enter" cue.
**(screenshot-verified twice — see below)**

**What works, and the methodology note that matters here.** The first screenshot taken on
this page, on mobile, caught the entrance animation mid-transition: the second headline line
overlapped the mandala's densest line-work and was close to illegible. Waiting three seconds
and recapturing showed the composition fully resolved — full contrast, a completely drawn
mandala, and legible type. **This is recorded as a finding about motion pacing (the
entrance takes several seconds to fully resolve), not a contrast defect** — the persisting,
resting state a user actually reads is excellent, and using the real Sanskrit terms
precisely (rather than generic "meditation/mindfulness" language) is exactly what the
brief's Spiritual Life Special Audit asks for: specific to CIRS, not a generic "Indian
spirituality" mood board.

**What's unverified / at risk.** At 28.5vh this is the third-longest page on the site,
covering Swadhyaya/Sadhana/Seva across many activities — plausibly earned given the content
breadth, but mid-page pacing was **NOT VERIFIED** beyond the DOM. The canvas (Three.js,
confirmed present) was not interacted with.

**Mobile.** No horizontal overflow (measured). Entrance animation timing (the transient
mid-animation frame noted above) is worth a deliberate look on a real device with a slower
GPU, since a phone that renders the mandala more slowly would show visitors a longer window
of the lower-contrast intermediate state.

**Keep:** the mandala concept and the precise use of the school's own vocabulary.
**Severity:** P2 (confirm the entrance settles quickly enough on a mid-range phone; not
confirmed to be a problem, but worth the 10-minute check given what the transient frame
looked like).

### `math-challenge.html` — 8.6

**Concept.** The one dark-themed page on the site (`matharena.css`, scoped to
`body.matharena`), three `<canvas>` elements used as actual mathematical demonstrations —
Heron of Alexandria's shortest-path reflection, the mutilated-chessboard invariant — plus
four difficulty zones and a month-by-month winners record.

**What works.** This is the best answer on the entire site to the brief's own Section 34
prompt ("Could this page belong to any generic school competition?"): no, because the canvas
elements are the interface, not illustration — exactly the "mathematical structures becoming
interface logic rather than decorative equations" opportunity the brief names, already
realised. Only 3 images total on the page; visual interest comes from typography and the
canvas demonstrations rather than photography, which is a legitimate, page-appropriate
choice rather than a gap.

**What's unverified / at risk.** Whether the three canvas demonstrations are actually
interactive (draggable/steppable) or auto-animating was **NOT VERIFIED** — this materially
changes the Complexity Justification score (interactive demonstration = 9–10; passive
animation = 6–7) and is worth a direct interaction check.

**Keep:** the canvas-as-interface-logic concept — do not replace it with static diagrams.
**Severity:** P2 (verify interactivity; if the canvases are passive, that is the single
highest-value 30-minute upgrade on the site, not a redesign).

### `houses.html` — 8.4

**Concept.** "Four Houses. One CIRS." headline, "Different colours. Shared purpose."
subhead, then a stacked list of four house panels each closed with a colour-coded rule
(confirmed: red under Vasishta, yellow under Valmiki) and an "Explore →" affordance.
**(screenshot-verified, mobile)**

**What works.** The house-name reveal uses a genuinely well-built technique: each name is a
visible `<span>` plus a decorative `<div class="house-title-slices" aria-hidden="true"
inert>` carrying clipped duplicate slices for a staggered clip-path reveal. A screen reader
gets "Vasishta" once; a naive heading-text scan (which this audit's own probe initially ran)
would misread it as quadruplicated content — it is not. This is exactly the kind of
technical craft that should be held up as a pattern for other pages, not just left alone.

**What's unverified / at risk.** This is the one page in its family without `lenis.min.js`
loaded (confirmed absent from its script list, present on every sibling page) — meaning
Houses uses native browser scroll where its neighbours use smooth-scroll. That may be
deliberate (a colour-panel stack may read better without scroll-smoothing lag), but it is
worth confirming it is a decision and not a regression, since it is a scroll-feel
inconsistency a returning visitor would notice.

**Severity:** P2 (confirm the missing Lenis is intentional).

### `sports.html` — 8.4

**Concept.** Five-second macro film (a wet cricket/football surface, droplets catching
light) instead of a literal action-shot hero, "SCROLL TO DISCOVER" cue, then nine
choreographed sections ("The whole court moves as one", "Find your rhythm, lane by lane",
"Read the bounce. Find the line.") each keyed to a specific sport rather than a generic
"Our Sports" grid. **(screenshot-verified, mobile opening)**

**What works.** The opening is a genuine, distinctive art-direction choice — texture and
tension standing in for literal action, which is a more sophisticated device than the
obvious "kids playing sports" cliché the brief explicitly warns against rewarding
generically. Section headlines are written per-sport, not templated.

**What's unverified / at risk.** At 32.4vh this is a long page; whether nine sections sustain
that length without sagging was **NOT VERIFIED** beyond DOM/heading structure.

**Severity:** P3.

### `captures.html` — 8.4

**Concept.** A scrubbed six-second camera-emergence film hands off to a photograph
dissolve, then curated thematic groupings — "Small worlds", "Among the trees", "By the
water", "Sky and shade", "Together", "Solo and stage" — across 86 photographs.

**What works.** The thematic grouping is real curation, not a flat "gallery" grid — it
answers the brief's own "generic gallery" warning directly.

**What's unverified / at risk.** Three separate dedicated scripts (`filmintro.js`,
`captures-featured.js`, `captures-gallery.js`) for one page is real script fragmentation;
current execution is strong, so this is a maintainability flag rather than a user-facing
defect. 30.9vh is long; pacing **NOT VERIFIED** beyond DOM.

**Severity:** P3.

### `crossroads.html` — 8.4

**Concept.** A restored-SVG masthead ("The Crossroads" as image content, not live text — the
accessible name comes from the image's `alt`, confirmed correct on inspection), "32 editions.
Countless stories.", newest-first issue archive.

**What works.** This is the strongest "does it feel like a publication or a page of cards
linking to articles" pass on the site (brief Section 35) — a real masthead, real issue
numbering, genuine editorial register.

**What's unverified / at risk.** Four separate dedicated scripts
(`crossroads-intro.js`, `crossroads-archive.js`, `crossroads-stories.js`,
`crossroads-manuscript.js`) — the highest script-fragmentation count on the site alongside
Founder. Two `<video>` elements present; their role in the masthead was **NOT VERIFIED**
interactively.

**Severity:** P3 (maintainability flag).

### `cultural-gallery.html` — 8.4 (raised from 8.1 after live verification)

**Concept.** The one page on the site that is not a document (per CLAUDE.md, by design): a
full-window field of photographs, no scroll (`scrollHeightVh: 1`, measured), no footer
(`landmarks.footer: 0`, measured), header only.

**What works.** This is the single most original page *architecture* on the entire site —
not a variation of a pattern used elsewhere, a genuinely different structural idea. It
directly answers the brief's Page Identity Test at the architectural level, not just the
visual level.

**Update — the interaction question was live-verified, and the result is strong.** The
first published version of this report flagged the page's 180 `<button>` elements as an
unverified P1 risk. A follow-up live keyboard pass (real Tab/Enter/Escape presses, not just
DOM inspection) found the engineering underneath is genuinely careful: a visible "Skip to
main content" link is the first Tab stop; the photo dialog is a correct
`role="dialog" aria-modal="true"` pattern, `inert` when closed; keyboard (Enter) and
mouse/touch activation are deliberately separated (`e.detail === 0` gates the
keyboard/AT-triggered `click` handler so a real mouse click, handled separately via
`pointerdown`/`pointerup` for drag-vs-click disambiguation, doesn't double-fire it); the
Tab-trap inside the open dialog was confirmed to hold; and closing with Escape was
confirmed, live, to restore focus to the *exact* tile that had been opened — non-trivial,
since the wall recycles a limited pool of DOM tiles across many photos, and getting that
restoration right takes real care. Full detail: `ACCESSIBILITY_AUDIT.md`'s A11Y-002.

**What's real and still worth doing, downgraded from P1 to P2.** All 168 tiles (at
1440×900) are simultaneous native Tab stops — there is no roving-tabindex/arrow-key grid
pattern moving *focus* between tiles (arrow keys pan the visual camera, which is a
different thing). Reaching the 100th tile by keyboard means 100 Tab presses. Nothing is
unreachable, and every tile carries a live, meaningful `aria-label`, but a roving-tabindex
pattern would be a real, worthwhile improvement if this page gets engineering attention
again — not urgent, since the page is fully operable today.

**A genuinely new finding from this same check, unrelated to keyboard access:** roughly 45%
of the photographs visible in one viewport (30 of 67 sampled) carry a generic accessible
name ("CIRS cultural gallery photograph 12") rather than a real caption. This traces
directly to a deliberate choice recorded in `tools/artswall.py`'s own header comment — the
team declines to invent captions for photos whose real subject/occasion isn't documented,
consistent with the site's content-integrity discipline elsewhere. **Not a bug; a
content-completeness item** (real captions are the school's to supply), listed under
Content Credibility below, not as an accessibility defect.

**Severity:** P2 (roving-tabindex enhancement; not urgent). The original P1 has been
resolved and closed, not carried forward.

### `alumni.html` — 8.3

**Concept.** "Where CIRS Takes You" — rings visualization, "150 destinations, one origin",
"Four paths, followed in public" (four named, real alumni), an institutions list organised
by country with counts (India 87, UK 16, US 21, …).

**What works.** The destination/journey metaphor is specific to what Alumni pages are for
(brief Section 9: "If I removed the text and navigation, could I still tell what this page
is about?" — yes), and using real named alumni with real destination counts is exactly the
"claim-evidence" discipline the brief asks for (Section 133) rather than generic "our
graduates go on to great things" copy.

**What's unverified / at risk.** 44 buttons across 26.3vh — interaction density and pattern
(likely filters/expand-on-institution) **NOT VERIFIED**.

**Severity:** P3.

### `admissions.html` — 8.0

**Concept.** No on-page form — a six-step "From enquiry to enrolment" structure (Enquire →
confirm entry route → review application portal → assessment → next steps → follow the
offer), entry requirements, dates, published fee schedule, a checklist.

**What works.** Confirmed `forms: 0` — this is a deliberate, correct choice: the actual
application happens on the school's own external portal (`easycollege.in`), and the page's
job is to be the clearest possible map to that portal plus the facts a parent needs before
using it. That is the right call for the brief's own Admissions Special Audit standard
("visual experimentation must never obstruct this information") — the page is
information-first by design, and scores accordingly on UX even though its visual identity
is the most conventional of the "flagship-tier" pages.

**Severity:** none confirmed.

### `art-attack.html` — 8.2 (raised from 7.7 after live measurement; DOM weight concern did not hold up)

**Concept.** Film opening, then "Made by Hand" / "On the Wall" / "How the Work Gets Made" /
"Wall Magazines" / "From the Art Room to the Stage" — organised by medium and process, not
just chronology.

**What works.** The medium-based organisation is a real curatorial decision, not a default.

**Update — the DOM-weight risk was measured live, and the real picture is much better than
the raw node count suggested.** The original report flagged 2,668 DOM nodes and 297 `<img>`
elements as a confirmed performance-risk outlier. Live measurement (Performance/Resource
Timing APIs, and checking exactly what a real browser fetches, not just what's in markup)
found:

- Of the 297 `<img>` tags, only **100 are actually revealed** on initial load — the other
  197 sit behind a "Show more works (197 more)" button, correctly hidden via `display:none`
  and marked `loading="lazy"`, and **are never fetched** until a visitor asks for them
  (confirmed by `assets/js/artattack.js`'s own design intent — *"Hidden images are lazy and
  so are never fetched"* — and verified live: hidden count matched the button's stated
  count exactly, 197 = 197).
- Of those 100 visible images, ~86 are individual-artwork thumbnails using a proper
  `-t.webp` thumbnail pipeline (4–15KB each on disk).
- The other ~14 are larger "process" photographs (`photos/<id>.webp`) used at genuinely
  large display sizes (up to ~966px wide). **A first check of these looked like a real
  bug** — the fallback `src` attribute points at a full-resolution 1800px-wide master
  (up to 559KB for `paper-table.webp`) — but checking `img.currentSrc` after letting the
  image actually load showed the browser correctly resolves its `srcset`
  (`paper-table-m.webp 900w, paper-table.webp 1800w`) and `sizes`
  (`(max-width: 700px) 60vw, 22vw`) down to the **68KB, 900w variant** — a properly-built
  responsive image, not a bug. `tools/make-art-attack.py` generates exactly this `-m.webp`
  variant by design (*"the same, at the width a phone asks for"*) and it works as intended
  at both mobile and this audit's 1440px desktop test width.
- Estimated real initial image payload with this architecture: roughly **1.5–1.6MB**
  (≈86 × ~8KB thumbnails + ≈14 × ~54KB process photos + 2 hero images) — reasonable for a
  100-tile visual arts gallery, not the "network weight regardless of lazy-loading" this
  report originally assumed.

**What's still true, and not changed by this correction:** the raw DOM node count (2,668)
is real and remains the highest on the site — this exists to support client-side filtering
and the "Show more"/category-select interactions across all 297 works, which is a
legitimate reason for it, not an accident. At this scale it is not evidenced to cause a
real problem (modern browsers handle DOM trees far larger than this without issue, and no
jank, layout, or memory symptom was observed or measured), so it is recorded as a
structural fact about the page rather than carried forward as a performance risk.

**Severity:** none confirmed. The original P2 verification task is closed.

### `theatre.html` — 8.4 (raised from 7.9 after a live scroll-through; longest page on the site)

**Concept.** Three acts (Anand Utsav, Masquerades, Class Presentations), 97 images, film
opening. Masquerade entries are attributed to houses by verified Google Drive folder
provenance and the school's own YouTube titles — explicitly never by costume colour
(documented discipline in CLAUDE.md, confirmed structurally by the per-house heading
breakdown: "Valmiki House: Melora", "Vasistha House: Vantara", etc.).

**What works.** The provenance discipline is a genuine content-credibility strength — most
sites would eyeball costume colours and get it wrong; this one sources every attribution.

**Update — the pacing question was live-verified with a real scroll-through, and the
length is earned, not padded.** The original report flagged this as the site's longest
page (40.9vh) with unverified pacing. A full scroll-through (real scroll gestures, not
`window.scrollTo` jumps — this site's Lenis smooth-scroll overrides direct position jumps
within a frame, the same issue this audit hit and corrected for during the original pass)
found:

- The length breaks down as Act I Anand Utsav 7.1vh, Act II Masquerades **23.1vh**, Act III
  Class Presentations 1.9vh, plus intro/closing. Masquerades' dominance is not a design
  accident: the section's own on-page copy states the real number directly — **"Four
  productions and 59 photographs from the school's archive"** — and the four houses split
  that count almost exactly evenly (15/14/15/15 photographs, confirmed live), each spanning
  a near-identical ~5.2–5.5vh. The length is transparently earned by stated, real content.
- The four house sections are **not** a repeated template with swapped photos. Screenshot
  comparison of Valmiki (*Melora* — a warm, candy-circus set), Vishwamitra (*El Diablo* — a
  cold, green-lit forest set) and Vasistha confirmed genuinely different staging, lighting
  and costume design per production, as you'd expect from four different plays.
  Section-by-section: Hero STRONG, Act I EXCEPTIONAL (varied, well-captioned production
  photography with a clear "one stage, the whole school" closing beat), Act II Masquerades
  STRONG (long but transparently justified and visually varied — the strongest single
  argument against a "padding" reading of this page), Act III Class Presentations SOLID
  (compact by content type — a video archive, not a gallery — not by neglect), closing
  SOLID.
- A **sticky house-jump pill** (Valmiki / Vasistha / Vishwamitra / Vyasa) stays visible and
  correctly tracks the active house while scrolling through Masquerades, confirmed live —
  a visitor is never actually forced to scroll linearly through all four productions.
- Both act-to-act transitions carry an explicit **"NEXT — Act III · Class Presentations ↓"**
  wayfinding cue (confirmed live, screenshot-verified) ahead of a deliberate dark-to-ivory
  ground-colour fade, rather than an abrupt cut.
- Class Presentations' relative brevity (1.9vh) reflects a **different content type**, not
  thinner effort: `tools/theatre.py`'s `classes_html()` renders 6 recent videos as cards
  plus 19 earlier ones (2015–2019) inside a collapsed `<details>` archive — 25 real videos,
  deliberately compact because video cards don't need a photo gallery's vertical footprint.
- The closing section is a genuine strength, not a generic placeholder: it states precisely
  what's confirmed and what's still missing ("The full recordings of the 2025 Masquerades,
  photographs from earlier seasons, and the titles and casts of earlier productions are all
  still missing") with a direct `mailto:info@cirschool.org` call to action — exactly the
  specific, actionable disclosure the brief asks for in place of a generic
  under-construction note.

**Keep:** the transparent content stats, the house-jump wayfinding, the "NEXT" transition
cues, the honest closing disclosure. **Change:** none found. **Severity:** none — the
original P2 verification task is closed.

### `404.html` — 8.2 (small moment, worth naming)

**Concept.** Dark ground, "This path seems to have wandered beyond the campus.", gold
primary CTA ("Return Home"), four quick links. **(screenshot-verified, mobile)**

**What works.** Correct `--on-gold` (dark) text on the gold CTA fill — the exact rule
CLAUDE.md states ("Gold is never lettering on ivory, and text on a gold fill is `--on-gold`,
not white") is followed even on the page most sites treat as an afterthought. No dead end:
four concrete next steps, not just "go home."

**Severity:** none. **This is a Do-Not-Touch page** precisely because it is easy to
under-invest in a 404 and this site didn't.

---

## The Article/Blog Template Family

27 of the 58 routes — every News-archive report and every Blog essay — are built from
`newsarticles.ARTICLES` and `blogposts.POSTS` in `tools/build-site.py` onto the **same**
`"blog"` sheet with `"litehead": True`. This is a deliberate, sensible architecture
decision (one reading-page template for all long-form text content), confirmed by source,
not an accident — the Duplicate-Content Audit finding here is about *content*, not
*structure*.

**News-archive reports (11 routes, avg. Overall 5.9).** Two of eleven
(`vishu-tamil-puthandu.html`, `gayathri-havan.html`) carry `"gallery"` keys in
`tools/newsarticles.py` and render a real photo gallery. The other **nine** — Science Expo,
English Week, Mathematics Week 2025, Competitions, Social Science Week, Chinmaya Vraja, the
CIRS General Election, Seva Week, the solo-instrument recital — carry **zero** body
photography (confirmed: `imgCount: 4` on every sampled page, all four images accounted for
by shared chrome — logo, footer icons — not article content). This is the single largest,
most concretely fixable content-design gap on the site: a real campus event, reported in
plain text, when the same template two entries later demonstrably supports photography.

**Blog essays (17 routes, avg. Overall 7.2).** Structurally stronger: `anakin-skywalker.html`
carries a genuine four-act classical-tragedy structure (Hamartia / Peripeteia / Anagnorisis
/ Catharsis) as its section headings — this is real editorial ambition for a student essay,
not filler. All essays share the same plain single-column template with no illustrative
imagery beyond shared chrome, which is a defensible "text earns its own attention" choice
for an essay platform, but also the family's one shared missed opportunity (a pull-quote
treatment, or a single representative image per essay, would differentiate them further
without contradicting the text-first intent).

---

## Motion Audit

**Libraries, confirmed by script inventory on every page:** GSAP + ScrollTrigger + Lenis,
self-hosted from `assets/vendor/` (not a CDN — confirmed in network log on first page load),
loaded on every page except two: `cultural-gallery.html` (no ScrollTrigger/Lenis — correct,
the page doesn't scroll) and `houses.html` (ScrollTrigger present, **Lenis absent** — see
above, flagged as worth confirming intentional).

**Motion vocabulary observed (page-level, from DOM/script inventory — not exhaustively
interacted with):**

| Pattern | Where | Notes |
|---|---|---|
| Full-screen film-scrub opening | Sports, Captures, Art Attack, Festivals, Theatre | Shared `filmintro.js` — one real component, five pages, not five separate implementations |
| WebGL portrait | Founder | Unique to one page, protected by design brief |
| Three.js sacred-geometry opening | Spiritual Life | Unique to one page (recent commit `40051e3`) |
| Canvas-as-interface | Math Challenge | Unique; the only page using canvas for *interaction* rather than *opening spectacle* |
| Clip-path text-slice reveal (`aria-hidden`+`inert`) | Houses (confirmed); likely reused pattern | Genuinely well-built accessible technique — candidate for reuse ("Steal From Ourselves") |
| Sticky/pinned chapter sequence | School History | `history.js` |
| `prefers-reduced-motion` handling | Site-wide | Confirmed present in `cirs.css` at minimum 5 separate rule blocks (lines 153, 360, 620, 1179, 1255, 1370) |

**Assessment.** The site does not have five different motion languages fighting each other
— it has one shared film-opening component reused across five pages with page-specific
footage, plus three genuinely one-off techniques (WebGL, Three.js, canvas) each reserved for
the one page whose subject justifies it (Founder, Spiritual Life, Math Challenge
respectively). That is the opposite of the brief's "more animation/3D for its own sake"
anti-pattern — each advanced technique is used exactly once, on the page that earns it.

**What was not verified.** Entrance-timing precision (the Spiritual Life transient-frame
lesson above suggests it is worth a deliberate check, not that it is broken), ScrollTrigger
cleanup/duplicate-trigger behaviour on back/forward navigation, and ScrollTrigger behaviour
under `prefers-reduced-motion` on the four canvas/WebGL pages specifically — the CSS rule
exists site-wide, but whether the *JavaScript* motion (WebGL animation loops, canvas RAF
loops) also respects the media query was **NOT VERIFIED** and is worth a direct check,
since CSS `prefers-reduced-motion` rules do not automatically disable a `requestAnimationFrame`
loop written in JS.

---

## Mobile & Responsive Audit

**Measured, not inferred:** `document.documentElement.scrollWidth − window.innerWidth` at
390×844 was **0 on all 30 primary routes tested** — index, founder, why-cirs,
school-history, leadership, the-cirs-experience, spiritual-life, curriculum (+2 children),
our-results, sports, houses, our-laurels, math-challenge, crossroads, blog,
creative-writing, captures, art-attack, festivals, theatre, cultural-gallery, school-info,
important-documents, news, admissions, parent-portal, alumni, 404. **Zero horizontal-scroll
bugs found**, sitewide, at mobile width. This is an unusually clean result for a
58-page site this visually ambitious and is worth stating plainly as a genuine technical
strength.

**What that measurement does not cover.** Horizontal overflow is a binary, page-level check.
It does not verify: whether headings wrap awkwardly, whether hero text sits at a readable
size, whether a desktop-only interaction (drag, hover-reveal, cursor-follow) has a sensible
mobile equivalent, or whether tap targets meet a minimum size. Of those, this audit
**screenshot-verified** (not merely DOM-measured) mobile composition on Home, 404, Founder,
School History, Spiritual Life, Houses and Sports — all seven read cleanly, with headline
type sized appropriately and no visible crowding in the shared header pill despite it
carrying five distinct controls (Enquire / Home / wordmark / News / Menu).

**Confirmed-safe pattern:** the shared header collapses to a "compact translucent pill on
first scroll" (per CLAUDE.md) and this was directly observed holding steady across every
mobile screenshot taken, including on pages with very different ground colours (ivory on
Founder, dark plum on School History and Spiritual Life, black on Sports) — the header's
own contrast logic (`data-header-theme`) is working across all of them.

**Not verified:** the founder WebGL canvas's and math-challenge's three canvas elements'
mobile GPU/DPR behaviour on a real device (only viewport-emulated in this audit, which does
not reproduce real mobile GPU constraints); tablet width (768–1024px) was not tested in this
pass — the brief lists it as a required breakpoint and it is a genuine coverage gap in this
audit, not a claim that tablet is broken.

---

## Accessibility Audit

Full detail: [`ACCESSIBILITY_AUDIT.md`](ACCESSIBILITY_AUDIT.md). Summary:

**Strong, confirmed foundations:**
- `:focus-visible{ outline:2px solid var(--focus); outline-offset:3px }` defined once,
  globally, in `cirs.css` line 174, with a **context-aware override** for dark/photo grounds
  swapping to `--gold-lit` for contrast (line 1158) — this is a deliberate, non-trivial
  accessibility investment, not a browser default left alone.
- `prefers-reduced-motion` handled in at least 5 separate, purpose-specific rule blocks.
- Zero `img` with a missing `alt` attribute on any sampled page (`imgsNoAlt: 0` everywhere
  checked); the high `imgsEmptyAlt` counts sampled and verified as legitimately decorative
  (ambient photo walls, logo) rather than missing content descriptions.
- Zero external links with `target="_blank"` missing `rel="noopener"` on any page checked.
- Zero buttons with no accessible name on any page checked.
- Colour tokens carry their own contrast ratios as inline CSS comments (e.g. `--ink:
  #1F1F1B; /* 15.68:1 on ivory */`, `--campus: #2E5D3A; /* 7.26:1 on ivory */`) — evidence of
  contrast being designed-for, not checked after the fact.

**Retracted finding, corrected in this revision:** an earlier pass of this audit reported
the header drawer's own headings ("Talk to CIRS", "Portals", "Follow CIRS", "Site
navigation") as appearing in DOM order before the page's H1 and exposed to assistive
technology — based on a flat `querySelectorAll` that doesn't account for CSS-based hiding.
Live follow-up verification (walking each heading's ancestor chain for computed
`display`/`visibility`, not just the `hidden` attribute) found both containers are
genuinely removed from the accessibility tree by default — the drawer via `hidden`/
`display:none`, the Enquire panel via `visibility:hidden`+`opacity:0`+`max-height:0`. **This
was a false positive in the audit itself; there is no bug, and nothing needed fixing.** Full
detail in `ACCESSIBILITY_AUDIT.md`'s "Retracted finding" section.

**Verified live, and resolved well — A11Y-002:** `cultural-gallery.html`'s 180 buttons were
originally flagged as an unverified P1 (keyboard tab-order and focus-management unchecked).
A follow-up live keyboard pass found a visible skip link, a correctly-built
`role="dialog"`/`inert`/focus-trap pattern, deliberate keyboard-vs-pointer event separation,
and focus restoration confirmed to land back on the exact tile opened. One real, more minor
finding survives (all 168 tiles are simultaneous Tab stops with no roving-tabindex — a P2
enhancement, not a P1 defect), plus one unrelated, non-bug content finding (~45% of visible
photos carry a deliberately generic caption, pending real captions from the school). Full
detail in `ACCESSIBILITY_AUDIT.md`.

**Not verified:** screen-reader semantics with an actual AT (NVDA/VoiceOver), zoom-to-400%
reflow, and colour-blindness simulation on the four house colours specifically (their
contrast against ivory/dark grounds is documented in the CSS comments, but simulated
colour-vision-deficiency rendering was not checked).

---

## Performance & Asset Audit

Full detail: [`PERFORMANCE_AUDIT.md`](PERFORMANCE_AUDIT.md) / [`ASSET_AUDIT.md`](ASSET_AUDIT.md).
No Lighthouse/WebPageTest run was available in this environment — every figure below is a
direct filesystem or DOM measurement, labelled **MEASURED**, never a claimed Core Web Vital.

- **Deployed asset weight** (excludes `assets/source/`, which CLAUDE.md confirms never
  deploys): **585.4 MB across 2,156 files.**
- **Images:** 1,169 WebP vs. 760 JPG deployed (61%/39% split) — a real majority-modern-format
  posture, not a token gesture. Total `assets/img/` (deployed): 158.1 MB across 1,935 files.
- **Video:** 115.1 MB across 23 files (16 MP4, 7 WebM) — every film-opening page pairs a
  large-screen file with a phone-cut `-m.mp4` served via a media-query `<source>`, confirmed
  in `tools/build-site.py`'s `film_html()`.
- **Largest single deployed files:** Crossroads issue PDFs (up to 27 MB for issue 21) —
  these are downloads, not page-load weight, but worth flagging for the PDF/download
  experience audit (no file-size label shown next to the download link, confirmed absent
  from `important-documents.html`'s and Crossroads' link markup).
- **`art-attack.html`'s 2,668 nodes / 297 images, live-measured:** raised in an earlier
  version of this audit as a performance-risk outlier; live network/resource measurement
  found only 100 of the 297 images are ever fetched on initial load (the other 197 are
  correctly `display:none` + `loading="lazy"` behind a "Show more" button), and its
  larger process photographs resolve, via `srcset`, to properly-sized ~27–112KB variants
  rather than their multi-hundred-KB fallback `src`. Real initial image payload is an
  estimated 1.5–1.6MB — reasonable for a 100-tile gallery. The 2,668-node count itself
  remains the highest on the site (it supports real filtering across all 297 works) but no
  measured consequence of that was found. See the Art Attack page audit for the full
  measurement.
- **Video loading discipline:** every sampled `<video>` element uses `muted` + `poster` +
  either `preload="none"` or a JS-gated `.load()` call after the poster paints (confirmed in
  `film_html()`'s `progressive_loader` script for Art Attack specifically) — this is
  deliberate bandwidth discipline, not an oversight.

---

## Design System & Technical Architecture

Full detail: [`DESIGN_SYSTEM_AUDIT.md`](DESIGN_SYSTEM_AUDIT.md). Headline finding: **this is
a real design system, not merely visual similarity.** Evidence:

- Colour is centralised as named roles (`--grounds`/`--paper`, `--ink`, `--gold`, `--campus`,
  status colours) at the top of `cirs.css`, each carrying its measured contrast ratio as an
  inline comment — page sheets read these roles rather than declaring their own colour
  values (confirmed: no page-local hex colour was found duplicating a root token in the
  files sampled).
- `:focus-visible` and `prefers-reduced-motion` are defined **once**, globally, and
  overridden contextually (dark grounds) rather than redefined per page.
- The film-opening component (`filmintro.js` / `assets/css/filmintro.css`) is one shared
  implementation reused across 5 pages with page-specific data, not 5 copies.
- `netlify.toml` and `vercel.json` coexisting is a **documented, deliberate** transitional
  state (per CLAUDE.md/HOSTING.md), not architectural drift.

**Confirmed technical debt (not fabricated — direct script-count evidence):** Founder (11
scripts) and Crossroads (4 dedicated scripts beyond the shared 7) are the two most
fragmented pages on the site. Current execution on both is strong; the risk is future
maintainability, not present-day user experience.

---

## Repetition & Cross-Page Consistency

**Intentional, correct consistency (not flagged as repetition):** the shared header, drawer,
footer, button and card primitives are identical across all 58 pages by design — this is
what makes the site read as one system rather than assembled components, and the brief
explicitly says not to punish consistency.

**One shared component reused deliberately across a cluster:** Sports, Captures, Art Attack,
Festivals and Theatre all open on `filmintro.js`'s scrubbed-video pattern. This is
**intentional design-system consistency, not undesirable sameness** — each page supplies
its own footage and title, and the underlying device (a film the reader scrubs with scroll)
is distinctive enough, and rare enough outside this cluster, that five uses does not exhaust
it. It would become a problem at a sixth or seventh use; it is not one yet.

**One confirmed near-duplicate content pair, worth a content pass, not a structural
fix:** `why-cirs.html` states "Two boards. One ambition." as a narrative section heading and
then, in a closing summary-card grid, restates it as "Two boards, one ambition." — likewise
"Knowledge. Service. Skill." and "Knowledge, service and skill." This reads as a deliberate
narrative-then-recap device more than an error, but the near-identical wording (punctuation
is the only difference) means the recap cards don't add new phrasing the way a true summary
should. **P3, content polish.**

**Curriculum family (`curriculum.html`, `curriculum/ib-diploma.html`,
`curriculum/cbse.html`):** IB and CBSE share the same `"ibdp"` sheet deliberately (confirmed
in `tools/build-site.py`: "It wears the IB page's sheet, which is the curriculum family's
furniture"). This is documented, intentional twin-page architecture, not accidental
duplication — flagged here only to confirm it was checked, not to recommend a change.

---

## Broken-Experience Report

Full detail (mostly a clean bill, stated plainly): [`BROKEN_EXPERIENCES.md`](BROKEN_EXPERIENCES.md).

- **Broken links / missing assets:** `python tools/check-links.py` → **"58 pages, 10,119
  references, all resolve."** Zero broken links or missing assets, measured directly, not
  sampled.
- **HTML validity:** `npx html-validate@11` on all 58 pages (including both `curriculum/`
  children) → **zero errors.**
- **Console errors:** none observed on any of the ~36 pages navigated to during this audit
  (Home, Founder, Why CIRS, School History, Leadership, The CIRS Experience, Spiritual Life,
  Curriculum ×3, Our Results, Sports, Houses, Our Laurels, Math Challenge, Crossroads, Blog,
  Creative Writing, Captures, Art Attack, Festivals, Theatre, Cultural Gallery, School Info,
  Important Documents, News, Admissions, Parent Portal, Alumni, 404, plus 6 article samples)
  — spot-checked explicitly on School History and Spiritual Life, silent (no output) on every
  other page's console.
- **404 handling:** confirmed correctly served with a designed page, not a bare browser error.
- **Placeholder content:** exactly one — `our-laurels.html`, explicitly and honestly labelled
  as such (see Route Inventory).
- **Content gap presented as "broken":** the 9 photo-less News reports are **not** broken —
  every link and image tag resolves; the report is simply text-only. Listed here for
  completeness per the brief's own instruction to record even non-bugs precisely.

---

## Content Credibility & Underdesigned Pages

**The single clearest underdesigned-content finding on the site:** the 9 photo-less
News-archive reports. What exists: specific, factual report copy (dates, names of events,
outcomes). What the interface fails to communicate: any visual evidence that the event
happened — on a site whose credibility elsewhere rests heavily on real, specific campus
photography (School History's sourced archive, Theatre's provenance-verified house
attributions, Captures' curated photo essay). What design opportunity is wasted: the
template already supports a gallery (`newsarticles.py`'s `"gallery"` key, proven working on
2 of 11 entries) — this is a **content-population task against an existing, working
template**, not a redesign.

**A second, smaller instance of the same underlying pattern, found during live keyboard
verification of Cultural Gallery:** roughly 45% of the photographs visible in one viewport
(30 of 67 sampled) carry a generic, non-descriptive accessible name
("CIRS cultural gallery photograph 12 — CIRS Cultural Gallery") rather than a real caption.
Unlike the News reports, this is **not** a case of the interface failing to use content the
school has already supplied — `tools/artswall.py`'s own comment states the team
deliberately declines to invent a caption for a photo whose real subject or occasion isn't
documented, rather than guessing. That is the same content-integrity discipline that makes
School History and Theatre trustworthy, applied consistently here — the right call, not an
oversight. It is still real content the school could usefully supply for these ~30 photos,
the same category as several other "captions/credits owed" items already tracked
informally elsewhere on this site.

**No other underdesigned-content pattern was found** with comparable confidence. Long-form
pages are long because their subject genuinely spans a year or an anthology, not because
content is padded. Theatre's length was live-verified directly (a full scroll-through
confirmed 59 real, stated photographs and genuinely varied per-house staging behind its
40.9vh — see the Theatre page audit); Festivals and Creative Writing were not individually
scroll-verified in this pass, but show the same DOM-level signal Theatre did before its
check (real per-section headings, not repeated near-identical structures stacked
back-to-back) — worth the same live confirmation if either becomes a priority.

---

## Do-Not-Touch List

| Route | What must be preserved | Why |
|---|---|---|
| founder.html | The WebGL opening, its timing, its restraint | Explicitly designer-protected in CLAUDE.md; screenshot-confirmed as the most typographically confident moment on the site |
| school-history.html | The archive concept, the six-chapter structure, the sourced-milestone discipline | Best Page Identity Test pass on the site; content credibility is structurally protected by `tools/history.py` |
| math-challenge.html | Canvas-as-interface-logic | Directly realises the brief's own "math as interaction, not decoration" ask — do not replace with static images |
| spiritual-life.html | The mandala concept, the precise Sanskrit vocabulary | Restraint and specificity are exactly what the brief's own Spiritual Life audit asks for; do not add more ornament |
| houses.html | The `aria-hidden`+`inert` clip-path text-reveal technique | Genuinely well-built accessible motion pattern — a "steal from ourselves" candidate for reuse, not just a keep |
| cultural-gallery.html | The dialog pattern: `role="dialog"`+`inert`+keyboard/pointer event separation (`e.detail===0`)+focus restoration to the correct recycled tile | Live-verified, genuinely careful engineering for a hard problem (a virtualized, draggable photo field); a "steal from ourselves" candidate for any future lightbox on the site |
| theatre.html | The sticky house-jump nav, the explicit "NEXT — Act …" transition cues, the honest closing disclosure with a direct email CTA | Live-verified: real wayfinding that prevents the page's real length from ever feeling like a forced scroll, and a closing pattern (state what's confirmed vs. missing, ask for it directly) worth reusing anywhere else on the site that has a similar gap |
| 404.html | The gold-CTA contrast, the quick-links list | An easy page to under-invest in; this one wasn't — protect it from being simplified into a bare error message |
| `:focus-visible` / `prefers-reduced-motion` rules in `cirs.css` | The global-with-contextual-override pattern | Root-level accessibility investment; any redesign must keep both, not reintroduce per-component overrides |
| art-attack.html | The `srcset`/`sizes` responsive-image setup and the hide-until-"Show more" gating for 197 of 297 images | Live-verified to work correctly (confirmed via `currentSrc`, not just markup) — a genuinely well-built pattern for a large, filterable image collection; worth reusing wherever else on the site renders a large gallery |

---

## Redesign Priority Matrix

Full detail: [`REDESIGN_PRIORITY.md`](REDESIGN_PRIORITY.md). Summary:

| Priority | Route(s) | Current | Potential | Effort | Problem | Direction |
|---|---|---|---|---|---|---|
| P1 | 9 photo-less News reports | 5.7 avg | High | S–M (content, not code) | Zero photography on a photography-literate site | Populate `tools/newsarticles.py`'s existing `"gallery"` key per report, matching the 2 that already work |
| P2 | cultural-gallery.html tile Tab-order | 8.4 | Low–Medium | M | 168 tiles are simultaneous Tab stops, no roving-tabindex | Add a roving-tabindex/grid pattern if this page gets engineering attention; not urgent — *(the keyboard/focus-trap question itself was live-verified and resolved well; this is the one real item that survived)* |
| P2 | houses.html missing Lenis | 8.4 | Low–Medium | S | Only page in its visual family without smooth-scroll | Confirm intentional; if not, restore Lenis for consistency |
| P3 | why-cirs.html recap-card wording | 7.3 | Low | S | Two heading pairs restate each other near-verbatim | Differentiate the recap-card wording from the narrative headings above them |
| P3 | Founder / Crossroads script fragmentation | 8.8 / 8.4 | Low (maintainability only) | M | 11 and 4+7 scripts respectively | Not urgent; consolidate opportunistically during unrelated future work on these pages |

*Three rows from earlier versions of this matrix have been resolved and removed, all by
live verification rather than a code change: "Header/drawer heading order" (the headings in
question were already correctly excluded from the accessibility tree — see Accessibility
Audit), "theatre.html pacing" (a full scroll-through found the page's 40.9vh length is
transparently earned by 59 real, stated photographs and genuinely varied per-house staging
— see the Theatre page audit above), and "art-attack.html DOM weight" (live network/resource
measurement found the page's responsive images and hide-until-requested gallery already work
correctly — see the Art Attack page audit above). None needed a fix; see Accessibility
Audit's "Retracted finding" section for the first one.*

**our-laurels.html** is deliberately excluded from this matrix — it is an honestly
disclosed placeholder awaiting content the school owns, not a design problem to solve.

---

## Quick Wins

| Change | Route(s) | Effort | Expected Impact |
|---|---|---|---|
| Add a file-size label next to Crossroads issue and Important Documents PDF links | crossroads.html, important-documents.html | S | Several Crossroads PDFs exceed 20 MB; a visitor should know before tapping on mobile data |
| Populate 1–2 photographs on the highest-traffic photo-less News reports first (Science Expo, English Week) | science-expo.html, english-week.html | S (content) | Proves the template works before committing to all 9; matches the two entries that already have galleries |
| Confirm/restore Lenis on houses.html | houses.html | S | Removes one scroll-feel inconsistency between sibling pages in the same visual family |

---

## Design Debt Map

| ID | Root problem | Routes affected | Severity | Correct fix |
|---|---|---|---|---|
| DESIGN-002 | why-cirs.html recap cards restate narrative headings near-verbatim | why-cirs.html only | P3 | Content edit, not a component fix |
| DESIGN-003 | houses.html missing Lenis vs. sibling pages | houses.html only | P2 | Confirm intent; restore if accidental |
| DESIGN-004 | cultural-gallery.html's 168 tiles are simultaneous Tab stops, no roving-tabindex | cultural-gallery.html only | P2 (live-verified; not urgent, page is fully operable) | Add roving-tabindex/grid navigation if this page gets engineering attention |
| TECH-001 | Script fragmentation (Founder: 11 scripts; Crossroads: 4 dedicated + 7 shared) | founder.html, crossroads.html | P3 (maintainability) | Opportunistic consolidation, not urgent |

*~~TECH-002 (art-attack.html DOM size)~~ — resolved and removed. Live measurement found
the 2,668-node DOM causes no measured network, memory or jank problem; its images are
correctly gated and responsive. See the Art Attack page audit.*

---

## Final Verdict

**THE WEBSITE AT ITS BEST:** School History's archive, Founder's WebGL opening, Spiritual
Life's mandala (once settled), Math Challenge's interactive canvases, Houses' accessible
text-reveal technique, Cultural Gallery's live-verified dialog engineering, Theatre's
transparently-earned Masquerades act, Art Attack's correctly-gated 297-work gallery,
Sports' macro-texture film, 404's quietly complete small moment.

**THE WEBSITE AT ITS WORST:** the 9 photo-less News-archive reports, and Our Laurels'
disclosed placeholder — both content gaps, not design failures.

**WHAT MUST BE PRESERVED:** everything in the [Do-Not-Touch List](#do-not-touch-list),
especially the global `:focus-visible`/`prefers-reduced-motion` pattern and the
canvas-as-interface-logic device on Math Challenge.

**WHAT MUST BE FIXED FIRST:** nothing. Every code-level item this report raised as an open
risk across its full revision history — drawer heading order, Cultural Gallery's
keyboard/focus behaviour, Theatre's pacing, and Art Attack's DOM weight — was checked live
rather than left as an assumption, and none needed a fix: the heading order was a false
positive; Cultural Gallery's dialog engineering is genuinely well-built (one small,
non-urgent enhancement noted); Theatre's 40.9vh length is transparently earned by real,
stated content; and Art Attack's images are correctly lazy-gated and responsive, resolving
to properly-sized files in practice despite a large raw DOM node count. The only genuinely
open items left anywhere in this audit are content the school owns (9 News reports, Our
Laurels, ~30 Cultural Gallery captions) and two low-stakes confirmations (Houses/Lenis,
why-cirs.html's recap wording).

**WHAT SHOULD BE REDESIGNED NEXT:** nothing on this site needs a *redesign* by the evidence
gathered here, and — after four rounds of live verification — nothing needs a code fix
either. What it needs is photographs on 9 News reports and, informally, captions for ~30
Cultural Gallery photos.

**WHAT SHOULD NOT RECEIVE MORE COMPLEXITY:** Art Attack (already the heaviest single page
on the site by DOM node count, even though that count is now confirmed harmless) and any
page tempted to add a fourth advanced-motion technique alongside
WebGL/Three.js/canvas — the site's restraint (one advanced technique per page, each
justified by its subject) is a genuine strength and should not be diluted by adding a
signature effect to a page that doesn't need one.

**WHERE ADVANCED CREATIVE DEVELOPMENT IS ACTUALLY JUSTIFIED:** nowhere new, on this
evidence. The three pages that currently carry WebGL/Three.js/canvas are exactly the three
pages whose subject justifies it (a founder's likeness, a sacred-geometry contemplative
space, mathematical demonstration). Extending any of those techniques to a fourth page
without an equally specific reason would be exactly the "3D because it's available" pattern
the brief warns against.

**FINAL TOP 10 / BOTTOM 10:** see [Top & Bottom Pages](#top--bottom-pages).

**FINAL PRACTICAL IMPLEMENTATION ORDER:**
1. ~~Live keyboard/focus pass on Cultural Gallery~~ — **done**, resolved well; see
   `ACCESSIBILITY_AUDIT.md` A11Y-002. Its one surviving item (roving-tabindex across 168
   tiles) is a P2 enhancement for whenever this page next gets engineering attention, not
   an immediate next step.
2. ~~Live pacing scroll-through on Theatre~~ — **done**, resolved well; the length is
   transparently earned (59 stated photographs, genuinely varied staging per house). A
   mid-page spot-check of Spiritual Life and School History's choreography remains
   optional, lower-confidence follow-ups, not required.
3. ~~Art Attack DOM-weight measurement~~ — **done**, resolved well; live network/resource
   measurement found the responsive images and "Show more" gating already work correctly.
   The 2,668-node DOM remains the highest on the site but causes no measured problem.
4. Populate photographs on the 2 highest-value photo-less News reports as a proof of
   concept, then the remaining 7 if it reads well.
5. Confirm the Houses/Lenis discrepancy; restore if unintentional.
6. Everything else on the [Quick Wins](#quick-wins) list, opportunistically.

No step in this order is a redesign. The website's ceiling is already visible in its own
best pages — the work is finishing what's started and verifying what wasn't screenshotted,
not reimagining what already works.

---

*Generated by an audit-only session. No `.html`, `.css`, `.js`, or `tools/*.py` file was
modified to produce this report or its supporting files.*
