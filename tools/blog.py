#!/usr/bin/env python3
"""Editorial index and related-story navigation for the CIRS student journal.

The article text and publication metadata live in blogposts.py. This module
only presents that source material and derives counts and reading times from it.
"""

import os
from collections import Counter
from html import escape
from math import ceil

import blogposts


# The earlier PDF lift included several display titles and bylines in article
# paragraphs. These exact fragments were checked against Issues 30, 31 and 32
# before exclusion from reading pages. Issue 17 was corrected at the source.
LAYOUT_ARTIFACTS = {
    "death-of-rationalism": {
        3: ("The Outward Gaze ",),
        8: ("The Of Death Rationalism Rationalism Rationalism Rationalism ",),
    },
    "anakin-skywalker": {
        6: ("Hamartia - The Tyranny of Devotion ",),
        7: ("Aayush S. B. | IB II Yr ",),
        9: ("Anagnorisis - The Ash of ",),
    },
    "sportswashing": {
        4: ("THE TRUTH THE TRUTH A TROPHY Shaurya Bhartia | XII MGMT ",),
    },
    "rumors-at-cirs": {
        3: ("- The Epic Choice ",),
    },
    "hot-wheels-vs-barbie": {
        9: ("Prisha Kantesaria | IB II Year ",),
    },
    "geography-and-geopolitics": {
        7: ("Shaurya Bhartia | 12 Mgmt ",),
    },
}

# Issue 31 prints the end of Rumors alongside a separate article, Itihasa.
# The original text extraction appended that article to the Rumors entry.
ADJACENT_ARTICLE_PARAGRAPHS = {"rumors-at-cirs": {5, 6, 7, 8}}

PRINT_SUBHEADS = {
    "death-of-rationalism": {3: "The Outward Gaze"},
    "anakin-skywalker": {
        6: "Hamartia — The Tyranny of Devotion",
        7: "Peripeteia — The Reversal Born of the Self",
        9: "Anagnorisis — The Ash of Understanding",
        10: "Catharsis — The Terror of Recognition",
    },
}


def esc(value):
    return escape(str(value), quote=True)


def byline(post):
    if not post["author"]:
        return "No byline in print"
    source = post.get("credit_source")
    if source == "site":
        return f"{post['author']} · existing blog credit, no byline in print"
    if source == "school":
        return f"{post['author']} · school-supplied credit, no byline in print"
    return post["author"]


def issue_pdf(post):
    return f"assets/documents/crossroads/crossroads-issue-{post['issue']:02d}.pdf"


def reading_paragraphs(post):
    paragraphs = list(post["paragraphs"])
    for index, fragments in LAYOUT_ARTIFACTS.get(post["slug"], {}).items():
        for fragment in fragments:
            if fragment not in paragraphs[index]:
                raise ValueError(f"Review PDF cleanup for {post['slug']} paragraph {index}")
            paragraphs[index] = paragraphs[index].replace(fragment, "", 1)
    return [paragraph for index, paragraph in enumerate(paragraphs)
            if index not in ADJACENT_ARTICLE_PARAGRAPHS.get(post["slug"], set())]


def body_html(post):
    blocks = []
    subheads = PRINT_SUBHEADS.get(post["slug"], {})
    for index, paragraph in enumerate(reading_paragraphs(post)):
        if index in subheads:
            blocks.append(f'      <h2>{esc(subheads[index])}</h2>')
        blocks.append(f'      <p>{esc(paragraph)}</p>')
    return "\n".join(blocks)


def reading_time(post):
    """Minutes at 220 words per minute, using every published paragraph."""
    prose = sum(len(p.split()) for p in reading_paragraphs(post))
    headings = sum(len(h.split()) for h in PRINT_SUBHEADS.get(post["slug"], {}).values())
    headings += len(post.get("subtitle", "").split())
    return max(1, ceil((prose + headings) / 220))


# The slot each card draws its image in, from assets/css/blognews.css: the
# story list's image column, and the smaller one beside Latest issue's stories.
CARD_SIZES = {
    "story": "(max-width: 425px) 80vw, (max-width: 540px) 340px, "
             "(max-width: 760px) 120px, (max-width: 1000px) 145px, 185px",
    "latest": "(max-width: 540px) 96px, (max-width: 760px) 120px, 110px",
}


def image_html(post, loading="lazy", slot="story"):
    """A card's image: the 400, 800 and 1000px cuts from tools/make-media.py, and
    the article's own image above them, so a card never fetches the
    2000px lead the article page opens on unless a screen needs it."""
    if not post.get("image"):
        return ""
    name = post["image"]
    stem = os.path.splitext(name)[0]
    width = post["image_width"]
    candidates = [f"assets/img/blog/{esc(stem)}-{w}.webp {w}w"
                  for w in (400, 800, 1000) if w < width]
    candidates.append(f"assets/img/blog/{esc(name)} {width}w")
    return (
        f'<img src="assets/img/blog/{esc(name)}" '
        f'srcset="{", ".join(candidates)}" sizes="{CARD_SIZES[slot]}" '
        f'alt="{esc(post.get("image_alt", ""))}" '
        f'width="{post["image_width"]}" height="{post["image_height"]}" '
        f'loading="{loading}" decoding="async">'
    )


def rail_html():
    return """<ul class="ij-nav__list">
      <li><a href="#latest">Latest issue</a></li>
      <li><a href="#stories">All stories</a></li>
      <li><a href="#archive">From the archive</a></li>
      <li><a href="#crossroads-link">Crossroads</a></li>
    </ul>"""


def count():
    return blogposts.count()


def issue_count():
    return len(blogposts.issues())


def _latest():
    latest_issue = max(blogposts.issues())
    posts = [p for p in blogposts.by_issue() if p["issue"] == latest_issue]
    lead = posts[0]
    side = []
    for post in posts[1:]:
        image = (
            f'<a class="ij-latest__image" href="{esc(post["slug"])}.html">'
            f'{image_html(post, slot="latest")}</a>' if post.get("image") else ""
        )
        side.append(f"""<article class="ij-latest__side-story">
          <div class="ij-latest__side-copy">
            <p class="ij-category">{esc(post["section"])}</p>
            <h3><a href="{esc(post["slug"])}.html">{esc(post["title"])}</a></h3>
            <p class="ij-latest__side-meta">{esc(byline(post))}</p>
          </div>
          {image}
        </article>""")
    return f"""<section class="ij-section ij-latest" id="latest" aria-labelledby="ij-latest-title">
      <div class="ij-section__head">
        <div><p class="ij-section__number">01 / The current edition</p>
          <h2 id="ij-latest-title">Latest issue</h2></div>
        <a class="ij-issue-link" href="{issue_pdf(lead)}">Crossroads {latest_issue} <span aria-hidden="true">↗</span></a>
      </div>
      <div class="ij-latest__spread">
        <article class="ij-lead">
          <p class="ij-lead__label">Lead essay <span aria-hidden="true">/</span> {esc(lead["section"])}</p>
          <h3><a href="{esc(lead["slug"])}.html">{esc(lead["title"])}</a></h3>
          <p class="ij-lead__excerpt">{esc(lead["excerpt"])}</p>
          <div class="ij-lead__bottom">
            <span>{esc(byline(lead))}</span>
            <span>{reading_time(lead)} min read</span>
            <a href="{esc(lead["slug"])}.html">Read the essay <span aria-hidden="true">→</span></a>
          </div>
        </article>
        <div class="ij-latest__aside">
          <p class="ij-latest__aside-label">Also in Issue {latest_issue}</p>
          {''.join(side)}
        </div>
      </div>
    </section>"""


def _story_row(post, index):
    image = (
        f'<a class="ij-story__image" href="{esc(post["slug"])}.html" '
        f'aria-label="Read {esc(post["title"])}">{image_html(post)}</a>'
        if post.get("image") else ""
    )
    searchable = " ".join([
        post["title"], post["section"], byline(post),
        f"Issue {post['issue']}", post["excerpt"],
    ])
    row_class = "ij-story" if post.get("image") else "ij-story ij-story--type"
    return f"""<article class="{row_class}" data-story data-category="{esc(post["section"])}"
      data-issue="{post["issue"]}" data-title="{esc(post["title"])}"
      data-order="{index}" data-search="{esc(searchable)}">
      <span class="ij-story__number" aria-hidden="true">{index + 1:02d}</span>
      <div class="ij-story__copy">
        <p class="ij-story__category">{esc(post["section"])}</p>
        <h3><a href="{esc(post["slug"])}.html">{esc(post["title"])}</a></h3>
        <p class="ij-story__excerpt">{esc(post["excerpt"])}</p>
      </div>
      <div class="ij-story__details">
        <span>{esc(byline(post))}</span>
        <a href="{issue_pdf(post)}">Issue {post["issue"]}</a>
        <span>{reading_time(post)} min read</span>
      </div>
      {image}
    </article>"""


def _topics():
    counts = Counter(p["section"] for p in blogposts.POSTS)
    items = [
        f'<button type="button" data-topic="all" aria-pressed="true">'
        f'All <span data-topic-count>{count()}</span></button>'
    ]
    for name in sorted(counts, key=lambda item: (-counts[item], item)):
        items.append(
            f'<button type="button" data-topic="{esc(name)}" aria-pressed="false">'
            f'{esc(name)} <span data-topic-count>{counts[name]}</span></button>'
        )
    return "\n".join(items)


def _stories():
    rows = "\n".join(_story_row(post, i)
                     for i, post in enumerate(blogposts.by_issue()))
    return f"""<section class="ij-section ij-stories" id="stories" aria-labelledby="ij-stories-title" data-journal>
      <div class="ij-section__head">
        <div><p class="ij-section__number">02 / The complete collection</p>
          <h2 id="ij-stories-title">All stories</h2></div>
        <span class="ij-section__aside">{count()} articles across {issue_count()} issues</span>
      </div>
      <div class="ij-discovery" data-discovery hidden>
        <div class="ij-discovery__search">
          <label for="ij-search">Search stories</label>
          <input id="ij-search" type="search" placeholder="Title, author, subject…" autocomplete="off" data-search-input>
        </div>
        <div class="ij-discovery__sort">
          <label for="ij-sort">Sort by</label>
          <select id="ij-sort" data-sort>
            <option value="newest">Newest issue</option>
            <option value="oldest">Oldest issue</option>
            <option value="title">Title A–Z</option>
          </select>
        </div>
      </div>
      <div class="ij-topics" role="group" aria-label="Filter stories by topic" data-topic-controls hidden>
        {_topics()}
      </div>
      <p class="ij-results" role="status" aria-live="polite" data-results>{count()} stories</p>
      <div class="ij-story-list" data-story-list>
        {rows}
      </div>
      <div class="ij-empty" data-empty hidden>
        <h3>No stories found</h3>
        <p>Try another search or topic to see the full collection.</p>
        <button type="button" data-reset>Show all stories</button>
      </div>
    </section>"""


def _archive():
    # These two issue dates are printed in their source magazines.
    slugs = ("the-social-glue", "notes-of-healing")
    posts = {p["slug"]: p for p in blogposts.POSTS}
    entries = []
    for post in (posts[slug] for slug in slugs):
        entries.append(f"""<article class="ij-archive__story">
          <p>{esc(post["date"])} <span aria-hidden="true">/</span> Issue {post["issue"]}</p>
          <h3><a href="{esc(post["slug"])}.html">{esc(post["title"])}</a></h3>
          <p>{esc(post["excerpt"])}</p>
        </article>""")
    return f"""<section class="ij-section ij-archive" id="archive" aria-labelledby="ij-archive-title">
      <div class="ij-section__head">
        <div><p class="ij-section__number">03 / Earlier voices</p>
          <h2 id="ij-archive-title">From the archive</h2></div>
        <span class="ij-section__aside">Also listed above in All stories</span>
      </div>
      <div class="ij-archive__grid">{''.join(entries)}</div>
    </section>"""


def front_html():
    markup = (_latest() + _stories() + _archive() +
              """<section class="ij-connection" id="crossroads-link" aria-labelledby="ij-crossroads-title">
      <div>
        <p class="ij-connection__kicker">Every article began in print</p>
        <h2 id="ij-crossroads-title">The Crossroads</h2>
        <p>Read the complete magazine issues and explore the student publication behind these stories.</p>
      </div>
      <a href="crossroads.html">Explore the magazine archive <span aria-hidden="true">↗</span></a>
    </section>
    <aside class="ij-contact" id="write" aria-labelledby="ij-contact-title">
      <h2 id="ij-contact-title">Write for The Crossroads</h2>
      <p>Students can contact the Crossroads Editorial Board through the school.
        A public submission address, deadline and subscription list are not available here yet.</p>
    </aside>""")
    return "\n".join(line.rstrip() for line in markup.splitlines())


# Category first, then a short subject-based bridge for sections with few posts.
RELATED_BRIDGES = {
    "geography-and-geopolitics": ("sportswashing", "trust-or-bust"),
    "sportswashing": ("geography-and-geopolitics", "the-race-beyond"),
    "the-journey-behind-excellence": ("the-race-beyond", "voyages-in-the-yuva-kendra"),
    "the-race-beyond": ("the-journey-behind-excellence", "trust-or-bust"),
    "trust-or-bust": ("the-race-beyond", "geography-and-geopolitics"),
    "rumors-at-cirs": ("the-social-glue", "my-home"),
    "voyages-in-the-yuva-kendra": ("my-home", "resurgence"),
    "my-home": ("voyages-in-the-yuva-kendra", "rumors-at-cirs"),
    "the-social-glue": ("rumors-at-cirs", "my-home"),
}


def related_for(post):
    by_slug = {item["slug"]: item for item in blogposts.POSTS}
    chosen = [
        item for item in blogposts.by_issue()
        if item["section"] == post["section"] and item["slug"] != post["slug"]
    ]
    for slug in RELATED_BRIDGES.get(post["slug"], ()):
        item = by_slug[slug]
        if item not in chosen and item["slug"] != post["slug"]:
            chosen.append(item)
    return chosen[:3]


def related_html(post):
    items = []
    for item in related_for(post):
        items.append(f"""<li>
          <a href="{esc(item["slug"])}.html">
            <span>{esc(item["section"])} / Issue {item["issue"]}</span>
            <strong>{esc(item["title"])}</strong>
          </a>
        </li>""")
    return f"""<section class="art__related" aria-labelledby="art-related-title">
      <h2 id="art-related-title">Keep reading</h2>
      <ul>{''.join(items)}</ul>
    </section>"""
