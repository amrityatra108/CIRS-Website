#!/usr/bin/env python3
"""Editorial index and related-story navigation for the CIRS student journal.

The article text and publication metadata live in blogposts.py. This module
only presents that source material and derives counts and reading times from it.
"""

import os
import re
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


def display_byline(post):
    """The credit readers see, on the front page and the article page alike.
    Where a credit came from (credit_source: the school, or the old blog,
    because the issue prints none) stays in POSTS and tools/blog-inventory.csv;
    it is a note for whoever maintains the page, not part of the byline."""
    return post["author"] or "No byline in print"


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
        # A poem's stanza keeps its line breaks (blogposts.verse); a paragraph
        # of prose has none.
        blocks.append(f'      <p>{esc(paragraph).replace(chr(10), "<br>")}</p>')
    return "\n".join(blocks)


def reading_time(post):
    """Minutes at 220 words per minute, using every published paragraph."""
    prose = sum(len(p.split()) for p in reading_paragraphs(post))
    headings = sum(len(h.split()) for h in PRINT_SUBHEADS.get(post["slug"], {}).values())
    headings += len(post.get("subtitle", "").split())
    return max(1, ceil((prose + headings) / 220))


CARD_SIZES = {
    "story": "(max-width: 600px) 90vw, (max-width: 1000px) 60vw, (max-width: 1440px) 65vw, 1000px",
    "latest": "(max-width: 600px) 30vw, 140px",
    "feature": "(max-width: 600px) 78vw, (max-width: 1000px) 46vw, (max-width: 1440px) 37vw, 540px",
    "narrow": "(max-width: 600px) 44vw, (max-width: 1440px) 28vw, 400px",
    "world": "(max-width: 600px) 90vw, (max-width: 1000px) 60vw, (max-width: 1440px) 61vw, 890px",
    "spread": "(max-width: 600px) 90vw, (max-width: 1000px) 60vw, 46vw",
    "rail": "(max-width: 600px) 90vw, (max-width: 1000px) 30vw, 440px",
    "card": "(max-width: 600px) 72vw, 280px",
}

# All stories shows every picture in one 4:3 box. These are cut away from its
# centre to keep what the picture is of; a banner too wide for the box to crop
# without losing its lettering is shown whole inside it.
CARD_FOCUS = {
    "the-cirs-effect": "50% 6%",
    "the-dancing-parasite": "50% 0%",
    "the-social-glue": "0% 50%",
    "death-of-detail": "100% 50%",
}
CARD_WHOLE = {"when-fomo-becomes-expensive"}


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
        f'<img src="assets/img/blog/{esc(stem) + "-400.webp" if width > 400 else esc(name)}" '
        f'srcset="{", ".join(candidates)}" sizes="{CARD_SIZES[slot]}" '
        f'alt="{esc(post.get("image_alt", ""))}" '
        f'width="{post["image_width"]}" height="{post["image_height"]}" '
        f'loading="{loading}" decoding="async">'
    )


def rail_html():
    return """<ul class="ij-nav__list">
      <li><a href="#latest">Latest issue</a></li>
      <li><a href="#campus-culture">Campus &amp; culture</a></li>
      <li><a href="#world-sport">World &amp; sport</a></li>
      <li><a href="#stories">All stories</a></li>
      <li><a href="#archive">From the archive</a></li>
    </ul>"""


def count():
    return blogposts.count()


def issue_count():
    return len(blogposts.issues())


def image_role(post):
    ratio = post.get('image_width', 1) / post.get('image_height', 1)
    return 'portrait' if ratio < .85 else 'cinematic' if ratio > 2.3 else 'square' if ratio < 1.15 else 'wide'


def editorial_photo(post, *, loading="lazy", slot="feature", caption=True):
    if not post.get("image"):
        return ""
    credit = post.get("image_caption", "") if caption else ""
    caption_html = f"<figcaption>{esc(credit)}</figcaption>" if credit else ""
    ratio = post['image_width'] / post['image_height']
    return f'''<figure class="ij-photo" data-image-role="{image_role(post)}" style="--native-width:{post['image_width']}px;--ratio:{ratio:.4f}">
      <a href="{esc(post['slug'])}.html" aria-label="Read {esc(post['title'])}">{image_html(post, loading=loading, slot=slot)}</a>
      {caption_html}</figure>'''


def editorial_meta(post):
    date = f" / {esc(post['date'])}" if post.get("date") else ""
    return f"Issue {post['issue']}{date}"


def article_module(post, variant, *, image=True, excerpt=True, heading="h3", slot=None):
    slot = slot or {"image-feature": "spread", "world-feature": "world", "narrow": "narrow"}.get(variant, "latest")
    photo = editorial_photo(post, slot=slot, caption=variant == "image-feature") if image else ""
    deck = f'<p class="ij-deck">{esc(post["excerpt"])}</p>' if excerpt else ""
    return f'''<article class="ij-module ij-module--{variant}">
      <p class="ij-kicker">{esc(post['section'])}</p>
      {photo}
      <{heading}><a href="{esc(post['slug'])}.html">{esc(post['title'])}</a></{heading}>
      {deck}
      <p class="ij-byline">{esc(display_byline(post))}</p>
      <p class="ij-meta">{editorial_meta(post)} <span>{reading_time(post)} min read</span></p>
    </article>'''


def _latest():
    latest_issue = max(blogposts.issues())
    latest = [p for p in blogposts.by_issue() if p["issue"] == latest_issue]
    lead = latest[0]
    # Two stories stand beside the lead, about its height; the rest of the
    # issue runs in a row beneath both, at most three across.
    rail, more = latest[1:3], latest[3:]
    supporting = (f'<div class="ij-secondary">{"".join(article_module(p, "secondary") for p in rail)}</div>'
                  if rail else "")
    beneath = (f'''
        <div class="ij-front__more" data-cols="{min(3, len(more))}">{"".join(article_module(p, "secondary") for p in more)}</div>'''
               if more else "")
    role = image_role(lead) if lead.get("image") else "none"
    # The issue's own pull quote for the lead, where it prints one (blogposts.py).
    quote = (f'\n            <blockquote class="ij-lead__quote"><p>“{esc(lead["pull_quote"])}”</p></blockquote>'
             if lead.get("pull_quote") else "")
    return f'''<section class="ij-front" id="latest" aria-labelledby="ij-edition-title">
      <div class="ij-edition"><h2 id="ij-edition-title">The latest edition</h2>
        <a href="{issue_pdf(lead)}">The Crossroads / {editorial_meta(lead)} <span aria-hidden="true">↗</span></a></div>
      <div class="ij-front__grid">
        <article class="ij-lead" data-image-role="{role}">
          <div class="ij-lead__copy"><p class="ij-kicker">{esc(lead['section'])} / The lead essay</p>
            <h3><a href="{esc(lead['slug'])}.html">{esc(lead['title'])}</a></h3>
            <p class="ij-deck">{esc(lead['excerpt'])}</p>
            <p class="ij-byline">{esc(display_byline(lead))}</p>
            <p class="ij-meta">{editorial_meta(lead)} <span>{reading_time(lead)} min read</span></p>
            <a class="ij-read" href="{esc(lead['slug'])}.html">Read the essay <span aria-hidden="true">→</span></a>{quote}
          </div>
          {editorial_photo(lead, loading='eager')}
        </article>
        {supporting}{beneath}
      </div>
    </section>'''


def _editorial_spreads():
    posts = {p["slug"]: p for p in blogposts.POSTS}
    quote = reading_paragraphs(posts["death-of-rationalism"])[1]
    return f'''<section class="ij-section" id="campus-culture" aria-labelledby="ij-campus-title">
      <div class="ij-section__head"><h2 id="ij-campus-title">Campus &amp; culture</h2><p>Life, expression and the ideas between classes</p></div>
      <div class="ij-middle">
        <div class="ij-middle__feature">{article_module(posts['notes-of-healing'], 'image-feature')}</div>
        <div class="ij-middle__column">
          {article_module(posts['rumors-at-cirs'], 'narrow')}
          {article_module(posts['voyages-in-the-yuva-kendra'], 'brief', image=False, excerpt=False)}
        </div>
        <aside class="ij-opinion" aria-labelledby="ij-opinion-title">
          <h3 id="ij-opinion-title">Opinion &amp; reflection</h3>
          {article_module(posts['is-ai-art-really-art'], 'text-feature', image=False, heading='h4')}
          <figure class="ij-thought"><blockquote><p>“{esc(quote)}”</p></blockquote>
            <figcaption>From <a href="death-of-rationalism.html">The Death of Rationalism</a> / Issue 32</figcaption></figure>
          {article_module(posts['my-home'], 'brief', image=False, excerpt=False, heading='h4')}
        </aside>
      </div>
    </section>
    <section class="ij-section" id="world-sport" aria-labelledby="ij-world-title">
      <div class="ij-section__head"><h2 id="ij-world-title">World &amp; sport</h2><p>Power, competition and the pursuit of excellence</p></div>
      <div class="ij-world">
        {article_module(posts['geography-and-geopolitics'], 'world-feature')}
        <div class="ij-world__rail">
          {article_module(posts['sportswashing'], 'text-feature', slot='rail')}
          {article_module(posts['the-journey-behind-excellence'], 'brief', excerpt=False, slot='rail')}
        </div>
      </div>
    </section>'''


def first_sentence(text):
    return re.split(r'(?<=[.!?])\s+', text, maxsplit=1)[0]


def _card(post, index):
    """One story on the All stories shelf: its picture in the shelf's one box,
    then its section, title, credit and issue. The title's link covers the
    whole card, so the card is a single way into the article."""
    searchable = " ".join([post['title'], post['section'], display_byline(post),
                           f"Issue {post['issue']}", post['excerpt']])
    focus = CARD_FOCUS.get(post['slug'])
    art = ""
    if post.get("image"):
        style = f' style="--focus:{focus}"' if focus else ""
        whole = ' data-fit="whole"' if post['slug'] in CARD_WHOLE else ""
        art = f'<div class="ij-card__art"{style}{whole}>{image_html(post, slot="card")}</div>'
    return f'''<li class="ij-card" data-story data-category="{esc(post['section'])}"
      data-issue="{post['issue']}" data-title="{esc(post['title'])}"
      data-order="{index}" data-search="{esc(searchable)}">
      {art}
      <p class="ij-kicker">{esc(post['section'])}</p>
      <h3><a href="{esc(post['slug'])}.html">{esc(post['title'])}</a></h3>
      <p class="ij-byline">{esc(display_byline(post))}</p>
      <p class="ij-meta">{editorial_meta(post)} <span>{reading_time(post)} min read</span></p>
    </li>'''


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
    posts = blogposts.by_issue()
    cards = "\n".join(_card(post, i) for i, post in enumerate(posts))
    return f"""<section class="ij-section ij-stories" id="stories" aria-labelledby="ij-stories-title" data-journal>
      <div class="ij-section__head">
        <h2 id="ij-stories-title">All stories</h2>
        <p>{count()} articles across {issue_count()} issues</p>
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
      <div class="ij-shelf__bar">
        <p class="ij-results" role="status" aria-live="polite" data-results>{count()} stories</p>
        <div class="ij-shelf__nav" data-shelf-nav hidden>
          <button type="button" data-shelf-step="-1" aria-controls="ij-shelf" aria-label="Scroll the stories back"><span aria-hidden="true">←</span></button>
          <button type="button" data-shelf-step="1" aria-controls="ij-shelf" aria-label="Scroll the stories on"><span aria-hidden="true">→</span></button>
        </div>
      </div>
      <ul class="ij-shelf" id="ij-shelf" aria-label="All stories" data-story-list>
        {cards}
      </ul>
      <div class="ij-shelf__track" aria-hidden="true" data-shelf-track hidden><span data-shelf-thumb></span></div>
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
        <h2 id="ij-archive-title">From the archive</h2>
        <p>Earlier voices from The Crossroads</p>
      </div>
      <div class="ij-archive__grid">{''.join(entries)}</div>
    </section>"""


def front_html():
    markup = (_latest() + _editorial_spreads() + _stories() + _archive() +
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
