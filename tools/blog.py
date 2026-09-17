#!/usr/bin/env python3
"""The CIRS Blog's feed: the markup for the cards and the featured story.

What the blog publishes is in tools/blogposts.py — seventeen articles taken
whole from The Crossroads. This file only lays them out: the lead story at
the top, then a card for every article, newest issue first.

A card carries what the school asked it to carry — the title, the issue it
was printed in, who wrote it, the section it ran under, and two or three
lines of the article's own opening. The lines are never written here; they
are the article's first sentences, cut at a sentence end by blogposts.py.
"""

import blogposts



def esc(t):
    """Article text is raw prose: its ampersands and quotes mean themselves."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _card(post, featured=False):
    slug = post["slug"]
    issue = post["issue"]
    when = f" &middot; {post['date']}" if post["date"] else ""
    by = post["author"] or "The Crossroads Editorial Board"
    cls = "post post--lead" if featured else "post"
    return f'''      <article class="{cls} rv">
        <a class="post__link" href="{slug}.html">
          <p class="post__cat">{esc(post["section"])}</p>
          <h3 class="post__title serif">{esc(post["title"])}</h3>
          <p class="post__stand">{esc(post["excerpt"])}</p>
          <p class="post__meta">
            <span class="post__by">{esc(by)}</span>
            <span class="post__issue">Issue&nbsp;{issue}{when}</span>
          </p>
        </a>
      </article>'''


def feed_html():
    """Every article but the lead, newest issue first."""
    posts = blogposts.by_issue()
    return "\n".join(_card(p) for p in posts[1:])


def featured_html():
    """The lead: the first article of the newest issue, set larger."""
    post = blogposts.by_issue()[0]
    issue = post["issue"]
    when = f" &middot; {post['date']}" if post["date"] else ""
    by = post["author"] or "The Crossroads Editorial Board"
    return f'''    <div class="feat rv">
      <div class="feat__text">
        <p class="feat__flag"><span class="sc">Featured</span></p>
        <p class="feat__cat">{esc(post["section"])}</p>
        <h2 class="feat__title serif" data-split>{esc(post["title"])}</h2>
        <p class="feat__stand">{esc(post["excerpt"])}</p>
        <p class="feat__by"><b>{esc(by)}</b> &middot; The Crossroads, Issue&nbsp;{issue}{when}</p>
        <p class="feat__more"><a class="btn btn--primary" href="{post["slug"]}.html">Read the article &rarr;</a></p>
      </div>
    </div>'''


def count():
    return blogposts.count()


def issue_count():
    return len(blogposts.issues())
