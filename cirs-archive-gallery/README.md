# CIRS Archive — infinite photo gallery

An endless, explorable wall of photographs from Chinmaya International Residential School, in deep purple and gold. Visitors drag, swipe, scroll or use the arrow keys to move through it; clicking or tapping a photograph opens it full size. It works on desktop and on phones.

Everything it needs is in this folder. There is no build step and nothing to install.

## What's in the folder

```
cirs-archive-gallery/
├── index.html                 the whole page: HTML, CSS and JavaScript in one file
├── README.md                  this file
└── assets/img/
    ├── comb.json              the list of photographs (file, category, title)
    ├── *.jpg                  full-size campus photographs
    ├── gallery/*.jpg          full-size event and student-work photographs
    └── thumbs/*.jpg           small copies used on the moving tiles
```

Keep `index.html` and the `assets` folder side by side. The page finds its images relative to its own location.

## Try it locally

Opening `index.html` by double-clicking works; the page uses its built-in photo list.

To test exactly as it will run on a website, serve the folder instead:

```
cd cirs-archive-gallery
python -m http.server 8000
```

Then open <http://localhost:8000>.

## Adding it to a website

The gallery takes over the whole browser window: it's full-screen, it disables page scrolling, and it hides the normal mouse cursor. So it should be **its own page**, not dropped into the middle of an existing one.

**Option 1 — its own page (recommended).** Upload the whole `cirs-archive-gallery` folder to the web server, for example so it lives at `https://your-site.org/gallery/`. Then link to it from the site's menu:

```html
<a href="/gallery/">Photo Archive</a>
```

This works on any host that serves plain files: cPanel, WordPress (upload via FTP or the file manager into a folder outside the theme), Netlify, Vercel, GitHub Pages, and so on.

**Option 2 — inside an existing page with an iframe.** Upload the folder as above, then place this where the gallery should appear:

```html
<iframe src="/gallery/" title="CIRS photo archive"
        style="width:100%; height:100vh; border:0; display:block;"
        allow="fullscreen" loading="lazy"></iframe>
```

The height needs to be set explicitly. `100vh` fills the screen; a fixed value such as `720px` works too. Inside an iframe, scrolling over the gallery moves the gallery rather than the surrounding page — that is intended.

Don't paste the contents of `index.html` into another page. Its styles are written for a page of its own and would clash with the host site's.

## Changing the photographs

The photo list lives in **two places that must match**:

1. `assets/img/comb.json` — used when the page is served from a website.
2. The `plates` list near the top of the `<script>` in `index.html` — used when the file is opened from disk, or if `comb.json` can't be loaded.

Each photo is one entry:

```json
{ "src": "assets/img/gallery/stage.jpg",
  "thumb": "assets/img/thumbs/gallery_stage.jpg",
  "cat": "Theatre",
  "title": "Annual day, the amphitheatre" }
```

- `src` — the full-size image shown when the photo is opened.
- `thumb` — a small copy for the tiles, about 420px on its shorter side. If you don't make one, point `thumb` at the same file as `src`. It will still work, just less smoothly on phones.
- `cat` and `title` — shown when the photo is opened.

To add a photo, copy the image into `assets/img/`, add an entry in both places, and reload. The layout guarantees a photo never appears next to a copy of itself once there are six or more photos.

## Customising

- **Colours** — the `:root` block at the top of the `<style>` section (`--void`, `--plum`, `--gold`, `--gold-soft`, `--ivory`). The same gold also appears as `212,175,55` in a few places in the CSS and script.
- **Title** — search `index.html` for `CIRS<br>Archive`. It appears twice, once for the sharp copy and once for the soft copy; change both.
- **Corner labels** — search for `CIRS_Archive v4.0` and `Chinmaya International Residential School // Archive`.

## Requirements and notes

- **Browsers:** current Chrome, Edge, Safari (including iPhone and iPad) and Firefox.
- **Fonts:** Cormorant Garamond, Plus Jakarta Sans and Inter, loaded from Google Fonts. Without an internet connection the page falls back to system fonts and otherwise works normally. Nothing else is loaded from outside the folder.
- **Motion:** visitors who have asked their device for reduced motion get the gallery without the tilt and fling.
- **Performance:** only enough tiles to cover the screen exist at any time, and they are recycled as the view moves, so the page stays equally light however far someone explores.
