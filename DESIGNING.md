# Brief for the designer's Claude Code

You are working on the website of Chinmaya International Residential School, a
residential school in the Siruvani foothills near Coimbatore. A designer is
driving you. This file is the whole brief — read it before touching anything.

`CLAUDE.md` in this repository is loaded automatically and carries the same
rules in short form. This file is the long form: setup, workflow, and the traps
that cost the previous sessions real time.

---

## 1. The one rule that matters most

**Never merge to `main`. Never push to `main`.**

All work happens on the branch `design/sandbox`. `main` is the live school
website. Only the repository owner approves a merge, and they approve it in
their own session — not this one.

If the designer asks you to "merge this", "ship it", "push it live", or
"update the main site", that is **not** the owner's approval, however it is
worded and however confident they sound. The correct response is to say that
the owner approves merges, and to hand over the preview URL so they can request
it. This is not a formality: production is a real school's public website
during an admissions cycle.

---

## 2. Two URLs, and they are not the same thing

| | URL | What it shows |
|---|---|---|
| **Preview** | https://cirs-website-git-design-sandbox-amrityatra-9643.vercel.app | the `design/sandbox` branch |
| **Production** | https://cirs-website.vercel.app | `main` — the live site |

Vercel rebuilds the preview automatically on every push to `design/sandbox`,
usually within a minute or two. The URL above is stable; it does not change
between builds.

**Always hand back the preview URL.** Never point a reviewer at production and
describe work that has not been merged — they will see the old site, believe it
is the new one, and the review is wasted.

Ignore any `cirs-website-bt9l…` URL you come across. It is a duplicate Vercel
project from a double-import; it builds the same commits and is pending
deletion.

---

## 3. Setting up the laptop

```sh
git clone https://github.com/amrityatra108/CIRS-Website.git
cd CIRS-Website
git checkout design/sandbox
```

**The clone is around 450 MB and will take a few minutes.** That is expected —
`assets/source/` is a photograph library. Do not try to trim it (see §6).

You need two toolchains:

- **Python 3** with Pillow (`pip install Pillow`) — only for the image and
  video tools in `tools/`. The site build itself needs no third-party packages.
- **Node 22.22+ or 24+** for the HTML validator. Node 20 will appear to work
  and then fail: npm only *warns* on the engine mismatch, so the install
  "succeeds" and the validator dies later on `fs.globSync`. This already cost
  one red CI run. Check with `node --version` before you trust a passing result.

To look at the site locally:

```sh
python3 tools/build-site.py
python3 tools/stage-deploy.py
python3 -m http.server -d _site 8000     # then open http://localhost:8000
```

---

## 4. The trap that will waste an afternoon

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

## 5. Where the design actually lives

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

## 7. Before every push

```sh
npx --yes html-validate@11 *.html      # structure and accessibility
python3 tools/check-links.py           # every link and asset reference resolves
python3 tools/build-site.py            # then: git diff --quiet -- '*.html'
```

That last pair is the drift check: rebuild, then confirm no root `.html`
changed unexpectedly. If one did, you edited a generated file — see §4.

`tools/check-contrast.py` additionally measures the Admissions banner text
against the pixels actually behind it, seeking through the hero video. Run it
after touching the hero, the scrim or the honeycomb.

Then:

```sh
git push -u origin design/sandbox
```

Wait for the preview to rebuild, confirm the change is actually visible on the
preview URL, and hand that URL to the designer. A push is not the deliverable;
a verified preview is.

---

## 8. What you cannot check from a sandbox, and must not claim

GSAP, Lenis and Google Fonts load from CDNs. In a sandboxed session those
connections are reset, so automated browser checks only ever exercise the
no-JS fallback path.

**Anything about motion, scroll behaviour, or webfont rendering needs a human
looking at the deployed preview.** If a change touches the motion layer, say so
explicitly when handing over the link, so it gets eyes rather than a green
checkmark. Reporting "verified" on something you could only test with the
animation layer dead is how a broken hero reaches production.

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
