# Source photographs

Unedited originals from the school — 8192px camera files, around 150 MB in
total. They are **not** part of the site and no page references them.

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
