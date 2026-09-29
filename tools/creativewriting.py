#!/usr/bin/env python3
"""Render CIRS Creative Writing, a student literary journal, from structured content.

Every edition, poem, presentation and excerpt comes from
creative-writing-content.json (its "_readme" describes each field). This module
supplies layout, navigation and checks, never writing or attribution:

  * an epigraph or excerpt must appear verbatim in its poem
  * a presentation's size and slide count are read from the file itself
  * an edition's atmosphere is contrast-checked before it is published
  * an edition awaiting the school's poems says so, and shows no count
  * a field the source does not record (date, level, grade, title,
    presentation) is left out, never guessed

Pages written from here (all through tools/build-site.py):

  creative-writing.html                   All writing: hero, collection, archive
  creative-writing/junior.html            the same page for the Junior School
  creative-writing/senior.html            the same page for the Senior School
  creative-writing/<school>/<slug>.html   one edition, its contents and its poems

<school> is "anthology" for an edition whose level the school has not yet
confirmed. <slug> is "<month>-<year>" when both are recorded, else the id.

The collection is one chronological list. assets/js/cwriting.js lays it out as
two opposing waves on a wide, tall, motion-friendly window and leaves it as an
editorial list everywhere else; the markup here is complete either way.
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

# The two layouts the script adds on top of the list. Kept here, next to the
# markup they belong to; the head script below and cwriting.js repeat them.
SPLIT_QUERY = "(min-width:900px) and (min-height:620px) and (prefers-reduced-motion:no-preference)"
WAVE_QUERY = ("(min-width:1100px) and (min-height:620px) and (prefers-reduced-motion:no-preference)"
              " and (prefers-contrast:no-preference) and (forced-colors:none)")


def _style(e: dict) -> str:
    """The edition's atmosphere, and the length of its longest word, which
    the display lettering uses to fit a title of any width."""
    t = e["theme_css"]
    mark = t["ground"] if t["dark"] else t["ink"]
    longest = max(len(word) for word in e["topic"].split())
    return (f'--ed-ground:{t["ground"]};--ed-ink:{t["ink"]};'
            f'--ed-soft:{t["soft"]};--ed-accent:{t["accent"]};--ed-mark:{mark};'
            f'--lw:{max(longest, 5)}')


def poem_title(p: dict) -> str:
    """The poem's title, or, when the school gave none, its opening line."""
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


def _writers(e: dict) -> list[str]:
    seen, out = set(), []
    for p in e["poems"]:
        if p["author"].casefold() not in seen:
            seen.add(p["author"].casefold())
            out.append(p["author"])
    return out


def _ppt_line(e: dict) -> str:
    """'PPTX · 18 slides · 4.2 MB', from what the file itself says."""
    ppt = e["ppt"]
    if not ppt:
        return ""
    bits = [ppt["ext"]]
    if ppt.get("slides"):
        bits.append(_plural(ppt["slides"], "slide"))
    bits.append(ppt["size"])
    return " · ".join(bits)


def _br(lines: list[str]) -> str:
    """An excerpt's lines, each its own block so a long one can wrap with a
    hanging indent, as it does in the poem."""
    return "".join(f'<span class="cw-l">{esc(line)}</span>' for line in lines)


# ---------------------------------------------------------------- excerpts

def _excerpt(e: dict, p: dict, text: str, key: str) -> dict:
    return {"lines": _lines(text), "author": p["author"], "poem": p["id"], "e": e,
            "key": key, "href": f'{e["href"]}#poem-{p["id"]}'}


def excerpt_pool() -> list[dict]:
    """Every stored excerpt, in edition and poem order. Each was checked
    against its poem when the data was loaded."""
    out = []
    for e, _, p in published_poems():
        for k, text in enumerate(p.get("lines") or []):
            out.append(_excerpt(e, p, text, f'{p["id"]}-{k}'))
    return out


def edition_excerpt(e: dict) -> dict | None:
    """The verbatim lines that stand for an edition: the excerpt that holds
    its epigraph, else the epigraph itself, else the first excerpt stored."""
    pool = [x for x in excerpt_pool() if x["e"] is e]
    epigraph = e.get("epigraph")
    if epigraph:
        want = set(_lines(epigraph["text"]))
        for x in pool:
            if x["poem"] == epigraph["poem"] and want <= set(x["lines"]):
                return x
        poem = next(p for p in e["poems"] if p["id"] == epigraph["poem"])
        return _excerpt(e, poem, epigraph["text"], f'{poem["id"]}-epigraph')
    return pool[0] if pool else None


def hero_quote() -> dict | None:
    """The opening line on the landing page: the featured edition's own."""
    e = featured("all")
    if e and e["status"] == "published":
        x = edition_excerpt(e)
        if x:
            return x
    pool = excerpt_pool()
    return pool[0] if pool else None


def quote_figure(x: dict) -> str:
    """The hero's line with its writer and edition. Where it can be read
    rides along as data-cw-href, for the one "Read this poem" link."""
    e = x["e"]
    when = f'<span class="cw-quote__when">{esc(e["date"])}</span>' if e["date"] else ""
    return (f'<figure class="cw-quote" data-cw-key="{esc(x["key"])}" data-cw-href="{esc(x["href"])}">'
            f'<blockquote class="cw-quote__text"><p>{_br(x["lines"])}</p></blockquote>'
            f'<figcaption class="cw-quote__cap">'
            f'<span class="cw-quote__author">{esc(x["author"])}</span>'
            f'<span class="cw-quote__edition">{esc(e["topic"])}</span>{when}'
            f'</figcaption>'
            f'</figure>')


# ---------------------------------------------------------------- the hero

def _collection_name(collection: str) -> str:
    return "All" if collection == "all" else school_name(collection)


def hero_html(collection: str) -> str:
    if collection != "all":
        info = data()["schools"][collection]
        name = school_name(collection)
        first, _, second = name.partition(" ")
        return f'''<section class="cw-hero cw-hero--compact" id="top" aria-labelledby="cw-title" data-cw-hero>
  <div class="cw-hero__grid">
    <div class="cw-hero__lead">
      <p class="cw-hero__label"><a href="creative-writing.html"><span aria-hidden="true">&larr;</span> All writing</a></p>
      <h1 class="cw-hero__title" id="cw-title"><span class="cw-hero__kicker">Creative Writing</span> <span class="cw-hero__word cw-hero__word--a">{esc(first)}</span> <span class="cw-hero__word cw-hero__word--b">{esc(second)}</span></h1>
    </div>
    <div class="cw-hero__side">
      <p class="cw-hero__line">{esc(info["line"])}</p>
      <p class="cw-hero__grades">{esc(info["grades"])}</p>
      <a class="cw-hero__cue" href="#editions">Explore the writing <span aria-hidden="true">&darr;</span></a>
    </div>
  </div>
</section>'''

    first = hero_quote()
    pool = excerpt_pool()
    side = ""
    if first:
        another = ""
        templates = ""
        if len(pool) >= 2:
            another = ('<button class="cw-hero__another" type="button" data-cw-another hidden>'
                       'Another line <span aria-hidden="true">&#8635;</span></button>')
            templates = "\n      ".join(
                f'<template data-cw-line>{quote_figure(x)}</template>' for x in pool)
        side = f'''    <div class="cw-hero__side" id="give-me-a-line" data-cw-fade>
      <p class="cw-hero__label cw-hero__label--gold">From the collection</p>
      <div class="cw-hero__stage" data-cw-stage>
        {quote_figure(first)}
      </div>
      <div class="cw-hero__actions">
        <a class="cw-quote__read" href="{esc(first["href"])}" data-cw-read>Read this poem <span aria-hidden="true">&rarr;</span></a>
        {another}
      </div>
      <p class="sr-only" role="status" aria-live="polite" data-cw-announce></p>
      {templates}
    </div>'''
    return f'''<div class="cw-zone" data-cw-zone>
<section class="cw-hero" id="top" aria-labelledby="cw-title" data-cw-hero>
  <div class="cw-hero__grid">
    <div class="cw-hero__lead">
      <p class="cw-hero__label" data-cw-fade>CIRS <span aria-hidden="true">&middot;</span> Student writing</p>
      <div class="cw-hero__titleblock">
        <h1 class="cw-hero__title" id="cw-title"><span class="cw-hero__word cw-hero__word--a" data-cw-a>Creative</span> <span class="cw-hero__word cw-hero__word--b" data-cw-b>Writing</span></h1>
        <p class="cw-hero__between" data-cw-between>Two schools. Many voices.</p>
      </div>
      <p class="cw-hero__sub" data-cw-fade>Poetry, stories and thoughts written at CIRS.</p>
      <a class="cw-hero__cue" href="#editions" data-cw-fade>Explore the writing <span aria-hidden="true">&darr;</span></a>
    </div>
{side}
  </div>
</section>
</div>'''


# ---------------------------------------------------------------- the collection

def filter_html(active: str) -> str:
    targets = {"all": "creative-writing.html", "junior": "creative-writing/junior.html",
               "senior": "creative-writing/senior.html"}
    names = {"all": "All writing", "junior": "Junior School", "senior": "Senior School"}
    # The current-page marker is built outside the f-string: a backslash in an
    # f-string expression is a syntax error before Python 3.12, and this file
    # would not import at all on 3.11 — which is what the school's own machines
    # and most shared hosts still run.
    current = ' aria-current="page"'
    links = "\n".join(
        f'      <a class="cw-filter__link" href="{targets[c]}#editions"'
        f'{current if c == active else ""}>{names[c]}</a>'
        for c in COLLECTIONS)
    return f'''    <nav class="cw-filter" aria-label="Collections">
{links}
    </nav>'''


def stats_line(collection: str) -> str:
    items = in_collection(collection)
    published = [e for e in items if e["status"] == "published"]
    if not items:
        return ""
    head = _plural(len(items), "edition")
    if not published:
        return f"{head} · Poems to be supplied"
    poems = sum(len(e["poems"]) for e in published)
    writers = len({p["author"].casefold() for e in published for p in e["poems"]})
    return f'{head} · {_plural(poems, "poem")} · {_plural(writers, "writer")}'


def wave_sides(items: list[dict], collection: str) -> list[dict]:
    """Which column each title sits in, and the grid row it starts on.

    A column is a layout decision and says nothing about a school. Where the
    collection holds both confirmed Junior and confirmed Senior editions, the
    Junior ones lean left and the Senior ones right, and an edition whose
    level is unconfirmed goes to the shorter side. Everywhere else (one
    school's page, or nothing yet confirmed) the titles simply alternate.
    Each title takes two half-rows and the right column starts a half-row
    lower, which is what makes the zigzag."""
    schools = {e["school"] for e in items}
    split = collection == "all" and {"junior", "senior"} <= schools
    taken = {"left": 0, "right": 0}
    out = []
    for n, e in enumerate(items):
        if split and e["school"] in SCHOOLS:
            side = "left" if e["school"] == "junior" else "right"
        elif split:
            side = "left" if taken["left"] <= taken["right"] else "right"
        else:
            side = "left" if n % 2 == 0 else "right"
        k = taken[side]
        taken[side] += 1
        out.append({"side": side, "row": 2 * k + 1 + (side == "right")})
    return out


def wave_item_html(e: dict, n: int, place: dict) -> str:
    x = edition_excerpt(e) if e["status"] == "published" else None
    school = school_name(e["school"])
    when = f'<span class="cw-wave__when">{esc(e["date"])}</span>' if e["date"] else ""
    detail = []
    if school:
        detail.append(f'<p class="cw-wave__school">{esc(school)}</p>')
    if x:
        detail.append(f'<blockquote class="cw-wave__quote"><p>{_br(x["lines"])}</p></blockquote>'
                      f'<p class="cw-wave__by">{esc(x["author"])}</p>')
    elif e["status"] == "published" and e.get("intro"):
        detail.append(f'<p class="cw-wave__intro">{esc(e["intro"])}</p>')
    detail.append(f'<p class="cw-wave__meta">{esc(_counts(e))}</p>')
    if e["ppt"]:
        detail.append(f'<p class="cw-wave__ppt">Presentation &middot; {esc(_ppt_line(e))}</p>')
    actions = []
    if x:
        actions.append(f'<a class="cw-wave__read" href="{esc(x["href"])}">Read poem '
                       f'<span aria-hidden="true">&rarr;</span></a>')
    actions.append(f'<a class="cw-wave__open" href="{esc(e["href"])}">'
                   f'{"Open edition" if e["status"] == "published" else "View edition"}</a>')
    detail.append(f'<div class="cw-wave__actions">{"".join(actions)}</div>')
    body = "\n        ".join(detail)
    return f'''      <li class="cw-wave__item" style="{_style(e)};--r:{place["row"]}" data-cw-item data-side="{place["side"]}">
        <p class="cw-wave__kicker"><span class="cw-wave__no">{n + 1:02d}</span>{when}</p>
        <a class="cw-wave__link" href="{esc(e["href"])}" data-cw-open data-cw-title><span class="cw-wave__title">{esc(e["topic"])}</span></a>
        <div class="cw-wave__detail" data-cw-detail>
        {body}
        </div>
      </li>'''


def wave_html(collection: str) -> str:
    items = in_collection(collection)
    if not items:
        return ('<p class="wrap cw-wave__empty">More editions will appear here as the '
                'school publishes them.</p>')
    places = wave_sides(items, collection)
    rows = max(p["row"] for p in places) + 1
    lis = "\n".join(wave_item_html(e, n, places[n]) for n, e in enumerate(items))
    return f'''  <div class="cw-wave" data-cw-wave>
    <ol class="cw-wave__list" style="--rows:{rows}" aria-label="{esc(_collection_name(collection))} editions, newest first">
{lis}
    </ol>
    <div class="cw-wave__stage">
      <div class="cw-wave__pin">
        <section class="cw-preview" aria-label="Selected edition" data-cw-preview>
          <div class="cw-preview__body" data-cw-preview-body></div>
        </section>
      </div>
    </div>
  </div>'''


# ---------------------------------------------------------------- featured

def featured_picks(collection: str, limit: int = 3) -> list[dict]:
    """Published editions, the featured ones first, then in the order the
    school's data lists them (which makes no claim about recency)."""
    pool = [e for e in in_collection(collection) if e["status"] == "published"]
    return sorted(pool, key=lambda e: (not e.get("featured"), e["order"]))[:limit]


def featured_html(collection: str) -> str:
    picks = featured_picks(collection)
    if not picks:
        return ""
    entries = []
    for n, e in enumerate(picks):
        x = edition_excerpt(e)
        quote = ""
        if x:
            quote = (f'<blockquote class="cw-feature__quote"><p>{_br(x["lines"])}</p>'
                     f'<footer>{esc(x["author"])}</footer></blockquote>')
        intro = f'<p class="cw-feature__intro">{esc(e["intro"])}</p>' if e.get("intro") else ""
        when = f'<p class="cw-feature__when">{esc(e["date"])}</p>' if e["date"] else ""
        school = school_name(e["school"])
        tag = f'<p class="cw-feature__school">{esc(school)}</p>' if school else ""
        size = "large" if n % 2 == 0 else "small"
        entries.append(f'''      <li class="cw-feature cw-feature--{size}" style="{_style(e)}">
        {when}
        <h3 class="cw-feature__title" data-cw-title><a href="{esc(e["href"])}" data-cw-open><span>{esc(e["topic"])}</span></a></h3>
        {tag}
        <p class="cw-feature__writers">{esc(", ".join(_writers(e)))}</p>
        {quote}
        {intro}
        <a class="cw-feature__read" href="{esc(e["href"])}">Open edition <span aria-hidden="true">&rarr;</span></a>
      </li>''')
    body = "\n".join(entries)
    return f'''<section class="cw-featured" id="featured" aria-labelledby="cw-featured-title">
  <div class="wrap">
    <header class="cw-featured__head">
      <p class="cw-eyebrow">Featured editions</p>
      <h2 class="cw-featured__title" id="cw-featured-title" data-cw-slice>Voices</h2>
    </header>
    <ol class="cw-featured__list">
{body}
    </ol>
  </div>
</section>'''


# ---------------------------------------------------------------- archive

def archive_html(collection: str) -> str:
    pool = [e for e in editions() if collection == "all" or e["school"] == collection]
    years = sorted({*data().get("archiveYears", []), *(e["year"] for e in pool if e["year"])},
                   reverse=True)
    groups = [(str(y), [e for e in pool if e["year"] == y]) for y in years]
    undated = [e for e in pool if not e["year"]]
    if undated:
        groups.append(("Year not recorded", undated))
    out = []
    for n, (label, items) in enumerate(groups):
        items = sorted(items, key=lambda e: (-(e["month"] or 0), e["order"]))
        if items:
            rows = []
            for e in items:
                month = MONTHS[e["month"] - 1][:3] if e["month"] else "&ndash;"
                level = school_name(e["school"]) or "Level to be confirmed"
                ppt = (f'<a class="cw-archive__ppt" href="{esc(e["ppt"]["href"])}" download>'
                       f'Presentation &middot; {esc(_ppt_line(e))}</a>') if e["ppt"] else ""
                rows.append(f'''          <li class="cw-archive__row{" is-awaiting" if e["status"] != "published" else ""}" style="{_style(e)}">
            <a class="cw-archive__link" href="{esc(e["href"])}" data-cw-open>
              <span class="cw-archive__month">{month}</span>
              <span class="cw-archive__topic" data-cw-title>{esc(e["topic"])}</span>
              <span class="cw-archive__level">{esc(level)}</span>
              <span class="cw-archive__count">{esc(_counts(e))}</span>
              <span class="cw-archive__go" aria-hidden="true">&rarr;</span>
            </a>{ppt}
          </li>''')
            body = ('        <ol class="cw-archive__list">\n' + "\n".join(rows) + "\n        </ol>")
        else:
            body = '        <p class="cw-archive__none">Editions from this year are to be added.</p>'
        note = "" if label.isdigit() else " cw-archive__label--note"
        out.append(f'''      <section class="cw-archive__year" aria-labelledby="cw-year-{n}">
        <h3 class="cw-archive__label{note}" id="cw-year-{n}">{esc(label)}</h3>
{body}
      </section>''')
    return "\n".join(out)


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
    return (template
            .replace("{{CW_ACTIVE}}", active)
            .replace("{{CW_HERO}}", hero_html(active))
            .replace("{{CW_STATS}}", esc(stats_line(active)))
            .replace("{{CW_FILTER}}", filter_html(active))
            .replace("{{CW_WAVE}}", wave_html(active))
            .replace("{{CW_FEATURED}}", featured_html(active))
            .replace("{{CW_ARCHIVE}}", archive_html(active))
            .replace("{{CW_LEGACY}}", legacy_html() if active == "all" else ""))


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


def _download(e: dict) -> str:
    """The presentation link, or nothing: an edition without one shows no control."""
    if not e["ppt"]:
        return ""
    return (f'<a class="cw-head__download" href="{esc(e["ppt"]["href"])}" download>'
            f'<span class="cw-head__download-label">Download presentation '
            f'<span aria-hidden="true">&darr;</span></span>'
            f'<span class="cw-head__download-file">{esc(_ppt_line(e))}</span></a>')


def edition_html(e: dict) -> str:
    school = e["school"] or "anthology"
    awaiting = e["status"] != "published"
    poems = e["poems"]
    total = len(poems)
    back = (f'creative-writing/{e["school"]}.html#editions' if e["school"]
            else "creative-writing.html#editions")
    # In-page links carry the page's own address. The shared script scrolls
    # every href="#…" itself and leaves no history entry; an address with the
    # page's path is the browser's own same-document navigation, so the
    # address changes, Back and Forward walk the poems, and a refresh lands
    # where the reader was.
    here = esc(e["href"])

    crumbs = ['<li><a href="creative-writing.html">Creative Writing</a></li>']
    if e["school"]:
        crumbs.append(f'<li><a href="creative-writing/{e["school"]}.html">{esc(school_name(e["school"]))}</a></li>')
    crumbs.append(f'<li><span aria-current="page">{esc(e["date"] or e["topic"])}</span></li>')

    facts = []
    if awaiting:
        facts.append('<li>Poems to be supplied</li>')
    else:
        facts.append(f'<li><strong>{e["writers"]}</strong> {"writer" if e["writers"] == 1 else "writers"}</li>')
        facts.append(f'<li><strong>{total}</strong> {"poem" if total == 1 else "poems"}</li>')
    facts.append(f'<li>{esc(school_name(e["school"]))}</li>' if e["school"]
                 else '<li>School level to be confirmed</li>')
    intro = f'<p class="cw-head__intro">{esc(e["intro"])}</p>' if e.get("intro") else ""

    head = f'''<header class="cw-head" id="top">
  <div class="wrap cw-head__wrap">
    <nav class="cw-head__crumbs" aria-label="Breadcrumb"><ol>{"".join(crumbs)}</ol></nav>
    <h1 class="cw-head__title" data-cw-title>{esc(e["topic"])}</h1>
    {intro}
    <ul class="cw-head__facts">{"".join(facts)}</ul>
    {_download(e)}
  </div>
</header>'''

    if awaiting:
        body = f'''<section class="cw-awaiting" id="contents" aria-labelledby="cw-awaiting-title">
  <div class="wrap cw-awaiting__wrap">
    <h2 class="cw-awaiting__title" id="cw-awaiting-title">Awaiting the writers&rsquo; pages.</h2>
    <p>The poems for {esc(e["topic"])}{", " + esc(e["date"]) if e["date"] else ""} will be published here, each with its writer and grade, once the school supplies them.</p>
  </div>
</section>'''
    else:
        contents = "\n".join(
            f'''      <li><a class="cw-contents__link" href="{here}#poem-{esc(p["id"])}">
        <span class="cw-contents__no">{i + 1:02d}</span>
        <span class="cw-contents__who">{esc(p["author"])}</span>
        <span class="cw-contents__what">{esc(poem_title(p))}</span>
        <span class="cw-contents__go" aria-hidden="true">&rarr;</span>
      </a></li>''' for i, p in enumerate(poems))
        articles = []
        for i, p in enumerate(poems):
            prev_p = poems[i - 1] if i else None
            next_p = poems[i + 1] if i + 1 < total else None
            if prev_p:
                prev = (f'<a class="cw-poem__step cw-poem__step--prev" href="{here}#poem-{esc(prev_p["id"])}" rel="prev">'
                        f'<span class="cw-poem__step-label"><span aria-hidden="true">&larr;</span> Previous poem</span>'
                        f'<span class="cw-poem__step-name">{esc(prev_p["author"])}</span></a>')
            else:
                prev = '<span class="cw-poem__step cw-poem__step--none" aria-hidden="true"></span>'
            if next_p:
                nxt = (f'<a class="cw-poem__step cw-poem__step--next" href="{here}#poem-{esc(next_p["id"])}" rel="next">'
                       f'<span class="cw-poem__step-label">Next poem <span aria-hidden="true">&rarr;</span></span>'
                       f'<span class="cw-poem__step-name">{esc(next_p["author"])}</span></a>')
            else:
                nxt = (f'<a class="cw-poem__step cw-poem__step--next" href="{here}#more">'
                       '<span class="cw-poem__step-label">End of the edition <span aria-hidden="true">&darr;</span></span>'
                       '<span class="cw-poem__step-name">More editions</span></a>')
            titled = bool(p.get("title"))
            grade = _grade(p)
            byline = ""
            if titled:
                byline += f'<p class="cw-poem__author">{esc(p["author"])}</p>'
            if grade:
                byline += f'<p class="cw-poem__grade">{esc(grade)}</p>'
            stanzas = "\n".join("          " + _stanza(s) for s in p["stanzas"])
            name_cls = "cw-poem__name" + ("" if titled else " cw-poem__name--writer")
            articles.append(f'''      <article class="cw-poem" id="poem-{esc(p["id"])}" aria-labelledby="poem-{esc(p["id"])}-name" data-cw-poem data-cw-n="{i + 1:02d}" data-cw-who="{esc(p["author"])}">
        <header class="cw-poem__head">
          <p class="cw-poem__meta"><span>{esc(e["topic"])}</span><span>{i + 1:02d} / {total:02d}</span></p>
          <h2 class="{name_cls}" id="poem-{esc(p["id"])}-name">{esc(poem_title(p) if titled else p["author"])}</h2>
          {byline}
        </header>
        <div class="cw-verse">
{stanzas}
        </div>
        <nav class="cw-poem__nav" aria-label="After the poem by {esc(p["author"])}">
          {prev}
          <a class="cw-poem__contents" href="{here}#contents">Contents</a>
          {nxt}
        </nav>
      </article>''')
        rail_ppt = f'<a class="cw-rail__link" href="{here}#presentation">Presentation</a>' if e["ppt"] else ""
        rail_back = f'All {esc(school_name(e["school"]))}' if e["school"] else "All writing"
        rail_when = f'<p class="cw-rail__when">{esc(e["date"])}</p>' if e["date"] else ""
        body = f'''<section class="cw-contents" id="contents" aria-labelledby="cw-contents-title">
  <div class="wrap">
    <h2 class="cw-contents__label" id="cw-contents-title">Contents</h2>
    <ol class="cw-contents__list">
{contents}
    </ol>
  </div>
</section>

<div class="cw-reading" id="reader" data-cw-reading>
  <div class="cw-reading__layout">
    <aside class="cw-rail" aria-label="Edition navigation">
      <div class="cw-rail__inner">
        <a class="cw-rail__back" href="{back}"><span aria-hidden="true">&larr;</span> {rail_back}</a>
        <p class="cw-rail__title">{esc(e["topic"])}</p>
        {rail_when}
        <p class="cw-rail__now" aria-hidden="true"><span class="cw-rail__count"><span data-cw-now>01</span> / {total:02d}</span><span class="cw-rail__who">{esc(poems[0]["author"])}</span></p>
        <a class="cw-rail__link" href="{here}#contents">Contents</a>
        {rail_ppt}
      </div>
    </aside>
    <div class="cw-poems">
{chr(10).join(articles)}
    </div>
  </div>
</div>'''

    pres = ""
    if e["ppt"]:
        pres = f'''
<section class="cw-pres" id="presentation" aria-labelledby="cw-pres-title">
  <div class="wrap cw-pres__wrap">
    <h2 class="cw-pres__title" id="cw-pres-title">Presentation</h2>
    {_download(e)}
  </div>
</section>'''

    before, after = _neighbours(e)
    more = []
    for label, other in (("Newer edition", before), ("Earlier edition", after)):
        if other:
            more.append(f'''      <li><a class="cw-more__link" href="{esc(other["href"])}" style="{_style(other)}" data-cw-open>
        <span class="cw-more__label">{label}</span>
        <span class="cw-more__topic" data-cw-title>{esc(other["topic"])}</span>
        <span class="cw-more__meta">{esc(" · ".join(x for x in (other["date"], _counts(other)) if x))}</span>
      </a></li>''')
    more_list = f'    <ul class="cw-more__list">\n{chr(10).join(more)}\n    </ul>\n' if more else ""
    all_name = (esc(school_name(e["school"])) + " ") if e["school"] else ""
    more_html = f'''<nav class="cw-more" id="more" aria-labelledby="cw-more-title">
  <div class="wrap">
    <h2 class="cw-more__heading" id="cw-more-title">More editions</h2>
{more_list}    <a class="cw-more__all" href="{back}">All {all_name}editions <span aria-hidden="true">&rarr;</span></a>
  </div>
</nav>'''

    return f'''<div class="cw-edition cw-edition--{school}{" is-awaiting" if awaiting else ""}" style="{_style(e)}" data-cw-edition="{esc(e["id"])}">
{head}
{body}{pres}
{more_html}
</div>'''


# ---------------------------------------------------------------- pages

def page_entries() -> dict:
    """The PAGES entries build-site.py adds: the two collection views and
    every edition. None is in MENU; Creative Writing is how a reader reaches them."""
    base = {"sheet": "cwriting", "banner": None, "jump": False, "uc": False,
            "cache_suffix": "-journal-1"}
    pages = {}
    for c in SCHOOLS:
        name = school_name(c)
        pages[f"creative-writing/{c}"] = dict(
            base, nav=f"{name} Creative Writing", litehead=False,
            title=f"{name} Creative Writing | CIRS",
            description=f'{data()["schools"][c]["line"]} Creative writing from the {name} '
                        f"of Chinmaya International Residential School, edition by edition.",
            cw={"kind": "main", "collection": c})
    for e in editions():
        name = school_name(e["school"])
        when = f', {e["date"]}' if e["date"] else ""
        pages[e["path"]] = dict(
            base, nav=esc(e["topic"]),
            # Every edition opens on the site's ivory, with its own colour as
            # a restrained accent, so the header letters in ink.
            litehead=True,
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
    """Before first paint: mark the page for the layouts the script will add,
    so a reload part-way down does not jump when the script arrives. If
    cwriting.js never runs, every mark is taken off again and the page is
    the plain, complete document it was written as."""
    marks = ""
    if spec["kind"] == "main":
        wave = f'if(w.matchMedia("{WAVE_QUERY}").matches)h.classList.add("cw-wave-on");'
        split = (f'if(w.matchMedia("{SPLIT_QUERY}").matches)h.classList.add("cw-split-on");'
                 if spec["collection"] == "all" else "")
        marks = f"{split}{wave}"
    return ('<script>(function(d,w){var h=d.documentElement;h.classList.add("cw-js");'
            f'try{{{marks}}}catch(e){{}}'
            'setTimeout(function(){if(!w.__cwBooted)h.classList.remove("cw-js","cw-split-on","cw-wave-on")},5000)})(document,window)</script>\n')


if __name__ == "__main__":
    for e in editions():
        print(f'{e["path"]:<48} {e["status"]:<9} {len(e["poems"]):>2} poems  {level_label(e)}')
    print(f"{count()} poems by {writer_count()} writers")
