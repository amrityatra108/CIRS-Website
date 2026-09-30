#!/usr/bin/env python3
"""The Math Challenge archive: the monthly winners, and the grade divisions.

WHAT THESE PAPERS ARE. They are the school's winners announcements — each
one names the winners for a grade group in a given month and carries their
photographs — and they are not problem papers. The page says so in those
words. Filing them as "the monthly problem" would misdescribe them to every
parent who opened one, and the mathematics department has not supplied the
problems themselves.

They are laid out month by month, the way the school's own Maths Challenge
page lays them out, newest month first. Twenty-five papers across seven
months. Two months are short a grade group; the page lists only the
bulletins that exist and never fills a missing slot.

To add a month: put the PDFs in assets/documents/math-challenge/<yyyy-mm>/
as grades-5-6.pdf and so on, and add the month here. The division rows, the
grade filters, the search and the counts all build from this list.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = "assets/documents/math-challenge"

# The four divisions, in the order they appear on the page. The key is what
# the filter buttons and each record carry in data-grade. The sentence is the
# page's own description of the division; it describes the level, and makes
# no claim about any particular paper.
GRADES = [
    ("5-6",   "Grades 5&ndash;6",
     "Number sense, pattern and logic &mdash; problems that reward noticing "
     "rather than calculating quickly."),
    ("7-8",   "Grades 7&ndash;8",
     "Reasoning stretched further: relationships, geometry and the kind of "
     "puzzle that needs a plan before a pencil."),
    ("9-10",  "Grades 9&ndash;10",
     "Problems that ask a student to connect ideas from different parts of "
     "the syllabus, and to justify the connection."),
    ("11-12", "Grades 11&ndash;12",
     "Sustained problems of the sort that reward a whole evening, and the "
     "habits of mind that higher study asks for."),
]

# The five stages of thinking: general guidance, not a worked problem.
JOURNEY = [
    ("01", "Question",
     "Read it twice. Decide what is actually being asked, and what is only decoration."),
    ("02", "Think",
     "Look for the pattern, the symmetry, the thing that stays the same while everything else moves."),
    ("03", "Explore",
     "Try the small case. Draw it. Guess, then test the guess and find out why it failed."),
    ("04", "Solve",
     "Build the argument step by step, and check that each step follows from the one before it."),
    ("05", "Discover",
     "Ask what the problem was really about &mdash; that is the part that carries to the next one."),
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

LABEL = {key: label for key, label, _ in GRADES}
PLAIN = {key: label.replace("&ndash;", "–") for key, label, _ in GRADES}


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


def size(rel):
    """The PDF's size as a reader would want it said: 1.4 MB, 820 KB."""
    path = os.path.join(ROOT, DOCS, rel)
    n = os.path.getsize(path)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} MB"
    return f"{max(1, round(n / 1000))} KB"


def published(grade):
    return sum(1 for c in CHALLENGES if c["grade"] == grade)


def zones_html():
    """One native-scroll section per division; never relabel results as problems."""
    links = []
    blocks = []
    panels = []
    for i, (key, label, blurb) in enumerate(GRADES, 1):
        links.append(f'<a href="#grade-{key}">{label}</a>')
        blocks.append(f'<div class="mc-stack__block"><span>0{i}</span><strong>{label}</strong></div>')
        papers = "\n".join(
            f'<li><a href="{DOCS}/{c["file"]}" target="_blank" rel="noopener">'
            f'{c["month"]}<span>Winners’ bulletin · PDF · {size(c["file"])} ↗</span></a></li>'
            for c in CHALLENGES if c["grade"] == key)
        panels.append(f'''<section class="mc-grade" id="grade-{key}" aria-labelledby="grade-{key}-title" tabindex="-1">
          <p class="mc-kicker">Division 0{i}</p>
          <h3 id="grade-{key}-title">{label}</h3>
          <p class="mc-grade__intro">{blurb}</p>
          <p class="mc-grade__notice">Grade-specific problem sets have not been supplied. The published documents below announce winners.</p>
          <a class="mc-grade__lab" href="#cube-lab">Explore the 1729 cube challenge →</a>
          <h4>Published results</h4>
          <ul class="mc-grade__papers">{papers}</ul>
          <a class="mc-zone__link" href="#archive" data-grade="{key}">View this division in the results archive →</a>
        </section>''')
    return ('<nav class="mc-grade-nav" aria-label="Choose your grade division">' + "".join(links) + '</nav>'
            '<div class="mc-division-story"><div class="mc-stack" aria-hidden="true">'
            '<div class="mc-stack__layers">' + "".join(blocks) + '</div>'
            '<p>One layer at a time.<br>Four ways to think.</p></div>'
            '<div class="mc-grade-sections">' + "\n".join(panels) + '</div></div>')


def motif(i):
    """A small block figure per row: one, two, three or four stacked tiers,
    drawn from the same bevelled block as the sculpture."""
    blocks = []
    for tier in range(i):
        for col in range(4 - tier):
            x = 16 + col * 22 + tier * 11
            y = 92 - tier * 20
            blocks.append(f'<rect x="{x}" y="{y}" width="18" height="16" rx="2.5"/>')
    return "".join(blocks)


def filters_html():
    """The month search, the division filter, the count and Reset."""
    if not CHALLENGES:
        return ""
    buttons = ['          <button type="button" class="mc-filter" data-grade="all" '
               'aria-pressed="true">All divisions</button>']
    for key, label, _ in GRADES:
        buttons.append(f'          <button type="button" class="mc-filter" data-grade="{key}" '
                       f'aria-pressed="false">{label}</button>')
    months = len(MONTHS)
    return f'''      <div class="mc-tools" id="archive-tools">
        <div class="mc-search">
          <label for="mcSearch">Search by month or year</label>
          <input type="search" id="mcSearch" name="month" placeholder="e.g. April, 2025" autocomplete="off" spellcheck="false">
        </div>
        <div class="mc-filters" role="group" aria-label="Filter the archive by division">
{chr(10).join(buttons)}
        </div>
        <div class="mc-tally">
          <p class="mc-count" id="mcCount" role="status" aria-live="polite">{len(CHALLENGES)} bulletins across {months} months</p>
          <button type="button" class="mc-reset" id="mcReset" hidden>Reset</button>
        </div>
      </div>'''


def archive_html():
    """The winners, month by month: one document row per published bulletin."""
    if not CHALLENGES:
        return '''      <p class="mc-empty">
        <em>[Placeholder &mdash; the monthly winners, to be supplied by the mathematics
        department.]</em>
      </p>'''

    months = []
    for key, label, grades in MONTHS:
        year = key[:4]
        short = label.split()[0][:3].lower()
        rows = []
        for g in grades:
            rel = f"{key}/grades-{g}.pdf"
            rows.append(f'''            <article class="mc-doc" data-grade="{g}">
              <h4 class="mc-doc__grade">{LABEL[g]}</h4>
              <span class="mc-doc__type">Winners&rsquo; bulletin</span>
              <span class="mc-doc__month">{esc(label)}</span>
              <a class="mc-doc__open" href="{DOCS}/{rel}" target="_blank" rel="noopener"
                 aria-label="Open PDF: {esc(label)}, {PLAIN[g]} winners&rsquo; bulletin, {size(rel)} (opens in a new tab)">
                <span class="mc-doc__action">Open PDF</span>
                <span class="mc-doc__size">{size(rel)}</span>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M5 11 11 5M6.5 5H11v4.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </a>
            </article>''')
        n = len(grades)
        months.append(f'''        <div class="mc-month" id="archive-{key}" data-month="{key}"
             data-find="{esc(label.lower())} {short} {key}">
          <div class="mc-month__head">
            <h3 class="mc-month__name">{esc(label)}</h3>
            <p class="mc-month__meta"><span class="mc-month__n">{n}</span> {"bulletin" if n == 1 else "bulletins"}</p>
          </div>
          <div class="mc-docs">
{chr(10).join(rows)}
          </div>
        </div>''')

    return (f'''      <div class="mc-months" id="mcMonths">
{chr(10).join(months)}
      </div>
      <div class="mc-none" id="mcNone" hidden>
        <p class="mc-none__title">No published bulletins match.</p>
        <p class="mc-none__text" id="mcNoneText">Try another month or year, or show every division.</p>
        <button type="button" class="mc-reset mc-reset--big" data-reset>Reset the archive</button>
      </div>''')


def journey_html():
    """The five stages as a compact typographic sequence."""
    return "\n".join(f'''        <li class="mc-step">
          <span class="mc-step__n" aria-hidden="true">{num}</span>
          <h3 class="mc-step__name">{name}</h3>
          <p class="mc-step__text">{text}</p>
        </li>''' for num, name, text in JOURNEY)


def count():
    return len(CHALLENGES)


def month_count():
    return len(MONTHS)
