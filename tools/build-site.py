#!/usr/bin/env python3
"""Assemble every page of the site from shared partials and per-page content.

The site used to be one long page. It is now ten, which means the header, the
menu and the footer appear ten times — and a menu that has to be edited in ten
files is a menu that goes stale in nine of them. So no page is authored as a
whole file. Each page is:

    tools/partials/       the chrome every page shares
    tools/pages/<slug>.html   only the sections unique to that page
    PAGES below           title, menu label, banner copy, grouping

and this script writes <slug>.html at the repository root. Edit those inputs,
never the generated pages — a rebuild overwrites them, and CI fails if what is
committed does not match what a rebuild produces.

The menu is generated from PAGES, so adding a page here puts it in the menu of
all ten pages at once. Cross-page links are rewritten from the section anchors
the original single page used: SECTION_PAGE says which page each section now
lives on, and a link to a section on the current page stays a plain #anchor
rather than reloading the page you are already reading.

    python3 tools/build-site.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_BUST = "b=6"

# slug -> page definition. Order here is the order in the menu.
#   nav    the label in the menu and the <title>
#   group  the menu column it sits under
#   eyebrow/heading/lead  the banner at the top of the page
#   uc     False to leave off the under-construction note. Nothing sets
#          it: the note belongs at the foot of every page, the home page
#          included, because every page is still being filled in
PAGES = {
    "index": {
        "nav": "Home",
        "group": None,
        "title": "Chinmaya International Residential School — Siruvani, Coimbatore",
        "description": "A co-educational residential school on a hundred acres in the Siruvani "
                       "foothills — CBSE and the International Baccalaureate, Grades V to XII.",
        "banner": None,
    },
    "news": {
        "nav": "News",
        "group": "News",
        "title": "News",
        "description": "News and events from Chinmaya International Residential School — "
                       "assemblies, weeks, competitions and the term's diary.",
        "banner": ("News", "From <em>the Campus.</em>",
                   "Reports from the departments and the houses, and the dates already in the "
                   "school calendar."),
    },
    "why-cirs": {
        "nav": "Why CIRS",
        "group": "About CIRS",
        "title": "Why CIRS",
        "description": "Who we are, what the school is recognised for, and the Junior and Senior "
                       "Schools that carry it.",
        "banner": ("About CIRS", "Why <em>CIRS.</em>",
                   "A community of knowledge, service and skill in the Siruvani foothills — and "
                   "the two schools, Junior and Senior, that carry it."),
    },
    "our-leaders-speak": {
        "nav": "Our Leaders Speak",
        "group": "About CIRS",
        "title": "Our Leaders Speak",
        "description": "A message from the Principal of Chinmaya International Residential School.",
        "banner": ("Our leaders speak", "In Their <em>Own Words.</em>",
                   "A message from the Principal."),
    },
    "our-leadership": {
        "nav": "Our Leadership",
        "group": "About CIRS",
        "title": "Our Leadership",
        "description": "The Board of Directors of Chinmaya International Residential School, and "
                       "the staff and faculty.",
        "banner": ("Governance", "Our <em>Leadership.</em>",
                   "CIRS is an undertaking of the Central Chinmaya Mission Trust, Mumbai, and is "
                   "managed by its Board of Directors."),
    },
    "academics": {
        "nav": "Academics",
        "group": "Academics",
        "title": "Academics",
        "description": "Two curricula under one roof — CBSE from Grade V, and the International "
                       "Baccalaureate Diploma in Grades XI and XII.",
        "banner": ("Academics", "Two Curricula, <em>One Campus.</em>",
                   "CBSE from Grade V, and the International Baccalaureate Diploma in the final "
                   "two years."),
    },
    "student-life": {
        "nav": "Student Life",
        "group": "Student Life",
        "title": "Student Life",
        "description": "Residential life at CIRS, the shape of an ordinary school day, and the "
                       "hundred-acre campus it happens on.",
        "banner": ("Student life", "Live, Learn, <em>Belong.</em>",
                   "The boarding houses, the shape of an ordinary day, and the campus the whole "
                   "of it happens on."),
    },
    "sports": {
        "nav": "Sports",
        "group": "Student Life",
        "title": "Sports",
        "description": "Athletics, the playing fields and the sporting record at CIRS.",
        "banner": ("Sports", "Sport, Every Day <em>at Four.</em>",
                   "The four o'clock hour, the fields it happens on, and what the teams have won."),
    },
    "arts": {
        "nav": "Arts, Music & Theatre",
        "group": "Student Life",
        "title": "Arts, Music & Theatre",
        "description": "Music, theatre and the visual arts at Chinmaya International Residential "
                       "School.",
        "banner": ("Arts", "Express, Perform, <em>Create.</em>",
                   "Music, theatre and the visual arts, and the amphitheatre built into the "
                   "slope."),
    },
    "admissions": {
        "nav": "Admissions",
        "group": "Admissions",
        "title": "Admissions",
        "description": "How to apply to Chinmaya International Residential School — registration "
                       "for 2027–2028, the entrance examination, visiting, and fees.",
        # A hero rather than the flat band: this is the page that has to
        # persuade, not merely inform.
        "hero": ("Admissions 2027–2028", "How to <em>Apply.</em>",
                 "Registration is open. The entrance examination, a visit to the school, and the "
                 "offer — the whole procedure, in order."),
        "hero_placeholder": "Header animation &mdash; admissions<br>photograph or looping video<br>to be supplied",
        "jump": True,
    },
    "alumni": {
        "nav": "Alumni",
        "group": "Admissions",
        "title": "Alumni",
        "description": "Where CIRS students go after school — universities in India and abroad.",
        "banner": ("After CIRS", "Where They <em>Go Next.</em>",
                   "The universities our students read at, in India and abroad."),
    },
}

# Which page each of the old single-page section anchors now lives on.
SECTION_PAGE = {
    "about": "why-cirs", "junior": "why-cirs", "senior": "why-cirs",
    "quote": "our-leaders-speak",
    "people": "our-leadership",
    "academics": "academics",
    "life": "student-life", "day": "student-life", "campus": "student-life",
    "athletics": "sports", "fields": "sports", "achievements": "sports",
    "arts": "arts",
    "pathways": "alumni",
    "latest": "news", "diary": "news",
    "admissions": "admissions", "apply": "admissions", "examination": "admissions",
    "visit": "admissions", "before": "admissions", "fees": "admissions",
    "voices": "admissions", "gallery": "admissions", "contact": "admissions",
    "top": "index", "main": None,   # main is on every page; top only on home
}


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        sys.exit(f"build-site: missing {rel}")
    return open(path, encoding="utf-8").read()


def rewrite_links(html, slug):
    """Turn the old single-page #anchors into links that work across pages."""
    def swap(m):
        anchor = m.group(1)
        if anchor not in SECTION_PAGE:
            return m.group(0)          # href="#" placeholders, and #main
        target = SECTION_PAGE[anchor]
        if target is None:
            return m.group(0)
        if target == slug:
            # Already on this page. An anchor equal to the slug is the old
            # single page's name for the whole section, which is now the page
            # itself — so it means the top, not a section that no longer exists.
            return 'href="#top"' if anchor == slug else m.group(0)
        page = "index.html" if target == "index" else f"{target}.html"
        # A link to #admissions means the Admissions page, not a section on it.
        # The old single page had a section per page; now the page IS the
        # section, so an anchor equal to the slug becomes a plain page link.
        if target == "index" or anchor == target:
            return f'href="{page}"'
        return f'href="{page}#{anchor}"'
    return re.sub(r'href="#([A-Za-z0-9_-]+)"', swap, html)


def nav_html(slug):
    groups = {}
    for s, p in PAGES.items():
        if p["group"]:
            groups.setdefault(p["group"], []).append((s, p))
    out = ['<nav class="drawer__grid" aria-label="All pages">']
    for group, items in groups.items():
        gid = "dnav-" + re.sub(r"[^a-z]+", "-", group.lower()).strip("-")
        out.append("    <div>")
        out.append(f'      <p class="sc" id="{gid}">{group}</p>')
        out.append(f'      <ul aria-labelledby="{gid}">')
        for s, p in items:
            here = ' aria-current="page"' if s == slug else ""
            out.append(f'        <li><a href="{s}.html"{here}>{p["nav"]}</a></li>')
        out.append("      </ul>")
        out.append("    </div>")
    out.append("  </nav>")
    return "\n".join(out)


def banner_html(page):
    eyebrow, heading, lead = page["banner"]
    return f'''<section class="pagehead on-purple" id="top" data-ground="#1E1626">
  <div class="wrap pagehead__inner">
    <p class="marker"><span class="sc">{eyebrow}</span></p>
    <h1 class="serif" data-split>{heading}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>'''


HOME_TAB = '''<a class="htab" href="index.html">
        <span class="htab__icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2.6 7.6 9 2.2l6.4 5.4M4.4 9.2v6.2h9.2V9.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="htab__label">Home</span>
      </a>'''


def hero_html(page):
    """The home page's opening in miniature, for a page that must persuade.

    The media slot deliberately carries a labelled placeholder rather than a
    stand-in photograph: a temporary picture on an admissions banner is the
    kind of thing that quietly ships.
    """
    eyebrow, heading, lead = page["hero"]
    return f'''<section class="pagehero" id="top" data-ground="#0E0B12">
  <div class="pagehero__media">
    <div class="pagehero__ph"><span>{page["hero_placeholder"]}</span></div>
  </div>
  <div class="pagehero__mono" aria-hidden="true"></div>
  <div class="pagehero__scrim" aria-hidden="true"></div>
  <div class="wrap pagehero__inner">
    <p class="marker"><span class="sc">{eyebrow}</span></p>
    <h1 class="serif" data-split>{heading}</h1>
    <p class="lead">{lead}</p>
    <p class="pagehero__cta">
      <a class="btn btn--primary btn--lg" href="https://easycollege.in/cirs/school/application/index.aspx">Register online</a>
      <a class="btn btn--ghost btn--lg" href="#apply">How to apply</a>
    </p>
  </div>
</section>'''


def jump_html(body):
    """Build the right-hand index from the page's own sections.

    Labels come from each section's small-caps marker, so the index cannot
    drift out of step with the headings — there is nothing to keep in sync.
    """
    items = []
    for m in re.finditer(r'<section[^>]*\bid="([^"]+)"[^>]*>(.*?)</section>', body, re.S):
        sid, inner = m.group(1), m.group(2)
        label = re.search(r'<span class="sc">(.*?)</span>', inner, re.S)
        if label:
            items.append((sid, re.sub(r"\s+", " ", label.group(1)).strip()))
    if not items:
        return ""
    links = "\n".join(f'      <a href="#{i}">{t}</a>' for i, t in items)
    return f'''<nav class="jump" aria-label="On this page">
  <div class="jump__panel" id="jumpPanel">
      <p>On this page</p>
{links}
  </div>
  <button type="button" class="jump__toggle" aria-expanded="false" aria-controls="jumpPanel">
    <svg width="14" height="12" viewBox="0 0 14 12" fill="none" aria-hidden="true"><path d="M1 1h12M1 6h12M1 11h7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    <span>On this page</span>
  </button>
</nav>'''


UC = '''<section class="uc">
  <div class="wrap uc__inner">
    <span class="uc__mark" aria-hidden="true">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 4.5v4M8 11.2h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="8" r="6.6" stroke="currentColor" stroke-width="1.2"/></svg>
    </span>
    <div>
      <p class="uc__label">Under construction</p>
      <p class="uc__text">This page is still being written. Photographs, names and figures marked
        in brackets are placeholders awaiting the school, and more will be added here in the weeks
        ahead. <a href="mailto:info@cirschool.org">Tell us what is missing.</a></p>
    </div>
  </div>
</section>'''


def build(slug, page):
    head = read("tools/partials/head.html")
    head = (head.replace("{{TITLE}}", page["title"])
                .replace("{{DESCRIPTION}}", page["description"])
                .replace("{{CANONICAL}}", "" if slug == "index" else f"{slug}.html")
                .replace("{{CACHE_BUST}}", CACHE_BUST))

    parts = [head, "<body>", read("tools/partials/chrome.html").rstrip("\n")]
    drawer = read("tools/partials/drawer.html").replace("{{NAV}}", nav_html(slug))
    # The home page needs no Home tab — the wordmark already leads here, and a
    # Home link on Home is a link to nowhere.
    header = read("tools/partials/header.html").replace(
        "{{HOME_TAB}}", "" if slug == "index" else HOME_TAB)
    parts += [header.rstrip("\n"), drawer.rstrip("\n")]
    parts.append('<main id="main">')
    if page.get("hero"):
        parts.append(hero_html(page))
    elif page.get("banner"):
        parts.append(banner_html(page))
    content = read(f"tools/pages/{slug}.html").rstrip("\n")
    parts.append(content)
    if page.get("jump"):
        parts.append(jump_html(content))
    if page.get("uc", True):
        parts.append(UC)
    parts.append("</main>")
    parts.append(read("tools/partials/footer.html").rstrip("\n"))
    parts.append(read("tools/partials/scripts.html").replace("{{CACHE_BUST}}", CACHE_BUST).rstrip("\n"))
    parts += ["</body>", "</html>", ""]

    return rewrite_links("\n".join(parts), slug)


if __name__ == "__main__":
    for slug, page in PAGES.items():
        out = os.path.join(ROOT, f"{slug}.html")
        html = build(slug, page)
        open(out, "w", encoding="utf-8").write(html)
        print(f"  write  {slug}.html ({len(html):,} chars)")
