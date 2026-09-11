# Source photographs

Photographs from the school, held for making derived images. They are **not**
part of the site and no page references them.

Three batches, and they differ:

- The first batch is unedited camera originals — 8192px files, around 150 MB.
- 23 files added in September 2026 from a shared Drive folder, resized to
  3200px on the long edge (159 MB down to 24 MB).
- 70 files added in September 2026 from two further Drive folders — *CIRS -
  Academic Activities* and *CIRS* — also resized to 3200px (429 MB down to
  73 MB). Classrooms and laboratories, robotics, assemblies, NCC parades,
  athletics and swimming, dance and theatre, TEDx Youth@CIRS, SPIC MACAY,
  the prayer hall, music and art.

Everything after the first batch is resized on the way in. Drive remains the
archive of those true originals; at full size they would have added roughly
570 MB to every clone for detail no page can use — the largest thing the site
renders is 2400px, and a honeycomb cell is 460px. Nothing was dropped as a
duplicate: all 93 are distinct from each other and from what was already here.

They are here because derived images are made from them:
`tools/make-header.py` crops, blurs and grades one of these into
`assets/img/admissions-header.jpg`, a 140 KB banner. Keeping the originals
means the next banner is a one-line command rather than another round of
asking for the files.

Two things follow, and both are enforced rather than remembered:

- `tools/stage-deploy.py` copies only assets that a page actually references,
  so nothing in here reaches a web host. Before that rule existed, a
  copy-everything stage produced a 153 MB deploy of a 6 MB site.
- `tools/check-links.py` reports unreferenced files in `assets/img` and
  `assets/video` as orphans, because there they usually are. It does not look
  in here, which is the whole reason this directory is separate from
  `assets/img` rather than mixed into it.

Anything web-facing — cropped, resized, and referenced by a page — belongs in
`assets/img`, not here.
