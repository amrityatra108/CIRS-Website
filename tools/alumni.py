#!/usr/bin/env python3
"""The alumni journey: every destination, voice and named alumnus on one page.

The Alumni page is a journey rather than a directory — campus, departure, a
field of destinations, the alumni themselves, the pathways out, the index and
the way back — and every one of those chapters is built from the lists below.
This file is the whole of the page's content. Nothing on it is written into
tools/pages/alumni.html except the chapters' own copy.

WHAT IS HERE IS WHAT THE SCHOOL HAS ALREADY SAID.

The page it replaces carried four things and nothing else: eighteen
institutions grouped into four regions, three alumni quotations with the
names of the alumni who gave them, four named alumni with their present
roles, and a note that further alumni were to be supplied. All four are
reproduced below exactly as they stood. Not one name, year, university,
role, city or quotation has been added to them, because there is nowhere in
this repository that a fifth alumnus could have been read from.

WHAT IS DELIBERATELY MISSING.

Batch years. Portraits. Cities. Which alumnus went to which institution.
Anything an alumnus is doing now beyond the one line each of the four
carries. The page asks for all of it in as many words rather than filling
the shape with invention, and ALUMNI-CONTENT.md is the list the school works
through to supply it. A portrait that has not arrived renders as a marked
plate, not as a stock photograph of somebody else.

TO PUBLISH MORE.

  A destination — add to DESTINATIONS. It appears as a point in the
  constellation, a row in the index, and a filterable member of its region.
  Give it a position; the field is art-directed, not laid out by algorithm.

  An alumnus — add to ALUMNI. Name and one verified line is enough to
  publish; batch, institution, place and portrait all appear as soon as they
  are filled in, and are silently left out until they are.

  A quotation — add to VOICES, with the name of the person who said it.

Nothing else has to change. The constellation, the region filters, the
index, the counts and the editorial chapters all build from these lists.
"""

# ------------------------------------------------------------------
# The regions, in the order the constellation and the index use. The key
# is what every point and row carries in data-region, and what the filter
# buttons switch on.
# ------------------------------------------------------------------
REGIONS = [
    ("india", "India"),
    ("uk",    "United Kingdom"),
    ("us",    "United States"),
    ("apac",  "Asia&ndash;Pacific"),
]

# ------------------------------------------------------------------
# The destinations: institutions CIRS students have gone on to, exactly as
# the previous page listed them.
#
#   key       stable id, used by the panel and the index
#   name      as it should read in full
#   short     as it reads on the point in the field, where space is tight
#   country   the country, spelled out
#   region    one of the REGION keys
#   x, y      position in the field, as a percentage of its width and
#             height. The field is a constellation, not a map: the four
#             regions cluster, and cluster west to east, but no point
#             claims a latitude. See the note in alumni.css.
# ------------------------------------------------------------------
DESTINATIONS = [
    # India
    ("srcc",        "Shri Ram College of Commerce", "Shri Ram",
     "India", "india", 60.38, 49.56),
    ("nid",         "National Institute of Design", "NID",
     "India", "india", 55.38, 56.89),
    # cvv carries the longest label on the field and iitm sat straight
    # across from it; these two are spread so the lettering clears.
    ("cvv",         "Chinmaya Vishwa Vidyapeeth", "Chinmaya Vishwa Vidyapeeth",
     "India", "india", 50.20, 69.40),
    ("iitm",        "IIT Madras", "IIT Madras",
     "India", "india", 66.60, 70.60),

    # United Kingdom
    ("durham",      "Durham University", "Durham",
     "United Kingdom", "uk", 43.75, 18.89),
    ("manchester",  "The University of Manchester", "Manchester",
     "United Kingdom", "uk", 42.00, 24.67),
    ("warwick",     "University of Warwick", "Warwick",
     "United Kingdom", "uk", 43.13, 30.44),
    ("imperial",    "Imperial College London", "Imperial",
     "United Kingdom", "uk", 44.13, 36.22),
    # pulled down and out from Imperial, whose label it sat on
    ("lse",         "The London School of Economics and Political Science", "LSE",
     "United Kingdom", "uk", 49.60, 41.20),

    # United States
    ("northwestern", "Northwestern University", "Northwestern",
     "United States", "us", 12.50, 29.78),
    ("chicago",     "University of Chicago", "Chicago",
     "United States", "us", 15.63, 36.67),
    ("purdue",      "Purdue University", "Purdue",
     "United States", "us", 18.75, 43.56),
    ("virginia",    "University of Virginia", "Virginia",
     "United States", "us", 24.50, 47.78),
    ("nyu",         "New York University", "NYU",
     "United States", "us", 26.25, 33.33),
    ("parsons",     "The New School &mdash; Parsons", "Parsons",
     "United States", "us", 28.44, 40.22),
    ("boston",      "Boston University", "Boston",
     "United States", "us", 28.25, 26.67),

    # Asia-Pacific
    ("hkust",       "The Hong Kong University of Science and Technology", "HKUST",
     "Hong Kong", "apac", 84.50, 61.78),
    ("nus",         "National University of Singapore", "NUS",
     "Singapore", "apac", 79.63, 78.44),
]

# Where CIRS itself sits in the field. Every line in the constellation is
# drawn from this point: one beginning, and eighteen paths away from it.
ORIGIN = (59.13, 76.00)

# ------------------------------------------------------------------
# The alumni the school has named, with the single line each was given.
#
#   key, name, role   all verified, all reproduced as they stood
#   batch             "" until the school supplies it
#   place             "" until the school supplies it
#   institution       "" — which institution each attended is NOT recorded
#                     anywhere in this repository, and guessing it from the
#                     destination list above would be an invention
#   portrait          "" until a photograph arrives AND its use is cleared.
#                     Until then the page draws a marked plate.
#   then_portrait     "" — the school-era photograph for the Then/Now
#                     reveal. Both halves must be real for it to run.
# ------------------------------------------------------------------
ALUMNI = [
    {"key": "hari-om-jani", "name": "Hari Om Jani",
     "role": "Professor of Physics, Oxford University",
     "field": "Science and research",
     "batch": "", "place": "", "institution": "",
     "portrait": "", "then_portrait": ""},

    {"key": "soham-desai", "name": "Soham Desai",
     "role": "Strength &amp; Conditioning Coach, Indian Cricket Team",
     "field": "Sport",
     "batch": "", "place": "", "institution": "",
     "portrait": "", "then_portrait": ""},

    {"key": "divyaj-dt", "name": "Divyaj DT",
     "role": "Goalkeeper, National Under-19 Football Team",
     "field": "Sport",
     "batch": "", "place": "", "institution": "",
     "portrait": "", "then_portrait": ""},

    {"key": "shashwat-santosh", "name": "Shashwat Santosh",
     "role": "Designer, Google Creative Labs",
     "field": "Design",
     "batch": "", "place": "", "institution": "",
     "portrait": "", "then_portrait": ""},
]

# ------------------------------------------------------------------
# The three quotations, with the alumni who gave them. These are the only
# alumni words the school has published, and they carry the middle of the
# page on their own.
# ------------------------------------------------------------------
VOICES = [
    {"key": "kavya-s", "name": "Kavya S", "batch": "",
     "quote": "CIRS is an <em>emotion.</em>"},
    {"key": "roshan-b", "name": "Roshan B", "batch": "",
     "quote": "I learned the value of <em>balance</em> in my life over those seven "
              "years there."},
    {"key": "mugdha-sultania", "name": "Mugdha Sultania", "batch": "",
     "quote": "I would literally trade anything to just go back and <em>re-live</em> "
              "each and every moment spent there."},
]

# ------------------------------------------------------------------
# The pathways out. Each one is anchored in something this site already
# states — a destination from the list above, or one of the named alumni,
# or a fact carried on the Curriculum page — and each names its anchor, so
# a reader can see what the pathway is built on rather than taking it on
# trust.
#
#   key, label, heading, copy    the scene
#   anchors                      destination keys, shown as the evidence
#   people                       alumni keys, shown the same way
#   ground                       the scene's colour, as a key that
#                                alumni.css declares a ground for. It is
#                                written into data-scene, NOT data-ground:
#                                cirs.js reads data-ground as a colour value
#                                and would try to tween the body to "ink".
# ------------------------------------------------------------------
PATHWAYS = [
    {"key": "abroad", "label": "Higher education abroad",
     "heading": "The Diploma <em>applies directly.</em>",
     "copy": "The IB opens direct application to North America, the UK, Europe and "
             "Australia. Fourteen of the eighteen institutions CIRS students have "
             "gone on to are outside India.",
     "anchors": ["imperial", "chicago", "lse", "boston"], "people": [],
     "ground": "ink"},

    {"key": "national", "label": "The Indian national pathway",
     "heading": "And the national pathway <em>stays open.</em>",
     "copy": "CBSE keeps the Indian route fully open, with board examinations at "
             "Grades X and XII and a choice of Engineering, Medicine and Management "
             "streams in the senior years.",
     "anchors": ["iitm", "srcc", "cvv"], "people": [],
     "ground": "navy"},

    {"key": "design", "label": "Design and the arts",
     "heading": "Some of them <em>make things.</em>",
     "copy": "Two of the eighteen destinations are design schools rather than "
             "universities, and one of the four alumni the school has named works as "
             "a designer.",
     "anchors": ["nid", "parsons"], "people": ["shashwat-santosh"],
     "ground": "gold"},

    {"key": "science", "label": "Science and research",
     "heading": "Some of them <em>stay in the question.</em>",
     "copy": "The furthest a CIRS education has been followed in public is into a "
             "university physics department &mdash; and the route into research runs "
             "through institutions already on this list.",
     "anchors": ["imperial", "hkust", "purdue"], "people": ["hari-om-jani"],
     "ground": "slate"},

    {"key": "sport", "label": "Sport",
     "heading": "And some of them <em>go professional.</em>",
     "copy": "Sport at CIRS fills the four o&rsquo;clock hour every day of the school "
             "year. Two of the four alumni the school has named carried it into a "
             "national side.",
     "anchors": [], "people": ["soham-desai", "divyaj-dt"],
     "ground": "maroon"},
]


# ==================================================================
# Lookups and counts
# ==================================================================

def _dest(key):
    for d in DESTINATIONS:
        if d[0] == key:
            return d
    raise KeyError("alumni.py: no destination named %r" % (key,))


def _person(key):
    for p in ALUMNI:
        if p["key"] == key:
            return p
    raise KeyError("alumni.py: no alumnus named %r" % (key,))


def count():
    return len(DESTINATIONS)


def region_count(region):
    return sum(1 for d in DESTINATIONS if d[4] == region)


def country_count():
    return len({d[3] for d in DESTINATIONS})


def abroad_count():
    return sum(1 for d in DESTINATIONS if d[3] != "India")


def named_count():
    return len(ALUMNI)


def voice_count():
    return len(VOICES)


# ==================================================================
# The constellation
# ==================================================================

def lines_svg():
    """Every path in the field, drawn from CIRS outward.

    One line per destination, bowed rather than straight so eighteen of them
    read as a spray of routes and not as the spokes of a wheel. The bow is
    always to the same side of the straight line, which is what makes the
    whole field lean in one direction instead of looking scattered.

    The viewBox is 0 0 100 100 and the coordinates are the same percentages
    the points carry, so a line and the point it ends at cannot drift apart
    when the field is resized.
    """
    ox, oy = ORIGIN
    paths = []
    for key, _name, _short, _country, region, x, y in DESTINATIONS:
        mx, my = (ox + x) / 2, (oy + y) / 2
        # Perpendicular to the run, scaled by its length: short hops bow
        # a little, long ones bow more.
        dx, dy = x - ox, y - oy
        length = (dx * dx + dy * dy) ** .5 or 1
        bow = min(length * .14, 9)
        cx, cy = mx - dy / length * bow, my + dx / length * bow
        paths.append(
            '    <path class="ajc__line" data-region="%s" data-line="%s" '
            'd="M%.2f %.2f Q%.2f %.2f %.2f %.2f"/>'
            % (region, key, ox, oy, cx, cy, x, y))
    return "\n".join(paths)


def constellation_html():
    """The field: an SVG of routes, and a real button for every destination.

    The lines are SVG and inert. The points are HTML buttons positioned over
    them, because a button is the only thing that is reliably focusable,
    announceable and clickable — an SVG <circle> with a tabindex is none of
    those three on every browser that matters.

    Below a certain width the same buttons become a plain list: see the
    mobile block in alumni.css. There is one DOM, and no second markup path
    that can rot.
    """
    ox, oy = ORIGIN
    total = len(DESTINATIONS)
    points = []
    for i, (key, name, short, country, region, x, y) in enumerate(DESTINATIONS):
        points.append('''      <li class="ajc__item" data-region="%s">
        <button type="button" class="ajc__pt" id="ajc-pt-%s"
                style="--x:%s%%;--y:%s%%"
                data-point="%s" data-region="%s"
                aria-expanded="false" aria-controls="ajc-panel">
          <span class="ajc__dot" aria-hidden="true"></span>
          <span class="ajc__label"><span class="ajc__name">%s</span><span class="ajc__country">%s</span></span>
          <span class="sr-only">Destination %d of %d. %s, %s. Open details.</span>
        </button>
      </li>''' % (region, key, x, y, key, region, short, country,
                  i + 1, total, name, country))

    filters = ['      <button type="button" class="ajc__filter is-on" data-filter="all" '
               'aria-pressed="true">All <span class="ajc__fcount">%d</span></button>' % total]
    for key, label in REGIONS:
        filters.append(
            '      <button type="button" class="ajc__filter" data-filter="%s" '
            'aria-pressed="false">%s <span class="ajc__fcount">%d</span></button>'
            % (key, label, region_count(key)))

    return '''<div class="ajc" data-constellation>
  <div class="ajc__bar">
    <div class="ajc__filters" role="group" aria-label="Filter the destinations by region">
%s
    </div>
    <p class="ajc__status" data-constellation-status role="status">Showing all %d destinations.</p>
  </div>

  <div class="ajc__field" data-constellation-field>
    <svg class="ajc__lines" viewBox="0 0 100 100" preserveAspectRatio="none"
         aria-hidden="true" focusable="false">
%s
    </svg>

    <p class="ajc__origin" style="--x:%s%%;--y:%s%%" aria-hidden="true">
      <span class="ajc__originDot"></span>
      <span class="ajc__originName">CIRS<small>Siruvani</small></span>
    </p>

    <ul class="ajc__points">
%s
    </ul>
  </div>

  <div class="ajc__panel" id="ajc-panel" role="dialog" aria-modal="true"
       aria-labelledby="ajc-panel-name" hidden>
    <div class="ajc__panelInner">
      <p class="ajc__panelRegion sc" data-panel-region></p>
      <!-- Seeded rather than empty: the panel is hidden until a point is
           opened, but an empty heading is invalid markup either way, and
           aria-labelledby points at this element. -->
      <h3 class="serif ajc__panelName" id="ajc-panel-name" data-panel-name>Destination</h3>
      <p class="ajc__panelCountry" data-panel-country></p>
      <p class="ajc__panelNote">A destination CIRS students have gone on to.
        <em>[Which alumni read here, and in which years, to be supplied by the
        school.]</em></p>
      <button type="button" class="ajc__panelClose" data-panel-close>
        Close<span class="sr-only"> this destination</span>
      </button>
    </div>
  </div>
</div>''' % ("\n".join(filters), total, lines_svg(), ox, oy, "\n".join(points))


# ==================================================================
# The index
# ==================================================================

def destinations_html():
    """The index: text first, grouped by region, filterable and searchable.

    No logo wall. Eighteen institutions is a list, and a list set properly
    is easier to read and to search than eighteen pictures of wordmarks the
    school has no licence to reproduce.
    """
    groups = []
    for region, label in REGIONS:
        rows = []
        for key, name, _short, country, r, _x, _y in DESTINATIONS:
            if r != region:
                continue
            search = name.replace("&mdash;", "-").lower() + " " + country.lower()
            rows.append('''          <li class="ajd__row" data-region="%s" data-search="%s">
            <span class="ajd__name">%s</span>
            <span class="ajd__country">%s</span>
          </li>''' % (region, search, name, country))
        groups.append('''      <section class="ajd__group" data-region="%s">
        <h3 class="ajd__region"><span class="sc">%s</span>
          <span class="ajd__n">%d<span class="sr-only"> destinations</span></span></h3>
        <ul class="ajd__rows">
%s
        </ul>
      </section>''' % (region, label, region_count(region), "\n".join(rows)))

    return '''<div class="ajd" data-destinations>
  <div class="ajd__search">
    <label class="ajd__label" for="ajd-q">Search the destinations</label>
    <input class="ajd__input" id="ajd-q" type="search" autocomplete="off"
           placeholder="University, or country">
    <p class="ajd__count" data-destinations-count role="status">%d institutions in %d countries.</p>
  </div>

  <div class="ajd__groups">
%s
  </div>

  <p class="ajd__empty" data-destinations-empty hidden>No destination matches that search.</p>
</div>''' % (len(DESTINATIONS), country_count(), "\n".join(groups))


# ==================================================================
# The alumni themselves
# ==================================================================

def _plate(person, kind="now"):
    """A portrait frame for a portrait that has not arrived.

    The school has published no photograph of any alumnus, and there is no
    honest way to show one: a stock face is a lie about a real person, and
    another student's photograph is a worse one. So the frame is drawn
    rather than filled — the initials, the name of what is missing, and the
    permission it is waiting on — and it is built to be replaced. Fill
    "portrait" in the entry above and the plate becomes an <img> with
    nothing else on the page to change.
    """
    initials = "".join(part[0] for part in person["name"].split()[:2]).upper()
    src = person["then_portrait"] if kind == "then" else person["portrait"]
    label = "School years" if kind == "then" else "Today"
    if src:
        return ('<img class="ajp__img" src="%s" alt="%s, %s." '
                'width="900" height="1200" loading="lazy" decoding="async">'
                % (src, person["name"], person["role"]))
    return '''<span class="ajp__plate" data-plate="%s">
          <span class="ajp__initials" aria-hidden="true">%s</span>
          <span class="ajp__plateLabel sc">%s</span>
          <span class="ajp__plateNote"><em>[Portrait to be supplied by the school, with
            the alumnus&rsquo;s permission.]</em></span>
        </span>''' % (kind, initials, label)


def people_html():
    """The four named alumni, one editorial chapter each.

    Alternating sides, and the name set large enough to be the picture while
    there is no picture. Everything the school has said about each of them
    is on the chapter; everything it has not said is asked for by name.
    """
    chapters = []
    for i, person in enumerate(ALUMNI):
        side = "right" if i % 2 else "left"
        meta = []
        if person["batch"]:
            meta.append('<span class="ajp__metaItem"><b>Batch</b>%s</span>' % person["batch"])
        if person["institution"]:
            meta.append('<span class="ajp__metaItem"><b>Read at</b>%s</span>'
                        % person["institution"])
        if person["place"]:
            meta.append('<span class="ajp__metaItem"><b>Now in</b>%s</span>' % person["place"])
        # Nothing but the field is known for any of the four today. The row
        # still renders, so the chapter does not collapse into a name and a
        # gap, and it says which of the five pathways the alumnus belongs to.
        meta.append('<span class="ajp__metaItem"><b>Path</b>%s</span>' % person["field"])

        chapters.append('''  <article class="ajp" id="alumnus-%s" data-person="%s" data-side="%s">
    <div class="ajp__figure">
      <figure class="ajp__frame">
        %s
      </figure>
      <p class="ajp__index" aria-hidden="true">%02d</p>
    </div>

    <div class="ajp__text">
      <h3 class="serif ajp__name" data-split>%s</h3>
      <p class="ajp__role">%s</p>
      <p class="ajp__meta">%s</p>
      <p class="ajp__await"><em>[The rest of this alumnus&rsquo;s story &mdash; the batch, where
        they read, and what they would say about the years here &mdash; to be supplied by the
        school.]</em></p>
    </div>
  </article>''' % (person["key"], person["key"], side, _plate(person), i + 1,
                   person["name"], person["role"], "".join(meta)))
    return "\n".join(chapters)


def voices_html():
    """The three quotations, each given a scene of its own.

    These are the only alumni words on the site, so they are not set as
    cards three abreast. Each one holds the screen by itself, at the size
    the sentence deserves.
    """
    scenes = []
    for voice in VOICES:
        batch = voice["batch"] or "<em>[Batch to be supplied]</em>"
        scenes.append('''  <figure class="ajv" data-voice="%s">
    <p class="ajv__mark" aria-hidden="true">&ldquo;</p>
    <blockquote class="ajv__quote">
      <p class="serif" data-split>%s</p>
    </blockquote>
    <figcaption class="ajv__by">
      <span class="ajv__name">%s</span>
      <span class="ajv__batch">%s</span>
    </figcaption>
  </figure>''' % (voice["key"], voice["quote"], voice["name"], batch))
    return "\n".join(scenes)


# ==================================================================
# The pathways
# ==================================================================

def pathways_html():
    """Five scenes on one horizontal track, each naming what it is built on.

    A pathway that cannot name its evidence is an advertisement. Every scene
    below carries the destinations and the alumni it was drawn from, as
    links into the chapters further up where those exist, so the claim and
    the thing supporting it are never more than a click apart.
    """
    scenes = []
    total = len(PATHWAYS)
    for i, path in enumerate(PATHWAYS):
        evidence = []
        for key in path["anchors"]:
            d = _dest(key)
            evidence.append('<li class="ajw__ev"><span class="ajw__evName">%s</span>'
                            '<span class="ajw__evWhere">%s</span></li>' % (d[1], d[3]))
        for key in path["people"]:
            p = _person(key)
            evidence.append('<li class="ajw__ev"><a class="ajw__evName" href="#alumnus-%s">%s</a>'
                            '<span class="ajw__evWhere">%s</span></li>'
                            % (p["key"], p["name"], p["role"]))

        scenes.append('''    <article class="ajw" data-pathway="%s" data-scene="%s">
      <p class="ajw__n" aria-hidden="true">%d <span>/ %d</span></p>
      <p class="ajw__label sc">%s</p>
      <h3 class="serif ajw__head">%s</h3>
      <p class="ajw__copy">%s</p>
      <p class="ajw__evLabel sc">Drawn from</p>
      <ul class="ajw__evList">
        %s
      </ul>
    </article>''' % (path["key"], path["ground"], i + 1, total, path["label"],
                     path["heading"], path["copy"],
                     "\n        ".join(evidence)))

    dots = "\n".join(
        '      <li><button type="button" class="ajw__dot" data-goto="%d" '
        'aria-label="Go to %s"><span></span></button></li>' % (i, p["label"])
        for i, p in enumerate(PATHWAYS))

    return '''<div class="ajw-track" data-pathways>
  <div class="ajw-rail" data-pathways-rail>
%s
  </div>
  <nav class="ajw-nav" aria-label="The pathways">
    <ul class="ajw__dots">
%s
    </ul>
  </nav>
</div>''' % ("\n".join(scenes), dots)
