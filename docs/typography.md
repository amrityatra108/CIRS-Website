# Self-hosted typography

## Current status

The English body and interface use Mona Sans. Bodoni Moda is the display face, selected as an openly licensed alternative to Brier. Literata remains in selected editorial passages and headings, and EB Garamond remains in quotations and selected emphasis. Jost's film-title role has moved to Mona Sans. Tiro Devanagari Hindi continues to cover Hindi, Sanskrit and Devanagari text.

The family tokens are in `assets/css/cirs.css`; `assets/css/typography.css` assigns shared weights and roles after the page sheets. Page sheets use those semantic tokens. The non-deployed Brier mapping is in `tools/typography-brier.css` for a future licensed installation.

| Role | Current face | Treatment |
| --- | --- | --- |
| English body, controls, navigation, labels, dates, captions and data | Mona Sans | Variable weights; body 350, navigation 450, labels 500, controls 600 |
| Thin film titles | Mona Sans | Weight 200, width 105% |
| Display headings | Bodoni Moda | Variable upright weights; existing display scale and authored casing retained |
| Selected editorial passages and headings | Literata | Existing editorial role retained |
| Quotations and expressive heading emphasis | EB Garamond | Genuine italic |
| Hindi, Sanskrit and Devanagari | Tiro Devanagari Hindi | Genuine 400 face; script-specific line height and tracking retained |

Font synthesis is disabled globally. The homepage hero keeps its approved weight 400 exception. `:lang(hi)`, `:lang(sa)` and `.deva` selectors keep Latin faces from overriding Devanagari.

## Font files and licences

Mona Sans v2.0.27 comes from the [official Mona Sans repository](https://github.com/github/mona-sans) at pinned commit `0f7dc66ddd766605eb0e75c3f47bf9d1dd38ceca`. It is licensed under SIL Open Font License 1.1; the full notice is `assets/fonts/licenses/monasans-OFL.txt`. The three upstream variable WOFF2 files are kept byte for byte. The regular upright file contains weight and optical-size axes; the second upright file also has the width axis and is selected for expanded film titles; the third is a true italic. The generated CSS declares weight 200–900 and only the axes present in each file. A 92% `size-adjust` is used to keep existing layouts close to their earlier metrics.

Bodoni Moda's upright and italic faces are built from [official source revision `30ce6cdc354ef179a3b72ba0f0e71826e599348c`](https://github.com/indestructible-type/Bodoni/tree/30ce6cdc354ef179a3b72ba0f0e71826e599348c), with the complete SIL OFL 1.1 notice retained in `assets/fonts/licenses/bodonimoda-OFL.txt`. The optical-size axis is fixed at 11 so headline hairlines remain legible; the genuine 400–900 weight axis remains variable. Literata, EB Garamond and Tiro Devanagari Hindi remain self-hosted under their SIL OFL 1.1 notices. Newsreader's open font files remain in source, though public pages no longer select them. Jost's deployed font and notice were removed after its film role changed. `assets/fonts/manifest.json` records revisions, upstream URLs, SHA-256 hashes and byte sizes. `assets/css/fonts.css` is generated. No browser font request relies on a third-party font service.

No Brier font file is stored or served by this site. Type Department's trial is for testing only, and a future live Brier installation would require a Web License for the production domain and seller-supplied webfont files. `tools/make-fonts.py` refuses Brier inputs and regenerates only the open fonts. The Brier mapping remains inactive; it is not part of the live font system.

## Rebuilding and checking

The normal site build needs no font tooling or network connection. To regenerate the optional open-font assets, install `fonttools[woff]==4.62.1` in an isolated Python environment and run `python tools/make-fonts.py`. The generator fetches pinned open-source sources during asset preparation, validates the embedded metadata and writes the files, CSS, manifest and licence notices. Setting any `CIRS_BRIER_*` variable or placing Brier assets in the public source tree makes the command fail before it touches any font file.

The shared head preloads only the standard Mona Sans upright file and the current display upright file. Browsers fetch italic or the Mona Sans width file only when needed. Use a browser's network and computed-font views to confirm actual requests and rendering; source declarations alone cannot prove that a face loaded or that a glyph was present. Check cold-load layout shift separately from settled layout, especially around the animated hero and scroll-driven pages.

After a font change, run the site build, link check, HTML validation, JS and Python syntax checks, and generated-page drift check. Check all public routes at 1440×900, 1280×800, 768×1024, 390×844 and 320×640, including 200% zoom, keyboard focus, reduced motion, overflow, failed requests and console errors. Compare headline wraps, film titles, quotations and article reading comfort against the pre-change pages.
