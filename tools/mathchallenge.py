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
months; two months are short a grade group, which are shown with consistent
grade slots and clearly labeled "No document published".

To add a month: put the PDFs in assets/documents/math-challenge/<yyyy-mm>/
as grades-5-6.pdf and so on, and add the month here. The cards, the grade
filters and the search all build from this list.
"""

# The four zones, in the order they appear on the page. The key is what the
# filter buttons and each card carry in data-grade.
GRADES = [
    ("5-6",   "Grades 5&ndash;6",   "Foundation Challenge",
     "Number sense, pattern and logic &mdash; problems that reward noticing "
     "rather than calculating quickly.",
     "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"),
    ("7-8",   "Grades 7&ndash;8",   "Logic Challenge",
     "Reasoning stretched further: relationships, geometry and the kind of "
     "puzzle that needs a plan before a pencil.",
     "M12 3a9 9 0 1 0 9 9M12 3v9l6 3M3 12h9"),
    ("9-10",  "Grades 9&ndash;10",  "Advanced Challenge",
     "Problems that ask a student to connect ideas from different parts of "
     "the syllabus, and to justify the connection.",
     "M3 19c4-8 8-14 18-14M3 5v14h18M7 19v-4M12 19v-9M17 19V7"),
    ("11-12", "Grades 11&ndash;12", "Master Challenge",
     "Sustained problems of the sort that reward a whole evening, and the "
     "habits of mind that higher study asks for.",
     "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"),
]

# The five stages of the journey: number, name, practical thinking technique,
# and demonstration problem step.
JOURNEY = [
    ("01", "Question",
     "Read it twice. Decide what is actually being asked, and what is only decoration.",
     "The Mutilated Chessboard",
     "An 8&times;8 board has 64 squares. Cut away two diagonally opposite corners, leaving 62 squares. Can you tile the remaining surface with 31 dominoes of size 2&times;1 without overlap?",
     "Question technique: strip decorative constraints; express the board strictly by its boundary geometry."),
    ("02", "Think",
     "Look for the pattern, the symmetry, the thing that stays the same while everything else moves.",
     "Search for an Invariant",
     "Observe what does not change: regardless of where a 2&times;1 domino is laid horizontally or vertically, it must cover two adjacent squares that share an edge.",
     "Thinking technique: do not start testing arrangements; search for a conserved property (an invariant)."),
    ("03", "Explore",
     "Try the small case. Draw it. Guess, then test the guess and find out why it failed.",
     "The Minimal 2&times;2 Case",
     "Reduce to a 2&times;2 grid with opposite corners excised: only 2 squares remain. Can one domino cover them? No &mdash; they only touch diagonally at a vertex, sharing no edge.",
     "Exploration technique: minimal cases expose geometric edge-sharing rules that brute force obscures."),
    ("04", "Solve",
     "Build the argument step by step, and check that each step follows from the one before it.",
     "Color Parity Deduction",
     "Color the 64 squares like a chessboard: 32 dark, 32 light. Diagonally opposite corners always share the same color! Removing two dark corners leaves 30 dark and 32 light squares. But every 2&times;1 domino covers exactly 1 dark and 1 light square. Thirty-one dominoes require 31 dark and 31 light squares. Since 30 &ne; 32, complete tiling is mathematically impossible!",
     "Solving technique: coloring transforms an impossible brute-force search into a deterministic parity proof."),
    ("05", "Discover",
     "Ask what the problem was really about &mdash; that is the part that carries to the next one.",
     "The Power of Invariants",
     "Without parity, checking all possible placements would require over 2&times;10<sup>15</sup> tests. By identifying an invariant, the problem resolves in seconds. This principle carries forward to graph theory, topology, and algorithm design.",
     "Discovery technique: the best solution changes how you view structure, not merely the answer to one question."),
]

# Month by month, newest first. Each is (folder, how it should read, the
# grade groups that month has published).
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
    """The four grade cards with interactive zone selection."""
    out = []
    for i, (key, label, title, blurb, path_data) in enumerate(GRADES, 1):
        out.append(f'''      <article class="ma-zone rv" data-grade="{key}" tabindex="0" role="region" aria-label="{title} ({label})">
        <div class="ma-zone__head">
          <span class="ma-zone__icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <path d="{path_data}"/>
            </svg>
          </span>
          <p class="ma-zone__grade">{label}</p>
        </div>
        <h3 class="ma-zone__title">{title}</h3>
        <p class="ma-zone__copy">{blurb}</p>
        <button type="button" class="ma-zone__btn" data-filter-grade="{key}">
          <span>View {label} Archive</span>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
            <path d="M7 1v12M1.5 7.5L7 13l5.5-5.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <span class="ma-zone__mark" aria-hidden="true">{i:02d}</span>
      </article>''')
    return "\n".join(out)


def journey_html():
    """The five stages, rendered as an interactive problem-solving showcase."""
    out = []
    for num, name, technique, step_title, step_problem, step_note in JOURNEY:
        active = ' is-active' if num == '01' else ''
        out.append(f'''      <li class="ma-step rv{active}" data-step="{num}" id="step-{num}">
        <div class="ma-step__badge">
          <span class="ma-step__n">{num}</span>
          <span class="ma-step__tag">{name}</span>
        </div>
        <h3 class="ma-step__name">{step_title}</h3>
        <p class="ma-step__technique"><strong>Technique:</strong> {technique}</p>
        <div class="ma-step__exhibit">
          <p class="ma-step__desc">{step_problem}</p>
          <p class="ma-step__subnote">{step_note}</p>
        </div>
      </li>''')
    return "\n".join(out)


def filters_html():
    """The grade filters and the search."""
    if not CHALLENGES:
        return ""
    buttons = ['        <button type="button" class="ma-filter is-on" data-grade="all" '
               'aria-pressed="true">All Grades</button>']
    for key, label, _, _, _ in GRADES:
        buttons.append(f'        <button type="button" class="ma-filter" data-grade="{key}" '
                       f'aria-pressed="false">{label}</button>')
    return f'''      <div class="ma-tools">
        <div class="ma-filters" role="group" aria-label="Filter archive by grade">
{chr(10).join(buttons)}
        </div>
        <div class="ma-search-wrap">
          <label class="ma-search">
            <span class="vh">Search archive by month or year</span>
            <input type="search" id="maSearch" placeholder="Search by month or year (e.g. April, 2026)"
                   autocomplete="off" aria-label="Search winners archive">
          </label>
        </div>
      </div>'''


def archive_html():
    """The winners, month by month, with 4 consistent grade slots and honest empty states."""
    if not CHALLENGES:
        return '''      <p class="ma-empty">
        <span class="ma-empty__mark" aria-hidden="true">&empty;</span>
        <em>[Placeholder &mdash; the monthly winners, to be supplied by the mathematics
        department.]</em>
      </p>'''

    months = []
    for key, label, published_grades in MONTHS:
        cards = []
        for g, gl, gtitle, _, _ in GRADES:
            if g in published_grades:
                cards.append(f'''          <article class="ma-card ma-card--published rv" data-grade="{g}"
                   data-find="{esc(label.lower())}">
            <div class="ma-card__header">
              <span class="ma-card__pill">Published Bulletin</span>
              <span class="ma-card__month-tag">{esc(label)}</span>
            </div>
            <h4 class="ma-card__title">{gl}</h4>
            <p class="ma-card__division">{gtitle}</p>
            <p class="ma-card__desc">Official school announcement naming monthly winners and student honorees.</p>
            <a class="ma-card__open" href="assets/documents/math-challenge/{key}/grades-{g}.pdf" target="_blank" rel="noopener">
              <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M9 1H3a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V6L9 1Z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M9 1v5h5M5 11h6M5 8h3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
              <span>View {gl} Winners (PDF)</span>
              <span class="ma-card__arrow" aria-hidden="true">&rarr;</span>
            </a>
          </article>''')
            else:
                cards.append(f'''          <article class="ma-card ma-card--empty rv" data-grade="{g}"
                   data-find="{esc(label.lower())}">
            <div class="ma-card__header">
              <span class="ma-card__pill ma-card__pill--none">No document published</span>
              <span class="ma-card__month-tag">{esc(label)}</span>
            </div>
            <h4 class="ma-card__title">{gl}</h4>
            <p class="ma-card__division">{gtitle}</p>
            <p class="ma-card__empty-note">The mathematics department did not issue a bulletin for this division in {esc(label)}.</p>
            <span class="ma-card__unavailable" aria-disabled="true">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.4"/><path d="M4.5 4.5l7 7" stroke="currentColor" stroke-width="1.4"/></svg>
              <span>No document available</span>
            </span>
          </article>''')

        months.append(f'''      <section class="ma-month rv" data-month="{key}">
        <div class="ma-month__header">
          <h3 class="ma-month__name">{esc(label)}</h3>
          <span class="ma-month__count">{len(published_grades)} of 4 divisions published</span>
        </div>
        <div class="ma-grid">
{chr(10).join(cards)}
        </div>
      </section>''')

    return (f'''      <div class="ma-months" id="maGrid">
{chr(10).join(months)}
      </div>
      <p class="ma-none" id="maNone" hidden>No archive bulletins match that search or grade filter.</p>''')


def count():
    return len(CHALLENGES)
