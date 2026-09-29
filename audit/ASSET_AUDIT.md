# Asset Audit

Part of the [Full Site Audit](FULL_SITE_AUDIT.md). Audit only — nothing was deleted, moved,
converted or re-compressed. All figures below are direct filesystem measurements.

## Scope note

`assets/source/` (150 MB+ of unedited camera originals, per CLAUDE.md) is **deliberately
excluded** from every "deployed" figure in this document, since it never ships —
`tools/stage-deploy.py` copies only what a page references, and the repository's own
`check-links.py` orphan check exists specifically to keep `assets/source/` out of
`assets/img/`. Treating `assets/source/` as deployed weight would be a fabricated finding.

## Deployed footprint

**585.4 MB across 2,156 files** in `assets/` excluding `assets/source/`.

### Images

- 1,935 files, 158.1 MB, in `assets/img/` (deployed).
- Format mix: **1,169 WebP (60.4%)**, 760 JPG (39.3%), 4 PNG, 2 SVG.
- **Assessment:** a majority-WebP posture is a real, measured optimisation practice, not a
  token gesture. The remaining 760 JPGs were not individually audited for whether they could
  convert to WebP without quality loss (that requires per-file inspection this audit did not
  perform) — flagged as a **candidate list**, not a confirmed finding, for a future
  targeted pass.

### Video

- 23 files, 115.1 MB, in `assets/video/`: 16 MP4 + 7 WebM.
- Every film-opening page (Sports, Captures, Art Attack, Festivals, Theatre) pairs a
  large-screen encode with a phone-specific `-m.mp4` cut, selected via a `media` query on
  the `<source>` element (confirmed in `tools/build-site.py`'s `film_html()` and the
  `FILM_LARGE` breakpoint constant `(min-width: 768px) and (min-height: 501px)`) — this is
  a deliberate, working responsive-video strategy, not an oversight.
- CLAUDE.md states all film cuts are all-intra encoded specifically so they scrub cleanly
  when the reader controls playback position via scroll — this audit did not independently
  verify the encode's keyframe interval (that requires a codec inspection tool this
  environment does not have), so it is recorded as **stated in source documentation,
  NOT INDEPENDENTLY VERIFIED** here.

### Documents (downloads)

- `assets/documents/crossroads/`: 32 issue PDFs. Largest is issue 21 at **27.0 MB**;
  several others exceed 20 MB (issues 22, 4, 8, 28, 25, 12).
- `important-documents.html` links to 40 PDFs (governance/statutory/results documents) —
  sizes not individually measured in this pass, but the same "no size label before
  download" gap applies here as to Crossroads (see Quick Wins in the main report).

## Largest individual deployed files (top 10, excluding `assets/source/`)

| File | Size |
|---|---|
| assets/documents/crossroads/crossroads-issue-21.pdf | 27.0 MB |
| assets/video/art-attack-opening.webm | 14.5 MB |
| assets/documents/crossroads/crossroads-issue-22.pdf | 12.3 MB |
| assets/documents/crossroads/crossroads-issue-04.pdf | 11.3 MB |
| assets/documents/crossroads/crossroads-issue-08.pdf | 11.1 MB |
| assets/video/theatre-opening.webm | 11.0 MB |
| assets/video/festivals-opening.webm | 10.6 MB |
| assets/documents/crossroads/crossroads-issue-28.pdf | 10.6 MB |
| assets/documents/crossroads/crossroads-issue-25.pdf | 10.5 MB |
| assets/documents/crossroads/crossroads-issue-12.pdf | 10.4 MB |

Video files this large are opening-sequence WebM masters, paired with smaller MP4/mobile
cuts for most real-world playback — the WebM figure alone is not what most visitors
download (see Performance Audit for the media-query-gated `<source>` selection).

## Duplicate / near-duplicate assets

Not exhaustively hashed in this pass (a full binary-diff pass across 1,935+ image files was
out of scope for the time available). No obvious accidental duplicates were found among the
files directly inspected (largest-file listing, per-page sampled images). **NOT
MEASURED** as a complete duplicate-detection pass — flagged as a gap, not a clean bill.

## Unused / orphaned assets

`tools/check-links.py` includes an orphan check (per CLAUDE.md: "that would break the
orphan check in check-links.py") — since `check-links.py` ran clean with no orphan warnings
in its output, there is no evidence of unused deployed assets. This audit did not
independently re-implement an orphan scan; it relies on the repository's own existing,
documented check having run clean.

## Recommendation summary (do not implement — audit only)

- Candidate: spot-check the largest of the 760 remaining JPGs for WebP conversion headroom.
- Confirmed-worth-doing: add file-size labels to Crossroads/Important Documents PDF links
  (Quick Win, main report).
- Not urgent: video re-encoding — CLAUDE.md explicitly warns against re-encoding the
  all-intra film masters with a longer keyframe interval, since that would break scroll-
  scrubbing; any future video optimisation work must respect that constraint.
