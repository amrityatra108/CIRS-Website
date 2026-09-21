#!/usr/bin/env python3
"""The Maths Challenge archive: the monthly problems, and the grade zones.

CHALLENGES is empty, and that is not an oversight.

The Maths Challenge page was an under-construction stub: a heading, four
bullet points and a line saying the format and the past problems were still
to come from the mathematics department. There were no problem papers on it,
no archive, no results and no links — the only links the page carried were
the ones every page carries, in the header and the footer.

So there is nothing here to reproduce. The archive below is the shape the
resources will take rather than the resources themselves, and until the
department supplies them the page says so in as many words instead of
showing an archive that does not exist. Inventing a month, a paper or a
winner would put words in the school's mouth, and the page would read as
though the challenge had a history the site cannot show.

To publish the archive: add an entry per problem paper, put the file in
assets/documents/math-challenge/, and the page builds the cards, the grade
filters and the search from this list. Nothing else has to change.

    {"month": "February 2026",      # as it should read on the card
     "grade": "9-10",              # one of the GRADE keys below
     "title": "The Ladder Problem",
     "file": "feb-2026-grades-9-10.pdf",   # in assets/documents/math-challenge/
     "note": "Solutions published with the March paper."}   # optional
"""

# The four zones, in the order they appear on the page. The key is what the
# filter buttons and each card carry in data-grade.
GRADES = [
    ("5-6",   "Grades 5&ndash;6",   "Foundation Challenge",
     "Number sense, pattern and logic &mdash; problems that reward noticing "
     "rather than calculating quickly."),
    ("7-8",   "Grades 7&ndash;8",   "Logic Challenge",
     "Reasoning stretched further: relationships, geometry and the kind of "
     "puzzle that needs a plan before a pencil."),
    ("9-10",  "Grades 9&ndash;10",  "Advanced Challenge",
     "Problems that ask a student to connect ideas from different parts of "
     "the syllabus, and to justify the connection."),
    ("11-12", "Grades 11&ndash;12", "Master Challenge",
     "Sustained problems of the sort that reward a whole evening, and the "
     "habits of mind that higher study asks for."),
]

# The five stages of the journey: number, name, and what happens there.
JOURNEY = [
    ("01", "Question", "Read it twice. Decide what is actually being asked, "
                       "and what is only decoration."),
    ("02", "Think",    "Look for the pattern, the symmetry, the thing that "
                       "stays the same while everything else moves."),
    ("03", "Explore",  "Try the small case. Draw it. Guess, then test the "
                       "guess and find out why it failed."),
    ("04", "Solve",    "Build the argument step by step, and check that each "
                       "step follows from the one before it."),
    ("05", "Discover", "Ask what the problem was really about &mdash; that is "
                       "the part that carries to the next one."),
]

# Every problem paper published. See the note at the top of this file.
CHALLENGES = []


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def zones_html():
    """The four grade cards."""
    out = []
    for i, (key, label, title, blurb) in enumerate(GRADES, 1):
        out.append(f'''      <article class="ma-zone rv" data-grade="{key}">
        <p class="ma-zone__grade">{label}</p>
        <h3 class="ma-zone__title">{title}</h3>
        <p class="ma-zone__copy">{blurb}</p>
        <span class="ma-zone__mark" aria-hidden="true">{i:02d}</span>
      </article>''')
    return "\n".join(out)


def journey_html():
    """The five stages, as a numbered list."""
    out = []
    for num, name, what in JOURNEY:
        out.append(f'''      <li class="ma-step rv">
        <p class="ma-step__n">{num}</p>
        <h3 class="ma-step__name">{name}</h3>
        <p class="ma-step__copy">{what}</p>
      </li>''')
    return "\n".join(out)


def filters_html():
    """The grade filters. Rendered only when there is something to filter."""
    if not CHALLENGES:
        return ""
    buttons = ['        <button type="button" class="ma-filter is-on" data-grade="all" '
               'aria-pressed="true">All</button>']
    for key, label, _, _ in GRADES:
        buttons.append(f'        <button type="button" class="ma-filter" data-grade="{key}" '
                       f'aria-pressed="false">{label}</button>')
    return f'''      <div class="ma-tools">
        <div class="ma-filters" role="group" aria-label="Filter by grade">
{chr(10).join(buttons)}
        </div>
        <label class="ma-search">
          <span class="vh">Search the challenges</span>
          <input type="search" id="maSearch" placeholder="Search by month or title"
                 autocomplete="off">
        </label>
      </div>'''


def archive_html():
    """The papers — or, until there are any, what the page is waiting for."""
    if not CHALLENGES:
        return '''      <p class="ma-empty">
        <span class="ma-empty__mark" aria-hidden="true">&empty;</span>
        <em>[Placeholder &mdash; the monthly problem papers, the grades each was set for and
        the solutions, to be supplied by the mathematics department.]</em>
        Nothing is published here yet. When the papers are added they will appear in this
        archive, filterable by grade zone and searchable by month.
      </p>'''

    cards = []
    for c in CHALLENGES:
        note = f'<p class="ma-card__note">{esc(c["note"])}</p>' if c.get("note") else ""
        label = next((l for k, l, _, _ in GRADES if k == c["grade"]), c["grade"])
        cards.append(f'''        <article class="ma-card rv" data-grade="{c["grade"]}"
                 data-find="{esc((c["month"] + " " + c["title"]).lower())}">
          <p class="ma-card__when">{esc(c["month"])} &middot; <span>{label}</span></p>
          <h3 class="ma-card__title">{esc(c["title"])}</h3>
          {note}
          <a class="ma-card__open" href="assets/documents/math-challenge/{c["file"]}">
            Open the problem <span aria-hidden="true">&rarr;</span>
          </a>
        </article>''')
    return (f'''      <div class="ma-grid" id="maGrid">
{chr(10).join(cards)}
      </div>
      <p class="ma-none" id="maNone" hidden>No challenge matches that search.</p>''')


def count():
    return len(CHALLENGES)
