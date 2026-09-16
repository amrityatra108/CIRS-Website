#!/usr/bin/env python3
"""The CIRS Blog's contents, and the markup for its feed.

The page is built and the design is finished; what it does not yet have is a
single piece of writing. So this file holds two kinds of entry and the feed
renders whichever it finds:

    a DESK   a standing section with nobody published in it yet. It shows its
             name, its photograph and what it is for, and says plainly that it
             is waiting for its first piece.
    a POST   a published article: category, title, standfirst, the student who
             wrote it, and the date.

To publish the first real article, change a desk into a post — give it a
`title`, `standfirst`, `author` and `date`, and it stops saying it is waiting.
Nothing else has to change. The order of DESKS below is the order of the feed.

Nothing here is invented. Titles and bylines belong to the students who write
them, and there is no placeholder student in this file for the same reason
there is no placeholder testimonial anywhere else on this site.
"""

# The featured slot at the top of the feed. The photograph is real; the story
# is not written yet. When it is, fill in title/standfirst/author/date exactly
# as for a desk below.
FEATURED = {
    "photo": "blog/featured.jpg",
    "alt": "Students presenting their work at a school exhibition",
    "category": "School Events",
    "title": None,
    "standfirst": None,
    "author": None,
    "date": None,
}

# name, slug-ish photo, alt text, what the desk is for
DESKS = [
    ("Student Voices", "blog/voices.jpg",
     "A student speaking into a microphone at the front of a hall",
     "First-person writing by students, on anything they have thought hard enough about "
     "to want to say in public."),
    ("Campus Life", "blog/campus.jpg",
     "Students at the long tables in the dining hall",
     "The days as they are actually lived — prep, the dining hall, the walk between "
     "classes, the hour before lights out."),
    ("Science &amp; Technology", "blog/science.jpg",
     "A teacher holding up a flask in front of a class",
     "What is happening in the laboratories and the workshops, written by the students "
     "doing it."),
    ("Arts", "blog/arts.jpg",
     "Students at work on a large floor pattern in the courtyard",
     "Studio work, rehearsal, the making of things — and writing about the work of "
     "others."),
    ("Sports", "blog/sport.jpg",
     "Students on the tennis court with rackets",
     "Match reports, training, and the argument about who should have started."),
    ("Culture", "blog/culture.jpg",
     "A festival procession on campus",
     "The festivals the school keeps, and what they mean to the people keeping them."),
    ("Achievements", "blog/honours.jpg",
     "Students in ceremonial sashes at the investiture",
     "Honours, results and representative selections — reported, not announced."),
    ("Reflections", "blog/reflection.jpg",
     "Students seated cross-legged in rows at morning assembly",
     "The quieter register: what a year, a term or a single morning left behind."),
    ("Community", "blog/service.jpg",
     "Cadets carrying equipment on a service morning",
     "Service, outreach and the school's work beyond its own boundary."),
]


def _card(name, photo, alt, blurb, n):
    """One desk in the feed. A desk with no article is honest about it."""
    return f'''      <article class="post rv">
        <a class="post__link" href="#feed" aria-label="{name} — no article published yet">
          <figure class="post__media">
            <img src="assets/img/{photo}" alt="{alt}" width="1000" height="750" loading="lazy">
          </figure>
          <p class="post__cat">{name}</p>
          <h3 class="post__title serif">{blurb}</h3>
          <p class="post__meta"><span class="post__await">Awaiting its first piece</span>
            <span class="post__n">{n:02d}</span></p>
        </a>
      </article>'''


def feed_html():
    return "\n".join(_card(name, photo, alt, blurb, i + 1)
                     for i, (name, photo, alt, blurb) in enumerate(DESKS))


def featured_html():
    f = FEATURED
    if f["title"]:
        body = f'''        <h2 class="feat__title serif" data-split>{f["title"]}</h2>
        <p class="feat__stand">{f["standfirst"]}</p>
        <p class="feat__by"><b>{f["author"]}</b> &middot; {f["date"]}</p>
        <p class="feat__more"><a class="btn btn--primary" href="#feed">Read more &rarr;</a></p>'''
    else:
        body = '''        <h2 class="feat__title serif" data-split>The first featured story
          <em>has not been written yet.</em></h2>
        <p class="feat__stand">This is where it will run: a photograph across half the
          screen, a headline at this size, and the student who wrote it named underneath.
          The slot is built and waiting on the editorial board.</p>
        <p class="feat__by"><em>[Featured story &mdash; title, standfirst, author and date
          to be supplied by the Crossroads Editorial Board.]</em></p>'''
    return f'''    <div class="feat rv">
      <figure class="feat__media">
        <img src="assets/img/{f["photo"]}" alt="{f["alt"]}" width="1600" height="1000" loading="lazy">
      </figure>
      <div class="feat__text">
        <p class="feat__flag"><span class="sc">Featured</span></p>
        <p class="feat__cat">{f["category"]}</p>
{body}
      </div>
    </div>'''


def desk_count():
    return len(DESKS)


def published_count():
    return (1 if FEATURED["title"] else 0)
