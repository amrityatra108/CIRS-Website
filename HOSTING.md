# Chinmaya International Residential School — hosting

Everything in this zip is static. No build step, no server-side code, no database.

## What's in here

```
index.html                 the home page
news.html                  the other ten pages, one file each
why-cirs.html
our-leaders-speak.html
our-leadership.html
academics.html
student-life.html
sports.html
arts.html
admissions.html
alumni.html
assets/js/pages.js         behaviour only a multi-page site needs
assets/css/cirs.css        the design system, imported from the artifact
assets/css/pages.css       the components only a multi-page site needs
assets/js/cirs.js          interaction layer
assets/img/                the emblem, photography, favicon, social card
assets/video/              the hero background loop
docs/design-system.html    the design specification
tools/                     the scripts that generate every page (see below)
tools/make-header.py       composes the Admissions banner photograph
tools/check-contrast.py    measures banner text against the pixels behind it
.github/workflows/ci.yml   the checks that run on every push and pull request
```

**Every `.html` file at the root is generated. Do not edit them.** A rebuild
overwrites them and CI fails if what is committed does not match a rebuild. Edit these
instead, then run `python3 tools/build-site.py`:

```
tools/pages/<slug>.html     the sections unique to that page
tools/partials/             the header, menu, footer and chrome every page shares
tools/build-site.py         the page list: titles, menu labels, banner copy
```

The site was one long page until the menu became redundant. It is now ten, which means
the header, menu and footer appear ten times — and a menu that has to be edited in ten
files is a menu that goes stale in nine of them. Hence the partials, and hence the
menu being generated from the page list in `tools/build-site.py`: add a page there and
it appears in the menu of all ten at once.

## The checks

Every push and pull request runs three things, all of which you can run yourself:

```sh
npx html-validate *.html          # structure and accessibility, every page
python3 tools/check-links.py      # every link and asset reference resolves
python3 tools/build-site.py       # then: git diff --quiet -- '*.html'
```

The last one is the important one. Editing a generated page by hand looks like it
works and is silently undone by the next build — and the menu, which is on all ten
pages, is exactly what someone would be tempted to fix in one file. So CI rebuilds and
fails if the committed pages differ.

The link check never touches the network. Since the site became ten pages the menu *is*
the navigation, so it verifies that `page.html#anchor` links point at a page that
exists **and** an anchor that exists on it — the failure a single-page checker cannot
see. External URLs are left alone: a check that goes red because a CDN had a bad
morning is one people learn to ignore. `href="#"` is the site's own placeholder for a
page that does not exist yet and is allowed.

`.htmlvalidate.json` turns off exactly one rule, `no-autoplay`. The hero background is
a muted, looping, decorative video marked `aria-hidden`; that rule guards against media
that starts making noise at a visitor, which this cannot.

## The Admissions banner photograph

`assets/img/admissions-header.jpg` is composed, not shot. `tools/make-header.py` takes a campus
photograph, crops it to 2:1, blurs it slightly so detail never competes with the type, maps it to a
duotone between the site's purple and a warm highlight, and darkens it along the diagonal the
headline sits on:

```sh
python3 tools/make-header.py                        # the default campus aerial
python3 tools/make-header.py assets/img/your.jpg    # or your own photograph
```

Any photograph wider than it is tall works; the crop is centred. The grade is what makes it read as
part of this site rather than a stock picture dropped into it — an ungraded photo looks pasted on,
however well it is darkened.

The CSS scrim over the banner is deliberately light, because most of the darkening is baked into
the picture. **Change one and re-measure the other:**

```sh
python3 -m http.server 8990    # in one shell
python3 tools/check-contrast.py
```

That samples the rendered page: for every line in the banner it averages the pixels actually behind
it and reports the contrast ratio against the WCAG floors. It is the only honest way to check text
on a photograph, because the answer depends on the picture, the scrim and where the words land —
none of which a stylesheet can tell you. It dismisses the contact panel first; measuring through
that white card once made a perfectly legible headline appear to fail at 2.3:1.

## Bringing in a new design from the Claude artifact

The design lives as a Claude artifact: one self-contained HTML file with every
photograph and the campus video embedded as base64. It is still a **one page** design,
so the sync deliberately no longer writes `index.html` — if it did, it would flatten
the site back into a single scroll every time it ran.

```sh
python3 tools/sync-from-artifact.py path/to/artifact.html
python3 tools/build-site.py
```

The sync takes the design system and the media — `assets/css/cirs.css`,
`assets/js/cirs.js`, `assets/img/`, `assets/video/` — and writes the artifact's markup
to `tools/artifact-reference.html`, which is neither served nor built. When the
artifact gains a section, diff it against that reference file, move the new markup into
the right `tools/pages/*.html`, and rebuild. That hand step is deliberate: only a
person can say which of ten pages a new section belongs on.

Each embedded photograph is named from `tools/media.tsv`, keyed by the md5 of its
bytes, so a photograph keeps its filename across artifact versions. A digest the table
does not know about stops the sync with the digest to add — so nothing ever lands in
`assets/img/` as `image-7.jpg`.

The sync also reapplies one small correction the artifact does not carry: an explicit
`type="button"` on the two `<button>` elements, which the accessibility pass asks for.
That belongs upstream in the artifact eventually. Keep that step tiny — anything larger
than an attribute should be fixed in the design, not patched on the way out of it.

## Deploying to Netlify

The site is on Netlify as **preeminent-alfajores-71115e**, at
<https://preeminent-alfajores-71115e.netlify.app>.

`netlify.toml` points Netlify at `_site/`, not at the repository root. The root holds the generated
pages next to the scripts that build them, so publishing it would ship `tools/`, `.github/` and
`node_modules` alongside the site. `tools/stage-deploy.py` copies just the publishable files —
the eleven pages, `assets/` minus the parked editor's sources, and the two files that keep a review
preview out of search results — into `_site/`, which is generated and git-ignored.

```sh
python3 tools/build-site.py
python3 tools/stage-deploy.py
```

Netlify runs both as its build command, so a deploy from a clean checkout stages itself.

**Visitor access.** The team had `requireSSOTeamLogin` set on *all* projects, which is why the
first shared link returned 401 and bounced to a Netlify login. It is now off for this project, so
the URL opens for anyone. Turn it back on in Netlify → Site configuration → Access & security when
the review is over.

**`_headers` and `robots.txt` are review-preview files.** They set `X-Robots-Tag: noindex` and
disallow crawling, because the pages still carry bracketed placeholders and an under-construction
note that should not be indexed under the school's name. `tools/stage-deploy.py` writes them;
delete that step for the real launch.

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
Upload all ten `.html` files and the `assets` folder into `public_html`, keeping them in
the same directory — the pages link to each other by plain filename, so the structure has
to stay flat. That's it.

## Check it locally first

From inside the unzipped folder:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`. Opening `index.html` by double-clicking works too, and the
links between pages still resolve, but a local server matches how it will behave once hosted.

## Just need to show someone quickly

There used to be a `dist/cirs-home.html` here — the whole site inlined into one file to
email or open from a USB stick. That worked while the site was one page. It cannot
carry ten, because its menu links would all point at pages that are not in the file, so
it has been removed rather than left to mislead. Send the Netlify preview link, or a
zip of `index.html`, the other nine pages and `assets/`.

## The content editor — parked

There was a `cirs-editor.html`: the whole site in one file, wrapped in a point-and-click editor —
click any headline or paragraph and type, click any photo to replace it, then download a complete
updated site. It worked, and it is not gone. It is simply not built or committed at the moment,
because it was 11 MB of base64 rewritten into the repository on every content change and nobody is
using it yet.

To bring it back for a session:

```sh
python3 tools/build-bundles.py --editor    # writes cirs-editor.html
```

Then double-click the file — no install, no login, no internet connection needed. Its sources,
`assets/css/editor.css` and `assets/js/editor.js`, are still in the repository and still maintained
alongside the markup, so the rebuild is current rather than a fossil.

Do not commit the result. If the editor comes back for good, add it to the bundle-freshness check
in `.github/workflows/ci.yml` at the same time — a committed bundle nobody checks drifts out of
step with the site in silence, which is exactly the failure that check exists to prevent.

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
- **News, on an ongoing basis.** `tools/pages/news.html` currently carries the six reports and
  the diary taken from new.cirschool.org. It is a hand-edited page: add an `<article class="newsitem">`
  to the grid for each new report, or replace the `.newslead` for a big one, then rebuild. Nothing
  fetches from that site automatically, so this page goes stale unless someone updates it.
- **Admissions material still to come**: the fee structure PDF for 2027–2029 (the old site linked
  one; it has not been re-published here), the application timeline, the interview format and how
  offers are communicated, and photographs for the six slots on the Admissions page plus three
  testimonials. Every one of those is a bracketed placeholder on the page today.
- **The header animation for the Admissions banner** — a photograph or a short looping video. The
  banner currently renders a labelled placeholder rather than a stand-in picture, deliberately: a
  temporary photograph on an admissions banner is the kind of thing that quietly ships.
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
