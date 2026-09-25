#!/usr/bin/env python3
<<<<<<< HEAD
"""The Creative Writing page: the moving rows of student work, and the stages.

THE WALL IS EMPTY ON PURPOSE. The design is four rows of posters, one row per
class group, sliding past. The school's own creative writing has not been
supplied yet, so every poster below is a slot that says so in plain words.

The design this page is built to arrived with titles already in it — "The
Little Dreamer", "The Secret Garden", "A Letter to Tomorrow" — and class
attributions under them. Not one of those is a CIRS pupil's work: they are
the mock designer's filler. Putting them on a school's live site would
announce stories that nobody wrote, under classes that never sent them in,
each with a READ STORY link to nothing. So they are not here.

TO PUBLISH. Add the pieces to PIECES below, keyed by class group:

    PIECES = {
        "5-6": [
            {"title": "…", "author": "…", "href": "assets/documents/…pdf"},
        ],
    }

A group with pieces renders them as posters; a group without renders its
slots. href is optional — a piece with no file yet still reads as a poster,
it simply does not open. Nothing else has to change: the rows, the repeats
that fill the strip and the wall's copy all follow from this list.

HOW A ROW MOVES. A row is a marquee: the cards are repeated until the strip
is wider than any screen, and the track is two identical halves so it can
loop by sliding exactly half its width. Where a row carries real pieces only
the first copy is a real link — every repeat after it is aria-hidden and out
of the tab order, so a screen reader and the tab key meet each piece once.
A row of slots is one decorative strip: the whole track is aria-hidden and
the row's heading carries the state in a sentence instead, rather than
reading "awaiting a piece" eight times over.
"""

# The four class groups, in the order they appear on the wall.
CLASS_GROUPS = [
    ("5-6",   "Classes V &ndash; VI"),
    ("7-8",   "Classes VII &ndash; VIII"),
    ("9-10",  "Classes IX &ndash; X"),
    ("11-12", "Classes XI &ndash; XII"),
]

# Published work, by class group. Empty until the Crossroads Editorial Board
# supplies it — see the note at the top before filling anything in here.
PIECES = {}

# Slots shown on a row with nothing published yet.
SLOTS = 4

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


def published():
    """Every published piece, flattened."""
    return [p for key, _ in CLASS_GROUPS for p in PIECES.get(key, [])]


def count():
    return len(published())


def _slot(label, n, index):
    """An empty poster: a place on the wall, and what it is waiting for."""
    glyph = GLYPHS[index % len(GLYPHS)]
    return f'''            <article class="cw-poster cw-poster--slot">
              <div class="cw-poster__card">
                <span class="cw-poster__art" aria-hidden="true">
                  <span class="cw-poster__num">{n:02d}</span>
                  <span class="cw-poster__glyph">{glyph}</span>
                </span>
                <span class="cw-poster__type">{label}</span>
                <span class="cw-poster__title">Awaiting a piece</span>
                <span class="cw-poster__meta">To be supplied by the Crossroads
                  Editorial Board</span>
                <span class="cw-poster__read">Not yet published</span>
              </div>
            </article>'''


def _poster(piece, label, n, index, real):
    """One published piece. Only the first copy is a link anyone can reach."""
    glyph = GLYPHS[index % len(GLYPHS)]
    hide = "" if real else ' aria-hidden="true"'
    tab = "" if real else ' tabindex="-1"'
    by = esc(piece["author"])
    note = esc(piece.get("note", ""))
    inner = f'''                <span class="cw-poster__art" aria-hidden="true">
                  <span class="cw-poster__num">{n:02d}</span>
                  <span class="cw-poster__glyph">{glyph}</span>
                </span>
                <span class="cw-poster__type">{label}</span>
                <span class="cw-poster__title">{esc(piece["title"])}</span>
                <span class="cw-poster__by">{by}</span>
                <span class="cw-poster__meta">{note}</span>'''
    if piece.get("href"):
        return f'''            <article class="cw-poster"{hide}>
              <a class="cw-poster__link" href="{piece["href"]}"{tab}>
{inner}
                <span class="cw-poster__read">Read the piece
                  <span aria-hidden="true">&rarr;</span></span>
              </a>
            </article>'''
    # Published, but the school has not sent the file yet: a poster that reads
    # as a poster and says plainly that it does not open.
    return f'''            <article class="cw-poster"{hide}>
              <div class="cw-poster__card">
{inner}
                <span class="cw-poster__read">File to follow</span>
              </div>
            </article>'''


def rows_html():
    """The four class rows — posters where there is work, slots where there is not."""
    out = []
    for i, (key, label) in enumerate(CLASS_GROUPS):
        pieces = PIECES.get(key, [])
        base = pieces if pieces else list(range(SLOTS))
        # Repeat the cards until one half of the track is wider than any
        # screen, then lay two identical halves so the loop has no seam.
        repeat = max(1, -(-MIN_PER_HALF // len(base)))
        half = base * repeat
        cards = []
        for copy in range(2):
            for j, item in enumerate(half):
                if pieces:
                    real = copy == 0 and j < len(base)
                    cards.append(_poster(item, label, j % len(base) + 1, j, real))
                else:
                    cards.append(_slot(label, j % len(base) + 1, j))

        # A row of slots says its state once, in the heading, rather than
        # eight times over in a strip a screen reader cannot skim.
        if pieces:
            said, track_hidden = "", ""
        else:
            said = (' <span class="vh">&mdash; no pieces published yet; '
                    'awaiting the Crossroads Editorial Board.</span>')
            track_hidden = ' aria-hidden="true"'

        out.append(f'''      <div class="cw-row cw-row--{'right' if i % 2 else 'left'} rv">
        <p class="cw-row__label"><span class="sc">{label}</span>{said}</p>
        <div class="cw-row__window">
          <div class="cw-track"{track_hidden}>
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
=======
"""Render the curated CIRS Creative Writing anthology from structured content.

Edit creative-writing-content.json to add a chapter or poem. The supplied
collection is the sole source of student writing; this module supplies layout
and navigation, never substitute writing or attribution.
"""

from __future__ import annotations

import html
import json
from pathlib import Path


CONTENT_PATH = Path(__file__).with_name("creative-writing-content.json")


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def collection() -> dict:
    data = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    seen = set()
    for chapter in data["chapters"]:
        if not chapter.get("id") or not chapter.get("title"):
            raise ValueError("Every chapter needs an id and title")
        if not chapter.get("poems"):
            raise ValueError("Only populated chapters may appear in the anthology")
        if chapter["id"] in seen:
            raise ValueError(f"Duplicate anthology id: {chapter['id']}")
        seen.add(chapter["id"])
        for poem in chapter["poems"]:
            if not poem.get("id") or not poem.get("author") or not poem.get("stanzas"):
                raise ValueError("Every poem needs an id, author and stanzas")
            if poem["id"] in seen:
                raise ValueError(f"Duplicate anthology id: {poem['id']}")
            if any(ch.isdigit() for ch in poem["author"]):
                raise ValueError(f"Numeric identifier in author field: {poem['id']}")
            seen.add(poem["id"])
    return data


def published() -> list[dict]:
    return [poem for chapter in collection()["chapters"] for poem in chapter["poems"]]


def count() -> int:
    return len(published())


def writer_count() -> int:
    return len({poem["author"].casefold() for poem in published()})


def _opening(poem: dict) -> str:
    return poem["stanzas"][0].splitlines()[0]


def hero_excerpt_html() -> str:
    """A source-checked margin excerpt with a linked poet credit."""
    poem = next(poem for poem in published() if poem["id"] == "turning-ananda-priyan")
    lines = ["Still, sometimes in the margin,", "there’s pressure without a mark"]
    if "\n".join(lines) not in "\n".join(poem["stanzas"]):
        raise ValueError("Hero excerpt differs from the sourced poem")
    excerpt = "<br>".join(esc(line) for line in lines)
    return (
        '<span class="cw-hero__excerpt-theme">From Turning a New Page</span>'
        f'<span class="cw-hero__excerpt-line">{excerpt}</span>'
        f'<cite class="cw-hero__excerpt-credit">— {esc(poem["author"])}</cite>'
        f'<a class="cw-hero__excerpt-link" href="#poem-{esc(poem["id"])}">Read the poem <span aria-hidden="true">↗</span></a>'
    )


def _row_card(poem: dict, n: int, real: bool) -> str:
    opening = esc(_opening(poem))
    author = esc(poem["author"])
    contents = (
        f'<span class="cw-row__card-number">Poem {n:02d}</span>'
        f'<span class="cw-row__card-opening">{opening}</span>'
        f'<span class="cw-row__card-author">By {author}</span>'
        '<span class="cw-row__card-action">Read full poem <span aria-hidden="true">↗</span></span>'
    )
    if real:
        return (
            f'<a class="cw-row__card" href="#poem-{esc(poem["id"])}">'
            + contents + '</a>'
        )
    return (
        f'<div class="cw-row__card" aria-hidden="true" '
        f'data-cw-target="#poem-{esc(poem["id"])}">'
        + contents + '</div>'
    )


def rows_html() -> str:
    """Five seamless moving rows; only three unique poem links per theme."""
    rows = []
    for chapter_n, chapter in enumerate(collection()["chapters"], 1):
        chapter_id = esc(chapter["id"])
        eyebrow = f"Chapter {chapter_n:02d}"
        if chapter.get("month"):
            eyebrow += f' <span aria-hidden="true">·</span> {esc(chapter["month"])}'
        poems = chapter["poems"]
        # At least six cards per half keep the loop wider than desktop screens.
        # Visual repetitions have no links and are hidden from assistive tech.
        real_cards = [_row_card(poem, n, True) for n, poem in enumerate(poems, 1)]
        clones = [_row_card(poem, n, False) for n, poem in enumerate(poems, 1)]
        repeats = max(2, -(-6 // len(poems)))
        first_half = "\n".join(real_cards + clones * (repeats - 1))
        second_half = "\n".join(clones * repeats)
        direction = "left" if chapter_n % 2 else "right"
        rows.append(f'''<div class="cw-row cw-row--{direction}">
  <div class="wrap cw-row__head">
    <p class="cw-row__eyebrow">{eyebrow}</p>
    <h3 class="cw-row__title"><a href="#chapter-{chapter_id}">{esc(chapter["title"])}</a></h3>
    <p class="cw-row__count">{len(poems)} selected poems</p>
  </div>
  <div class="cw-row__window">
    <div class="cw-row__track">
      <div class="cw-row__half">
{first_half}
      </div>
      <div class="cw-row__half" aria-hidden="true">
{second_half}
      </div>
    </div>
  </div>
</div>''')
    return "\n".join(rows)


def _poem_html(poem: dict, chapter: dict, n: int, total_in_chapter: int,
               previous: dict | None, following: dict | None) -> str:
    poem_id = esc(poem["id"])
    title = esc(_opening(poem))
    stanzas = "\n".join(
        '<p class="cw-poem__stanza">'
        + "<br>".join(esc(line) for line in stanza.splitlines())
        + "</p>"
        for stanza in poem["stanzas"]
    )
    links = []
    if previous:
        links.append(
            f'<a class="cw-poem__nav-link cw-poem__nav-link--prev" href="#poem-{esc(previous["id"])}">'
            '<span aria-hidden="true">←</span> Previous poem</a>'
        )
    links.append(
        f'<a class="cw-poem__nav-link cw-poem__nav-link--theme" href="#chapter-{esc(chapter["id"])}">'
        'Back to chapter</a>'
    )
    if following:
        links.append(
            f'<a class="cw-poem__nav-link cw-poem__nav-link--next" href="#poem-{esc(following["id"])}">'
            'Next poem <span aria-hidden="true">→</span></a>'
        )
    return f'''    <article class="cw-poem" id="poem-{poem_id}" aria-labelledby="poem-{poem_id}-title">
      <div class="cw-poem__topline"><span>Poem {n:02d} of {total_in_chapter:02d}</span><span>Opening line</span></div>
      <h3 class="cw-poem__title" id="poem-{poem_id}-title">{title}</h3>
      <p class="cw-poem__byline">By <span>{esc(poem["author"])}</span></p>
      <div class="cw-poem__body">
{stanzas}
      </div>
      <nav class="cw-poem__nav" aria-label="Navigate from poem beginning {title} by {esc(poem["author"])}">
        {"".join(links)}
      </nav>
    </article>'''


def _interlude_html(poem_id: str, lines: list[str]) -> str:
    poem = next(poem for poem in published() if poem["id"] == poem_id)
    source = "\n".join(poem["stanzas"])
    excerpt = "\n".join(lines)
    if excerpt not in source:
        raise ValueError(f"Editorial excerpt differs from poem {poem_id}")
    line_html = "<br>".join(esc(line) for line in lines)
    return (
        '<blockquote class="cw-interlude" data-cw-reveal>'
        f'<p class="cw-interlude__line">{line_html}</p>'
        f'<cite class="cw-interlude__credit">— {esc(poem["author"])}</cite>'
        "</blockquote>"
    )


def chapters_html() -> str:
    chapters = collection()["chapters"]
    all_poems = [poem for chapter in chapters for poem in chapter["poems"]]
    positions = {poem["id"]: i for i, poem in enumerate(all_poems)}
    out = []
    for chapter_n, chapter in enumerate(chapters, 1):
        chapter_id = esc(chapter["id"])
        month = f'<span class="cw-chapter__month">{esc(chapter["month"])}</span>' if chapter.get("month") else ""
        poems = []
        for poem_n, poem in enumerate(chapter["poems"], 1):
            i = positions[poem["id"]]
            poems.append(_poem_html(
                poem, chapter, poem_n, len(chapter["poems"]),
                all_poems[i - 1] if i else None,
                all_poems[i + 1] if i + 1 < len(all_poems) else None,
            ))
        out.append(f'''<section class="cw-chapter cw-chapter--{chapter_n}" id="chapter-{chapter_id}" aria-labelledby="chapter-{chapter_id}-title">
  <div class="cw-chapter__inner">
    <header class="cw-chapter__head" data-cw-reveal>
      <p class="cw-chapter__eyebrow">Chapter {chapter_n:02d} {month}</p>
      <h2 class="cw-chapter__title" id="chapter-{chapter_id}-title">{esc(chapter["title"])}</h2>
      <div class="cw-chapter__details">
        <p class="cw-chapter__count">{len(chapter["poems"])} poems · {len({p["author"].casefold() for p in chapter["poems"]})} writers</p>
        <a class="cw-chapter__back" href="#chapters">Back to index <span aria-hidden="true">↗</span></a>
      </div>
    </header>
    <div class="cw-chapter__poems">
{chr(10).join(poems)}
    </div>
  </div>
</section>''')
        if chapter_n == 1:
            out.append(_interlude_html(
                "joy-aryaa-shah", ["Little lights proving everything's alright"]
            ))
        if chapter_n == 3:
            out.append(_interlude_html(
                "refuge-tarushi-agarwal",
                ["Here I don't have to explain a thing,", "I just draw until my thoughts take wing."]
            ))
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
    return "\n".join(out)
