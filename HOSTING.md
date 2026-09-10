# Chinmaya International Residential School — hosting

Everything in this zip is static. No build step, no server-side code, no database.

## What's in here

```
index.html                 the site
assets/css/cirs.css        styles
assets/js/cirs.js          interaction layer
assets/img/                the emblem, photography, favicon, social card
assets/video/               the hero background loop
dist/cirs-home.html        the entire site in one file (images inlined)
cirs-editor.html            a point-and-click tool for editing text and photos yourself
docs/design-system.html    the design specification
tools/                     scripts that regenerate the above (see below)
.github/workflows/ci.yml   the checks that run on every push and pull request
```

`index.html` and `assets/` are the source of truth. `dist/cirs-home.html` and `cirs-editor.html`
are built from them and should never be hand-edited — a `tools/build-bundles.py` run overwrites
both.

## The checks

Every push and pull request runs three things, all of which you can run yourself:

```sh
npx html-validate index.html      # structure and accessibility
python3 tools/check-links.py      # every anchor and asset reference resolves
python3 tools/build-bundles.py    # then: git diff --quiet -- dist cirs-editor.html
```

The last one is the important one. `dist/cirs-home.html` and `cirs-editor.html` are generated, and
nothing else stops someone editing a bundle directly and having the change silently overwritten by
the next build — so CI rebuilds them and fails if the committed copies differ.

The link check never touches the network. It verifies in-page anchors and `assets/` paths against
what is actually in the repository, and leaves external URLs alone: a check that goes red because
a CDN had a bad morning is one people learn to ignore. `href="#"` is the site's own placeholder for
a page that does not exist yet — the drawer and footer are full of them — and is allowed.

`.htmlvalidate.json` turns off exactly one rule, `no-autoplay`. The hero background is a muted,
looping, decorative video marked `aria-hidden`; that rule guards against media that starts making
noise at a visitor, which this cannot.

## Regenerating from a Claude artifact

The design lives as a Claude artifact: one self-contained HTML file with every photograph and the
campus video embedded as base64. When a new version of it comes back, split it into hostable files
rather than committing the 10 MB blob as the site:

```
python3 tools/sync-from-artifact.py path/to/artifact.html   # -> index.html, assets/*
python3 tools/build-bundles.py                              # -> dist/, cirs-editor.html
```

The sync keeps the curated `<head>` in `tools/head.html` (title, description, canonical URL, social
card) rather than the artifact's bare `<title>`, and names each embedded photograph from
`tools/media.tsv`, keyed by the md5 of its bytes. A photograph the table doesn't know about stops
the sync with the digest to add — so nothing ever lands in `assets/img/` as `image-7.jpg`.

It also reapplies one small correction the artifact does not carry — an explicit `type="button"` on
the two `<button>` elements, which the accessibility pass asks for. That belongs upstream in the
artifact eventually; until then it survives every sync. Keep that step tiny: anything larger than an
attribute should be fixed in the design, not patched on the way out of it.

## Put it online

**Netlify** (fastest, free)
1. Unzip the folder.
2. Go to **app.netlify.com/drop** and drag the unzipped folder onto the page.
3. It is live in about ten seconds on a `*.netlify.app` address.

**Cloudflare Pages or Vercel**
Connect the repository, then set framework preset **None**, build command **empty**,
output directory **`.`**

**GitHub Pages**
Push the contents to a repository, then Settings → Pages → deploy from branch → root.

**A normal shared host (cPanel, FTP)**
Upload `index.html` and the `assets` folder into `public_html`. That's it.

## Check it locally first

From inside the unzipped folder:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`. Opening `index.html` by double-clicking also works, but a
local server matches how it will behave once hosted.

## Just need to show someone quickly

`dist/cirs-home.html` is the complete site in a single file with every image embedded. Email it,
put it in Drive, or open it straight from disk — no server or `assets` folder required.

## Editing text and photos yourself — `cirs-editor.html`

Double-click `cirs-editor.html` to open it in any browser. No install, no login, no internet
connection required — it is the whole site in one file, in a version built specifically for
editing:

- **Click any headline, paragraph, or label** (it highlights gold on hover) and type — it behaves
  like a text box.
- **Click any photo, or the hero video**, and a file picker opens to replace it. If the same photo
  appears more than once (the emblem in the header and footer, for instance), every copy of it
  updates together.
- When you're done, click **Download Updated Site** at the bottom of the page. It saves a new file
  named `cirs-website-updated.html` to your Downloads folder — a complete, working copy of the site
  with your changes baked in, images and all.
- **Reload (discard changes)** throws away anything you typed since the last download and starts
  over from the original.

What to do with `cirs-website-updated.html` next:
- **Fastest:** it already works as a website on its own — rename it `index.html` and host it exactly
  as described above (Netlify drag-and-drop is easiest). The only downside is every photo is
  embedded in that one file rather than loaded separately, so the page is a little heavier than the
  optimised `index.html` + `assets/` version.
- **Best quality:** send `cirs-website-updated.html` back for the changes to be split back out into
  the faster `index.html` + `assets/` structure.

A few things this tool deliberately does not do: it won't let you add or remove whole sections,
reorder anything, or edit the scroll animation. It only touches the words and pictures already on
the page. It also runs the page without the scroll animation and motion effects (nothing to trip
over while you're clicking around) — those come back automatically in the real site and in the
exported file the moment it's opened as `index.html` in a normal browser.

## Before pointing the school's real domain at it

Two lines need the live address, because relative paths do not work for search engines or social
previews:

1. In `index.html`, set `<link rel="canonical" href="…">` to the live URL.
2. In `index.html`, make `og:image` and `twitter:image` absolute —
   `https://yourdomain.com/assets/img/og.jpg` rather than `assets/img/og.jpg`.

## Notes

- Three fonts load from Google Fonts, and GSAP and Lenis load from a CDN. All are cached and
  free. If the school needs everything self-hosted for a policy reason, those five files can be
  downloaded into `assets/` and the `<script>` and `<link>` tags repointed.
- The page works with JavaScript disabled — it simply renders without the animation.
- Links marked `#` are pages that do not exist yet in this prototype. They are deliberately inert
  rather than jumping to the top of the page.

## Still outstanding before a public launch

- **Have the school verify the Devanagari motto** — ज्ञानं सेवा च कौशलम् — reconstructed from the
  romanised form on the current site. It is the most prominent element on the page.
- **A vector version of the emblem**, for print and very large displays. The current one is the
  school's real medallion cropped from a supplied source, 320 px, which comfortably covers every
  on-screen use in this build.
- **The hero video loop is live** — `assets/video/campus-loop.mp4` (973 KB) and `.webm` (1.4 MB),
  encoded from the school's own supplied footage, muted, at 1600 px wide. `poster="assets/img/hero.jpg"`
  still covers the instant before it loads and any browser that can't play it. To replace it later,
  overwrite those two files with a new export — no HTML/CSS change needed.
- **Board results and university placement figures** from the examinations office.
- **A photography shoot.** Every image is the school's own, re-cropped and graded, but the best
  available source is about 1400 px wide.
- **The Principal's photograph and welcome message are live** — Rajeshwari Satish, cropped from a
  supplied photo to `assets/img/principal.jpg`.
- **Board of Directors introductions** for the Our People section. All eight roles are named and
  correct; every biography is a bracketed `[A short introduction to … to be supplied by the
  school.]` placeholder. Five of the eight also need a photograph — Swami Swaroopananda, Shri. Viju
  Mahtaney, Shri Jadgish Moorjani, Shri. Siddharth Balachandran and Shri. Ram Buxani currently
  render as a labelled placeholder tile.
- **A caption for the staff and faculty photograph** — occasion, date and names.
- **The Why CIRS photo is live** — `assets/img/why-cirs.jpg`, cropped from a supplied photo of three
  students to a 4:5 portrait, faces centred.
- **Photography for five sections that currently render as a labelled placeholder tile** instead of
  a photograph: Junior School, Senior School, Residential Life, Athletics, and Arts/Music/Theatre.
  Search the page for `feature__ph` to find each one.
- **Junior School and Senior School programme detail** — enrolment numbers, leadership names,
  specific outcomes — to replace the two `[Placeholder — …]` paragraphs in those sections.
- **Athletics and Arts specifics** — team names, fixtures, ensembles, and production dates — to
  replace the bracketed placeholder sentences in those two sections.
