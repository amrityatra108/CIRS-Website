#!/usr/bin/env python3
<<<<<<< HEAD
"""The CIRS Blog's front page: a news-stand laid out from the articles.

What the blog publishes is in tools/blogposts.py — seventeen articles taken
whole from The Crossroads. This file only lays them out, in the shape of a
magazine front page: a lead story over two smaller ones, then the sections,
each with its own rule and its own grid.

A card carries what the school asked it to carry — the title, the issue it
was printed in, who wrote it, the section it ran under, and two or three
lines of the article's own opening. The lines are never written here; they
are the article's first sentences, cut at a sentence end by blogposts.py.

Every card also carries a photograph that does not exist yet. Until the
school supplies them, the frame draws itself — see _ph() — so the page keeps
its proportions and check-links.py has no missing file to find.

COMPOSITION lays down the front page slot by slot, drawing from a pool of
articles held in issue order. Each slot names the section it wants; whatever
is left over at the end falls into the closing grid, so adding an article to
blogposts.py can never drop it from the page or print it twice.
"""

import blogposts


def esc(t):
    """Article text is raw prose: its ampersands and quotes mean themselves."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _by(post):
    return post["author"] or "The Crossroads Editorial Board"


def _where(post):
    when = f" &middot; {post['date']}" if post["date"] else ""
    return f"Issue&nbsp;{post['issue']}{when}"


def _ph(post, ratio):
    """The photograph that is not here yet.

    A placeholder rather than a file: the school has not supplied pictures for
    these seventeen articles, and a src pointing at a photograph that does not
    exist would fail check-links.py and print a broken frame on the page. This
    holds the exact space the photograph will take — the ratio is the one its
    slot wants — and says plainly what it is waiting for.

    To give an article its photograph: put the file in assets/img/blog/, add
    "image" to its entry in blogposts.py, and this returns an <img> instead.
    """
    src = post.get("image")
    if src:
        return (f'<div class="nx-shot nx-shot--{ratio}">'
                f'<img src="assets/img/blog/{src}" alt="" loading="lazy"></div>')
    return (f'<div class="nx-shot nx-shot--{ratio} nx-shot--ph" role="img" '
            f'aria-label="Photograph to come">'
            f'<span class="nx-ph__cat">{esc(post["section"])}</span>'
            f'<span class="nx-ph__note">Photograph<br>to come</span></div>')


# ---------------------------------------------------------------- card shapes

def card_overlay(post, ratio="tall", big=False):
    """A · the photograph carries the story, the words sit over its foot."""
    cls = "nx-card nx-card--over" + (" is-big" if big else "")
    return f'''      <article class="{cls} rv">
        <a class="nx-card__link" href="{post["slug"]}.html">
          {_ph(post, ratio)}
          <div class="nx-card__over">
            <span class="nx-chip">{esc(post["section"])}</span>
            <h3 class="nx-card__title">{esc(post["title"])}</h3>
            <p class="nx-card__meta">{esc(_by(post))} &middot; {_where(post)}</p>
          </div>
        </a>
      </article>'''


def card_stacked(post, ratio="wide", small=False):
    """B · the default: photograph, then section, then title, then the line."""
    cls = "nx-card nx-card--stack" + (" is-sm" if small else "")
    return f'''      <article class="{cls} rv">
        <a class="nx-card__link" href="{post["slug"]}.html">
          {_ph(post, ratio)}
          <div class="nx-card__text">
            <p class="nx-cat">{esc(post["section"])}</p>
            <h3 class="nx-card__title">{esc(post["title"])}</h3>
            <p class="nx-card__meta">{esc(_by(post))} &middot; {_where(post)}</p>
          </div>
        </a>
      </article>'''


def card_row(post):
    """C · a square thumb at the left, the words in a column beside it."""
    return f'''      <article class="nx-card nx-card--row rv">
        <a class="nx-card__link" href="{post["slug"]}.html">
          {_ph(post, "sq")}
          <div class="nx-card__text">
            <p class="nx-cat">{esc(post["section"])}</p>
            <h3 class="nx-card__title">{esc(post["title"])}</h3>
            <p class="nx-card__meta">{esc(_by(post))} &middot; {_where(post)}</p>
          </div>
        </a>
      </article>'''


def card_excerpt(post):
    """D · B, and then the article's own opening under the line."""
    return f'''      <article class="nx-card nx-card--stack rv">
        <a class="nx-card__link" href="{post["slug"]}.html">
          {_ph(post, "wide")}
          <div class="nx-card__text">
            <p class="nx-cat">{esc(post["section"])}</p>
            <h3 class="nx-card__title">{esc(post["title"])}</h3>
            <p class="nx-card__meta">{esc(_by(post))} &middot; {_where(post)}</p>
            <p class="nx-card__stand">{esc(post["excerpt"])}</p>
          </div>
        </a>
      </article>'''


def bar(heading, href=None):
    """The rule that opens a section: a red tick, the name, a hairline."""
    more = (f'<a class="nx-bar__more" href="{href}">View all <span aria-hidden="true">&rarr;</span></a>'
            if href else "")
    return f'''      <div class="nx-bar rv">
        <h2 class="nx-bar__name">{esc(heading)}</h2>
        <hr class="nx-bar__rule">
        {more}
      </div>'''


# ------------------------------------------------------------- the front page

# Slot by slot, down the page. Each entry is (kind, heading, section, count).
# "section" is the section to draw from, or None to take whatever is next in
# issue order. A slot that cannot be filled is simply skipped, so the page
# survives an article being withdrawn as well as one being added.
COMPOSITION = [
    ("hero",    None,                  None,            3),
    ("grid3",   "Culture",             "Culture",       3),
    # Top Stories is where the sections too small to carry a grid of their own
    # go, so that naming it does not starve a larger section further down.
    ("lead",    "Top Stories",         ("World", "Campus Life", "Reflection"), 3),
    ("grid2over", "Opinion",           "Opinion",       2),
    ("grid2",   "Sport",               "Sport",         2),
    ("banner",  None,                  None,            0),
    ("duo",     None,                  ("Economics", "The Editorial"), 2),
]


class Pool:
    """The articles, newest issue first, handed out once each."""

    def __init__(self):
        self.left = list(blogposts.by_issue())

    def take(self, n, section=None):
        """n articles: from one section, from each of several, or whatever next.

        A tuple asks for one article from each section it names, in that order,
        which is how a slot gathers up sections too small to stand alone.
        """
        if isinstance(section, tuple):
            got = []
            for name in section:
                got += self.take(1, name)
            return got[:n]
        got = []
        for post in list(self.left):
            if len(got) == n:
                break
            if section is None or post["section"] == section:
                got.append(post)
                self.left.remove(post)
        return got


def front_html():
    """The whole front page below the masthead, in one string."""
    pool = Pool()
    out = []

    for kind, heading, section, n in COMPOSITION:
        if kind == "banner":
            out.append(_banner())
            continue

        if kind == "duo":
            out.append(_duo(pool, section))
            continue

        posts = pool.take(n, section)
        if not posts:
            continue

        if kind == "hero":
            out.append(_hero(posts))
        elif kind == "lead":
            out.append(_lead(heading, posts))
        elif kind == "grid3":
            out.append(_grid(heading, posts, "nx-grid--3",
                             [card_stacked(p) for p in posts]))
        elif kind == "grid2over":
            out.append(_grid(heading, posts, "nx-grid--2",
                             [card_overlay(p, "wide") for p in posts]))
        elif kind == "grid2":
            out.append(_grid(heading, posts, "nx-grid--2",
                             [card_stacked(p) for p in posts]))

    # Whatever the slots did not call for. Never dropped, never repeated.
    rest = pool.take(len(pool.left))
    if rest:
        cls = "nx-grid--3" if len(rest) % 3 == 0 else "nx-grid--2"
        out.append(_grid("From the archive", rest, cls,
                         [card_stacked(p) for p in rest]))

    return "\n".join(out)


def _hero(posts):
    """The lead story, tall, with two more standing beside it."""
    beside = "\n".join(card_row(p) for p in posts[1:])
    return f'''    <section class="nx-hero" aria-label="The latest issue">
      <div class="nx-hero__grid">
{card_overlay(posts[0], "tall", big=True)}
        <div class="nx-hero__side">
{beside}
        </div>
      </div>
    </section>'''


def _lead(heading, posts):
    """A big picture story beside the red panel, then two under them."""
    under = "\n".join(card_stacked(p) for p in posts[1:])
    return f'''    <section class="nx-sec" aria-label="{esc(heading)}">
{bar(heading)}
      <div class="nx-lead">
{card_overlay(posts[0], "wide", big=True)}
        <div class="nx-panel rv">
          <p class="nx-panel__eyebrow">Never miss an issue</p>
          <h3 class="nx-panel__title">The Crossroads, in your inbox</h3>
          <p class="nx-panel__note">Every article here ran first in the school&rsquo;s
            monthly magazine. New issues are posted as they are printed.</p>
          <p class="nx-panel__act"><em>[Placeholder &mdash; the list to subscribe to, to be
            supplied by the Crossroads Editorial Board and the CIRS Social Media Team.]</em></p>
        </div>
      </div>
      <div class="nx-grid nx-grid--2">
{under}
      </div>
    </section>'''


def _grid(heading, posts, cls, cards):
    return f'''    <section class="nx-sec" aria-label="{esc(heading)}">
{bar(heading)}
      <div class="nx-grid {cls}">
{chr(10).join(cards)}
      </div>
    </section>'''


def _duo(pool, sections):
    """Two small sections side by side, each with its own rule and one card."""
    cols = []
    for name in sections:
        got = pool.take(1, name)
        if not got:
            continue
        cols.append(f'''      <div class="nx-duo__col">
{bar(name)}
{card_excerpt(got[0])}
      </div>''')
    if not cols:
        return ""
    return f'''    <section class="nx-sec nx-duo" aria-label="More from the magazine">
{chr(10).join(cols)}
    </section>'''


def _banner():
    """The red band: what the magazine wants from the people reading it."""
    return '''    <section class="nx-cta rv" id="write">
      <div class="nx-cta__shot">
        <img src="assets/img/blog/frag-desk.jpg" alt="Students writing at their desks"
             width="1200" height="800" loading="lazy">
      </div>
      <div class="nx-cta__text">
        <h2 class="nx-cta__title">Write for The Crossroads</h2>
        <p>Everything here began as a piece in the school&rsquo;s monthly magazine. It takes
          writing from any student in the school &mdash; argument, reportage, reflection,
          review &mdash; and what runs in print runs here afterwards.</p>
        <p class="nx-cta__act"><em>[Placeholder &mdash; the editorial board&rsquo;s submission
          address and the deadline for each issue, to be supplied by the Crossroads Editorial
          Board and the CIRS Social Media Team.]</em></p>
      </div>
    </section>'''


def rail_html():
    """The strip of sections under the masthead, biggest section first."""
    counts = {}
    for post in blogposts.POSTS:
        counts[post["section"]] = counts.get(post["section"], 0) + 1
    order = sorted(counts, key=lambda s: (-counts[s], s))
    items = "\n".join(
        f'        <li><span>{esc(s)}</span><b>{counts[s]}</b></li>' for s in order)
    return f'''      <ul class="nx-rail__list">
{items}
      </ul>'''
=======
"""Editorial index and related-story navigation for the CIRS student journal.

The article text and publication metadata live in blogposts.py. This module
only presents that source material and derives counts and reading times from it.
"""

from collections import Counter
from html import escape
from math import ceil

import blogposts


# The earlier PDF lift included several display titles and bylines in article
# paragraphs. These exact fragments were checked against Issues 30, 31 and 32
# before exclusion from reading pages. Issue 17 was corrected at the source.
LAYOUT_ARTIFACTS = {
    "death-of-rationalism": {
        3: ("The Outward Gaze ",),
        8: ("The Of Death Rationalism Rationalism Rationalism Rationalism ",),
    },
    "anakin-skywalker": {
        6: ("Hamartia - The Tyranny of Devotion ",),
        7: ("Aayush S. B. | IB II Yr ",),
        9: ("Anagnorisis - The Ash of ",),
    },
    "sportswashing": {
        4: ("THE TRUTH THE TRUTH A TROPHY Shaurya Bhartia | XII MGMT ",),
    },
    "rumors-at-cirs": {
        3: ("- The Epic Choice ",),
    },
    "hot-wheels-vs-barbie": {
        9: ("Prisha Kantesaria | IB II Year ",),
    },
    "geography-and-geopolitics": {
        7: ("Shaurya Bhartia | 12 Mgmt ",),
    },
}

# Issue 31 prints the end of Rumors alongside a separate article, Itihasa.
# The original text extraction appended that article to the Rumors entry.
ADJACENT_ARTICLE_PARAGRAPHS = {"rumors-at-cirs": {5, 6, 7, 8}}

PRINT_SUBHEADS = {
    "death-of-rationalism": {3: "The Outward Gaze"},
    "anakin-skywalker": {
        6: "Hamartia — The Tyranny of Devotion",
        7: "Peripeteia — The Reversal Born of the Self",
        9: "Anagnorisis — The Ash of Understanding",
        10: "Catharsis — The Terror of Recognition",
    },
}


def esc(value):
    return escape(str(value), quote=True)


def byline(post):
    if not post["author"]:
        return "No byline in print"
    source = post.get("credit_source")
    if source == "site":
        return f"{post['author']} · existing blog credit, no byline in print"
    if source == "school":
        return f"{post['author']} · school-supplied credit, no byline in print"
    return post["author"]


def issue_pdf(post):
    return f"assets/documents/crossroads/crossroads-issue-{post['issue']:02d}.pdf"


def reading_paragraphs(post):
    paragraphs = list(post["paragraphs"])
    for index, fragments in LAYOUT_ARTIFACTS.get(post["slug"], {}).items():
        for fragment in fragments:
            if fragment not in paragraphs[index]:
                raise ValueError(f"Review PDF cleanup for {post['slug']} paragraph {index}")
            paragraphs[index] = paragraphs[index].replace(fragment, "", 1)
    return [paragraph for index, paragraph in enumerate(paragraphs)
            if index not in ADJACENT_ARTICLE_PARAGRAPHS.get(post["slug"], set())]


def body_html(post):
    blocks = []
    subheads = PRINT_SUBHEADS.get(post["slug"], {})
    for index, paragraph in enumerate(reading_paragraphs(post)):
        if index in subheads:
            blocks.append(f'      <h2>{esc(subheads[index])}</h2>')
        blocks.append(f'      <p>{esc(paragraph)}</p>')
    return "\n".join(blocks)


def reading_time(post):
    """Minutes at 220 words per minute, using every published paragraph."""
    prose = sum(len(p.split()) for p in reading_paragraphs(post))
    headings = sum(len(h.split()) for h in PRINT_SUBHEADS.get(post["slug"], {}).values())
    headings += len(post.get("subtitle", "").split())
    return max(1, ceil((prose + headings) / 220))


def image_html(post, loading="lazy"):
    if not post.get("image"):
        return ""
    return (
        f'<img src="assets/img/blog/{esc(post["image"])}" '
        f'alt="{esc(post.get("image_alt", ""))}" '
        f'width="{post["image_width"]}" height="{post["image_height"]}" '
        f'loading="{loading}" decoding="async">'
    )


def rail_html():
    return """<ul class="ij-nav__list">
      <li><a href="#latest">Latest issue</a></li>
      <li><a href="#stories">All stories</a></li>
      <li><a href="#archive">From the archive</a></li>
      <li><a href="#crossroads-link">Crossroads</a></li>
    </ul>"""
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168


def count():
    return blogposts.count()


def issue_count():
    return len(blogposts.issues())
<<<<<<< HEAD
=======


def _latest():
    latest_issue = max(blogposts.issues())
    posts = [p for p in blogposts.by_issue() if p["issue"] == latest_issue]
    lead = posts[0]
    side = []
    for post in posts[1:]:
        image = (
            f'<a class="ij-latest__image" href="{esc(post["slug"])}.html">'
            f'{image_html(post)}</a>' if post.get("image") else ""
        )
        side.append(f"""<article class="ij-latest__side-story">
          <div class="ij-latest__side-copy">
            <p class="ij-category">{esc(post["section"])}</p>
            <h3><a href="{esc(post["slug"])}.html">{esc(post["title"])}</a></h3>
            <p class="ij-latest__side-meta">{esc(byline(post))}</p>
          </div>
          {image}
        </article>""")
    return f"""<section class="ij-section ij-latest" id="latest" aria-labelledby="ij-latest-title">
      <div class="ij-section__head">
        <div><p class="ij-section__number">01 / The current edition</p>
          <h2 id="ij-latest-title">Latest issue</h2></div>
        <a class="ij-issue-link" href="{issue_pdf(lead)}">Crossroads {latest_issue} <span aria-hidden="true">↗</span></a>
      </div>
      <div class="ij-latest__spread">
        <article class="ij-lead">
          <p class="ij-lead__label">Lead essay <span aria-hidden="true">/</span> {esc(lead["section"])}</p>
          <h3><a href="{esc(lead["slug"])}.html">{esc(lead["title"])}</a></h3>
          <p class="ij-lead__excerpt">{esc(lead["excerpt"])}</p>
          <div class="ij-lead__bottom">
            <span>{esc(byline(lead))}</span>
            <span>{reading_time(lead)} min read</span>
            <a href="{esc(lead["slug"])}.html">Read the essay <span aria-hidden="true">→</span></a>
          </div>
        </article>
        <div class="ij-latest__aside">
          <p class="ij-latest__aside-label">Also in Issue {latest_issue}</p>
          {''.join(side)}
        </div>
      </div>
    </section>"""


def _story_row(post, index):
    image = (
        f'<a class="ij-story__image" href="{esc(post["slug"])}.html" '
        f'aria-label="Read {esc(post["title"])}">{image_html(post)}</a>'
        if post.get("image") else ""
    )
    searchable = " ".join([
        post["title"], post["section"], byline(post),
        f"Issue {post['issue']}", post["excerpt"],
    ])
    row_class = "ij-story" if post.get("image") else "ij-story ij-story--type"
    return f"""<article class="{row_class}" data-story data-category="{esc(post["section"])}"
      data-issue="{post["issue"]}" data-title="{esc(post["title"])}"
      data-order="{index}" data-search="{esc(searchable)}">
      <span class="ij-story__number" aria-hidden="true">{index + 1:02d}</span>
      <div class="ij-story__copy">
        <p class="ij-story__category">{esc(post["section"])}</p>
        <h3><a href="{esc(post["slug"])}.html">{esc(post["title"])}</a></h3>
        <p class="ij-story__excerpt">{esc(post["excerpt"])}</p>
      </div>
      <div class="ij-story__details">
        <span>{esc(byline(post))}</span>
        <a href="{issue_pdf(post)}">Issue {post["issue"]}</a>
        <span>{reading_time(post)} min read</span>
      </div>
      {image}
    </article>"""


def _topics():
    counts = Counter(p["section"] for p in blogposts.POSTS)
    items = [
        f'<button type="button" data-topic="all" aria-pressed="true">'
        f'All <span data-topic-count>{count()}</span></button>'
    ]
    for name in sorted(counts, key=lambda item: (-counts[item], item)):
        items.append(
            f'<button type="button" data-topic="{esc(name)}" aria-pressed="false">'
            f'{esc(name)} <span data-topic-count>{counts[name]}</span></button>'
        )
    return "\n".join(items)


def _stories():
    rows = "\n".join(_story_row(post, i)
                     for i, post in enumerate(blogposts.by_issue()))
    return f"""<section class="ij-section ij-stories" id="stories" aria-labelledby="ij-stories-title" data-journal>
      <div class="ij-section__head">
        <div><p class="ij-section__number">02 / The complete collection</p>
          <h2 id="ij-stories-title">All stories</h2></div>
        <span class="ij-section__aside">{count()} articles across {issue_count()} issues</span>
      </div>
      <div class="ij-discovery" data-discovery hidden>
        <div class="ij-discovery__search">
          <label for="ij-search">Search stories</label>
          <input id="ij-search" type="search" placeholder="Title, author, subject…" autocomplete="off" data-search-input>
        </div>
        <div class="ij-discovery__sort">
          <label for="ij-sort">Sort by</label>
          <select id="ij-sort" data-sort>
            <option value="newest">Newest issue</option>
            <option value="oldest">Oldest issue</option>
            <option value="title">Title A–Z</option>
          </select>
        </div>
      </div>
      <div class="ij-topics" role="group" aria-label="Filter stories by topic" data-topic-controls hidden>
        {_topics()}
      </div>
      <p class="ij-results" role="status" aria-live="polite" data-results>{count()} stories</p>
      <div class="ij-story-list" data-story-list>
        {rows}
      </div>
      <div class="ij-empty" data-empty hidden>
        <h3>No stories found</h3>
        <p>Try another search or topic to see the full collection.</p>
        <button type="button" data-reset>Show all stories</button>
      </div>
    </section>"""


def _archive():
    # These two issue dates are printed in their source magazines.
    slugs = ("the-social-glue", "notes-of-healing")
    posts = {p["slug"]: p for p in blogposts.POSTS}
    entries = []
    for post in (posts[slug] for slug in slugs):
        entries.append(f"""<article class="ij-archive__story">
          <p>{esc(post["date"])} <span aria-hidden="true">/</span> Issue {post["issue"]}</p>
          <h3><a href="{esc(post["slug"])}.html">{esc(post["title"])}</a></h3>
          <p>{esc(post["excerpt"])}</p>
        </article>""")
    return f"""<section class="ij-section ij-archive" id="archive" aria-labelledby="ij-archive-title">
      <div class="ij-section__head">
        <div><p class="ij-section__number">03 / Earlier voices</p>
          <h2 id="ij-archive-title">From the archive</h2></div>
        <span class="ij-section__aside">Also listed above in All stories</span>
      </div>
      <div class="ij-archive__grid">{''.join(entries)}</div>
    </section>"""


def front_html():
    markup = (_latest() + _stories() + _archive() +
              """<section class="ij-connection" id="crossroads-link" aria-labelledby="ij-crossroads-title">
      <div>
        <p class="ij-connection__kicker">Every article began in print</p>
        <h2 id="ij-crossroads-title">The Crossroads</h2>
        <p>Read the complete magazine issues and explore the student publication behind these stories.</p>
      </div>
      <a href="crossroads.html">Explore the magazine archive <span aria-hidden="true">↗</span></a>
    </section>
    <aside class="ij-contact" id="write" aria-labelledby="ij-contact-title">
      <h2 id="ij-contact-title">Write for The Crossroads</h2>
      <p>Students can contact the Crossroads Editorial Board through the school.
        A public submission address, deadline and subscription list are not available here yet.</p>
    </aside>""")
    return "\n".join(line.rstrip() for line in markup.splitlines())


# Category first, then a short subject-based bridge for sections with few posts.
RELATED_BRIDGES = {
    "geography-and-geopolitics": ("sportswashing", "trust-or-bust"),
    "sportswashing": ("geography-and-geopolitics", "the-race-beyond"),
    "the-journey-behind-excellence": ("the-race-beyond", "voyages-in-the-yuva-kendra"),
    "the-race-beyond": ("the-journey-behind-excellence", "trust-or-bust"),
    "trust-or-bust": ("the-race-beyond", "geography-and-geopolitics"),
    "rumors-at-cirs": ("the-social-glue", "my-home"),
    "voyages-in-the-yuva-kendra": ("my-home", "resurgence"),
    "my-home": ("voyages-in-the-yuva-kendra", "rumors-at-cirs"),
    "the-social-glue": ("rumors-at-cirs", "my-home"),
}


def related_for(post):
    by_slug = {item["slug"]: item for item in blogposts.POSTS}
    chosen = [
        item for item in blogposts.by_issue()
        if item["section"] == post["section"] and item["slug"] != post["slug"]
    ]
    for slug in RELATED_BRIDGES.get(post["slug"], ()):
        item = by_slug[slug]
        if item not in chosen and item["slug"] != post["slug"]:
            chosen.append(item)
    return chosen[:3]


def related_html(post):
    items = []
    for item in related_for(post):
        items.append(f"""<li>
          <a href="{esc(item["slug"])}.html">
            <span>{esc(item["section"])} / Issue {item["issue"]}</span>
            <strong>{esc(item["title"])}</strong>
          </a>
        </li>""")
    return f"""<section class="art__related" aria-labelledby="art-related-title">
      <h2 id="art-related-title">Keep reading</h2>
      <ul>{''.join(items)}</ul>
    </section>"""
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
