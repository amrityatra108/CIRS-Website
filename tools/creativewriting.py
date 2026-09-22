#!/usr/bin/env python3
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
    return "\n".join(out)
