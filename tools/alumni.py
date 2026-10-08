#!/usr/bin/env python3
"""The alumni journey: destinations, voices and named alumni on one page.

The Alumni page is a journey rather than a directory — campus, departure, a
field of destinations, the alumni themselves, the pathways out, the index and
the way back — and every one of those chapters is built from the lists below.
This file is the whole of the page's content. Nothing on it is written into
tools/pages/alumni.html except the chapters' own copy.

Destination institutions come from the sanitized, institution-only
alumni-destinations.json. The raw registration workbook and row-level review
remain outside this repository. Previously published map coordinates are kept.
Additional campus reference points have public location sources recorded in
the dataset; they do not identify the campus an alumnus attended. Institutions
without reviewed locations stay in the directory without guessed coordinates.

The page also includes source-linked biographies and four photographs
supplied by CIRS. Batch years and unverified personal details are omitted.

WHAT IS DELIBERATELY MISSING.

Batch years. Cities. Which alumnus went to which institution,
except for Hari Om Jani, whose biography records the National University of
Singapore. Extended biographies are included for all four named alumni.
ALUMNI-CONTENT.md tracks what is still missing.

TO PUBLISH MORE.

  A destination — add a sanitized institution entry to
  alumni-destinations.json. Verified coordinates add a map point; entries
  without them remain in the directory.

  An alumnus — add to ALUMNI. Name and one verified line is enough to
  publish. Add an extended account in "biography" when one is supplied;
  batch, institution, place and portrait appear as soon as they are filled
  in, and are silently left out until they are.

  A quotation — add to VOICES, with the name of the person who said it.

Nothing else has to change. The map, the region filters, the index, the
counts and the editorial chapters all build from these lists.
"""

import os
import json
from pathlib import Path
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import robinson          # noqa: E402  the projection, shared with make-worldmap.py
import alumniregister    # noqa: E402  who registered where; see make-alumni-register.py
# Country boundaries are generated offline in the same projection as the markers.
COUNTRIES = json.loads(Path(__file__).with_name("alumni-countries.json").read_text(encoding="utf-8"))["countries"]
COUNTRY_NAMES = {"United States of America": "United States"}

# ------------------------------------------------------------------
# The regions, in the order the map and the index use. The key is what
# every point and row carries in data-region, and what the filter
# buttons switch on.
# ------------------------------------------------------------------
REGIONS = [
    ("india", "India"),
    ("uk",    "United Kingdom"),
    ("us",    "United States"),
    ("canada", "Canada"),
    ("apac",  "Asia&ndash;Pacific"),
    ("europe", "Europe"),
    ("middle-east", "Middle East"),
]

# ------------------------------------------------------------------
# THE MAP
#
# The field is a map of the world, drawn in Robinson (see
# tools/robinson.py for why that projection and not a web one), with
# CIRS on it where Coimbatore is and every destination where it is.
# Distance on it means distance. Nothing is art-directed except which
# side of a point its name sits on, with small disclosed display offsets
# where several institutions share a city.
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
    anybody travels, and straight lines out of one point form a
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
# Previously published points retain their reviewed coordinates. Publicly
# reviewed campus reference locations carry coordinate_review provenance.
# Neither kind of point confirms an individual's campus or attendance.
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
DESTINATION_RECORDS = json.loads(
    Path(__file__).with_name("alumni-destinations.json").read_text(encoding="utf-8")
)
DESTINATIONS = [(d["key"], d["name"], d["short"], d["country"], d["region"],
                 d["lat"], d["lon"], tuple(d["nudge"]), tuple(d["label"]))
                for d in DESTINATION_RECORDS]
MAPPED_DESTINATIONS = [d for d in DESTINATIONS if d[5] is not None and d[6] is not None]


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
#   portrait          the identified photograph supplied by CIRS
#   then_portrait     "" — the school-era photograph for the Then/Now
#                     reveal. Both halves must be real for it to run.
# ------------------------------------------------------------------
ALUMNI = [
    {"key": "hari-om-jani", "name": "Hari Om Jani",
     "role": "Materials research, University of Oxford",
     "field": "Science and research",
     "batch": "", "place": "", "institution": "National University of Singapore",
     "portrait": "assets/img/alumni/hari-om-jani.webp", "portrait_size": (732, 732),
     "portrait_alt": "Hari Om Jani wearing glasses and a navy jacket against a plain background.",
     "then_portrait": "",
     "biography": (
         "He moved to Singapore to pursue his bachelor’s degree in Physics and PhD "
         "at the National University of Singapore. He continued there as a Research "
         "Fellow and later as a Senior Research Fellow, before moving to Oxford in "
         "2022 as a Marie Skłodowska-Curie Fellow. In 2024, Hari was selected as a "
         "Young Scientist for the Lindau Nobel Laureate Meeting and was awarded the "
         "Royal Society University Research Fellowship, through which he established "
         "his research group, Designer Quantum Materials for Devices. He took up his "
         "current position at Queen’s College and the Department of Materials in 2026."
     ),
     "sources": [("The Queen’s College profile", "https://www.queens.ox.ac.uk/people/prof-hariom-jani/")]},

    {"key": "soham-desai", "name": "Soham Desai",
     "role": "Strength and conditioning coach",
     "field": "Sport",
     "batch": "", "place": "", "institution": "",
     "portrait": "assets/img/alumni/soham-desai.webp", "portrait_size": (497, 618),
     "portrait_alt": "Soham Desai standing with his arms folded in a navy sports shirt.",
     "then_portrait": "",
     "biography": (
         "Soham Desai has been the backbone of one of the most celebrated cricket "
         "teams in the world. He served for five years as the lead Strength and "
         "Conditioning Coach of the Indian Cricket Team, and is currently with the "
         "IPL team Lucknow Super Giants."
     ),
     "sources": [("Indian Express profile", "https://indianexpress.com/article/sports/cricket/strength-and-conditioning-coach-soham-desai-jasprit-bumrah-ind-vs-eng-10134895/"), ("Soham Desai’s 2026 update", "https://www.linkedin.com/posts/soham-desai-91799698_ipl2026-strengthandconditioning-activity-7444994473845219328-afGw")]},

    {"key": "divyaj-dt", "name": "Divyaj DT",
     "role": "Goalkeeper in India youth squads",
     "field": "Sport",
     "batch": "", "place": "", "institution": "",
     "portrait": "assets/img/alumni/Divyaj-dt.jpg", "portrait_size": (387, 516),
     "portrait_alt": "Divyaj DT in a red NorthEast United football kit.",
     "then_portrait": "",
     "biography": (
         "Divyaj is an alumnus of Alchemy International Football Academy & Baroda "
         "Football Academy, progressing to the NorthEast United FC, where he "
         "currently plays as Goalkeeper, and has represented India internationally "
         "at the youth levels, including the India U19 and India U20 national teams. "
         "He was a part of the squad that became champions at the SAFF U19 Championship."
     ),
     "sources": [("AIFF: 2023 SAFF U19 squad", "https://www.the-aiff.com/index.php/article/india-squad-for-saff-u-19-championship-announced"), ("AIFF: 2023 SAFF U19 champions", "https://www.the-aiff.com/article/champs-triple-strike-blue-colts-send-crippled-pakistan-packing"), ("AIFF: 2025 AFC U20 qualifying squad", "https://www.the-aiff.com/article/india-squad-for-2025-afc-u20-asian-cup-qualifiers-in-laos-announced")]},

    {"key": "shashwat-santosh", "name": "Shashwath Santosh",
     "role": "Designer, Google Creative Lab",
     "field": "Design",
     "batch": "", "place": "", "institution": "",
     "portrait": "assets/img/alumni/shashwath-santosh.webp", "portrait_size": (1194, 796),
     "portrait_alt": "Shashwath Santosh seated outdoors and speaking into a microphone.",
     "then_portrait": "",
     "biography": (
         "Shashwath Santosh is an industrial and product designer based in New York, "
         "currently working at Google Creative Lab on AI-driven experiences like "
         "Gemini, Project Astra, and Genie. His website can be found at "
         "shashwathsantosh.com."
     ),
     "sources": [("Shashwath Santosh’s portfolio", "https://shashwathsantosh.com/")]},
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
     "copy": "Design schools also appear among the destinations, and one of the four "
             "alumni the school has named works as a designer.",
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


def mapped_region_count(region):
    return sum(1 for d in MAPPED_DESTINATIONS if d[4] == region)


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
    for key, _n, _s, _c, region, lat, lon, nudge, label in MAPPED_DESTINATIONS:
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


def country_name(country):
    return COUNTRY_NAMES.get(country["name"], country["name"])


def country_total(name):
    return sum(d[3] == name for d in DESTINATIONS)


def map_svg():
    """Natural Earth country hit areas, aligned with the existing Robinson points.

    One roving keyboard stop; arrows traverse shapes. The country selector and
    region buttons offer the same directory without requiring map navigation.
    """
    shapes = []
    for i, country in enumerate(COUNTRIES):
        name = country_name(country)
        label = "%s: %d institutions." % (name, country_total(name))
        shapes.append('<path class="ajc__land" d="%s" fill-rule="evenodd" '
                      'data-country="%s" data-count="%d" aria-label="%s"/>' %
                      (country["path"], escape(name, quote=True), country_total(name),
                       escape(label, quote=True)))
    return ('<svg class="ajc__map" viewBox="0 0 %.4f %.4f" '
            'role="group" aria-label="World institution destinations">%s</svg>' %
            (VB_W, VB_H, "\n".join(shapes)))


def country_controls():
    names = sorted({country_name(c) for c in COUNTRIES} | {d[3] for d in DESTINATIONS})
    options = ''.join('<option value="%s">%s (%d)</option>' %
                      (escape(n, quote=True), escape(n), country_total(n)) for n in names)
    return ('<div class="ajc__countryControls" data-directory-controls hidden>'
            '<label for="ajc-country">Browse a country or territory</label>'
            '<select id="ajc-country"><option value="">Choose a country or territory</option>%s</select>'
            '<button type="button" data-country-open>Open directory</button>'
            '<a href="#aj-destinations">Full text directory</a></div>' % options)


def constellation_html():
    """The mapped destinations and their illustrative routes from Siruvani.

    The named points are HTML buttons over the top of the SVG, because a
    button is the only thing reliably focusable, announceable and
    clickable; an SVG <circle> with a tabindex is none of the three on
    every browser that matters.

    Offsets are written as cqw — hundredths of the field's own width —
    so a name keeps the clearance it was placed with at every width the
    map is drawn at. The field is the query container; see alumni.css.

    At small map widths decorative dots and country controls remain visible.
    Dense institution labels give way to the complete directory below.
    """
    ox, oy = ORIGIN
    total = len(MAPPED_DESTINATIONS)
    points = []
    dots = []
    for i, (key, name, short, country, region,
            lat, lon, nudge, label) in enumerate(MAPPED_DESTINATIONS):
        short = next(d for d in DESTINATION_RECORDS if d["key"] == key).get("map_short", short)
        x, y = place(lat, lon, nudge)
        lx, ly, side = label
        dots.append('<circle cx="%.3f" cy="%.3f" r=".95"/>' % (x, y))
        points.append('''      <li class="ajc__item" data-region="%s">
        <button type="button" class="ajc__pt" disabled id="ajc-pt-%s"
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

    filters = ['      <button type="button" class="ajc__filter" data-filter="all" '
               'aria-haspopup="dialog">Browse all <span class="ajc__fcount">%d</span></button>' % len(DESTINATIONS)]
    for key, label in REGIONS:
        filters.append(
            '      <button type="button" class="ajc__filter" data-filter="%s" '
            'aria-haspopup="dialog">%s <span class="ajc__fcount">%d</span></button>'
            % (key, label, region_count(key)))

    return '''<div class="ajc" data-constellation>
  <div class="ajc__bar">
    <div class="ajc__filters" role="group" aria-label="Browse institutions by region" data-directory-controls hidden>
%(filters)s
    </div>
    <p class="ajc__status" data-constellation-status role="status">Showing %(total)d mapped destinations. The directory below lists all %(all)d institutions.</p>
  </div>

  %(controls)s
  <p class="ajc__hint" data-map-hint role="status">Select a country to explore its institutions.</p>
  <div class="ajc__field" data-constellation-field>
%(map)s

    <svg class="ajc__mapMarkers" viewBox="0 0 %(vw).4f %(vh).4f" aria-hidden="true" focusable="false">%(dots)s</svg>

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

  <p class="ajc__source"><a href="#aj-destinations">Read the full institution directory</a>. Points locate reviewed campus references, not confirmation of the campus attended; small display offsets separate nearby institutions. Routes are illustrative. Counts describe institutions in this directory, not alumni totals. Countries with no entries remain available to explore. Illustrative boundaries: <a href="https://www.naturalearthdata.com/about/terms-of-use/">Natural Earth</a>, 1:50m, via world-atlas 2.0.2; Robinson projection. Additional location data: <a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a> and the linked campus sources.</p>
  <dialog class="ajc__directory" id="ajc-panel" aria-labelledby="ajc-panel-name" aria-describedby="ajc-panel-note" data-lenis-prevent>
    <div class="ajc__dialogBar">
      <p class="aj-label">The institution directory</p>
      <button type="button" data-panel-close autofocus>Close<span class="sr-only"> directory</span></button>
    </div>
    <div class="ajc__dialogHead">
      <h3 class="serif" id="ajc-panel-name">All institutions</h3>
      <p id="ajc-panel-note">Alumni-reported institutions are not confirmation of an individual’s attendance or campus. Points show reviewed campus references. Entries without reviewed coordinates are listed, not plotted. Alumni named under an institution registered it themselves through the Alumni Registration Form, and are shown by name, years at CIRS and course only.</p>
    </div>
    <div class="ajc__dialogTools">
      <label for="ajc-search">Search this directory</label>
      <input id="ajc-search" type="search" placeholder="Institution, country or alumnus" autocomplete="off">
      <button type="button" data-panel-all>Browse all institutions</button>
    </div>
    <p data-panel-count role="status"></p>
    <ul class="ajc__results" data-panel-results></ul>
    <p data-panel-empty hidden>No institutions are listed for this country in the current directory.</p>
  </dialog>
%(alumni)s
</div>''' % {"filters": "\n".join(filters), "total": total, "all": len(DESTINATIONS),
              "map": map_svg(), "controls": country_controls(), "lines": routes_svg(),
              "vw": VB_W, "vh": VB_H,
              "ox": ox / VB_W * 100, "oy": oy / VB_H * 100,
              "points": "\n".join(points), "dots": "".join(dots),
              "alumni": alumni_templates()}


def alumni_at(key):
    """Who registered at an institution, as (name, years, course), by name."""
    return [(n, y, c) for k, n, y, c in alumniregister.REGISTER if k == key]


def alumni_templates():
    """Each institution's registered alumni, as an inert <template>.

    The directory dialog clones one in under its institution's row when it
    lists that institution; nothing else on the page reads them, so the
    index below stays a list of institutions. Every name and course is
    escaped here: they were typed into a form by the public.
    """
    out = []
    for key, *_rest in DESTINATIONS:
        people = alumni_at(key)
        if not people:
            continue
        rows = []
        for name, years, course in people:
            meta = " \u00b7 ".join(p for p in ("CIRS " + years, course) if p.strip())
            rows.append('      <li><span class="ajc__alumnusName">%s</span>'
                        '<span class="ajc__alumnusMeta">%s</span></li>'
                        % (escape(name), escape(meta)))
        out.append('  <template id="ajd-alumni-%s">\n'
                   '    <p class="ajc__alumniHead">%d registered alumn%s</p>\n'
                   '    <ul class="ajc__alumni">\n%s\n    </ul>\n'
                   '  </template>'
                   % (escape(key, quote=True), len(people),
                      "us" if len(people) == 1 else "i", "\n".join(rows)))
    return "\n".join(out)


# ==================================================================
# The index
# ==================================================================

def destinations_html():
    """The index: text first, grouped by region, filterable and searchable.

    Names and search attributes are escaped from the sanitized institution
    dataset.
    """
    groups = []
    for region, label in REGIONS:
        rows = []
        for key, name, _short, country, r, _lat, _lon, _n, _l in DESTINATIONS:
            if r != region:
                continue
            search = name.replace("&mdash;", "-").lower() + " " + country.lower()
            review = next(d for d in DESTINATION_RECORDS if d["key"] == key).get("coordinate_review")
            campus = review["campus"] if review else ""
            source = ('\n            <a class="ajd__locationSource" href="%s">Campus location source<span class="sr-only"> for %s</span></a>' %
                      (escape(review["sources"][0], quote=True), escape(name))) if review else ""
            campus_attr = ' data-campus="%s"' % escape(campus, quote=True) if campus else ""
            rows.append('''          <li class="ajd__row" data-key="%s" data-region="%s" data-search="%s" data-mapped="%s"%s>
            <span class="ajd__name">%s</span>
            <span class="ajd__country">%s</span>%s
          </li>''' % (escape(key, quote=True), escape(region, quote=True), escape(search, quote=True),
                     "true" if _lat is not None and _lon is not None else "false", campus_attr, escape(name), escape(country), source))
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
    """Show the alumnus's identified portrait or a fallback plate."""
    initials = "".join(part[0] for part in person["name"].split()[:2]).upper()
    src = person["then_portrait"] if kind == "then" else person["portrait"]
    label = "School years" if kind == "then" else "Today"
    if src:
        width, height = person.get("portrait_size", (900, 1200))
        alt = person.get("portrait_alt", person["name"] + ".")
        return ('<img class="ajp__img" src="%s" alt="%s" '
                'width="%d" height="%d" loading="lazy" decoding="async">'
                % (escape(src, quote=True), escape(alt, quote=True), width, height))
    return '''<span class="ajp__plate" data-plate="%s">
          <span class="ajp__initials" aria-hidden="true">%s</span>
          <span class="ajp__plateLabel sc">%s</span>
          <span class="ajp__plateNote"><em>[Portrait to be supplied by the school, with
            the alumnus&rsquo;s permission.]</em></span>
        </span>''' % (kind, initials, label)


# How far a portrait may be drawn past its own pixels. Three of the supplied
# portraits are small (387 to 732px); in the one-column layout a tablet gets,
# the frame would stretch them to 707 CSS px — up to 3.65 times over on a
# 2x screen. The figure stops at this multiple of the photograph's own width
# in the 3:4 frame instead, which leaves every desktop and phone layout
# exactly as it was. The school's larger originals are what will lift it.
PORTRAIT_STRETCH = 1.25


def _figure_cap(person):
    """A max-width for the figure, or "" when the portrait can fill any frame."""
    if not person.get("portrait"):
        return ""
    width, height = person.get("portrait_size", (900, 1200))
    cap = round(min(width, height * 3 / 4) * PORTRAIT_STRETCH)
    return ' style="max-width:%dpx"' % cap if cap < 720 else ""


def people_html():
    """The four named alumni in the original alternating editorial layout."""
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
        source_links = " ".join(
            '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' %
            (escape(url, quote=True), escape(label))
            for label, url in person.get("sources", []))
        sources_html = '<p class="ajp__sources">%s</p>' % source_links if source_links else ""

        chapters.append('''  <article class="ajp" id="alumnus-%s" data-person="%s" data-side="%s">
    <div class="ajp__figure"%s>
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
  </article>''' % (person["key"], person["key"], side, _figure_cap(person), _plate(person), i + 1,
                   person["name"], person["role"], biography_html,
                   "".join(meta), sources_html))
    return "\n".join(chapters)


def voices_html():
    """Complete published quotations and exact attribution, in a card grid."""
    scenes = []
    for voice in VOICES:
        batch = voice["batch"]
        scenes.append('''  <figure class="ajv rv" data-voice="%s">
    <p class="ajv__mark" aria-hidden="true">&ldquo;</p>
    <blockquote class="ajv__quote">
      <p class="serif" data-split>%s</p>
    </blockquote>
    <figcaption class="ajv__by">
      <span class="ajv__name">%s</span>
%s
    </figcaption>
  </figure>''' % (voice["key"], voice["quote"], voice["name"],
                 '<span class="ajv__batch">%s</span>' % escape(batch) if batch else ""))
    return '<div class="wrap ajv-grid">' + "\n".join(scenes) + "</div>"


# ==================================================================
# The pathways
# ==================================================================

def pathways_html():
    """Five pathways in one scrolling frame, each naming its evidence.

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
        'aria-label="Go to %s"><span aria-hidden="true">%02d</span></button></li>' % (i, p["label"], i + 1)
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
