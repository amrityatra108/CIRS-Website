#!/usr/bin/env python3
"""The alumni journey: every destination, voice and named alumnus on one page.

The Alumni page is a journey rather than a directory — campus, departure, a
field of destinations, the alumni themselves, the pathways out, the index and
the way back — and every one of those chapters is built from the lists below.
This file is the whole of the page's content. Nothing on it is written into
tools/pages/alumni.html except the chapters' own copy.

WHAT IS HERE IS WHAT THE SCHOOL HAS ALREADY SAID.

The previous page carried eighteen institutions grouped into four regions,
three alumni quotations, four named alumni with their present roles, and a
note that further alumni were to be supplied. Those records remain. The
current page also includes extended biographies for the four named alumni;
batch years, current cities, portraits and personal reflections remain
omitted until supplied.

WHAT IS DELIBERATELY MISSING.

Batch years. Portraits. Cities. Which alumnus went to which institution,
except for Hari Om Jani, whose biography records the National University of
Singapore. Extended biographies are included for all four named alumni.
ALUMNI-CONTENT.md tracks what is still missing. A portrait that has not
arrived renders as a marked plate, not as a stock photograph of somebody else.

TO PUBLISH MORE.

  A destination — add to DESTINATIONS. It appears as a point on the map,
  a row in the index, and a filterable member of its region. Give it a
  latitude and a longitude; the map places it and draws its route.

  An alumnus — add to ALUMNI. Name and one verified line is enough to
  publish. Add an extended account in "biography" when one is supplied;
  batch, institution, place and portrait appear as soon as they are filled
  in, and are silently left out until they are.

  A quotation — add to VOICES, with the name of the person who said it.

Nothing else has to change. The map, the region filters, the index, the
counts and the editorial chapters all build from these lists.
"""

import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import robinson          # noqa: E402  the projection, shared with make-worldmap.py
import worldland         # noqa: E402  the coastline it has already projected

# ------------------------------------------------------------------
# The regions, in the order the map and the index use. The key is what
# every point and row carries in data-region, and what the filter
# buttons switch on.
# ------------------------------------------------------------------
REGIONS = [
    ("india", "India"),
    ("uk",    "United Kingdom"),
    ("us",    "United States"),
    ("apac",  "Asia&ndash;Pacific"),
]

# ------------------------------------------------------------------
# THE MAP
#
# The field is a map of the world, drawn in Robinson (see
# tools/robinson.py for why that projection and not a web one), with
# CIRS on it where Coimbatore is and every destination where it is.
# Distance on it means distance. Nothing is art-directed except which
# side of a point its name sits on, and that only because five of the
# nineteen are in Britain.
#
# Positions come out of robinson.project() in viewBox units — the frame
# is VB_W across and VB_H down — and go into the page as percentages of
# the field, which is cut to exactly that ratio. One unit of the frame
# is one unit in either direction: the projection is uniform, so a
# nudge of 2 sideways and a nudge of 2 downward are the same distance.
# ------------------------------------------------------------------
VB_W, VB_H = robinson.VB_W, robinson.VB_H

# Siruvani, Coimbatore: the campus itself, not the city centre.
ORIGIN_LAT, ORIGIN_LON = 10.95, 76.72


def route(ax, ay, bx, by):
    """A flight path from (ax, ay) to (bx, by), as a cubic bezier.

    A straight line between two points on a flat map is not the way
    anybody travels, and nineteen straight lines out of one point is a
    starburst. These bow — always toward the top of the frame, because
    that is the side a great circle leans on for every route on this
    map — by a share of their own length, capped so that Coimbatore to
    Chicago does not arc out of the picture.
    """
    vx, vy = bx - ax, by - ay
    length = (vx * vx + vy * vy) ** 0.5
    if length < 0.001:
        return "M%.2f %.2f" % (ax, ay)
    nx, ny = -vy / length, vx / length
    if ny > 0:                      # keep the bow on the northern side
        nx, ny = -nx, -ny
    bow = min(length * 0.17, 13.0)
    return "M%.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f" % (
        ax, ay,
        ax + vx * 0.27 + nx * bow, ay + vy * 0.27 + ny * bow,
        ax + vx * 0.73 + nx * bow, ay + vy * 0.73 + ny * bow,
        bx, by)


# ------------------------------------------------------------------
# The destinations: institutions CIRS students have gone on to.
#
# Eighteen of the nineteen were on the previous version of this page and
# are reproduced exactly. NTU Singapore was supplied afterwards by the
# school — which is how every further one should arrive.
#
#   key       stable id, used by the panel and the index
#   name      as it should read in full
#   short     as it reads on the map, where space is tight
#   country   the country, spelled out
#   region    one of the REGION keys
#   lat, lon  where the institution actually is
#   nudge     (dx, dy) in frame units, and the ONLY licence taken with
#             geography. Imperial and the LSE are two miles apart and
#             would be one dot; so would NYU and Parsons, Northwestern
#             and Chicago, NUS and NTU. Each is moved by a couple of
#             frame units — a few pixels — so that both can be seen and
#             both can be clicked. Nothing is moved further than that.
#   label     (dx, dy, side) for the name: where it sits relative to its
#             point, and which way it runs — "l" ends at that offset,
#             "r" starts there, "c" is centred on it. A name further
#             than a whisker from its point is joined to it by a leader,
#             so no name is ever ambiguous about which point it belongs
#             to. Five of these are in Britain, which is why the offsets
#             are written down rather than computed.
# ------------------------------------------------------------------
DESTINATIONS = [
    # ---- India ----
    ("iitm",        "IIT Madras", "IIT Madras",
     "India", "india", 13.01, 80.24, (0.4, 0.4), (4.8, 0.4, "r")),
    ("srcc",        "Shri Ram College of Commerce", "Shri Ram",
     "India", "india", 28.69, 77.21, (0.0, 0.0), (0.0, -5.0, "c")),
    ("nid",         "National Institute of Design", "NID",
     "India", "india", 23.03, 72.55, (0.0, 0.0), (-3.4, -0.6, "l")),
    ("cvv",         "Chinmaya Vishwa Vidyapeeth", "Chinmaya Vishwa Vidyapeeth",
     "India", "india", 9.98, 76.55, (-2.4, 2.4), (-4.6, 5.2, "l")),

    # ---- United Kingdom ----
    ("durham",      "Durham University", "Durham",
     "United Kingdom", "uk", 54.77, -1.58, (-0.4, -1.4), (-3.0, -3.2, "l")),
    ("manchester",  "The University of Manchester", "Manchester",
     "United Kingdom", "uk", 53.47, -2.23, (-1.4, -0.1), (-3.0, 0.0, "l")),
    ("warwick",     "University of Warwick", "Warwick",
     "United Kingdom", "uk", 52.38, -1.56, (-0.2, 1.0), (-3.0, 3.4, "l")),
    ("imperial",    "Imperial College London", "Imperial",
     "United Kingdom", "uk", 51.50, -0.18, (0.6, 1.6), (3.0, 2.6, "r")),
    ("lse",         "The London School of Economics and Political Science", "LSE",
     "United Kingdom", "uk", 51.51, -0.12, (1.4, -0.3), (3.0, -2.0, "r")),

    # ---- Asia–Pacific ----
    ("nus",         "National University of Singapore", "NUS",
     "Singapore", "apac", 1.30, 103.78, (0.9, 0.7), (3.0, 1.8, "r")),
    ("ntu",         "Nanyang Technological University", "NTU",
     "Singapore", "apac", 1.35, 103.68, (-0.9, -0.7), (-3.0, 2.6, "l")),
    ("hkust",       "The Hong Kong University of Science and Technology", "HKUST",
     "Hong Kong", "apac", 22.34, 114.26, (0.0, 0.0), (3.2, 0.4, "r")),

    # ---- United States ----
    ("northwestern", "Northwestern University", "Northwestern",
     "United States", "us", 42.06, -87.69, (-0.9, -0.9), (-3.0, -5.2, "l")),
    ("chicago",     "University of Chicago", "Chicago",
     "United States", "us", 41.79, -87.60, (0.2, 0.3), (-3.4, 1.0, "l")),
    ("purdue",      "Purdue University", "Purdue",
     "United States", "us", 40.42, -86.91, (0.9, 1.0), (0.0, 4.4, "c")),
    ("virginia",    "University of Virginia", "Virginia",
     "United States", "us", 38.03, -78.51, (0.0, 0.0), (2.8, 3.0, "r")),
    ("nyu",         "New York University", "NYU",
     "United States", "us", 40.73, -73.99, (0.0, 0.2), (3.4, 0.6, "r")),
    ("parsons",     "The New School &mdash; Parsons", "Parsons",
     "United States", "us", 40.74, -73.99, (-0.9, -0.9), (-3.0, -2.4, "l")),
    ("boston",      "Boston University", "Boston",
     "United States", "us", 42.35, -71.11, (0.6, -0.8), (3.0, -2.2, "r")),
]


def place(lat, lon, nudge=(0.0, 0.0)):
    """Where a destination's point falls, in frame units."""
    x, y = robinson.project(lat, lon)
    return (x + nudge[0], y + nudge[1])


# Where every route starts, in frame units.
ORIGIN = place(ORIGIN_LAT, ORIGIN_LON)

# ------------------------------------------------------------------
# The alumni the school has named, with their verified roles and available
# biographies.
#
#   key, name, role   all verified, all reproduced as they stood
#   batch             "" until the school supplies it
#   place             "" until the school supplies it
#   institution       "" — which institution each attended is NOT recorded
#                     for three of the four; Hari Om Jani's is recorded below
#   biography         an extended biography supplied for this alumnus
#   portrait          "" until a photograph arrives AND its use is cleared.
#                     Until then the page draws a marked plate.
#   then_portrait     "" — the school-era photograph for the Then/Now
#                     reveal. Both halves must be real for it to run.
# ------------------------------------------------------------------
ALUMNI = [
    {"key": "hari-om-jani", "name": "Hari Om Jani",
     "role": "Professor of Physics, Oxford University",
     "field": "Science and research",
     "batch": "", "place": "", "institution": "National University of Singapore",
     "portrait": "", "then_portrait": "",
     "biography": "He moved to Singapore to pursue his bachelor’s degree in Physics and PhD at the National University of Singapore. He continued there as a Research Fellow and later as a Senior Research Fellow, before moving to Oxford in 2022 as a Marie Skłodowska-Curie Fellow. In 2024, Hari was selected as a Young Scientist for the Lindau Nobel Laureate Meeting and was awarded the Royal Society University Research Fellowship, through which he established his research group, Designer Quantum Materials for Devices. He took up his current position at Queen’s College and the Department of Materials in 2026."},

    {"key": "soham-desai", "name": "Soham Desai",
     "role": "Strength &amp; Conditioning Coach, Lucknow Super Giants",
     "field": "Sport",
     "batch": "", "place": "", "institution": "",
     "portrait": "", "then_portrait": "",
     "biography": "Soham Desai has been the backbone of one of the most celebrated cricket teams in the world. He served for five years as the lead Strength and Conditioning Coach of the Indian Cricket Team, and is currently with the IPL team Lucknow Super Giants."},

    {"key": "divyaj-dt", "name": "Divyaj DT",
     "role": "Goalkeeper, NorthEast United FC",
     "field": "Sport",
     "batch": "", "place": "", "institution": "",
     "portrait": "", "then_portrait": "",
     "biography": "Divyaj is an alumnus of Alchemy International Football Academy & Baroda Football Academy, progressing to the NorthEast United FC, where he currently plays as Goalkeeper, and has represented India internationally at the youth levels, including the India U19 and India U20 national teams. He was a part of the squad that became champions at the SAFF U19 Championship."},

    {"key": "shashwat-santosh", "name": "Shashwath Santosh",
     "role": "Designer, Google Creative Lab",
     "field": "Design",
     "batch": "", "place": "", "institution": "",
     "portrait": "", "then_portrait": "",
     "biography": "Shashwath Santosh is an industrial and product designer based in New York, currently working at Google Creative Lab on AI-driven experiences like Gemini, Project Astra, and Genie. His website can be found at shashwathsantosh.com."},
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
# The map
# ==================================================================

def routes_svg():
    """One flight path per destination, out of Siruvani, plus the leaders.

    Both are .ajc__line and both carry data-line, so the script lights a
    name's leader with its route and the filters dim the pair together —
    there is one set of lines on this map, not two that could disagree.

    The viewBox is the projection's own frame and preserveAspectRatio is
    left at its default, because the field is cut to exactly that ratio:
    a route drawn here lands on the coastline drawn beside it.
    """
    ox, oy = ORIGIN
    out = []
    for key, _n, _s, _c, region, lat, lon, nudge, label in DESTINATIONS:
        x, y = place(lat, lon, nudge)
        out.append(
            '      <path class="ajc__line" data-region="%s" data-line="%s" d="%s"/>'
            % (region, key, route(ox, oy, x, y)))

        # The leader, from just outside the point to just short of the
        # name. Under about a point and a half of frame there is nothing
        # to lead: the name is already touching its point.
        lx, ly, _side = label
        dist = (lx * lx + ly * ly) ** 0.5
        if dist > 2.6:
            ux, uy = lx / dist, ly / dist
            out.append(
                '      <path class="ajc__line ajc__leader" data-region="%s" '
                'data-line="%s" d="M%.2f %.2f L%.2f %.2f"/>'
                % (region, key,
                   x + ux * 1.5, y + uy * 1.5,
                   x + lx - ux * 1.0, y + ly - uy * 1.0))
    return "\n".join(out)


def map_svg():
    """The world under the routes: coastline only, no borders, no grid.

    Borders would date the map and say nothing about where anybody
    studied; a graticule would make it an instrument. What is wanted is
    the shape of the land, far enough down in the dark that the nineteen
    points are the brightest things in the frame.
    """
    return ('    <svg class="ajc__map" viewBox="0 0 %.4f %.4f" '
            'aria-hidden="true" focusable="false">\n'
            '      <path class="ajc__land" d="%s"/>\n'
            '    </svg>' % (VB_W, VB_H, worldland.LAND))


def constellation_html():
    """The map: nineteen destinations, and the routes out to them.

    The named points are HTML buttons over the top of the SVG, because a
    button is the only thing reliably focusable, announceable and
    clickable; an SVG <circle> with a tabindex is none of the three on
    every browser that matters.

    Offsets are written as cqw — hundredths of the field's own width —
    so a name keeps the clearance it was placed with at every width the
    map is drawn at. The field is the query container; see alumni.css.

    Below 900px the same buttons become a plain list and the map is not
    drawn: nineteen names over a world 360 pixels wide is a puzzle, not
    a map. There is one DOM, and no second markup path that can rot.
    """
    ox, oy = ORIGIN
    total = len(DESTINATIONS)
    points = []
    for i, (key, name, short, country, region,
            lat, lon, nudge, label) in enumerate(DESTINATIONS):
        x, y = place(lat, lon, nudge)
        lx, ly, side = label
        points.append('''      <li class="ajc__item" data-region="%s">
        <button type="button" class="ajc__pt" id="ajc-pt-%s"
                style="--x:%.3f%%;--y:%.3f%%;--lx:%.3fcqw;--ly:%.3fcqw"
                data-point="%s" data-region="%s" data-side="%s"
                aria-expanded="false" aria-controls="ajc-panel">
          <span class="ajc__dot" aria-hidden="true"></span>
          <span class="ajc__label"><span class="ajc__name">%s</span><span class="ajc__country">%s</span></span>
          <span class="sr-only">Destination %d of %d. %s, %s. Open details.</span>
        </button>
      </li>''' % (region, key,
                  x / VB_W * 100, y / VB_H * 100,
                  lx / VB_W * 100, ly / VB_W * 100,
                  key, region, side, short, country,
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

  <div class="ajc__field" data-constellation-field>
%(map)s

    <svg class="ajc__lines" viewBox="0 0 %(vw).4f %(vh).4f"
         aria-hidden="true" focusable="false">
      <g class="ajc__routes">
%(lines)s
      </g>
      <g class="ajc__flights" data-flights></g>
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
</div>''' % {"filters": "\n".join(filters), "total": total,
              "map": map_svg(), "lines": routes_svg(),
              "vw": VB_W, "vh": VB_H,
              "ox": ox / VB_W * 100, "oy": oy / VB_H * 100,
              "points": "\n".join(points)}


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
        for key, name, _short, country, r, _lat, _lon, _n, _l in DESTINATIONS:
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
        # Every chapter carries the field of work, with batch, institution,
        # location and biography details filled only where they are supplied.
        meta.append('<span class="ajp__metaItem"><b>Path</b>%s</span>' % person["field"])

        biography = person.get("biography", "")
        biography_html = ('<p class="ajp__bio">%s</p>' % escape(biography)
                          if biography else "")
        missing = []
        if not person["batch"]:
            missing.append("batch year")
        if not person["institution"]:
            missing.append("institution attended")
        if not person["place"]:
            missing.append("current city")
        missing.append("a personal reflection")
        if len(missing) == 1:
            missing_text = missing[0]
        else:
            missing_text = ", ".join(missing[:-1]) + " and " + missing[-1]
        awaiting_html = ('<p class="ajp__await"><em>[Still to be supplied: %s.]'
                         '</em></p>' % escape(missing_text))

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
      %s
      <p class="ajp__meta">%s</p>
      %s
    </div>
  </article>''' % (person["key"], person["key"], side, _plate(person), i + 1,
                   person["name"], person["role"], biography_html,
                   "".join(meta), awaiting_html))
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
