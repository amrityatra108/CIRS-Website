# CIRS-Website

The website for Chinmaya International Residential School, Siruvani, Coimbatore.

A static site — no build step, no server-side code, no database. `index.html` plus `assets/` is
the whole thing; open `index.html` in a browser to see it.

| Path | What it is |
| --- | --- |
| `index.html` | the site, and the source of truth |
| `assets/` | styles, the interaction layer, photography, the campus video |
| `dist/cirs-home.html` | the entire site as one self-contained file, for emailing or a USB stick |
| `docs/design-system.html` | the design specification |
| `tools/` | scripts that rebuild the two bundles, and that import a new Claude artifact |
| `HOSTING.md` | how to put it online, how to edit it, and what the school still owes |
| `.github/workflows/ci.yml` | HTML validity, link and asset resolution, bundle freshness |

`dist/cirs-home.html` is generated. Edit `index.html` and `assets/`, then run:

```sh
python3 tools/build-bundles.py
```

There is also a point-and-click content editor, currently parked — `tools/build-bundles.py
--editor` rebuilds it on demand. See [HOSTING.md](HOSTING.md).

CI runs `npx html-validate index.html`, `python3 tools/check-links.py`, and a rebuild of the
bundle that fails if the committed copy has drifted from its sources.

See [HOSTING.md](HOSTING.md) for deployment and for importing a new design artifact.
