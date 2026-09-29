#!/usr/bin/env python3
"""Our Laurels: every honour on the page, where it came from, and the page.

Nothing here is new information. Each laurel is copied from a record this
site already publishes, and names that record in "source":

    competitions.html        the school's own roundup of the 2025 inter-school
                             results, published 1 October 2025
                             (tools/newsarticles.py, slug "competitions")
    news.html#…-results-2026 the school's results briefs for 2026
    school-history.html      tools/history.py, where every dated record
                             carries its own source
    houses.html#record       tools/houses.py RESULTS: the 2008 inter-house
                             results as the school's newsletters printed them
    why-cirs.html            the Green School Award (the year is not given)

Names are spelled as the school printed them. A name the source gives as a
first name only stays in the laurel's text but is left out of the roll of
names. Two spellings that are probably one student are never merged here:
that is the school's call, not this file's.

Photographs are the school's own. None is presented as a picture of the
competition it sits beside unless it is one: IMAGES captions describe the
frame, and "event" is True only for the few that show the honour itself.

To add a laurel, add a record to LAURELS with its source and rebuild. The
archive, its filters, the timeline and the roll of names are all built from
that list. HELD lists what was left out and why; `python3 tools/laurels.py`
prints it.
"""

import html
import json
import re

# ---------------------------------------------------------------------------
# Photographs. key -> (path, width, height, alt, caption, event)
# ---------------------------------------------------------------------------
IMAGES = {
    "ib-lab": ("assets/img/results-ib-lab.webp", 1800, 1200,
               "A CIRS student looking into a microscope in a biology laboratory",
               "A biology practical at CIRS", False),
    "cbse-lab": ("assets/img/results-cbse-lab.webp", 1800, 1200,
                 "A teacher demonstrating apparatus to students gathered round a laboratory bench",
                 "A physics demonstration at CIRS", False),
    "yoga": ("assets/img/sports-experience/yoga-group-wide.webp", 1920, 1200,
             "CIRS students in blue tracksuits holding a standing yoga pose on the school ground, "
             "hills behind them",
             "Yoga on the CIRS ground, beneath the Siruvani hills", False),
    "football": ("assets/img/sports/sport-football.jpg", 1600, 1200,
                 "Young CIRS footballers in green and amber shirts chasing the ball on the school field",
                 "Football on the CIRS field", False),
    "basketball": ("assets/img/sports-experience/basketball-game-wide.webp", 1920, 1200,
                   "Players leaping for a rebound under the basket on the CIRS outdoor court",
                   "A rebound on the CIRS outdoor court", False),
    "quiz": ("assets/img/houses/comp-quiz.jpg", 1400, 788,
             "CIRS students discussing a quiz answer at a table, one student holding a microphone",
             "A quiz in progress at CIRS", False),
    "mun": ("assets/img/hrun/03-mun.jpg", 1500, 1000,
            "Students in suits gathered with a flag at a CIRS Model United Nations",
            "Delegates at a Model United Nations held at CIRS", False),
    "band": ("assets/img/arts/band.jpg", 1600, 1194,
             "The CIRS student band performing outdoors in uniform",
             "The CIRS band", False),
    "tabla": ("assets/img/arts/tabla.jpg", 1600, 1194,
              "CIRS students seated on a carpet at tabla, their teacher beside them",
              "A tabla class at CIRS", False),
    "ensemble": ("assets/img/arts/ensemble.jpg", 1600, 1194,
                 "A row of dancers in costume raising their arms on a stage lit in violet",
                 "A dance ensemble on the CIRS stage", False),
    "collage": ("assets/img/news/competitions-1200.webp", 1200, 620,
                "A collage of CIRS students receiving certificates and trophies, and CIRS teams "
                "posing with their awards",
                "From the school&rsquo;s own report of the 2025 competitions", True),
    "vision": ("assets/img/history/vision-2012-lg.jpg", 1400, 933,
               "A trophy inscribed Central Chinmaya Mission Trust Education Cell Vision Award 2012, "
               "held up with its certificate by a woman in a sari and a swami in saffron",
               "The Vision Award and its certificate at the presentation. The people pictured are "
               "not named in the school&rsquo;s record", True),
    "brainfeed": ("assets/img/history/brainfeed-2017-lg.jpg", 1400, 1746,
                  "A wooden plaque with a gold panel reading brainfeed school excellence awards, "
                  "Top 500 Schools of India 2017-18",
                  "The plaque, dated 12 November 2017, Bengaluru", True),
    "kalam": ("assets/img/history/kalam-2007-sm.jpg", 640, 921,
              "The first typed page of the school's account of its students' meeting with "
              "President A. P. J. Abdul Kalam",
              "The first page of the school&rsquo;s account of the meeting", True),
    "sakshi": ("assets/img/history/sakshi-2008-sm.jpg", 640, 871,
               "The cover of the Chinmaya Sakshi e-newsletter, summer special, May 2008",
               "<i>Chinmaya Sakshi</i>, May 2008: the newsletter that printed the year&rsquo;s house "
               "results", True),
    "isa": ("assets/img/history/isa-2010-sm.jpg", 640, 943,
            "The first page of the CIRS Junior School holiday assignment, December 2010, "
            "explaining the International School Award",
            "The December 2010 assignment set for the International School Award programme",
            True),
    "report": ("assets/img/history/report-2019-sm.jpg", 640, 940,
               "The first page of the CIRS Annual Report dated 15 October 2019",
               "Annual Report, 15 October 2019, which records the survey", True),
    "forest": ("assets/img/forest-air.jpg", 1600, 900,
               "The CIRS campus from the air, the forest closing around it on every side",
               "The campus from the air, most of its hundred acres left to native growth", False),
    "track": ("assets/img/sports/hero-track.jpg", 2400, 1500,
              "Runners rounding the CIRS athletics track, flags and palms behind them",
              "The CIRS athletics track", False),
    "academic": ("assets/img/life-split-academic.jpg", 1800, 1200,
                 "CIRS students at their desks during an examination, one looking up",
                 "An examination hall at CIRS", False),
    "expo": ("assets/img/news/science-expo-1200.webp", 1200, 620,
             "A CIRS student explaining a science exhibit to a visitor at the Science Expo",
             "The Science Expo, 25 July 2025", True),
    "elections": ("assets/img/news/class-representative-elections-1200.webp", 1200, 620,
                  "A CIRS student writing at a desk during the class representative elections, an "
                  "NCC cadet beside her",
                  "Class Representative Elections, 25 April 2025", True),
    "seva": ("assets/img/news/seva-week-1200.webp", 1200, 620,
             "CIRS students handing supplies to a member of the community during Seva Week",
             "Seva Week, April 2025", True),
}

# ---------------------------------------------------------------------------
# Categories and levels. The key is what the filters and each record carry.
# Innovation is not offered: no laurel in hand is for it (see HELD).
# ---------------------------------------------------------------------------
CATEGORIES = [
    ("academics", "Academics"),
    ("sport", "Sport"),
    ("arts", "Arts"),
    ("speech", "Speech"),
    ("leadership", "Leadership"),
    ("international", "International"),
    ("school", "The School"),
]
CAT_NAME = dict(CATEGORIES)

LEVELS = [
    ("inter-house", "Inter-house"),
    ("inter-school", "Inter-school"),
    ("zonal", "Zonal"),
    ("national", "National"),
    ("international", "International"),
]
LEVEL_NAME = dict(LEVELS)

ROUNDUP = ("Competitions across CIRS, the school&rsquo;s report of 1 October 2025",
           "competitions.html")
IB_BRIEF = ("The school&rsquo;s IB results brief", "news.html#ib-results-2026")
CBSE_BRIEF = ("The school&rsquo;s CBSE results brief", "news.html#cbse-results-2026")


def history(record, label):
    return (f"School History: {label}", f"school-history.html#record-{record}")


SAKSHI_MAR = ("<i>Sakshi</i>, March 2008, on the Houses record", "houses.html#record")
SAKSHI_MAY = ("<i>Sakshi</i>, summer special, May 2008, on the Houses record",
              "houses.html#record")
ENEWS_2008 = ("CIRS e-newsletter, October&ndash;November 2008, on the Houses record",
              "houses.html#record")

# ---------------------------------------------------------------------------
# The laurels, newest first.
#
#   when     the date as the source gives it
#   title    the honour, in a line
#   event    the competition or body, and where
#   result   the placing or outcome, short
#   text     the record in full (the source's facts, re-set as prose)
#   names    (name, what for) for the roll of names: full names only
#   weight   feature | wide | tall | small | text — the archive tile's shape
#   figure   a short typographic mark for text-led tiles
# ---------------------------------------------------------------------------
LAURELS = [
    # ---- 2026 ------------------------------------------------------------
    {"id": "ib-2026", "year": 2026, "when": "May 2026",
     "cats": ["academics", "international"], "level": "international",
     "title": "Twenty-four diplomas from twenty-four candidates",
     "event": "IB Diploma Programme, May 2026 examination",
     "result": "24 of 24 diplomas &middot; two scores of 45 out of 45",
     "text": "Every candidate registered for the May 2026 IB Diploma examination was awarded "
             "the diploma, with an average of 39.4 points. Twelve scored 40 or above. Adithyan "
             "Diwakar Vidya and Shriya Shruti Misra both scored 45 out of 45, the maximum the "
             "Diploma allows.",
     "names": [("Adithyan Diwakar Vidya", "45 out of 45 in the IB Diploma"),
               ("Shriya Shruti Misra", "45 out of 45 in the IB Diploma")],
     "source": IB_BRIEF, "image": "ib-lab", "weight": "feature", "figure": "24/24"},
    {"id": "cbse-xii-management-2026", "year": 2026, "when": "March&ndash;April 2026",
     "cats": ["academics"], "level": "national",
     "title": "99.0 per cent in Class XII Management",
     "event": "CBSE Class XII board examinations",
     "result": "Stream topper, 99.0%",
     "text": "Dhruvik Sachin Agarwal topped the Class XII Management stream with 99.0%. The "
             "stream averaged 94%; 22 students scored 90% or above, and there was one centum in "
             "Business Studies and two in Applied Mathematics.",
     "names": [("Dhruvik Sachin Agarwal", "99.0% in Class XII Management")],
     "source": CBSE_BRIEF, "image": None, "weight": "text", "figure": "99.0"},
    {"id": "cbse-xii-science-2026", "year": 2026, "when": "March&ndash;April 2026",
     "cats": ["academics"], "level": "national",
     "title": "Joint toppers in Class XII Science",
     "event": "CBSE Class XII board examinations",
     "result": "Two toppers, 95.60% each",
     "text": "Sonakshi Birmiwal and Namburu Venkata Dheeraj topped the Class XII Science stream "
             "with 95.60% each. The class averaged 91%, twelve students scored 90% or above, "
             "and there was one centum in Chemistry and two in IP.",
     "names": [("Sonakshi Birmiwal", "95.60% in Class XII Science"),
               ("Namburu Venkata Dheeraj", "95.60% in Class XII Science")],
     "source": CBSE_BRIEF, "image": "cbse-lab", "weight": "small"},
    {"id": "cbse-x-2026", "year": 2026, "when": "March&ndash;April 2026",
     "cats": ["academics"], "level": "national",
     "title": "98.60 per cent in Class X",
     "event": "CBSE Class X board examinations",
     "result": "Class topper, 98.60%",
     "text": "Vishv Prem Nangia topped Class X with 98.60%. Forty-nine students scored 90% or "
             "above, and centums were recorded in Sanskrit (five), Hindi (two) and French "
             "(three).",
     "names": [("Vishv Prem Nangia", "98.60% in Class X")],
     "source": CBSE_BRIEF, "image": None, "weight": "text", "figure": "98.60"},

    # ---- 2025 ------------------------------------------------------------
    {"id": "quzbiz-2025", "year": 2025, "when": "29 August 2025",
     "cats": ["academics"], "level": "zonal",
     "title": "Winners of the QUZBIZ Zonal Quiz",
     "event": "QUZBIZ Zonal Quiz, Yuva Bharati School, Coimbatore",
     "result": "First of 180 teams &middot; through to the State-level quiz",
     "text": "Two CIRS teams entered the zonal round of QUZBIZ. Out of 180 teams, Adithyan "
             "Diwakar and Heril Goti reached the final, led throughout and won, taking "
             "certificates, a cash prize of &#8377;10,000 and a place in the State-level quiz "
             "in Chennai.",
     "names": [("Adithyan Diwakar &amp; Heril Goti", "QUZBIZ Zonal Quiz, first of 180 teams")],
     "source": ROUNDUP, "image": "quiz", "weight": "wide"},
    {"id": "hindu-quiz-2025", "year": 2025, "when": "22 August 2025",
     "cats": ["academics"], "level": "inter-school",
     "title": "Senior champions at The Hindu In School Quiz",
     "event": "The Hindu In School Quiz, NGP College, Coimbatore",
     "result": "Senior 1st and 3rd &middot; junior 2nd",
     "text": "Five CIRS teams took part among 2,000. In the senior category Adithyan and Heril "
             "were champions and Vishv Prem and Swarit placed third; in the junior category "
             "Devansh and Pradyuth came second. Govardhan and Hridit, Arnav and Jashit, and "
             "Viraj and Divyam were singled out for recognition.",
     "names": [],
     "source": ROUNDUP, "image": None, "weight": "text", "figure": "1st"},
    {"id": "lotus-quiz-2025", "year": 2025, "when": "20 August 2025",
     "cats": ["academics"], "level": "inter-school",
     "title": "First prize at the Lotus Quiz",
     "event": "Lotus Quiz, Satchidananda Jothi Niketan International School, Mettupalayam",
     "result": "First of 40 teams",
     "text": "Devansh Mazumdar and Pradyuth Senthilkumar won the Lotus Quiz against forty "
             "teams, and were given certificates, trophies and a cash prize of &#8377;5,000.",
     "names": [("Devansh Mazumdar &amp; Pradyuth Senthilkumar", "Lotus Quiz, first of 40 teams")],
     "source": ROUNDUP, "image": None, "weight": "text", "figure": "1 / 40"},
    {"id": "aqmen-2025", "year": 2025, "when": "5 August 2025",
     "cats": ["academics"], "level": "inter-school",
     "title": "Third at the AQMEN Quiz",
     "event": "AQMEN Quiz, PSBB Millennium School, Coimbatore",
     "result": "Third of 55 teams",
     "text": "The Quiz Club&rsquo;s junior team, Devansh Mazumdar of Grade 8 and Arnav Anand of "
             "Grade 7, placed third among 55 teams from schools across Coimbatore in a quiz set "
             "by Prof. Rangarajan, winning certificates and &#8377;1,000.",
     "names": [("Devansh Mazumdar &amp; Arnav Anand", "AQMEN Quiz, third of 55 teams")],
     "source": ROUNDUP, "image": None, "weight": "small"},
    {"id": "yoga-2025", "year": 2025, "when": "13 July 2025",
     "cats": ["sport"], "level": "zonal",
     "title": "Overall champions, South Zone Yoga",
     "event": "South Zone Yoga Competition 2025&ndash;26, School Games Sport Development "
              "Foundation India, Erode",
     "result": "Overall Championship &middot; 6 gold, 5 silver, 6 bronze",
     "text": "Across every category, CIRS students brought home six gold, five silver and six "
             "bronze medals, and with them the Overall Championship.",
     "names": [],
     "source": ROUNDUP, "image": "yoga", "weight": "feature", "figure": "17"},
    {"id": "football-u14-2025", "year": 2025, "when": "2025",
     "cats": ["sport"], "level": "inter-school",
     "title": "Under-14 champions, eleven-a-side",
     "event": "11-on-11 Football Tournament, Chandrakanthi Public School, Coimbatore",
     "result": "Champions of 36 schools &middot; Best Player",
     "text": "The CIRS Under-14 boys won the eleven-a-side tournament against 36 schools, and "
             "Tanay Lakshman of Grade 8 was named Best Player.",
     "names": [("Tanay Lakshman", "Best Player, Under-14 football")],
     "source": ROUNDUP, "image": "football", "weight": "tall"},
    {"id": "takshila-2025", "year": 2025, "when": "28&ndash;29 August 2025",
     "cats": ["sport"], "level": "inter-school",
     "title": "Second runners-up, Under-11 football",
     "event": "Takshila Inter-School 7-on-7 Football Tournament, Delhi Public School, Coimbatore",
     "result": "Second runners-up &middot; Best Defender",
     "text": "The Under-11 boys finished as second runners-up, and Arnav Ramoliya of Grade 5 "
             "was given the Best Defender Award.",
     "names": [("Arnav Ramoliya", "Best Defender, Under-11 football")],
     "source": ROUNDUP, "image": None, "weight": "small"},
    {"id": "kpr-basketball-2025", "year": 2025, "when": "9&ndash;10 August 2025",
     "cats": ["sport"], "level": "inter-school",
     "title": "Third place, both Under-19 teams",
     "event": "KPR Basketball Tournament 2025, KPR Engineering College, Coimbatore",
     "result": "Boys 3rd &middot; girls 3rd",
     "text": "With twenty teams from four districts competing, the CIRS Under-19 boys and "
             "Under-19 girls both finished third.",
     "names": [],
     "source": ROUNDUP, "image": "basketball", "weight": "wide"},
    {"id": "sahodaya-basketball-2025", "year": 2025, "when": "24&ndash;25 July 2025",
     "cats": ["sport"], "level": "inter-school",
     "title": "Runners-up, Under-16 girls",
     "event": "Coimbatore Sahodaya Basketball Tournament 2025, SNS CBSE School",
     "result": "Runners-up of 22 teams",
     "text": "The Under-16 girls reached the final of a 22-team category and finished as "
             "runners-up.",
     "names": [],
     "source": ROUNDUP, "image": None, "weight": "text", "figure": "2nd"},
    {"id": "bhajan-2025", "year": 2025, "when": "26 July 2025",
     "cats": ["arts"], "level": "inter-school",
     "title": "First prize for bhajan",
     "event": "Interschool Bhajan Competition, Suguna International School",
     "result": "First of more than 20 schools",
     "text": "Ten CIRS students from Grades 7 to 12 sang for the school and took first prize "
             "among more than twenty schools.",
     "names": [],
     "source": ROUNDUP, "image": "tabla", "weight": "tall"},
    {"id": "instrumental-2025", "year": 2025, "when": "26 August 2025",
     "cats": ["arts"], "level": "inter-school",
     "title": "First in Wind, second in Rhythm",
     "event": "46th Sahodaya Inter School Instrumental Music Competition, CS Academy, Coimbatore",
     "result": "Wind 1st &middot; Rhythm 2nd &middot; 41 schools",
     "text": "Thirteen students represented CIRS across four categories: Wind, Rhythm, Keyboard "
             "and Band. Among 41 schools, Yuvraj Tibrewal of Class 9 placed first in Wind and "
             "Arham Jain of Class 9 second in Rhythm.",
     "names": [("Yuvraj Tibrewal", "First in Wind, Sahodaya instrumental music"),
               ("Arham Jain", "Second in Rhythm, Sahodaya instrumental music")],
     "source": ROUNDUP, "image": "band", "weight": "wide"},
    {"id": "dance-2025", "year": 2025, "when": "16 August 2025",
     "cats": ["arts"], "level": "inter-school",
     "title": "Third place, Under-19 girls&rsquo; dance",
     "event": "Interschool Sahodaya Dance Competition, Benglen Public School",
     "result": "Third of 25 schools",
     "text": "CIRS entered three groups: Under-14 girls, Under-19 boys and Under-19 girls. Among "
             "25 schools, the Under-19 girls placed third.",
     "names": [],
     "source": ROUNDUP, "image": "ensemble", "weight": "small"},
    {"id": "public-speaking-2025", "year": 2025, "when": "23 August 2025",
     "cats": ["speech"], "level": "inter-school",
     "title": "First place in public speaking",
     "event": "Public speaking competition, Vidhya Niketan School (CBSE), Vilanankurichi",
     "result": "First place",
     "text": "Pradyum Tibarewal of Grade 12 took first place.",
     "names": [("Pradyum Tibarewal", "First in public speaking; second in declamation")],
     "source": ROUNDUP, "image": "mun", "weight": "wide"},
    {"id": "declamation-2025", "year": 2025, "when": "9 August 2025",
     "cats": ["speech"], "level": "inter-school",
     "title": "Three places in English declamation",
     "event": "English Declamation Competition, The United Public School, Periyanaickenpalayam",
     "result": "Two seconds and a third",
     "text": "Saptarshi Pal of Grade 8 placed second, Adhyatma Ghranthik Agarwal of Grade 10 "
             "third, and Pradyum Tibarewal of Grade 12 second.",
     "names": [("Saptarshi Pal", "Second in English declamation"),
               ("Adhyatma Ghranthik Agarwal", "Third in English declamation")],
     "source": ROUNDUP, "image": None, "weight": "text", "figure": "2 &middot; 3 &middot; 2"},
    {"id": "storytelling-2025", "year": 2025, "when": "2025",
     "cats": ["speech"], "level": "inter-school",
     "title": "Second and fourth in storytelling",
     "event": "46th CBSE Sahodaya Inter-school Storytelling Competition, Aksharam International "
              "School",
     "result": "Category D 2nd &middot; category C 4th",
     "text": "Aashi Kedia of Grade 10 won second place in category D, and Anokhi Kankani of "
             "Grade 8 fourth place in category C.",
     "names": [("Aashi Kedia", "Second in Sahodaya storytelling"),
               ("Anokhi Kankani", "Fourth in Sahodaya storytelling")],
     "source": ROUNDUP, "image": None, "weight": "small"},
    {"id": "extempore-2025", "year": 2025, "when": "2025",
     "cats": ["speech"], "level": "inter-school",
     "title": "Second place in English extempore",
     "event": "English Extempore Competition, CMC International School, Coimbatore",
     "result": "Category B, second",
     "text": "Amayra Goel of Grade 8 took second place in category B.",
     "names": [("Amayra Goel", "Second in English extempore")],
     "source": ROUNDUP, "image": None, "weight": "small"},
    {"id": "spell-bee-2025", "year": 2025, "when": "2025",
     "cats": ["speech"], "level": "inter-school",
     "title": "Laurels at the Sahodaya Spell Bee",
     "event": "46th CBSE Sahodaya English Spell Bee, Anugraha Mandhir CBSE Senior Secondary "
              "School, Coimbatore",
     "result": "[Placings to be supplied by the school]",
     "text": "The school&rsquo;s report says CIRS students brought laurels from this Spell Bee. "
             "[The students&rsquo; names and placings are not in the published report and are "
             "to be supplied by the school.]",
     "names": [],
     "source": ROUNDUP, "image": None, "weight": "small", "pending": True},

    # ---- 2019 ------------------------------------------------------------
    {"id": "ranking-2019", "year": 2019, "when": "2019",
     "cats": ["school"], "level": "national",
     "title": "Second in India, first in Tamil Nadu",
     "event": "Education World school survey, conducted by C fore",
     "result": "2nd co-educational boarding school in India &middot; 1st in Tamil Nadu, "
               "eighth year running",
     "text": "In Education World&rsquo;s 2019 survey CIRS rose from fourth to second place in "
             "the country among co-educational boarding schools, and kept first place in "
             "Tamil Nadu for the eighth consecutive year.",
     "names": [],
     "source": history("ranking-2019", "Education World survey"),
     "image": "report", "weight": "tall"},
    {"id": "lead-school-2019", "year": 2019, "when": "2019",
     "cats": ["leadership", "school"], "level": "national",
     "title": "A CBSE Lead School",
     "event": "Central Board of Secondary Education",
     "result": "Selected to guide five CBSE schools",
     "text": "The CBSE selected CIRS as one of its Lead Schools, to guide five other CBSE "
             "schools.",
     "names": [],
     "source": history("report-2019", "the Annual Report, 15 October 2019"),
     "image": None, "weight": "text", "figure": "5"},
    {"id": "cbse-2019", "year": 2019, "when": "2019",
     "cats": ["academics"], "level": "national",
     "title": "Every candidate above 80 per cent",
     "event": "CBSE Class XII board examinations",
     "result": "45 of 45 above 80% &middot; 41 above 90%",
     "text": "All 45 students who sat the Class XII examination scored above 80% in aggregate, "
             "and 41 of them above 90%. Science averaged 92.06% and Management 94.23%.",
     "names": [],
     "source": history("cbse-2019", "Class XII results, 2019"),
     "image": "academic", "weight": "small"},

    # ---- 2017 ------------------------------------------------------------
    {"id": "brainfeed-2017", "year": 2017, "when": "12 November 2017",
     "cats": ["school"], "level": "national",
     "title": "Top 500 Schools of India",
     "event": "Brainfeed School Excellence Awards 2017&ndash;18, Bengaluru",
     "result": "Named among the Top 500 Schools of India",
     "text": "Brainfeed&rsquo;s School Excellence Awards named CIRS among the Top 500 Schools of "
             "India 2017&ndash;18, in the category Best International Boarding / Happiness "
             "Quotient Index / Influential School Brand, and among the best international "
             "schools of Tamil Nadu.",
     "names": [],
     "source": history("brainfeed-2017", "Brainfeed Top 500 Schools of India"),
     "image": "brainfeed", "weight": "tall"},

    # ---- 2012 ------------------------------------------------------------
    {"id": "vision-award-2012", "year": 2012, "when": "2012",
     "cats": ["school"], "level": None,
     "title": "The CCMT Education Cell Vision Award",
     "event": "Education Cell, Central Chinmaya Mission Trust",
     "result": "Vision Award for 2012",
     "text": "The Education Cell of the Central Chinmaya Mission Trust presented its Vision "
             "Award for 2012 to CIRS, Coimbatore.",
     "names": [],
     "source": history("vision-award-2012", "The CCMT Education Cell Vision Award"),
     "image": "vision", "weight": "feature"},

    # ---- 2011 ------------------------------------------------------------
    {"id": "isa-2011", "year": 2011, "when": "2011",
     "cats": ["international", "school"], "level": "international",
     "title": "The International School Award",
     "event": "British Council",
     "result": "International School Award",
     "text": "CIRS received the British Council&rsquo;s International School Award, which "
             "recognises good practice in bringing an international dimension into the "
             "curriculum. The Junior School had taken up the programme the year before, with "
             "holiday assignments on the wider world.",
     "names": [],
     "source": history("isa-award-2011", "The International School Award"),
     "image": "isa", "weight": "small"},

    # ---- 2008 ------------------------------------------------------------
    {"id": "khel-mela-2008", "year": 2008, "when": "February 2008",
     "cats": ["sport"], "level": "inter-house",
     "title": "Valmiki take the Khel Mela",
     "event": "Khel Mela, the 12th Annual Athletic and Aquatic Meet",
     "result": "Overall championship and best march past: Valmiki",
     "text": "Valmiki won the overall championship and the best march past. Vasishta and "
             "Vishwamitra shared the award for best individual activities, and the list of "
             "winners gives the best drill to Vyasa (the same issue&rsquo;s account of the "
             "drill says the cup went to Vasishta and Vyasa together).",
     "names": [("Valmiki", "Khel Mela: overall championship and best march past"),
               ("Vasishta", "Khel Mela: best individual activities, shared"),
               ("Vishwamitra", "Khel Mela: best individual activities, shared"),
               ("Vyasa", "Khel Mela: best drill")],
     "source": SAKSHI_MAR, "image": "sakshi", "weight": "wide", "house": True},
    {"id": "aquatic-2008", "year": 2008, "when": "23&ndash;24 November 2008",
     "cats": ["sport"], "level": "inter-house",
     "title": "Vishwamitra win the Aquatic Meet",
     "event": "Inter-House Aquatic Meet",
     "result": "Vishwamitra first, Valmiki second",
     "text": "Vishwamitra won the Inter-House Aquatic Meet, ahead of Valmiki, Vyasa and "
             "Vasishta.",
     "names": [("Vishwamitra", "Inter-House Aquatic Meet")],
     "source": ENEWS_2008, "image": None, "weight": "text", "figure": "1st", "house": True},
    {"id": "quizzes-2008", "year": 2008, "when": "April&ndash;November 2008",
     "cats": ["academics"], "level": "inter-house",
     "title": "Four quizzes, four winners",
     "event": "Inter-house quizzes, senior and junior school",
     "result": "Valmiki, Vishwamitra, Vasishta and Vyasa each win one",
     "text": "Valmiki won the Senior Social Science Quiz on 30 April. In the junior school, "
             "Vishwamitra won the English Quiz on 22 October after three tie-break rounds "
             "against Valmiki, Vasishta the Mathematics Quiz on 5 November, and Vyasa the "
             "Science Quiz on 19 November.",
     "names": [("Valmiki", "Senior Social Science Quiz"),
               ("Vishwamitra", "Junior English Quiz"),
               ("Vasishta", "Junior Mathematics Quiz"),
               ("Vyasa", "Junior Science Quiz")],
     "source": ENEWS_2008, "image": None, "weight": "small", "house": True},

    # ---- 2007 ------------------------------------------------------------
    {"id": "kalam-2007", "year": 2007, "when": "7 May 2007",
     "cats": ["leadership"], "level": "national",
     "title": "Invited to Rashtrapati Bhavan",
     "event": "An interaction with President A.&nbsp;P.&nbsp;J. Abdul Kalam, New Delhi",
     "result": "32 students received by the President",
     "text": "A vacation assignment on the President&rsquo;s &lsquo;Vision for India "
             "2020&rsquo;, recast by the school as &lsquo;My Vision for Myself, my Family, my "
             "School and my Country&rsquo;, led to an invitation: thirty-two students from "
             "Classes VI to XII met President Kalam in the Committee Room of Rashtrapati "
             "Bhavan.",
     "names": [],
     "source": history("kalam-2007", "At Rashtrapati Bhavan"),
     "image": "kalam", "weight": "small"},

    # ---- Undated -----------------------------------------------------------
    {"id": "green-school", "year": None, "when": "[Year to be confirmed by the school]",
     "cats": ["school"], "level": "national",
     "title": "The Green School Award",
     "event": "Centre for Science and Environment, New Delhi",
     "result": "Green School Award",
     "text": "Roughly eighty of the campus&rsquo;s hundred acres have been left to native flora "
             "and fauna. It cost the school land it could have built on, and earned it the "
             "Green School Award from the Centre for Science and Environment, New Delhi.",
     "names": [],
     "source": ("Why CIRS, the school&rsquo;s own account", "why-cirs.html"),
     "image": "forest", "weight": "wide"},
]

BY_ID = {l["id"]: l for l in LAURELS}
assert len(BY_ID) == len(LAURELS), "every laurel needs a unique id"
for _l in LAURELS:
    assert _l["image"] is None or _l["image"] in IMAGES, _l["id"]
    assert all(c in CAT_NAME for c in _l["cats"]), _l["id"]
    assert _l["level"] is None or _l["level"] in LEVEL_NAME, _l["id"]

YEARS = sorted({l["year"] for l in LAURELS if l["year"]}, reverse=True)
FIRST_YEAR, LAST_YEAR = 1996, 2026

# Held back, with the reason. Printed by `python3 tools/laurels.py`.
HELD = [
    ("Ranked 16th IB school worldwide", "On the home ticker; no source or year in hand."),
    ("Among the top 50 CBSE schools in India", "On the home ticker; no source or year."),
    ("IB World Toppers, 45/45, 2019 and 2024", "Held in tools/history.py UNRESOLVED."),
    ("Vayu Nigrah, first prize, SSVM Transforming India Conclave",
     "Prize unconfirmed; the year may be 2024 (tools/history.py UNRESOLVED). This is the "
     "one laurel that would support an Innovation category."),
    ("Spell Bee names", "The 2025 report says students won, but lists no names."),
    ("Green School Award year", "Why CIRS names the award, not the year."),
    ("Photographs of the 2025 inter-school results", "None is in the Drive: its numbered folders "
     "cover the school's own 2026 events. The featured laurels use illustrative school photographs, "
     "captioned for what they show."),
    ("Drive originals over 10 MB", "The connector will not hand over files over 10 MB, so these "
     "folders were not pulled and need the school to export smaller copies: 16 Science Quiz "
     "Juniors, 30 English Quiz, 32 English Jr Quiz, 28 Story telling, 15 Trinity Exam Achievers, "
     "34 HAM, 33 ShishuVatika Poem Rec, 9 Khel Mela, and 31 Spell Bee beyond four frames. "
     "The 'chinmaya olympiad winners' folder is empty."),
    ("Placings for the three competitions in SEASON", "The photographs show the events; no "
     "placing or name is supplied, so none is stated."),
]

# ---------------------------------------------------------------------------
# Competitions in the school's own photographs: "Where the next laurel begins".
#
# These are events, not laurels: the photographs show a competition in
# progress, and the school has not supplied its placings, so none is stated.
# Each date is one the photographs themselves carry: the Spell Bee's is on the
# screen behind the speaker; the others are the phones' own timestamps
# (IMG_20260212_..., IMG_20260227_...) and agree with the school's folder
# titles. No student is named. The Drive connector will not hand over files
# over 10 MB, so only the photographs below were pulled; the Science Quiz,
# English Quiz, Storytelling, Trinity, HAM and Khel Mela folders hold larger
# originals (see HELD). tools/make-laurels.py cuts the images.
#
#   file / id / folder   the original in the school's Drive
#   size                 (large w, h, small w, h) as the tool cuts them
# ---------------------------------------------------------------------------
SEASON_IMG = "assets/img/laurels"
SEASON_PHOTOS = {
    "sb-1": dict(file="CRS00027.JPG", id="1r_9mTWwdPu-WNxdXlvoJ6IPvXUlfdV26", folder="31. Spell Bee",
                 size=(1600, 900, 800, 450),
                 alt="A junior student spelling into a microphone on the stage of the school hall, "
                     "in front of a screen reading Junior Spell Bee Competition, with two judges at "
                     "a red-clothed table and pupils seated on the right",
                 cap="The Junior Spell Bee Competition, 18 August 2026"),
    "sb-2": dict(file="CRS00033.JPG", id="1Yv0QvETnnxENXwuW82S8lj5TF7-B-wwv", folder="31. Spell Bee",
                 size=(1600, 900, 800, 450),
                 alt="A student at the microphone on stage beside the Junior Spell Bee Competition "
                     "screen, the judges at their red table to the left",
                 cap="At the microphone, beside the competition screen"),
    "po-1": dict(file="IMG_20260212_180819.jpg", id="1FZyniPmNz7BtMUjzPI7WIwFYpkWGN0R2",
                 folder="10. LANGUAGE POEM RECITATION", size=(1600, 900, 800, 450),
                 alt="A student in school uniform reciting at a microphone on a tiled terrace, "
                     "tiers of pupils in mustard kurtas seated behind",
                 cap="The Language Poem Recitation, 12 February 2026"),
    "po-2": dict(file="IMG_20260212_180828.jpg", id="1tso6IEljUVZFpsP15NrT6fUncRLJADnn",
                 folder="10. LANGUAGE POEM RECITATION", size=(1600, 900, 800, 450),
                 alt="Two judges seated at a round table making notes, pupils in mustard kurtas on "
                     "tiered steps behind them",
                 cap="The judges&rsquo; table"),
    "po-3": dict(file="IMG_20260212_181121.jpg", id="1oA-yUFkKSJvMGoTX4-JydtvkXbsX0dA0",
                 folder="10. LANGUAGE POEM RECITATION", size=(900, 1600, 450, 800),
                 alt="A girl in school uniform reciting at a microphone stand in front of a "
                     "wooden door",
                 cap="A reciter at the microphone"),
    "da-1": dict(file="IMG_20260227_184526.jpg", id="1_d7_nonRbUC9NFjlgpf-VPQaCdHzojcT",
                 folder="17. Junior Group Dance Competition", size=(1600, 900, 800, 450),
                 alt="Dancers in yellow costumes and red scarves in a line across a stage with a "
                     "blue backdrop and a Dance Competition banner",
                 cap="The Junior Group Dance Competition, 27 February 2026"),
    "da-2": dict(file="IMG_20260227_185020.jpg", id="1ljKU9Q_MWmLg_8rLjjiZUJ0Bt25wgQ10",
                 folder="17. Junior Group Dance Competition", size=(1600, 900, 800, 450),
                 alt="A boy in an indigo costume in mid-step on stage, a group of dancers in white "
                     "and red behind him",
                 cap="A group in indigo, white and red"),
    "da-3": dict(file="IMG_20260227_183959.jpg", id="14updB0L2HcwPfUk5uRMSBVgTVZfYML9T",
                 folder="17. Junior Group Dance Competition", size=(1600, 900, 800, 450),
                 alt="Four dancers in black tops and gold trousers striking a pose on a stage with "
                     "a blue backdrop",
                 cap="Four dancers in black and gold"),
}

SEASON = [
    {"id": "spell-bee-2026", "name": "Junior Spell Bee", "date": "18 August 2026", "ghost": "18 Aug",
     "layout": "a", "photos": ["sb-1", "sb-2"],
     "line": "The screen behind the speaker reads &lsquo;Chinmaya International Residential School "
             "welcomes you to the Junior Spell Bee Competition&rsquo;, and gives the date.",
     "basis": "Dated from the screen in the photograph."},
    {"id": "poem-2026", "name": "Language Poem Recitation", "date": "12 February 2026",
     "ghost": "12 Feb", "layout": "b", "photos": ["po-1", "po-2", "po-3"],
     "line": "One pupil at a time recites at a microphone, before judges at a table and a school "
             "seated on the steps.",
     "basis": "Dated from the photographs&rsquo; own timestamps and the school&rsquo;s folder title."},
    {"id": "dance-2026", "name": "Junior Group Dance Competition", "date": "27 February 2026",
     "ghost": "27 Feb", "layout": "c", "photos": ["da-1", "da-2", "da-3"],
     "line": "Groups take the stage one after another beneath a hand-painted &lsquo;Dance "
             "Competition&rsquo; banner.",
     "basis": "Dated from the photographs&rsquo; own timestamps and the school&rsquo;s folder title."},
]

# ---------------------------------------------------------------------------
# The designed sequences. Each names laurels by id; the words are the page's.
# ---------------------------------------------------------------------------

# 2 — Excellence has many forms. A form is not a laurel: each line is a fact
# from the site, and the photograph is the school's.
FORMS = [
    ("academics", "Academics", "academic",
     "Twenty-four IB diplomas from twenty-four candidates, May 2026."),
    ("sport", "Sport", "track",
     "Overall champions of the South Zone Yoga Competition, July 2025."),
    ("arts", "Arts", "ensemble",
     "First prize at the Interschool Bhajan Competition, July 2025."),
    ("innovation", "Innovation", "expo",
     "More than 140 models and activities at the Science Expo, July 2025."),
    ("leadership", "Leadership", "elections",
     "Every classroom a constituency: the class elections of April 2025."),
    ("service", "Service", "seva",
     "Rallies, care homes and temple grounds: Seva Week, every April."),
]

# 3 — In figures. (figure, suffix, label, context, laurel id)
NUMBERS = [
    ("24", "/24", "IB Diplomas awarded",
     "Every candidate in the May 2026 examination earned the diploma.", "ib-2026"),
    ("45", "/45", "The maximum, twice",
     "Two students reached the highest score the IB Diploma allows.", "ib-2026"),
    ("17", "", "Medals at South Zone Yoga",
     "Six gold, five silver and six bronze, and the Overall Championship, July 2025.",
     "yoga-2025"),
    ("8", "th", "Year first in Tamil Nadu",
     "Education World&rsquo;s 2019 survey, which also placed CIRS second in India among "
     "co-educational boarding schools.", "ranking-2019"),
]

# 4 — The reel, oldest first. (laurel id, composition)
REEL = [
    ("kalam-2007", "a"),
    ("khel-mela-2008", "b"),
    ("isa-2011", "c"),
    ("vision-award-2012", "d"),
    ("brainfeed-2017", "a"),
    ("ranking-2019", "e"),
    ("yoga-2025", "b"),
    ("ib-2026", "d"),
]

# 5 — Featured laurels. (laurel id, headline, composition)
FEATURES = [
    ("ib-2026", "Two perfect scores.", "low-left"),
    ("yoga-2025", "Six gold. Five silver. Six bronze.", "top-right"),
    ("football-u14-2025", "Champions of thirty-six schools.", "split"),
    ("quzbiz-2025", "One team from a hundred and eighty.", "low-right"),
    ("bhajan-2025", "Ten voices, one first prize.", "centre"),
]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def plain(text):
    """Entity-laden HTML as the words it says, for an attribute."""
    return html.escape(html.unescape(re.sub(r"<[^>]+>", "", text)), quote=True)


def img_html(key, sizes, cls="", eager=False, lazy=True):
    path, w, h, alt, _cap, _ev = IMAGES[key]
    klass = f' class="{cls}"' if cls else ""
    load = ' fetchpriority="high"' if eager else (' loading="lazy"' if lazy else "")
    return (f'<img{klass} src="{path}" width="{w}" height="{h}" alt="{plain(alt)}" '
            f'sizes="{sizes}"{load} decoding="async">')


def caption(key):
    return IMAGES[key][4]


def cats_label(l):
    return " &middot; ".join(CAT_NAME[c] for c in l["cats"])


def meta_html(l, cls):
    level = f'<span>{LEVEL_NAME[l["level"]]}</span>' if l["level"] else ""
    return (f'<p class="{cls}"><span>{cats_label(l)}</span>{level}'
            f'<span>{l["when"]}</span></p>')


def source_html(l, cls="lr-source"):
    label, href = l["source"]
    return f'<p class="{cls}">Source: <a href="{href}">{label}</a></p>'


def season_photo(key, sizes, n):
    r = SEASON_PHOTOS[key]
    lw, lh, sw, sh = r["size"]
    img = (f'<img src="{SEASON_IMG}/{key}-800.jpg" '
           f'srcset="{SEASON_IMG}/{key}-800.jpg {sw}w, {SEASON_IMG}/{key}-1600.jpg {lw}w" '
           f'sizes="{sizes}" width="{lw}" height="{lh}" alt="{plain(r["alt"])}" '
           f'loading="lazy" decoding="async">')
    orient = "portrait" if lh > lw else "landscape"
    return (f'<figure class="lr-event__ph lr-event__ph--{n} is-{orient}" style="--i:{n}">'
            f'<div class="lr-event__frame" style="aspect-ratio:{lw}/{lh}">{img}</div>'
            f'<figcaption>{r["cap"]}</figcaption></figure>')


def season_html():
    out = []
    for ev in SEASON:
        sizes = {"a": ["(max-width: 899px) 92vw, 62vw", "(max-width: 899px) 92vw, 30vw"],
                 "b": ["(max-width: 899px) 92vw, 62vw", "(max-width: 899px) 92vw, 40vw",
                       "(max-width: 899px) 60vw, 22vw"],
                 "c": ["(max-width: 899px) 92vw, 56vw", "(max-width: 899px) 92vw, 34vw",
                       "(max-width: 899px) 92vw, 34vw"]}[ev["layout"]]
        photos = "".join(season_photo(k, sizes[i], i + 1) for i, k in enumerate(ev["photos"]))
        out.append(
            f'      <li class="lr-event lr-event--{ev["layout"]}" id="season-{ev["id"]}">\n'
            f'        <article class="lr-event__inner" aria-labelledby="ev-{ev["id"]}">\n'
            f'          <p class="lr-event__ghost" aria-hidden="true">{ev["ghost"]}</p>\n'
            f'          <header class="lr-event__head">\n'
            f'            <p class="lr-event__meta"><span>Competition</span><span>{ev["date"]}</span></p>\n'
            f'            <h3 class="lr-event__title" id="ev-{ev["id"]}">{ev["name"]}</h3>\n'
            f'            <p class="lr-event__line">{ev["line"]}</p>\n'
            f'            <p class="lr-event__status">Placings: not yet published on this site.</p>\n'
            f'            <p class="lr-event__basis">{ev["basis"]}</p>\n'
            f'          </header>\n'
            f'          {photos}\n'
            f'        </article>\n'
            f'      </li>')
    return "\n".join(out)


def forms_html():
    out = []
    for i, (key, word, image, note) in enumerate(FORMS):
        out.append(
            f'      <li class="lr-form lr-form--{i % 6 + 1}" data-form="{key}" '
            f'style="--len:{len(word)}">\n'
            f'        <h3 class="lr-form__word" aria-label="{word}">'
            + "".join(f'<span aria-hidden="true" style="--i:{j}">{ch}</span>'
                      for j, ch in enumerate(word)) +
            '</h3>\n'
            f'        <figure class="lr-form__media"><div class="lr-form__frame">'
            f'{img_html(image, "(max-width: 760px) 92vw, 46vw")}</div>'
            f'<figcaption>{caption(image)}</figcaption></figure>\n'
            f'        <p class="lr-form__note"><span class="lr-form__n">{i + 1:02d}</span> {note}</p>\n'
            f'      </li>')
    return "\n".join(out)


def numbers_html():
    out = []
    for i, (fig, suffix, label, context, lid) in enumerate(NUMBERS):
        suf = f'<span class="lr-number__suffix">{suffix}</span>' if suffix else ""
        label_src, href = BY_ID[lid]["source"]
        out.append(
            f'      <li class="lr-number">\n'
            f'        <p class="lr-number__figure" data-count="{fig}">'
            f'<span class="lr-number__big">{fig}</span>{suf}</p>\n'
            f'        <div class="lr-number__copy">\n'
            f'          <p class="lr-number__label">{label}</p>\n'
            f'          <p class="lr-number__context">{context}</p>\n'
            f'          <p class="lr-source">Source: <a href="{href}">{label_src}</a></p>\n'
            f'        </div>\n'
            f'      </li>')
    return "\n".join(out)


def reel_html():
    out = []
    for i, (lid, comp) in enumerate(REEL):
        l = BY_ID[lid]
        media = ""
        if l["image"]:
            media = (f'<figure class="lr-spread__media"><div class="lr-spread__frame">'
                     f'{img_html(l["image"], "(max-width: 760px) 92vw, 34vw")}</div>'
                     f'<figcaption>{caption(l["image"])}</figcaption></figure>')
        out.append(
            f'        <li class="lr-spread lr-spread--{comp}" data-year="{l["year"]}">\n'
            f'          <article class="lr-spread__inner" aria-labelledby="reel-{lid}">\n'
            f'            <p class="lr-spread__year" aria-hidden="true">{l["year"]}</p>\n'
            f'            {media}\n'
            f'            <div class="lr-spread__copy">\n'
            f'              {meta_html(l, "lr-spread__meta")}\n'
            f'              <h3 class="lr-spread__title" id="reel-{lid}">{l["title"]}</h3>\n'
            f'              <p class="lr-spread__event">{l["event"]}</p>\n'
            f'              <p class="lr-spread__text">{l["text"]}</p>\n'
            f'              {source_html(l)}\n'
            f'            </div>\n'
            f'          </article>\n'
            f'        </li>')
    return "\n".join(out)


def names_line(l):
    return ", ".join(n for n, _ in l["names"]).replace("&amp;", "and")


def features_html():
    out = []
    for i, (lid, headline, comp) in enumerate(FEATURES):
        l = BY_ID[lid]
        names = ""
        if l["names"]:
            names = ('<ul class="lr-feature__names">' + "".join(
                f'<li>{n}</li>' for n, _ in l["names"]) + '</ul>')
        words = headline.split(" ")
        title = " ".join(f'<span class="lr-line"><span style="--i:{j}">{w}</span></span>'
                         for j, w in enumerate(words))
        out.append(
            f'  <article class="lr-feature lr-feature--{comp}" id="featured-{lid}" '
            f'aria-labelledby="feature-{lid}-title">\n'
            f'    <figure class="lr-feature__media">'
            f'<div class="lr-feature__frame">{img_html(l["image"], "100vw")}</div>'
            f'<figcaption class="lr-feature__cap">{caption(l["image"])}</figcaption></figure>\n'
            f'    <div class="lr-feature__copy">\n'
            f'      <p class="lr-feature__index" aria-hidden="true">{i + 1:02d}</p>\n'
            f'      {meta_html(l, "lr-feature__meta")}\n'
            f'      <h3 class="lr-feature__title" id="feature-{lid}-title" '
            f'aria-label="{plain(headline)}">{title}</h3>\n'
            f'      <p class="lr-feature__event">{l["event"]}</p>\n'
            f'      <p class="lr-feature__text">{l["text"]}</p>\n'
            f'      {names}\n'
            f'      {source_html(l, "lr-source lr-source--dark")}\n'
            f'    </div>\n'
            f'  </article>')
    return "\n".join(out)


def filters_html():
    total = len(LAURELS)
    cats = [f'<li><button type="button" class="lr-cat" data-cat="all" aria-pressed="true">'
            f'<span class="lr-cat__n">00</span><span class="lr-cat__name">All</span>'
            f'<span class="lr-cat__count">{total}</span></button></li>']
    for i, (key, name) in enumerate(CATEGORIES, 1):
        n = sum(1 for l in LAURELS if key in l["cats"])
        cats.append(f'<li><button type="button" class="lr-cat" data-cat="{key}" '
                    f'aria-pressed="false"><span class="lr-cat__n">{i:02d}</span>'
                    f'<span class="lr-cat__name">{name}</span>'
                    f'<span class="lr-cat__count">{n}</span></button></li>')
    levels = ['<button type="button" class="lr-opt" data-level="all" aria-pressed="true">'
              'Every level</button>']
    for key, name in LEVELS:
        levels.append(f'<button type="button" class="lr-opt" data-level="{key}" '
                      f'aria-pressed="false">{name}</button>')
    years = ['<button type="button" class="lr-opt" data-year="all" aria-pressed="true">'
             'Every year</button>']
    for y in YEARS:
        years.append(f'<button type="button" class="lr-opt" data-year="{y}" '
                     f'aria-pressed="false">{y}</button>')
    if any(l["year"] is None for l in LAURELS):
        years.append('<button type="button" class="lr-opt" data-year="undated" '
                     'aria-pressed="false">Undated</button>')
    return (
        '    <div class="lr-filters" data-lr-filters hidden>\n'
        '      <ol class="lr-cats" aria-label="Filter by category">\n        '
        + "\n        ".join(cats) +
        '\n      </ol>\n'
        '      <div class="lr-opts">\n'
        '        <div class="lr-opts__group" role="group" aria-labelledby="lr-level-label">'
        '<span class="lr-opts__label" id="lr-level-label">Level</span>'
        + "".join(levels) + '</div>\n'
        '        <div class="lr-opts__group" role="group" aria-labelledby="lr-year-label">'
        '<span class="lr-opts__label" id="lr-year-label">Year</span>'
        + "".join(years) + '</div>\n'
        '      </div>\n'
        '    </div>')


def grid_html():
    out = []
    for l in LAURELS:
        weight = l["weight"]
        has_img = bool(l["image"]) and weight != "text"
        media = ""
        if has_img:
            sizes = {"feature": "(max-width: 760px) 92vw, 62vw",
                     "wide": "(max-width: 760px) 92vw, 50vw",
                     "tall": "(max-width: 760px) 92vw, 32vw",
                     "small": "(max-width: 760px) 40vw, 30vw"}[weight]
            media = (f'<figure class="lr-card__media"><div class="lr-card__frame">'
                     f'{img_html(l["image"], sizes)}</div>'
                     f'<figcaption class="lr-card__cap">{caption(l["image"])}</figcaption>'
                     f'</figure>')
        figure = (f'<p class="lr-card__figure" aria-hidden="true">{l["figure"]}</p>'
                  if weight == "text" and l.get("figure") else "")
        year = l["year"] or "undated"
        names = ""
        if l["names"]:
            names = ('<ul class="lr-card__names">' + "".join(
                f'<li><b>{n}</b> {what}</li>' for n, what in l["names"]) + '</ul>')
        pending = " is-pending" if l.get("pending") else ""
        out.append(
            f'      <li class="lr-item lr-item--{weight}{pending}" id="laurel-{l["id"]}" '
            f'data-cats="{" ".join(l["cats"])}" data-level="{l["level"] or ""}" '
            f'data-year="{year}">\n'
            f'        <article class="lr-card" aria-labelledby="card-{l["id"]}">\n'
            f'          {media}{figure}\n'
            f'          <div class="lr-card__body">\n'
            f'            {meta_html(l, "lr-card__meta")}\n'
            f'            <h3 class="lr-card__title" id="card-{l["id"]}">'
            f'<button type="button" class="lr-card__open" aria-haspopup="dialog" '
            f'data-laurel="{l["id"]}">{l["title"]}</button></h3>\n'
            f'            <p class="lr-card__result">{l["result"]}</p>\n'
            f'            <div class="lr-card__more">\n'
            f'              <p class="lr-card__event">{l["event"]}</p>\n'
            f'              <p class="lr-card__text">{l["text"]}</p>\n'
            f'              {names}\n'
            f'              {source_html(l)}\n'
            f'            </div>\n'
            f'          </div>\n'
            f'        </article>\n'
            f'      </li>')
    return "\n".join(out)


def timeline_html():
    span = LAST_YEAR - FIRST_YEAR
    marks, panels = [], []
    for i, y in enumerate(sorted(YEARS)):
        items = [l for l in LAURELS if l["year"] == y]
        n = len(items)
        x = (y - FIRST_YEAR) / span
        marks.append(
            f'<li style="--x:{x:.4f}" class="{"is-alt" if i % 2 else ""}">'
            f'<button type="button" class="lr-tl__year" data-year="{y}" aria-pressed="false" '
            f'aria-controls="lr-tl-{y}"><span class="lr-tl__y">{y}</span>'
            f'<span class="lr-tl__n">{n} {"laurel" if n == 1 else "laurels"}</span>'
            f'</button></li>')
        rows = "".join(
            f'<li><a href="#laurel-{l["id"]}" data-laurel-link="{l["id"]}">'
            f'<span class="lr-tl__cat">{cats_label(l)}</span>'
            f'<span class="lr-tl__title">{l["title"]}</span>'
            f'<span class="lr-tl__when">{l["when"]}</span></a></li>' for l in items)
        panels.append(
            f'<div class="lr-tl__panel" id="lr-tl-{y}" data-year="{y}">'
            f'<h3 class="lr-tl__head"><span>{y}</span> '
            f'<small>{n} {"laurel" if n == 1 else "laurels"} on record</small></h3>'
            f'<ol class="lr-tl__list">{rows}</ol>'
            f'<button type="button" class="lr-tl__show" data-show-year="{y}">'
            f'Show {y} in the archive <span aria-hidden="true">&uarr;</span></button></div>')
    return (
        '    <div class="lr-tl__rail" data-lr-rail>\n'
        f'      <span class="lr-tl__end lr-tl__end--start">{FIRST_YEAR}</span>\n'
        '      <div class="lr-tl__track"><span class="lr-tl__line" aria-hidden="true"></span>'
        '<span class="lr-tl__handle" aria-hidden="true"></span>\n'
        '        <ol class="lr-tl__years" aria-label="Years with laurels on record">'
        + "".join(marks) + '</ol>\n'
        '      </div>\n'
        '      <span class="lr-tl__end lr-tl__end--end">Today</span>\n'
        '    </div>\n'
        '    <div class="lr-tl__panels" data-lr-panels>' + "".join(panels) + '</div>')


def names_html():
    """The roll of names. Sizes and drift are fixed here, not random, so the
    composition is the same on every load and before any script runs."""
    seen, roll = {}, []
    for l in LAURELS:
        for n, what in l["names"]:
            key = n
            if key in seen:
                seen[key]["what"].append((what, l))
                continue
            seen[key] = {"name": n, "what": [(what, l)], "house": l.get("house", False)}
            roll.append(seen[key])
    # Interleave so no two neighbours share a year's cluster.
    order = roll[::2] + roll[1::2]
    out = []
    for i, r in enumerate(order):
        size = (i * 7 + 3) % 5 + 1
        style = "i" if i % 3 == 1 else "r"
        drift = ((i * 37) % 11 - 5) / 5
        detail = "; ".join(f'{w}, {l["year"] or "undated"}' for w, l in r["what"])
        house = " lr-name--house" if r["house"] else ""
        out.append(
            f'      <li class="lr-name lr-name--s{size} lr-name--{style}{house}" '
            f'style="--drift:{drift:.2f}">'
            f'<button type="button" class="lr-name__btn" aria-describedby="lr-name-{i}">'
            f'{r["name"]}</button>'
            f'<span class="lr-name__detail" id="lr-name-{i}">{detail}</span></li>')
    return "\n".join(out), len(order)


def hero_points_json():
    """The laurels as points for the opening field: enough to preview."""
    pts = [{"y": l["year"] or "", "t": plain(l["title"]), "c": plain(cats_label(l))}
           for l in LAURELS]
    return json.dumps(pts, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def expand(content):
    names, count = names_html()
    people = sum(len(l["names"]) for l in LAURELS)
    return (content.replace("{{LAURELS_FORMS}}", forms_html())
                   .replace("{{LAURELS_NUMBERS}}", numbers_html())
                   .replace("{{LAURELS_REEL}}", reel_html())
                   .replace("{{LAURELS_FEATURES}}", features_html())
                   .replace("{{LAURELS_FILTERS}}", filters_html())
                   .replace("{{LAURELS_GRID}}", grid_html())
                   .replace("{{LAURELS_TIMELINE}}", timeline_html())
                   .replace("{{LAURELS_SEASON}}", season_html())
                   .replace("{{LAURELS_NAMES}}", names)
                   .replace("{{LAURELS_NAME_COUNT}}", str(count))
                   .replace("{{LAURELS_COUNT}}", str(len(LAURELS)))
                   .replace("{{LAURELS_YEAR_SPAN}}", f"{min(YEARS)}&ndash;{max(YEARS)}")
                   .replace("{{LAURELS_POINTS}}", hero_points_json()))


if __name__ == "__main__":
    print(f"{len(LAURELS)} laurels, {len(YEARS)} years: {', '.join(map(str, sorted(YEARS)))}")
    for c, name in CATEGORIES:
        print(f"  {name:14} {sum(1 for l in LAURELS if c in l['cats'])}")
    print("\nHeld back:")
    for what, why in HELD:
        print(f"  - {what}: {why}")
