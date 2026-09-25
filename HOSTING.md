# Chinmaya International Residential School — hosting

Everything in this zip is static. No build step, no server-side code, no database.

## What's in here

```
index.html                 the home page
                           and twenty-four more, one file each, in the five menu groups:
  Vision                   founder · why-cirs · school-history · leadership
  Student Life             the-cirs-experience · curriculum · our-results · sports ·
                           our-laurels · math-challenge
  Literary Excellence      crossroads · blog · creative-writing
  Art, Culture & Music     captures · art-attack · festivals · theatre · cultural-gallery
  Connect                  school-info · news · admissions · parent-portal · alumni
important-documents.html   linked from School Information and the footer, not from the menu
assets/css/cirs.css        the design system, imported from the artifact
assets/css/pages.css       the components only a multi-page site needs
assets/css/founder.css     per-page sheets, each scoped to a body class and loaded
assets/css/artswall.css    only by the page that declares it
assets/css/blog.css
assets/js/cirs.js          interaction layer
assets/js/pages.js         behaviour only a multi-page site needs
assets/js/artswall.js      the Cultural Gallery photograph wall
assets/img/                the emblem, photography, favicon, social card
assets/video/              the hero background loop
assets/source/             unedited camera originals; never deployed
docs/design-system.html    the design specification
tools/                     the scripts that generate every page (see below)
tools/make-photos.py       cuts every site photograph from assets/source/
tools/make-header.py       composes the Admissions banner photograph
tools/check-contrast.py    measures banner text against the pixels behind it
tools/stage-deploy.py      copies only the assets a page references, into _site/
.github/workflows/ci.yml   the checks that run on every push and pull request
```

**Every `.html` file at the root is generated. Do not edit them.** A rebuild
overwrites them and CI fails if what is committed does not match a rebuild. Edit these
instead, then run `python3 tools/build-site.py`:

```
tools/pages/<slug>.html     the sections unique to that page
tools/partials/             the header, menu, footer and chrome every page shares
tools/build-site.py         PAGES: titles, menu labels, banner copy, what each page is
                            MENU:  which pages are in the menu, in which group, in what order
```

The site was one long page until the menu became redundant. It is now twenty-five, which
means the header, menu and footer appear twenty-five times — and a menu that has to be
edited in twenty-five files is a menu that goes stale in twenty-four of them. Hence the
partials, and hence the menu being generated from `MENU` in `tools/build-site.py`: add a
slug to a group there and it appears in the menu of all twenty-five at once.

`PAGES` and `MENU` are deliberately separate. `PAGES` says what a page *is* — its title,
its banner, whether it carries a hero, its own stylesheet or an in-preparation note.
`MENU` says only where it sits in the navigation. A page can therefore exist and be
linked to without being in the menu, which is what `important-documents.html` does.

## The checks

Every push and pull request runs three things, all of which you can run yourself:

```sh
npx html-validate *.html          # structure and accessibility, every page
python3 tools/check-links.py      # every link and asset reference resolves
python3 tools/build-site.py       # then: git diff --quiet -- '*.html'
```

The last one is the important one. Editing a generated page by hand looks like it
works and is silently undone by the next build — and the menu, which is on every one of
the twenty-five pages, is exactly what someone would be tempted to fix in one file. So CI
rebuilds and fails if the committed pages differ.

The link check never touches the network. Since the site became many pages the menu *is*
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
person can say which page a new section belongs on.

Each embedded photograph is named from `tools/media.tsv`, keyed by the md5 of its
bytes, so a photograph keeps its filename across artifact versions. A digest the table
does not know about stops the sync with the digest to add — so nothing ever lands in
`assets/img/` as `image-7.jpg`.

The sync also reapplies one small correction the artifact does not carry: an explicit
`type="button"` on the two `<button>` elements, which the accessibility pass asks for.
That belongs upstream in the artifact eventually. Keep that step tiny — anything larger
than an attribute should be fixed in the design, not patched on the way out of it.

## Hosting

The site is moving from Netlify to **Vercel**, and is live there at
<https://cirs-website.vercel.app>, deploying on every push to `main`. Until Netlify is
retired the two configurations are both kept and **must be changed together** — a build
command that drifts between two hosts is discovered only when one of them breaks.

Neither host publishes the repository root. The root holds the twenty-five generated pages
next to the scripts that generate them, so publishing it would ship `tools/`, `.github/`,
`node_modules` and the 150 MB of camera originals in `assets/source/`. Both hosts run:

```sh
python3 tools/build-site.py     # the twenty-five pages
python3 tools/stage-deploy.py   # only what a page references, into _site/
```

and publish `_site/`, which is generated and git-ignored. Before that rule existed, a
copy-everything stage produced a **153 MB deploy of a 6 MB site**.

### Vercel — the new home

`vercel.json` carries the build command, `_site` as the output directory, `cleanUrls` (so
`/admissions` works, as it does on Netlify today) and `X-Robots-Tag: noindex` for as long as
this is a review preview.

To deploy it the first time, either:

- **Vercel dashboard → Add New → Project → import `amrityatra108/CIRS-Website`.** It reads
  `vercel.json`, so leave the framework preset alone and do not override the build command or
  output directory. This needs no CLI and no MCP.
- **Or `npx vercel --prod`** from a checkout, signed in as the owner.

Two things to watch on the first deploy:

- **The build runs Python.** Both images have `python3` and both run this build today. If a
  future image ever fails on a missing interpreter, either commit `_site/` (drop it from
  `.gitignore`) and set `"buildCommand": null`, or add a `package.json` so Vercel selects a
  runtime that includes Python.
- **`_headers` is Netlify's file** and the staging script still writes it into `_site/`. On
  Vercel it is inert — harmless, but `vercel.json` is what sets the headers there.

`.mcp.json` registers Vercel's MCP server at `https://mcp.vercel.com`. It authenticates over
OAuth, which cannot be completed from a non-interactive session — run `/mcp` in an interactive
Claude Code session and authorise it there. It is not needed to deploy.

### Netlify — being retired

Currently live at <https://preeminent-alfajores-71115e.netlify.app>, site id
`3c304db1-b4fa-4caa-ae8a-3590edae7934`.

Note for the record: the team had `requireSSOTeamLogin` set on *all* projects, which is why
the first shared link returned 401 and bounced to a Netlify login. It was turned off for this
project so the review link would open for anyone.

**Once the Vercel deploy is confirmed working, decommission in this order** — the order
matters, because doing it the other way round leaves the school with no site at all:

1. Confirm every page loads on the Vercel URL, and that the honeycomb hero plays.
2. Point any DNS or shared links at Vercel.
3. Delete `netlify.toml`, and remove the `_headers` write from `tools/stage-deploy.py`
   (`robots.txt` stays — it is host-agnostic).
4. Delete the Netlify site, so nobody bookmarks a copy that has stopped being updated.

Leaving a stale Netlify deploy running is the failure mode worth avoiding: two live URLs for
one school, one of them quietly out of date.

### Anywhere else

The site is plain static files, so any host works. Serve the **contents of `_site/`** from the
web root, keeping it flat — the pages link to each other by plain filename.

## Check it locally first

```bash
python3 tools/build-site.py && python3 tools/stage-deploy.py
cd _site && python3 -m http.server 8000
```

Then open `http://localhost:8000`. Opening `index.html` by double-clicking works too, and the
links between pages still resolve, but a local server matches how it will behave once hosted.

## Review previews and search engines

`tools/stage-deploy.py` writes `_headers` and `robots.txt` into `_site/`, and `vercel.json`
sets the same header. They keep the preview out of search results, because the pages still
carry bracketed placeholders and an under-construction note that should not be indexed under
the school's name.

**Remove all three at the real launch**, or the finished site will be invisible to Google.

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
- **Leadership (`leadership.html`) — what the school still has to confirm.** The page was
  redesigned in September 2026 as a portrait gallery. Its people, portraits and all five messages
  are data in `tools/leadership.py`; `tools/make-leadership.py` cuts the photographs. Nothing on
  the page is a placeholder, so everything outstanding is listed here instead.
  - *Roster discrepancy.* The school's own management page (cirschool.org/management.html) lists
    eight people, including **Shri Ram Buxani, Director**, who is on neither this site's current
    roster nor School Information. An older design artifact listed him too. He has **not** been
    added back: confirm whether he is still a Director.
  - *Mahtaney's name.* This site says "Shri Vijay Mahtaney"; the school's management page says
    "Shri. Viju Mahtaney". Confirm the preferred form. There is still no approved photograph of
    him, so his entry is text only, by design.
  - *The Principal's name.* "Smt. G. Rajeshwari" (School Information, owner-confirmed); the
    school site signs her message "Rajeshwari", and the old design artifact called her
    "Rajeshwari Satish". Confirm the form to use everywhere.
  - *Messages now follow the school's published text* (cirschool.org and new.cirschool.org agree
    word for word), with greetings and sign-offs restored. This site previously carried edited
    versions. The one that matters: **the Principal's message had been rewritten**, and the
    rewrite reversed the published physics — it said "the higher the pressure in the eye, the
    calmer it stays … the more violent … the winds", where the published message says "higher
    the pressure in the eye of the storm, lower the intensity of the winds around it". The
    published version is what the page shows; if the rewrite was approved by the Principal,
    say so and it can go back. The Chairman's, Resident Director's and Director — Academics'
    messages had also been copy-edited and had lost their sign-offs. One change is ours: the
    Resident Director's "unsumountable" is set as "insurmountable". Confirm that, and whether the
    school wants the grammar of any message corrected at source (for example "this natural
    phenomena and study", "an yearend examination").
  - *Titles and dates.* The Chairman's and the Resident Director's messages both carry the title
    "Transcending Limitations" on the school site; both are kept. Pujya Guruji's message speaks of
    "making the Chinmaya International Residential School a reality", so it predates the school's
    opening; the page gives no date for any message because none is published.
  - *Introductions still needed:* Swami Anukoolanandaji and Smt. G. Rajeshwari have none. Smt.
    Shanti Krishnamurthy's ("Principal of CIRS from 2009 … Director — Academics and
    Administration since 2018 … a Director of the CCMT Education Cell") came from this site's
    earlier copy; confirm it.
  - *Directors' introductions were trimmed* to what is about CIRS or could be checked: Moorjani
    against cvv.ac.in and citiustech.com; Balachandran's Pravasi Bharatiya Samman; Mahtaney's
    Park Hyatt Chennai against its published history. Removed as dated or unverifiable:
    Mahtaney's "twenty-eight directorships" and present ownership of the hotel; Balachandran's
    "largest individual shareholder of the Bombay Stock Exchange", the MRAMM award and the
    consulate welfare work. cvv.ac.in also calls Moorjani a Trustee of the Central Chinmaya
    Mission Trust — worth adding if the school confirms it.
  - *Photographs.* The best available original of Smt. Shanti Krishnamurthy is a full-length
    shot in which her face is small, so her portrait is only 356 px wide and will look soft on
    high-density screens; a head-and-shoulders photograph would fix it. Swami Swaroopanandaji
    (368 px) and Smt. G. Rajeshwari (484 px) would also benefit. Swami Swaroopanandaji and Pujya
    Guruji Swami Tejomayananda are from chinmayamission.com, Shri Jagdish Moorjani from
    citiustech.com (black and white as published), Shri Siddharth Balachandran from
    buimerccorp.com — downloaded with the owner's approval, originals in
    `assets/source/leadership/`. new.cirschool.org was checked for larger copies; it has none.
  - *Staff and faculty photograph.* The page describes the staff in the school's own words from
    new.cirschool.org/faculty and captions the photograph without a year, because none is known.
    Send the occasion and year if it should be dated; it is not presented as the current roster.
- **The Why CIRS photo is live** — `assets/img/why-cirs.jpg`, cropped from a supplied photo of three
  students to a 4:5 portrait, faces centred.
- **Photography for the sections that still render as a labelled placeholder tile** instead of
  a photograph. Search the built pages for `feature__ph` to find each one. Six sports
  facilities, the classrooms and the laboratories are waiting on a large enough export of the
  school's own photographs.
- **Junior School and Senior School programme detail** — enrolment numbers, leadership names,
  specific outcomes — to replace the two `[Placeholder — …]` paragraphs in those sections.
- **Athletics and Arts specifics** — team names, fixtures, ensembles, and production dates — to
  replace the bracketed placeholder sentences in those two sections.
