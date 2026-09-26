# Navigation prototype

An isolated study of the header, the full-screen menu and Enquire. It changes
the design and the behaviour of the navigation, not the colour scheme. **It does
not replace the production navigation.** Nothing here is built by
`tools/build-site.py` or shipped by `tools/stage-deploy.py`.

To view it, serve the repository root and open the prototype:

```sh
python3 -m http.server 8000     # from the repository root
# http://localhost:8000/previews/navigation/
# ?page=<slug> shows it as that page would: its menu category opens first
# and its row is marked "You are here" (default: sports)
```

## What it holds to

- **Colour.** `nav.css` defines no colour. Every value is a role from the top of
  `assets/css/cirs.css`: `--paper` for the header, the category area and
  Enquire; `--paper-2` for the destination area; `--ink`, `--ink-soft` and
  `--ink-mute` for lettering; `--rule` for hairlines; `--gold` only for rules,
  indicators and the one filled button, with `--on-gold` on it. There is no
  glass, no translucent capsule and no gradient. Green and purple are not used.
- **Content.** The menu block in `index.html` was written from `MENU` and
  `PAGES` in `tools/build-site.py`: the same five groups, pages, labels and
  destinations, in the same order. Enquire carries the same sections,
  wording and nine destinations as `tools/partials/header.html`, and the
  menu's foot keeps the drawer's two calls to action and four utility links.
  A `<base href="../../">` lets every href be written exactly as production
  writes it.
- **Behaviour carried over from `cirs.js`.** Hover intent on the categories,
  keyboard focus opening Enquire, Escape, the Tab loop while the menu is open,
  and the header sliding away past the opening, with the gold hairline
  holding its place.

## Adopting it

If it is approved, `nav.css` and `nav.js` become the header, drawer and
Enquire rules in `pages.css`, `drawer.css` and `cirs.js`. `nav_html()` in
`build-site.py` takes the `nv-item` markup, and `header.html` and
`drawer.html` take the rest. Screenshots and a recording are in
`review/navigation-prototype/`.
