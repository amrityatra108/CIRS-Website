# CIRS-Website

The website for Chinmaya International Residential School, Siruvani, Coimbatore.

A static site — ten pages, no server-side code, no database. The pages are generated from
partials by a small Python script, so nothing needs installing to serve it: the `.html` files
plus `assets/` are the whole thing.

| Path | What it is |
| --- | --- |
| `index.html` and ten others | the pages — **generated, do not edit** |
| `tools/pages/`, `tools/partials/` | what the pages are generated *from* |
| `tools/build-site.py` | the page list, and the build |
| `assets/` | styles, the interaction layer, photography, the campus video |
| `docs/design-system.html` | the design specification |
| `HOSTING.md` | how to put it online, how to edit it, and what the school still owes |
| `.github/workflows/ci.yml` | HTML validity, link resolution, page freshness |

The home page is a short scroll — hero, film, the credentials ticker, the motto and the
closing call to action. Everything else lives on its own page, reached from the menu, from the
News tab in the header, or from the Home tab that every inner page carries.

Every `.html` file at the root is generated. Edit `tools/pages/` or `tools/partials/`, then:

```sh
python3 tools/build-site.py
```

There is also a point-and-click content editor, currently parked — `tools/build-bundles.py
--editor` rebuilds it on demand. See [HOSTING.md](HOSTING.md).

CI runs `npx html-validate *.html`, `python3 tools/check-links.py`, and a rebuild that fails
if the committed pages have drifted from their sources.

See [HOSTING.md](HOSTING.md) for deployment and for importing a new design artifact.
