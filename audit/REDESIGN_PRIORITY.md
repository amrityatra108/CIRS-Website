# Redesign Priority Matrix

Part of the [Full Site Audit](FULL_SITE_AUDIT.md). Audit only — this is a planning
document, not implemented work. Priority = Severity×30% + Strategic Importance×25% +
Redesign Potential×25% + Cross-Site Impact×20%, normalized to 10, per the brief's formula.
Effort: S/M/L/XL. Potential: Low/Medium/High/Exceptional (how much stronger the page/system
could become, not current quality).

## Raw priority ranking

**Four items resolved since first publication, all by live verification rather than by
writing code.** "Shared header/drawer heading order" was originally ranked #1: live
follow-up (walking each heading's ancestor chain for computed `display`/`visibility`, not a
flat DOM query) showed the four headings in question are already correctly removed from
the accessibility tree — there was no bug. "Cultural Gallery keyboard/focus" was then
ranked #1: a live keyboard pass (real Tab/Enter/Escape presses) found a visible skip link,
a correctly-built dialog pattern, and confirmed focus-trap and focus-restoration behaviour
— also no bug requiring a code fix (one small, real enhancement survived — no
roving-tabindex across its 168 tiles — carried forward below at P2). "Theatre pacing" was
then ranked #2: a full live scroll-through (real scroll gestures, since this site's Lenis
smooth-scroll overrides direct `scrollTo` jumps) found the page's 40.9vh length is
transparently earned — its own on-page copy states "59 photographs," the four houses split
that count almost evenly, and screenshot comparison confirmed genuinely different staging
per house rather than a repeated template. "Art Attack DOM weight" was then ranked #2: live
Performance/Resource-Timing measurement found only 100 of 297 images are ever fetched on
initial load (the rest sit behind a "Show more" button, correctly hidden and lazy), and its
larger process photos resolve via `srcset` to properly-sized ~27–112KB variants rather than
their much larger fallback `src` — confirmed by checking `img.currentSrc` after load, not
just the markup. See `ACCESSIBILITY_AUDIT.md` and `FULL_SITE_AUDIT.md`'s Theatre and Art
Attack page audits for the write-ups. The ranking below has been renumbered accordingly.

| Order | Route / System | Current | Potential | Effort | Problem | Direction |
|---|---|---|---|---|---|---|
| 1 | 9 photo-less News reports (science-expo, english-week, mathematics-week-2025, competitions, social-science-week, chinmaya-vraja, cirs-general-election, seva-week, solo-instrument) | 5.7 avg | High | S–M per report (content, not code) | Real events reported with zero photographic evidence, on a photography-literate site | Populate `tools/newsarticles.py`'s existing `"gallery"` key, matching the 2 reports that already use it |
| 2 | cultural-gallery.html tile Tab-order | 8.4 | Low–Medium | M | 168 tiles are simultaneous Tab stops, no roving-tabindex | Add roving-tabindex/grid navigation whenever this page next gets engineering attention; not urgent |
| 3 | houses.html missing Lenis | 8.4 | Low–Medium | S | Only page in its family without smooth-scroll | Confirm intent; restore if accidental |
| 4 | why-cirs.html recap-card wording | 7.3 | Low | S (content) | Two heading pairs restate narrative headings near-verbatim | Differentiate wording between narrative section and recap cards |
| 5 | founder.html / crossroads.html script fragmentation | 8.8 / 8.4 | Low (maintainability only) | M | 11 and 4+7 scripts respectively | Opportunistic consolidation during unrelated future work |
| 6 | our-laurels.html | 3.3 | Exceptional (once content arrives) | Depends entirely on school-supplied data | Disclosed placeholder | Not a design task — awaiting competition records from sports/activities office |

*(Also worth noting, though not on this matrix since it's not a code task: ~30 Cultural
Gallery photos carry a deliberately generic caption pending real ones from the school — the
same category as `our-laurels.html`, a content gap rather than a design problem.)*

## Practical implementation order (dependency-aware — may differ from raw priority)

This site's problems are unusually independent of each other — there is no single shared
component whose fix would cascade across many pages the way the brief's own example
describes (the four candidates for that — the drawer heading order, Cultural Gallery's
dialog pattern, Theatre's pacing, and Art Attack's DOM weight — all turned out on
verification not to need a code fix at all — see above).

1. **Photograph population on the 2 highest-value News reports** (Science Expo, English
   Week) as a proof of concept against the existing template, before committing to all 9.
2. **Houses/Lenis confirmation.**
3. Everything else, opportunistically, in the order listed in
   [Quick Wins](FULL_SITE_AUDIT.md#quick-wins).

**Explicitly not on this list, and should not be added to it:** any page currently scoring
7.5+ that this audit did not flag a confirmed or plausible problem on. School History,
Founder, Spiritual Life, Math Challenge, Houses, Sports, Captures, Crossroads, Theatre,
Art Attack, Alumni, Admissions and 404 have no open finding above P3, and P3 findings on
this list (recap-card wording, script fragmentation) are explicitly polish-tier, not
blockers to anything.
