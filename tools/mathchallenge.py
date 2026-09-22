#!/usr/bin/env python3
"""The Math Challenge archive: the monthly winners, and the grade zones.

WHAT THESE PAPERS ARE. They are the school's winners announcements — each
one names the winners for a grade group in a given month and carries their
photographs — and they are not problem papers. The page says so in those
words. Filing them as "the monthly problem" would misdescribe them to every
parent who opened one, and the mathematics department has not supplied the
problems themselves.

They are laid out month by month, the way the school's own Maths Challenge
page lays them out, newest month first. Twenty-five papers across seven
months; two months are short a grade group, which is left as a gap rather
than filled in.

To add a month: put the PDFs in assets/documents/math-challenge/<yyyy-mm>/
as grades-5-6.pdf and so on, and add the month here. The cards, the grade
filters and the search all build from this list.
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

# Month by month, newest first. Each is (folder, how it should read, the
# grade groups that month has). A month short of a grade group is short of
# it here too — October 2025 has no 11-12 paper and February 2026 has
# neither 9-10 nor 11-12, and inventing one would be inventing a result.
MONTHS = [
    ("2026-04", "April 2026",     ["5-6", "7-8", "9-10", "11-12"]),
    ("2026-02", "February 2026",  ["5-6", "7-8"]),
    ("2026-01", "January 2026",   ["5-6", "7-8", "9-10", "11-12"]),
    ("2025-10", "October 2025",   ["5-6", "7-8", "9-10"]),
    ("2025-09", "September 2025", ["5-6", "7-8", "9-10", "11-12"]),
    ("2025-08", "August 2025",    ["5-6", "7-8", "9-10", "11-12"]),
    ("2025-07", "July 2025",      ["5-6", "7-8", "9-10", "11-12"]),
]


def challenges():
    """Every paper, flattened, newest month first."""
    out = []
    for key, label, grades in MONTHS:
        for g in grades:
            out.append({"key": key, "month": label, "grade": g,
                        "file": f"{key}/grades-{g}.pdf"})
    return out


CHALLENGES = challenges()


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
    """The grade filters and the search. Only when there is something to filter."""
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
          <span class="vh">Search the winners by month</span>
          <input type="search" id="maSearch" placeholder="Search by month"
                 autocomplete="off">
        </label>
      </div>'''


def archive_html():
    """The winners, month by month — or what the page is waiting for."""
    if not CHALLENGES:
        return '''      <p class="ma-empty">
        <span class="ma-empty__mark" aria-hidden="true">&empty;</span>
        <em>[Placeholder &mdash; the monthly winners, to be supplied by the mathematics
        department.]</em>
      </p>'''

    months = []
    for key, label, grades in MONTHS:
        cards = []
        for g in grades:
            gl = next(l for k, l, _, _ in GRADES if k == g)
            # The month is the heading above these cards, so a card carries
            # only its grade group; repeating the month on all four of them
            # made every card in a month read the same.
            cards.append(f'''          <article class="ma-card rv" data-grade="{g}"
                   data-find="{esc(label.lower())}">
            <h4 class="ma-card__title">{gl}</h4>
            <a class="ma-card__open" href="assets/documents/math-challenge/{key}/grades-{g}.pdf">
              <span class="vh">{esc(label)}, </span>See the winners
              <span aria-hidden="true">&rarr;</span>
            </a>
          </article>''')
        months.append(f'''      <section class="ma-month rv" data-month="{key}">
        <h3 class="ma-month__name">{esc(label)}</h3>
        <div class="ma-grid">
{chr(10).join(cards)}
        </div>
      </section>''')

    return (f'''      <div class="ma-months" id="maGrid">
{chr(10).join(months)}
      </div>
      <p class="ma-none" id="maNone" hidden>No month matches that search.</p>''')


def count():
    return len(CHALLENGES)
