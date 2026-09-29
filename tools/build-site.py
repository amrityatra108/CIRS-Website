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
import founder_story
import houses
import sports_house_history
import documents as docs
import blogposts
import newsarticles
import cvpnews
import crossroads
import mathchallenge
import creativewriting
import captures
import theatre
import festivals
import leadership
import history
import laurels
import experience

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_BUST = "b=115"

# Where a film's large-screen encode is offered. Everything that fails it —
# a phone held either way up — takes the phone encode (tools/make-films.py),
# so turning a phone never asks for a different file. A tablet passes it.
FILM_LARGE = "(min-width: 768px) and (min-height: 501px)"

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
    ("Student Life",         ["the-cirs-experience", "spiritual-life", "curriculum", "our-results", "sports",
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
        "cache_suffix": "-founder-18",
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
        # A photographic opening, typographic expansion, finite archival
        # camera path and complete record. HTML provides the normal-flow
        # mobile, reduced-motion and graphics-failure experience.
        # Every record is written from tools/history.py,
        # which names each one's source; tools/make-history.py cuts the images.
        "banner": None,
        "sheet": "history",
        "cache_suffix": "-history-cinematic-4",
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
        "cache_suffix": "-curriculum-atlas-2",
        # No banner. The page opens on its own full-window scene, built in
        # tools/pages/curriculum.html: the gold path of the grades rising
        # through the school's purple, the heading, the page's facts and its
        # own section index. That index is visible and labelled, so the
        # floating "On this page" control would be a second copy of it; hence
        # jump False. The opening is dark and full-screen, so the header
        # starts clear over it in light lettering, as over any hero.
        "banner": None,
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
        "nav": "The CIRS experience",
        "title": "The CIRS experience",
        "description": "Residential life at CIRS: one school day for Junior and Senior School, "
                       "side by side, and the hundred-acre campus it happens on.",
        # No banner and no hero key: this page opens on a photograph of its
        # own, built in tools/pages/the-cirs-experience.html, which carries the
        # page's h1 and its own id="top". It is dark, so the header floats over
        # it in light lettering. Every time and photograph on the page is
        # written from tools/experience.py. The page ends on its own night
        # section, so it takes no shared closing scene (see below), and nothing
        # on it is a placeholder, so no under-construction note.
        "sheet": "student-life",
        "cache_suffix": "-experience-1",
        "uc": False,
    },
    "spiritual-life": {
        "nav": "Spiritual Life",
        "title": "Spiritual Life at CIRS",
        "description": "Swadhyaya, sadhana and seva at Chinmaya International Residential "
                       "School: the daily practices, sacred occasions and student-led service "
                       "rooted in the vision of Pujya Gurudev Swami Chinmayananda.",
        # No banner. The page opens on a full-window photograph of its own —
        # students seated in the amphitheatre after dark — which carries the
        # h1, and the header floats over it in white lettering until the
        # first scroll. Every activity on the page is taken from the school's
        # own account ("Spiritual Page", 2026); see the comment at the top of
        # tools/pages/spiritual-life.html. Photographs are cut by
        # tools/make-spiritual.py. The spiritual guides' portraits and roles
        # are bracketed placeholders, so the under-construction note stays.
        "banner": None,
        "sheet": "spiritual",
        "cache_suffix": "-spiritual-three-1",
        "closing": ("Come and see", "the day for yourself",
                    [("Plan a visit", "admissions.html#visit", "closing-scene__admissions"),
                     ("The CIRS experience", "the-cirs-experience.html", "closing-scene__contact"),
                     ("Our Founder", "founder.html", "closing-scene__contact")]),
    },
    "sports": {
        "nav": "Our Sports",
        "title": "Sports & Laurels — Built in the Arena | CIRS",
        "description": "Built in the Arena — Athletics, house competition, physical discipline and sporting laurels at Chinmaya International Residential School, Coimbatore.",
        "sheet": "sports",
        "cache_suffix": "-sports-3",
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
                       "Vasishta, Valmiki, Vishwamitra and Vyasa — their colours, identities "
                       "and a dated archive of published inter-house results.",
        "banner": None,
        "sheet": "houses",
        "cache_suffix": "-houses-6",
        "uc": False,
        "jump": False,
    },
    "crossroads": {
        "nav": "The Crossroads",
        # The old site filed this under a "Creative Corner" this site does not
        # have; Student Life is where the arts and the clubs live here.
        "title": "The Crossroads | CIRS Monthly Magazine",
        "description": "Issues of The Crossroads, the monthly magazine of Chinmaya "
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
        "cache_suffix": "-blog-superpass-2",
        "jump": False,
        "uc": False,
        # Mona Sans carries the Blog interface and prose; its grid remains distinct.
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
                       "carried them: the school's achievement archive, from 2007 to today.",
        # A hall of achievement: it opens on the count, travels through the
        # fields, the figures and the years, and ends in the complete archive.
        # Every record is written from tools/laurels.py, which names its source
        # and audits every figure set large against it.
        "banner": None,
        "sheet": "laurels",
        "cache_suffix": "-laurels-4",
        "uc": False,
        "jump": False,
    },
    "math-challenge": {
        "nav": "Math Challenge",
        "title": "Math Challenge",
        "description": "The Math Challenge at Chinmaya International Residential School — "
                       "four grade divisions, and the winners' bulletins the mathematics "
                       "department publishes month by month.",
        # No banner from the shared builder. The page opens on its own
        # installation: a sculpture of 216 blocks that the stage's scroll
        # turns from cube to field to torus (assets/js/math-sculpture.js,
        # loaded by assets/js/matharena.js), on ivory, so the header opens
        # in ink. Styles in assets/css/matharena.css, scoped to body.matharena.
        "banner": None,
        "sheet": "matharena",
        "litehead": True,
        "cache_suffix": "-kinetic-1",
    },
    "creative-writing": {
        "nav": "Creative Writing",
        "title": "Creative Writing | Written at CIRS",
        "description": "Poems by students of Chinmaya International Residential School. "
                       "Explore the collection and read each edition.",
        # Student literary collection: plum introduction, paper excerpt,
        # published editorial archive and warm-paper poem readers.
        # Every edition, poem and presentation is data in
        # tools/creative-writing-content.json, rendered by tools/creativewriting.py,
        # which also adds the Junior, Senior and edition pages below.
        "banner": None,
        "sheet": "cwriting",
        "cache_suffix": "-literary-2",
        "jump": False,
        "uc": False,
        # The opening is deep purple, so the header letters in light over it.
        "litehead": False,
        "cw": {"kind": "main", "collection": "all"},
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
        # finished work (assets/js/artattack.js). The film carries the h1,
        # which is visible from its first frame.
        "sheet": "artattack",
        "cache_suffix": "-art-attack-6",
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
        # Restore the approved diya-to-rangoli film before the current
        # photograph-led year. Keep the documented festival chapters below.
        "sheet": "festivals",
        "cache_suffix": "-festivals-year-1",
        "nav": "CIRS Festivals",
        "title": "CIRS Festivals",
        "description": "Seven festivals kept through the school year at Chinmaya International "
                       "Residential School, from Raksha Bandhan to Holi, in the school's own "
                       "photographs.",
        "banner": None,
        "opening": {
            "video": "festivals-opening",
            "mobile_video": None,
            "poster": "festivals-opening-poster.jpg",
            "still": "festivals-opening-final.jpg",
            "still_element": True,
            "title": "CIRS Festivals",
            "pending": True,
        },
        "uc": False,
    },
    "theatre": {
        # The page body is tools/pages/theatre.html; its sheet is
        # assets/css/culture.css, shared by the three Art, Culture & Music
        # pages that open on a film.
        "sheet": "culture",
        "cache_suffix": "-theatre-stage-2",
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
            # The film keeps its original scroll distances (film to 252vh, the
            # last frame held to 281vh, the title up by 328vh), now as
            # fractions of a 470vh travel, because the page's own sheet lets
            # the run go on for 110vh more. That extra is the handoff: the
            # film's last frame darkens, one line of light is drawn, the page
            # names itself and the line opens onto the Prologue (body.theatre
            # in assets/css/theatre.css; th-hand in assets/js/theatre.js).
            "phases": (0.5362, 0.5974, 0.6970),
            "stage_extra": theatre.handoff_html(),
            # Without scripting the film is its still frame, and the page's own
            # rule that holds the title back until the film reveals it would
            # leave that frame with no name on it.
            "noscript_css": "body.theatre .film[data-film-pending] .film__title{opacity:1}",
        },
        # After the opening, a Prologue and a programme, then three acts —
        # Anand Utsav, Masquerades and Class Presentations — with an
        # intermission, an archive request and a curtain call between and
        # after them, written from tools/theatre.py, with a sheet and a
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
        "description": "Use the school's separate fee-payment and parent-login services, "
                       "with contact details for help from CIRS.",
        "banner": ("Parents", "Parent <em>Portal.</em>",
                   "Fee payment and parent login are available through the school&rsquo;s "
                   "separate existing systems."),
        # Shared with School Information — see assets/css/connect.css.
        "sheet": "connect",
        "cache_suffix": "-portal-photo-1",
        # This page supplies its own contact and navigation footer.
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
    # What a visitor sees at an address that is no page of this site. Both
    # hosts serve 404.html from the root of the deploy, with a 404 status,
    # for any path that matches nothing, so the page cannot know where it is
    # being shown from: "notfound" writes every reference on it from the root
    # (see to_root), leaves out the curtain and the closing scene, and gives
    # it no canonical address. Not in MENU; nobody navigates to it.
    "404": {
        "nav": "Page not found",
        "title": "Page not found | CIRS",
        "description": "This address is not a page of the Chinmaya International Residential "
                       "School website.",
        # The band and its links are the page, in tools/pages/404.html.
        "banner": None,
        "sheet": "notfound",
        "notfound": True,
        "jump": False,
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
        # Spiritual Life's gallery/day belong to its own chapter navigation.
        if slug == "spiritual-life" and anchor in ("top", "gallery", "day", "vision"):
            return m.group(0)
        # Curriculum now has its own #pathways; the legacy alias points to
        # Alumni, so keep this page's banner action on its own section.
        if slug == "curriculum" and anchor == "pathways":
            return m.group(0)
        # Likewise the Founder page's own #life, the life story, which its
        # opening's "Begin the journey" leads down to.
        if slug == "founder" and anchor == "life":
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
    return prefix_refs(html, "../" * depth)


def to_root(html):
    """Write every relative reference from the root of the site instead.

    The not-found page is one file, 404.html, but a host serves it at
    whatever path failed — /curriculum/cbse/nothing as readily as /nothing —
    so no relative path can be right for it: "assets/css/cirs.css" would be
    asked for from /curriculum/cbse/assets/ and the page would arrive
    unstyled. "/assets/css/cirs.css" is right from anywhere. Only that page
    is written this way; every other page stays relative, which is what lets
    the site be opened from a folder as well as served.
    """
    return prefix_refs(html, "/")


def prefix_refs(html, up):
    """Put `up` in front of every relative reference, as to_depth describes."""
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
    # The Creative Writing collections and editions open the menu on the
    # group their parent page belongs to.
    if slug.startswith("creative-writing/"):
        slug = "creative-writing"
    return next((i for i, (_, slugs) in enumerate(MENU) if slug in slugs), 0)


def nav_html(slug):
    """The menu: five categories in one number column and one label column,
    each followed by its pages. From 901px the pages of the open category
    stand in the destination area beside the categories; below that each
    category opens its pages beneath it. The open category is the current
    page's, and the current page's link carries aria-current. The gold
    marker is one element that cirs.js moves between the categories."""
    active = menu_group_index(slug)
    out = ['<nav class="nv-menu__nav" aria-labelledby="drawer-title">']
    for i, (group, slugs) in enumerate(MENU):
        gid = "dnav-" + re.sub(r"[^a-z]+", "-", group.lower()).strip("-")
        selected = "true" if i == active else "false"
        state = "" if i == active else " hidden"
        out.append(f'  <div class="nv-item" style="--i:{i}">')
        out.append(f'    <button type="button" class="nv-cat" id="{gid}-button" data-menu-index="{i}" '
                   f'aria-expanded="{selected}" aria-controls="{gid}-panel">'
                   f'<span class="nv-cat__num" aria-hidden="true">{i + 1:02d}</span>'
                   f'<span class="nv-cat__word">{esc(group)}</span></button>')
        out.append(f'    <section class="nv-dest" id="{gid}-panel" aria-labelledby="{gid}-button"{state}>')
        out.append(f'      <p class="nv-dest__kicker" aria-hidden="true">{esc(group)}</p>')
        out.append('      <ul class="nv-dest__list">')
        for sl in slugs:
            page = PAGES[sl]
            here = ' aria-current="page"' if sl == slug else ""
            out.append(f'        <li><a href="{sl}.html"{here}><span class="nv-dest__label">{esc(page["nav"])}</span>'
                       '<span class="nv-dest__here" aria-hidden="true">You are here</span>'
                       '<svg class="nv-dest__arrow" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" '
                       'focusable="false"><path d="M4 12h15M13.5 6.5 19 12l-5.5 5.5" fill="none" stroke="currentColor" '
                       'stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg></a></li>')
        out += ['      </ul>', '    </section>', '  </div>']
    out.append('  <span class="nv-marker" aria-hidden="true"></span>')
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
    # The ramp to paper, unless the page puts it further down itself. It is
    # dark for more than half its depth, so the shared header treats it as a
    # dark ground (data-header-theme; see "Header state" in cirs.js).
    seam = ("" if film.get("seam") is False else
            '\n<div class="film__seam" data-header-theme="dark" aria-hidden="true"></div>')
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
    preload = "none" if slug == "art-attack" else "auto"
    progressive_loader = ('''\n    <script>
      (function (video) {
        var connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        var constrained = connection && (connection.saveData || ["slow-2g", "2g", "3g"].indexOf(connection.effectiveType) !== -1);
        if (!video || reduced || constrained) return;
        var still = document.currentScript.closest(".film").querySelector(".film__still");
        function loadAfterPaint() {
          requestAnimationFrame(function () {
            requestAnimationFrame(function () {
              window.setTimeout(function () { if (!document.hidden) video.load(); }, 50);
            });
          });
        }
        // The opening still carries the first useful composition. Let its
        // high-priority request finish before the film competes for bandwidth.
        if (still && !still.complete) {
          still.addEventListener("load", loadAfterPaint, { once: true });
          still.addEventListener("error", loadAfterPaint, { once: true });
        } else loadAfterPaint();
      })(document.currentScript.closest(".film").querySelector("[data-film-video]"));
    </script>''') if slug == "art-attack" else ""
    cue = (
        '    <p class="film__scroll-cue" data-film-scroll-cue>'
        '<span aria-hidden="true">↓</span><span>Scroll to discover</span></p>\n'
        if slug == "sports" else ""
    )
    mobile_video = film.get("mobile_video", f'{film["video"]}-m')
    mobile_source = (f'<source src="assets/video/{mobile_video}.mp4" type="video/mp4">'
                     if mobile_video else
                     f'<source src="assets/video/{film["video"]}.mp4" type="video/mp4">')
    return f'''<section class="film" id="{slug}-opening" data-film{attrs}>
  <div class="film__stage">
{still}    <video class="film__video" data-film-video
           width="1280" height="720"
           poster="assets/img/{film["poster"]}"
           preload="{preload}" muted playsinline disablepictureinpicture
           aria-hidden="true" tabindex="-1">
      <!-- H.264 first, which is the other way round from the rest of this
           site. These files are not played but seeked, several times a
           second, and H.264 is the one codec every browser that has it
           decodes in hardware — so it is the path that scrubs without
           stuttering wherever it exists. The VP9 is for the browsers built
           without the proprietary decoder, which would otherwise have no
           opening at all. Both are the same length at 24fps, so the mapping
           in filmintro.js holds whichever one is picked.

           Pages with a mobile cut use it on phones in either orientation;
           Festivals currently uses its approved full-resolution MP4 there.
           The large-screen file is listed first,
           behind the query phones fail, so a browser that ignores media on
           a video's sources keeps the file it always had. -->
      <source src="assets/video/{film["video"]}.mp4" type="video/mp4"
              media="{FILM_LARGE}">
      {mobile_source}
      <source src="assets/video/{film["video"]}.webm" type="video/webm">
    </video>
{cue}    <h1 class="film__title" data-film-title>{title}</h1>
{film.get("stage_extra", "")}{shot}{progressive_loader}  </div>
</section>{seam}'''


def esc(text, attr=False):
    """The magazine's own punctuation, made safe to put in a page.

    Article text is raw prose lifted from a PDF: it contains ampersands and
    quotation marks that mean themselves. Escaping is what keeps a headline
    that opens on a quoted sentence from ending the attribute it sits in.
    """
    out = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return out.replace('"', "&quot;") if attr else out


def news_article_html(page):
    """A report the school published on one of its own earlier sites.

    It wears the same furniture as a Crossroads article, so an archived
    report reads like part of this site rather than a page rescued from
    another one, and inherits that sheet's measure and its behaviour on a
    phone. The rail carries provenance instead of an issue number: what this
    is, where it first appeared, and a way back to the News page.
    """
    art = page["news"]

    image = ""
    if art.get("image"):
        image = (f'    <figure class="art__hero">\n'
                 f'      <img src="{esc(art["image"], attr=True)}"\n'
                 f'           alt="{esc(art.get("image_alt", ""), attr=True)}"\n'
                 f'           width="{art.get("image_size", (1200, 620))[0]}" height="{art.get("image_size", (1200, 620))[1]}" decoding="async">\n'
                 f'    </figure>\n\n')

    if art.get("blocks"):
        # Written for this site from a school report (tools/cvpnews.py):
        # paragraphs under a few plain headings.
        body = "\n".join(f"        <h2>{esc(t)}</h2>" if kind == "h" else f"        <p>{esc(t)}</p>"
                         for kind, t in art["blocks"])
    else:
        body = "\n".join(f"        <p>{esc(p)}</p>" for p in art["paragraphs"])

    gallery = ""
    if art.get("figures"):
        shots = []
        for f in art["figures"]:
            shots.append(
                f'          <figure class="newsgal__shot">\n'
                f'            <img src="{esc(f["src"], attr=True)}"\n'
                f'                 alt="{esc(f["alt"], attr=True)}" width="{f["w"]}" height="{f["h"]}" loading="lazy" decoding="async">\n'
                f'          </figure>')
        gallery = ('        <div class="newsgal newsgal--report">\n'
                   + "\n".join(shots) + "\n        </div>\n")
    elif art.get("gallery"):
        folder = os.path.join(ROOT, "assets/img/news-archive", art["gallery"])
        shots = []
        for name in sorted(os.listdir(folder)):
            shots.append(
                f'          <figure class="newsgal__shot">\n'
                f'            <img src="assets/img/news-archive/{art["gallery"]}/{name}"\n'
                f'                 alt="" width="1200" height="675" loading="lazy" decoding="async">\n'
                f'          </figure>')
        gallery = ('        <div class="newsgal">\n'
                   + "\n".join(shots) + "\n        </div>\n")

    dek = f'      <p class="art__subtitle">{esc(art["dek"])}</p>\n' if art.get("dek") else ""
    if art.get("report"):
        edition = esc(art["report"])
        rail = (f'    <aside class="art__rail" aria-label="About this report">\n'
                f'      <p>Written from</p>\n'
                f'      <strong>The school&rsquo;s CVP report,<br>{esc(cvpnews.TERM)}</strong>\n'
                + (f'      <p>{esc(art["who"])}</p>\n' if art.get("who") else "") +
                f'      <a href="news.html#term">The term in review</a>\n'
                f'      <a href="news.html">All CIRS news</a>\n'
                f'    </aside>\n')
    else:
        edition = "From the CIRS news archive"
        rail = (f'    <aside class="art__rail" aria-label="Where this was published">\n'
                f'      <p>First published on</p>\n'
                f'      <strong>The school&rsquo;s own<br>news pages</strong>\n'
                f'      <a href="{esc(art.get("source", ""), attr=True)}" target="_blank" rel="noopener">'
                f'The original page <span aria-hidden="true">&#8599;</span></a>\n'
                f'      <a href="news.html">All CIRS news</a>\n'
                f'    </aside>\n')

    return (f'<article class="art" id="top">\n'
            f'  <header class="art__head">\n'
            f'    <div class="art__shell">\n'
            f'      <nav class="art__breadcrumb" aria-label="Breadcrumb">\n'
            f'        <a href="news.html">News</a><span aria-hidden="true">/</span>'
            f'<span>{esc(art["section"])}</span>\n'
            f'      </nav>\n'
            f'      <p class="art__edition">{edition}</p>\n'
            f'      <h1 class="art__title">{esc(art["title"])}</h1>\n'
            f'{dek}      <div class="art__credits">\n'
            f'        <span>{esc(art["section"])}</span>\n'
            f'        <span>{esc(art["date"])}</span>\n'
            f'      </div>\n'
            f'    </div>\n'
            f'  </header>\n'
            f'  <div class="art__layout">\n'
            f'{rail}'
            f'    <div class="art__content">\n'
            f'{image}      <div class="art__body">\n'
            f'{body}\n'
            f'{gallery}      </div>\n'
            f'      <p class="art__back"><a href="news.html">&#8592; Back to News</a></p>\n'
            f'    </div>\n'
            f'  </div>\n'
            f'</article>')


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
      <a href="crossroads.html">All issues of The Crossroads</a>
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
    return f'''<section class="pagehead on-dark" id="top" data-ground="#181815">
  <div class="wrap pagehead__inner">
    <p class="marker"><span class="sc">{eyebrow}</span></p>
    <h1 class="serif" data-split>{heading}</h1>
    <p class="lead">{lead}</p>
{cta}  </div>
</section>'''


HOME_TAB = '''      <a class="nv-tab nv-tab--home" href="index.html">
        <span class="nv-tab__icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2.6 7.6 9 2.2l6.4 5.4M4.4 9.2v6.2h9.2V9.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="nv-tab__label">Home</span>
      </a>
'''


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
    return f'''<section class="pagehero" id="top" data-ground="#11110F">
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
    # Its own size, so the page keeps the space before the file arrives
    # (founder.css draws every .ffig img at height:auto, which the attribute
    # cannot override), and an 800px cut from tools/make-media.py for the
    # screens that draw it at a third of its width.
    extra = ""
    dims = founder.size(slot)
    if dims:
        w, h, small = dims
        extra = f' width="{w}" height="{h}"'
        if small:
            extra += (f' srcset="{small[0]}?{CACHE_BUST} {small[1]}w, {src}?{CACHE_BUST} {w}w"'
                      f' sizes="{sizes or founder.SIZES.get(slot, "(max-width: 899px) 92vw, 44vw")}"')
    elif sizes:
        extra = f' sizes="{sizes}"'
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
                     f'aria-label="Read The Crossroads {issue["label"]}">'
                     f'<img src="{issue["cover"]}?{CACHE_BUST}" alt="The Crossroads {issue["label"]} cover" '
                     'width="300" height="420" loading="lazy" decoding="async" fetchpriority="low"></a>')
    return '<div class="crossroads-stories__media"><div class="crossroads-stories__stack">' + ''.join(cards) + '</div></div>'


def crossroads_latest(feature=False):
    issue = next((i for i in crossroads.issues() if i["latest"] and i["pdf"]), None)
    if not issue:
        return ""
    if feature and issue["cover"]:
        return (f'<a class="crossroads-archive-hero__feature" href="{issue["pdf"]}" '
                f'aria-label="Read the latest issue: {issue["label"]} (PDF)">'
                f'<img src="{issue["cover"]}?{CACHE_BUST}" alt="" width="300" height="420" loading="lazy" decoding="async" fetchpriority="low">'
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
                    f'alt="Cover of The Crossroads {label}" loading="lazy" fetchpriority="low" '
                    f'width="720" height="1008">')
        else:
            face = (f'''<span class="crcover__mast">The Crossroads</span>
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
        <h3 class="sr-only">The Crossroads {label}</h3>
        <a class="crcard__link" href="{issue["pdf"]}" target="_blank" rel="noopener"
           aria-label="Read The Crossroads {label} in a new tab">
          {cover}
        </a>
        <div class="crcard__foot">
          <span class="crcard__label">{label}</span>
          <a class="crcard__state" href="{issue["pdf"]}" target="_blank" rel="noopener">Read issue &rarr;</a>
          <a class="crcard__dl" href="{issue["pdf"]}" download
             aria-label="Download The Crossroads {label} as a PDF">
            <svg width="13" height="13" viewBox="0 0 14 14" aria-hidden="true"><path d="M7 1v8M3.5 6L7 9.5 10.5 6M2 12.5h10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            Download
          </a>
        </div>
      </article>''')
        else:
            cards.append(f'''      <article class="crcard{mods} is-pending rv">
        <h3 class="sr-only">The Crossroads {label}</h3>
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
                # The wall follows a full-screen introduction. Its covers are
                # decoration and must not delay the title or essential controls.
                lazy = ' loading="lazy" fetchpriority="low"'
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


def sports_house_bands_html():
    """Sports-page house bands from the same sourced data as the Houses page."""
    bands = []
    for index, h in enumerate(sports_house_history.HOUSES):
        slug = h["slug"]
        active = " is-active" if index == 0 else ""
        expanded = "true" if index == 0 else "false"
        bands.append(f'''    <article class="house-band house-band--{slug}{active}" id="sports-house-{slug}">
      <div class="house-band__media">
        <img src="{houses.img(h["hero"])}" alt="{esc(h["hero_alt"], attr=True)}"
             width="900" height="1125" loading="lazy" decoding="async">
        <div class="house-band__tint house-band__tint--{h["colour"].lower()}" aria-hidden="true"></div>
      </div>
      <div class="house-band__content">
        <div class="house-band__header">
          <span class="house-band__color-tag">{h["colour"].upper()}</span>
          <h3 class="serif house-band__name"><button type="button" class="house-band__trigger"
            id="sports-house-{slug}-name" aria-expanded="{expanded}"
            aria-controls="sports-house-{slug}-details">{h["name"]}</button></h3>
        </div>
        <section class="house-band__details" id="sports-house-{slug}-details"
                 aria-labelledby="sports-house-{slug}-name">
          <p class="house-band__identity">{h["colour"]} house &middot; {h["symbol"]}</p>
          <ul class="house-band__facts"><li><strong>From the school record:</strong> {h["fact"]}</li></ul>
          <p class="house-band__link"><a href="houses.html#house-{slug}">Explore {h["name"]} House</a></p>
        </section>
      </div>
    </article>''')
    return "\n".join(bands)


# Houses owns its page rendering; Sports retains the historical data above.
def houses_hero_html():
    return houses.hero_html()


def houses_chapters_html():
    return houses.chapters_html()


def houses_track_html():
    return houses.stage_html()


def houses_record_html():
    return houses.archive_html()


def houses_gallery_html():
    return houses.gallery_html()


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
    if page.get("notfound"):
        # The not-found page has no address of its own to be canonical for,
        # and is never one to index. This is not the review preview's
        # site-wide noindex and does not go when that does at launch.
        head = re.sub(r'<link rel="canonical"[^>]*>\n',
                      '<meta name="robots" content="noindex">\n', head)

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

    if slug == "spiritual-life":
        # A synchronous gate establishes the optional scene before first paint.
        # No script or a failed module leaves a readable photographic opening.
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/spiritual-opening.css?{CACHE_BUST}">\n'
            '<link rel="modulepreload" href="assets/js/spiritual-light.js">\n'
            '<link rel="modulepreload" href="assets/founder-opening/vendor/three.module.min.js">\n'
            '<link rel="modulepreload" href="assets/founder-opening/vendor/three.core.js">\n'
            '<script>if(!matchMedia("(prefers-reduced-motion: reduce)").matches){document.documentElement.classList.add("sp-boot","sl-body-motion");setTimeout(function(){if(!window.__spiritualOpeningReady)document.documentElement.classList.remove("sp-boot");if(!window.__spiritualBodyReady)document.documentElement.classList.remove("sl-body-motion")},5000)}</script>\n</head>')

    if slug == "math-challenge":
        # Decided before first paint, so the stage never lays out twice:
        # mc-motion lets headings ride in, mc-kinetic makes the stage the
        # tall scrolled installation. Without motion, WebGL or height it
        # stays an ordinary opening. A timer undoes both if the page script
        # never starts, so nothing waits on a script that did not arrive.
        # The sculpture is imported by matharena.js with this same query; the
        # preload also puts it in front of stage-deploy.py, which ships only
        # what a page names.
        head = head.replace("</head>",
            f'<link rel="modulepreload" href="assets/js/math-sculpture.js?{CACHE_BUST}">\n'
            '<link rel="modulepreload" href="assets/founder-opening/vendor/three.module.min.js">\n'
            '<link rel="modulepreload" href="assets/founder-opening/vendor/three.core.js">\n'
            '<script>(function(){var d=document.documentElement;'
            'if(matchMedia("(prefers-reduced-motion: reduce)").matches)return;'
            'd.classList.add("mc-motion");'
            'if("WebGLRenderingContext" in window&&innerHeight>=500)d.classList.add("mc-kinetic");'
            'setTimeout(function(){if(!window.__mcBooted)d.classList.remove("mc-motion","mc-kinetic")},6000)'
            '})()</script>\n</head>')

    # Shared typography follows page sheets so the approved roles stay consistent.
    head = head.replace("</head>",
        f'<link rel="stylesheet" href="assets/css/typography.css?{CACHE_BUST}">\n</head>')

    if slug in ("crossroads", "founder", "art-attack", "spiritual-life", "math-challenge"):
        # These pages open with their own films (Math Challenge with its
        # sculpture, whose first frame is the page's heading and actions). The shared curtain would hide
        # the skip control and add a second scroll lock. Keep the no-script
        # footer fallback after removing the curtain-specific head block.
        curtain_note = head.index("<!-- The opening curtain")
        curtain_note_end = head.index("</noscript>", curtain_note) + len("</noscript>")
        head = (head[:curtain_note]
                + '<noscript><style>.footer-wrap{position:relative}</style></noscript>'
                + head[curtain_note_end:])
    if slug == "art-attack":
        # The title has a safe system-font fallback; let the still and CSS
        # establish the opening before optional webfont files compete.
        head = head.replace(
            '<link rel="preload" href="assets/fonts/monasans-normal.woff2" as="font" type="font/woff2" crossorigin>\n', "")
        head = head.replace(
            '<link rel="preload" href="assets/fonts/bodonimoda-normal.woff2" as="font" type="font/woff2" crossorigin>\n', "")
    if slug == "crossroads":
        # Crossroads opens with vector lettering, so font preloads compete
        # with its introduction and navigation before text needs them.
        head = head.replace(
            '<link rel="preload" href="assets/fonts/monasans-normal.woff2" as="font" type="font/woff2" crossorigin>\n', "")
        head = head.replace(
            '<link rel="preload" href="assets/fonts/bodonimoda-normal.woff2" as="font" type="font/woff2" crossorigin>\n', "")
        head = head.replace(
            "</head>",
            '<style>body.crossroads-intro-active :is(.progress,.ring,.totop,.jump,.footer-wrap){visibility:hidden!important}'
            'body.crossroads-intro-active .crossroads-intro{background:#16031c url("assets/img/crossroads/opening-poster.jpg") center/cover no-repeat}'
            '</style>'
            '<link rel="preload" as="image" href="assets/img/crossroads/opening-poster.jpg" fetchpriority="high">\n'
            f'<link rel="preload" href="assets/js/crossroads-intro.js?{CACHE_BUST}-intro-9" as="script" fetchpriority="high">\n'
            f'<link rel="stylesheet" href="assets/css/crossroads-intro.css?{CACHE_BUST}-intro-9">\n'
            f'<link rel="stylesheet" href="assets/css/crossroads-archive.css?{CACHE_BUST}">\n'
            f'<link rel="stylesheet" href="assets/css/crossroads-stories.css?{CACHE_BUST}-hover-4">\n'
            f'<link rel="stylesheet" href="assets/css/crossroads-manuscript.css?{CACHE_BUST}">\n'
            '<noscript><style>body.crossroads-intro-active :is(.header,.drawer,.progress,.ring,.totop,.jump,.skip-link,.footer-wrap){visibility:visible!important}'
            '.crossroads-intro[data-crossroads-intro-pending] .crossroads-intro__opening{display:none}'
            '.crossroads-intro[data-crossroads-intro-pending] .crossroads-intro__content{visibility:visible;opacity:1}'
            '.crossroads-intro[data-crossroads-intro-pending]{background:var(--cr-purple-deep)}'
            '.crossroads-intro[data-crossroads-intro-pending] .crossroads-intro__base{visibility:visible!important}'
            '</style></noscript>\n</head>')
    if slug == "founder":
        # The opening's intro film and portrait both need scripting. Without
        # it the film is hidden, and the still first portrait stands in for
        # the interactive one, with only the link down to the life story.
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/founder-portrait.css?{CACHE_BUST}-portrait-1">\n'
            f'<link rel="stylesheet" href="assets/css/founder-gurudev-journey.css?{CACHE_BUST}-story-7">\n'
            '<noscript><style>.gurudev-opening .gc-intro{display:none}'
            '.gurudev-opening .gp-hero[hidden]{display:block!important}'
            '.gurudev-opening :is(.gp-hint,.gp-watch,.gp-sound,.gp-toggle){display:none}'
            # The script sizes the still to the window (--gp-photo-*). Without
            # it the default is 72% of the width, which on a wide window is
            # taller than the window: cropped, and over the name beneath it.
            '@media (min-width:651px){.gurudev-opening .gp-images img{width:auto;height:calc(100% - 132px);'
            'left:50%;top:64px;transform:translateX(-50%)}}'
            '</style></noscript>\n</head>')
    if page.get("cw"):
        head = head.replace("</head>", creativewriting.head_html(page["cw"]) + "</head>")
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
        pending += opening.get("noscript_css", "")
        critical_art_attack = ('''<style id="art-attack-critical">
body.art-attack{--film-ground:#0B080D;--film-crop:50% 50%;--film-crop-narrow:50% 50%;background:#0B080D}
body.art-attack .film{position:relative;height:var(--film-run,460vh);background:#000}
body.art-attack .film__stage{position:sticky;top:0;height:100vh;height:100svh;overflow:hidden;background:#0B080D}
body.art-attack .film__video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 50%;display:block;pointer-events:none;opacity:1;transition:opacity .3s ease-out}
body.art-attack .film[data-film-pending] .film__video{opacity:0}
body.art-attack .film[data-film-pending] .film__still{visibility:visible}
body.art-attack .film__still{position:absolute;z-index:0;inset:0;width:100%;height:100%;display:block;object-fit:cover;object-position:50% 50%}
body.art-attack .film__stage:after{content:"";position:absolute;z-index:1;left:0;right:0;bottom:0;height:clamp(70px,13svh,150px);background:linear-gradient(to bottom,transparent,#170F18);pointer-events:none}
body.art-attack .film__title{position:absolute;z-index:2;left:50%;right:auto;top:49%;bottom:auto;width:min(86vw,720px);margin:0;padding:0;color:#FAF9F3;text-align:center;text-transform:none;opacity:1;transform:translate(-50%,-50%);filter:none;text-shadow:0 2px 30px rgba(11,8,13,.55),0 0 2px rgba(11,8,13,.35)}
body.art-attack .film__art-prefix{display:block;margin-bottom:clamp(12px,2vh,22px);padding-left:.42em;font-family:var(--font-ui,Arial,sans-serif);font-size:clamp(12px,1.2vw,17px);font-weight:400;letter-spacing:.42em;line-height:1;text-transform:uppercase;color:#E3DCCB}
body.art-attack .film__art-name{display:block;font-family:var(--font-display,Georgia,serif);font-size:clamp(56px,6.3vw,100px);font-weight:500;letter-spacing:-.055em;line-height:.92;white-space:nowrap}
@media(max-aspect-ratio:6/5){body.art-attack .film__still{object-position:50% 50%}body.art-attack .film__title{top:52%}}
@media(max-width:720px){body.art-attack .film__title{width:calc(100vw - 32px)}body.art-attack .film__art-prefix{font-size:12px}body.art-attack .film__art-name{font-size:clamp(48px,12vw,76px)}}
@media(max-width:360px){body.art-attack .film__art-name{font-size:clamp(42px,11.5vw,52px)}}
@media(prefers-reduced-motion:reduce){body.art-attack .film{height:100svh}}
</style>\n''') if slug == "art-attack" else ""
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/filmintro.css?{CACHE_BUST}">\n'
            f'{critical_art_attack}'
            f'<noscript><style>.film{{height:100svh}}body.art-attack .film{{height:100svh}}{nudge}{pending}{still}'
            '</style></noscript>\n</head>')
        if slug == "art-attack" and opening.get("still"):
            # This is the approved frame behind the title. Discover it in the
            # head so the large archive document and the later film request do
            # not keep the first visible composition black on a slow link.
            head = head.replace(
                "</head>",
                f'<link rel="preload" href="assets/img/{opening["still"]}" as="image" fetchpriority="high">\n</head>')
    if slug == "theatre":
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/theatre.css?{CACHE_BUST}">\n</head>')
    if slug == "our-laurels":
        # The opening's two words are set in Newsreader, the face the Founder
        # opening introduced; preload it in place of the display face.
        head = head.replace(
            '<link rel="preload" href="assets/fonts/bodonimoda-normal.woff2" as="font" type="font/woff2" crossorigin>\n',
            '<link rel="preload" href="assets/fonts/newsreader-normal.woff2" as="font" type="font/woff2" crossorigin>\n')
        # The opening's first frame is its start state, not its end state: this
        # marks the document before anything paints (laurels.css hides the count,
        # its word and the fragments while it is set), and laurels.js takes it
        # off when the entrance begins. If scripting never arrives, or motion is
        # reduced, the page shows itself.
        head = head.replace("</head>",
            '<script>(function(){var d=document.documentElement;'
            'if(matchMedia("(prefers-reduced-motion: reduce)").matches)return;'
            'd.classList.add("lr-pre");'
            'setTimeout(function(){d.classList.remove("lr-pre")},4500)})()</script>\n'
            # Without scripting the archive's rows cannot open, so every record is laid open.
            '<noscript><style>.lr-row__panel[hidden]{display:block}.lr-row__plus{display:none}</style></noscript>\n</head>')
    if slug == "leadership":
        # The message a #msg-... URL asks for is chosen before first paint.
        head = head.replace("</head>", leadership.head_script() + leadership.head_css() + "</head>")
    if slug == "captures":
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/captures-featured.css?{CACHE_BUST}">\n'
            f'<link rel="stylesheet" href="assets/css/captures-gallery.css?{CACHE_BUST}">\n'
            f'<link rel="stylesheet" href="assets/css/captures-hero.css?{CACHE_BUST}">\n'
            # "Through our eyes" starts from its dark first frame. That is
            # decided before first paint, so the field is never drawn
            # finished and then hidden; a timer undoes it if the page script
            # never starts, which leaves the field's written composition.
            '<script>(function(){var d=document.documentElement;'
            'if(matchMedia("(prefers-reduced-motion: reduce)").matches)return;'
            'd.classList.add("toe-motion");'
            'setTimeout(function(){if(!window.__toeBooted)d.classList.remove("toe-motion")},6000)'
            '})()</script>\n</head>')
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
    if (slug in ("admissions", "school-info", "news", "curriculum", "school-history", "leadership",
                 "our-laurels")
            or page.get("notfound") or page.get("cw")):
        # These pages open immediately with their own video, document sheets,
        # journal masthead or, on Curriculum, the rising path of the grades
        # the page leads with — and School History on its archive's title — so
        # the shared curtain is unnecessary. A visitor who has lost their way
        # needs the way back at once, not a curtain first.
        curtain_note = head.index("<!-- The opening curtain")
        curtain_note_end = head.index("</noscript>", curtain_note) + len("</noscript>")
        head = head[:curtain_note] + head[curtain_note_end:]

    # The cinematic closing scene and practical footer are shared by all
    # scrolling public pages. Load this sheet after page-specific styles.
    if not wall:
        head = head.replace("</head>",
            f'<link rel="stylesheet" href="assets/css/footer.css?{CACHE_BUST}-footer-1">\n</head>')

    head = head.replace("</head>",
        f'<link rel="stylesheet" href="assets/css/drawer.css?{CACHE_BUST}-nav-4">\n'
        # Without scripting nothing moves the header between its states, so
        # it stays the readable pill throughout.
        '<noscript><style>.nv-header{opacity:1!important;visibility:visible!important;'
        '--nav-name:var(--ink);--nav-sub:var(--ink-mute);--nav-text:var(--ink);'
        '--nav-icon:var(--ink-soft);--nav-lift:none}'
        '.nv-header__bar{width:min(calc(100% - 2 * var(--nv-pill-inset)),var(--nv-pill-max))!important;'
        'height:var(--nv-pill-h)!important;margin-top:var(--nv-pill-inset)!important;'
        'border-radius:999px!important;background-color:var(--paper)!important;'
        'border-color:var(--rule)!important}'
        '</style></noscript>\n</head>')

    # Openings with no full-screen visual hero start on the floating pill.
    # Other pages keep the controls clear over their first visual section
    # and gather into the pill once the reader scrolls.
    lite = bool(page.get("litehead"))
    header_start = ("content" if page.get("banner") or page.get("post") or page.get("news")
                    or page.get("notfound")
                    or (page.get("cw") and (page["cw"]["kind"] != "main"
                        or page["cw"].get("collection") != "all"))
                    or slug in ("news", "leadership", "school-info", "blog", "cultural-gallery")
                    else "hero")
    header_tone = "light" if lite else "dark"
    # A page opening on a scrubbed film is marked twice: "film" for the
    # mechanics every such page shares, and its own slug for the handful of
    # decisions its footage makes for it.
    classes = [c for c in ["wall" if wall else page.get("sheet"),
                           "film" if page.get("opening") else None,
                           slug if page.get("opening") else None,
                           "crossroads-intro-active" if slug == "crossroads" else None,
                           "parent-portal" if slug == "parent-portal" else None,
                           "litehead" if lite else None] if c]
    body_class = " ".join(classes)
    chrome = read("tools/partials/chrome.html")
    if slug == "founder":
        chrome = chrome.replace('<div class="progress" id="progress" aria-hidden="true"></div>\n', "")
    if slug == "blog" or page.get("post") or page.get("cw"):
        # Journal pages open directly on readable type, and Creative Writing
        # opens on the title and a student's own line. The shared full-screen
        # curtain would hide them and force an unrelated wait.
        intro_start = chrome.index("<!-- Opening sequence.")
        intro_end = chrome.index("<!-- Film lightbox", intro_start)
        chrome = chrome[:intro_start] + chrome[intro_end:]
    if slug == "parent-portal":
        # The full-window photograph is this page's opening; the shared opaque
        # curtain would cover it and run its own scroll lock.
        start = chrome.index("<!-- Opening sequence.")
        end = chrome.index("<!-- Film lightbox", start)
        chrome = chrome[:start] + chrome[end:]
    if (slug in ("admissions", "school-info", "news", "curriculum", "school-history", "leadership",
                 "our-laurels")
            or page.get("notfound")):
        # Admissions, School Information, News, Curriculum, School History and
        # Leadership each have their own visible opening. The shared curtain would delay it behind a
        # blank screen.
        intro_start = chrome.index("<!-- Opening sequence.")
        intro_end = chrome.index("<!-- Film lightbox", intro_start)
        chrome = chrome[:intro_start] + chrome[intro_end:]
    parts = [head, f'<body class="{body_class}">' if body_class else "<body>",
             chrome.rstrip("\n")]
    if slug in ("crossroads", "founder", "art-attack", "spiritual-life", "math-challenge"):
        intro_start = parts[-1].index("<!-- Opening sequence.")
        intro_end = parts[-1].index("<!-- Film lightbox", intro_start)
        parts[-1] = parts[-1][:intro_start] + parts[-1][intro_end:]
    drawer = (read("tools/partials/drawer.html")
              .replace("{{NAV}}", nav_html(slug))
              .replace("{{ACTIVE_GROUP}}", str(menu_group_index(slug)))
              .replace("{{BRAND_HREF}}", "#top" if slug == "index" else "index.html"))
    # Keep the approved Home control on every page. On Home it returns to the
    # opening hero without reloading the page or replaying the curtain.
    header = (read("tools/partials/header.html")
              .replace("{{BRAND_HREF}}", "#top" if slug == "index" else "index.html")
              .replace("{{HOME_TAB}}", HOME_TAB.replace('href="index.html"', 'href="#top"')
                       if slug == "index" else HOME_TAB)
              .replace("{{HEADER_MODE}}", header_start)
              .replace("{{HEADER_TONE}}", header_tone)
              .replace("{{HEADER_TABS}}", ""))
    if slug == "news":
        header = header.replace('class="nv-tab nv-tab--news" href="news.html"',
                                'class="nv-tab nv-tab--news" href="news.html" aria-current="page"')
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
    # The page shell can continue parsing for several seconds on a slow
    # connection. Start the shared navigation controller once its header,
    # drawer and main landmark (including the opening composition) exist;
    # waiting for the deferred bundle at the end of a long archive page leaves
    # Menu inert. The head preload avoids a second request in the common case.
    parts.append(f'<script src="assets/js/navigation.js?{CACHE_BUST}-core-3"></script>')
    # The "On this page" index goes here, before the content it indexes.
    jump_at = len(parts)
    if page.get("cw"):
        content = creativewriting.render(page["cw"])
    elif page.get("post"):
        content = article_html(page)
    elif page.get("news"):
        content = news_article_html(page)
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
    if slug == "our-laurels":
        content = laurels.expand(content)
    if slug == "leadership":
        content = leadership.expand(content)
    if slug == "the-cirs-experience":
        content = experience.expand(content, CACHE_BUST)
    content = (content.replace("{{ARTSWALL}}", artswall_html())
                        .replace("{{SPORTS_HOUSE_BANDS}}", sports_house_bands_html() if slug == "sports" else "")
                       .replace("{{HOUSES_HERO}}", houses_hero_html())
                       .replace("{{HOUSES_CHAPTERS}}", houses_chapters_html())
                       .replace("{{HOUSES_TRACK}}", houses_track_html())

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
                       .replace("{{MATH_JOURNEY}}", mathchallenge.journey_html() if slug == "math-challenge" else "")
                       .replace("{{MATH_ZONES}}", mathchallenge.zones_html() if slug == "math-challenge" else "")
                       .replace("{{MATH_FILTERS}}", mathchallenge.filters_html() if slug == "math-challenge" else "")
                       .replace("{{MATH_ARCHIVE}}", mathchallenge.archive_html() if slug == "math-challenge" else "")
                       .replace("{{CAPTURES_GALLERY}}", captures.gallery_html() if slug == "captures" else "")
                       .replace("{{CAPTURES_HERO_BEHIND}}", captures.hero_html()[0] if slug == "captures" else "")
                       .replace("{{CAPTURES_HERO_OVER}}", captures.hero_html()[1] if slug == "captures" else "")
                       .replace("{{CAPTURES_END}}", captures.end_html() if slug == "captures" else "")
                       .replace("{{CAPTURES_END_CAPTION}}", captures.END[2])
                       .replace("{{CAPTURES_COUNT_CAP}}", captures.count_word().capitalize())
                       .replace("{{CAPTURES_CHAPTER_NAV}}", captures.chapter_nav_html() if slug == "captures" else "")
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
                       .replace("{{ALUMNI_COUNT}}", alumni.count_word())
                       .replace("{{FOUNDER_GURUDEV_JOURNEY}}", founder_story.journey_html() if slug == "founder" else ""))
    if slug == "news":
        # The term in review, and its entries in the archive: tools/cvpnews.py.
        content = (content.replace("{{NEWS_TERM}}", cvpnews.term_html())
                          .replace("{{NEWS_TERM_ARCHIVE}}", cvpnews.archive_html()))
    if slug == "our-results":
        content = (content.replace("{{RESULTS_REGIONS}}", results_regions_html())
                          .replace("{{RESULTS_FILTERS}}", results_filters_html())
                          .replace("{{RESULTS_DIRECTORY}}", results_directory_html())
                          .replace("{{RESULTS_COUNT_CAP}}", alumni.count_word().capitalize())
                          .replace("{{RESULTS_COUNT}}", str(alumni.count())))
    if slug == "theatre":
        content = (content.replace("{{THEATRE_PROLOGUE}}", theatre.prologue_html())
                          .replace("{{THEATRE_PROGRAMME}}", theatre.programme_html())
                          .replace("{{THEATRE_ANAND_UTSAV}}", theatre.anand_utsav_html())
                          .replace("{{THEATRE_INTERMISSION}}", theatre.intermission_html())
                          .replace("{{THEATRE_MASQUERADES}}", theatre.masquerades_html())
                          .replace("{{THEATRE_CLASSES}}", theatre.classes_html())
                          .replace("{{THEATRE_CURTAIN_CALL}}", theatre.curtain_call_html())
                          .replace("{{THEATRE_ONWARD}}", theatre.onward_html())
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
        if slug in ("captures", "leadership", "the-cirs-experience", "our-laurels") or page.get("notfound"):
            # Captures already ends with its own full-width photograph, and
            # Leadership with its staff photograph and a compact pair of
            # links: a second full-screen scene would compete with both.
            # Keep that as the page's final image before the site footer.
            # The not-found page is kept to its one message and its links.
            footer = footer[footer.index('<div class="footer-wrap">'):]
        if slug == "admissions":
            footer = footer.replace('href="admissions.html#examination">Important Dates',
                                    'href="admissions.html#dates">Important Dates')
        if slug == "school-history":
            # The arrival already uses campus-band. Give the archive's close
            # the courtyard photograph on every viewport, in one picture.
            footer = footer.replace('src="assets/img/campus-band.jpg"',
                                    'src="assets/img/campus-lawn.jpg"', 1)
            footer = footer.replace('width="1920" height="1080"',
                                    'width="1600" height="900"', 1)
        if page.get("closing"):
            footer = closing_html(footer, page["closing"])
        parts.append(footer)
    if slug == "crossroads":
        # This page-specific controller only owns the introduction. Load it
        # before shared animation dependencies so Skip and its bounded lock
        # are ready as soon as the critical styles have arrived.
        parts.append(f'<script src="assets/js/crossroads-intro.js?{CACHE_BUST}-intro-9" defer></script>')
    shared_scripts = read("tools/partials/scripts.html").replace("{{CACHE_BUST}}", CACHE_BUST)
    if slug == "houses":
        shared_scripts = "\n".join(line for line in shared_scripts.splitlines() if 'src="assets/vendor/lenis.min.js' not in line)
    parts.append(shared_scripts.rstrip("\n"))
    if not wall:
        parts.append(f'<script src="assets/js/footer.js?{CACHE_BUST}-footer-1" defer></script>')
    if slug == "crossroads":
        parts.append(f'<script src="assets/js/crossroads-archive.js?{CACHE_BUST}" defer></script>')
        parts.append(f'<script src="assets/js/crossroads-stories.js?{CACHE_BUST}-hover-4" defer></script>')
        parts.append(f'<script src="assets/js/crossroads-manuscript.js?{CACHE_BUST}" defer></script>')
    if slug == "founder":
        # In this order: the sound the portrait calls, the portrait, then the
        # sequence that hands the intro film over to the portrait.
        parts.append(f'<script src="assets/js/founder-liquid-sound.js?{CACHE_BUST}-portrait-1" defer></script>')
        parts.append(f'<script src="assets/js/founder-portrait.js?{CACHE_BUST}-portrait-2" defer></script>')
        parts.append(f'<script src="assets/js/founder-opening.js?{CACHE_BUST}-portrait-1" defer></script>')
        parts.append(f'<script src="assets/js/founder-gurudev-journey.js?{CACHE_BUST}-story-6" defer></script>')
    if slug == "the-cirs-experience":
        parts.append(f'<script src="assets/js/student-life-journey.js?{CACHE_BUST}-experience-1" defer></script>')
    if slug == "spiritual-life":
        parts.append(f'<script src="assets/js/spiritual.js?{CACHE_BUST}" defer></script>')
        parts.append(f'<script type="module" src="assets/js/spiritual-opening.js?{CACHE_BUST}"></script>')
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
        # The archive, the divisions and the stage's lettering. It imports
        # the optional sculpture (math-sculpture.js) itself, so a failed
        # graphics load cannot take the filters or the links with it.
        parts.append(f'<script src="assets/js/matharena.js?{CACHE_BUST}" defer></script>')
    if page.get("cw"):
        parts.append(f'<script src="assets/js/cwriting.js?{CACHE_BUST}" defer></script>')
    if slug == "houses":
        parts.append(f'<script src="assets/js/houses-journey.js?{CACHE_BUST}-houses-3" defer></script>')
    if slug == "blog":
        parts.append(f'<script src="assets/js/blog-index.js?{CACHE_BUST}-editorial-1" defer></script>')
    if slug == "festivals":
        parts.append(f'<script src="assets/js/festivals.js?{CACHE_BUST}" defer></script>')
    if slug == "art-attack":
        parts.append(f'<script src="assets/js/artattack.js?{CACHE_BUST}" defer></script>')
    if slug == "leadership":
        parts.append(f'<script src="assets/js/leadership.js?{CACHE_BUST}" defer></script>')
    if slug == "curriculum":
        parts.append(f'<script src="assets/js/curriculum.js?{CACHE_BUST}-atlas-2" defer></script>')
    if slug == "school-history":
        parts[0] = parts[0].replace('</head>', f'<link rel="stylesheet" href="assets/css/history-cinematic.css?{CACHE_BUST}-4">\n</head>')
        parts.append(f'<script src="assets/js/history.js?{CACHE_BUST}-cinematic-4" defer></script>')
        # The journey's controller imports Three.js only
        # on a window wide enough for the 3D path, so a phone never fetches it.
        parts.append(f'<script type="module" src="assets/js/history-cinematic-journey.js?{CACHE_BUST}-4"></script>')
    if slug == "our-laurels":
        parts.append(f'<script src="assets/js/laurels.js?{CACHE_BUST}" defer></script>')
    if page.get("opening"):
        parts.append(f'<script src="assets/js/filmintro.js?{CACHE_BUST}" defer></script>')
    if slug == "sports":
        parts.append(f'<script src="assets/js/sports-journey.js?{CACHE_BUST}" defer></script>')
    if slug == "theatre":
        parts.append(f'<script src="assets/js/theatre.js?{CACHE_BUST}" defer></script>')
    if slug == "captures":
        parts.append(f'<script src="assets/js/captures-featured.js?{CACHE_BUST}" defer></script>')
        parts.append(f'<script src="assets/js/captures-gallery.js?{CACHE_BUST}" defer></script>')
        parts.append(f'<script src="assets/js/captures-hero.js?{CACHE_BUST}" defer></script>')
    if slug == "parent-portal":
        parts.append(f'<script src="assets/js/parent-portal-motion.js?{CACHE_BUST}" defer></script>')
    if wall:
        parts.append(f'<script src="assets/js/artswall.js?{CACHE_BUST}-focus-1" defer></script>')
    parts += ["</body>", "</html>", ""]

    # The index goes in after rewrite_links: its anchors name sections on this
    # page, and must not be sent to the page an old single-page anchor meant.
    html = to_depth(rewrite_links("\n".join(parts), slug).replace(JUMP_MARK, jump), slug)
    if page.get("notfound"):
        html = to_root(html)
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
# The school's own news reports, one page each. They are not in MENU — the
# News page is how a reader reaches them, exactly as the Blog is for articles.
for _art in newsarticles.ARTICLES + cvpnews.ARTICLES:
    PAGES[_art["slug"]] = {
        "nav": esc(_art["title"]),
        "title": esc(_art["title"], attr=True) + " | CIRS News",
        "description": esc((_art["dek"] or _art["title"])[:180], attr=True),
        "sheet": "blog",
        "cache_suffix": "-news-archive-1",
        "uc": False,
        "jump": False,
        # An archived report opens on paper like a Blog article does, so the
        # header cannot float over it in white lettering.
        "litehead": True,
        "news": _art,
    }


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


# Creative Writing's two collection views and one page per edition, all
# written from tools/creative-writing-content.json. Not in MENU: the
# Creative Writing page is how a reader reaches them.
PAGES.update(creativewriting.page_entries())


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
