# CIRS-Website

The website for Chinmaya International Residential School, Siruvani, Coimbatore.

A static site — no build step, no server-side code, no database. `index.html` plus `assets/` is
the whole thing; open `index.html` in a browser to see it.

| Path | What it is |
| --- | --- |
| `index.html` | the site, and the source of truth |
| `assets/` | styles, the interaction layer, photography, the campus video |
| `dist/cirs-home.html` | the entire site as one self-contained file, for emailing or a USB stick |
| `cirs-editor.html` | point-and-click editing of the copy and photographs, offline, no install |
| `docs/design-system.html` | the design specification |
| `tools/` | scripts that rebuild the two bundles, and that import a new Claude artifact |
| `HOSTING.md` | how to put it online, how to edit it, and what the school still owes |
| `.github/workflows/ci.yml` | HTML validity, link and asset resolution, bundle freshness |

Both files in the middle of that table are generated. Edit `index.html` and `assets/`, then run:

```sh
python3 tools/build-bundles.py
```

CI runs `npx html-validate index.html`, `python3 tools/check-links.py`, and a rebuild of the
bundles that fails if the committed copies have drifted from their sources.

See [HOSTING.md](HOSTING.md) for deployment and for importing a new design artifact.
