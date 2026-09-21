#!/usr/bin/env python3
"""The Creative Writing page: the moving rows of student work, and the stages.

WHERE THE POSTERS COME FROM. Every card on this page is a piece the school
has already published — the articles in tools/blogposts.py, each lifted whole
from an issue of The Crossroads and already given a page of its own by
build-site.py. Nothing here is written for the page: the title, the writer,
the section and the issue are the magazine's own, and each poster opens the
piece itself rather than a summary of it.

That matters because the design this page is built to is a wall of moving
posters, and a wall of moving posters is exactly the sort of thing that
invites invented titles and invented names to fill it. There are none. Where
the school has not published something — poetry and fiction, and the address
to send work to — the page says so in plain words instead, in the block below
the rows.

ROWS. Three, grouped by the sections the magazine itself uses, so a reader
who wants argument and a reader who wants the campus are not given the same
row. A row is a marquee: the cards are repeated until the strip is wider than
any screen, and the track is two identical halves so it can loop by sliding
exactly half its width. Only the first copy of each card is a real link —
every repeat after it is aria-hidden and out of the tab order, so a screen
reader and the tab key meet each piece once.

To add a piece: publish it in tools/blogposts.py. It joins the row its
section belongs to, with no edit here.
"""

import blogposts

# Which sections ride in which row, and what the row is called. A section not
# named here would be silently dropped, so ROWS is checked against the posts
# at build time — see rows() below.
ROWS = [
    ("Opinion &amp; Editorial", ["Opinion", "The Editorial"]),
    ("Culture &amp; Campus Life", ["Culture", "Campus Life", "Reflection"]),
    ("Economics, the World &amp; Sport", ["Economics", "World", "Sport"]),
]

# The five stages, as the reference lays them out. They describe the writing,
# not any student's writing, so nothing here is a claim about anybody.
JOURNEY = [
    ("01", "Imagine", "Let the first idea arrive, before it is any good."),
    ("02", "Explore", "Follow the curiosity wherever it leads, and read."),
    ("03", "Write",   "Give the idea a voice. A first draft is allowed to be one."),
    ("04", "Refine",  "Shape the words, and cut the ones doing no work."),
    ("05", "Share",   "Let the story find its reader."),
]

# The decorative glyph in the corner of a poster. Four, cycled, so a row has
# rhythm; all four are aria-hidden.
GLYPHS = ["Aa", "&#10022;", "&ldquo;", "&#9998;"]

# Cards per half of a track. Below this a short row loops visibly; the cards
# are repeated until the half is at least this long.
MIN_PER_HALF = 8


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rows():
    """Each row with the published pieces that belong to it, newest first."""
    by_section = {}
    for post in blogposts.POSTS:
        by_section.setdefault(post["section"], []).append(post)

    placed = set()
    out = []
    for label, sections in ROWS:
        items = []
        for section in sections:
            items += by_section.get(section, [])
            placed.add(section)
        # The magazine orders by issue; the newest issue leads the row.
        items.sort(key=lambda p: -p["issue"])
        if items:
            out.append((label, items))

    missed = sorted(set(by_section) - placed)
    if missed:
        raise ValueError("Creative Writing: no row carries " + ", ".join(missed))
    return out


def count():
    return len(blogposts.POSTS)


def _poster(post, n, index, real):
    """One poster. Only the first copy of a piece is a link anyone can reach."""
    glyph = GLYPHS[index % len(GLYPHS)]
    issue = f"Issue {post['issue']:02d}"
    when = f" &middot; {esc(post['date'])}" if post.get("date") else ""
    hide = "" if real else ' aria-hidden="true"'
    tab = "" if real else ' tabindex="-1"'
    return f'''            <article class="cw-poster"{hide}>
              <a class="cw-poster__link" href="{post['slug']}.html"{tab}>
                <span class="cw-poster__art" aria-hidden="true">
                  <span class="cw-poster__num">{n:02d}</span>
                  <span class="cw-poster__glyph">{glyph}</span>
                </span>
                <span class="cw-poster__type">{esc(post['section'])}</span>
                <span class="cw-poster__title">{esc(post['title'])}</span>
                <span class="cw-poster__by">{esc(post['author'])}</span>
                <span class="cw-poster__meta">{issue}{when}</span>
                <span class="cw-poster__read">Read the piece
                  <span aria-hidden="true">&rarr;</span></span>
              </a>
            </article>'''


def rows_html():
    """The three marquee rows — or nothing at all, if nothing is published."""
    groups = rows()
    if not groups:
        return ""

    out = []
    for i, (label, items) in enumerate(groups):
        # Repeat the pieces until one half of the track is wider than any
        # screen, then lay two identical halves so the loop has no seam.
        repeat = max(1, -(-MIN_PER_HALF // len(items)))
        half = items * repeat
        cards = []
        for copy in range(2):
            for j, post in enumerate(half):
                real = copy == 0 and j < len(items)
                cards.append(_poster(post, j % len(items) + 1, j, real))
        out.append(f'''      <div class="cw-row cw-row--{'right' if i % 2 else 'left'} rv">
        <p class="cw-row__label"><span class="sc">{label}</span></p>
        <div class="cw-row__window">
          <div class="cw-track">
{chr(10).join(cards)}
          </div>
        </div>
      </div>''')
    return "\n".join(out)


def journey_html():
    out = []
    for num, name, what in JOURNEY:
        out.append(f'''        <li class="cw-step rv">
          <p class="cw-step__n">{num}</p>
          <h3 class="cw-step__name">{name}</h3>
          <p class="cw-step__copy">{what}</p>
        </li>''')
    return "\n".join(out)
