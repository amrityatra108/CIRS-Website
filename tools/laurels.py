#!/usr/bin/env python3
"""Our Laurels: every honour on the page, where it came from, and the page.

Nothing here is new information. Each laurel is copied from a record this
site already publishes, and names that record in "source":

    competitions.html        the school's own roundup of the 2025 inter-school
                             results, published 1 October 2025
                             (tools/newsarticles.py, slug "competitions")
    news.html#…-results-2026 the school's results briefs for 2026
    annual-report.pdf        the school's Annual Report of 7 October 2025, in
                             the document register on School Information
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
# Innovation came in with the Annual Report of 7 October 2025.
# ---------------------------------------------------------------------------
CATEGORIES = [
    ("academics", "Academics"),
    ("sport", "Sport"),
    ("arts", "Arts"),
    ("speech", "Speech"),
    ("innovation", "Innovation"),
    ("leadership", "Leadership"),
    ("international", "International"),
    ("school", "The School"),
]
CAT_NAME = dict(CATEGORIES)

LEVELS = [
    ("inter-house", "Inter-house"),
    ("inter-school", "Inter-school"),
    ("zonal", "Zonal"),
    ("state", "State"),
    ("national", "National"),
    ("international", "International"),
]
LEVEL_NAME = dict(LEVELS)

ROUNDUP = ("Competitions across CIRS, the school&rsquo;s report of 1 October 2025",
           "competitions.html")
IB_BRIEF = ("The school&rsquo;s IB results brief", "news.html#ib-results-2026")
CBSE_BRIEF = ("The school&rsquo;s CBSE results brief", "news.html#cbse-results-2026")
AR2025 = ("The school&rsquo;s Annual Report, 7 October 2025",
          "assets/documents/school-info/annual-report.pdf")


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
     "title": "Two seconds and a fourth at the Sahodaya Spell Bee",
     "event": "46th CBSE Sahodaya English Spell Bee, Anugraha Mandhir CBSE Senior Secondary "
              "School, Coimbatore",
     "result": "Two seconds and a fourth",
     "text": "Tanay Lakshman of Grade 8 and Rhea of Grade 10 each took second place, and "
             "M.&nbsp;K. Prateethi of Class 12 fourth.",
     "names": [("M.&nbsp;K. Prateethi", "Fourth in the Sahodaya Spell Bee")],
     "source": AR2025, "image": None, "weight": "text", "figure": "2 &middot; 2 &middot; 4"},

    # ---- 2025, from the Annual Report of 7 October 2025 --------------------
    # Names as the report prints them. The report spells one Class XII student
    # "Kanistha C", "Kanishta" and "Kansihtha Chopra", and one swimmer "DILIP
    # REDDY" and "Dhilip Reddy"; each laurel keeps its own paragraph's spelling
    # and nothing is merged. First names alone stay out of the roll.
    {"id": "ranking-2025", "year": 2025, "when": "Reported October 2025",
     "cats": ["school"], "level": "national",
     "title": "Second in India, first in Tamil Nadu for the fourteenth year",
     "event": "Education World and Brainfeed school rankings",
     "result": "Education World: 2nd in India, 1st in Tamil Nadu &middot; Brainfeed: 3rd in India",
     "text": "Education World ranked CIRS second in the country among India&rsquo;s top "
             "co-educational boarding schools, and first in Tamil Nadu and Coimbatore for the "
             "14th consecutive year. Brainfeed ranked the school third in the country and first "
             "in both the state and the city.",
     "names": [],
     "source": history("report-2025", "the Annual Report, 7 October 2025"),
     "image": None, "weight": "text", "figure": "14"},
    {"id": "cbse-xii-2025", "year": 2025, "when": "2025",
     "cats": ["academics"], "level": "national",
     "title": "45 of 47 above 80 per cent in Class XII",
     "event": "CBSE Class XII board examinations",
     "result": "Management topper 98.6% &middot; Science topper 98.4%",
     "text": "V Athmika topped the Management stream with 98.6% and Kanistha C the Science "
             "stream with 98.4%. Of 47 students, 34 scored above 90% and 45 above 80%; Science "
             "averaged 89% and Management 93%, with centums in Mathematics, Physical Education, "
             "Informatics Practices and Business Studies.",
     "names": [("V Athmika", "98.6% in Class XII Management, 2025"),
               ("Kanistha C", "98.4% in Class XII Science, 2025")],
     "source": AR2025, "image": None, "weight": "text", "figure": "98.6"},
    {"id": "cbse-x-2025", "year": 2025, "when": "2025",
     "cats": ["academics"], "level": "national",
     "title": "An average of 89.2 per cent in Class X",
     "event": "CBSE Class X board examinations",
     "result": "Class topper 97.8% &middot; 56 of 95 at 90% or above",
     "text": "Ved Tulsian topped Class X with 97.8%. Of 95 students, 56 scored 90% or above and "
             "85 above 80%, and there were centums in Mathematics (eleven), Sanskrit (four), "
             "French (two), Science and Hindi.",
     "names": [("Ved Tulsian", "97.8% in Class X, 2025")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "ib-2025", "year": 2025, "when": "May 2025",
     "cats": ["academics", "international"], "level": "international",
     "title": "44 out of 45 in the IB Diploma",
     "event": "IB Diploma Programme, May 2025 examination",
     "result": "8 of 19 above 40 points &middot; highest 44",
     "text": "Shubhaang Agarwal scored 44 out of 45, followed by Raahi with 43, and Reshmi and "
             "Rishi Iyer with 42. Eight of the 19 candidates scored above 40, and the class "
             "averaged 38.9 points.",
     "names": [("Shubhaang Agarwal", "44 out of 45 in the IB Diploma, 2025"),
               ("Rishi Iyer", "42 out of 45 in the IB Diploma, 2025")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "studentrepreneur-2025", "year": 2025, "when": "Reported October 2025",
     "cats": ["innovation"], "level": "inter-school",
     "title": "First prize at SSVM Studentrepreneur",
     "event": "&lsquo;SSVM Studentrepreneur&rsquo; competition, SSVM, Coimbatore",
     "result": "First prize &middot; &#8377;75,000",
     "text": "Raunak, Naitik and Arnav won first prize for their project, and a cash reward of "
             "&#8377;75,000.",
     "names": [],
     "source": AR2025, "image": None, "weight": "text", "figure": "1st"},
    {"id": "youth-made-2025", "year": 2025, "when": "29 May 2025",
     "cats": ["innovation"], "level": None,
     "title": "A prize at the Youth MADE Festival",
     "event": "2025 Youth MADE Festival",
     "result": "Prize of $500",
     "text": "The project of Kanishk C K, Aaditya Tulsyan, Vishwanth, Hema Ruthvick and Arjun "
             "Reddy was recognised for its creativity, innovation and potential impact, and "
             "won $500.",
     "names": [("Kanishk C K", "Youth MADE Festival prize, 2025"),
               ("Aaditya Tulsyan", "Youth MADE Festival prize, 2025"),
               ("Hema Ruthvick", "Youth MADE Festival prize, 2025"),
               ("Arjun Reddy", "Youth MADE Festival prize, 2025")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "mindkraft-2025", "year": 2025, "when": "2025",
     "cats": ["innovation", "academics", "arts"], "level": "inter-school",
     "title": "Ideathon winners at Mindkraft",
     "event": "Mindkraft 2025, Karunya University, on World Water Day",
     "result": "Ideathon 1st &middot; quiz 2nd and 3rd &middot; painting 2nd",
     "text": "Competing against universities and colleges across Tamil Nadu, Kanishk, Krishnav "
             "Deorah and Aaditya Tulsyan won the Ideathon and &#8377;5,000. In the quiz, "
             "Vishvprem, Divyam, Aneesh and Viraj Lal came second and Krishnav Deorah, Aaditya "
             "Tulsyan and Kanishk third; Ritika Deorah was second in the painting competition.",
     "names": [("Krishnav Deorah", "Mindkraft Ideathon, first"),
               ("Ritika Deorah", "Mindkraft painting, second")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "zestro-2025", "year": 2025, "when": "25&ndash;26 February 2025",
     "cats": ["innovation", "academics"], "level": "inter-school",
     "title": "Overall champions at ZESTRO&rsquo;25",
     "event": "ZESTRO&rsquo;25, a national-level technical symposium, Karunya Deemed University",
     "result": "Overall championship &middot; quiz 1st and 2nd",
     "text": "In the quiz Divyam, Vishvprem and Swarit won and Pradyuth, Jasith and Devansh were "
             "runners-up. A CIRS team won the Project Expo and Paper Presentation with a "
             "project on forest animal conservation, and CIRS took the overall championship.",
     "names": [],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "robotica-2025", "year": 2025, "when": "7 February 2025",
     "cats": ["innovation"], "level": "inter-school",
     "title": "Runners-up at Robotica",
     "event": "Robotica 2025, the Robotics Club of VIT Chennai",
     "result": "Runners-up",
     "text": "Amogh Agarwal, Aryaman Bansal and Kanishk C K took the runners-up place in the "
             "robotics competition.",
     "names": [("Amogh Agarwal", "Robotica 2025, runners-up"),
               ("Aryaman Bansal", "Robotica 2025, runners-up")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "vssf-2025", "year": 2025, "when": "12&ndash;14 June 2025",
     "cats": ["academics"], "level": "national",
     "title": "Top 100 of a lakh, VSSF Science Camp",
     "event": "SPOT test and Science Camp, Vikram Sarabhai Science Foundation, Pune",
     "result": "Two of the top 100 in India",
     "text": "Pradyuth Senthilkumar of Grade 9 and Kansihtha Chopra of Grade 12 were selected "
             "among the top 100 of one lakh participants across the country through the SPOT "
             "test, and attended the VSSF Science Camp in Pune.",
     "names": [("Pradyuth Senthilkumar", "VSSF SPOT test, top 100 in India"),
               ("Kansihtha Chopra", "VSSF SPOT test, top 100 in India")],
     "source": AR2025, "image": None, "weight": "text", "figure": "100"},
    {"id": "yuvika-2025", "year": 2025, "when": "19&ndash;30 May 2025",
     "cats": ["academics"], "level": "national",
     "title": "Selected for ISRO YUVIKA",
     "event": "ISRO YUVIKA 2025, Vikram Sarabhai Space Centre, Thiruvananthapuram",
     "result": "Selected to represent the school",
     "text": "Ritika Deorah was selected for ISRO&rsquo;s YUVIKA programme, where she worked "
             "with ISRO scientists on group projects and science quizzes.",
     "names": [("Ritika Deorah", "ISRO YUVIKA 2025")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "space-quiz-2025", "year": 2025, "when": "29&ndash;31 July 2025",
     "cats": ["academics"], "level": None,
     "title": "To Sriharikota for a launch",
     "event": "Space Quiz, Sri Shakthi Engineering and Technology",
     "result": "Among the top 100 winners",
     "text": "As two of the top 100 winners of the Space Quiz, Naitik Agarwala of Class 11 and "
             "Anirudhha Koganti of the first IB year visited ISRO&rsquo;s Satish Dhawan Space "
             "Centre and watched the NISAR satellite launch aboard the GSLV-F16 on 30 July "
             "2025.",
     "names": [("Naitik Agarwala", "Space Quiz, top 100"),
               ("Anirudhha Koganti", "Space Quiz, top 100")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "aviation-quiz-2025", "year": 2025, "when": "Reported October 2025",
     "cats": ["academics"], "level": "state",
     "title": "Third in the state aviation quiz",
     "event": "State-level Quiz on the Aviation Industry, Remo International College with Hindu "
              "Tamil Thisai",
     "result": "Third of 12 finalists &middot; &#8377;5,000",
     "text": "Divyam Gupta was one of the 12 finalists from Tamil Nadu and Puducherry and took "
             "third place, with a cash prize of &#8377;5,000.",
     "names": [("Divyam Gupta", "Third, state aviation quiz")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "hmun-2025", "year": 2025, "when": "14&ndash;17 August 2025",
     "cats": ["speech", "leadership", "international"], "level": "international",
     "title": "Outstanding delegates at Harvard MUN",
     "event": "Harvard Model United Nations (HMUN) 2025",
     "result": "Two Outstanding Delegate awards",
     "text": "Forty CIRS students took part. Adwaith and Aryan received Outstanding Delegate "
             "awards; Shwet, Ashi, Aniruddha and Shaurya were named determined delegates, and "
             "Sairam received a diplomatic commendation.",
     "names": [],
     "source": history("mun-2025", "Harvard and IIMUN"), "image": None, "weight": "small"},
    {"id": "iimun-2025", "year": 2025, "when": "14&ndash;17 August 2025",
     "cats": ["speech", "leadership"], "level": "national",
     "title": "Mentions at the IIMUN Championship",
     "event": "14th IIMUN Championship Conference 2025, Mumbai",
     "result": "A special mention and two verbal mentions",
     "text": "34 CIRS students represented nations. Aryaman Bansal received a special mention, "
             "and Ahana Nair and Sannvi Bagaria verbal mentions.",
     "names": [("Aryaman Bansal", "Special mention, IIMUN 2025"),
               ("Ahana Nair", "Verbal mention, IIMUN 2025"),
               ("Sannvi Bagaria", "Verbal mention, IIMUN 2025")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "ncc-2025", "year": 2025, "when": "1&ndash;10 July 2025",
     "cats": ["leadership"], "level": None,
     "title": "Best Cadets at the NCC camp",
     "event": "NCC Annual Training Camp, Kalaignar Karunanidhi Institute of Technology",
     "result": "Overall Best Cadets award",
     "text": "36 CIRS cadets won medals in the drill test, quiz, relay, shot put and football, "
             "and the school received the overall Best Cadets award.",
     "names": [],
     "source": history("ncc-2025", "Best Cadets at the NCC camp"),
     "image": None, "weight": "text", "figure": "36"},
    {"id": "south-zone-swimming-2025", "year": 2025, "when": "26&ndash;30 August 2025",
     "cats": ["sport"], "level": "zonal",
     "title": "Two bronzes at South Zone swimming",
     "event": "South Zone Swimming Competition 2025&ndash;26, The Navabharath International "
              "School, Annur",
     "result": "Under-17 relay bronze &middot; Under-17 girls 400 m bronze",
     "text": "Among more than 1,500 swimmers from 310 schools, Shrey Kothari, Arav Jagadesh, "
             "Vidhur Vaibhav, Chundi Sai Bava Rishi and Sidharth Abinav Raja won bronze in the "
             "Under-17 boys&rsquo; 4 &times; 100 m freestyle relay, and Anagha Mappat bronze in "
             "the Under-17 girls&rsquo; 400 m.",
     "names": [("Anagha Mappat", "Bronze, 400 m, South Zone swimming")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "state-swimming-2025", "year": 2025, "when": "5 July 2025",
     "cats": ["sport"], "level": "state",
     "title": "Gold in the 200 m freestyle",
     "event": "Prime Sports State Level Swimming Competition, The Life Spring Swimming Club",
     "result": "One gold and two bronze &middot; 75 schools",
     "text": "Among more than 350 swimmers from 75 schools, Shrey Kothari won gold in the 200 m "
             "freestyle and bronze in the 100 m butterfly, and Dhilip Reddy bronze in the 100 m "
             "freestyle. At the CM Trophy on 6 September, at Bharathiar University, Shrey Kothari "
             "won bronze in the 200 m butterfly and the 200 m individual medley, and Dilip Reddy "
             "bronze in the 100 m freestyle.",
     "names": [("Shrey Kothari", "Gold, 200 m freestyle, state level")],
     "source": AR2025, "image": None, "weight": "text", "figure": "Gold"},
    {"id": "tennis-2025", "year": 2025, "when": "May and September 2025",
     "cats": ["sport"], "level": "state",
     "title": "A title and two finals in tennis",
     "event": "Jharkhand State Tennis Tournament, and the GST Tennis Tournament, Global School "
              "of Tennis",
     "result": "Under-16 singles winner &middot; Under-18 state runner-up",
     "text": "Shaurya Gadhyan was runner-up in the Under-18 singles of the Jharkhand state "
             "tournament in May. At the GST tournament on 28 September, Deepansh Gupta won the "
             "Under-16 singles, he and Shaurya Gadhyan were runners-up in the Under-16 doubles, "
             "and Yug Goyal placed third in the Under-14 singles.",
     "names": [("Deepansh Gupta", "Winner, Under-16 singles, GST tennis"),
               ("Shaurya Gadhyan", "Runner-up, Under-18 singles, Jharkhand state")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "football-u16-2025", "year": 2025, "when": "28&ndash;29 August 2025",
     "cats": ["sport"], "level": "inter-school",
     "title": "Runners-up, Under-16 and Under-12 football",
     "event": "46th Sahodaya 11-on-11 Inter School Football Tournament, Agaram Public School, "
              "Karur",
     "result": "Under-16 runners-up &middot; Under-12 runners-up",
     "text": "The CIRS Under-16 boys finished as runners-up. At the 3rd Nathan Memorial "
             "tournament on 4&ndash;5 July, at Vivekam Sr. Sec. School, Coimbatore, the "
             "Under-12 boys were also runners-up, and Anirudh E.S of Grade 6 was named Best "
             "Player.",
     "names": [("Anirudh E.S", "Best Player, Under-12 football")],
     "source": AR2025, "image": None, "weight": "text", "figure": "2nd"},
    {"id": "district-2025", "year": 2025, "when": "2025",
     "cats": ["sport"], "level": None,
     "title": "Called up by the district",
     "event": "Coimbatore district selections",
     "result": "Basketball camp &middot; Sub Junior hockey team",
     "text": "Yug Didwania of Grade 8 was selected for the Coimbatore district basketball camp "
             "on 4 August 2025, and Hardik Saralia was among the final 18 players chosen for "
             "the Coimbatore District Sub Junior Men&rsquo;s Hockey Team.",
     "names": [("Yug Didwania", "Coimbatore district basketball camp"),
               ("Hardik Saralia", "Coimbatore District Sub Junior hockey team")],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "vanijya-ratna-2025", "year": 2025, "when": "Reported October 2025",
     "cats": ["school"], "level": None,
     "title": "Vanijya Ratna for a CIRS teacher",
     "event": "Commerce Teachers Foundation",
     "result": "Vanijya Ratna Award",
     "text": "Dr. Rashmi was given the Vanijya Ratna Award for her contribution to education; "
             "her students averaged 96% in Accountancy.",
     "names": [],
     "source": AR2025, "image": None, "weight": "small"},

    # ---- 2024 ------------------------------------------------------------
    {"id": "kreativity-2024", "year": 2024, "when": "27&ndash;28 December 2024",
     "cats": ["innovation"], "level": "national",
     "title": "Third at the Kreativity League, IIT Delhi",
     "event": "Kreativity League 2024 Grand Finale, IIT Delhi",
     "result": "Third of 300 participants &middot; &#8377;9,000",
     "text": "Among 300 participants, Jayam, Gatik and Arnav took third place, winning trophies "
             "and a cash prize of &#8377;9,000.",
     "names": [],
     "source": AR2025, "image": None, "weight": "small"},
    {"id": "jklu-2024", "year": 2024, "when": "1 December 2024",
     "cats": ["innovation"], "level": None,
     "title": "Overall winners, &lsquo;My City, My Lab&rsquo;",
     "event": "JK Lakshmipat University &lsquo;My City, My Lab&rsquo; Ideathon 2024",
     "result": "Overall winners &middot; &#8377;1 lakh",
     "text": "Team Vayunigrah &mdash; Jayam Mangalam Modi, Gatik Chhawachharia and Arnav "
             "Agarwal &mdash; won the Ideathon for their innovative approach and practical "
             "solution design, and a prize of one lakh rupees.",
     "names": [("Jayam Mangalam Modi", "JKLU Ideathon, overall winners"),
               ("Gatik Chhawachharia", "JKLU Ideathon, overall winners"),
               ("Arnav Agarwal", "JKLU Ideathon, overall winners")],
     "source": AR2025, "image": None, "weight": "text", "figure": "&#8377;1L"},

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

# Held back, with the reason. Printed by `python3 tools/laurels.py`.
HELD = [
    ("Ranked 16th IB school worldwide", "On the home ticker; no source or year in hand."),
    ("Among the top 50 CBSE schools in India", "On the home ticker; no source or year."),
    ("IB World Toppers, 45/45, 2019 and 2024", "Held in tools/history.py UNRESOLVED."),
    ("Vayu Nigrah, first prize, SSVM Transforming India Conclave",
     "Prize unconfirmed; the year may be 2024 (tools/history.py UNRESOLVED). The Annual "
     "Report's JKLU Ideathon win by Team Vayunigrah (jklu-2024) is a different prize."),
    ("Annual Report 2025: the yoga teacher's first place, the Kangeyam Marathon and the "
     "CBSE Cluster VI athletics", "The yoga line cannot be read reliably; the marathon (6th to "
     "8th among 26,000) and athletics (5th to 8th) placings are taking part, not laurels."),
    ("Annual Report 2025: 'Out of 600 up IB school, CIRS stands 15th in the world'",
     "Cannot be read reliably; see tools/history.py, results-2025."),
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
# The designed sequences. Each names laurels by id and shows only what the
# record says. "evidence" is the phrase in the record that carries a figure or
# a line the page sets large; audit() fails the build if it is not there, so a
# number on the page can never drift from its record.
# ---------------------------------------------------------------------------

FIRST_YEAR, LAST_YEAR = min(YEARS), max(YEARS)
SCHOOL_OPENED = ("6 June 1996", "school-history.html#record-inauguration-1996")

# How a source is described on the page. Only what the link really is:
# a report the school published, its own annual report, a record in the
# School History archive, a newsletter as reproduced, the school's own account.
SOURCE_KINDS = {
    "news.html": "Results brief",
    "competitions.html": "School report",
    "school-history.html": "Archive record",
    "houses.html": "Newsletter record",
    "why-cirs.html": "School account",
}

# The larger scans, for looking closely. A "document" is a page photographed
# or scanned; the other exhibits are photographs of an object or an occasion.
LG = {
    "kalam": ("assets/img/history/kalam-2007-lg.jpg", 1170, 1683),
    "sakshi": ("assets/img/history/sakshi-2008-lg.jpg", 1332, 1812),
    "isa": ("assets/img/history/isa-2010-lg.jpg", 1087, 1601),
    "report": ("assets/img/history/report-2019-lg.jpg", 1087, 1597),
}
DOCUMENTS = {"kalam", "sakshi", "isa", "report"}

# 1 — the opening: fragments of evidence at three depths around the count.
#     (shown, laurel, evidence, depth, x %, y %, kept on a phone)
FRAGMENTS = [
    ("45 / 45", "ib-2026", "45 out of 45", "near", 71, 17, True),
    ("99.0%", "cbse-xii-management-2026", "99.0%", "near", 9, 72, True),
    ("6 · 5 · 6", "yoga-2025", "6 gold, 5 silver, 6 bronze", "mid", 14, 20, True),
    ("24 / 24", "ib-2026", "24 of 24 diplomas", "mid", 82, 60, False),
    ("Top 500", "brainfeed-2017", "Top 500 Schools of India", "mid", 74, 82, True),
    ("Rashtrapati Bhavan", "kalam-2007", "Rashtrapati Bhavan", "far", 4, 90, False),
    ("14th consecutive year", "ranking-2025", "14th consecutive year", "far", 3, 54, False),
    ("top 100 of one lakh", "vssf-2025", "top 100 of one lakh", "far", 84, 44, False),
    ("₹1 lakh", "jklu-2024", "₹1 lakh", "far", 15, 38, False),
]

# 2 — one field at a time. The lead is the record that introduces the field;
#     "label" is a phrase taken from it, "stat" a figure in its evidence.
LEADS = {
    "academics": dict(laurel="ib-2026", stat="45 / 45", evidence="45 out of 45",
                      label="two scores of 45 out of 45"),
    "sport": dict(laurel="football-u14-2025", stat="36", evidence="36 schools",
                  label="Champions of 36 schools"),
    "arts": dict(laurel="bhajan-2025", stat="1st", evidence="First of more than 20 schools",
                 label="First of more than 20 schools"),
    "speech": dict(laurel="public-speaking-2025", stat="1st", evidence="First place",
                   label="First place"),
    "innovation": dict(laurel="jklu-2024", stat="₹1 lakh", evidence="₹1 lakh",
                       label="Overall winners"),
    "leadership": dict(laurel="kalam-2007", stat="32", evidence="32 students",
                       label="32 students received by the President"),
    "international": dict(laurel="isa-2011", stat=None, evidence="International School Award",
                          label="International School Award"),
    "school": dict(laurel="brainfeed-2017", stat="Top 500", evidence="Top 500 Schools of India",
                   label="Named among the Top 500 Schools of India"),
}

# 3 — counted, not claimed. One figure to a screen; the evidence is the phrase
#     in the record that holds it. "17" is the sum of the record's own 6 + 5 + 6.
COUNTED = [
    dict(stat="24 / 24", label="IB Diplomas", laurel="ib-2026", evidence="24 of 24 diplomas",
         note="Every candidate registered for the May 2026 IB Diploma examination was awarded "
              "the diploma."),
    dict(stat="45 / 45", label="Perfect scores", laurel="ib-2026", evidence="45 out of 45",
         note="Two students, the maximum the Diploma allows."),
    dict(stat="99.0%", label="Class XII Management", laurel="cbse-xii-management-2026",
         evidence="99.0%", note="The stream topper, in the CBSE board examinations."),
    dict(stat="17", label="Medals at South Zone Yoga", laurel="yoga-2025",
         evidence="6 gold, 5 silver, 6 bronze",
         note="Six gold, five silver and six bronze, with the Overall Championship."),
    dict(stat="14th", label="Year first in Tamil Nadu", laurel="ranking-2025",
         evidence="14th consecutive year",
         note="Education World ranked CIRS first in Tamil Nadu and Coimbatore for the 14th "
              "consecutive year."),
    dict(stat="100", label="The top 100 of one lakh", laurel="vssf-2025",
         evidence="top 100 of one lakh",
         note="Two students, selected through the SPOT test for the VSSF Science Camp."),
]

# 4 — the reel, oldest first: the milestones that have their own exhibit.
TUNNEL = ["kalam-2007", "khel-mela-2008", "isa-2011", "vision-award-2012", "brainfeed-2017",
          "ranking-2019", "yoga-2025", "ib-2026"]

# 5 — featured laurels, in the order the page has always given them. The first
#     is the last milestone of the reel, and the reel hands over to it.
#     (laurel, headline, template, stat, evidence)
FEATURES = [
    ("ib-2026", "Two perfect scores.", "full", "45 / 45", "45 out of 45"),
    ("yoga-2025", "Six gold. Five silver. Six bronze.", "right", None, None),
    ("football-u14-2025", "Champions of thirty-six schools.", "type", "36 schools", "36 schools"),
    ("quzbiz-2025", "One team from a hundred and eighty.", "wide", "1 of 180", "First of 180 teams"),
    ("bhajan-2025", "Ten voices, one first prize.", "centre", "10 voices", "Ten CIRS students"),
]


# ---------------------------------------------------------------------------
# Audit: the checks a reader would want made, run at every build.
# ---------------------------------------------------------------------------

def plain_text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def record_text(l):
    parts = [l["title"], l["event"], l["result"], l["text"]] + [n for n, _ in l["names"]]
    return plain_text(" ".join(parts)).lower()


def audit(root="."):
    """Returns (errors, warnings). An error stops the build."""
    import os
    errors, warns, pages = [], [], {}

    def page(href):
        p = href.split("#")[0]
        if p not in pages:
            if not os.path.exists(os.path.join(root, p)):
                pages[p] = None
            elif p.endswith(".html"):
                pages[p] = open(os.path.join(root, p), encoding="utf-8").read()
            else:
                pages[p] = ""          # a document: its existence is the check
        return pages[p]

    seen, titles = set(), {}
    for l in LAURELS:
        i = l["id"]
        if i in seen:
            errors.append((i, "duplicate id"))
        seen.add(i)
        t = plain_text(l["title"]).lower()
        if t in titles:
            errors.append((i, f"duplicate title with {titles[t]}"))
        titles[t] = i
        for k in ("title", "event", "result", "text", "when"):
            if not plain_text(l.get(k)):
                errors.append((i, f"empty {k}"))
        if not l["cats"]:
            errors.append((i, "no category"))
        for c in l["cats"]:
            if c not in CAT_NAME:
                errors.append((i, f"unknown category {c}"))
        h = page(l["source"][1])
        if h is None:
            errors.append((i, f"source missing: {l['source'][1]}"))
        elif "#" in l["source"][1] and l["source"][1].split("#")[0].endswith(".html") \
                and f'id="{l["source"][1].split("#")[1]}"' not in h:
            errors.append((i, f"source anchor missing: {l['source'][1]}"))
        if l["image"] and not os.path.exists(os.path.join(root, IMAGES[l["image"]][0])):
            errors.append((i, "image file missing"))
        if l["year"] is None:
            warns.append((i, "undated: kept out of the chronology"))
        if l["level"] is None:
            warns.append((i, "no level recorded"))

    def need(what, lid, phrase):
        l = BY_ID.get(lid)
        if l is None:
            errors.append((what, f"unknown laurel {lid}"))
        elif phrase.lower() not in record_text(l):
            errors.append((what, f"'{phrase}' is not in the record {lid}"))

    for shown, lid, ev, *_ in FRAGMENTS:
        need(f"fragment {shown}", lid, ev)
    for cat, d in LEADS.items():
        if cat not in CAT_NAME:
            errors.append((f"lead {cat}", "unknown category"))
        need(f"lead {cat}", d["laurel"], d["evidence"])
        need(f"lead {cat} label", d["laurel"], d["label"])
        if cat not in BY_ID[d["laurel"]]["cats"]:
            errors.append((f"lead {cat}", f"{d['laurel']} is not in that category"))
    for c in COUNTED:
        need(f"counted {c['stat']}", c["laurel"], c["evidence"])
    for lid in TUNNEL:
        l = BY_ID[lid]
        if not l["image"]:
            errors.append((f"reel {lid}", "a milestone needs its own exhibit"))
        if l["year"] is None:
            errors.append((f"reel {lid}", "undated"))
    years = [BY_ID[i]["year"] for i in TUNNEL]
    if years != sorted(years):
        errors.append(("reel", "not in chronological order"))
    for lid, _h, _t, stat, ev in FEATURES:
        if lid not in BY_ID:
            errors.append((f"feature {lid}", "unknown laurel"))
        elif stat:
            need(f"feature {lid}", lid, ev)
    for key in LG:
        if not os.path.exists(os.path.join(root, LG[key][0])):
            errors.append((f"scan {key}", "large scan missing"))
    if page(SCHOOL_OPENED[1]) is None or f'id="{SCHOOL_OPENED[1].split("#")[1]}"' not in page(SCHOOL_OPENED[1]):
        errors.append(("ending", f"anchor missing: {SCHOOL_OPENED[1]}"))
    for k, r in SEASON_PHOTOS.items():
        if not os.path.exists(os.path.join(root, SEASON_IMG, f"{k}-1600.jpg")):
            errors.append((f"season {k}", "image missing"))
    return errors, warns


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

ARROW = '<svg class="lr-icon" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M4 14 14 4M4 4h10v10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def plain(text):
    """Entity-laden HTML as the words it says, for an attribute."""
    return html.escape(html.unescape(re.sub(r"<[^>]+>", "", text)), quote=True)


def img_html(key, sizes, cls="", eager=False, lazy=True, large=False):
    path, w, h, alt, _cap, _ev = IMAGES[key]
    if large and key in LG:
        path, w, h = LG[key]
    klass = f' class="{cls}"' if cls else ""
    load = ' fetchpriority="high"' if eager else (' loading="lazy"' if lazy else "")
    return (f'<img{klass} src="{path}" width="{w}" height="{h}" alt="{plain(alt)}" '
            f'sizes="{sizes}"{load} decoding="async">')


def caption(key):
    return IMAGES[key][4]


def cats_label(l):
    return " &middot; ".join(CAT_NAME[c] for c in l["cats"])


def year_text(l):
    return str(l["year"]) if l["year"] else "Undated"


def source_kind(l):
    href = l["source"][1]
    if href.endswith(".pdf"):
        return "Annual report"
    return SOURCE_KINDS[href.split("#")[0]]


def source_link(l, cls="lr-src", cursor="view"):
    label, href = l["source"]
    ext = ' target="_blank" rel="noopener"' if href.endswith(".pdf") else ""
    return (f'<a class="{cls}" href="{href}"{ext} data-cursor="{cursor}" '
            f'aria-label="Source: {plain(label)}">{source_kind(l)} '
            f'<span aria-hidden="true">{ARROW}</span></a>')


def source_line(l):
    label, href = l["source"]
    ext = ' target="_blank" rel="noopener"' if href.endswith(".pdf") else ""
    return f'<p class="lr-srcline">Source: <a href="{href}"{ext}>{label}</a></p>'


def fit_var(text):
    return len(plain_text(text))


# ---- the seasons in photographs ------------------------------------------

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


# ---- 1: the opening --------------------------------------------------------

def hero_html():
    frags = []
    for shown, lid, _ev, depth, x, y, phone in FRAGMENTS:
        l = BY_ID[lid]
        frags.append(
            f'<li class="lr-frag lr-frag--{depth}{"" if phone else " lr-frag--wide"}" '
            f'style="--x:{x};--y:{y}"><span class="lr-frag__v">{shown}</span>'
            f'<span class="lr-frag__m">{year_text(l)} &middot; {CAT_NAME[l["cats"][0]]}</span></li>')
    return (
        '<div class="lr-hero" data-lr-hero>\n'
        '      <h1 class="lr-hero__h1" id="lr-title">'
        f'<span class="lr-hero__num" data-lr-num>{len(LAURELS)}</span> '
        '<span class="lr-hero__word" data-lr-word>Laurels</span></h1>\n'
        '      <p class="lr-hero__range" data-lr-range><span>Years of achievement at CIRS</span>'
        f'<b>{FIRST_YEAR}<i aria-hidden="true"> &rarr; </i><span class="sr-only"> to </span>{LAST_YEAR}</b></p>\n'
        '      <ul class="lr-frags" aria-hidden="true">' + "".join(frags) + '</ul>\n'
        '    </div>')


# ---- 2: many forms ---------------------------------------------------------

def journey_html():
    lis, index = [], []
    for i, (key, name) in enumerate(CATEGORIES):
        d = LEADS[key]
        l = BY_ID[d["laurel"]]
        n = sum(1 for x in LAURELS if key in x["cats"])
        media = ""
        if l["image"]:
            k = l["image"]
            kind = "doc" if k in DOCUMENTS else "photo"
            media = (f'<figure class="lr-cat__media is-{kind}">'
                     f'<div class="lr-cat__frame">{img_html(k, "(max-width: 899px) 86vw, 34vw")}</div>'
                     f'<figcaption>{caption(k)}</figcaption></figure>')
        stat = (f'<p class="lr-cat__stat" style="--len:{fit_var(d["stat"])}">{d["stat"]}</p>'
                if d["stat"] else "")
        lis.append(
            f'      <li class="lr-cat lr-cat--{[1, 4, 2, 3][i % 4]}{"" if l["image"] else " is-bare"}" '
            f'id="cat-{key}" data-cat="{key}" style="--len:{fit_var(name)}">\n'
            f'        <article aria-labelledby="cat-{key}-t">\n'
            f'          <p class="lr-cat__n" aria-hidden="true">{i + 1:02d}</p>\n'
            f'          <h3 class="lr-cat__name" id="cat-{key}-t">{name}</h3>\n'
            f'          {media}\n'
            f'          {stat}\n'
            f'          <div class="lr-cat__copy">\n'
            f'            <p class="lr-cat__label">{d["label"]}</p>\n'
            f'            <p class="lr-cat__title">{l["title"]}</p>\n'
            f'            <p class="lr-cat__meta">{l["event"]} &middot; {year_text(l)}</p>\n'
            f'            <p class="lr-cat__links">{source_link(l)}'
            f'<a class="lr-more" href="#archive" data-lr-filter="{key}" data-cursor="view">'
            f'All {n} in {name.lower()} <span aria-hidden="true">{ARROW}</span></a></p>\n'
            f'          </div>\n'
            f'        </article>\n'
            f'      </li>')
        index.append(f'<li><a href="#cat-{key}" data-go="{i}"><span>{i + 1:02d}</span><em>{name}</em></a></li>')
    return "\n".join(lis), "".join(index)


# ---- 3: counted, not claimed ----------------------------------------------

def counted_html():
    lis, ledger = [], []
    for i, c in enumerate(COUNTED):
        l = BY_ID[c["laurel"]]
        meta = l["event"] if l["when"].casefold() in l["event"].casefold() else f'{l["event"]} &middot; {l["when"]}'
        lis.append(
            f'      <li class="lr-stat" data-i="{i}" style="--len:{fit_var(c["stat"])}">\n'
            f'        <p class="lr-stat__fig">{c["stat"]}</p>\n'
            f'        <p class="lr-stat__label">{c["label"]}</p>\n'
            f'        <p class="lr-stat__meta">{meta}</p>\n'
            f'        <p class="lr-stat__note">{c["note"]}</p>\n'
            f'        <p class="lr-stat__src">{source_link(l)}</p>\n'
            f'      </li>')
        ledger.append(f'<li>{c["stat"]}<span> {c["label"]}</span></li>')
    return "\n".join(lis), "".join(ledger)


# ---- 4: the reel ------------------------------------------------------------

def tunnel_html():
    lis, rail = [], []
    n = len(TUNNEL)
    for i, lid in enumerate(TUNNEL):
        l = BY_ID[lid]
        k = l["image"]
        kind = "doc" if k in DOCUMENTS else "photo"
        big = LG.get(k, (IMAGES[k][0], IMAGES[k][1], IMAGES[k][2]))
        lis.append(
            f'      <li class="lr-ms lr-ms--{"a" if i % 2 == 0 else "b"} lr-ms--{kind}" id="ms-{lid}" data-i="{i}" '
            f'data-year="{l["year"]}">\n'
            f'        <article class="lr-ms__inner" aria-labelledby="ms-{lid}-t">\n'
            f'          <p class="lr-ms__year" aria-hidden="true">{l["year"]}</p>\n'
            f'          <figure class="lr-ms__media is-{kind}">\n'
            f'            <a class="lr-ms__open" data-cursor="open" href="{big[0]}" '
            f'data-large="{big[0]}" data-w="{big[1]}" data-h="{big[2]}" data-i="{i}" '
            f'aria-haspopup="dialog" aria-label="Look closely: {plain(caption(k))}">'
            f'<span class="lr-ms__frame" style="--ar:{IMAGES[k][1] / IMAGES[k][2]:.4f}">{img_html(k, "(max-width: 899px) 86vw, 40vw", lazy=i > 1)}</span>'
            f'</a>\n'
            f'            <figcaption>{caption(k)}</figcaption>\n'
            f'          </figure>\n'
            f'          <div class="lr-ms__copy">\n'
            f'            <p class="lr-ms__meta"><span>{cats_label(l)}</span><span>{l["when"]}</span></p>\n'
            f'            <h3 class="lr-ms__title" id="ms-{lid}-t">{l["title"]}</h3>\n'
            f'            <p class="lr-ms__event">{l["event"]}</p>\n'
            f'            <p class="lr-ms__text">{l["text"]}</p>\n'
            f'            <p class="lr-ms__src">{source_link(l)}</p>\n'
            f'          </div>\n'
            f'        </article>\n'
            f'      </li>')
        rail.append(f'<li style="--f:{i / (n - 1):.4f}"><button type="button" data-go="{i}" '
                    f'aria-label="Go to {l["year"]}: {plain(l["title"])}"><span>{l["year"]}</span>'
                    f'</button></li>')
    return "\n".join(lis), "".join(rail)


# ---- 5: featured -------------------------------------------------------------

def features_html():
    out = []
    for i, (lid, headline, tpl, stat, _ev) in enumerate(FEATURES):
        l = BY_ID[lid]
        words = headline.split(" ")
        title = " ".join(f'<span class="lr-line"><span style="--i:{j}">{w}</span></span>'
                         for j, w in enumerate(words))
        names = ""
        if l["names"]:
            names = ('<ul class="lr-feature__names">' + "".join(
                f'<li>{n}</li>' for n, _ in l["names"]) + '</ul>')
        fig = (f'<p class="lr-feature__stat" style="--len:{fit_var(stat)}">{stat}</p>' if stat else "")
        out.append(
            f'  <article class="lr-feature lr-feature--{tpl}" id="featured-{lid}" '
            f'aria-labelledby="feature-{lid}-title">\n'
            f'    <figure class="lr-feature__media">'
            f'<div class="lr-feature__frame">{img_html(l["image"], "100vw", eager=i == 0, lazy=i > 0)}</div>'
            f'<figcaption class="lr-feature__cap">{caption(l["image"])}</figcaption></figure>\n'
            f'    <div class="lr-feature__copy">\n'
            f'      <p class="lr-feature__index" aria-hidden="true">{i + 1:02d}</p>\n'
            f'      <p class="lr-feature__meta"><span>{cats_label(l)}</span><span>{l["when"]}</span></p>\n'
            f'      <h3 class="lr-feature__title" id="feature-{lid}-title" '
            f'aria-label="{plain(headline)}">{title}</h3>\n'
            f'      {fig}\n'
            f'      <p class="lr-feature__event">{l["event"]}</p>\n'
            f'      <p class="lr-feature__text">{l["text"]}</p>\n'
            f'      {names}\n'
            f'      <p class="lr-feature__src">{source_link(l)}</p>\n'
            f'    </div>\n'
            f'  </article>')
    return "\n".join(out)


# ---- 6: the archive ----------------------------------------------------------

def archive_filters_html():
    total = len(LAURELS)
    cats = [f'<li><button type="button" class="lr-cat-btn" data-cat="all" aria-pressed="true">'
            f'<span class="lr-cat-btn__n">00</span><span class="lr-cat-btn__name">All</span>'
            f'<span class="lr-cat-btn__c">{total}</span></button></li>']
    for i, (key, name) in enumerate(CATEGORIES, 1):
        n = sum(1 for l in LAURELS if key in l["cats"])
        cats.append(f'<li><button type="button" class="lr-cat-btn" data-cat="{key}" '
                    f'aria-pressed="false"><span class="lr-cat-btn__n">{i:02d}</span>'
                    f'<span class="lr-cat-btn__name">{name}</span>'
                    f'<span class="lr-cat-btn__c">{n}</span></button></li>')
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
        '      <ol class="lr-fcats" aria-label="Filter by field">\n        ' + "\n        ".join(cats) +
        '\n      </ol>\n'
        '      <div class="lr-opts">\n'
        '        <div class="lr-opts__group" role="group" aria-labelledby="lr-year-label">'
        '<span class="lr-opts__label" id="lr-year-label">Year</span>' + "".join(years) + '</div>\n'
        '        <div class="lr-opts__group" role="group" aria-labelledby="lr-level-label">'
        '<span class="lr-opts__label" id="lr-level-label">Level</span>' + "".join(levels) + '</div>\n'
        '      </div>\n'
        '    </div>')


def rows_html():
    out = []
    for l in LAURELS:
        names = ""
        if l["names"]:
            names = ('<ul class="lr-row__names">' + "".join(
                f'<li><b>{n}</b> {what}</li>' for n, what in l["names"]) + '</ul>')
        img = ""
        peek = ""
        if l["image"]:
            k = l["image"]
            src = IMAGES[k][0]
            peek = f' data-peek="{src}" data-peek-w="{IMAGES[k][1]}" data-peek-h="{IMAGES[k][2]}"'
            img = (f'<figure class="lr-row__fig"><div class="lr-row__frame">'
                   f'{img_html(k, "(max-width: 899px) 86vw, 30vw")}</div>'
                   f'<figcaption>{caption(k)}</figcaption></figure>')
        q = plain_text(" ".join([l["title"], l["result"], l["event"], l["text"], cats_label(l),
                                 l["when"]] + [n for n, _ in l["names"]])).lower()
        out.append(
            f'      <li class="lr-row" id="laurel-{l["id"]}" data-cats="{" ".join(l["cats"])}" '
            f'data-level="{l["level"] or ""}" data-year="{l["year"] or "undated"}" '
            f'data-q="{html.escape(q, quote=True)}"{peek}>\n'
            f'        <div class="lr-row__line">\n'
            f'          <h3 class="lr-row__h"><button type="button" class="lr-row__btn" '
            f'aria-expanded="false" aria-controls="row-{l["id"]}" data-cursor="view">'
            f'<span class="lr-row__year">{year_text(l)}</span>'
            f'<span class="lr-row__title">{l["title"]}<small class="lr-row__result">{l["result"]}</small></span>'
            f'<span class="lr-row__cat">{CAT_NAME[l["cats"][0]]}</span>'
            f'<span class="lr-row__plus" aria-hidden="true"></span></button></h3>\n'
            f'          {source_link(l, "lr-row__src")}\n'
            f'        </div>\n'
            f'        <div class="lr-row__panel" id="row-{l["id"]}" hidden>\n'
            f'          <div class="lr-row__body">\n'
            f'            <p class="lr-row__meta">{cats_label(l)}'
            f'{" &middot; " + LEVEL_NAME[l["level"]] if l["level"] else ""} &middot; {l["when"]}</p>\n'
            f'            <p class="lr-row__event">{l["event"]}</p>\n'
            f'            <p class="lr-row__text">{l["text"]}</p>\n'
            f'            {names}\n'
            f'            {source_line(l)}\n'
            f'          </div>\n'
            f'          {img}\n'
            f'        </div>\n'
            f'      </li>')
    return "\n".join(out)


# ---- 7: the names ------------------------------------------------------------

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


def chapters_html():
    """Selected introductions only; every source record remains in the full archive."""
    photos = {"academics":"ib-lab", "sport":"football", "arts":"ensemble",
              "speech":"mun", "innovation":"expo", "leadership":"elections",
              "international":"isa", "school":"vision"}
    links, chapters = [], []
    for n, (key, name) in enumerate(CATEGORIES, 1):
        links.append(f'<a href="#achievement-{key}"><span>{n:02d}</span> {name}</a>')
        records = [l for l in LAURELS if key in l["cats"]][:3]
        stories = []
        for l in records:
            names = ''.join(f'<li><strong>{person}</strong> — {result}</li>' for person,result in l["names"])
            names = f'<ul>{names}</ul>' if names else ''
            stories.append(f'<details><summary>{l["title"]}</summary><p class="rd-laurel__date">{l["when"]} · {l["event"]}</p><p><strong>{l["result"]}</strong></p><p>{l["text"]}</p>{names}{source_line(l)}<a href="#laurel-{l["id"]}">Read the archive entry</a></details>')
        photo = photos[key]
        note = '' if IMAGES[photo][5] else '<p class="rd-laurel__photo-note">A related CIRS photograph; it does not document the listed award events.</p>'
        chapters.append(f'<section class="rd-laurel" id="achievement-{key}" aria-labelledby="achievement-title-{key}"><header><span id="cat-{key}" aria-hidden="true"></span><span id="cat-{key}-t" aria-hidden="true"></span><p>{n:02d} / 08</p><h2 id="achievement-title-{key}">{name}</h2></header><div class="rd-laurel__layout"><figure>{img_html(photo,"(max-width:999px) 86vw, 46vw")}<figcaption>{caption(photo)}{note}</figcaption></figure><div class="rd-laurel__stories">{"".join(stories)}<a class="rd-laurel__all" href="#archive">Explore the complete archive <svg class="lr-icon" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M9 3v12m-5-5 5 5 5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a></div></div></section>')
    notes = ''.join(f'<li><h3>{name}</h3><p>{LEADS[key]["label"]}</p>{source_line(BY_ID[LEADS[key]["laurel"]])}</li>' for key,name in CATEGORIES)
    context = '<details class="rd-laurels-context"><summary id="lr-forms-title">Excellence has many forms.</summary><ul>'+notes+'</ul></details>'
    return '<div class="rd-laurels" id="achievement-chapters" data-rd-chapters><nav class="rd-laurels__index" aria-label="Achievement chapters">'+''.join(links)+'</nav>'+''.join(chapters)+context+'</div>'


def expand(content):
    errors, warns = audit()
    if errors:
        raise SystemExit("laurels audit failed:\n" + "\n".join(f"  {a}: {b}" for a, b in errors))
    names, count = names_html()
    cats, cat_index = journey_html()
    stats, ledger = counted_html()
    ms, rail = tunnel_html()
    units = 2.0 + 0.85 * len(CATEGORIES)
    return (content.replace("{{LAURELS_CHAPTERS}}", chapters_html())
                   .replace("{{LAURELS_HERO}}", hero_html())
                   .replace("{{LAURELS_CATEGORIES}}", cats)
                   .replace("{{LAURELS_CAT_INDEX}}", cat_index)
                   .replace("{{LAURELS_CAT_UNITS}}", f"{units:.2f}")
                   .replace("{{LAURELS_STATS}}", stats)
                   .replace("{{LAURELS_LEDGER}}", ledger)
                   .replace("{{LAURELS_MILESTONES}}", ms)
                   .replace("{{LAURELS_RAIL}}", rail)
                   .replace("{{LAURELS_MILESTONE_N}}", str(len(TUNNEL)))
                   .replace("{{LAURELS_FEATURES}}", features_html())
                   .replace("{{LAURELS_FILTERS}}", archive_filters_html())
                   .replace("{{LAURELS_ROWS}}", rows_html())
                   .replace("{{LAURELS_SEASON}}", season_html())
                   .replace("{{LAURELS_NAMES}}", names)
                   .replace("{{LAURELS_NAME_COUNT}}", str(count))
                   .replace("{{LAURELS_COUNT}}", str(len(LAURELS)))
                   .replace("{{LAURELS_FIRST}}", str(FIRST_YEAR))
                   .replace("{{LAURELS_LAST}}", str(LAST_YEAR))
                   .replace("{{LAURELS_OPENED}}", SCHOOL_OPENED[0])
                   .replace("{{LAURELS_OPENED_HREF}}", SCHOOL_OPENED[1]))


if __name__ == "__main__":
    print(f"{len(LAURELS)} laurels, {FIRST_YEAR}-{LAST_YEAR}, {len(YEARS)} years: "
          f"{', '.join(map(str, sorted(YEARS)))}")
    for c, name in CATEGORIES:
        print(f"  {name:14} {sum(1 for l in LAURELS if c in l['cats'])}")
    errors, warns = audit()
    print(f"\naudit: {len(errors)} errors, {len(warns)} notes")
    for a, b in errors:
        print(f"  ERROR  {a}: {b}")
    for a, b in warns:
        print(f"  note   {a}: {b}")
    print(f"  {sum(1 for l in LAURELS if not l['image'])} of {len(LAURELS)} records have no image "
          f"(typography carries them)")
    print("\nHeld back:")
    for what, why in HELD:
        print(f"  - {what}: {why}")
