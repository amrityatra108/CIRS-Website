#!/usr/bin/env python3
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
    return "\n".join(out)
