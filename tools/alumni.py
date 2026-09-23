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

import math

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
# THE GALAXY
#
# The field is a spiral galaxy seen at an angle, with CIRS at the core
# and every destination a star out along one of the two arms. It is not
# a map and does not pretend to be one: the arms carry the regions in
# groups, and a star's distance from the core is how far along its arm
# it sits, not how far from Coimbatore anything is.
#
# The arm is a logarithmic spiral, r = R0 * e^(B*theta), projected as a
# disc tilted away from the viewer — INCL is the cosine of that tilt.
# ASPECT is the field's own 3:2, which is what turns a swing in percent
# of the width into the same swing in percent of the height.
#
# These same six numbers are handed to alumni-journey.js on the field
# element, so the stars it scatters lie along the same two arms as the
# nineteen that are named. One spiral, written down once.
# ------------------------------------------------------------------
SPIRAL_CX, SPIRAL_CY = 50.0, 50.0
SPIRAL_R0, SPIRAL_B  = 6.10, 0.2182
SPIRAL_ROT           = -0.55
SPIRAL_INCL          = 0.70
SPIRAL_ASPECT        = 1.5   # the field is 3:2
SPIRAL_THETA_MIN     = 2.7
SPIRAL_THETA_MAX     = 8.5
_YK = SPIRAL_INCL * SPIRAL_ASPECT


def spiral(arm, theta):
    """Where a point on an arm falls, as (x, y) in percent of the field."""
    r = SPIRAL_R0 * math.exp(SPIRAL_B * theta)
    a = theta + arm * math.pi + SPIRAL_ROT
    return (SPIRAL_CX + r * math.cos(a),
            SPIRAL_CY + r * math.sin(a) * _YK)


# ------------------------------------------------------------------
# The destinations: institutions CIRS students have gone on to.
#
# Eighteen of the nineteen were on the previous version of this page and
# are reproduced exactly. NTU Singapore was supplied afterwards by the
# school — which is how every further one should arrive.
#
#   key       stable id, used by the panel and the index
#   name      as it should read in full
#   short     as it reads on the star, where space is tight
#   country   the country, spelled out
#   region    one of the REGION keys
#   arm       0 or 1 — which of the galaxy's two arms it lies on
#   theta     how far along that arm, in radians from the core
#
# Regions sit in unbroken runs along an arm, innermost first, so the
# grouping survives being wound into a spiral: arm 0 carries India and
# then the United Kingdom, arm 1 carries Asia-Pacific and then the
# United States.
# ------------------------------------------------------------------
DESTINATIONS = [
    # ---- arm 0: India, then the United Kingdom ----
    ("iitm",        "IIT Madras", "IIT Madras",
     "India", "india", 0, 2.700),
    ("srcc",        "Shri Ram College of Commerce", "Shri Ram",
     "India", "india", 0, 3.425),
    ("nid",         "National Institute of Design", "NID",
     "India", "india", 0, 4.150),
    ("cvv",         "Chinmaya Vishwa Vidyapeeth", "Chinmaya Vishwa Vidyapeeth",
     "India", "india", 0, 4.875),
    ("durham",      "Durham University", "Durham",
     "United Kingdom", "uk", 0, 5.600),
    ("manchester",  "The University of Manchester", "Manchester",
     "United Kingdom", "uk", 0, 6.325),
    ("warwick",     "University of Warwick", "Warwick",
     "United Kingdom", "uk", 0, 7.050),
    ("imperial",    "Imperial College London", "Imperial",
     "United Kingdom", "uk", 0, 7.775),
    ("lse",         "The London School of Economics and Political Science", "LSE",
     "United Kingdom", "uk", 0, 8.500),

    # ---- arm 1: Asia-Pacific, then the United States ----
    ("nus",         "National University of Singapore", "NUS",
     "Singapore", "apac", 1, 2.700),
    ("ntu",         "Nanyang Technological University", "NTU",
     "Singapore", "apac", 1, 3.344),
    ("hkust",       "The Hong Kong University of Science and Technology", "HKUST",
     "Hong Kong", "apac", 1, 3.989),
    ("northwestern", "Northwestern University", "Northwestern",
     "United States", "us", 1, 4.633),
    ("chicago",     "University of Chicago", "Chicago",
     "United States", "us", 1, 5.278),
    ("purdue",      "Purdue University", "Purdue",
     "United States", "us", 1, 5.922),
    ("virginia",    "University of Virginia", "Virginia",
     "United States", "us", 1, 6.567),
    ("nyu",         "New York University", "NYU",
     "United States", "us", 1, 7.211),
    ("parsons",     "The New School &mdash; Parsons", "Parsons",
     "United States", "us", 1, 7.856),
    ("boston",      "Boston University", "Boston",
     "United States", "us", 1, 8.500),
]

# The core. Every arm is measured out from it, and it is where the page
# puts CIRS: one beginning, and nineteen ways out of it.
ORIGIN = (SPIRAL_CX, SPIRAL_CY)

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
             "Australia. {ABROAD_CAP} of the {COUNT} institutions CIRS students "
             "have gone on to are outside India.",
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
     "copy": "Two of the {COUNT} destinations are design schools rather than "
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


_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
          8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
          13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen",
          17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
          21: "twenty-one", 22: "twenty-two", 23: "twenty-three",
          24: "twenty-four", 25: "twenty-five"}


def word(n):
    """A count as a word, because the page is set in sentences.

    Every sentence that counts something takes its number from here rather
    than having it typed in. Adding a nineteenth destination had already
    left four sentences saying eighteen.
    """
    return _WORDS.get(n, str(n))


def count_word():
    return word(len(DESTINATIONS))


def abroad_word():
    return word(abroad_count())


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
    """One path per destination, running out along its own arm from the core.

    A straight line from the middle of a galaxy to a star would cut across
    the arms; these lie along them, so lighting one traces the arm a
    reader's eye is already following. They sit at almost nothing until
    the star they belong to is asked about.

    Both SVGs on this field use viewBox "0 0 150 100" with
    preserveAspectRatio="none". The field is 3:2, so that mapping is
    uniform in both directions — a circle drawn in it is still a circle —
    and a position in percent converts by (1.5x, y).
    """
    paths = []
    for key, _n, _s, _c, region, arm, theta in DESTINATIONS:
        pts = []
        steps = 40
        for i in range(steps + 1):
            t = SPIRAL_THETA_MIN + (theta - SPIRAL_THETA_MIN) * i / steps
            x, y = spiral(arm, t)
            pts.append("%.2f %.2f" % (x * 1.5, y))
        d = "M" + pts[0] + "".join(" L" + q for q in pts[1:])
        paths.append(
            '    <path class="ajc__line" data-region="%s" data-line="%s" d="%s"/>'
            % (region, key, d))
    return "\n".join(paths)


def constellation_html():
    """The galaxy: two arms of stars, nineteen of which are named.

    The arms and the loose field are drawn by alumni-journey.js from the
    spiral this file defines — handed over on the field element as
    data-spiral — so the stars it scatters lie along the same two arms as
    the nineteen named ones. The named ones are HTML buttons over the top,
    because a button is the only thing reliably focusable, announceable
    and clickable; an SVG <circle> with a tabindex is none of the three on
    every browser that matters.

    Below 900px the same buttons become a plain list. There is one DOM,
    and no second markup path that can rot.
    """
    ox, oy = ORIGIN
    total = len(DESTINATIONS)
    points = []
    for i, (key, name, short, country, region, arm, theta) in enumerate(DESTINATIONS):
        x, y = spiral(arm, theta)
        points.append('''      <li class="ajc__item" data-region="%s">
        <button type="button" class="ajc__pt" id="ajc-pt-%s"
                style="--x:%.3f%%;--y:%.3f%%"
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
%(filters)s
    </div>
    <p class="ajc__status" data-constellation-status role="status">Showing all %(total)d destinations.</p>
  </div>

  <div class="ajc__field" data-constellation-field
       data-spiral="%(cx).4f,%(cy).4f,%(r0).4f,%(b).4f,%(rot).4f,%(yk).4f,%(tmin).4f,%(tmax).4f">
    <svg class="ajc__lines" viewBox="0 0 150 100" preserveAspectRatio="none"
         aria-hidden="true" focusable="false">
%(lines)s
    </svg>

    <p class="ajc__origin" style="--x:%(ox).3f%%;--y:%(oy).3f%%" aria-hidden="true">
      <span class="ajc__originDot"></span>
      <span class="ajc__originName">CIRS<small>Siruvani</small></span>
    </p>

    <ul class="ajc__points">
%(points)s
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
</div>''' % {"filters": "\n".join(filters), "total": total, "lines": lines_svg(),
              "ox": ox, "oy": oy, "points": "\n".join(points),
              "cx": SPIRAL_CX, "cy": SPIRAL_CY, "r0": SPIRAL_R0, "b": SPIRAL_B,
              "rot": SPIRAL_ROT, "yk": _YK,
              "tmin": SPIRAL_THETA_MIN, "tmax": SPIRAL_THETA_MAX}


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
        for key, name, _short, country, r, _arm, _theta in DESTINATIONS:
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

        copy = (path["copy"].replace("{COUNT}", count_word())
                            .replace("{ABROAD_CAP}", abroad_word().capitalize())
                            .replace("{ABROAD}", abroad_word()))
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
                     path["heading"], copy,
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
