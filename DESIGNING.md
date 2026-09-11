# Brief for the designer's Claude Code

You are working on the website of Chinmaya International Residential School, a
residential school in the Siruvani foothills near Coimbatore. A designer is
driving you. This file is the whole brief — read it before touching anything.

`CLAUDE.md` is loaded automatically and carries the same rules in short form.
This file is the long form: setup, workflow, and the traps that have cost
previous sessions real time.

---

## 1. You are editing the live website

Work happens on `main`. **`main` is what the public sees.** Vercel rebuilds and
deploys on every push, so a push is a publication — there is no preview step
between you and a prospective parent reading the Admissions page.

The site: **https://cirs-website.vercel.app**

Two consequences, and neither is optional:

- **Run the checks in §7 before every push, without exception.** They are the
  only gate that happens *before* the public sees the change. The GitHub CI
  check runs after the deploy, not before it, so a green tick there confirms a
  mistake that is already live.
- **Look at the page after you push.** Load the URL above, confirm the change
  is what you intended, and say so. A push is not the deliverable; a verified
  live page is.

If a change is large, risky, or you are unsure, say so before pushing rather
than after. The owner would far rather answer a question than roll back the
school's public site during an admissions cycle.

---

## 2. Setting up the laptop

```sh
git clone https://github.com/amrityatra108/CIRS-Website.git
cd CIRS-Website
```

You will be on `main` already. That is the working branch.

**The clone is around 450 MB and will take a few minutes.** That is expected —
`assets/source/` is a photograph library. Do not try to trim it (see §6).

You need two toolchains:

- **Python 3** with Pillow (`pip install Pillow`) — only for the image and
  video tools in `tools/`. The site build itself needs no third-party packages.
- **Node 22.22+ or 24+** for the HTML validator. Node 20 will appear to work
  and then fail: npm only *warns* on the engine mismatch, so the install
  "succeeds" and the validator dies later on `fs.globSync`. This already cost
  one red CI run. Check `node --version` before you trust a passing result.

To look at the site locally — always do this before pushing:

```sh
python3 tools/build-site.py
python3 tools/stage-deploy.py
python3 -m http.server -d _site 8000     # then open http://localhost:8000
```

---

## 3. The trap that will waste an afternoon

**Every `.html` file in the repository root is generated.** Editing
`index.html` or `admissions.html` by hand looks like it works, survives a
refresh, and is then silently erased by the next build — and CI fails on the
drift.

The real sources are:

- `tools/partials/` — the head, header, menu and footer every page shares
- `tools/pages/<slug>.html` — the body of one page
- `tools/build-site.py` — the `PAGES` manifest: titles, menu labels, banner copy

The site was one long page until the menu became redundant; it is now eleven
pages. The menu is generated from that manifest, so adding a page there puts it
in the menu of all eleven at once. A menu edited in eleven files is a menu that
goes stale in ten of them — hence the partials.

Edit the source, run the build, commit both the source and the regenerated
`.html`.

---

## 4. Where the design actually lives

Most visual change needs no markup at all.

- **`assets/css/cirs.css`** — the design system. The tokens sit at the top of
  the file: palette, type scale, spacing steps, measure. **Change the token,
  not the fifty places that use it.**
- **`assets/css/pages.css`** — per-page components: header tabs, page hero,
  jump menu, tables, the news list.

The identity is deep purple, gold, dark red, black and white. **Red text on
purple was deliberately removed and replaced with gold** because it was
illegible; do not reintroduce it. The spacing scale (`--space-1` … `--space-10`)
exists so new components are built on the same steps rather than one-off pixel
values — please keep to it.

Type: EB Garamond for display, Schibsted Grotesk for interface and running
text, Tiro Devanagari Hindi for the motto.

**Changing a stylesheet or a hero asset? Bump `CACHE_BUST` in
`tools/build-site.py`.** Returning visitors hold the old file otherwise, and
the change appears not to have worked.

---

## 5. The Admissions hero

`tools/make-honeycomb.py` builds the hexagon wall and its looping video from a
**curated** list, `CELLS`, near the top of the file — not from whatever happens
to be in `assets/source/`. A cell is a 460px hexagon graded to near-monochrome
with headings over it, which punishes a crowded frame: an overhead crush of
students reads as grey mush at that size however good it looks full-bleed.

Add or remove names in `CELLS` and re-run the tool. A name that is not in
`assets/source/` fails loudly rather than silently changing the hero.

The tools honour EXIF rotation — several camera originals carry orientation 8
and would otherwise tile on their side. Keep it that way.

**After touching the hero, the scrim or the honeycomb, run
`tools/check-contrast.py`.** It measures the banner text against the pixels
actually behind it, seeking through the video loop.

---

## 6. Deliberate, not oversights

Three things look like mistakes and are not. Previous sessions have tried to
"fix" all three.

- **`assets/source/` is a 171 MB photograph library that is never deployed.**
  `tools/stage-deploy.py` copies only the assets a page actually references —
  that rule is what keeps the deploy at 7.6 MB instead of 153 MB. Do not move
  these into `assets/img`; that breaks the orphan check in `check-links.py`.
  To use one, derive a cropped and sized image into `assets/img` and reference
  it from a page.
- **Bracketed placeholder copy is waiting on the school.** Do not fill a
  placeholder with invented content, and **especially never invent a
  testimonial.** A plausible fabricated quote attributed to a real school's
  parents is worse than an obvious gap.
- **`netlify.toml` and `vercel.json` both exist** during the move to Vercel and
  must be changed together until Netlify is retired. See `HOSTING.md`.

---

## 7. Before every push — the only gate there is

```sh
npx --yes html-validate@11 *.html      # structure and accessibility
python3 tools/check-links.py           # every link and asset reference resolves
python3 tools/build-site.py            # then: git diff --quiet -- '*.html'
```

That last pair is the drift check: rebuild, then confirm no root `.html`
changed unexpectedly. If one did, you edited a generated file — see §3.

Then push, and **check the live page afterwards**:

```sh
git push -u origin main
```

---

## 8. What you cannot check, and must not claim

GSAP, Lenis and Google Fonts load from CDNs. In a sandboxed session those
connections are reset, so automated browser checks only ever exercise the
no-JS fallback path.

**Anything about motion, scroll behaviour, or webfont rendering needs a human
looking at the real site.** If a change touches the motion layer, say so
explicitly rather than reporting it verified. Claiming "verified" on something
you could only test with the animation layer dead is how a broken hero reaches
a prospective parent.

Measurement beats eyeballing everywhere else, though, and the repository has
form here: a contrast checker once reported 2.32:1 on legible text because it
was averaging a popup's white card as "background". The tell was that
strengthening the scrim moved the number to 2.35 and no further. **If a fix
does not move the number, the diagnosis is wrong — do not push harder on it.**

---

## 9. Open questions the owner has already flagged

Do not resolve these unilaterally; they are the owner's calls.

- Primary buttons are white-on-gold at **1.61:1**, below the 4.5:1 minimum.
  Dark purple text on the same gold gives 12.15:1. Undecided.
- A rewritten "CIRS is a family" passage is drafted but not yet placed on the
  Why CIRS page.
