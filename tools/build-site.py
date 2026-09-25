#!/usr/bin/env python3
"""Assemble every page of the site from shared partials and per-page content.

The site used to be one long page. It is now ten, which means the header, the
menu and the footer appear ten times — and a menu that has to be edited in ten
files is a menu that goes stale in nine of them. So no page is authored as a
whole file. Each page is:

    tools/partials/       the chrome every page shares
    tools/pages/<slug>.html   only the sections unique to that page
    PAGES below           title, menu label, banner copy, grouping

and this script writes <slug>.html at the repository root. Edit those inputs,
never the generated pages — a rebuild overwrites them, and CI fails if what is
committed does not match what a rebuild produces.

The menu is generated from PAGES, so adding a page here puts it in the menu of
all ten pages at once. Cross-page links are rewritten from the section anchors
the original single page used: SECTION_PAGE says which page each section now
lives on, and a link to a section on the current page stays a plain #anchor
rather than reloading the page you are already reading.

    python3 tools/build-site.py
"""

import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alumni
import artattack
import artswall
import blog
import founder
import houses
import documents as docs
import blogposts
import crossroads
import mathchallenge
import creativewriting
import captures
import theatre
import festivals
import leadership
import history

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_BUST = "b=102"

# Questions to settle before an application is submitted.
HERO_DATES = '''    <dl class="pagehero__dates">
      <div>
        <dt>Entry class</dt>
        <dd>Ask Admissions<small>Confirm availability for your child</small></dd>
      </div>
      <div>
        <dt>Application</dt>
        <dd>Portal available<small>Confirm the intake before submitting</small></dd>
      </div>
      <div>
        <dt>Dates and assessment</dt>
        <dd>Confirm directly<small>Ask about the schedule, format and location</small></dd>
      </div>
    </dl>'''

# The headlines the News hero cycles through. Every one is a story already on
# the page below — the reel is a way in, not a second copy of the news — so
# each carries the anchor of the section it came from, and nothing appears
# here that the page does not already report in full.
NEWS_FLASH = [
    ("Final examination, May 2026",
     "Twenty-four candidates, twenty-four diplomas", "#latest"),
    ("CBSE, March&ndash;April 2026",
     "Class XII Management closes the year on a 94% average", "#results"),
    ("4&ndash;9 August 2025",
     "English Week fills the portals with storytelling and spell bees", "#highlights"),
    ("25 July 2025",
     "Science Expo draws fifty schools to 140 models", "#highlights"),
    ("7&ndash;11 July 2025",
     "Mathematics Week ends with a house-wise Maths Run", "#highlights"),
    ("From 19 April 2025",
     "Seva Week takes students to homes, centres and temples", "#more"),
    ("19&ndash;21 January 2026",
     "Chinmaya Olympiad in Mathematics and Science", "#diary"),
]



# The menu. PAGES says what a page IS; this says where it sits and in what
# order, so a page can exist and be linked without being listed — Home, which
# the wordmark already leads to, Important Documents, which School Information
# and the footer link to, and Academics, whose two curriculum cards are linked
# from Our Results and the footer while Our Results waits for the results
# themselves.
MENU = [
    ("Vision",               ["founder", "why-cirs", "school-history", "leadership"]),
    ("Student Life",         ["the-cirs-experience", "curriculum", "our-results", "sports",
                              "houses", "our-laurels", "math-challenge"]),
    ("Literary Excellence",  ["crossroads", "blog", "creative-writing"]),
    ("Art, Culture & Music", ["captures", "art-attack", "festivals", "theatre",
                              "cultural-gallery"]),
    ("Connect",              ["school-info", "news", "admissions", "parent-portal", "alumni"]),
]

def newsflash_html():
    """The cycling headline reel under the News hero's buttons.

    The first item is marked on in the markup rather than by script, so the
    reel reads as a single headline before newsFlash() ever runs and stays
    one if it never does — no script, no motion, no reel, but never an empty
    strip. The rest are hidden with visibility, which keeps their links out
    of the tab order and off the accessibility tree while they are not up.
    """
    items = []
    for i, (when, what, anchor) in enumerate(NEWS_FLASH):
        on = " is-on" if i == 0 else ""
        items.append(f'''        <p class="newsflash__item{on}">
          <span class="newsflash__when">{when}</span>
          <a class="newsflash__what" href="{anchor}">{what}</a>
        </p>''')
    return f'''    <div class="newsflash" id="newsFlash">
      <p class="newsflash__label"><span class="newsflash__dot" aria-hidden="true"></span>Latest</p>
      <div class="newsflash__items">
{chr(10).join(items)}
      </div>
    </div>'''


# slug -> page definition. Order here is the order in the menu.
#   nav    the label in the menu and the <title>
#   group  the menu column it sits under
#   eyebrow/heading/lead  the banner at the top of the page
#   uc     False to leave off the under-construction note. Nothing sets
#          it: the note belongs at the foot of every page, the home page
#          included, because every page is still being filled in
PAGES = {
    "index": {
        "nav": "Home",
        "title": "Chinmaya International Residential School — Siruvani, Coimbatore",
        "description": "A co-educational residential school on a hundred acres in the Siruvani "
                       "foothills — CBSE and the International Baccalaureate, Grades V to XII.",
        "banner": None,
        "sheet": "home",
    },
    "news": {
        "nav": "News",
        "title": "News | The CIRS Journal",
        "description": "The CIRS Journal: school news, results and stories from Chinmaya "
                       "International Residential School in Siruvani, Coimbatore.",
        # The journal supplies its own masthead, feature and archive. Its
        # opening is readable immediately, without the shared video hero.
        "sheet": "news-journal",
        "cache_suffix": "-journal-11",
        "litehead": True,
        "uc": False,
    },
    "founder": {
        "litehead": True,
        "nav": "Founder",
        "title": "Our Founder — Pujya Gurudev Swami Chinmayananda",
        "description": "Pujya Gurudev Swami Chinmayananda, 1916–1993: the teacher whose "
                       "vision of an education that transforms rather than informs became "
                       "Chinmaya International Residential School.",
        # No banner and no hero from the shared builders. This page opens on a
        # composition of its own — oversized letters with the archival
        # photograph set into them — and brings its own sheet to do it.
        "banner": None,
        "sheet": "founder",
        "cache_suffix": "-founder-16",
    },
    "why-cirs": {
        "nav": "Why CIRS",
        "title": "Why CIRS",
        "description": "Who we are, what the school is recognised for, and the Junior and Senior "
                       "Schools that carry it.",
        "sheet": "why-cirs",
        "cache_suffix": "-why-cirs-10",
        # No banner. The page used to open on a purple plate carrying "Why
        # CIRS." and a line about a community of knowledge, with the first
        # photograph below it. The photograph is the better opening, so it
        # now runs full-bleed from the very top of the page and the header
        # floats over it — the same composition the home page and the
        # Founder page open on.
        "banner": None,
    },
    "school-history": {
        "nav": "School History",
        "title": "School History | The CIRS Archive",
        "description": "The CIRS archive: Pujya Gurudev's idea, the land bought one rupee at a "
                       "time, the inauguration on 6 June 1996 and the milestones since, each "
                       "with its source.",
        # No banner and no hero. The page opens on its own dark composition —
        # the school's records set back at shallow depths behind the title —
        # then tells six chapters in one bounded sticky sequence and ends on
        # the complete archive. Every record is written from tools/history.py,
        # which names each one's source; tools/make-history.py cuts the images.
        "banner": None,
        "sheet": "history",
        "cache_suffix": "-history-1",
        # The chapters carry their own visible index and "View all
        # milestones", so the floating "On this page" control would repeat it.
        "jump": False,
        # Nothing on this page is a placeholder any more: what could not be
        # sourced was taken out and is listed in tools/history.py.
        "uc": False,
        "closing": ("Have something to add", "to the archive?",
                    [("Write to the school",
                      "mailto:info@cirschool.org?subject=For%20the%20CIRS%20archive",
                      "closing-scene__admissions"),
                     ("View all milestones", "#timeline", "closing-scene__contact")],
                    "Photographs, documents and recollections from any year are welcome at "
                    "info@cirschool.org. The school reads everything it is sent and decides "
                    "what is added; nothing is published automatically."),
    },
    "leadership": {
        "nav": "Leadership",
        "title": "Our Leadership",
        "description": "The people who lead Chinmaya International Residential School, their "
                       "messages in full, and the school's staff and faculty.",
        # No hero and no banner. The page opens on ivory, with the h1 and the
        # first four portraits of the directory together in the first screen:
        # the people are the opening, not a campus photograph above them. It
        # brings its own sheet and script (leadership.css, leadership.js) and
        # the people and messages are data in tools/leadership.py. It keeps
        # the browser's own scroll, so its message links are real history
        # entries (cirs.js). There is no curtain, no "On this page" index —
        # the opening's two links do that — and no under-construction note:
        # nothing on the page is a placeholder.
        "banner": None,
        "sheet": "leadership",
        "cache_suffix": "-leadership-1",
        "litehead": True,
        "jump": False,
        "uc": False,
    },
    "school-info": {
        "nav": "School Information",
        "title": "School Information",
        "description": "Affiliation status, governance, infrastructure and grievance-redressal details for "
                       "Chinmaya International Residential School, with the Important Documents portal.",
        # No banner and no hero. The page opens on "The CIRS Record": four of
        # the school's own certificates laid out as sheets of paper, cut from
        # the PDFs by tools/make-record-previews.py, with the h1 beside them.
        # The opening is ivory, so the header takes dark lettering. The page
        # carries its own section index, so the shared "On this page" button
        # stays off; and the under-construction note gives way to a records
        # notice built from tools/documents.py, at the foot of the page.
        "banner": None,
        "sheet": "records",
        "cache_suffix": "-records-1",
        "litehead": True,
        "jump": False,
        "uc": False,
    },
    "important-documents": {
        "nav": "Important Documents",
        # Reached only by the one-click portal button on School Information —
        # a second main-menu entry for the same material would be clutter the
        # task never asked for.
        "title": "Important Documents",
        "description": "The Important Documents portal for Chinmaya International Residential School — "
                       "CBSE affiliation, statutory certificates, results, circulars and other official "
                       "documents referenced on the School Information page.",
        "banner": ("Important documents", "The Documents <em>Portal.</em>",
                   "Every official document referenced on the School Information page, open in one click. "
                   "Each opens in your browser's own PDF viewer, where it can be read or downloaded with "
                   "the browser's standard controls."),
    },
    "curriculum": {
        "nav": "Curriculum",
        "title": "Curriculum | CBSE & IB Diploma Programme",
        "description": "Follow the academic journey at Chinmaya International Residential School: "
                       "CBSE from Grade V, a choice of CBSE or IB Diploma from Grade XI, "
                       "and the Chinmaya Vision Programme across school life.",
        "sheet": "curriculum",
        "cache_suffix": "-curriculum-7",
        # No banner. The page opens on its own paper composition, built in
        # tools/pages/curriculum.html: the heading beside the Junior School
        # photograph, with the page's own section index under it. That index
        # is visible and labelled, so the floating "On this page" control
        # would be a second copy of it; hence jump False. The opening is on
        # paper, so the header wears dark lettering: hence litehead.
        "banner": None,
        "litehead": True,
        "jump": False,
        "uc": False,
        # One close rather than two: the shared closing scene carries this
        # page's own invitation instead of a separate "next steps" band above it.
        "closing": ("Discuss", "the next stage",
                    [("Ask about subjects",
                      "mailto:info@cirschool.org?subject=Grade%20XI%20and%20XII%20subject%20choices",
                      "closing-scene__admissions"),
                     ("Admissions guide", "admissions.html#apply", "closing-scene__contact"),
                     ("Published results", "our-results.html", "closing-scene__contact")]),
    },
    # A child page of Curriculum, and the first page on this site whose slug
    # names a directory: it is written to curriculum/ib-diploma.html and
    # served at /curriculum/ib-diploma, so the URL says where it belongs. It
    # is deliberately not in MENU — the Curriculum page is the way to it, and
    # a second top-level entry would undo the hierarchy the path states.
    "curriculum/ib-diploma": {
        "nav": "IB Diploma",
        "title": "IB Diploma Programme | CIRS",
        "description": "The IB Diploma Programme at Chinmaya International Residential School "
                       "for Grades XI and XII — academic depth, independent learning, research "
                       "and a global perspective.",
        "banner": ("IB Diploma at CIRS",
                   "IB Diploma Programme, <em>Grades XI and XII.</em>",
                   "Study six subject groups alongside the Diploma core. Ask the school "
                   "which subjects and levels are available for your entry year."),
        "banner_cta": [("See the subject groups", "#groups", "primary"),
                       ("Compare pathways", "curriculum.html#pathways", "ghost")],
        "sheet": "ibdp",
        "cache_suffix": "-ibdp-1",
        "jump": True,
        "uc": False,
    },
    # The CBSE pathway's own page, the IB Diploma's twin: served at
    # /curriculum/cbse, reached from the Curriculum page, and not in MENU for
    # the same reason. It wears the IB page's sheet, which is the curriculum
    # family's furniture — the breadcrumb, the cards and the habits strip.
    "curriculum/cbse": {
        "nav": "CBSE",
        "title": "CBSE Curriculum, Grades V to XII | CIRS",
        "description": "The CBSE curriculum at Chinmaya International Residential School from "
                       "Grade V to Grade XII — a broad foundation, the Board examinations in "
                       "Grades X and XII, and three senior streams.",
        "banner": ("Central Board of Secondary Education, New Delhi",
                   "CBSE, <em>Grades V to XII.</em>",
                   "A broad foundation, the Board examinations in Grades X and XII, and a choice "
                   "of Engineering, Medicine or Management in the senior years."),
        "sheet": "ibdp",
    },
    "the-cirs-experience": {
        "logintab": ("Student Portal", "https://cirs.in/school/"),
        "nav": "THE CIRS EXPERIENCE",
        "title": "THE CIRS EXPERIENCE",
        "description": "Residential life at CIRS, the shape of an ordinary school day, and the "
                       "hundred-acre campus it happens on.",
        # No banner and no hero key: this page opens on a hero of its own,
        # built in tools/pages/the-cirs-experience.html — a drifting line of
        # oversized lettering with photographs dealt up through it. It carries
        # the page's h1 and its own id="top". That hero is off-white, so the
        # header cannot float over it in white lettering: hence litehead.
        "sheet": "student-life",
        "cache_suffix": "-student-life-9",
    },
    "sports": {
        "nav": "Our Sports",
        "title": "Sports & Laurels — Built in the Arena | CIRS",
        "description": "Built in the Arena — Athletics, house competition, physical discipline and sporting laurels at Chinmaya International Residential School, Coimbatore.",
        "sheet": "sports",
        "cache_suffix": "-sports-2",
        # No banner from the shared builder. Like CIRS Captures, this page
        # opens on a film the reader scrubs — five seconds from a wet ball to
        # the field at sunrise under the Ghats — and the h1 is the one line
        # that arrives once it has ended. The body.sports block in
        # assets/css/filmintro.css is where this frame's own decisions live.
        "banner": None,
        "opening": {
            "video": "sports-field",
            "poster": "sports-field-poster.jpg",
            "title": "CIRS Sports",
            # With no scripting nothing seeks, so what stays up is the first
            # frame — a macro of a wet ball, not the field. The line's usual
            # place is the treeline of a frame that is never reached, and on
            # this one it lands on the lit crest of the leather and washes
            # out. Low on the frame it has the dark underside behind it, at
            # 11.9:1. Captures needs no such move: its first frame is dark
            # wherever the line falls.
            "noscript_title_top": "88%",
        },
    },
    "houses": {
        "barehead": True,
        "nav": "Our Houses",
        "title": "Our Houses | CIRS",
        "description": "The four houses of Chinmaya International Residential School — "
                       "Vasishtha, Valmiki, Vishwamitra and Vyasa — their colours, symbols "
                       "and a dated archive of published inter-house results.",
        "banner": None,
        "sheet": "houses",
        "cache_suffix": "-houses-1",
    },
    "crossroads": {
        "nav": "Crossroads",
        # The old site filed this under a "Creative Corner" this site does not
        # have; Student Life is where the arts and the clubs live here.
        "title": "Crossroads | CIRS Monthly Magazine",
        "description": "The archive of Crossroads, the monthly magazine of Chinmaya "
                       "International Residential School — a student-run initiative to foster "
                       "literary talent, edition by edition.",
        # No flat band and no video hero: an archive opens on its own
        # masthead, built in tools/pages/crossroads.html.
        "banner": None,
    },
    "blog": {
        "nav": "CIRS Blog",
        "title": "Ideas from CIRS | CIRS Blog",
        "description": "Student articles first published in The Crossroads, collected "
                       "as a journal of ideas from CIRS.",
        # No banner and no hero from the shared builders. A publication opens on
        # its own masthead, which the page brings with it, and it brings its own
        # sheet to set type larger than anything else on this site.
        "banner": None,
        # The front page wears its own sheet, not the one the articles wear:
        # it is a news stand and they are reading pages, and they share no
        # markup. blognews.css is scoped to body.blognews for that reason.
        "sheet": "blognews",
        "cache_suffix": "-blog-editorial-1",
        "jump": False,
        "uc": False,
        # Newsreader carries the Blog interface and prose; its grid remains distinct.
        "litehead": True,
    },
    "cultural-gallery": {
        "nav": "CIRS Cultural Gallery",
        "title": "Arts, Music & Theatre",
        "description": "Music, theatre and the visual arts at Chinmaya International Residential "
                       "School, as a wall of the school's photographs.",
        # The one page on the site that is not a document. It is a field of
        # photographs filling the window, which takes the scroll and opens a
        # photograph where another page would follow a link — so it wears the
        # header but no footer, and no banner above the fold, because it is
        # all fold. See "wall" in build() below.
        "wall": True,
    },
    # ---- pages in preparation -------------------------------------------
    # Each is a real page with a real banner and a plain account of what will
    # live on it, rather than a blank route. "soon" is what the body is built
    # from; see soon_html below.
    "our-results": {
        "nav": "Our Results",
        "title": "Our Results",
        "description": "Board results, university placements and the record behind them at "
                       "Chinmaya International Residential School.",
        "sheet": "results",
        "cache_suffix": "-results-14",
        "uc": False,
        "banner": None,
        # The book carries its own chapter controls.
        "jump": False,
    },
    "our-laurels": {
        "nav": "Our Laurels",
        "title": "Our Laurels",
        "description": "Competitions won, representative honours and the CIRS students who "
                       "carried them.",
        "banner": ("Our laurels", "Honours, <em>Named.</em>",
                   "Competitions won, representative honours, and the students who carried them."),
        "soon": ([("Inter-school", "Competition names, years and placings"),
                  ("District and state", "Selections and results"),
                  ("National", "Representative honours and participation"),
                  ("Inter-house", "The house championship and its holders")],
                 "competition names, years, placings and the students involved, to be supplied "
                 "by the sports office and the activities office",
                 [("sports.html", "Our Sports")]),
    },
    "math-challenge": {
        "nav": "Math Challenge",
        "title": "Math Challenge",
        "description": "The Math Challenge at Chinmaya International Residential School — "
                       "monthly problems for four grade zones, and the habits of mind they "
                       "are set to build.",
        # No banner from the shared builder. This page opens on a field of
        # mathematics it brings itself, and it is the one dark page on the
        # site — assets/css/matharena.css, scoped to body.matharena.
        "banner": None,
        "sheet": "matharena",
    },
    "creative-writing": {
        "nav": "Creative Writing",
        "title": "Creative Writing | Words become worlds. | CIRS",
        "description": "A curated anthology of poetry by students of Chinmaya "
                       "International Residential School.",
        # This anthology supplies its own typographic opening and h1.
        "banner": None,
        "sheet": "cwriting",
        "cache_suffix": "-anthology-2",
        "jump": False,
        "uc": False,
    },
    "captures": {
        "nav": "CIRS Captures",
        "title": "CIRS Captures",
        "cache_suffix": "-captures-journal-2",
        # Not "as its students see it", which this page said while it was a
        # placeholder: none of these files records who took it, so the page
        # makes no claim about who did.
        "description": "Photographs of wildlife, the grounds, performances and gatherings "
                       "in the CIRS Captures collection.",
        # No banner from the shared builder. This page opens on six seconds of
        # a camera coming out of the dark, which the reader scrubs with the
        # scroll, and the h1 is the one line that arrives once the film has
        # ended. See film_html above, and the body.captures block in
        # assets/css/filmintro.css for what this page tunes for its own frame.
        "banner": None,
        "opening": {
            "video": "captures-camera",
            "poster": "captures-camera-poster.jpg",
            "title": "CIRS Captures",
            # Keep the camera and title at their original scroll distances:
            # film to 252vh, final frame held to 277vh, title up by 324vh and
            # read to 360vh. The photograph then dissolves across the whole
            # frame by 400vh and rests for 30vh before the featured handoff.
            "phases": [0.5860, 0.6442, 0.7535, 0.8372, 0.9302],
            # The film's last frame as a still, for reduced motion, a film
            # that fails and no scripting (tools/make-captures-shot.py).
            "still": "captures-camera-final.jpg",
            # Two cuts of the supplied butterfly photograph: the portrait
            # one keeps the subject in view on narrow screens.
            "shot": {
                "src": "captures-shot.jpg", "size": (1425, 1080),
                "narrow": "captures-shot-portrait.jpg", "narrow_size": (810, 1080),
                "alt": captures.LEAD_CAPTION,
            },
            # The featured photographs (tools/pages/captures.html) take over
            # from the opening's last frame, and the ramp to paper follows
            # them rather than the film, so the page writes its own seam.
            "seam": False,
        },
        # The gallery has replaced the placeholder it was waiting behind, and
        # with it the under-construction note: what it listed as coming is
        # here. The page body is tools/pages/captures.html; the photographs,
        # their captions and their layout are tools/captures.py.
        "uc": False,
    },
    "art-attack": {
        # The page body is tools/pages/art-attack.html; its works, credits and
        # photographs are tools/art-attack.json, read by tools/artattack.py and
        # cut by tools/make-art-attack.py. It opens on the supplied film (see
        # assets/css/filmintro.css for its frame), which gives way to a
        # photograph of students at work and then, on scroll, the first
        # finished work (assets/js/artattack.js). The film carries the h1.
        "sheet": "artattack",
        "cache_suffix": "-art-attack-4",
        "nav": "CIRS Art Attack",
        "title": "CIRS Art Attack",
        "description": "Painting, drawing, craft and the things made for the stage by the students "
                       "of Chinmaya International Residential School.",
        "banner": None,
        # The note that replaced the under-construction banner is specific:
        # what is missing, and where to send it. It is the page's own.
        "uc": False,
        "opening": {
            "video": "art-attack-opening",
            "poster": "art-attack-opening-poster.jpg",
            "still": "art-attack-opening-final.jpg",
            "still_element": True,
            "title": "CIRS Art Attack",
            "title_markup": '<span class="film__art-prefix">CIRS </span><span class="film__art-name">Art Attack</span>',
            "pending": True,
        },
    },
    "festivals": {
        # The page body is tools/pages/festivals.html and its sheet
        # assets/css/festivals.css. It opens on its own composition of seven
        # of the school's photographs rather than on a film, so there is no
        # "opening" here; the photographs, their provenance and the India
        # calendar are in tools/festivals.py.
        "sheet": "festivals",
        "cache_suffix": "-festivals-year-1",
        "nav": "CIRS Festivals",
        "title": "CIRS Festivals",
        "description": "Seven festivals kept through the school year at Chinmaya International "
                       "Residential School, from Raksha Bandhan to Holi, in the school's own "
                       "photographs.",
        "banner": None,
        "uc": False,
    },
    "theatre": {
        # The page body is tools/pages/theatre.html; its sheet is
        # assets/css/culture.css, shared by the three Art, Culture & Music
        # pages that open on a film.
        "sheet": "culture",
        "cache_suffix": "-theatre-acts-1",
        "nav": "CIRS Theatre",
        "title": "CIRS Theatre",
        "description": "Productions, rehearsal and the stage at Chinmaya International "
                       "Residential School.",
        "banner": None,
        "opening": {
            "video": "theatre-opening",
            "poster": "theatre-opening-poster.jpg",
            "still": "theatre-opening-final.jpg",
            "still_element": True,
            "title": "CIRS Theatre",
            "phases": (0.70, 0.78, 0.91),
        },
        # After the opening, three acts — Anand Utsav, Masquerades and Class
        # Presentations — written from tools/theatre.py, with a sheet and a
        # script of their own (assets/css/theatre.css, assets/js/theatre.js).
        # The page closes on its own request for missing photographs and
        # recordings, which says precisely what the shared under-construction
        # note says in general, so the note is left off.
        "uc": False,
    },

    "admissions": {
        "nav": "Admissions",
        "title": "Admissions",
        "description": "Admissions information for Chinmaya International Residential School: "
                       "the application portal, published fee schedule and questions to confirm with the school.",
        # A hero rather than the flat band: this is the page that has to
        # persuade, not merely inform.
        #
        # Admissions carries its own quiet, document-led layout beneath the
        # shared honeycomb hero. The sheet is scoped by body.admissions.
        "sheet": "admissions",
        "cache_suffix": "-admissions-27",
        "hero_split": False,
        "hero": ("Admissions", "Admissions <em>Guide.</em>",
                 "Explore the application portal and published fee schedule. Confirm current "
                 "class availability, assessment arrangements and key dates with the Admissions Office."),
        "hero_media": ("admissions-honeycomb.jpg", "admissions-hero.webm",
                       "admissions-hero.mp4", 1920, 960),
        "hero_cta": [("Open the application portal",
                      "https://easycollege.in/cirs/school/application/index.aspx", "primary"),
                     ("Understand the process", "#apply", "ghost")],
        "hero_extra": HERO_DATES,
        "hero_placeholder": "Header animation &mdash; admissions<br>photograph or looping video<br>to be supplied",
        "jump": True,
        "popup": False,
        "uc": False,
    },
    "parent-portal": {
        "nav": "Parent Portal",
        # In the menu proper now, beside Alumni — both are doors for people
        # already attached to the school rather than pages about it. It is
        # removed from the drawer's utility strip at the same time, so the
        # drawer does not offer the same link twice.
        "title": "Parent Portal",
        "description": "Fee payment and the parent login for CIRS. The Parent Portal on this "
                       "site is not open yet; both run on the school's existing systems.",
        "banner": ("Parents", "Parent <em>Portal.</em>",
                   "A secure area for parents. It is not open yet &mdash; so this page carries the "
                   "fee payment and the parent login the school runs today, and the people to ask."),
        # Shared with School Information — see assets/css/connect.css.
        "sheet": "connect",
        "cache_suffix": "-portal-photo-1",
        # the page is itself an under-construction notice; the standard footer
        # one underneath it would only say the same thing twice.
        "uc": False,
    },
    "alumni": {
        "nav": "Alumni",
        "title": "Where CIRS Takes You | Alumni",
        "description": "Reconnect with CIRS, browse published alumni cohort records, and explore university destinations and alumni stories.",
        # The Alumni page supplies its own opening image and carries the h1.
        # Page styles and search behavior live in alumni.css and alumni-journey.js.
        "banner": None,
        "sheet": "alumni",
        "cache_suffix": "-alumni-7",
        "uc": False,
    },
}

# Which page each of the old single-page section anchors now lives on.
SECTION_PAGE = {
    # "about" is gone: the section that carried it is now the page's top,
    # and carries id="top" instead. A bare #about should fail the link
    # check loudly rather than resolve to an anchor that no longer exists.
    "junior": "why-cirs", "senior": "why-cirs",
    "quote": "leadership", "people": "leadership",
    "academics": "curriculum",
    "life": "the-cirs-experience", "day": "the-cirs-experience", "campus": "the-cirs-experience",
    "athletics": "sports", "fields": "sports", "achievements": "sports",
    "arts": "cultural-gallery",
    "pathways": "alumni",
    "latest": "news", "diary": "news",
    "admissions": "admissions", "apply": "admissions", "examination": "admissions",
    "visit": "admissions", "before": "admissions", "fees": "admissions",
    "voices": "admissions", "gallery": "admissions", "contact": "admissions",
    "advert": "admissions",
    "top": "index", "main": None,   # main is on every page; top only on home
}


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        sys.exit(f"build-site: missing {rel}")
    return open(path, encoding="utf-8").read()


def rewrite_links(html, slug):
    """Turn the old single-page #anchors into links that work across pages."""
    def swap(m):
        anchor = m.group(1)
        # Curriculum now has its own #pathways; the legacy alias points to
        # Alumni, so keep this page's banner action on its own section.
        if slug == "curriculum" and anchor == "pathways":
            return m.group(0)
        if anchor not in SECTION_PAGE:
            return m.group(0)          # href="#" placeholders, and #main
        target = SECTION_PAGE[anchor]
        if target is None:
            return m.group(0)
        if target == slug:
            # Already on this page. An anchor equal to the slug is the old
            # single page's name for the whole section, which is now the page
            # itself — so it means the top, not a section that no longer exists.
            return 'href="#top"' if anchor == slug else m.group(0)
        page = "index.html" if target == "index" else f"{target}.html"
        # A link to #admissions means the Admissions page, not a section on it.
        # The old single page had a section per page; now the page IS the
        # section, so an anchor equal to the slug becomes a plain page link.
        if target == "index" or anchor == target:
            return f'href="{page}"'
        return f'href="{page}#{anchor}"'
    return re.sub(r'href="#([A-Za-z0-9_-]+)"', swap, html)


def to_depth(html, slug):
    """Point a nested page's relative references back up to the root.

    Every page on this site is written as though it sits at the root, because
    until now every page did: "assets/css/cirs.css", "curriculum.html". A page
    whose slug carries a directory — "curriculum/ib-diploma" — is served from
    that directory, and the browser resolves those against it, so they have to
    climb back out first.

    Doing it here, once, on the finished HTML is what keeps the partials, the
    page sources and the other forty-two pages from having to know about it:
    a flat page is returned untouched and byte-identical.

    Left alone: anything absolute (a scheme, or a leading /), a same-page
    #anchor, and the empty href.
    """
    depth = slug.count("/")
    if not depth:
        return html
    up = "../" * depth

    def climb(m):
        attr, ref = m.group(1), m.group(2)
        if not ref or ref.startswith(("#", "/", "http://", "https://",
                                      "mailto:", "tel:", "data:")):
            return m.group(0)
        return f'{attr}="{up}{ref}"'

    html = re.sub(r'\b(href|src|poster)="([^"]*)"', climb, html)
    def climb_srcset(m):
        candidates = []
        for candidate in m.group(2).split(","):
            fields = candidate.strip().split()
            if not fields:
                continue
            ref = fields[0]
            if not ref.startswith(("#", "/", "http://", "https://", "data:", "blob:")):
                fields[0] = up + ref
            candidates.append(" ".join(fields))
        return f'{m.group(1)}="{", ".join(candidates)}"'
    html = re.sub(r'\b(srcset)="([^"]*)"', climb_srcset, html)
    # The og:image and twitter:image carry their path in content=, not in an
    # href, and a social preview fetching curriculum/assets/img/og.jpg gets a
    # 404 and shows no card at all. Only a relative assets/ path is touched.
    return re.sub(r'\b(content)="(assets/[^"]*)"', climb, html)


def menu_group_index(slug):
    return next((i for i, (_, slugs) in enumerate(MENU) if slug in slugs), 0)


def nav_html(slug):
    """Five typographic groups with accessible, directly linked panels."""
    active = menu_group_index(slug)
    out = ['<nav class="drawer__menu" aria-label="CIRS sections">']
    arrival_y = (14, -10, 12, -12, 12)
    arrival_z = (-200, -120, -260, -160, -220)
    for i, (group, slugs) in enumerate(MENU):
        gid = "dnav-" + re.sub(r"[^a-z]+", "-", group.lower()).strip("-")
        selected = "true" if i == active else "false"
        current_class = " is-active" if i == active else ""
        state = "" if i == active else " hidden"
        out.append('  <div class="drawer__item">')
        out.append(f'    <button type="button" class="drawer__group{current_class}" '
                   f'id="{gid}-button" data-menu-index="{i}" '
                   f'aria-controls="{gid}-panel" aria-expanded="{selected}" '
                   f'style="--enter-delay:{i * 40}ms;--enter-y:{arrival_y[i]}px;'
                   f'--enter-z:{arrival_z[i]}px">'
                   f'<span class="drawer__group-number" aria-hidden="true">{i + 1:02d}</span>'
                   f'<span class="drawer__group-word">{esc(group)}</span></button>')
        out.append(f'    <section class="drawer__panel" id="{gid}-panel" '
                   f'aria-labelledby="{gid}-button"{state}>')
        out.append(f'      <p class="drawer__panel-kicker">{esc(group)} / {i + 1:02d}</p>')
        out.append("      <ul>")
        for sl in slugs:
            page = PAGES[sl]
            here = ' aria-current="page"' if sl == slug else ""
            out.append(f'        <li><a href="{sl}.html"{here}>{esc(page["nav"])}</a></li>')
        out += ['      </ul>', '    </section>', '  </div>']
    out.append('</nav>')
    return "\n".join(out)


def soon_html(page):
    """The body of a page that exists but is not written yet.

    A blank route tells a visitor nothing and looks broken. This says what the
    page is for, lists what will be on it, names who it is waiting on, and
    points at the nearest page that is finished — so the menu can carry the new
    structure now without any of it dead-ending.
    """
    rows, ask, links = page["soon"]
    rail = "\n".join(f"      <div><dt>{t}</dt><dd>{d}</dd></div>" for t, d in rows)
    onward = ""
    if links:
        buttons = "\n".join(
            # btn--ghost is white, for photographs and dark grounds; this
            # section is paper, where it measured 1.1:1. The outline is ink.
            f'      <a class="btn btn--outline" href="{href}">{label}</a>' for href, label in links)
        onward = ('\n\n    <div class="soon__onward rv">\n' + buttons + "\n    </div>")
    return (
        '<section class="section" id="what">\n'
        '  <div class="wrap">\n'
        '    <div class="sec-head rv">\n'
        '      <p class="marker"><span class="sc">In preparation</span></p>\n'
        '      <h2 class="serif h2" data-split>What will be <em>on this page.</em></h2>\n'
        '    </div>\n\n'
        '    <dl class="factrail rv">\n'
        f'{rail}\n'
        '    </dl>\n\n'
        '    <p class="note rv" style="margin-top:24px"><em>[Placeholder &mdash; '
        f'{ask}.]</em></p>{onward}\n'
        '  </div>\n'
        '</section>')

def film_html(slug, page):
    """The opening of a page that starts on a film the reader scrubs.

    CIRS film pages share this furniture. Each page supplies its own footage,
    title and, where needed, phase boundaries; the scrubbing mechanics live in
    assets/css/filmintro.css and assets/js/filmintro.js.

    The film remains the opening's only dominant element. Our Sports adds one
    discreet scroll cue over its first frames; CIRS Captures dissolves from
    the camera's final frame to the photograph declared by "shot" in its
    entry (see the photo dissolve in filmintro.js).
    """
    film = page["opening"]
    phases = film.get("phases")
    attrs = f' data-film-phases="{" ".join(f"{v:g}" for v in phases)}"' if phases else ""
    if film.get("fps", 24) != 24:
        attrs += f' data-film-fps="{film["fps"]:g}"'
    if film.get("shot"):
        attrs += " data-film-photo"
    # The ramp to paper, unless the page puts it further down itself.
    seam = ("" if film.get("seam") is False else
            '\n<div class="film__seam" aria-hidden="true"></div>')
    shot = film.get("shot")
    # After the line in the document, so it is read after it, and over it on
    # screen by z-index. See assets/js/filmintro.js for the full-frame dissolve.
    shot = (
        '    <div class="film__shot" data-film-shot>\n'
        '      <picture>\n'
        f'        <source media="(max-aspect-ratio: 6/5)"\n'
        f'                srcset="assets/img/{shot["narrow"]}" width="{shot["narrow_size"][0]}" height="{shot["narrow_size"][1]}">\n'
        f'        <img class="film__photo" src="assets/img/{shot["src"]}" width="{shot["size"][0]}" height="{shot["size"][1]}"\n'
        f'             alt="{shot["alt"]}"\n'
        '             loading="lazy" decoding="async">\n'
        '      </picture>\n'
        '    </div>\n'
        if shot else "")
    if film.get("pending") or film.get("still"):
        attrs += " data-film-pending"
    title = film.get("title_markup", f'<span class="film__line">{film["title"]}</span>')
    still_element = bool(film.get("still_element"))
    still = (f'    <img class="film__still" src="assets/img/{film["still"]}" '
             'alt="" aria-hidden="true" width="1280" height="720" fetchpriority="high">\n'
             if film.get("still") and still_element else "")
    cue = (
        '    <p class="film__scroll-cue" data-film-scroll-cue>'
        '<span aria-hidden="true">↓</span><span>Scroll to discover</span></p>\n'
        if slug == "sports" else ""
    )
    return f'''<section class="film" id="{slug}-opening" data-film{attrs}>
  <div class="film__stage">
{still}    <video class="film__video" data-film-video
           width="1280" height="720"
           poster="assets/img/{film["poster"]}"
           preload="auto" muted playsinline disablepictureinpicture
           aria-hidden="true" tabindex="-1">
      <!-- H.264 first, which is the other way round from the rest of this
           site. These files are not played but seeked, several times a
           second, and H.264 is the one codec every browser that has it
           decodes in hardware — so it is the path that scrubs without
           stuttering wherever it exists. The VP9 is for the browsers built
           without the proprietary decoder, which would otherwise have no
           opening at all. Both are the same length at 24fps, so the mapping
           in filmintro.js holds whichever one is picked. -->
      <source src="assets/video/{film["video"]}.mp4" type="video/mp4">
      <source src="assets/video/{film["video"]}.webm" type="video/webm">
    </video>
{cue}    <h1 class="film__title" data-film-title>{title}</h1>
{shot}  </div>
</section>{seam}'''


def esc(text, attr=False):
    """The magazine's own punctuation, made safe to put in a page.

    Article text is raw prose lifted from a PDF: it contains ampersands and
    quotation marks that mean themselves. Escaping is what keeps a headline
    that opens on a quoted sentence from ending the attribute it sits in.
    """
    out = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return out.replace('"', "&quot;") if attr else out


def article_html(page):
    """A reading page for a complete student article from The Crossroads."""
    post = page["post"]
    issue = post["issue"]
    pdf = f"assets/documents/crossroads/crossroads-issue-{issue:02d}.pdf"
    when = f'        <span>{esc(post["date"])}</span>\n' if post["date"] else ""
    by = esc(blog.byline(post))
    subtitle = (f'      <p class="art__subtitle">{esc(post["subtitle"])}</p>\n'
                if post.get("subtitle") else "")
    image = ""
    if post.get("image"):
        dimensions = (f' width="{post["image_width"]}" height="{post["image_height"]}"'
                      if post.get("image_width") and post.get("image_height") else "")
        image = f'''    <figure class="art__hero">
      <img src="assets/img/blog/{esc(post["image"], attr=True)}"
           alt="{esc(post.get("image_alt", ""), attr=True)}"
          {dimensions} decoding="async">
      <figcaption>{esc(post.get("image_caption", "Image supplied for the web edition."))}</figcaption>
    </figure>

'''
    body = blog.body_html(post)
    return f'''<article class="art" id="top">
  <header class="art__head">
    <div class="art__shell">
      <nav class="art__breadcrumb" aria-label="Breadcrumb">
        <a href="blog.html">Ideas from CIRS</a><span aria-hidden="true">/</span><span>{esc(post["section"])}</span>
      </nav>
      <p class="art__edition">The Crossroads <span aria-hidden="true">/</span> Issue {issue}</p>
      <h1 class="art__title">{esc(post["title"])}</h1>
{subtitle}      <div class="art__credits">
        <span>{by}</span>
{when}        <span>{blog.reading_time(post)} min read</span>
      </div>
    </div>
  </header>
  <div class="art__layout">
    <aside class="art__rail" aria-label="Original publication">
      <p>First published in</p>
      <strong>The Crossroads<br>Issue {issue}</strong>
      <a href="{pdf}">Read the issue (PDF) <span aria-hidden="true">↗</span></a>
      <a href="crossroads.html">All Crossroads issues</a>
    </aside>
    <div class="art__content">
{image}      <div class="art__body">
{body}
      </div>
    </div>
  </div>
  <div class="art__shell">
    <footer class="art__foot">
      <p>Originally published in <em>The Crossroads</em>, Issue {issue}.</p>
      <div><a href="{pdf}">Read the complete issue (PDF)</a>
        <a href="blog.html">Back to all stories</a></div>
    </footer>
    {blog.related_html(post)}
  </div>
</article>'''


def banner_html(page):
    eyebrow, heading, lead = page["banner"]
    cta = "\n".join(f'      <a class="btn btn--{variant} btn--lg" href="{href}">{label}</a>'
                    for label, href, variant in page.get("banner_cta", []))
    cta = f'    <p class="pagehead__cta">\n{cta}\n    </p>\n' if cta else ""
    return f'''<section class="pagehead on-purple" id="top" data-ground="#1E1626">
  <div class="wrap pagehead__inner">
    <p class="marker"><span class="sc">{eyebrow}</span></p>
    <h1 class="serif" data-split>{heading}</h1>
    <p class="lead">{lead}</p>
{cta}  </div>
</section>'''


HOME_TAB = '''<a class="htab" href="index.html" data-magnetic aria-label="Home">
        <span class="htab__icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2.6 7.6 9 2.2l6.4 5.4M4.4 9.2v6.2h9.2V9.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="htab__label">Home</span>
      </a>'''


NEWS_TAB = '''<a class="htab htab--news" href="news.html" data-magnetic aria-label="News">
        <span class="htab__icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2.4 3.6h9.4v10.8H3.6a1.2 1.2 0 0 1-1.2-1.2V3.6Z" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"/><path d="M11.8 6.6h3.8v6.6a1.2 1.2 0 0 1-1.2 1.2h-2.6" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"/><path d="M4.8 6.4h4.6M4.8 9h4.6M4.8 11.6h2.8" stroke="currentColor" stroke-width="1.15" stroke-linecap="round"/></svg>
        </span>
        <span class="htab__label">News</span>
      </a>'''


STUDENT_PORTAL_TAB = '''<a class="htab htab--portal" href="https://cirs.in/school/"
         target="_blank" rel="noopener" data-magnetic aria-label="Open Student Portal in a new tab">
        <span class="htab__icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2.2 6.2 9 2.8l6.8 3.4L9 9.6 2.2 6.2Z" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"/><path d="M4.6 7.5v4.1c1.2 1.1 2.7 1.7 4.4 1.7s3.2-.6 4.4-1.7V7.5M15.8 6.3v4.3" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="htab__label">Student Portal</span>
      </a>'''


def hero_html(page):
    """The page's opening, at full height, merging into the scroll below it.

    It carries the call to action and whatever standing block the page needs
    under it — the dates on Admissions, the headline reel on News — because
    the notice box that used to hold them is gone: one opening statement
    rather than a banner and then a box repeating it.

    The media, the buttons and that trailing block all come from the page's
    own entry in PAGES, so a second hero is a few lines of data rather than a
    second copy of this markup.

    Admissions' media is a honeycomb of the school's own photographs, built by
    tools/make-honeycomb.py: a seamlessly looping video, with the still of the
    same wall as its poster so the panel is complete before the video arrives
    and stays complete if it never does.

    Both are graded to the site's purple and darkened along the diagonal the
    headline sits on, so the scrim above them stays light. Change either and
    re-measure with tools/check-contrast.py.
    """
    eyebrow, heading, lead = page["hero"]
    poster, webm, mp4, vw, vh = page["hero_media"]
    cta = "\n".join(f'      <a class="btn btn--{variant} btn--lg" href="{href}">{label}</a>'
                    for label, href, variant in page.get("hero_cta", []))
    cta = f'    <p class="pagehero__cta">\n{cta}\n    </p>\n' if cta else ""
    extra = page.get("hero_extra", "")
    split_attr = ' data-split' if page.get("hero_split", True) else ''
    video_load = ' preload="none"' if page.get("sheet") == "admissions" else ' autoplay'
    return f'''<section class="pagehero" id="top" data-ground="#0E0B12">
  <div class="pagehero__media" style="background-image:url('assets/img/{poster}?{CACHE_BUST}')">
    <video class="pagehero__video"{video_load} muted loop playsinline
           poster="assets/img/{poster}?{CACHE_BUST}" aria-hidden="true"
           width="{vw}" height="{vh}" fetchpriority="high">
      <source src="assets/video/{webm}?{CACHE_BUST}" type="video/webm">
      <source src="assets/video/{mp4}?{CACHE_BUST}" type="video/mp4">
    </video>
  </div>
  <div class="pagehero__scrim" aria-hidden="true"></div>
  <div class="wrap pagehero__inner">
    <p class="marker"><span class="sc">{eyebrow}</span></p>
    <h1 class="serif"{split_attr}>{heading}</h1>
    <p class="lead">{lead}</p>
{cta}{extra}
  </div>
</section>'''


JUMP_MARK = "<!-- on-this-page -->"


def jump_html(body):
    """Build the right-hand index from the page's own sections.

    Labels come from each section's small-caps marker, or from its heading
    where it has none, so the index cannot drift out of step with the
    headings — there is nothing to keep in sync. A section whose headline is
    a sentence names itself for the index instead, with data-jump-label.
    A page with fewer than two places to go gets no index at all.
    """
    items = []
    for m in re.finditer(r'<section([^>]*\bid="([^"]+)"[^>]*)>(.*?)</section>', body, re.S):
        attrs, sid, inner = m.group(1), m.group(2), m.group(3)
        label = (re.search(r'\bdata-jump-label="([^"]*)"', attrs)
                 or re.search(r'<span class="sc">(.*?)</span>', inner, re.S)
                 or re.search(r'<h[23][^>]*>(.*?)</h[23]>', inner, re.S))
        if not label:
            continue
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", label.group(1))).strip()
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)
        if text and all(text != t for _, t in items):
            items.append((sid, text))
    if len(items) < 2:
        return ""
    links = "\n".join(f'      <a href="#{i}">{t}</a>' for i, t in items)
    # A native <details>: the summary comes first, so Tab from it enters the
    # first link, and the list opens and closes with no script at all.
    # pages.js only adds the conveniences (Escape, outside click, the
    # current section). It is emitted straight after the page's banner, so
    # the keyboard meets it before the content, not after.
    return f'''<nav class="jump" aria-label="On this page">
  <details class="jump__details">
    <summary class="jump__toggle" title="On this page">
      <svg width="14" height="12" viewBox="0 0 14 12" fill="none" aria-hidden="true"><path d="M1 1h12M1 6h12M1 11h7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      <span class="jump__label">On this page</span>
    </summary>
    <div class="jump__panel" id="jumpPanel">
      <p aria-hidden="true">On this page</p>
{links}
    </div>
  </details>
</nav>'''


POPUP = '''<div class="pop" id="admissionsPop" role="dialog" aria-modal="true"
     aria-labelledby="popTitle" aria-describedby="popNote">
  <div class="pop__card">
    <button type="button" class="pop__close" id="popClose" aria-label="Close">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.5 3.5l9 9m0-9l-9 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    </button>
    <p class="pop__label" id="popTitle">Contact Admissions Office</p>
    <h2 class="serif">We are here <em>to help.</em></h2>
    <p class="pop__note" id="popNote">Ask the Admissions Office to confirm the current
      application window, assessment arrangements or availability of a school visit.</p>

    <div class="pop__row">
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true"><path d="M3.4 18.6l1.1-3.9a7.6 7.6 0 1 1 2.9 2.8l-4 1.1Z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M8.3 8.1c.2-.5.5-.5.8-.5h.5c.2 0 .4 0 .6.5l.6 1.4c.1.2 0 .4-.1.6l-.4.4c-.1.2-.2.3-.1.5.3.6 1.1 1.5 1.9 1.9.2.1.4 0 .5-.1l.5-.5c.2-.2.3-.2.5-.1l1.4.7c.2.1.3.3.3.5v.5c0 .5-.4.9-.9 1-1.6.2-3.9-1.3-5.2-3.4-.7-1.1-1-2.3-.9-3.4Z" fill="currentColor"/></svg>
      <span>
        <a href="https://wa.me/919360461572">+91 93604 61572</a>
        <small>WhatsApp</small>
      </span>
    </div>

    <div class="pop__row">
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true"><rect x="2.6" y="4.6" width="16.8" height="12.8" rx="1.6" stroke="currentColor" stroke-width="1.4"/><path d="m3.4 5.8 7.6 5.6 7.6-5.6" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>
      <span>
        <a href="mailto:admissions@cirschool.org">admissions@cirschool.org</a>
        <small>Email</small>
      </span>
    </div>
  </div>
</div>'''


def closing_html(footer, closing):
    """Give the shared closing scene a page's own heading and links.

    The scene stays the site's one closing treatment; a page whose close says
    something more specific than "Explore Admissions" says it here, rather
    than adding a second invitation band just above the scene.
    """
    first, second, links, *note = closing
    start = footer.index('<h2 class="closing-scene__title"')
    end = footer.index("</div>", footer.index('<div class="closing-scene__links">')) + len("</div>")
    anchors = "\n".join(f'        <a class="{cls}" href="{href}">{label}</a>'
                         for label, href, cls in links)
    return (footer[:start]
            + f'<h2 class="closing-scene__title" id="closing-scene-title">\n'
              f'        <span>{first}</span>\n        <span>{second}</span>\n      </h2>\n'
              + (f'      <p class="closing-scene__note">{note[0]}</p>\n' if note else "")
            + f'      <div class="closing-scene__links">\n{anchors}\n      </div>'
            + footer[end:])


def founder_fig(slot, cls="", sizes=""):
    """One photograph on the Founder page, or an honest gap where one is owed.

    The gap is not a grey box: it names the photograph that belongs there, so
    the page reads as an archive still being gathered rather than as something
    broken. tools/founder.py decides which of the two this is.
    """
    _, alt, label, *caption = founder.SLOTS[slot]
    src = founder.path(slot)
    klass = f"ffig {cls}".strip()
    if src is None:
        return (f'<figure class="{klass} ffig--gap" role="img" aria-label="{label}">'
                f'<span class="ffig__mark">Archive image pending</span>'
                f'<span class="ffig__what">{label}</span></figure>')
    extra = f' sizes="{sizes}"' if sizes else ""
    figcaption = f'<figcaption>{caption[0]}</figcaption>' if caption else ""
    return (f'<figure class="{klass}"><img src="{src}?{CACHE_BUST}" alt="{alt}" '
            f'loading="lazy" decoding="async"{extra}>{figcaption}</figure>')


def expand_figs(html):
    """Turn every {{FIG:slot}} and {{FIG:slot|class}} into a figure."""
    def swap(m):
        body = m.group(1)
        slot, _, cls = body.partition("|")
        return founder_fig(slot.strip(), cls.strip())
    return re.sub(r"\{\{FIG:([^}]+)\}\}", swap, html)


def crossroads_stories_covers():
    issues = [i for i in crossroads.issues() if i["cover"] and i["pdf"]][:7]
    if not issues:
        return ""
    # User-selected car cover (Issue 30), keeping its own PDF destination.
    featured = next((i for i in issues if i["number"] == 30), issues[0])
    featured_index = issues.index(featured)
    # Clockwise slots around the centre: three on each side. Keeping the DOM in
    # issue order lets the browser animate one stable carousel step at a time.
    rear_slot = {1: 2, 2: 4, 3: 6, 4: 5, 5: 3, 6: 1}
    cards = []
    for index, issue in enumerate(issues):
        delta = (index - featured_index) % len(issues)
        if delta == 0:
            klass = "crossroads-stories__front"
        else:
            slot = rear_slot[delta]
            klass = f"crossroads-stories__rear crossroads-stories__rear--{slot}"
        cards.append(f'<a class="{klass}" href="{issue["pdf"]}" '
                     f'aria-label="Read Crossroads {issue["label"]}">'
                     f'<img src="{issue["cover"]}" alt="Crossroads {issue["label"]} cover" '
                     'width="300" height="420" loading="lazy" decoding="async"></a>')
    return '<div class="crossroads-stories__media"><div class="crossroads-stories__stack">' + ''.join(cards) + '</div></div>'


def crossroads_latest(feature=False):
    issue = next((i for i in crossroads.issues() if i["latest"] and i["pdf"]), None)
    if not issue:
        return ""
    if feature and issue["cover"]:
        return (f'<a class="crossroads-archive-hero__feature" href="{issue["pdf"]}" '
                f'aria-label="Read the latest issue: {issue["label"]} (PDF)">'
                f'<img src="{issue["cover"]}" alt="" width="300" height="420" loading="lazy" decoding="async">'
                f'<span>Latest issue · {issue["label"]}</span></a>')
    if feature:
        return ""
    return (f'<a class="crossroads-archive-hero__secondary" href="{issue["pdf"]}">'
            'Read the latest issue <span aria-hidden="true">↗</span></a>')


def crossroads_html():
    """The archive wall: every edition of Crossroads, newest first.

    A cover is one of two things — the school's own scan, or the designed
    typographic placeholder for an issue not yet digitised. The foot under
    each cover carries the issue number and, when the PDF is up, both ways
    of reading it: open it in a tab, or take the file.
    """
    cards = []
    for issue in crossroads.issues():
        n, label = issue["number"], issue["label"]
        mods = f' crcard--v{issue["variant"]}'
        if issue["latest"]:
            mods += " crcard--latest"

        if issue["cover"]:
            face = (f'<img class="crcover__img" src="{issue["cover"]}?{CACHE_BUST}" '
                    f'alt="Cover of Crossroads {label}" loading="lazy" '
                    f'width="720" height="1008">')
        else:
            face = (f'''<span class="crcover__mast">Crossroads</span>
          <span class="crcover__num" aria-hidden="true">{n:02d}</span>
          <span class="crcover__sub">CIRS Monthly Magazine</span>''')

        cover = f'''<span class="crcover">
          {face}
        </span>'''

        if issue["pdf"]:
            # Two links, side by side in the foot rather than one stacked
            # inside the other: a link within a link is invalid, and a
            # download hidden behind a hover is no download at all on a
            # touch screen.
            cards.append(f'''      <article class="crcard{mods} rv">
        <h3 class="sr-only">Crossroads {label}</h3>
        <a class="crcard__link" href="{issue["pdf"]}" target="_blank" rel="noopener"
           aria-label="Read Crossroads {label} in a new tab">
          {cover}
        </a>
        <div class="crcard__foot">
          <span class="crcard__label">{label}</span>
          <a class="crcard__state" href="{issue["pdf"]}" target="_blank" rel="noopener">Read issue &rarr;</a>
          <a class="crcard__dl" href="{issue["pdf"]}" download
             aria-label="Download Crossroads {label} as a PDF">
            <svg width="13" height="13" viewBox="0 0 14 14" aria-hidden="true"><path d="M7 1v8M3.5 6L7 9.5 10.5 6M2 12.5h10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            Download
          </a>
        </div>
      </article>''')
        else:
            cards.append(f'''      <article class="crcard{mods} is-pending rv">
        <h3 class="sr-only">Crossroads {label}</h3>
        {cover}
        <div class="crcard__foot">
          <span class="crcard__label">{label}</span>
          <span class="crcard__state">PDF will be uploaded soon</span>
        </div>
      </article>''')

    return '<div class="crgrid">\n' + "\n".join(cards) + "\n    </div>"


def crosswall_html():
    """The drifting wall of covers behind the Crossroads masthead.

    Five columns, each a run of covers written out twice. The duplicate is
    what makes the drift endless: assets/js/cirs.js translates a column by
    its own height and the second copy is already in place, so there is no
    jump to hide. Neighbouring columns start in opposite directions.

    Only issues with a cover appear — an issue still waiting for its scan
    has nothing to contribute here, and the typographic placeholder that
    stands in for it on the card would read as a missing image at this size.
    """
    covers = [i["cover"] for i in crossroads.issues() if i["cover"]]
    if not covers:
        return ""

    cols, n = [], 5
    for c in range(n):
        # Dealt round-robin from a list that is already newest-first, so
        # neighbouring columns never show the same cover side by side.
        run = [covers[j] for j in range(c, len(covers), n)]
        while len(run) < 4:                       # a short column would end
            run = run + run                       # mid-drift on a tall screen
        tiles = []
        for copy in (0, 1):
            for src in run:
                wall = src.replace("assets/img/crossroads/",
                                   "assets/img/crossroads/wall/")
                # The second copy is the same file the first already
                # fetched, and only exists to close the loop.
                lazy = ' loading="lazy"' if (copy or c >= 3) else ''
                tiles.append(f'<img class="crwall__cell" src="{wall}?{CACHE_BUST}"'
                             f' alt="" width="300" height="420"{lazy} decoding="async">')
        cols.append(f'      <div class="crwall__col">\n'
                    f'        <div class="crwall__run" data-dir="{1 if c % 2 == 0 else -1}">'
                    + "".join(tiles) + '</div>\n      </div>')

    return ('<div class="crwall" aria-hidden="true">\n'
            + "\n".join(cols) + '\n    </div>')


ON_REQUEST = ('Available from the school office on request &middot; '
              '<a href="mailto:info@cirschool.org">info@cirschool.org</a>')


def doc_meta(d):
    """The date line under a document's title: when it is from or until when
    it holds, and plainly if it has expired. One source for both pages."""
    status = docs.effective_status(d)
    return f'<span class="docmeta docmeta--{status}">{docs.status_text(d)}</span>'


# ---------------------------------------------------------------------------
# The CIRS Record — School Information's document register and the status
# lines around it. All of it is read from tools/documents.py, so the opening's
# sheets, the register and the records notice at the foot of the page can
# never disagree with each other or with the Important Documents portal.
# ---------------------------------------------------------------------------

# What a visitor is told a document IS, in a word or two. The manifest's own
# status says how current it is; availability and upload come first, because a
# document nobody can open should say so before it says anything else.
REGISTER_LABELS = {
    "request":   "Available from the school on request",
    "await":     "Awaiting upload",
    "expired":   "Expired",
    "stale":     "Newer edition awaited",
    "valid":     "Valid",
    "current":   "Current",
    "permanent": "Permanent",
    "dated":     "On file",
    "undated":   "Date not supplied",
}


def register_status(d):
    """The key of the one label a document wears in the register."""
    if docs.is_on_request(d):
        return "request"
    if not docs.is_uploaded(d):
        return "await"
    status = docs.effective_status(d)
    if status == "current":
        return "valid" if d.get("valid_until") else "current"
    return status


def register_date(d):
    """Every date the manifest holds for a document, in the order a reader
    wants them: when it is from, and until when it held."""
    parts = []
    if d.get("issued"):
        parts.append(f"Issued {d['issued']}")
    if d.get("period"):
        parts.append(f"Covers {d['period']}")
    if d.get("valid_until"):
        verb = "ran to" if docs.effective_status(d) == "expired" else "valid to"
        parts.append(f"{verb} {d['valid_until']}" if parts
                     else f"{verb.capitalize()} {d['valid_until']}")
    return " &middot; ".join(parts) or "Date not supplied"


def _plain(html):
    """A title as text, for the search index and for sentences."""
    text = re.sub(r"<[^>]+>", "", html)
    return (text.replace("&amp;", "&").replace("&mdash;", "—")
                .replace("&ndash;", "–").replace("&middot;", "·"))


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", _plain(text).lower()).strip("-")


def _size(d):
    kb = os.path.getsize(os.path.join(ROOT, docs.asset_path(d))) / 1024
    return f"{kb / 1024:.1f} MB" if kb >= 1000 else f"{kb:.0f} KB"


def register_html():
    """The searchable register on School Information: every document in the
    manifest, grouped by its category, with its dates, one status label, and
    View beside Download where there is a file to open. A document the school
    keeps off the site offers a request by email instead, and one not yet
    uploaded offers nothing — never a button that leads nowhere.

    The search box and the filters are written with the hidden attribute and
    shown by assets/js/records.js, so without scripting the register is simply
    the complete list, which is all the controls would ever narrow it to."""
    total = len(docs.DOCUMENTS)
    groups, filters = [], []
    for category, items in docs.by_category():
        slug = _slug(category)
        filters.append(f'          <button type="button" class="reg__filter" data-reg-filter="{slug}" '
                       f'aria-pressed="false">{category} <span class="reg__n">{len(items)}</span></button>')
        rows = []
        for d in items:
            key = register_status(d)
            title_text = _plain(d["title"])
            if key == "request":
                subject = f"Request: {title_text}".replace("&", "and").replace(" ", "%20")
                actions = (f'<a class="reg__act reg__act--ask" href="mailto:info@cirschool.org?subject={subject}">'
                           f'Request by email<span class="sr-only">: {d["title"]}</span></a>')
                fmt = "Held by the school office"
            elif key == "await":
                actions = '<span class="reg__none">Not yet published</span>'
                fmt = "No file yet"
            else:
                path = docs.asset_path(d)
                actions = (f'<a class="reg__act" href="{path}" target="_blank" rel="noopener">'
                           f'View<span class="sr-only"> {d["title"]} (PDF, opens in a new tab)</span></a>'
                           f'<a class="reg__act reg__act--dl" href="{path}" download>'
                           f'Download<span class="sr-only"> {d["title"]} (PDF)</span></a>')
                fmt = f"PDF &middot; {_size(d)}"
            search = f"{title_text} {_plain(d['note'])}".lower().replace('"', "")
            rows.append(f'''          <li class="reg__row reg__row--{key}" id="doc-{d["id"]}" data-reg-text="{search}">
            <div class="reg__doc">
              <p class="reg__title">{d["title"]}</p>
              <p class="reg__note">{d["note"]}</p>
            </div>
            <p class="reg__when">{register_date(d)}<span class="reg__fmt">{fmt}</span></p>
            <p class="reg__state"><span class="rst rst--{key}">{REGISTER_LABELS[key]}</span></p>
            <p class="reg__acts">{actions}</p>
          </li>''')
        noun = "record" if len(items) == 1 else "records"
        groups.append(f'''        <div class="reg__group" data-reg-group="{slug}">
          <h3 class="reg__cat">{category} <span class="reg__n">{len(items)} {noun}</span></h3>
          <ul class="reg__list">
{chr(10).join(rows)}
          </ul>
        </div>''')
    return f'''<div class="reg" data-reg>
      <div class="reg__tools" data-reg-tools hidden>
        <div class="reg__search">
          <label class="reg__label" for="regSearch">Search the register</label>
          <input class="reg__input" id="regSearch" type="search" autocomplete="off" spellcheck="false"
                 placeholder="e.g. fire safety, calendar" aria-describedby="regCount">
        </div>
        <div class="reg__filters" role="group" aria-label="Show one category">
          <button type="button" class="reg__filter" data-reg-filter="all" aria-pressed="true">All <span class="reg__n">{total}</span></button>
{chr(10).join(filters)}
        </div>
        <p class="reg__count" id="regCount" data-reg-count aria-live="polite">Showing all {total} records</p>
      </div>
      <div class="reg__groups" id="doclist">
{chr(10).join(groups)}
      </div>
      <div class="reg__empty" data-reg-empty hidden>
        <p class="reg__emptyhead">No record matches that search.</p>
        <p>Try one word of the title &mdash; &ldquo;fire&rdquo;, &ldquo;calendar&rdquo;,
          &ldquo;affiliation&rdquo; &mdash; or ask the school office at
          <a href="mailto:info@cirschool.org">info@cirschool.org</a>.</p>
        <button type="button" class="reg__reset" data-reg-reset>Clear the search and filters</button>
      </div>
    </div>'''


def doc_sheet_status(doc_id):
    """The status line on one of the opening's sheets: its label and its date,
    so an expired letter can never be laid out there as if it were current."""
    d = next(x for x in docs.DOCUMENTS if x["id"] == doc_id)
    key = register_status(d)
    detail = {
        "valid": f"to {d.get('valid_until', '')}",
        "expired": f"{d.get('valid_until', '')}, renewal awaited",
        "permanent": f"issued {d.get('issued', '')}",
        "dated": f"issued {d.get('issued', '')}",
        "stale": f"issued {d.get('issued', '')}",
    }.get(key, "")
    return (f'<span class="rst rst--{key}">{REGISTER_LABELS[key]}</span>'
            + (f' <span class="rec-tag__when">{detail}</span>' if detail else ""))


def records_notice_html():
    """The notice at the foot of School Information: which records have lapsed,
    which are awaiting a newer edition or an upload, and which are held by the
    school — each named and linked to its row in the register, and counted
    from the manifest so the notice is never out of step with the page."""
    buckets = [("expired", "Expired, renewal awaited"),
               ("stale", "Newer edition awaited"),
               ("await", "Awaiting upload"),
               ("request", "Available from the school on request")]
    rows = []
    for key, label in buckets:
        items = [d for d in docs.DOCUMENTS if register_status(d) == key]
        if not items:
            continue
        links = ", ".join(f'<a href="#doc-{d["id"]}">{d["title"]}</a>' for d in items)
        rows.append(f'''          <div class="rec-notice__row">
            <dt><span class="rst rst--{key}">{label}</span> <span class="rec-notice__n">{len(items)}</span></dt>
            <dd>{links}</dd>
          </div>''')
    return '<dl class="rec-notice__list">\n' + "\n".join(rows) + '\n        </dl>'


def docportal_html():
    """The Important Documents portal itself: every document, grouped, each
    with its date and a one-click view/download link — or, for one not yet
    uploaded, a plain notice that it is awaiting the school rather than a dead
    link, and for one the school keeps off the site, where to ask for it."""
    groups = []
    for category, items in docs.by_category():
        steps = []
        for d in items:
            if docs.is_on_request(d):
                aside = f'<b>On request</b><br>{ON_REQUEST}'
            elif docs.is_uploaded(d):
                aside = (f'<a class="btn btn--outline" href="{docs.asset_path(d)}" target="_blank" '
                         f'rel="noopener">View</a> '
                         f'<a class="btn btn--primary" href="{docs.asset_path(d)}" download>Download</a>'
                         f'<br><small>View opens a tab; download saves the PDF</small>')
            else:
                aside = '<b>Awaiting upload</b><br>To be added by the school'
            meta = f'<br>{doc_meta(d)}'
            steps.append(f'''        <div class="step" id="doc-{d["id"]}">
          <p class="step__n"></p>
          <div>
            <h3 class="serif h3">{d["title"]}</h3>
            <p>{d["note"]}{meta}</p>
          </div>
          <p class="step__aside">{aside}</p>
        </div>''')
        groups.append(f'''      <div class="docportal__group rv">
        <p class="marker"><span class="sc">{category}</span></p>
        <div class="steps">
{chr(10).join(steps)}
        </div>
      </div>''')
    return '<div class="docportal">\n' + "\n".join(groups) + '\n    </div>'


# ---- Our Results: the destinations directory --------------------------
# Built from the Alumni page's own list (tools/alumni.py DESTINATIONS), so the
# two pages cannot disagree about where CIRS students have gone. They did:
# Results carried the eighteen from before NTU Singapore was supplied.

def results_regions_html():
    """The four region links in the destinations panel; each filters the directory."""
    rows = []
    for key, label in alumni.REGIONS:
        rows.append(f'          <li><a href="#directory" data-region-link="{key}">'
                    f'<span class="rb-regions__name">{label}</span> '
                    f'<span class="rb-regions__count">{alumni.region_count(key)}'
                    f'<span class="sr-only"> institutions</span></span></a></li>')
    return "\n".join(rows)


def results_filters_html():
    buttons = [f'        <button type="button" class="is-active" data-filter="all" '
               f'aria-pressed="true">All <span>{alumni.count()}</span></button>']
    for key, label in alumni.REGIONS:
        buttons.append(f'        <button type="button" data-filter="{key}" aria-pressed="false">'
                       f'{label} <span>{alumni.region_count(key)}</span></button>')
    return "\n".join(buttons)


def results_directory_html():
    labels = dict(alumni.REGIONS)
    rows = []
    for key, _label in alumni.REGIONS:
        for _k, name, short, country, region, *_rest in alumni.DESTINATIONS:
            if region != key:
                continue
            search = re.sub(r"&[a-z]+;", " ", f"{name} {short} {country} {labels[region]}").lower()
            rows.append(f'      <li data-region="{region}" data-search="{" ".join(search.split())}">'
                        f'<span>{country}</span>{name}</li>')
    return "\n".join(rows)


def artswall_html():
    """The wall's photographs, as an inert <template> the page's script reads.

    A link to the photograph around an image of its tile copy. Both paths sit
    in attributes check-links.py reads, so a photograph that went missing from
    assets/img/arts/ fails the checks rather than the page. <template> content
    is inert, so naming twenty-eight photographs here costs no requests — the
    script clones what it needs.
    """
    rows = []
    for name, cat, caption in artswall.PHOTOGRAPHS:
        rows.append(f'    <a href="{artswall.full(name)}">'
                    f'<img src="{artswall.thumb(name)}" alt="{caption}" data-cat="{cat}">'
                    f'</a>')
    return ('<template id="wall-plates">\n' + "\n".join(rows) + "\n</template>")


# ============================================================================
# The Houses page
# ----------------------------------------------------------------------------
# Six builders, all reading tools/houses.py, which is the only place a house
# name, colour, symbol or result is written down. The page source holds the
# sections and the prose; these hold everything that is per-house, so a fifth
# house — or a corrected spelling — is one edit in one file and appears in the
# opening frame, the four chapters, the competition archive, the record table
# and the gallery at once.
# ============================================================================


def houses_hero_html():
    """The four zones of the opening frame.

    Each zone is a link to its own chapter, so the whole interaction works
    from the keyboard with nothing added: tab moves between four links, Enter
    follows one, and :focus-visible expands the zone exactly as hover does.
    The name is the link's text rather than a label beside it, which is what
    gives the link its accessible name.

    The photograph is a real <img> and not a background, so it is in the
    accessibility tree with its alt text and the browser can size it. These
    four are the only images on the page that are not lazy — they are the
    fold — and for the same reason they are the only ones with a second
    rendition. A zone is a quarter of the window on a desktop and the whole
    of it on a phone, and "sizes" is the arithmetic of exactly that, so a
    phone fetches 500px and a desktop 900px instead of every visitor taking
    the larger of the two.
    """
    zones = []
    for i, h in enumerate(houses.HOUSES):
        small = houses.img(h["hero"].replace(".jpg", "-500.jpg"))
        zones.append(f'''        <a class="hsxz" id="hero-{h["slug"]}" data-house="{h["slug"]}"
           href="#house-{h["slug"]}" data-houses-zone>
          <span class="hsxz__ph">
            <img src="{houses.img(h["hero"])}" width="900" height="1125"
                 srcset="{small}?{CACHE_BUST} 500w, {houses.img(h["hero"])}?{CACHE_BUST} 900w"
                 sizes="(max-width: 620px) 100vw, (max-width: 900px) 50vw, 25vw"
                 alt="{esc(h["hero_alt"], attr=True)}"
                 {"" if i else 'fetchpriority="high" '}decoding="async">
          </span>
          <span class="hsxz__tint" aria-hidden="true"></span>
          <span class="hsxz__no" aria-hidden="true">{h["number"]}</span>
          <span class="hsxz__body">
            <span class="hsxz__name">{h["name"]}</span>
            <span class="hsxz__meta">{h["colour"]} &middot; {h["symbol"].lower()}</span>
            <span class="hsxz__go">Explore</span>
          </span>
        </a>''')
    return "\n".join(zones)


def houses_chapters_html():
    """One chapter per house, in the order tools/houses.py lists them.

    Each chapter opens with a wipe — a bar in the outgoing house's colour that
    the script contracts, recolours and expands into the incoming one. With no
    script it is a 6px rule in the house's colour, which is a perfectly good
    chapter divider, so nothing is hidden behind the animation.

    The house's own words are a <blockquote> with a <cite>, dated. That is
    deliberate and it is not a motto: no CIRS house motto is documented
    anywhere in this repository, and a line set large under a house name with
    no attribution would read as one.
    """
    chapters = []
    total = len(houses.HOUSES)
    for i, h in enumerate(houses.HOUSES):
        previous = houses.HOUSES[i - 1]["slug"] if i else h["slug"]
        chapters.append(f'''<article class="hch" id="house-{h["slug"]}" data-house="{h["slug"]}"
         data-houses-chapter data-from="{previous}">
  <div class="hch__wipe" aria-hidden="true" data-houses-wipe></div>
  <div class="hch__bleed">
    <img src="{houses.img(h["frame"])}" width="1600" height="900" loading="lazy"
         decoding="async" alt="{esc(h["frame_alt"], attr=True)}">
  </div>
  <p class="hch__ghost" aria-hidden="true" data-houses-ghost>{h["name"]}</p>
  <div class="wrap hch__inner">
    <p class="hch__step"><span class="hch__no">{h["number"]}</span>
      <span class="hch__of">/ {total:02d}</span></p>
    <h2 class="hch__name" data-houses-heading>{h["name"]}</h2>
    <p class="hch__id"><span class="hch__swatch" aria-hidden="true"></span>{h["colour"]}
      <span class="hch__dot" aria-hidden="true">&middot;</span>{h["symbol"]}</p>
    <blockquote class="hch__says">
      <p>{h["says"]}</p>
      <cite>{h["name"]} House, writing in <em>Sakshi</em>, February 2008</cite>
    </blockquote>
    <p class="copy hch__fact">{h["fact"]}</p>
    <p class="hch__more"><a href="#gallery-{h["slug"]}">{h["name"]} in frames</a></p>
  </div>
</article>''')
    return "\n\n".join(chapters)


def houses_track_html():
    """The competition archive, and the season line the script lays over it.

    Authored as an ordered list, oldest first: without the script every event
    is open on the page and reads as an archive. The script turns the list
    into a line of stops and shows one event at a time, which is the only
    thing it changes.

    A row is either placed — four houses, first to fourth — or judged, where
    the school named awards instead of a ranking. Both shapes come straight
    from the source; neither is converted into the other.
    """
    stops, panels = [], []
    for i, r in enumerate(houses.RESULTS):
        on = " is-on" if i == 0 else ""
        stops.append(f'''        <li><button type="button" class="hcomp__stop{on}"
            data-houses-stop="{i}" data-cat="{r["category"]}"
            aria-controls="event-{i}" aria-current="{"true" if i == 0 else "false"}">
          <span class="hcomp__when">{r["when"]}</span>
          <span class="hcomp__what">{r["event"]}</span>
        </button></li>''')

        body = []
        if r["order"]:
            rows = []
            for place, slug in enumerate(r["order"], 1):
                rows.append(f'''          <li data-house="{slug}">
            <span class="hcomp__pl">{place}</span>
            <span class="hcomp__hn">{houses.name_of(slug)}</span>
            <span class="hcomp__hc">{houses.colour_of(slug)}</span>
          </li>''')
            body.append('        <ol class="hcomp__order">\n' + "\n".join(rows) + "\n        </ol>")
        if r["awards"]:
            rows = []
            for award, slugs in r["awards"]:
                won = ", ".join(houses.name_of(s) for s in slugs)
                rows.append(f'''          <div data-house="{slugs[0]}">
            <dt>{award}</dt><dd>{won}</dd>
          </div>''')
            body.append('        <dl class="hcomp__awards">\n' + "\n".join(rows) + "\n        </dl>")
        if r.get("note"):
            body.append(f'        <p class="hcomp__note">{r["note"]}</p>')
        if not r["order"] and not r["awards"] and not r.get("note"):
            body.append('        <p class="hcomp__note">No placings were published.</p>')

        panels.append(f'''      <li class="hcomp__panel{on}" id="event-{i}" data-houses-panel="{i}"
          data-cat="{r["category"]}">
        <p class="hcomp__tag">{r["category"]} &middot; {r["when"]}</p>
        <h3 class="hcomp__ev">{r["event"]}</h3>
{chr(10).join(body)}
        <p class="hcomp__src">Source: {r["source"]}</p>
      </li>''')

    filters = "\n".join(
        f'''        <button type="button" class="hcomp__filter{" is-on" if c == "All" else ""}"
            data-houses-filter="{c}" aria-pressed="{"true" if c == "All" else "false"}">{c}</button>'''
        for c in houses.CATEGORIES)

    return f'''    <div class="hcomp__track" data-houses-track hidden>
      <h3 class="sr-only" id="comp-filter-h">Filter the archive by category</h3>
      <div class="hcomp__filters" role="group" data-houses-filters aria-labelledby="comp-filter-h">
{filters}
      </div>
      <div class="hcomp__line" aria-hidden="true"><span data-houses-line></span></div>
      <h3 class="sr-only" id="comp-stops-h">The events, oldest first</h3>
      <ol class="hcomp__stops" data-houses-stops aria-labelledby="comp-stops-h">
{chr(10).join(stops)}
      </ol>
    </div>

    <ol class="hcomp__panels" data-houses-panels>
{chr(10).join(panels)}
    </ol>'''


def houses_symposiums_html():
    """The four house productions of May 2008, as panels on a dark stage."""
    cards = []
    for slug, title, about in houses.SYMPOSIUMS:
        cards.append(f'''      <li data-house="{slug}">
        <p class="hcult__who"><span class="hcult__swatch" aria-hidden="true"></span>{houses.name_of(slug)}</p>
        <h3 class="hcult__title">{title}</h3>
        <p class="hcult__about">{about}</p>
      </li>''')
    return ('    <ul class="hcult__set" data-houses-symposiums>\n'
            + "\n".join(cards) + "\n    </ul>")


def houses_record_html():
    """Eight selected, dated event entries as one table.

    A real <table> with a caption, scoped headers and a row per event: the
    figures are data and a reader should be able to read down a column.
    Placings are the four house names in order, and a judged event says what
    was judged, in the same cell, rather than being forced into a ranking.
    """
    head = "".join(f'<th scope="col">{h["name"]}<small>{h["colour"]}</small></th>'
                   for h in houses.HOUSES)
    rows = []
    for r in houses.RESULTS:
        cells = []
        for h in houses.HOUSES:
            slug = h["slug"]
            if r["order"] and slug in r["order"]:
                place = r["order"].index(slug) + 1
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(place, "th")
                cells.append(f'<td data-house="{slug}"><b>{place}{suffix}</b></td>')
            elif r["awards"]:
                won = [a for a, slugs in r["awards"] if slug in slugs]
                if won:
                    cells.append(f'<td data-house="{slug}">{"; ".join(won)}</td>')
                else:
                    cells.append('<td><span class="hrec__none">&mdash;</span></td>')
            else:
                cells.append('<td><span class="hrec__none">&mdash;</span></td>')
        rows.append(f'''        <tr>
          <th scope="row">{r["event"]}<small>{r["when"]} &middot; {r["category"]}</small></th>
{"".join("          " + c + chr(10) for c in cells)}          <td class="hrec__src">{r["source"]}</td>
        </tr>''')
    return f'''    <div class="hrec__wrap rv">
      <table class="hrec__table">
        <caption>Inter-house results published by CIRS. A dash means the source named
          no placing for that house in that event, not that the house did not take
          part.</caption>
        <thead>
          <tr><th scope="col">Event</th>{head}<th scope="col">Published in</th></tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>'''


def houses_gallery_html():
    """One named-kit portrait per house, in a filterable strip.

    Every frame is a figure with a real caption outside the image, which is
    what keeps it readable on a phone and in the accessibility tree. The
    filter buttons carry the per-house ids the chapters link to, so
    "#gallery-vasishtha" lands on Vasishtha's portrait with or without script
    and the script presses it.
    """
    frames = []
    for h in houses.HOUSES:
        for name, alt, caption in ((h["hero"], h["hero_alt"], h["hero_cap"]),):
            frames.append(f'''        <li id="gallery-{h["slug"]}" data-house="{h["slug"]}">
          <figure>
            <img src="{houses.img(name)}" width="900" height="1125" loading="lazy"
                 decoding="async" alt="{esc(alt, attr=True)}">
            <figcaption><b>{h["name"]}</b><span>{caption}</span></figcaption>
          </figure>
        </li>''')
    tabs = ['        <button type="button" class="hgal__tab is-on" id="gallery-tab-all"'
            ' data-houses-house="all" aria-pressed="true">All four</button>']
    for h in houses.HOUSES:
        tabs.append(f'''        <button type="button" class="hgal__tab" id="gallery-tab-{h["slug"]}"
            data-houses-house="{h["slug"]}" aria-pressed="false">
          <span class="hgal__sw" aria-hidden="true"></span>{h["name"]}</button>''')
    return f'''    <div class="hgal__tabs" role="group" data-houses-tabs aria-labelledby="gal-h" hidden>
      <h3 class="sr-only" id="gal-h">Choose a house</h3>
{chr(10).join(tabs)}
    </div>
    <ul class="hgal__strip" data-houses-strip>
{chr(10).join(frames)}
    </ul>'''


# A tab a single page adds to the header, beside News. Student Life is the
# only page with one: its Student Login used to be an under-construction
# section at the foot of a very long page, which is a poor place to put the
# one thing a student comes for. As a header tab it is reachable from the
# first screen, and only on the page it belongs to.
#
# The mark is a student rather than a generic person: a mortarboard over a
# head and shoulders, drawn at the same size and stroke weight as the News
# and Menu marks so the three read as one row.
EXTRA_TAB = """      <a class="htab htab--login" href="{href}" target="_blank" rel="noopener" data-magnetic>
        <span class="htab__icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 2.4 16 5.2 9 8 2 5.2 9 2.4Z" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"/><path d="M4.6 6.6v2.2c0 1.2 2 2.1 4.4 2.1s4.4-.9 4.4-2.1V6.6" stroke="currentColor" stroke-width="1.25" stroke-linecap="round"/><path d="M4.2 15.6a4.8 4.8 0 0 1 9.6 0" stroke="currentColor" stroke-width="1.25" stroke-linecap="round"/></svg>
        </span>
        <span class="htab__label">{label}</span>
      </a>
"""

UC = '''<section class="uc">
  <div class="wrap uc__inner">
    <span class="uc__mark" aria-hidden="true">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 4.5v4M8 11.2h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="8" r="6.6" stroke="currentColor" stroke-width="1.2"/></svg>
    </span>
    <div>
      <p class="uc__label">Under construction</p>
      <p class="uc__text">This page is still being written. Photographs, names and figures marked
        in brackets are placeholders awaiting the school, and more will be added here in the weeks
        ahead. <a href="mailto:info@cirschool.org">Tell us what is missing.</a></p>
    </div>
  </div>
</section>'''


def build(slug, page):
    head = read("tools/partials/head.html")
    head = (head.replace("{{TITLE}}", page["title"])
                .replace("{{DESCRIPTION}}", page["description"])
                .replace("{{CANONICAL}}", "" if slug == "index" else f"{slug}.html")
                .replace("{{CACHE_BUST}}", CACHE_BUST))

    # A wall fills the window and does not scroll, so it brings its own sheet
    # and its own script, and goes without the footer and the under-construction
    # note — both of which live below a fold this page does not have. The body
    # class is what scopes artswall.css away from every other page.
    wall = page.get("wall")
    # A page may bring one sheet of its own, scoped away from every other page
    # by a body class of the same name: artswall.css under body.wall, and
    # founder.css under body.founder.
    sheet = "artswall" if wall else page.get("sheet")
    if sheet:
        head = head.replace(
            "</head>",
            f'<link rel="stylesheet" href="assets/css/{sheet}.css?{CACHE_BUST}">\n</head>')

    # Shared typography follows page sheets so the approved roles stay consistent.
    head = head.replace("</head>",
        f'<link rel="stylesheet" href="assets/css/typography.css?{CACHE_BUST}">\n</head>')

    if slug == "crossroads":
        head = head.replace(
            "</head>",
            f'<link rel="stylesheet" href="assets/css/crossroads-intro.css?{CACHE_BUST}-intro-5">\n'
            f'<link rel="stylesheet" href="assets/css/crossroads-archive.css?{CACHE_BUST}">\n'
            f'<link rel="stylesheet" href="assets/css/crossroads-stories.css?{CACHE_BUST}-hover-4">\n'
            f'<link rel="stylesheet" href="assets/css/crossroads-manuscript.css?{CACHE_BUST}">\n'
            '<noscript><style>.crossroads-intro-curtain{display:none}'
            '.crossroads-intro[data-crossroads-intro-pending] .crossroads-intro__content{visibility:visible;opacity:1}'
            '.crossroads-intro[data-crossroads-intro-pending]{background:var(--cr-purple-deep)}'
            '.crossroads-intro[data-crossroads-intro-pending] .crossroads-intro__base{visibility:visible!important}'
            '</style></noscript>\n</head>')
    if slug == "founder":
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/founder-journey.css?{CACHE_BUST}">\n</head>')
    if slug == "sports":
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/sports-journey.css?{CACHE_BUST}-sports-journey-5">\n</head>')
    # A page that opens on a scrubbed film carries the shared sheet, and with
    # it the two tuning blocks that sort out which page is which. Without
    # scripting nothing scrubs, so four screens of scroll would move a still
    # photograph: one screen, with the line already up — which is what the
    # stylesheet's own reduced-motion rule does too. A page with a still of
    # its film's last frame shows that rather than the film's first, and a
    # page whose opening ends on a photograph leaves the photograph out: its
    # moment is the movement out of the lens, and without the movement there
    # is nothing for it to arrive from. The path is relative to the page,
    # where the stylesheet's is to itself.
    if page.get("opening"):
        opening = page["opening"]
        nudge = opening.get("noscript_title_top")
        nudge = (f"body.{slug} .film__title{{--film-title-top:{nudge}}}" if nudge else "")
        if opening.get("still") and not opening.get("still_element"):
            nudge += ('.film__stage{background:#000 url(assets/img/' + opening["still"] + ') '
                      'var(--film-still-position, 50% 50%)/cover no-repeat}'
                      '.film__video{visibility:hidden}.film__shot{display:none}')
        still = ('.film__video{display:none}'
                 f'body.{slug} .film__still{{visibility:visible}}'
                 if opening.get("still") and opening.get("still_element") else "")
        pending = ('.film[data-film-pending] .film__title{opacity:1}'
                   if opening.get("pending") or opening.get("still") else "")
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/filmintro.css?{CACHE_BUST}">\n'
            f'<noscript><style>.film{{height:100svh}}{nudge}{pending}{still}'
            '</style></noscript>\n</head>')
    if slug == "theatre":
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/theatre.css?{CACHE_BUST}">\n</head>')
    if slug == "leadership":
        # The message a #msg-... URL asks for is chosen before first paint.
        head = head.replace("</head>", leadership.head_script() + leadership.head_css() + "</head>")
    if slug == "captures":
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/captures-featured.css?{CACHE_BUST}">\n'
            f'<link rel="stylesheet" href="assets/css/captures-gallery.css?{CACHE_BUST}">\n</head>')
    if slug == "parent-portal":
        # This page has no shared curtain, including its no-script override.
        curtain_note = head.index("<!-- The opening curtain")
        curtain_note_end = head.index("</noscript>", curtain_note) + len("</noscript>")
        head = head[:curtain_note] + head[curtain_note_end:]
        # Hide the photograph and copy only when this one-time entrance can
        # run. Without scripting or with reduced motion, the page is ready.
        portal_motion_gate = (
            '<script>\n(function(){\n'
            '  if (location.hash || window.scrollY > 8 || '
            'window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;\n'
            '  document.documentElement.classList.add("portal-motion-pending");\n'
            '  window.__cirsPortalMotionFallback = window.setTimeout(function(){\n'
            '    document.documentElement.classList.remove("portal-motion-pending");\n'
            '  }, 8500);\n'
            '  document.addEventListener("DOMContentLoaded", function(){\n'
            '    window.setTimeout(function(){\n'
            '      if (!window.__cirsPortalMotionBooted) '
            'document.documentElement.classList.remove("portal-motion-pending");\n'
            '    }, 700);\n'
            '  }, {once:true});\n'
            '})();\n</script>\n'
        )
        head = head.replace("</head>",
            portal_motion_gate +
            f'<link rel="stylesheet" href="assets/css/parent-portal-intro.css?{CACHE_BUST}">\n</head>')
    if slug in ("admissions", "school-info", "news", "curriculum", "school-history", "leadership"):
        # These pages open immediately with their own video, document sheets,
        # journal masthead or, on Curriculum, the photograph of learning the
        # page leads with — and School History on its archive's title — so
        # the shared curtain is unnecessary.
        curtain_note = head.index("<!-- The opening curtain")
        curtain_note_end = head.index("</noscript>", curtain_note) + len("</noscript>")
        head = head[:curtain_note] + head[curtain_note_end:]

    # The cinematic closing scene and practical footer are shared by all
    # scrolling public pages. Load this sheet after page-specific styles.
    if not wall:
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/footer.css?{CACHE_BUST}-footer-1">\n</head>')

    head = head.replace("</head>",
        f'<link rel="stylesheet" href="assets/css/drawer.css?{CACHE_BUST}-drawer-5">\n</head>')

    # A page that opens on a pale ground cannot have the header floating over
    # it in white lettering. "litehead" puts the class on <body>, and pages.css
    # gives the header dark lettering there from the first paint, with or
    # without JavaScript. The header's own state — clear or glass — is the
    # same on every page and belongs to cirs.js alone.
    lite = bool(page.get("litehead"))
    # A page opening on a scrubbed film is marked twice: "film" for the
    # mechanics every such page shares, and its own slug for the handful of
    # decisions its footage makes for it.
    classes = [c for c in ["wall" if wall else page.get("sheet"),
                           "film" if page.get("opening") else None,
                           slug if page.get("opening") else None,
                           "parent-portal" if slug == "parent-portal" else None,
                           "litehead" if lite else None] if c]
    body_class = " ".join(classes)
    chrome = read("tools/partials/chrome.html")
    if slug == "founder":
        chrome = chrome.replace('<div class="progress" id="progress" aria-hidden="true"></div>\n', "")
    if slug == "blog" or page.get("post"):
        # Journal pages open directly on readable type. The shared full-screen
        # curtain would hide their masthead and force an unrelated wait.
        intro_start = chrome.index("<!-- Opening sequence.")
        intro_end = chrome.index("<!-- Film lightbox", intro_start)
        chrome = chrome[:intro_start] + chrome[intro_end:]
    if slug == "parent-portal":
        # The full-window photograph is this page's opening; the shared opaque
        # curtain would cover it and run its own scroll lock.
        start = chrome.index("<!-- Opening sequence.")
        end = chrome.index("<!-- Film lightbox", start)
        chrome = chrome[:start] + chrome[end:]
    if slug in ("admissions", "school-info", "news", "curriculum", "school-history", "leadership"):
        # Admissions, School Information, News, Curriculum, School History and
        # Leadership each have their own visible opening. The shared curtain would delay it behind a
        # blank screen.
        intro_start = chrome.index("<!-- Opening sequence.")
        intro_end = chrome.index("<!-- Film lightbox", intro_start)
        chrome = chrome[:intro_start] + chrome[intro_end:]
    parts = [head, f'<body class="{body_class}">' if body_class else "<body>",
             chrome.rstrip("\n")]
    if slug == "crossroads":
        parts[-1] = parts[-1].replace('class="curtain"', 'class="curtain crossroads-intro-curtain"')
    drawer = (read("tools/partials/drawer.html")
              .replace("{{NAV}}", nav_html(slug))
              .replace("{{ACTIVE_GROUP}}", str(menu_group_index(slug)))
              .replace("{{BRAND_HREF}}", "#top" if slug == "index" else "index.html"))
    # The home page needs no Home tab — the wordmark already leads here, and a
    # Home link on Home is a link to nowhere.
    header = (read("tools/partials/header.html")
              .replace("{{BRAND_HREF}}", "#top" if slug == "index" else "index.html")
              .replace("{{HOME_TAB}}", "" if slug == "index" else HOME_TAB)
              .replace("{{HEADER_TABS}}",
                       EXTRA_TAB.format(href=page["logintab"][1], label=page["logintab"][0])
                       if page.get("logintab") else ""))
    if slug == "news":
        header = header.replace('class="htab htab--news" href="news.html"',
                                'class="htab htab--news" href="news.html" aria-current="page"')
    parts += [header.rstrip("\n"), drawer.rstrip("\n")]
    parts.append('<main id="main">')
    if slug == "parent-portal":
        parts.append(read("tools/partials/parent-portal-intro.html").rstrip("\n"))
    # A page may open on a composition of its own, above and instead of the
    # shared hero or banner. It is a partial rather than a page body because
    # what follows it here is still built by soon_html.
    if page.get("opening"):
        parts.append(film_html(slug, page))
    if page.get("hero"):
        parts.append(hero_html(page))
    elif page.get("banner"):
        parts.append(banner_html(page))
    # The "On this page" index goes here, before the content it indexes.
    jump_at = len(parts)
    if page.get("post"):
        content = article_html(page)
    elif page.get("soon"):
        content = soon_html(page)
    else:
        content = read(f"tools/pages/{slug}.html").rstrip("\n")
    content = expand_figs(content)
    if slug == "art-attack":
        content = artattack.expand(content)
    if slug == "captures":
        content = captures.expand_featured(content)
    if slug == "festivals":
        content = festivals.expand(content)
    if slug == "school-history":
        content = history.expand(content)
    if slug == "leadership":
        content = leadership.expand(content)
    content = (content.replace("{{ARTSWALL}}", artswall_html())
                       .replace("{{HOUSES_HERO}}", houses_hero_html())
                       .replace("{{HOUSES_CHAPTERS}}", houses_chapters_html())
                       .replace("{{HOUSES_TRACK}}", houses_track_html())
                       .replace("{{HOUSES_SYMPOSIUMS}}", houses_symposiums_html())
                       .replace("{{HOUSES_RECORD}}", houses_record_html())
                       .replace("{{HOUSES_GALLERY}}", houses_gallery_html())
                       .replace("{{ARTSWALL_COUNT}}", str(artswall.count()))
                       .replace("{{REGISTER}}", register_html() if slug == "school-info" else "")
                       .replace("{{RECORDS_NOTICE}}", records_notice_html() if slug == "school-info" else "")
                       .replace("{{DOCPORTAL}}", docportal_html())
                       .replace("{{CROSSROADS_WALL}}", crosswall_html())
                       .replace("{{CROSSROADS}}", crossroads_html())
                       .replace("{{CROSSROADS_COUNT}}", str(crossroads.COUNT))
                       .replace("{{CROSSROADS_LATEST_LINK}}", crossroads_latest())
                       .replace("{{CROSSROADS_LATEST_FEATURE}}", crossroads_latest(feature=True))
                       .replace("{{CROSSROADS_STORIES_COVERS}}", crossroads_stories_covers())
                       .replace("{{MATH_JOURNEY}}", mathchallenge.journey_html())
                       .replace("{{MATH_ZONES}}", mathchallenge.zones_html())
                       .replace("{{MATH_FILTERS}}", mathchallenge.filters_html())
                       .replace("{{MATH_ARCHIVE}}", mathchallenge.archive_html())
                       .replace("{{CAPTURES_GALLERY}}", captures.gallery_html() if slug == "captures" else "")
                       .replace("{{CAPTURES_END}}", captures.end_html() if slug == "captures" else "")
                       .replace("{{CAPTURES_END_CAPTION}}", captures.END[2])
                       .replace("{{CAPTURES_COUNT_CAP}}", captures.count_word().capitalize())
                       .replace("{{CAPTURES_CHAPTER_NAV}}", captures.chapter_nav_html() if slug == "captures" else "")
                       .replace("{{CW_ROWS}}", creativewriting.rows_html())
                       .replace("{{CW_CHAPTERS}}", creativewriting.chapters_html())
                       .replace("{{CW_HERO_EXCERPT}}", creativewriting.hero_excerpt_html())
                       .replace("{{CW_COUNT}}", str(creativewriting.count()))
                       .replace("{{CW_WRITERS}}", str(creativewriting.writer_count()))
                       .replace("{{BLOG_FRONT}}", blog.front_html())
                       .replace("{{BLOG_RAIL}}", blog.rail_html())
                       .replace("{{BLOG_COUNT}}", str(blog.count()))
                       .replace("{{BLOG_ISSUES}}", str(blog.issue_count()))
                       .replace("{{ALUMNI_CONSTELLATION}}", alumni.constellation_html())
                       .replace("{{ALUMNI_DESTINATIONS}}", alumni.destinations_html())
                       .replace("{{ALUMNI_PEOPLE}}", alumni.people_html())
                       .replace("{{ALUMNI_VOICES}}", alumni.voices_html())
                       .replace("{{ALUMNI_PATHWAYS}}", alumni.pathways_html())
                       .replace("{{ALUMNI_COUNT_CAP}}", alumni.count_word().capitalize())
                       .replace("{{ALUMNI_COUNT}}", alumni.count_word()))
    if slug == "our-results":
        content = (content.replace("{{RESULTS_REGIONS}}", results_regions_html())
                          .replace("{{RESULTS_FILTERS}}", results_filters_html())
                          .replace("{{RESULTS_DIRECTORY}}", results_directory_html())
                          .replace("{{RESULTS_COUNT_CAP}}", alumni.count_word().capitalize())
                          .replace("{{RESULTS_COUNT}}", str(alumni.count())))
    if slug == "theatre":
        content = (content.replace("{{THEATRE_PROGRAMME}}", theatre.programme_html())
                          .replace("{{THEATRE_ANAND_UTSAV}}", theatre.anand_utsav_html())
                          .replace("{{THEATRE_MASQUERADES}}", theatre.masquerades_html())
                          .replace("{{THEATRE_CLASSES}}", theatre.classes_html())
                          .replace("{{THEATRE_VIEWER_DATA}}", theatre.viewer_data()))
    content = re.sub(r"\{\{DOC_STATUS:([a-z0-9-]+)\}\}",
                     lambda m: doc_sheet_status(m.group(1)), content)
    parts.append(content)
    # Every page carries the index; jump_html leaves it out where there is
    # nothing to jump to. "jump": False opts a page out. It is placed after
    # the banner, before the content, so the keyboard meets it first.
    jump = jump_html(content) if page.get("jump", True) and not wall else ""
    if jump:
        parts.insert(jump_at, JUMP_MARK)
    if page.get("popup"):
        parts.append(POPUP)
    if page.get("uc", True) and not wall:
        parts.append(UC)
    parts.append("</main>")
    if not wall:
        footer = read("tools/partials/footer.html").rstrip("\n")
        if slug in ("captures", "leadership"):
            # Captures already ends with its own full-width photograph, and
            # Leadership with its staff photograph and a compact pair of
            # links: a second full-screen scene would compete with both.
            # Keep that as the page's final image before the site footer.
            footer = footer[footer.index('<div class="footer-wrap">'):]
        if slug == "admissions":
            footer = footer.replace('href="admissions.html#examination">Important Dates',
                                    'href="admissions.html#dates">Important Dates')
        if page.get("closing"):
            footer = closing_html(footer, page["closing"])
        parts.append(footer)
    parts.append(read("tools/partials/scripts.html").replace("{{CACHE_BUST}}", CACHE_BUST).rstrip("\n"))
    if not wall:
        parts.append(f'<script src="assets/js/footer.js?{CACHE_BUST}-footer-1" defer></script>')
    if slug == "crossroads":
        parts.append(f'<script src="assets/js/crossroads-intro.js?{CACHE_BUST}-intro-5" defer></script>')
        parts.append(f'<script src="assets/js/crossroads-archive.js?{CACHE_BUST}" defer></script>')
        parts.append(f'<script src="assets/js/crossroads-stories.js?{CACHE_BUST}-hover-4" defer></script>')
        parts.append(f'<script src="assets/js/crossroads-manuscript.js?{CACHE_BUST}" defer></script>')
    if slug == "founder":
        parts.append(f'<script src="assets/js/founder-journey.js?{CACHE_BUST}" defer></script>')
    if slug == "why-cirs":
        parts.append(f'<script src="assets/js/why-cirs.js?{CACHE_BUST}" defer></script>')
    if slug == "the-cirs-experience":
        parts.append(f'<script src="assets/js/student-life-journey.js?{CACHE_BUST}" defer></script>')
    if slug == "our-results":
        parts.append(f'<script src="assets/js/results-journey.js?{CACHE_BUST}" defer></script>')
    if slug == "admissions":
        parts.append(f'<script src="assets/js/admissions.js?{CACHE_BUST}" defer></script>')
    if slug == "school-info":
        parts.append(f'<script src="assets/js/records.js?{CACHE_BUST}" defer></script>')
    if slug == "alumni":
        parts.append(f'<script src="assets/js/alumni-journey.js?{CACHE_BUST}" defer></script>')
    if slug == "news":
        parts.append(f'<script src="assets/js/news-journal.js?{CACHE_BUST}" defer></script>')
    if slug == "math-challenge":
        parts.append(f'<script src="assets/js/matharena.js?{CACHE_BUST}" defer></script>')
    if slug == "creative-writing":
        parts.append(f'<script src="assets/js/cwriting.js?{CACHE_BUST}" defer></script>')
    if slug == "houses":
        parts.append(f'<script src="assets/js/houses-journey.js?{CACHE_BUST}" defer></script>')
    if slug == "blog":
        parts.append(f'<script src="assets/js/blog-index.js?{CACHE_BUST}-editorial-1" defer></script>')
    if slug == "festivals":
        parts.append(f'<script src="assets/js/festivals.js?{CACHE_BUST}" defer></script>')
    if slug == "art-attack":
        parts.append(f'<script src="assets/js/artattack.js?{CACHE_BUST}" defer></script>')
    if slug == "leadership":
        parts.append(f'<script src="assets/js/leadership.js?{CACHE_BUST}" defer></script>')
    if slug == "curriculum":
        parts.append(f'<script src="assets/js/curriculum.js?{CACHE_BUST}" defer></script>')
    if slug == "school-history":
        parts.append(f'<script src="assets/js/history.js?{CACHE_BUST}" defer></script>')
    if page.get("opening"):
        parts.append(f'<script src="assets/js/filmintro.js?{CACHE_BUST}" defer></script>')
    if slug == "sports":
        parts.append(f'<script src="assets/js/sports-journey.js?{CACHE_BUST}" defer></script>')
    if slug == "theatre":
        parts.append(f'<script src="assets/js/theatre.js?{CACHE_BUST}" defer></script>')
    if slug == "captures":
        parts.append(f'<script src="assets/js/captures-featured.js?{CACHE_BUST}" defer></script>')
        parts.append(f'<script src="assets/js/captures-gallery.js?{CACHE_BUST}" defer></script>')
    if slug == "parent-portal":
        parts.append(f'<script src="assets/js/parent-portal-motion.js?{CACHE_BUST}" defer></script>')
    if wall:
        parts.append(f'<script src="assets/js/artswall.js?{CACHE_BUST}" defer></script>')
    parts += ["</body>", "</html>", ""]

    # The index goes in after rewrite_links: its anchors name sections on this
    # page, and must not be sent to the page an old single-page anchor meant.
    html = to_depth(rewrite_links("\n".join(parts), slug).replace(JUMP_MARK, jump), slug)
    # A page with newly page-scoped assets can invalidate its own shared and
    # local files without rewriting every generated page in the repository.
    cache_suffix = page.get("cache_suffix", "")
    if cache_suffix:
        html = html.replace(f"?{CACHE_BUST}", f"?{CACHE_BUST}{cache_suffix}")
    return html


# Every published article is a page. They are added here rather than written
# out above because they are data: seventeen entries in tools/blogposts.py,
# each of which becomes a page with the site's own chrome around it. They are
# not in MENU — the Blog is how a reader reaches them.
for _post in blogposts.POSTS:
    PAGES[_post["slug"]] = {
        "nav": esc(_post["title"]),
        "title": esc(_post["title"], attr=True) + " | CIRS Blog",
        "description": esc(_post["excerpt"][:180], attr=True),
        "sheet": "blog",
        "cache_suffix": "-blog-editorial-1",
        "uc": False,
        "jump": False,
        # An article opens on paper, so the header cannot float over it in
        # white lettering. The Blog's own masthead is dark and does not.
        "litehead": True,
        "post": _post,
    }


if __name__ == "__main__":
    for slug, page in PAGES.items():
        out = os.path.join(ROOT, f"{slug}.html")
        # A slug may name a directory: "curriculum/ib-diploma" is a child page
        # of Curriculum and is written, and served, under it.
        os.makedirs(os.path.dirname(out), exist_ok=True)
        html = build(slug, page)
        open(out, "w", encoding="utf-8").write(html)
        print(f"  write  {slug}.html ({len(html):,} chars)")
    # A certificate marked current whose date has gone by. The pages already
    # show it as expired; this names it so tools/documents.py is updated.
    for title in docs.check_dates(datetime.date.today()):
        print(f"  NOTE   {title}: validity date has passed, so it is published as "
              f"expired — upload the renewal or set its status in tools/documents.py")
