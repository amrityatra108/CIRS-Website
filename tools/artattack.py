"""CIRS Art Attack — the works on the wall, the photographs around them.

Everything here is read from tools/art-attack.json, which tools/make-art-attack.py
writes along with the images, so the site build itself never needs an image
library. The manifest records, for every work, where the image came from and
only what the source itself says about it.

WHAT IS VERIFIED, AND HOW. A work from the Creative Corner of The Crossroads
carries the credit the magazine printed beneath it, as it printed it: the
name (often a first name and an initial) and the class. Nothing is added to
that. No work has a title, a medium or a year of its own in the magazine, so
none is shown; what is shown instead is the issue it appeared in, and that
issue's date as its own cover or contents page prints it (ISSUES below).
The five paintings from the school's archive, the photographs and the two
digital renders stay in the manifest but are not put on the page, which is
for work made by hand (on_page below).

Where a credit could not be read it is left out rather than guessed at. A
work the magazine printed with no credit at all is left off the wall, unless
its page says what it is: the four C20 competition entries in Issue 07 are
shown, uncredited, with the page's own description.

CATEGORIES come from what the magazine's own page shows the work to be —
paper folding is craft, a photograph is a photograph — and never from a
judgement about how good or how finished it looks.

The occasions in the photograph captions come from the name of the folder
each photograph sits in, in the school's Drive; see the "folder" of each.
"""

import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "art-attack.json")
IMG = "assets/img/art-attack"

# Each issue's date as its own cover prints it (and, for 20, 21, 22, 25, 27,
# 30, 31 and 32, its contents page). An issue whose cover names an occasion
# and not a month is shown by that occasion; one whose cover gives no year
# is shown without one. Nothing here is worked out from the issue numbers.
ISSUES = {
    1: "August 2022", 2: "September edition", 3: "Anand Utsav issue",
    4: "November–December 2022", 5: "January–February 2023",
    6: "February–March 2023", 7: "April 2023", 8: "May 2023", 9: "July 2023",
    10: "August 2023", 11: "September 2023", 12: "Anand Utsav issue",
    13: "November–December issue", 14: "January–February 2024",
    15: "March 2024", 16: "April–May 2024", 17: "July 2024",
    18: "August 2024", 19: "September–October 2024",
    20: "November–December 2024", 21: "January 2025", 22: "February 2025",
    23: "April 2025", 24: "May 2025", 25: "July 2025", 26: "Anand Utsav issue",
    27: "November–December 2025", 28: "Pongal issue", 29: "Khel Mela 2026",
    30: "April 2026", 31: "May 2026", 32: "August 2026",
}

def on_page(w):
    """What the page shows: work made by hand, printed in the Creative Corner."""
    return "crossroads" in w["source"] and w["category"] in ("painting", "craft")


# The filters, in the order they are offered. A filter is only offered if
# the collection can fill it; "together" is any work credited to more than
# one person, or to a house.
FILTERS = [
    ("painting", "Painting &amp; drawing"),
    ("craft", "Craft"),
    ("together", "Made together"),
]
MIN_FILTER = 6

# The first thing the page hangs, before the collection: a salon wall of the
# most colourful work, in four rows that each fill the width. A large work
# beside a cluster of six, three works of a size, a run of small ones, and a
# cluster beside another large work. A cluster is a list of two rows. Each
# work on the page appears once, so none of these is repeated in the
# collection below or in the ribbons.
OPENING_WORK = "cc26-27-02"         # the painting the opening's photograph gives way to
HANG = [
    ("lead", ["cc04-12-06",
              [["cc08-25-03", "cc15-23-07", "cc10-23-05"],
               ["cc14-23-01", "cc31-24-06", "cc22-23-10"]]]),
    ("trio", ["cc05-23-02", "cc06-22-03", "cc21-22-01"]),
    ("run", ["cc10-22-06", "cc22-22-01", "cc30-23-04", "cc11-23-08",
             "cc19-22-03", "cc18-23-04", "cc32-23-05"]),
    ("close", [[["cc26-27-03", "cc15-23-02", "cc21-23-04"],
                ["cc13-23-04", "cc28-23-01", "cc11-23-06"]],
               "cc03-12-01"]),
]
# Two bands of colour further down the page, each a line of works that drifts
# sideways as the page scrolls past it (assets/js/artattack.js).
RIBBONS = {
    "warm": ["cc10-23-07", "cc20-23-04", "cc02-12-07", "cc10-23-02", "cc10-23-09",
             "cc08-26-04", "cc22-23-11", "cc25-22-01", "cc31-24-05", "cc21-23-01",
             "cc06-23-03", "cc17-23-02", "cc12-22-06", "cc19-23-05"],
    "cool": ["cc28-23-05", "cc05-22-04", "cc08-25-02", "cc24-22-01", "cc15-22-01",
             "cc16-23-02", "cc20-23-05", "cc07-22-04", "cc21-22-02", "cc07-22-03",
             "cc11-23-02", "cc27-23-03", "cc21-23-06"],
}
FIRST_SHOWN = 30                    # works in the collection before "Show more"

HOUSES = {"Valmiki", "Vasishta", "Vishwamitra", "Vyasa"}


def load():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def esc(text):
    return html.escape(text or "", quote=True)


def grade_label(g):
    """A class as a reader expects it, from however the magazine printed it."""
    if not g:
        return ""
    s = g.strip()
    ib = s.replace("Year", "").replace(" ", "").upper()
    if ib in ("IB1", "IIB", "IBI"):
        return "IB Year 1"
    if ib in ("IB2", "IIIB", "IBII"):
        return "IB Year 2"
    if s.startswith("Alumni "):
        return "Alumni, " + s[len("Alumni "):].replace("-", "–")
    if s in ("Alumnus",) or s.startswith("Grade "):
        return s
    return "Grade " + s


def credit(w):
    """(names, class) — the printed credit, tidied but never extended."""
    people = [p for p in w["people"] if p.get("name")]
    if not people:
        grades = [grade_label(p["grade"]) for p in w["people"] if p.get("grade")]
        return "", grades[0] if grades else ""
    names = [p["name"] for p in people]
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    grades = []
    for p in people:
        g = grade_label(p.get("grade"))
        if g and g not in grades:
            grades.append(g)
    return joined, " · ".join(grades)


def source_line(w):
    src = w["source"]
    if "archive" in src:
        return "From the school’s archive"
    n = src["crossroads"]
    return f"The Crossroads, Issue {n:02d} · {ISSUES[n]}"


def is_together(w):
    names = [p for p in w["people"] if p.get("name")]
    return len(names) > 1 or (w.get("printed") or "") in HOUSES


def cat_of(w):
    return w["category"]


CAT_LABEL = {"painting": "Painting or drawing", "photography": "Photograph",
             "digital": "Digital work", "craft": "Craft"}


def works_by_id(m=None):
    m = m or load()
    return {w["id"]: w for w in m["works"]}


def hang_ids():
    out = []
    for _, items in HANG:
        for item in items:
            out.extend([i for row in item for i in row] if isinstance(item, list) else [item])
    return out


def placed():
    """Works given a place of their own, each once."""
    ids = [OPENING_WORK, *hang_ids(), *(i for r in RIBBONS.values() for i in r)]
    assert len(ids) == len(set(ids)), "a work is placed twice"
    return set(ids)


def collection(m=None):
    """Every work on the page not given a place of its own, newest issue first."""
    m = m or load()
    byid = works_by_id(m)
    for i in placed():
        assert on_page(byid[i]), f"{i} is placed but is not a work for this page"
    taken = placed()
    rest = [w for w in m["works"] if on_page(w) and w["id"] not in taken]
    return sorted(rest, key=lambda w: (-w["source"].get("crossroads", 0), w["id"]))


def count(m=None):
    return sum(1 for w in (m or load())["works"] if on_page(w))


def issue_count(m=None):
    return len({w["source"]["crossroads"] for w in (m or load())["works"] if on_page(w)})


def work_attrs(w):
    """The data the viewer reads. Kept on the link so the page is the manifest."""
    names, grade = credit(w)
    cats = [cat_of(w)] + (["together"] if is_together(w) else [])
    a = {
        "data-aa-work": w["id"],
        "data-w": str(w["size"][0]),
        "data-h": str(w["size"][1]),
        "data-cat": " ".join(cats),
        "data-issue": str(w["source"].get("crossroads", "")),
        "data-kind": CAT_LABEL.get(w["category"], ""),
        "data-source": source_line(w),
    }
    if w.get("title"):
        a["data-title"] = w["title"]
    if names:
        a["data-name"] = names
    if grade:
        a["data-grade"] = grade
    if w.get("note"):
        a["data-note"] = w["note"]
    return " ".join(f'{k}="{esc(v)}"' for k, v in a.items())


def label_html(w, cls="aa-label"):
    names, grade = credit(w)
    title = w.get("title")
    first = f'<span class="{cls}__title">{esc(title)}</span>' if title else ""
    who = f'<span class="{cls}__name">{esc(names)}</span>' if names else ""
    parts = [p for p in (first, who) if p]
    meta = " · ".join(x for x in (grade, (f"Issue {w['source']['crossroads']:02d}" if "crossroads" in w["source"] else "Archive")) if x)
    return (f'<span class="{cls}">' + "".join(parts)
            + f'<span class="{cls}__meta">{esc(meta)}</span></span>')


def work_html(w, cls="aa-work", sizes="(max-width: 700px) 50vw, 22vw", eager=False, hidden=False):
    tw, th = w["thumb"]
    full = f"{IMG}/works/{w['id']}.webp"
    thumb = f"{IMG}/works/{w['id']}-t.webp"
    # The thumb is cut 440px tall; the full image is the viewer's. A work
    # drawn larger than its thumb (the hang) asks for the full image instead.
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    ar = w["size"][0] / w["size"][1]
    return (f'<figure class="{cls}"{" hidden" if hidden else ""} style="--ar:{ar:.4f}">'
            f'<a class="{cls}__link" href="{full}" {work_attrs(w)}>'
            f'<img src="{thumb}" srcset="{thumb} {tw}w, {full} {w["size"][0]}w" sizes="{sizes}" '
            f'width="{tw}" height="{th}" alt="{esc(w["alt"])}" {load} decoding="async">'
            f'</a><figcaption>{label_html(w)}</figcaption></figure>')


def ar_of(w):
    return w["size"][0] / w["size"][1]


def vw(frac, share=0.84):
    """A share of the row as a sizes value; the row is about 84vw wide."""
    return f"{max(8, round(frac * share * 100))}vw"


def hang_html():
    """The salon wall. Every row fills the width and every work keeps its shape.

    Works in a row share one height, so each is as wide as its proportions
    make it (flex-grow by aspect ratio, in the sheet). A cluster beside a
    large work is two such rows stacked; its width is solved here so that the
    cluster, with its captions and gaps, stands exactly as tall as the large
    work beside it with its one caption. With L the large work's height per
    unit of width, K the cluster's (the sum of 1/S over its rows, S being a
    row's summed aspect ratios) and M the gaps inside the cluster's rows
    (the sum of (n - 1)/S), the cluster's width is

        (row - gap) * L/(L+K) + gap * M/(L+K) - (caption + gap) / (L+K)

    which the sheet evaluates, since only it knows the row's width, the gap
    and the caption height (--cp, --cm and --cq are the three fractions)."""
    byid = works_by_id()
    rows = []
    for kind, items in HANG:
        works = [byid[i] for i in items if not isinstance(i, list)]
        clusters = [i for i in items if isinstance(i, list)]
        # The row's width in units of its height, for the sizes estimate.
        units = sum(ar_of(w) for w in works)
        for c in clusters:
            units += 1 / sum(1 / sum(ar_of(byid[i]) for i in r) for r in c)
        wide = kind in ("lead", "close")
        out = []
        for item in items:
            if not isinstance(item, list):
                w = byid[item]
                out.append(work_html(w, "aa-hang__work",
                                     f"(max-width: 760px) {'92vw' if wide else '46vw'}, "
                                     f"{vw(ar_of(w) / units)}"))
                continue
            L = 1 / ar_of(works[0])
            sums = [sum(ar_of(byid[i]) for i in r) for r in item]
            K = sum(1 / S for S in sums)
            M = sum((len(r) - 1) / S for r, S in zip(item, sums))
            P, Q1, Q = L / (L + K), M / (L + K), 1 / (L + K)
            subrows = []
            for r, S in zip(item, sums):
                cell = "\n".join(
                    work_html(byid[i], "aa-hang__work",
                              f"(max-width: 760px) {vw(ar_of(byid[i]) / S, 0.92)}, "
                              f"{vw(ar_of(byid[i]) / S * P)}")
                    for i in r)
                subrows.append(f'<div class="aa-hang__sub">\n{cell}\n</div>')
            out.append(f'<div class="aa-hang__cluster" style="--cp:{P:.4f};--cm:{Q1:.4f};--cq:{Q:.4f}">\n'
                       + "\n".join(subrows) + "\n</div>")
        rows.append(f'<div class="aa-hang__row aa-hang__row--{kind}">\n' + "\n".join(out) + "\n</div>")
    return '<div class="aa-hang">\n' + "\n".join(rows) + "\n</div>"


def ribbon_html(name):
    """A band of works at one height, wider than the window, that drifts."""
    byid = works_by_id()
    figs = []
    for i in RIBBONS[name]:
        w = byid[i]
        a = ar_of(w)
        figs.append(work_html(w, "aa-ribbon__work",
                              f"(max-width: 760px) {round(a * 150)}px, {round(a * 240)}px"))
    label = {"warm": "More from the Creative Corner", "cool": "Still more from the Creative Corner"}[name]
    return (f'<section class="aa-ribbon aa-ribbon--{name}" aria-label="{label}"'
            f' data-aa-ribbon data-dir="{-1 if name == "warm" else 1}">\n'
            '  <div class="aa-ribbon__track" data-aa-track>\n'
            + "\n".join(figs) + "\n  </div>\n</section>")


def filters_html():
    m = load()
    items = collection(m)
    counts = {key: 0 for key, _ in FILTERS}
    for w in items:
        counts[cat_of(w)] = counts.get(cat_of(w), 0) + 1
        if is_together(w):
            counts["together"] += 1
    buttons = [f'<button type="button" class="aa-filter" data-filter="all" aria-pressed="true">'
               f'All <span class="aa-filter__n">{len(items)}</span></button>']
    for key, label in FILTERS:
        if counts.get(key, 0) >= MIN_FILTER:
            buttons.append(f'<button type="button" class="aa-filter" data-filter="{key}" aria-pressed="false">'
                           f'{label} <span class="aa-filter__n">{counts[key]}</span></button>')
    issues = sorted({w["source"]["crossroads"] for w in items if "crossroads" in w["source"]}, reverse=True)
    options = "\n".join(f'          <option value="{n}">Issue {n:02d} · {esc(ISSUES[n])}</option>' for n in issues)
    return f'''<div class="aa-filters" role="group" aria-label="Show works by kind">
        {"".join(buttons)}
      </div>
      <label class="aa-issue">
        <span class="aa-issue__label">Issue</span>
        <select class="aa-issue__select" data-aa-issue>
          <option value="">Every issue</option>
{options}
        </select>
      </label>'''


def wall_html():
    items = collection()
    return "\n".join(work_html(w, hidden=i >= FIRST_SHOWN) for i, w in enumerate(items))


def opening_work_html():
    w = works_by_id()[OPENING_WORK]
    names, grade = credit(w)
    full = f"{IMG}/works/{w['id']}.webp"
    return (f'<a class="aa-open__work" href="{full}" {work_attrs(w)}>'
            f'<img src="{full}" width="{w["size"][0]}" height="{w["size"][1]}" alt="{esc(w["alt"])}" '
            f'fetchpriority="high" decoding="async"></a>'
            f'<p class="aa-open__label"><span class="aa-label__name">{esc(names)}</span>'
            f'<span class="aa-label__meta">{esc(grade)} · {esc(source_line(w))}</span></p>')


def photos_by_id(m=None):
    return {p["id"]: p for p in (m or load())["photos"]}


def photo_html(pid, cls, sizes="(max-width: 700px) 100vw, 60vw", eager=False, caption=True):
    p = photos_by_id()[pid]
    big, small = f"{IMG}/photos/{pid}.webp", f"{IMG}/photos/{pid}-m.webp"
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    img = (f'<img src="{big}" srcset="{small} {p["mobile"][0]}w, {big} {p["size"][0]}w" sizes="{sizes}" '
           f'width="{p["size"][0]}" height="{p["size"][1]}" alt="{esc(p["alt"])}" {load} decoding="async">')
    cap = f'<figcaption>{esc(p["caption"])}</figcaption>' if caption else ""
    return f'<figure class="{cls}">{img}{cap}</figure>'


def expand(content):
    """Fill the page body's placeholders."""
    m = load()
    swaps = {
        "{{AA_OPENING_WORK}}": opening_work_html,
        "{{AA_HANG}}": hang_html,
        "{{AA_FILTERS}}": filters_html,
        "{{AA_WALL}}": wall_html,
        "{{AA_COUNT}}": lambda: str(count(m)),
        "{{AA_RIBBON:warm}}": lambda: ribbon_html("warm"),
        "{{AA_RIBBON:cool}}": lambda: ribbon_html("cool"),
        "{{AA_ISSUE_COUNT}}": lambda: str(issue_count(m)),
        "{{AA_FIRST_SHOWN}}": lambda: str(FIRST_SHOWN),
    }
    for key, fn in swaps.items():
        if key in content:
            content = content.replace(key, fn())
    # {{AA_PHOTO:id:class:sizes[:eager][:nocaption]}}
    import re

    def photo(mo):
        bits = mo.group(1).split("|")
        pid, cls = bits[0], bits[1]
        sizes = bits[2] if len(bits) > 2 and bits[2] else "(max-width: 700px) 100vw, 60vw"
        flags = bits[3:]
        return photo_html(pid, cls, sizes, eager="eager" in flags, caption="nocaption" not in flags)
    return re.sub(r"\{\{AA_PHOTO:([^}]+)\}\}", photo, content)
