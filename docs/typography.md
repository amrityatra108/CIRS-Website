# Self-hosted typography

## Current status

The English body and interface use Mona Sans. Newsreader remains the display face, Literata remains in selected editorial passages and headings, and EB Garamond remains in quotations and selected emphasis until licensed Brier files are supplied. Jost's film-title role has moved to Mona Sans. Tiro Devanagari Hindi continues to cover Hindi, Sanskrit and Devanagari text. This is an interim stage of the requested Brier and Mona Sans pairing.

The family tokens are in `assets/css/cirs.css`; `assets/css/typography.css` assigns shared weights and roles after the page sheets. Page sheets use those semantic tokens. The non-deployed Brier mapping is in `tools/typography-brier.css`. It must only be activated after the font files and their licence have been checked.

| Role | Current face | Treatment |
| --- | --- | --- |
| English body, controls, navigation, labels, dates, captions and data | Mona Sans | Variable weights; body 350, navigation 450, labels 500, controls 600 |
| Thin film titles | Mona Sans | Weight 200, width 105% |
| Display headings | Newsreader | Existing display scale and authored casing retained pending Brier |
| Selected editorial passages and headings | Literata | Existing editorial role retained pending Brier |
| Quotations and expressive heading emphasis | EB Garamond | Genuine italic pending Brier |
| Hindi, Sanskrit and Devanagari | Tiro Devanagari Hindi | Genuine 400 face; script-specific line height and tracking retained |

Font synthesis is disabled globally. The homepage hero keeps its approved weight 400 exception. `:lang(hi)`, `:lang(sa)` and `.deva` selectors keep Mona Sans and future Brier from overriding Devanagari.

## Font files and licences

Mona Sans v2.0.27 comes from the [official Mona Sans repository](https://github.com/github/mona-sans) at pinned commit `0f7dc66ddd766605eb0e75c3f47bf9d1dd38ceca`. It is licensed under SIL Open Font License 1.1; the full notice is `assets/fonts/licenses/monasans-OFL.txt`. The three upstream variable WOFF2 files are kept byte for byte. The regular upright file contains weight and optical-size axes; the second upright file also has the width axis and is selected for expanded film titles; the third is a true italic. The generated CSS declares weight 200–900 and only the axes present in each file. A 92% `size-adjust` is used to keep existing layouts close to their earlier metrics.

Newsreader, Literata, EB Garamond and Tiro Devanagari Hindi remain self-hosted under their existing SIL OFL 1.1 notices while they have active roles. Jost's deployed font and notice were removed after its film role changed. `assets/fonts/manifest.json` records revisions, upstream URLs, SHA-256 hashes and byte sizes. `assets/css/fonts.css` is generated. No browser font request relies on a third-party font service.

No licensed Brier font file is stored in this public repository. Do not copy one from Lando Norris, a CDN, or an unofficial mirror. Type Department's standard Web License covers live text on one website domain and prohibits modifying, converting, or renaming its font software. `tools/make-fonts.py` therefore refuses Brier inputs and regenerates only the open fonts. The planned production integration will stage seller-supplied WOFF2 files privately, preserving their exact bytes and filenames, and activate Brier only on the licensed domain. That private staging is not implemented yet; the Brier mapping remains inactive. The actual CIRS invoice and supplied webfont kit must establish the licensed domain and weights before activation. The private licence and invoice must not be published.

## Rebuilding and checking

The normal site build needs no font tooling or network connection. To regenerate the optional open-font assets, install `fonttools[woff]==4.62.1` in an isolated Python environment and run `python tools/make-fonts.py`. The generator fetches pinned open-source sources during asset preparation, validates the embedded metadata and writes the files, CSS, manifest and licence notices. It reports `LICENSED BRIER FONT FILE REQUIRED` as a reminder that the display role remains interim; setting any `CIRS_BRIER_*` variable or placing Brier assets in the public source tree makes the command fail before it touches any font file.

The shared head preloads only the standard Mona Sans upright file and the current display upright file. Browsers fetch italic or the Mona Sans width file only when needed. Use a browser's network and computed-font views to confirm actual requests and rendering; source declarations alone cannot prove that a face loaded or that a glyph was present. Check cold-load layout shift separately from settled layout, especially around the animated hero and scroll-driven pages.

After a font change, run the site build, link check, HTML validation, JS and Python syntax checks, and generated-page drift check. Check all public routes at 1440×900, 1280×800, 768×1024, 390×844 and 320×640, including 200% zoom, keyboard focus, reduced motion, overflow, failed requests and console errors. Compare headline wraps, film titles, quotations and article reading comfort against the pre-change pages.
