#!/usr/bin/env python3
"""Render CIRS Creative Writing — "The Living Manuscript" — from structured content.

Every edition, poem, presentation and excerpt comes from
creative-writing-content.json (its "_readme" describes each field). This module
supplies layout, navigation and checks, never writing or attribution:

  * an epigraph or "Give me a line" excerpt must appear verbatim in its poem
  * a presentation's size and slide count are read from the file itself
  * an edition's atmosphere is contrast-checked before it is published
  * an edition awaiting the school's poems says so, and shows no count

Pages written from here (all through tools/build-site.py):

  creative-writing.html                   All editions
  creative-writing/junior.html            the same page, Junior School chosen
  creative-writing/senior.html            the same page, Senior School chosen
  creative-writing/<school>/<slug>.html   one edition and its reader

<school> is "anthology" for an edition whose level the school has not yet
confirmed. <slug> is "<month>-<year>" when both are recorded, else the id.
"""

from __future__ import annotations

import html
import json
import os
import re
import zipfile
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTENT_PATH = HERE / "creative-writing-content.json"
TEMPLATE_PATH = HERE / "pages" / "creative-writing.html"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
SCHOOLS = ("junior", "senior")
COLLECTIONS = ("all", "junior", "senior")
SHAPES = ("portrait", "landscape", "square")

# Each edition wears one of these atmospheres. They are meaning — a topic's
# colour — in the way the festival inks are, so they live here, beside the
# data, and are measured before a page is written: ink and soft ink are body
# text (7:1 and 4.5:1), accent is display lettering and rules only (3:1).
MOODS = {
    "dawn":    {"ground": "#F3E7CC", "ink": "#2B2037", "soft": "#574A50", "accent": "#7A5A1F"},
    "dusk":    {"ground": "#392A48", "ink": "#FAF9F3", "soft": "#D6D3CA", "accent": "#FFD75C"},
    "paper":   {"ground": "#EDE7D8", "ink": "#1F1F1B", "soft": "#4E4D47", "accent": "#7A0F1E"},
    "night":   {"ground": "#1E1626", "ink": "#FAF9F3", "soft": "#C9C5BC", "accent": "#FFC308"},
    "meadow":  {"ground": "#DCE6D6", "ink": "#173B27", "soft": "#2E4E38", "accent": "#2E5D3A"},
    "ember":   {"ground": "#7A0F1E", "ink": "#FAF9F3", "soft": "#F2DCD2", "accent": "#FFD75C"},
    "monsoon": {"ground": "#22313A", "ink": "#EEF2F0", "soft": "#BCCBD1", "accent": "#9CC9D8"},
    "chalk":   {"ground": "#1F3B2D", "ink": "#F4F0E6", "soft": "#CAD6C5", "accent": "#FFE7A6"},
    "sky":     {"ground": "#DDE9EE", "ink": "#16303A", "soft": "#344E5A", "accent": "#2F6E86"},
}

# The hero's scattered words. Between them they hold every letter of
# CREATIVE WRITING — "voice" is the only V, "tomorrow" the only W — which is
# what lets cwriting.js assemble the title out of them. Positions are
# percentages of the hero, chosen to keep the centre clear for the cursor.
HERO_WORDS = [
    ("dream",       14, 22, -4, 1.35),
    ("memory",      70, 16,  3, 1.1),
    ("rain",        86, 44, -2, 1.5),
    ("home",        24, 70,  2, 1.2),
    ("silence",     58, 78, -3, 1.3),
    ("courage",     8,  48,  3, 1.05),
    ("tomorrow",    72, 64,  2, 1.25),
    ("imagination", 30, 36, -2, 1.0),
    ("voice",       46, 14,  4, 1.2),
]
HERO_TITLE = ("Creative", "Writing")


def esc(value) -> str:
    return html.escape(str(value), quote=True)


# ---------------------------------------------------------------- checks

def _luminance(hex_colour: str) -> float:
    hex_colour = hex_colour.lstrip("#")
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _verbatim(excerpt: str, poem: dict) -> bool:
    """True when the excerpt's lines run, in order, somewhere in the poem."""
    want = _lines(excerpt)
    have = [line.strip() for stanza in poem["stanzas"] for line in stanza.splitlines()]
    return any(have[i:i + len(want)] == want for i in range(len(have) - len(want) + 1))


def roman(n: int) -> str:
    numerals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for value, letters in numerals:
        while n >= value:
            out, n = out + letters, n - value
    return out


def _size(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f} MB"
    return f"{max(1, round(n / 1024))} KB"


def _ppt(spec) -> dict | None:
    """What a reader needs to know before downloading: read from the file."""
    if not spec:
        return None
    rel = spec["file"] if isinstance(spec, dict) else spec
    if not rel.startswith("assets/") or not rel.lower().endswith((".pptx", ".ppt", ".pdf")):
        raise ValueError(f"Presentation path must be an assets/ .pptx, .ppt or .pdf: {rel}")
    path = ROOT / rel
    if not path.exists():
        raise ValueError(f"Presentation not in the repository: {rel}")
    slides = spec.get("slides") if isinstance(spec, dict) else None
    ext = path.suffix.lower().lstrip(".")
    if ext == "pptx" and slides is None:
        with zipfile.ZipFile(path) as deck:
            slides = sum(1 for name in deck.namelist()
                         if re.fullmatch(r"ppt/slides/slide\d+\.xml", name))
    return {"href": rel, "ext": ext.upper(), "size": _size(path.stat().st_size),
            "slides": slides}


# ---------------------------------------------------------------- the data

@lru_cache(maxsize=1)
def data() -> dict:
    raw = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    seen_ids, seen_urls = set(), set()
    editions = []
    for n, source in enumerate(raw["editions"]):
        e = dict(source)
        eid = e.get("id") or ""
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", eid):
            raise ValueError(f"Edition {n} needs a lower-case id: {eid!r}")
        if eid in seen_ids:
            raise ValueError(f"Duplicate edition id: {eid}")
        seen_ids.add(eid)
        if e.get("school") not in (None, *SCHOOLS):
            raise ValueError(f"{eid}: school must be junior, senior or null")
        if not e.get("topic"):
            raise ValueError(f"{eid}: an edition needs a topic")
        month, year = e.get("month"), e.get("year")
        if month is not None and not 1 <= int(month) <= 12:
            raise ValueError(f"{eid}: month is 1-12")
        status = e.get("status", "published")
        if status not in ("published", "awaiting"):
            raise ValueError(f"{eid}: status is published or awaiting")
        if status == "awaiting" and not raw.get("showAwaiting", True):
            continue
        poems = e.get("poems") or []
        if status == "published" and not poems:
            raise ValueError(f"{eid}: a published edition needs its poems")
        if status == "awaiting" and poems:
            raise ValueError(f"{eid}: an edition with poems is published, not awaiting")

        theme = dict(MOODS.get((e.get("theme") or {}).get("mood") or "paper") or {})
        if not theme:
            raise ValueError(f"{eid}: unknown mood")
        for key in ("ground", "ink", "soft", "accent"):
            if (e.get("theme") or {}).get(key):
                theme[key] = e["theme"][key]
        for key, floor in (("ink", 7), ("soft", 4.5), ("accent", 3)):
            ratio = contrast(theme[key], theme["ground"])
            if ratio < floor:
                raise ValueError(f"{eid}: {key} on ground is {ratio:.2f}:1, below {floor}:1")
        theme["dark"] = _luminance(theme["ground"]) < 0.2
        shape = (e.get("theme") or {}).get("shape") or "portrait"
        if shape not in SHAPES:
            raise ValueError(f"{eid}: shape is portrait, landscape or square")

        poem_ids = set()
        for p in poems:
            pid = p.get("id") or ""
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", pid) or pid in poem_ids:
                raise ValueError(f"{eid}: every poem needs a unique lower-case id ({pid!r})")
            poem_ids.add(pid)
            if not p.get("author") or not p.get("stanzas"):
                raise ValueError(f"{eid}/{pid}: a poem needs an author and stanzas")
            if any(ch.isdigit() for ch in p["author"]):
                raise ValueError(f"{eid}/{pid}: numeric identifier in the author field")
            for line in p.get("lines") or []:
                if not _verbatim(line, p):
                    raise ValueError(f"{eid}/{pid}: excerpt is not verbatim: {line!r}")
        epigraph = e.get("epigraph")
        if epigraph:
            source = next((p for p in poems if p["id"] == epigraph.get("poem")), None)
            if not source or not _verbatim(epigraph["text"], source):
                raise ValueError(f"{eid}: epigraph is not verbatim from its poem")
            epigraph = dict(epigraph, author=source["author"])

        segment = e.get("school") or "anthology"
        slug = e.get("slug") or (f"{MONTHS[month - 1].lower()}-{year}" if month and year else eid)
        path = f"creative-writing/{segment}/{slug}"
        if path in seen_urls:
            raise ValueError(f"{eid}: another edition already lives at /{path}")
        seen_urls.add(path)

        if month and year:
            date, issue = f"{MONTHS[month - 1]} {year}", f"{month:02d} / {year}"
        elif month:
            date, issue = MONTHS[month - 1], MONTHS[month - 1]
        elif year:
            date, issue = str(year), str(year)
        else:
            date, issue = None, None

        e.update(
            order=n, status=status, poems=poems, month=month, year=year, slug=slug,
            segment=segment, path=path, href=f"{path}.html", theme_css=theme,
            shape=shape, date=date, issue=issue, epigraph=epigraph,
            writers=len({p["author"].casefold() for p in poems}),
            ppt=_ppt(e.get("ppt")),
        )
        editions.append(e)
    raw = dict(raw, editions=editions)
    return raw


def editions() -> list[dict]:
    return data()["editions"]


def school_name(key) -> str:
    return data()["schools"][key]["name"] if key in SCHOOLS else ""


def level_label(e: dict) -> str:
    return school_name(e["school"]) or "School level to be confirmed"


def _newest(e: dict):
    return (-(e["year"] or 0), -(e["month"] or 0), e["order"])


def in_collection(collection: str) -> list[dict]:
    """Published first, newest first; an unconfirmed level is listed under All.
    All shows only published editions once there are any: an edition still
    awaiting its poems is listed in its own school's collection and the archive."""
    chosen = [e for e in editions() if collection == "all" or e["school"] == collection]
    if collection == "all" and any(e["status"] == "published" for e in chosen):
        chosen = [e for e in chosen if e["status"] == "published"]
    return sorted(chosen, key=lambda e: (e["status"] != "published", *_newest(e)))


def featured(collection: str) -> dict | None:
    chosen = in_collection(collection)
    if not chosen:
        return None
    return min(chosen, key=lambda e: (not e.get("featured"), e["status"] != "published",
                                      *_newest(e)))


def published_poems():
    for e in editions():
        for n, p in enumerate(e["poems"], 1):
            yield e, n, p


def count() -> int:
    return sum(1 for _ in published_poems())


def writer_count() -> int:
    return len({p["author"].casefold() for _, _, p in published_poems()})


# ---------------------------------------------------------------- fragments

def _style(e: dict) -> str:
    """The edition's atmosphere, and the length of its longest word, which
    the display lettering uses to fit a cover of any width."""
    t = e["theme_css"]
    mark = t["ground"] if t["dark"] else t["ink"]
    longest = max(len(word) for word in e["topic"].split())
    return (f'--ed-ground:{t["ground"]};--ed-ink:{t["ink"]};'
            f'--ed-soft:{t["soft"]};--ed-accent:{t["accent"]};--ed-mark:{mark};'
            f'--lw:{max(longest, 5)}')


def _tone(e: dict) -> str:
    return "dark" if e["theme_css"]["dark"] else "light"


def poem_title(p: dict) -> str:
    return p.get("title") or p["stanzas"][0].splitlines()[0].strip()


def _grade(p: dict) -> str:
    g = p.get("grade")
    if g in (None, ""):
        return ""
    return f"Grade {roman(int(g)) if isinstance(g, int) or str(g).isdigit() else g}"


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def _counts(e: dict) -> str:
    if e["status"] != "published":
        return "Poems to be supplied"
    return f'{_plural(len(e["poems"]), "poem")} · {_plural(e["writers"], "writer")}'


# Junior covers carry a hand-drawn stroke: one path, drawn in the accent.
DOODLES = [
    '<svg class="cw-doodle" viewBox="0 0 120 24" aria-hidden="true" focusable="false"><path pathLength="100" d="M3 15c14-9 25 7 39-1s24-8 36 1 25 4 39-6" /></svg>',
    '<svg class="cw-doodle" viewBox="0 0 120 24" aria-hidden="true" focusable="false"><path pathLength="100" d="M4 12c20 6 40 7 58 2 16-5 34-7 54 1" /><path pathLength="100" d="M20 19c22 3 48 2 78-4" /></svg>',
    '<svg class="cw-doodle" viewBox="0 0 120 24" aria-hidden="true" focusable="false"><path pathLength="100" d="M3 18c8-12 16-12 22 0s14 12 22 0 14-12 22 0 14 12 22 0 12-10 26-4" /></svg>',
]


def cover_html(e: dict, n: int, layout: dict, loading: str = "lazy") -> str:
    """One edition cover on the wall. Typography is the picture."""
    school = e["school"] or "anthology"
    awaiting = e["status"] != "published"
    issue = e["issue"] or ""
    level = level_label(e)
    epigraph = ""
    if e.get("epigraph"):
        epigraph = (f'<span class="cw-cover__epigraph">&ldquo;{esc(e["epigraph"]["text"]).replace(chr(10), " ")}&rdquo;'
                    f'<span class="cw-cover__epigraph-by">{esc(e["epigraph"]["author"])}</span></span>')
    doodle = DOODLES[n % len(DOODLES)] if school == "junior" else ""
    label = f'{e["topic"]}, {e["date"] or "undated"}, {level}. {_counts(e)}.'
    style = (f'{_style(e)};--c-start:{layout["start"]};--c-span:{layout["span"]};'
             f'--c-shift:{layout["shift"]};--m-width:{layout["mwidth"]};--m-align:{layout["malign"]}')
    return f'''      <li class="cw-wall__item cw-wall__item--{e["shape"]}" style="{style}">
        <a class="cw-cover cw-cover--{school} cw-cover--{_tone(e)}{" is-awaiting" if awaiting else ""}" href="{esc(e["href"])}" data-cw-cover>
          <span class="sr-only">{esc(label)} {"View" if awaiting else "Read"} edition</span>
          <span class="cw-cover__face" aria-hidden="true">
            <span class="cw-cover__top"><span class="cw-cover__issue">{esc(issue)}</span><span class="cw-cover__school">{esc(school_name(e["school"]) or "Anthology")}</span></span>
            <span class="cw-cover__topic">{esc(e["topic"])}{doodle}</span>
            {epigraph}
            <span class="cw-cover__meta"><span>{esc(_counts(e))}</span><span>{esc(level)}</span></span>
            <span class="cw-cover__cta">{"View" if awaiting else "Read"} edition <span class="cw-arrow">&rarr;</span></span>
          </span>
        </a>
      </li>'''


SPANS = {"portrait": 4, "square": 5, "landscape": 7}


def wall_layout(items: list[dict]) -> list[dict]:
    """An asymmetric editorial wall: two covers a row on twelve columns, the
    heavier side and the dropped cover alternating row by row, so any mix of
    portrait, landscape and square covers stays balanced without a grid of
    equal cards. Phones get a single varied column instead (m-width/m-align)."""
    out = []
    for r in range(0, len(items), 2):
        row = items[r:r + 2]
        spans = [SPANS[e["shape"]] for e in row]
        if len(row) == 2:
            while sum(spans) > 11:
                i = 0 if spans[0] >= spans[1] else 1
                spans[i] -= 1
            if (r // 2) % 2 == 0:
                starts, shifts = [1, 13 - spans[1]], [0, 1]
            else:
                free = 12 - sum(spans)
                first = 1 + (1 if free >= 3 else 0)
                starts, shifts = [first, 13 - spans[1] - (1 if free >= 4 else 0)], [1, 0]
        else:
            starts = [2 if (r // 2) % 2 == 0 else 13 - spans[0] - 1]
            shifts = [0]
        for i, e in enumerate(row):
            k = r + i
            out.append({
                "start": starts[i], "span": spans[i], "shift": shifts[i],
                "mwidth": {"portrait": "78%", "square": "88%", "landscape": "100%"}[e["shape"]],
                "malign": ("0 auto 0 0" if k % 2 == 0 else "0 0 0 auto")
                          if e["shape"] != "landscape" else "0",
            })
    return out


def wall_html(collection: str) -> str:
    feature = featured(collection)
    items = [e for e in in_collection(collection) if e is not feature]
    if not items:
        return ('<p class="cw-wall__empty">More editions will appear here as the school '
                'publishes them.</p>')
    layout = wall_layout(items)
    covers = "\n".join(cover_html(e, n, layout[n]) for n, e in enumerate(items))
    return f'''    <ol class="cw-wall" aria-label="{esc(_collection_name(collection))} editions">
{covers}
    </ol>'''


def _collection_name(collection: str) -> str:
    return "All" if collection == "all" else school_name(collection)


def featured_html(collection: str) -> str:
    e = featured(collection)
    if not e:
        return ""
    awaiting = e["status"] != "published"
    school = e["school"] or "anthology"
    issue_no = f'No. {e["month"]:02d}' if e["month"] else "Anthology"
    rows = [("Month", e["date"] or "Not recorded"), ("Topic", e["topic"]),
            ("School", level_label(e)),
            ("Poems", str(len(e["poems"])) if not awaiting else "To be supplied")]
    meta = "\n".join(f'          <div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in rows)
    intro = e.get("intro") or ("The poems and presentation for this edition will be "
                               "published here once the school supplies them.")
    epigraph = ""
    if e.get("epigraph"):
        epigraph = (f'<p class="cw-featured__epigraph">&ldquo;{esc(e["epigraph"]["text"]).replace(chr(10), "<br>")}&rdquo;'
                    f'<span>{esc(e["epigraph"]["author"])}</span></p>')
    doodle = DOODLES[0] if school == "junior" else ""
    return f'''    <article class="cw-featured cw-featured--{school} cw-featured--{_tone(e)}" style="{_style(e)}" aria-labelledby="cw-featured-{collection}">
      <a class="cw-featured__cover cw-cover--{school}{" is-awaiting" if awaiting else ""}" href="{esc(e["href"])}" data-cw-cover tabindex="-1" aria-hidden="true">
        <span class="cw-featured__mast">CIRS <em>Creative Writing</em></span>
        <span class="cw-featured__issue"><span>{esc(issue_no)}</span><span>{esc(e["date"] or "")}</span></span>
        <span class="cw-featured__topic">{esc(e["topic"])}{doodle}</span>
        {epigraph}
        <span class="cw-featured__foot"><span>{esc(school_name(e["school"]) or "Anthology")}</span><span>{esc(_counts(e))}</span></span>
      </a>
      <div class="cw-featured__text" data-cw-reveal>
        <p class="cw-eyebrow">Featured edition</p>
        <h3 class="cw-featured__title" id="cw-featured-{collection}">{esc(e["topic"])}</h3>
        <dl class="cw-featured__meta">
{meta}
        </dl>
        <p class="cw-featured__intro">{esc(intro)}</p>
        <a class="cw-featured__read" href="{esc(e["href"])}" data-cw-cover-link>{"View" if awaiting else "Read"} edition <span class="cw-arrow" aria-hidden="true">&rarr;</span></a>
      </div>
    </article>'''


def panels_html(active: str) -> str:
    blocks = []
    for c in COLLECTIONS:
        if c == "all":
            line = ("Every edition, Junior and Senior. Choose a collection to read one "
                    "school&rsquo;s writing.")
        else:
            info = data()["schools"][c]
            line = f'{esc(info["line"])} <span>{esc(info["grades"])}</span>'
        hidden = "" if c == active else " hidden"
        blocks.append(f'''  <div class="cw-panel cw-panel--{c}" id="cw-panel-{c}" data-cw-panel="{c}"{hidden}>
    <p class="wrap cw-panel__line">{line}</p>
    <div class="wrap">
{featured_html(c)}
    </div>
    <div class="wrap cw-panel__wall">
      <h3 class="cw-panel__wall-title" data-cw-reveal>{"More editions" if featured(c) else "Editions"}</h3>
{wall_html(c)}
    </div>
  </div>''')
    return "\n".join(blocks)


def switch_html(active: str) -> str:
    targets = {"all": "creative-writing.html", "junior": "creative-writing/junior.html",
               "senior": "creative-writing/senior.html"}
    names = {"all": "All", "junior": "Junior School", "senior": "Senior School"}
    links = "\n".join(
        f'      <a class="cw-switch__option" href="{targets[c]}#editions" data-cw-pick="{c}"'
        f' aria-controls="cw-panel-{c}"{" aria-current=\"page\"" if c == active else ""}>{names[c]}</a>'
        for c in COLLECTIONS)
    return f'''    <nav class="cw-switch" aria-label="Collections" data-cw-switch>
{links}
      <span class="cw-switch__thumb" aria-hidden="true"></span>
    </nav>'''


def hero_words_html() -> str:
    out = []
    for word, x, y, r, s in HERO_WORDS:
        letters = "".join(f'<span class="cw-l">{esc(ch)}</span>' for ch in word)
        out.append(f'<span class="cw-word" style="--x:{x}%;--y:{y}%;--r:{r}deg;--s:{s}">{letters}</span>')
    return "\n      ".join(out)


def hero_title_html() -> str:
    lines = []
    for n, line in enumerate(HERO_TITLE):
        chars = "".join(f'<span class="cw-ch">{esc(ch)}</span>' for ch in line.upper())
        caret = ('<span class="cw-caret" data-cw-caret></span>'
                 if n == len(HERO_TITLE) - 1 else "")
        lines.append(f'<span class="cw-hero__line cw-hero__line--{n + 1}">{chars}{caret}</span>')
    return (f'<span class="sr-only">{" ".join(HERO_TITLE)}</span>'
            f'<span class="cw-hero__letters" aria-hidden="true">{"".join(lines)}</span>')


def lines_html() -> str:
    """Every stored excerpt, as templates the page draws one from."""
    items = []
    for e, n, p in published_poems():
        for text in p.get("lines") or []:
            body = "<br>".join(esc(line) for line in _lines(text))
            grade = _grade(p)
            edition = f'{e["topic"]}{" · " + e["date"] if e["date"] else ""}'
            items.append(
                f'<figure class="cw-line__quote">'
                f'<blockquote><p>{body}</p></blockquote>'
                f'<figcaption><span class="cw-line__author">{esc(p["author"])}</span>'
                + (f'<span class="cw-line__grade">{esc(grade)}</span>' if grade else "")
                + f'<span class="cw-line__edition">{esc(edition)}</span>'
                f'<a class="cw-line__read" href="{esc(e["href"])}#poem-{esc(p["id"])}">Read poem <span class="cw-arrow" aria-hidden="true">&rarr;</span></a>'
                f'</figcaption></figure>')
    if not items:
        return ""
    return "\n".join(f"<template data-cw-line>{item}</template>" for item in items), items[0]


def archive_html() -> str:
    years = sorted({*data().get("archiveYears", []),
                    *(e["year"] for e in editions() if e["year"])}, reverse=True)
    groups = [(str(y), [e for e in editions() if e["year"] == y]) for y in years]
    undated = [e for e in editions() if not e["year"]]
    if undated:
        groups.append(("Year not recorded", undated))
    rows = []
    for label, items in groups:
        items = sorted(items, key=lambda e: (-(e["month"] or 0), e["order"]))
        if items:
            entries = "\n".join(
                f'''          <li class="cw-archive__entry{" is-awaiting" if e["status"] != "published" else ""}" style="{_style(e)}">
            <a href="{esc(e["href"])}">
              <span class="cw-archive__month">{esc(MONTHS[e["month"] - 1] if e["month"] else "—")}</span>
              <span class="cw-archive__topic">{esc(e["topic"])}</span>
              <span class="cw-archive__school">{esc(school_name(e["school"]) or "Level to be confirmed")}</span>
              <span class="cw-archive__count">{esc(_counts(e))}</span>
              <span class="cw-arrow" aria-hidden="true">&rarr;</span>
            </a>
          </li>''' for e in items)
            body = f'        <ol class="cw-archive__list">\n{entries}\n        </ol>'
        else:
            body = '        <p class="cw-archive__none">Editions from this year are to be added.</p>'
        rows.append(f'''      <div class="cw-archive__year" data-cw-reveal>
        <h3 class="cw-archive__label">{esc(label)}</h3>
{body}
      </div>''')
    return "\n".join(rows)


def legacy_html() -> str:
    """The anthology's old #poem-… and #chapter-… addresses, and where they went."""
    out = []
    for e in editions():
        if e["status"] != "published":
            continue
        out.append(f'<a data-cw-legacy="chapter-{esc(e["id"])}" href="{esc(e["href"])}">{esc(e["topic"])}</a>')
        for p in e["poems"]:
            out.append(f'<a data-cw-legacy="poem-{esc(p["id"])}" href="{esc(e["href"])}#poem-{esc(p["id"])}">{esc(poem_title(p))}</a>')
    return "<template data-cw-legacies>" + "".join(out) + "</template>"


def main_html(active: str) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8").rstrip("\n")
    lines = lines_html()
    templates, first = lines if lines else ("", "")
    return (template
            .replace("{{CW_HERO_WORDS}}", hero_words_html())
            .replace("{{CW_HERO_TITLE}}", hero_title_html())
            .replace("{{CW_SWITCH}}", switch_html(active))
            .replace("{{CW_PANELS}}", panels_html(active))
            .replace("{{CW_ACTIVE}}", active)
            .replace("{{CW_LINES}}", templates)
            .replace("{{CW_FIRST_LINE}}", first)
            .replace("{{CW_ARCHIVE}}", archive_html())
            .replace("{{CW_LEGACY}}", legacy_html() if active == "all" else "")
            .replace("{{CW_COUNT}}", str(count()))
            .replace("{{CW_WRITERS}}", str(writer_count()))
            .replace("{{CW_YEAR}}", str(max((e["year"] or 0) for e in editions()) or "")))


# ---------------------------------------------------------------- an edition

def _stanza(stanza: str) -> str:
    lines = []
    for line in stanza.splitlines():
        indent = len(line) - len(line.lstrip(" "))
        cls = "cw-verse__l cw-verse__l--in" if indent else "cw-verse__l"
        lines.append(f'<span class="{cls}">{esc(line.strip())}</span>')
    return '<p class="cw-verse__stanza">' + "".join(lines) + "</p>"


def _neighbours(e: dict):
    """The editions either side of this one in its own collection."""
    shelf = in_collection(e["school"] or "all")
    if e["school"] is None:
        shelf = [x for x in shelf if x["school"] is None]
    i = shelf.index(e)
    return (shelf[i - 1] if i else None), (shelf[i + 1] if i + 1 < len(shelf) else None)


def presentation_html(e: dict) -> str:
    ppt = e["ppt"]
    school = school_name(e["school"])
    heading = f'{school + " " if school else ""}Creative Writing'
    counts = []
    if e["status"] == "published":
        counts.append(_plural(len(e["poems"]), "poem"))
    if ppt and ppt.get("slides"):
        counts.append(_plural(ppt["slides"], "slide"))
    counts_html = f'<p class="cw-pres__counts">{esc(" · ".join(counts))}</p>' if counts else ""
    if ppt:
        action = (f'<a class="cw-pres__download" href="{esc(ppt["href"])}" download '
                  f'aria-describedby="cw-pres-file">Download Presentation <span class="cw-pres__arrow" aria-hidden="true">&darr;</span></a>'
                  f'<p class="cw-pres__file" id="cw-pres-file">{esc(ppt["ext"])} · {esc(ppt["size"])}</p>')
    else:
        action = ('<p class="cw-pres__pending">The presentation for this edition will be '
                  'available to download here once the school supplies it.</p>')
    return f'''  <section class="cw-pres{" is-pending" if not ppt else ""}" id="presentation" aria-labelledby="cw-pres-title">
    <div class="wrap cw-pres__layout">
      <div class="cw-pres__deck" aria-hidden="true">
        <span class="cw-pres__slide"></span><span class="cw-pres__slide"></span>
        <span class="cw-pres__slide cw-pres__slide--front"><span>{esc(e["topic"])}</span><small>{esc(e["date"] or "")}</small></span>
      </div>
      <div class="cw-pres__text" data-cw-reveal>
        <p class="cw-eyebrow">The Presentation Edition</p>
        <h2 class="cw-pres__title" id="cw-pres-title">{esc(e["topic"])}</h2>
        <p class="cw-pres__date">{esc(e["date"] or "Date not recorded")}</p>
        <p class="cw-pres__school">{esc(heading)}</p>
        {counts_html}
        {action}
      </div>
    </div>
  </section>'''


def edition_html(e: dict) -> str:
    school = e["school"] or "anthology"
    awaiting = e["status"] != "published"
    poems = e["poems"]
    total = len(poems)
    crumbs = [('creative-writing.html', "Creative Writing")]
    if e["school"]:
        crumbs.append((f'creative-writing/{e["school"]}.html', school_name(e["school"])))
    crumb_html = '<span aria-hidden="true">/</span>'.join(
        f'<a href="{href}">{esc(label)}</a>' for href, label in crumbs)
    ppt_chip = ('<a class="cw-open__ppt" href="#presentation">Edition PPT '
                '<span aria-hidden="true">&darr;</span></a>')
    counts = ""
    if not awaiting:
        counts = (f'<p class="cw-open__counts"><span><strong>{e["writers"]}</strong> {"writer" if e["writers"] == 1 else "writers"}</span>'
                  f'<span><strong>{total}</strong> {"poem" if total == 1 else "poems"}</span></p>')
    else:
        counts = '<p class="cw-open__counts cw-open__counts--pending">Poems to be supplied</p>'
    intro = f'<p class="cw-open__intro">{esc(e["intro"])}</p>' if e.get("intro") else ""
    level_note = ("" if e["school"] else
                  '<p class="cw-open__note">School level to be confirmed</p>')
    issue = (f'<p class="cw-open__issue">{esc(e["issue"])}</p>' if e["issue"] else
             '<p class="cw-open__issue cw-open__issue--undated">Date not recorded</p>')
    doodle = DOODLES[0] if school == "junior" else ""

    opening = f'''<header class="cw-open cw-open--{school}" id="top" data-cw-open>
  <div class="wrap cw-open__layout">
    <div class="cw-open__bar">
      <nav class="cw-open__crumbs" aria-label="Breadcrumb">{crumb_html}</nav>
      {ppt_chip}
    </div>
    <div class="cw-open__title">
      {issue}
      <h1 class="cw-open__topic">{esc(e["topic"])}{doodle}</h1>
      <p class="cw-open__kind">Creative Writing Collection</p>
      <p class="cw-open__school">{esc(school_name(e["school"]) or "Anthology")}</p>
      {level_note}
    </div>
    <div class="cw-open__foot">
      {counts}
      {intro}
      <a class="cw-open__begin" href="#reader">{"Begin reading" if not awaiting else "About this edition"} <span aria-hidden="true">&darr;</span></a>
    </div>
  </div>
</header>'''

    if awaiting:
        reader = f'''<section class="cw-reader cw-reader--awaiting" id="reader" aria-labelledby="cw-awaiting-title">
  <div class="wrap cw-awaiting">
    <p class="cw-eyebrow">This edition</p>
    <h2 class="cw-awaiting__title" id="cw-awaiting-title">Awaiting the writers&rsquo; pages.</h2>
    <p>The poems for {esc(e["topic"])}{", " + esc(e["date"]) if e["date"] else ""} will be published here, each with its writer and grade, once the school supplies them.</p>
  </div>
</section>'''
    else:
        index = "\n".join(
            f'          <li><a class="cw-index__link" href="#poem-{esc(p["id"])}" data-cw-goto="{i}"'
            f'{" aria-current=\"true\"" if i == 0 else ""}><span class="cw-index__n">{i + 1:02d}</span>'
            f'<span class="cw-index__t">{esc(poem_title(p))}</span></a></li>'
            for i, p in enumerate(poems))
        articles = []
        for i, p in enumerate(poems):
            prev_p, next_p = (poems[i - 1] if i else None), (poems[i + 1] if i + 1 < total else None)
            nav = []
            if prev_p:
                nav.append(f'<a class="cw-poem__step cw-poem__step--prev" href="#poem-{esc(prev_p["id"])}" rel="prev" data-cw-goto="{i - 1}">'
                           f'<span class="cw-poem__step-label"><span aria-hidden="true">&larr;</span> Previous poem</span>'
                           f'<span class="cw-poem__step-title">{esc(poem_title(prev_p))}</span></a>')
            else:
                nav.append('<span class="cw-poem__step cw-poem__step--prev cw-poem__step--none" aria-hidden="true"></span>')
            if next_p:
                nav.append(f'<a class="cw-poem__step cw-poem__step--next" href="#poem-{esc(next_p["id"])}" rel="next" data-cw-goto="{i + 1}">'
                           f'<span class="cw-poem__step-label">Next poem <span aria-hidden="true">&rarr;</span></span>'
                           f'<span class="cw-poem__step-title">{esc(poem_title(next_p))}</span></a>')
            else:
                nav.append('<a class="cw-poem__step cw-poem__step--next" href="#presentation">'
                           '<span class="cw-poem__step-label">End of the edition <span aria-hidden="true">&darr;</span></span>'
                           '<span class="cw-poem__step-title">The presentation edition</span></a>')
            titled = bool(p.get("title"))
            grade = _grade(p)
            stanzas = "\n".join("          " + _stanza(s) for s in p["stanzas"])
            articles.append(f'''      <article class="cw-poem" id="poem-{esc(p["id"])}" aria-labelledby="poem-{esc(p["id"])}-title" data-cw-poem="{i}">
        <p class="cw-poem__count"><span>{i + 1:02d}</span> / {total:02d}</p>
        {"" if titled else '<p class="cw-poem__untitled">Untitled &middot; first line</p>'}
        <h2 class="cw-poem__title{"" if titled else " cw-poem__title--line"}" id="poem-{esc(p["id"])}-title">{esc(poem_title(p))}</h2>
        <p class="cw-poem__by"><span class="cw-poem__author">{esc(p["author"])}</span>{f'<span class="cw-poem__grade">{esc(grade)}</span>' if grade else ""}</p>
        <div class="cw-verse">
{stanzas}
        </div>
        <nav class="cw-poem__nav" aria-label="Poems either side of {esc(poem_title(p))}">
          {"".join(nav)}
        </nav>
      </article>''')
        reader = f'''<section class="cw-reader" id="reader" aria-label="The poems" data-cw-reader>
  <div class="cw-reader__layout">
    <aside class="cw-rail" id="cw-rail" aria-label="In this edition" data-cw-rail>
      <div class="cw-rail__inner">
        <div class="cw-rail__head">
          <p class="cw-rail__title">{esc(e["topic"])}</p>
          <button class="cw-rail__close" type="button" data-cw-drawer-close>Close <span class="sr-only">the poem index</span></button>
        </div>
        <a class="cw-rail__ppt" href="#presentation">Edition PPT <span aria-hidden="true">&darr;</span></a>
        <div class="cw-progress" data-cw-progress>
          <span class="cw-progress__label"><span data-cw-now>01</span> / {total:02d}</span>
          <span class="cw-progress__track" aria-hidden="true"><span class="cw-progress__fill"></span></span>
        </div>
        <nav class="cw-index" aria-label="Poems in this edition">
          <ol>
{index}
          </ol>
        </nav>
        <p class="cw-rail__keys">Use <kbd>&larr;</kbd> <kbd>&rarr;</kbd> to turn poems</p>
      </div>
    </aside>
    <div class="cw-poems">
{chr(10).join(articles)}
    </div>
  </div>
  <button class="cw-readbar" type="button" aria-controls="cw-rail" aria-expanded="false" data-cw-drawer-open>
    <span class="cw-readbar__label">Poems</span>
    <span class="cw-readbar__count"><span data-cw-now>01</span> / {total:02d}</span>
    <span class="cw-readbar__track" aria-hidden="true"><span class="cw-progress__fill"></span></span>
  </button>
</section>'''

    before, after = _neighbours(e)
    more = []
    for label, other in (("Newer edition", before), ("Earlier edition", after)):
        if other:
            more.append(f'''    <a class="cw-more__link" href="{esc(other["href"])}" style="{_style(other)}" data-cw-cover>
      <span class="cw-more__label">{label}</span>
      <span class="cw-more__topic">{esc(other["topic"])}</span>
      <span class="cw-more__date">{esc(other["date"] or "Date not recorded")} · {esc(_counts(other))}</span>
    </a>''')
    back = (f'creative-writing/{e["school"]}.html#editions' if e["school"]
            else "creative-writing.html#editions")
    more_html = f'''<nav class="cw-more wrap" aria-label="More editions">
  <div class="cw-more__grid">
{chr(10).join(more)}
  </div>
  <a class="cw-more__all" href="{back}">All {esc(school_name(e["school"]) + " " if e["school"] else "")}editions <span class="cw-arrow" aria-hidden="true">&rarr;</span></a>
</nav>'''

    return f'''<div class="cw-edition cw-edition--{school} cw-edition--{_tone(e)}{" is-awaiting" if awaiting else ""}" style="{_style(e)}" data-cw-edition="{esc(e["id"])}">
{opening}
{reader}
{presentation_html(e)}
{more_html}
</div>'''


# ---------------------------------------------------------------- pages

def page_entries() -> dict:
    """The PAGES entries build-site.py adds: the two collection views and
    every edition. None is in MENU; Creative Writing is how a reader reaches them."""
    base = {"sheet": "cwriting", "banner": None, "jump": False, "uc": False,
            "litehead": True, "cache_suffix": "-manuscript-1"}
    pages = {}
    for c in SCHOOLS:
        name = school_name(c)
        pages[f"creative-writing/{c}"] = dict(
            base, nav=f"{name} Creative Writing",
            title=f"{name} Creative Writing | CIRS",
            description=f'{data()["schools"][c]["line"]} Creative writing from the {name} '
                        f"of Chinmaya International Residential School, edition by edition.",
            cw={"kind": "main", "collection": c})
    for e in editions():
        name = school_name(e["school"])
        when = f', {e["date"]}' if e["date"] else ""
        pages[e["path"]] = dict(
            base, nav=esc(e["topic"]),
            # The opening is the edition's own ground: ink lettering on a
            # pale one, the header's light lettering on a dark one.
            litehead=not e["theme_css"]["dark"],
            title=esc(f'{e["topic"]}{when} | {name + " " if name else ""}Creative Writing | CIRS'),
            description=esc((e.get("intro") or f'The {e["topic"]} edition of CIRS Creative Writing.')[:180]),
            cw={"kind": "edition", "edition": e["id"]})
    return pages


def render(spec: dict) -> str:
    if spec["kind"] == "main":
        return main_html(spec["collection"])
    e = next(x for x in editions() if x["id"] == spec["edition"])
    return edition_html(e)


def head_html(spec: dict) -> str:
    """Before first paint: mark the page for its entrances, so nothing below
    the fold is drawn and then hidden. If cwriting.js never runs, the mark is
    taken off again and the whole page shows. The shared curtain is not used
    here; a returning tab's is hidden at once rather than flashed."""
    return ('<script>(function(d){var h=d.documentElement;h.classList.add("cw-js");'
            'try{if(matchMedia("(prefers-reduced-motion: reduce)").matches)h.classList.add("cw-still")}catch(e){}'
            'setTimeout(function(){if(!window.__cwBooted)h.classList.remove("cw-js")},5000)})(document)</script>\n')


if __name__ == "__main__":
    for e in editions():
        print(f'{e["path"]:<48} {e["status"]:<9} {len(e["poems"]):>2} poems  {level_label(e)}')
    print(f"{count()} poems by {writer_count()} writers")
