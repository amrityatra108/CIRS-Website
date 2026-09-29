# Working on this repository

## The workflow the owner expects

This is the workflow for work the **owner** drives. Design sessions are the one
exception and are covered in the next section.

For every change, in this order:

1. **Do the work on a branch of its own**, named for the change, never directly on `main`.
2. **Run the checks** — see below. Do not offer work that has not passed them.
3. **Ask before merging to `main`.** The owner confirms each merge; do not merge unprompted.
4. **After merging, deploy and hand back a Vercel link** they can share for review.

Steps 3 and 4 are the parts most easily forgotten. A change that is committed but not merged,
or merged but not deployed, is not finished from the owner's point of view.

There is no standing branch to work on, and there should not be one. There was, and it went
stale: it sat hundreds of commits behind `main` while the work carried on around it, and it
still held personal data that `main` had deliberately withdrawn. A branch that outlives the
change it was made for stops being a workspace and becomes a second, older copy of the site —
one that looks mergeable and is not. Branch for the change, merge it, let it go.

## Design sessions

A designer drives design work through this same Claude account, **directly on
`main`**. The owner chose that deliberately, over a sandbox branch.

That means every push is a publication: Vercel deploys on push, and the GitHub
CI check runs *after* the deploy, not before it. The checks below are the only
gate that happens before the public sees a change, so run them every time, and
load https://cirs-website.vercel.app afterwards to confirm the change is what
was intended.

Say so before pushing, not after, when a change is large or you are unsure.
`DESIGNING.md` is the designer's full brief — keep it accurate if the workflow
changes.

## The pages are generated

Every `.html` file at the repository root is built by `tools/build-site.py` from
`tools/partials/` and `tools/pages/<slug>.html`. **Editing a root `.html` by hand looks like it
works and is silently undone by the next build**, and CI fails on the drift. Edit the sources.

The menu is generated from the page list in `tools/build-site.py`, so adding a page there puts
it in the menu of every page at once. The header, menu and Enquire sheet are drawn by
`assets/css/drawer.css`. The shared controller in `assets/js/cirs.js` keeps the approved controls
clear, with no bar, over full-screen openings and gathers them into a compact translucent pill
on the first scroll; pages without a full-screen opening start on the pill (`header_start` in
`tools/build-site.py`). Page sheets should not restyle or hide the shared header.

Arts, Music & Theatre is the one page that is not a document. It is a full-window field of
photographs — `"wall": True` in that page list — so it wears the header but no footer, no
banner and no scroll. Its photographs are listed in `tools/artswall.py` and cut by
`tools/make-arts-wall.py`; its sheet and script are `assets/css/artswall.css` and
`assets/js/artswall.js`, both scoped to `body.wall`.

CIRS Theatre is written as a performance: the scrubbed opening film, a handoff onto the ivory
Prologue, the Programme, then Act I Anand Utsav, an intermission, Act II Masquerades (a four-house
playbill, finite house galleries and a photograph viewer) and Act III Class Presentations, and
finally the archive request and the way onward. Everything but the archive request is written
from `tools/theatre.py`, which records every photograph's Drive source, house, year and caption
and every YouTube link (the markup functions sit below its data; never copy those arrays into
the script). `tools/make-theatre.py` cuts the images into `assets/img/theatre/` from the
school's Drive (the originals are not in the repository). A photograph is attributed to a house
only by its Drive folder and the school's own YouTube titles, never by costume colour. The sheet
and script are `assets/css/theatre.css` and `assets/js/theatre.js` (all scoped to `body.theatre`;
one scroll owner, no second Lenis). The film itself is the shared one, and the handoff runs
inside its own sticky stage; its phase fractions in `tools/build-site.py` keep the original
timing. On this page `<body>` carries the class `film`, so the film's `.film{height:…}` sizes the
body too: never give the body `overflow:hidden` here (it clips the whole page to the film's
height); lock scroll on `html`.

The Founder page opens on the designer's Gurudev handoff: a four-second film
(`assets/video/gurudev-intro.mp4`, phone cut by `tools/make-films.py`), then a WebGL portrait of
two GLB busts — the young Balakrishna Menon first, the older Gurudev showing through a trail
that follows the pointer, with paired swirls after two idle seconds — and an opt-in sound that
follows cursor speed. `assets/js/founder-opening.js`, `founder-portrait.js` and
`founder-liquid-sound.js`, styled by `assets/css/founder-portrait.css`. The busts are packed in
`assets/models/gurudev-portraits.json` and the recording is
`assets/audio/gurudev-liquid-source.m4a`, both as supplied. The reveal's shader, width, wake,
swirl timing and the sound's settings are the designer's approved values; change them only on
the designer's say. The life story below (`#life`) keeps the site's own copy, which has been
corrected against the Chinmaya archives since the handoff was written — do not revert it to the
handoff's `events.json`.

Math Challenge opens on a sculpture of 216 bevelled blocks that its stage's scroll turns from a
6×6×6 cube into an 18×12 field and then a torus (`assets/js/math-sculpture.js`, Three.js from
`assets/founder-opening/vendor/`). `assets/js/matharena.js` owns the archive filters, the
division links and the stage's one progress value, and imports the sculpture itself, so a failed
graphics load leaves a plain opening with the drawn cube. The drawings are made from the same
numbers by `tools/make-math-sculpture.py` — keep its constants in step with the script's. The
archive is `tools/mathchallenge.py`: the PDFs are the school's winners' bulletins, not problem
papers, and a month lists only the bulletins that exist.

Creative Writing is a student literary journal written from `tools/creative-writing-content.json` by
`tools/creativewriting.py` (page shell `tools/pages/creative-writing.html`, sheet `assets/css/cwriting.css`,
script `assets/js/cwriting.js`). The same generator writes `creative-writing/junior.html`, `senior.html` and one
page per edition. Every edition, poem, excerpt and presentation is data there; a field the school has not
supplied (school level, month, year, title, grade, presentation) is left out, never guessed, and an edition
with no confirmed level stays under All. The hero's line and "Another line" come only from the stored,
build-verified excerpts. The editions are one chronological list in the HTML; on windows at least 1100×620 with
motion and normal contrast, `cwriting.js` lays it out as two opposing waves around a sticky preview through
`gsap.matchMedia` (marks `cw-wave-on` and `cw-split-on` are set on `<html>` in `head_html()` so a reload does not
jump, and torn down again if the script or GSAP is missing). Edition pages are deliberately still: no motion, the
poems in one flow with real `#poem-…` anchors. `cirs.js` scrolls every `href="#…"` itself and leaves no history
entry, so the links between poems carry the page's own address (`…/january-2026.html#poem-…`, see `edition_html`);
the browser then does the navigation, which is what keeps Back and Forward working. Do not turn them back into
bare `#` links. A presentation link exists only for an edition whose `ppt` file is in the repository.

Leadership's people, portrait crops and five messages are data in `tools/leadership.py`;
`tools/make-leadership.py` cuts the portraits. The messages are the school's published text word
for word — do not copy-edit them. The page keeps native scroll (no Lenis) so its `#msg-…` links
are real history entries.

News's "The term in review" (`#term`) and its article pages are written from `tools/cvpnews.py`, which
is written only from the school's CVP report for October 2025 – March 2026 and records every conflict
in that report and how it was settled. `tools/make-news-cvp.py` cuts the photographs from the report's
PDF (not in the repository) into `assets/img/news/cvp/`. Add nothing to those articles that the report
does not say.

Spiritual Life (`tools/pages/spiritual-life.html`) is written from the school's own account,
the "Spiritual Page" Google Doc: every activity, frequency and audience on it comes from there,
grouped under that document's Swadhyaya, Sadhana and Seva. Its extra photographs are cut from
`assets/source/` by `tools/make-spiritual.py`; those carry no record of their occasion, so their
captions describe the frame and never name a practice. Its sheet and script are
`assets/css/spiritual.css` and `assets/js/spiritual.js`.

Curriculum (`tools/pages/curriculum.html`) is the Curriculum Atlas: one gold path from the
opening through the grade journey, dividing at Grade X into CBSE and the IB Diploma. Its facts
come only from `docs/curriculum-content.md`. The markup is complete reading order, and the
CBSE/IB comparison is a real `<table>`. `assets/js/curriculum.js` adds two modes, each built
when its media query holds and removed when it stops: `html.cur-stage` (windows at least
1024×680 with motion) stacks the journey's photographs in one CSS-sticky frame and uncovers the
stage being read — native scroll, nothing pinned by script, no GSAP; `html.cur-motion` gives
the division, the Diploma core and the school-life photographs a once-only entrance. Nothing
moves under reduced motion, and the IB index's current group is marked in every mode.

School History is the CIRS archive, and every date on it is written from `tools/history.py`:
each event carries its source, and anything unconfirmed is a `note` there (never published) or
held back in `UNRESOLVED`. `python3 tools/history.py` prints the report. `tools/make-history.py`
cuts its exhibits into `assets/img/history/` from the school's own PDFs and Drive photographs;
its sheet and script are `assets/css/history.css` and `assets/js/history.js`. Do not add a dated
claim to that page without a source for it, and do not attribute a photograph to an event its
own record does not support.

Our Laurels is the hall of achievement, and everything on it is written from `tools/laurels.py`:
the 56 records, their sources and images, and the evidence-checked sequences built on them
(`FRAGMENTS`, `LEADS`, `COUNTED`, `TUNNEL`, `FEATURES`). `audit()` fails the build if a quoted
figure or label is not in its own record; `python3 tools/laurels.py` prints the report and what
is `HELD` back. The hero count and date range are computed from the data, never typed. The
sheet and script are `assets/css/laurels.css` and `assets/js/laurels.js`, on the site's own GSAP
and Lenis, with no WebGL: `gsap.matchMedia` gives `body.lr-cine` (sticky stages of real DOM in CSS
3D, driven by custom properties) on windows at least 900×560 with motion, a lite document
otherwise, and the plain document under reduced motion or without script — all with the same
content. Do not add a record, figure or photograph without a source, and do not name a student
the record does not name. `tools/make-laurels.py` cuts the Drive season photographs.

## Checks, before every push

```sh
npx --yes html-validate@11 *.html      # structure and accessibility
python3 tools/check-links.py           # every link and asset reference resolves
python3 tools/build-site.py            # then: git diff --quiet -- '*.html'
```

`tools/check-contrast.py` additionally measures banner text against the pixels actually behind
it, seeking through the hero video. It takes the page as an argument and defaults to
Admissions — `news.html` for the other hero, `crossroads.html` for the drifting covers,
`arts.html` for the fold over the photograph wall. Run it after touching any hero, a scrim
or the honeycomb. It needs playwright-core, which is not in the repository: point
`CIRS_BROWSER_DIR` at the directory holding it.

## Things that are deliberate, not oversights

- `assets/source/` holds 150 MB of unedited camera originals. They are **never** deployed —
  `tools/stage-deploy.py` copies only assets a page references. Do not "tidy" them into
  `assets/img`; that would break the orphan check in `check-links.py`.
- Placeholder copy says plainly that it is waiting for the school. Do not replace a bracketed
  placeholder with invented content — particularly not testimonials.
- Colour is a set of roles at the top of `assets/css/cirs.css` (grounds, ink, gold, label,
  campus green, status, focus). Page sheets read those roles; page-local colour tokens are
  aliases of them. Gold `--gold` is never lettering on ivory, and text on a gold fill is
  `--on-gold`, not white. House colours, festival inks, status colours and film seam colours
  are meaning, not decoration, and stay. DESIGNING.md §4 has the detail.
- `netlify.toml` and `vercel.json` both exist during the move to Vercel and must be changed
  together until Netlify is retired. See HOSTING.md.
- Every opening film has a phone cut, `assets/video/<name>-m.mp4`, from `tools/make-films.py`,
  chosen by a media-aware `<source>`. Replace a film and re-run the tool. The scrubbed films are
  all-intra in both cuts; never re-encode one with a longer keyframe interval. Images that
  `tools/make-media.py` derives (Founder textures and layers, Alumni, Blog card sizes) have their
  masters in `assets/source/`, which is why those PNGs are not in `assets/img`.

## What is not verifiable from a sandbox session

**Motion now is.** GSAP, ScrollTrigger and Lenis are served from `assets/vendor/` rather than
from a CDN, so a sandbox session loads them and the reveals, the pinned sections and the smooth
scroll can be checked before a change ships. This used to be the largest blind spot here.

**Type now is, too.** Mona Sans serves English body and interface text. Bodoni Moda,
Literata and EB Garamond serve the display, editorial and quotation roles;
Tiro Devanagari Hindi still serves Devanagari. All current faces are self-hosted in
`assets/fonts/`, so a sandbox session can check real lettering, line lengths and headline
breaks. `tools/make-fonts.py` builds the font assets; see `docs/typography.md` before changing
a face or weight.

The cause, for anyone who meets it again elsewhere: it was never the certificate. The browser
a session drives does not use `$HTTPS_PROXY`, which is what `curl` reads — so the request to
fonts.googleapis.com was never made at all rather than being refused. Anything else loaded
from a third-party origin in a page under test will behave the same way.
