#!/usr/bin/env python3
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


def count():
    return blogposts.count()


def issue_count():
    return len(blogposts.issues())
