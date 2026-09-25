"""The four CIRS houses, and every fact this site states about them.

One module, read by tools/build-site.py, which writes the house chapters, the
competition archive, the standings table and the gallery into the page. There
is no second copy of a house name, a colour or a result anywhere.

WHERE EACH FACT COMES FROM
--------------------------
Nothing below is inferred, and nothing below is invented. Every field carries
a source, and a field with no source is absent rather than filled in.

The repository holds the school's own material from the old website in pdf/,
and it turned out to answer almost everything:

  pdf/Khel Mela Sakshi 2008.pdf          February 2008, the Khel Mela issue of
                                         Sakshi. Pages 12-13 are the four
                                         houses writing about themselves. This
                                         is where the symbols come from, and
                                         Vasishtha's red and Vishwamitra's
                                         green in the school's own words.
  pdf/Sakshi Newleter March 2008.pdf     the Khel Mela 2008 results.
  pdf/Sakshi Newleter summer special     the Senior Social Science Quiz, and
      May 2008.pdf                       the four house symposiums with their
                                         titles.
  pdf/E-Newletter Octnov08.pdf           four inter-house results from the
                                         second term of 2008, each with all
                                         four houses placed.

And the photograph library answered the rest. The house colours are not
written down anywhere on this site, but they are worn in the school's own
photographs, with a house name visible on the garment:

  assets/source/IMG_0612.JPG             a deep red basketball jersey reading
                                         VASISHTHA, and red house flags on the
                                         officials' table.
  assets/source/IMG_8229.JPG             the investiture, VALMIKI on yellow
                                         sashes.
  assets/source/IMG_20260709_181900.jpg  a green tee with the ending
                                         WAMITRA visible on another student
                                         in the same frame; Sakshi gives the
                                         full house name and green colour.
  assets/source/IMG_20260709_181712.jpg  a blue tee reading VYASA.
  assets/source/IMG_0851.JPG             all four colours on one tennis court.
  assets/source/0G8A3883.JPG             the medal ribbons read XXIX ANNUAL
                                         AQUATIC MEET, KHEL MELA 2025-2026.

SPELLING
--------
The school's own documents are not consistent with themselves — Vasishtha,
Vasishta and Vashistha all appear across the 2008 newsletters, and Vishwamitra
alternates with Viswamitra and Viswamithra. The spellings used here follow the
photographed house kit where legible, and the headings in the newsletters:

    Vasishtha     printed on the basketball jersey
    Valmiki       consistent everywhere
    Vishwamitra   the heading spelling in Sakshi, and the photographed kit
    Vyasa         printed on the house tee, consistent everywhere

MOTTOS
------
There are none here, because none is documented. Each house instead carries a
short quotation from what that house wrote about itself in Sakshi in February
2008, marked as a quotation and dated. A quotation is not a motto and this
page does not present it as one. See MISSING below.

MISSING
-------
Listed so it is asked for rather than guessed at:

  * house mottos, if the houses have them
  * the house emblems as artwork — the animals are documented in words, but
    no drawn or photographed emblem is in this repository
  * current house captains and house masters — the 2008 newsletters name the
    students who held those posts eighteen years ago, which is not something
    to publish
  * the house championship holders since 2008, and the current standings
  * photographs of the house symposiums, and of Masquerade by house
  * the date of every photograph on this page. The gallery would carry a year
    beside each caption if one were known; none of these frames arrived with
    a date, so none is shown rather than a year being estimated
  * why 2008 has two annual aquatic meets in it. The February report puts the
    aquatic meet inside Khel Mela, on the same day as the track and field
    events, and calls the whole thing the 12th Annual Athletic and Aquatic
    Meet; the October-November issue then reports "the school Annual Inter
    House Aquatic Meet 2008" on 23-24 November as its own event. Both are
    published here as published. Whether these are two meets, or one meet
    straddling an academic year, or a change of calendar, is the school's to
    say.
  * a complete Khel Mela results sheet for any year. A photographed
    2025-2026 ribbon names the 29th Annual Aquatic Meet; the placings for it
    are not in this repository.
"""

# ---------------------------------------------------------------------------
# The houses, in the order the school lists them on the page: the order they
# are introduced in. Each entry is everything sourced about one house.
#
#   slug        the anchor and the CSS token suffix
#   name        spelling printed in the supplied kit photo or Sakshi heading
#   colour      the colour word, which is always shown beside the name so the
#               page never identifies a house by colour alone
#   number      01..04, the order on this page and nothing more
#   symbol      the animal, from Sakshi, February 2008
#   says        that house's own words, February 2008, quoted
#   fact        a factual line, each traceable to the sources above
#   hero        the portrait in the opening frame
#   hero_alt    what is in that frame
#   frame       the chapter's wide photograph
#   frame_alt   what is in that frame
# ---------------------------------------------------------------------------
HOUSES = [
    {
        "slug": "vasishtha",
        "name": "Vasishtha",
        "colour": "Red",
        "number": "01",
        "symbol": "The lion",
        "says": "Just like the lion, our house symbolizes strength and "
                "determination, never giving up and a readiness to break new "
                "challenges.",
        "fact": "Vasishtha was the first house to pass a thousand points in the "
                "school&rsquo;s history, and in February 2008 it described itself as the "
                "unbeaten champion of the march past. Its drills have used pompoms and "
                "poles, and before those, pyramids, umbrellas and leziums.",
        "hero": "hero-vasishtha.jpg",
        "hero_cap": "The house jersey, on the outdoor court",
        "hero_alt": "A CIRS student in a deep red house jersey printed Vasishtha, "
                    "playing on the outdoor basketball court",
        "frame": "ch-vasishtha.jpg",
        "frame_cap": "A team activity in red CIRS shirts",
        "frame_alt": "A group of students in red CIRS shirts standing round "
                     "a large numbered grid chalked on the floor, holding coloured ribbons",
    },
    {
        "slug": "valmiki",
        "name": "Valmiki",
        "colour": "Yellow",
        "number": "02",
        "symbol": "The tiger",
        "says": "We perceive the goal through our all-seeing eye; that of a tiger, "
                "and we hope to continue our remarkable tradition of victory.",
        "fact": "Valmiki took both the overall championship and the best march past at "
                "Khel Mela 2008, and won the Senior Social Science Quiz in April that "
                "year. Its Khel Mela drill that season was a dupatta and cap drill.",
        "hero": "hero-valmiki.jpg",
        "hero_cap": "The house sash, at an investiture",
        "hero_alt": "Students at a CIRS investiture ceremony wearing yellow Valmiki "
                    "house sashes, right hands raised in the pledge",
        "frame": "ch-valmiki.jpg",
        "frame_cap": "On the ball at a CIRS football match",
        "frame_alt": "A player in an amber CIRS shirt on the ball during a "
                     "inter-house football match on the CIRS ground",
    },
    {
        "slug": "vishwamitra",
        "name": "Vishwamitra",
        "colour": "Green",
        "number": "03",
        "symbol": "The eagle",
        "says": "A fierce and elegant eagle, soaring through cloudy night skies and "
                "bright days, soaring through life.",
        "fact": "The eagle has been Vishwamitra&rsquo;s symbol since 2005. The house "
                "won the Inter-House Aquatic Meet and the junior English quiz in the "
                "second term of 2008, and brought the fight drill &mdash; two armies, "
                "staged as a series of exercises &mdash; to Khel Mela for the first time.",
        "hero": "hero-vishwamitra.jpg",
        "hero_cap": "The house tee, at a classroom contest",
        "hero_alt": "A CIRS student in a green shirt working "
                    "at a desk during a classroom activity",
        "frame": "ch-vishwamitra.jpg",
        "frame_cap": "Covering across at a CIRS football match",
        "frame_alt": "A player in a green CIRS shirt covering across the "
                     "ground during an inter-house football match",
    },
    {
        "slug": "vyasa",
        "name": "Vyasa",
        "colour": "Blue",
        "number": "04",
        "symbol": "The dragon",
        "says": "Winning is difficult, but not impossible, and this is the hope that "
                "keeps us striving for the impossible.",
        "fact": "Vyasa took the best drill cup at Khel Mela 2008 with a drill of hoops and "
                "a bamboo dance, and it won the Junior Science Quiz that November.",
        "hero": "hero-vyasa.jpg",
        "hero_cap": "The house shirt, waiting to return",
        "hero_alt": "A CIRS student in a blue house shirt printed Vyasa, waiting to "
                    "return at a tennis session",
        "frame": "ch-vyasa.jpg",
        "frame_cap": "The juniors at work, in house colours",
        "frame_alt": "Junior students in blue Vyasa house tees laying out Tamil letter "
                     "cards on the floor of the hall",
    },
]

# ---------------------------------------------------------------------------
# The inter-house record, as the school published it.
#
# Each row is one dated event from the available school material. Where the
# source gives placements or named awards, those are reproduced. Nothing is
# aggregated into a championship table: these sources do not include a
# complete points total, and a total made from selected results would be
# presented as something the school did not publish here.
#
#   when      the date as the source gives it, no more precisely
#   event     the event's own name
#   category  the strip the competition track groups it under
#   order     the four houses, first to fourth, by slug
#   awards    (award, [slugs]) where the event was judged, not ranked
#   source    which file in pdf/ this row is read from
# ---------------------------------------------------------------------------
RESULTS = [
    {
        # The report names it "our 12th Annual Athletic and Aquatic Meet", and
        # describes the aquatic meet running inside Khel Mela on the same day
        # as the track and field events. The preview in the February issue
        # calls the same event the 12th Annual Athletic Meet; the report's
        # fuller name is the one used here.
        "when": "February 2008",
        "event": "Khel Mela &mdash; the 12th Annual Athletic and Aquatic Meet",
        "category": "Sport",
        "order": None,
        "awards": [("Overall championship", ["valmiki"]),
                   ("Best march past", ["valmiki"]),
                   ("Best individual activities", ["vasishtha", "vishwamitra"]),
                   ("Best drill", ["vyasa"])],
        "source": "Sakshi, March 2008",
        # The source disagrees with itself here, and the page says so rather
        # than choosing quietly. Its list of winners reads "Best Drill - Vyasa
        # House"; three paragraphs earlier its own account of the drill
        # competition says the cup went to "these houses (Vasishtha and Vyasa
        # house)". The list is what is reproduced above, because it is the
        # formal list of winners — but a reader is entitled to know the issue
        # printed both.
        "note": "The same issue reports the best drill cup two ways: its list of winners "
                "names Vyasa alone, while its account of the drill competition says the "
                "cup went to Vasishtha and Vyasa together. The list is what is shown here.",
    },
    {
        "when": "30 April 2008",
        "event": "Senior Social Science Quiz",
        "category": "Quizzing",
        "order": ["valmiki", "vasishtha", "vyasa", "vishwamitra"],
        "awards": None,
        "source": "Sakshi, summer special, May 2008",
    },
    {
        "when": "May 2008",
        "event": "The house symposiums",
        "category": "Culture",
        "order": None,
        "awards": None,
        "source": "Sakshi, summer special, May 2008",
        "note": "Four productions, one from each house, and the only house event in "
                "these sources that was staged rather than scored. The titles are "
                "under <a href=\"#culture\">Where each house tells a story</a>.",
    },
    {
        "when": "22 October 2008",
        "event": "English Quiz, junior school",
        "category": "Quizzing",
        "order": ["vishwamitra", "valmiki", "vyasa", "vasishtha"],
        "awards": None,
        "source": "CIRS e-newsletter, October&ndash;November 2008",
        "note": "Vishwamitra and Valmiki tied, and three further rounds were needed "
                "to separate them.",
    },
    {
        "when": "5 November 2008",
        "event": "Mathematics Quiz, junior school",
        "category": "Quizzing",
        "order": ["vasishtha", "vishwamitra", "vyasa", "valmiki"],
        "awards": None,
        "source": "CIRS e-newsletter, October&ndash;November 2008",
    },
    {
        "when": "19 November 2008",
        "event": "Junior Science Quiz",
        "category": "Quizzing",
        "order": ["vyasa", "valmiki", "vishwamitra", "vasishtha"],
        "awards": None,
        "source": "CIRS e-newsletter, October&ndash;November 2008",
    },
    {
        "when": "23&ndash;24 November 2008",
        "event": "Inter-House Aquatic Meet",
        "category": "Sport",
        "order": ["vishwamitra", "valmiki", "vyasa", "vasishtha"],
        "awards": None,
        "source": "CIRS e-newsletter, October&ndash;November 2008",
    },
    {
        "when": "2025&ndash;2026",
        "event": "Khel Mela &mdash; the 29th Annual Aquatic Meet",
        "category": "Sport",
        "order": None,
        "awards": None,
        "source": "the meet&rsquo;s own medal ribbons",
        "note": "A photographed ribbon names this as the 29th Annual Aquatic Meet; "
                "this repository does not contain its house placings.",
    },
]

# The four house productions of May 2008, with their titles as Sakshi printed
# them and the school's own one-line account of each. The culture chapter is
# built from this. No other production is named anywhere in this repository,
# and none is added here.
SYMPOSIUMS = [
    ("valmiki", "The Twilight of the Gods",
     "How past lives and experiences can shape us as individuals."),
    ("vasishtha", "The Butterfly Effect",
     "In life we do not usually get second chances, so we should make the best of "
     "the only opportunity we get."),
    ("vishwamitra", "V for Vendetta",
     "Nothing in life is trivial enough to be underestimated."),
    ("vyasa", "The Breakthrough",
     "When power and money are at stake, people forget more important relationships."),
]

# The competition categories the sources actually support, and nothing beyond
# them. Debates, arts, service and academic contests happen at CIRS and are on
# other pages of this site, but no source here places the four houses in one,
# so they are not offered as filters.
CATEGORIES = ["All", "Sport", "Quizzing", "Culture"]

DIR = "assets/img/houses"


def by_slug():
    return {h["slug"]: h for h in HOUSES}


def name_of(slug):
    return by_slug()[slug]["name"]


def colour_of(slug):
    return by_slug()[slug]["colour"]


def img(name):
    return f"{DIR}/{name}"
