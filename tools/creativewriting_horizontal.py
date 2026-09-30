#!/usr/bin/env python3
"""Render the restored horizontal CIRS anthology from the complete collection.

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
    """Use the complete reconciled collection in the restored horizontal design."""
    import creativewriting as cw
    chapters = []
    for edition in cw.in_collection():
        poems = [dict(poem, author=poem.get("author") or "Author not recorded")
                 for poem in edition["poems"]]
        chapters.append(dict(id=edition["id"], title=edition["topic"],
                             month=edition["date_label"], poems=poems))
    return {"chapters": chapters}


def published() -> list[dict]:
    return [poem for chapter in collection()["chapters"] for poem in chapter["poems"]]


def count() -> int:
    return len(published())


def writer_count() -> int:
    import creativewriting as cw
    return cw.writer_count()


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
    """One seamless horizontal row per theme, with every supplied poem."""
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
        repeats = max(1, -(-6 // len(poems)))
        first_half = "\n".join(real_cards + clones * (repeats - 1))
        second_half = "\n".join(clones * repeats)
        direction = "left" if chapter_n % 2 else "right"
        rows.append(f'''<div class="cw-row cw-row--{direction}">
  <div class="wrap cw-row__head">
    <p class="cw-row__eyebrow">{eyebrow}</p>
    <h3 class="cw-row__title"><a href="#chapter-{chapter_id}">{esc(chapter["title"])}</a></h3>
    <p class="cw-row__count">{len(poems)} {"poem" if len(poems) == 1 else "poems"}</p>
  </div>
  <div class="cw-row__window">
    <div class="cw-row__track" style="--cw-row-duration:{12 * repeats * len(poems)}s">
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


# Each chapter's visual identity in the poem reader (assets/css/cwriting.css,
# `[data-cw-design]`). No chapter artwork was ever supplied, so these are drawn
# from the site's own colour roles and paper grain, after the moods the
# collection once recorded for its chapters (dawn, dusk, paper, night, meadow)
# and, for the one chapter that had none, its own title.
CHAPTER_DESIGNS = {
    "joy-of-little-things": "lights",
    "echoes-of-yesterday": "dusk",
    "turning-a-new-page": "paper",
    "refuge-from-reality": "night",
    "lift-yourself-by-yourself": "meadow",
    "the-dawn-of-a-new-era": "sunrise",
}


def _title(poem: dict) -> str:
    return poem.get("title") or _opening(poem)


def _poem_html(poem: dict, chapter: dict, n: int, total_in_chapter: int,
               previous: dict | None, following: dict | None) -> str:
    poem_id = esc(poem["id"])
    title = esc(_title(poem))
    stanzas = "\n".join(
        '<p class="cw-poem__stanza">'
        + "<br>".join(esc(line) for line in stanza.splitlines())
        + "</p>"
        for stanza in poem["stanzas"]
    )
    # Previous and next stay inside the chapter: its first poem has no
    # previous and its last no next, rather than stepping into another theme.
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
    return f'''    <article class="cw-poem" id="poem-{poem_id}" aria-labelledby="poem-{poem_id}-title" data-cw-poem>
      <div class="cw-poem__topline"><span>Poem {n:02d} of {total_in_chapter:02d}</span><span>{"Title" if poem.get("title") else "Opening line"}</span></div>
      <h3 class="cw-poem__title" id="poem-{poem_id}-title">{title}</h3>
      <p class="cw-poem__byline">By <span>{esc(poem["author"])}</span>{" · " + esc(poem["grade"]) if poem.get("grade") else ""}</p>
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


def _contents_html(chapter: dict) -> str:
    """The chapter's poems as a list to choose from, each opening the reader."""
    items = []
    for n, poem in enumerate(chapter["poems"], 1):
        grade = f' <span aria-hidden="true">·</span> {esc(poem["grade"])}' if poem.get("grade") else ""
        items.append(
            f'<li><a class="cw-contents__link" href="#poem-{esc(poem["id"])}">'
            f'<span class="cw-contents__number" aria-hidden="true">{n:02d}</span>'
            f'<span class="cw-contents__title">{esc(_title(poem))}</span>'
            f'<span class="cw-contents__author">By {esc(poem["author"])}{grade}</span>'
            '</a></li>'
        )
    return (f'<ol class="cw-chapter__contents" aria-label="Poems in {esc(chapter["title"])}">'
            + "".join(items) + "</ol>")


def reader_html() -> str:
    """The focused reader: one shell, filled by cwriting.js with a single poem.

    The poems themselves are never copied into it. The script moves the one
    article being read in from its chapter and returns it when the reader
    moves on, so without the script the page is simply the whole anthology.
    """
    return '''<section class="cw-reader" id="reader" aria-labelledby="cw-reader-chapter" data-cw-reader hidden>
  <div class="cw-reader__scene" aria-hidden="true">
    <div class="cw-reader__ground"></div>
    <div class="cw-reader__motif"></div>
    <div class="cw-reader__light"><span></span><span></span></div>
    <div class="cw-reader__quiet"><span></span><span></span></div>
  </div>
  <div class="cw-reader__inner">
    <div class="cw-reader__bar">
      <a class="cw-reader__back" href="#chapters" data-cw-back><span aria-hidden="true">←</span> Back to Chapter</a>
      <div class="cw-reader__settings" role="group" aria-label="Reading settings">
        <button class="cw-switch" type="button" aria-pressed="false" data-cw-mode="design"><span class="cw-switch__track" aria-hidden="true"><span class="cw-switch__knob"></span></span><span class="cw-switch__label">Show Chapter Design</span></button>
        <button class="cw-switch" type="button" aria-pressed="false" data-cw-mode="quiet"><span class="cw-switch__track" aria-hidden="true"><span class="cw-switch__knob"></span></span><span class="cw-switch__label">Quiet Reading</span></button>
      </div>
    </div>
    <header class="cw-reader__chapter">
      <p class="cw-reader__eyebrow" data-cw-reader-eyebrow></p>
      <h2 class="cw-reader__chapter-title" id="cw-reader-chapter" data-cw-reader-chapter>Poem reader</h2>
    </header>
    <div class="cw-reader__stage" data-cw-reader-stage></div>
    <nav class="cw-reader__nav" aria-label="Poems in this chapter">
      <button class="cw-reader__step cw-reader__step--prev" type="button" data-cw-step="-1"><span class="cw-reader__step-dir"><span aria-hidden="true">←</span> Previous Poem</span><span class="cw-reader__step-title" data-cw-step-title></span></button>
      <p class="cw-reader__position" data-cw-position></p>
      <button class="cw-reader__step cw-reader__step--next" type="button" data-cw-step="1"><span class="cw-reader__step-dir">Next Poem <span aria-hidden="true">→</span></span><span class="cw-reader__step-title" data-cw-step-title></span></button>
    </nav>
  </div>
  <p class="cw-sr" role="status" aria-live="polite" aria-atomic="true" data-cw-reader-status></p>
</section>'''


def chapters_html() -> str:
    chapters = collection()["chapters"]
    out = []
    for chapter_n, chapter in enumerate(chapters, 1):
        chapter_id = esc(chapter["id"])
        month = f'<span class="cw-chapter__month">{esc(chapter["month"])}</span>' if chapter.get("month") else ""
        chapter_poems = chapter["poems"]
        poems = []
        for poem_n, poem in enumerate(chapter_poems, 1):
            poems.append(_poem_html(
                poem, chapter, poem_n, len(chapter_poems),
                chapter_poems[poem_n - 2] if poem_n > 1 else None,
                chapter_poems[poem_n] if poem_n < len(chapter_poems) else None,
            ))
        design = CHAPTER_DESIGNS.get(chapter["id"], "paper")
        out.append(f'''<section class="cw-chapter cw-chapter--{chapter_n}" id="chapter-{chapter_id}" aria-labelledby="chapter-{chapter_id}-title" data-cw-chapter data-cw-chapter-number="{chapter_n:02d}" data-cw-design="{design}">
  <div class="cw-chapter__inner">
    <header class="cw-chapter__head" data-cw-reveal>
      <p class="cw-chapter__eyebrow">Chapter {chapter_n:02d} {month}</p>
      <h2 class="cw-chapter__title" id="chapter-{chapter_id}-title">{esc(chapter["title"])}</h2>
      <div class="cw-chapter__details">
        <p class="cw-chapter__count">{len(chapter["poems"])} {"poem" if len(chapter["poems"]) == 1 else "poems"} · {len({p["authorId"] for p in chapter["poems"] if p.get("authorId")})} writers</p>
        <a class="cw-chapter__back" href="#chapters">Back to index <span aria-hidden="true">↗</span></a>
      </div>
    </header>
    {_contents_html(chapter)}
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
