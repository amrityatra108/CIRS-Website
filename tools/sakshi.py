#!/usr/bin/env python3
"""Chinmaya Sakshi, the Anand Utsav Bulletin of October 2026.

Sakshi is the school's own newsletter. The October 2026 issue is a 26-page
Canva design the school exported as a PDF; it is not in the repository. This
module records what the issue says and builds two things from it:

  * the News page's "From the school's bulletin" section and one article page
    for each story, written from ARTICLES below;
  * the Student Council's pledges, written from GROUPS below, which the
    Student Life, Spiritual Life, Sports and Houses pages each print for the
    group whose page it is.

The rule is the one the rest of the site keeps: nothing is added. Every
paragraph is the school's own, taken from the issue and reproduced whole, and
every pledge is the students' own words, unedited. Only slips of typing are
corrected, and they are listed here so that nothing is corrected quietly:

  * the Deans' pledge prints "contributeto it"; it reads "contribute to it";
  * the Sports Secretaries' pledge prints "student ,not"; it reads "student,
    not";
  * straight quotation marks become curly ones, and the names are set in
    ordinary capitals where the issue prints them in small capitals.

Where the issue is silent, so is the site:

  * The issue does not give the year of its festivals; they are the festivals
    of the year it reports, and the years given here are the ones its own
    dates carry (Ram Navami is printed "27 March 2026"). India Week, Seva Week
    and Management Week carry no dates in the issue, and say so.
  * The Champion Cup football tournament is printed "3rd May 2025", a year
    before every other match in the issue. It is reproduced as printed.
  * The Cultural Secretaries' pledge is not headed by its group. It stands in
    that group's block on the page, beside their photograph and heading, in
    the same way that each other group's pledge stands beside its own.
  * The bulletin's own heading for the Deans is "School Deans"; their pledge
    calls them "Student Deans". The heading is used for the role, and the
    pledge is left as they wrote it.
  * The council's page headings read "Council 2025-26" in one hidden layer of
    the design and "Council 2026-27" everywhere it shows. 2026-27 is used,
    which is also what the cover and the contents say.

The photographs are the issue's own, taken from the PDF as the image objects
that were placed on its pages, so they are at the resolution the school
supplied. tools/make-sakshi.py cuts them into assets/img/news/sakshi/ and,
for the council, assets/img/council/. Each is named below by page and object
number. Group photographs are captioned with the order the names stand in on
the issue's own page; nobody is named from a face.

    slug        the page it becomes, <slug>.html
    section     the News archive's filter category
    group       the heading it stands under in the bulletin section
    date        as it reads; datetime, machine-readable; undated, if the
                issue gives no date, in which case the date is not a <time>
    dek         the one-line summary
    who         who or what it concerns, for the article's rail
    blocks      ("h", heading), ("p", paragraph), ("ul", [lines]),
                ("html", markup) and ("fig", n), in order; ("fig", n) puts
                photograph n (1 is the lead) into the text at that point
    photos      (page, xref, alt) in the PDF; the first leads
    lead        True for the three stories that open the section
"""
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = "assets/img/news/sakshi"
COUNCIL_DIR = "assets/img/council"

ISSUE = "Chinmaya Sakshi"
ISSUE_LINE = "Anand Utsav Bulletin, October 2026"
COUNCIL_YEARS = "2026–27"

# ---------------------------------------------------------------------------
# The Student Council, 2026-27
#
# One entry per group that has a pledge. "names" are in the order the issue's
# own page places them, left to right along the photograph: each label sits
# above or below the person it names, and the order was read from where the
# labels stand. "page" is where the pledge is printed on this site, and
# "anchor" the id it carries there.
# ---------------------------------------------------------------------------
GROUPS = {
    "deans": {
        "role": "School Deans",
        "short": "School Deans",
        "names": ["Aarav Ashish Bhartia", "Rhea Sontakke"],
        "photo": (6, 2233),
        "alt": "The two School Deans of the Student Council 2026–27 standing side by side among green plants",
        "page": "the-cirs-experience.html",
        "anchor": "deans-pledge",
        "pledge": [
            "Inspired by Gurudev’s vision, of “Spreading Maximum Happiness to Maximum People for The "
            "Maximum Amount of Time,” we, the Student Deans of CIRS 2026 - 27, aspire to contribute to it. "
            "Our aim is to transform ourselves and our fellow students into strong, capable and cultured "
            "individuals. We shall not fear to stand for Dharma and shall work together to safeguard the "
            "glory of Bharat with our dynamic spirituality.",
        ],
    },
    "cultural": {
        "role": "Cultural Secretaries",
        "short": "Cultural Secretaries",
        "names": ["Viraj Vijaykumar Lal", "Ritika Deorah", "Veer Srimal", "Aradhya Ashish Saraf"],
        "photo": (7, 2259),
        "alt": "The four Cultural Secretaries of the Student Council 2026–27 standing in a row before green shrubs",
        "page": "spiritual-life.html",
        "anchor": "cultural-pledge",
        "pledge": [
            "As the proud representatives of the CIRS student body, we dedicate ourselves to building the next "
            "generation of leaders. We believe that every individual has unique strengths, and when brought "
            "together, they become the foundation for the growth and glory of our school. With empathy in our "
            "hearts and strength in our character, we strive to remain rooted in discipline, committed to "
            "merit, and willing to sacrifice for the greater good. Guided by the vision of our Pujya Gurudev, "
            "we pledge to serve as role models and give our best in every endeavour by transforming "
            "challenges into opportunities for excellence.",
        ],
    },
    "sports": {
        "role": "Sports Secretaries",
        "short": "Sports Secretaries",
        "names": ["Divyam Gupta", "Sahana Harihara", "Deepika S", "S Aaryan"],
        "photo": (7, 2262),
        "alt": "The four Sports Secretaries of the Student Council 2026–27 standing in a row on a brick path in the garden",
        "page": "sports.html",
        "anchor": "sports-pledge",
        "pledge": [
            "To honour the spirit of sports is to nurture sportsmanship in every student, not just in playing, "
            "but in believing. We commit ourselves to bringing out the best in each player, not by pushing "
            "them toward the podium, but by helping them discover the ache of a hard practice, the thrill of "
            "a comeback, and the trust that holds a team together. Because a first serve mastered after weeks "
            "of failing means more than a medal, and a teammate’s hand pulling you up means more than "
            "any record.",
            "Sport is the one hour in school when pressure feels like freedom, when we run until our lungs "
            "burn, scream till our voices break, and for once, no one tells us to keep it down. No rules "
            "holding us back, no one watching the clock.",
            "Just us, our team, and the game we’d choose again and again.",
        ],
    },
    "valmiki": {
        "role": "Valmiki House Captains",
        "short": "Valmiki",
        "names": ["Muhil T", "Sannvi Bagaria", "Aryaman Ashish Saraf", "Yuvika Agarwal"],
        "photo": (8, 2277),
        "alt": "The four Valmiki House Captains of the Student Council 2026–27 standing in a row beside a lake",
        "page": "houses.html",
        "anchor": "pledge-valmiki",
        "pledge": [
            "We march forward with our heads and flags held high. The sacred yellow brings not only joy to our "
            "hearts but also dynamism to our souls. We stand as one united by the spirit of optimism, carrying "
            "forward all our duties with respect and achievements with humility. Leading this house means more "
            "than just fulfilling our responsibilities but also learning, failing and growing from all our "
            "mistakes while celebrating our triumphs. Thanks to our ever-smiling house masters, Smt Rashmi P & "
            "Smt Sreedevi C, we take up every endeavour with positivity and do everything with absolute "
            "dedication. Throughout the following year we will continue the legacy of this resilient "
            "house—bound by togetherness, unwavering in heart. Vamos Valmiki!",
        ],
    },
    "vasishtha": {
        "role": "Vasishta House Captains",
        "short": "Vasishta",
        "names": ["Adhyatma Ghranthik Agarwal", "Adhvika K", "S Rithesh", "Haasini Anandhan"],
        "photo": (8, 2280),
        "alt": "The four Vasishta House Captains of the Student Council 2026–27 standing in a row before green shrubs",
        "page": "houses.html",
        "anchor": "pledge-vasishtha",
        "pledge": [
            "We proudly carry the fiery flag of the red house as Vasishta blazes forward with an unstoppable "
            "force fueled by an imperishable spirit and a persistent drive to conquer every obstacle. The sage "
            "Vasishta stands as the symbol of supreme spiritual wisdom and total mastery of the mind and "
            "senses. Pujya Gurudev’s teachings brighten our path through the darkness, just as our maroon "
            "red represents the beating heart of our passion, persistence, and courage. With Gurudev’s "
            "blessings, no challenge is too hard and no hurdle too high. We are a wildfire of determination, "
            "destined to rise, conquer, and leave our mark—for we are Vasishta, the eternal house of the "
            "flame.",
        ],
    },
    "vyasa": {
        "role": "Vyasa House Captains",
        "short": "Vyasa",
        "names": ["Krishnav Deorah", "Harshita Bondia", "Shubham R Velani", "Anokhi Kankani"],
        "photo": (9, 2296),
        "alt": "The four Vyasa House Captains of the Student Council 2026–27 standing in a row before green shrubs",
        "page": "houses.html",
        "anchor": "pledge-vyasa",
        "pledge": [
            "We draw our energy from the vast, deep ocean we represent. Wearing our blue with pride, we are a "
            "family defined by our resilience. We promise to face the year ahead by sticking together and "
            "taking on challenges head-on. Just like the tide, we keep moving forward, ready to adapt, "
            "regroup, and bounce back stronger whenever we fall. With quiet confidence and shared drive, we "
            "are here to lift each other up. Marching forward together, we will give it our all to keep the "
            "Blue flag flying high.",
        ],
    },
    "vishwamitra": {
        "role": "Vishwamitra House Captains",
        "short": "Vishwamitra",
        "names": ["Riishvanth P", "Shagun Parmanandka", "Mahir Sunil Bera", "Kavya Arun Prasad"],
        "photo": (9, 2299),
        "alt": "The four Vishwamitra House Captains of the Student Council 2026–27 standing in a row before green shrubs",
        "page": "houses.html",
        "anchor": "pledge-vishwamitra",
        "pledge": [
            "Vishwamitra is the perfect mixture of responsibility and amusement. It has made us realize that a "
            "house is made of 154 members and loads of talent, but it becomes a home made of laughter, tears "
            "and comfort. We have grown through countless failures and unforgettable accomplishments. Each "
            "year, we have overcome all our differences and carry a sense of pride in the green. This year we "
            "pledge to continue to give it our all and take this green to greater heights. Not just by "
            "perseverance but also with love and strength, we make every opportunity, moment and goal worth "
            "it.",
        ],
    },
}

# The whole council, from the issue's group photograph (page 6).
COUNCIL_GROUP = {
    "photo": (6, 2236),
    "alt": "The Student Council 2026–27 standing in rows on the steps of a school building, "
           "in sashes over school uniform, with a swami in saffron among them",
}

HOUSE_SLUGS = ["vasishtha", "valmiki", "vishwamitra", "vyasa"]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def webp_size(path):
    """Width and height from a WebP header, so the build needs no imaging library."""
    with open(os.path.join(ROOT, path), "rb") as f:
        head = f.read(30)
    kind = head[12:16]
    if kind == b"VP8 ":
        w, h = struct.unpack("<HH", head[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if kind == b"VP8L":
        b = head[21:25]
        w = 1 + (((b[1] & 0x3F) << 8) | b[0])
        h = 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
        return w, h
    if kind == b"VP8X":
        w = 1 + int.from_bytes(head[24:27], "little")
        h = 1 + int.from_bytes(head[27:30], "little")
        return w, h
    raise ValueError(f"not a WebP: {path}")


def council_path(key, width):
    return f"{COUNCIL_DIR}/{key}-{width}.webp"


def council_image(key, alt, sizes, eager=False):
    """A council photograph, in the two widths tools/make-sakshi.py cuts."""
    big = council_path(key, 1600)
    small = council_path(key, 800)
    w, h = webp_size(big)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{big}" srcset="{small} 800w, {big} 1600w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{esc(alt)}" decoding="async" {load}>')


def _join_names(names):
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def pledge_html(key, sizes="(max-width: 820px) 100vw, 44vw", level=3, extra=""):
    """One group's pledge: its photograph, and its words set large.

    The pledge is a first-person statement by the students named under it, so
    it is a quotation and is marked up as one, and the figcaption names who
    is speaking and in what role. The heading names the group. What is shown
    is exactly GROUPS[key]["pledge"]; nothing is shortened for the layout.
    """
    g = GROUPS[key]
    heading = f"h{level}"
    tid = f"cp-{key}-title"
    quote = "\n".join(f"          <p>{esc(p)}</p>" for p in g["pledge"])
    names = "".join(f"<li>{esc(n)}</li>" for n in g["names"])
    photo = council_image(key, g["alt"], sizes)
    cls = f"cp cp--{key}" + (f" {extra}" if extra else "")
    return f'''<article class="{cls}" id="{g["anchor"]}" aria-labelledby="{tid}" data-pledge="{key}">
  <figure class="cp__photo">
    {photo}
    <figcaption>From left: {esc(_join_names(g["names"]))}.</figcaption>
  </figure>
  <div class="cp__voice">
    <p class="cp__eyebrow">Student Council {COUNCIL_YEARS}</p>
    <{heading} class="cp__role" id="{tid}">{esc(g["role"])}</{heading}>
    <figure class="cp__pledge">
      <blockquote>
{quote}
      </blockquote>
      <figcaption>
        <ul class="cp__names" aria-label="{esc(g["role"])}">{names}</ul>
        <span class="cp__tag">{esc(g["role"])}, Student Council {COUNCIL_YEARS}</span>
      </figcaption>
    </figure>
  </div>
</article>'''


# ---------------------------------------------------------------------------
# The stories
# ---------------------------------------------------------------------------
ARTICLES = [
    # ------------------------------------------------------------- leads
    {
        "slug": "cfore-school-excellence-award-2026",
        "title": "Cfore School Excellence Award 2026",
        "section": "Achievements",
        "group": "Anand Utsav 2026",
        "date": "22–23 September 2026",
        "datetime": "2026-09-22",
        "lead": True,
        "dek": "CIRS is ranked third in India and first in Coimbatore among India’s Best Residential Co-Ed Schools (Indian Curriculum).",
        "who": "The whole school",
        "photos": [
            (4, 2126, "A woman in a sari holding a trophy on the stage of the Cfore School Rankings 2026 event, between two men"),
        ],
        "blocks": [
            ("p", "We are extremely happy to share that Chinmaya International Residential School, Coimbatore, has been honoured with the prestigious Cfore School Excellence Award 2026, securing the 3rd Rank in India and the 1st Rank in Coimbatore in the category of India’s Best Residential Co-Ed Schools (Indian Curriculum)."),
            ("p", "On behalf of CIRS, Smt. Saranya C., Deputy Headmistress, received the award at the Cfore School Rankings 2026 event held in New Delhi on 22 and 23 September 2026."),
            ("p", "This recognition is a moment of great pride for the entire CIRS family. It celebrates our continued commitment to academic excellence, holistic education and the all-round development of our students. We are grateful to our students, faculty, staff and parents whose collective efforts continue to make CIRS a place of learning, growth and excellence."),
        ],
    },
    {
        "slug": "student-council-2026-27",
        "title": "The Student Council 2026–27",
        "section": "Campus",
        "group": "Anand Utsav 2026",
        "date": "3 August 2026",
        "datetime": "2026-08-03",
        "lead": True,
        "dek": "The new School Council leaders received their badges at the Investiture Ceremony on Gurudev Aaradhana, and each group of the council has written its pledge.",
        "who": "The Student Council",
        "photos": [
            (6, 2236, COUNCIL_GROUP["alt"]),
        ],
        "blocks": [
            ("p", "For students at CIRS, 3 August was a day of remembrance, responsibility and reflection as we honoured the Maha Samadhi of Pujya Swami Chinmayananda and welcomed the new School Council leaders. The day commenced with Guru Paduka Puja, followed by Atma Nivedanam, the Investiture Ceremony, where leaders received badges from the Principal, Smt. Rajeshwari, and Headmaster, Sri Ganesh."),
            ("h", "The pledges"),
            ("p", "The October 2026 bulletin prints a pledge from each group of the Student Council 2026–27, under the heading We Pledge. Each is printed in full, in the students’ own words, on the page of the school where that group’s work belongs."),
            ("html", "<ul class=\"art__links\">"
                     "<li><a href=\"the-cirs-experience.html#student-council\">The School Deans</a>, on The CIRS experience</li>"
                     "<li><a href=\"spiritual-life.html#cultural-secretaries\">The Cultural Secretaries</a>, on Spiritual Life</li>"
                     "<li><a href=\"sports.html#secretaries\">The Sports Secretaries</a>, on Our Sports</li>"
                     "<li>The House Captains, each on the page of their own house: "
                     "<a href=\"houses.html#pledge-vasishtha\">Vasishta</a>, "
                     "<a href=\"houses.html#pledge-valmiki\">Valmiki</a>, "
                     "<a href=\"houses.html#pledge-vishwamitra\">Vishwamitra</a> and "
                     "<a href=\"houses.html#pledge-vyasa\">Vyasa</a>, on Our Houses</li>"
                     "</ul>"),
            ("html", "<p>The bulletin’s account of the day, with its photographs: <a href=\"gurudev-aaradhana-2026.html\">Gurudev Aaradhana</a>.</p>"),
        ],
    },
    {
        "slug": "ganesh-chaturthi-2026",
        "title": "Ganesh Chaturthi: ten days with Ganapati Bappa",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "14–25 September 2026",
        "datetime": "2026-09-14",
        "lead": True,
        "dek": "Decorated stages, rangolis, daily pujas and grade-wise programmes, ending with the Visarjan procession to the school lake.",
        "who": "The whole school",
        "photos": [
            (14, 2480, "A decorated Ganesh murti carried through a crowd of students and staff"),
            (14, 2489, "Two boys at a lectern before a decorated Ganesh backdrop"),
            (14, 2483, "A girl in a red dress dancing with her arms raised in front of a festival backdrop"),
        ],
        "blocks": [
            ("p", "On 14th September, CIRS welcomed Ganapati Bappa for ten days of devotion, creativity and togetherness. The celebrations featured beautifully decorated stages, vibrant rangolis, daily pujas and grade-wise programmes that brought the spirit of Ganesh Chaturthi alive. The festivities culminated on 25th September with the Visarjan procession. Singing and chanting together, students accompanied Bappa to the school lake for immersion. As we bid Him farewell, we reflected on life’s transient nature and the importance of living with wisdom, goodness and purpose."),
        ],
    },
    # ------------------------------------------------------ Anand Utsav 2026
    {
        "slug": "directors-message-october-2026",
        "title": "A message from the Director",
        "section": "Campus",
        "group": "Anand Utsav 2026",
        "date": "Bulletin of October 2026",
        "datetime": "2026-10",
        "undated": True,
        "dek": "In the 75th year of Chinmaya Mission, Smt. Shanti Krishnamurthy writes to the children and parents of CIRS.",
        "who": "Smt. Shanti Krishnamurthy, Director – Academics & Administration",
        "photos": [],
        "blocks": [
            ("p", "Hari Om! Namaste!"),
            ("p", "As we celebrate the 75th year of Chinmaya Mission, we look back with deep gratitude at a remarkable journey inspired by the vision of Pujya Swami Chinmayananda. Among Gurudev’s many dreams was the vision of a residential school where education would go beyond the classroom—where children would learn, grow, discover themselves and imbibe the values of our rich cultural heritage while living in an atmosphere of discipline, affection and fellowship. Chinmaya International Residential School is a beautiful manifestation of that dream."),
            ("p", "Today, CIRS stands among the leading schools in the country and has now been recognised as No. 1 in India in the Premier League among the top Co-Ed Boarding Schools. This is a moment of great pride for the entire Chinmaya family. More importantly, it is a reminder of how far Gurudev’s vision has travelled—from a dream in his heart to an institution that continues to inspire young lives and set high standards in education."),
            ("p", "Dear Children, you are the inheritors of Gurudev’s vision. Your achievements, your character and the way you contribute to society will be the true measure of the legacy that Gurudev wanted to establish. We are grateful to our dear parents for entrusting their children to an institution that seeks to nurture not merely capable minds, but strong character and meaningful lives."),
            ("p", "May the vision and blessings of Pujya Gurudev continue to guide CIRS, and may every student who passes through its portals carry the light of Chinmaya wherever life takes them."),
            ("p", "Hari Om!"),
            ("p", "Shanti Krishnamurthy, Director – Academics & Administration"),
        ],
    },
    {
        "slug": "anand-utsav-2026-schedule",
        "title": "Anand Utsav 2026: the schedule",
        "section": "Campus",
        "group": "Anand Utsav 2026",
        "date": "5–7 October 2026",
        "datetime": "2026-10-05",
        "dek": "Three days on campus: Parent–Teacher meetings, the exhibitions, the Annual Day programme and the Matru-Pitru Aradhana.",
        "who": "Parents and students",
        "photos": [],
        "blocks": [
            ("p", "The schedule of Anand Utsav 2026, as printed in the October 2026 bulletin. Times and venues are the school’s."),
            ("h", "Monday, 5 October 2026"),
            ("ul", [
                "1.00 p.m. – CIRS Gates Open",
                "1.00 p.m. – Registration and Welcome (Chinmaya Vraja)",
                "1.30 p.m. – Flag Hoisting & Inauguration of Anand Utsav 2026 (Front of school Block)",
                "2.00 p.m. – 5:30 p.m. – Sessions I, II & III of Parent–Teacher Meeting; Projects and Exhibitions by students (as per the appointment schedule)",
                "3:30 p.m. – Tea (Academic Block)",
                "3.30 p.m. – 4.15 p.m. – Session by our CIRS Guidance Counselor, for the parents of classes 11 and 12 (MPH)",
                "6:15 p.m. – To be seated in the New Auditorium (Chinmaya Vraja)",
                "6:45 p.m. – 8.15 p.m. – Address to parents by Pujya Swami Anukoolanandaji, Residential Director, CIRS; Award Distribution Ceremony (Chinmaya Vraja)",
                "8:15 p.m. – 9:00 p.m. – Dinner (Hockey Court)",
                "9:30 p.m. – CIRS Gates Close",
            ]),
            ("h", "Tuesday, 6 October 2026"),
            ("ul", [
                "8:45 a.m. – CIRS Gates open",
                "9:00 a.m. – 1:30 p.m. – Sessions IV, V, and VI of Parent–Teacher Meeting; Exhibitions continue (as per the appointment schedule)",
                "10:30 a.m. – 11:00 a.m. – Tea (Academic Blocks)",
                "1:30 p.m. – 2:30 p.m. – Lunch (boys and their parents in the Dining Hall; girls and their parents in the MPH)",
                "2:30 p.m. – 4:30 p.m. – Session VII of Parents – RHP Meeting, in the respective Dorms; Exhibitions close at 2:30 pm",
                "Director’s address, in the AV Room – 2:30 to 3 pm for grade 9 parents; 3:15 to 3:45 pm for grade 10 parents",
                "4:00 p.m. – 4:30 p.m. – Tea (in front of the Dorms)",
                "4:30 p.m. – 5:30 p.m. – Rest and getting ready (Dorm of your ward)",
                "5:45 p.m. – Parents to be seated (Chinmaya Vraja)",
                "6:00 p.m. – 8:30 p.m. – Annual Day Program: Annual Report, Felicitation, Cultural Program (Chinmaya Vraja)",
                "8:30 p.m. – Dinner (Hockey Court)",
                "9:30 p.m. – CIRS Gates Close",
            ]),
            ("h", "Wednesday, 7 October 2026"),
            ("ul", [
                "7:15 a.m. – CIRS Gates open before breakfast",
                "8:00 a.m. – 9:15 a.m. – Matru-Pitru Aradhana & Valedictory function; parents report directly to the New Auditorium (Chinmaya Vraja)",
                "9:15 a.m. – 10.00 a.m. – Breakfast (Dining Hall / MPH)",
                "10.00 a.m. – 12 noon – Sessions VIII and IX of Parent–Teacher Meeting (as per the appointment schedule)",
                "11:00 a.m. – High Tea (Academic Blocks)",
                "12 noon – CIRS Gates Open for Departure; students accompany their parents",
            ]),
        ],
    },
    {
        "slug": "vidya-vaibhav-2026",
        "title": "Vidya Vaibhav: the projects for Anand Utsav 2026",
        "section": "Academics",
        "group": "Anand Utsav 2026",
        "date": "5–7 October 2026",
        "datetime": "2026-10-05",
        "dek": "Ten projects by departments and classes, each with its room, for the exhibitions of Anand Utsav.",
        "who": "Departments and Classes 5 to 8",
        "photos": [],
        "blocks": [
            ("p", "Vidya Vaibhav is the bulletin’s list of the projects that departments and classes will show at Anand Utsav 2026, with the room each is in and the school’s own synopsis of it."),
            ("h", "Dept. of Languages: “Living in Awareness – Chinmayam”"),
            ("html", "<p><strong>Venue:</strong> Room No 23</p>"),
            ("p", "The project explores how the rich literary traditions of Hindi, Sanskrit, Tamil, and French languages awaken young minds to values, culture, spirituality, and conscious living. The project aims to show that language is not merely a means of communication, but a powerful pathway to self-awareness, wisdom, and harmonious living. Through literature, we seek to inspire the youth to think consciously, act wisely, and live meaningfully."),
            ("h", "Dept. of Mathematics: “Where Mathematics, Logic, Games and Culture Meet!”"),
            ("html", "<p><strong>Venue:</strong> Math Lab</p>"),
            ("p", "The Maths Department will showcase how games make mathematics engaging while developing logical reasoning, strategic thinking, problem-solving, and pattern recognition. With a special focus on Indian traditional games and Indian Knowledge Systems (IKS), the project will use interactive and hands-on activities to help visitors play, think, and discover the mathematics hidden in games."),
            ("h", "Dept. of Science: “My Home, My Laboratory”"),
            ("html", "<p><strong>Venue:</strong> Physics Lab</p>"),
            ("p", "Science is not confined to laboratories—it is present in every corner of our homes. This exhibition explores how Physics, Chemistry, and Biology work together in everyday life, from household appliances and kitchen processes to food, cleaning products, cosmetics, human health, smart home and sustainable living, revealing the science behind familiar experiences."),
            ("h", "Dept. of Social Science: “Life-Line of Bharat”"),
            ("html", "<p><strong>Venue:</strong> Room No 7</p>"),
            ("p", "This project explores the role of geography in promoting unity in diversity and to understand how Geography has shaped the evolution of civilization in Bharat through historical, cultural and environmental perspectives. The project explores how the mountains, rivers, deserts and trade routes impact the culture and national identity."),
            ("h", "Dept. of Management: “Learn, Lead, & Serve-Young Entrepreneurs with a Purpose”"),
            ("html", "<p><strong>Venue:</strong> Room No 17, Chemistry Lab &amp; Biology Lab</p>"),
            ("p", "This project provides Management students with hands-on experience in planning, marketing, sales and financial management, while fostering responsible and socially conscious entrepreneurship. Through the Exhibition-cum-Sale, students learn that entrepreneurship is not merely about profit, but about creating value and making a difference to support the underprivileged with the profits earned, while Chinmaya CORD’s handmade products will promote entrepreneurship skills at the grassroot level."),
            ("h", "Classes 5 and 6: “Uddhared Ātmanātmānam – Rise by Your Own Self”"),
            ("html", "<p><strong>Venue:</strong> Room No 1</p>"),
            ("p", "This project introduces the foundational teaching of self-effort and self-mastery. Through the śloka Uddhared ātmanātmānam, students explore how their thoughts, choices and actions shape their lives. The project encourages them to recognise the mind as both a potential friend and an obstacle, and to develop qualities such as self-discipline, positive thinking, responsibility and perseverance."),
            ("h", "Dept. of Arts: “Prakriti to Kala”"),
            ("html", "<p><strong>Venue:</strong> Art Room</p>"),
            ("p", "Students have explored traditional art with a functional and contemporary touch, drawing inspiration from nature and their surroundings. The project showcases decorative and functional 2D and 3D artworks such as wall hangings, lamps, pots, relief works, jewellery, bags, and home décor with diverse materials like clay, thread, fabric, wire, M-Seal, paper, moulds, and waste materials. The project aims to integrate tradition, creativity, functionality, sustainability, and aesthetics into meaningful art for everyday space."),
            ("h", "Dept. of Music: “Nāma Saṅkīrtana–Cultivating Harmony through Music”"),
            ("html", "<p><strong>Venue:</strong> AV Room</p>"),
            ("p", "Nāma Saṅkīrtana is a music-based initiative that seeks to revive and promote the traditional practice of collective chanting and singing of the Divine Name. The project aims to make devotional music an integral and joyful part of school life. Beyond musical learning, the project seeks to create an atmosphere of inner quietude, harmony and cultural rootedness, enabling children to experience music as a means of connecting the individual with the collective and the sacred."),
            ("h", "Class 7: “Karma to Arpaṇa – Act and Offer”"),
            ("html", "<p><strong>Venue:</strong> Room No 9</p>"),
            ("p", "Through the second and the third slokas of Gita Panchamrit, students explore how the Kurukṣetra situation applies to real life. Students explore the actions, attitudes and motivations of individuals. Through the project, students reflect on qualities such as leadership, courage, self-awareness, preparedness and the consequences of one’s choices. The project gradually shifts the learner from simply knowing the story to asking: How do I respond when I face challenges, pressure or conflict?"),
            ("h", "Class 8: “Śaraṇāgati – Trust and Surrender”"),
            ("html", "<p><strong>Venue:</strong> Room No 15</p>"),
            ("p", "Through Ananyāś cintayanto māṁ, students explore the meaning of wholehearted devotion and trust in the Divine. Sarvadharmān parityajya introduces the profound idea of śaraṇāgati—surrendering oneself completely to the Divine. The project encourages students to understand surrender not as weakness, but as an expression of faith, inner strength and freedom from fear."),
        ],
    },
    # ------------------------------------------------------ #CIRS Celebrations
    {
        "slug": "holi-2026",
        "title": "Holi on Dronacharya Field",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "3–4 March 2026",
        "datetime": "2026-03-03",
        "dek": "The festivities began with Holika Dahan and ended with students and staff playing with colours.",
        "who": "The whole school",
        "photos": [
            (10, 2319, "A man in an orange kurta smearing colour on a smiling student among others with coloured faces at Holi"),
        ],
        "blocks": [
            ("p", "The school marked Holi with great enthusiasm, devotion and togetherness. The festivities began on the evening of 3 March with Holika Dahan, symbolising the triumph of good over evil. On 4 March, the day commenced with Lord Krishna Puja and Aarti in the MPH, creating a devotional atmosphere. This was followed by a vibrant celebration at Dronacharya Field, where students and staff joyfully played with colours. The celebration brought the CIRS family together in a spirit of friendship, laughter, joy and festive camaraderie."),
        ],
    },
    {
        "slug": "ram-navami-2026",
        "title": "Ram Navami: dance, song and a skit",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "27 March 2026",
        "datetime": "2026-03-27",
        "dek": "Parents of the new students joined the celebration, whose evening programme had dance, songs and a skit.",
        "who": "Students, staff and parents of new students",
        "photos": [
            (11, 2370, "A garlanded child dressed as Bal Ram seated at a decorated altar as women make offerings"),
            (11, 3521, "A student in a golden crown and a student in a red sari on a dark stage"),
            (11, 2367, "Students in costume in a scene from the Ram Navami skit"),
        ],
        "blocks": [
            ("p", "On 27 March 2026, CIRS celebrated the birth of Lord Ram with great enthusiasm and devotion. Parents of the new students also joined the celebrations, adding to the significance of the occasion. Students and staff gathered with reverence and renewed positive energy. The evening programme featured captivating dance performances, soulful songs and an engaging skit. The celebration created a serene and spiritually uplifting atmosphere, leaving everyone with a profound sense of peace, joy and spiritual fulfilment."),
        ],
    },
    {
        "slug": "hanuman-jayanti-2026",
        "title": "Hanuman Jayanti: the Chalisa, 54 times",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "2 April 2026",
        "datetime": "2026-04-02",
        "dek": "A morning puja and Likitha Japa, an evening of chanting, and a skit on Hanumanji’s selfless devotion.",
        "who": "Students and staff",
        "photos": [
            (13, 2451, "A student in a yellow kurta seated before a garlanded murti, lamps and offerings"),
            (13, 2454, "Students in costume on a blue-lit stage during a skit"),
            (13, 2448, "A student in a yellow kurta writing in a notebook, seated on the floor"),
        ],
        "blocks": [
            ("p", "Hanuman Jayanti was celebrated on 2 April with deep devotion and spiritual fervour, honouring Lord Hanuman, the eternal symbol of strength, surrender and unwavering devotion to Lord Rama. The day began with a sacred morning puja and Likitha Japa, as students and staff immersed themselves in prayer. The evening resonated with the chanting of the Hanuman Chalisa, rendered 54 times, creating an atmosphere of peace and devotion. Students enriched the celebration through a special skit portraying Hanumanji’s selfless devotion and noble deeds. The celebration inspired reflection on humility, faith, courage, love and selfless service."),
        ],
    },
    {
        "slug": "tamil-new-year-and-vishu-2026",
        "title": "Tamil New Year and Vishu",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "14 April 2026",
        "datetime": "2026-04-14",
        "dek": "Dorm parents led students, eyes closed, to the Vishukkani; the evening brought Tamil songs by the choir and dance.",
        "who": "The whole school",
        "photos": [
            (11, 2375, "A student speaking at a microphone beneath a sign that reads Mother Tamil"),
            (11, 2384, "Performers in white and gold saris dancing on a stage"),
        ],
        "blocks": [
            ("p", "Tamil New Year and Vishu were celebrated at CIRS on 14 April with enthusiasm, embracing the rich traditions and festive spirit of both occasions. The day began auspiciously as dorm parents led us, with our eyes closed, to experience the beautiful tradition of ‘Vishukkani’, symbolising hope, gratitude and abundance. Dressed in vibrant traditional attire, we gathered at noon to enjoy a sumptuous Sadhya with friends. The evening featured a special Aarti, soulful Tamil songs by the choir and graceful dance performances celebrating Tamil Nadu’s vibrant culture, fostering joy, togetherness and cultural appreciation."),
        ],
    },
    {
        "slug": "gurudev-jayanti-2026",
        "title": "Gurudev Jayanti",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "8 May 2026",
        "datetime": "2026-05-08",
        "dek": "Paduka Puja, the chanting of Gurudev’s 108 names and a yatra for new students, closing with bhajans by the school choir.",
        "who": "The whole school",
        "photos": [
            (12, 2414, "Students wearing coloured headbands seated on the amphitheatre steps, with a person in saffron in the foreground"),
            (12, 2411, "Students standing in a row in a courtyard wearing coloured bands, with a person in saffron beside them"),
            (12, 2417, "A teacher speaking into a microphone beside a decorated board as students in house shirts look on"),
        ],
        "blocks": [
            ("p", "To commemorate the birth anniversary of Pujya Gurudev Swami Chinmayananda, Gurudev Jayanti was observed on 8 May with devotion and reverence. The programme commenced with a Paduka Puja, during which Gurudev’s 108 names were chanted, reaffirming our commitment to his noble ideals. A special yatra depicting significant milestones from his life was organised, offering new students an opportunity to learn about his teachings and spiritual legacy. The evening concluded with a unique aarti, accompanied by soulful bhajans presented by the school choir, creating an atmosphere of serenity and tranquillity."),
        ],
    },
    {
        "slug": "guru-poornima-2026",
        "title": "Guru Poornima",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "29 July 2026",
        "datetime": "2026-07-29",
        "dek": "Students chanted Gurudev’s 108 names, then sought the blessings of teachers and staff.",
        "who": "The whole school",
        "photos": [
            (10, 2314, "A woman seated on a chair as a student in pink bends to touch her feet, with rows of students seated behind"),
            (10, 2342, "A student in glasses with her head bowed and her hand at her forehead"),
            (10, 2345, "A woman in a yellow sari touching another person’s forehead before a blue backdrop"),
        ],
        "blocks": [
            ("p", "A Guru plays a vital role in shaping every individual’s journey through wisdom, knowledge and values. On 29th July, Guru Purnima was celebrated with devotion and gratitude, invoking the grace of Maharishi Ved Vyasa and the revered Guru Parampara for the well-being of all. The morning commenced with Paduka Puja in the MPH, followed by the chanting of Gurudev’s 108 names. Students then sought blessings from teachers and staff, while “Shri Gurubhyo Namah” resonated, inspiring gratitude and reverence."),
        ],
    },
    {
        "slug": "gurudev-aaradhana-2026",
        "title": "Gurudev Aaradhana and the Investiture Ceremony",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "3 August 2026",
        "datetime": "2026-08-03",
        "dek": "The Maha Samadhi of Pujya Swami Chinmayananda was honoured, and the new School Council leaders received their badges.",
        "who": "The whole school",
        "photos": [
            (12, 2399, "Students in school uniform wearing sashes standing in a long line in a hall"),
            (12, 2402, "Three students wearing green sashes on a stage before a Vyasa banner"),
            (12, 2408, "Students seated in a hall, listening"),
            (12, 2396, "A student in a yellow kurta with palms joined"),
        ],
        "blocks": [
            ("p", "For students at CIRS, 3 August was a day of remembrance, responsibility and reflection as we honoured the Maha Samadhi of Pujya Swami Chinmayananda and welcomed the new School Council leaders. The day commenced with Guru Paduka Puja, followed by Atma Nivedanam, the Investiture Ceremony, where leaders received badges from the Principal, Smt. Rajeshwari, and Headmaster, Sri Ganesh. The evening Aarti preceded the Inter-House competition, Shravanam, Smaranam, Mananam, celebrating poetry, bhajans, art and Gurudev’s wisdom."),
            ("html", "<p><a href=\"student-council-2026-27.html\">The Student Council 2026&ndash;27</a></p>"),
        ],
    },
    {
        "slug": "onam-2026",
        "title": "Onam: pookalams, a sadhya and a skit",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "26 August 2026",
        "datetime": "2026-08-26",
        "dek": "Staff made the flower rangolis; students danced, sang and staged a skit on the values of unity and togetherness.",
        "who": "Students and staff",
        "photos": [
            (15, 1257, "Students on a stage in a skit, one standing beneath a colourful ceremonial umbrella"),
            (15, 1263, "Girls in bright traditional skirts dancing in a row on a stage"),
        ],
        "blocks": [
            ("p", "The fragrance of flowers on 26th August marked the arrival of Onam, celebrating the beloved King Mahabali. The festivities began with colourful pookalams (flower rangolis) adorning the campus, thoughtfully created by the staff. Dressed in traditional attire, students and staff enjoyed a sumptuous Onam Sadhya. The celebrations continued with vibrant dances, melodious songs and a skit portraying the essence of Onam and its values of unity and togetherness. The day concluded with Gurudev’s Aarti and prayers for happiness, prosperity and well-being."),
        ],
    },
    {
        "slug": "raksha-bandhan-2026",
        "title": "Raksha Bandhan in the CIRS quadrangle",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "28 August 2026",
        "datetime": "2026-08-28",
        "dek": "Sisters tied rakhis on their brothers’ wrists, and the brothers answered with grade-wise programmes.",
        "who": "Junior and Senior School",
        "photos": [
            (13, 2457, "Students in festive clothes kneeling on the grass holding plates, with a group standing behind them"),
            (13, 2460, "A girl speaking into a microphone beside a boy in a kurta"),
            (13, 2463, "Students tying rakhis at a long table laid with plates"),
        ],
        "blocks": [
            ("p", "The warmth of the brother-sister bond filled the CIRS quadrangle on 28th August as Raksha Bandhan was celebrated with joy. Following the morning Krishna Puja, sisters tied rakhis on their brothers’ wrists, symbolising love, care and protection. Students from the Junior and Senior Schools shared cherished sibling memories, adding meaning to the occasion. The celebrations concluded joyfully as brothers surprised their sisters with grade-wise programmes, creating an atmosphere of laughter, affection and togetherness while honouring the special bond of siblings."),
        ],
    },
    {
        "slug": "krishna-janmashtami-2026",
        "title": "Krishna Janmashtami: the midnight Aarti and Handi Phod",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "4 September 2026",
        "datetime": "2026-09-04",
        "dek": "Some students fasted while awaiting the birth of Lord Krishna, and the celebration ended with Handi Phod.",
        "who": "The whole school",
        "photos": [
            (15, 2532, "A small child dressed as Krishna in a crown and a pearl necklace"),
            (15, 2535, "Students singing into microphones on a stage lit in blue"),
            (15, 2547, "Students forming a human pyramid at night beneath a hanging pot"),
        ],
        "blocks": [
            ("p", "On 4th September, CIRS celebrated Janmashtami with immense joy and devotion. The day began with Krishna Puja, with some students observing a fast while awaiting the birth of Lord Krishna. The highlight was the midnight Aarti, when His birth was welcomed with Pooja, vibrant bhajans and delicious Prasad. The celebrations concluded enthusiastically with Handi Phod, re-enacting Krishna’s childhood playfulness of stealing butter from earthen pots in Vrindavan. The occasion fostered togetherness, devotion, joy and the sweet spirit of Krishna."),
            ("html", "<p><a href=\"festivals.html\">More photographs of the school’s festivals</a></p>"),
        ],
    },
    {
        "slug": "teachers-day-2026",
        "title": "Teachers’ Day: a rose for every teacher",
        "section": "Community",
        "group": "#CIRS Celebrations",
        "date": "5 September 2026",
        "datetime": "2026-09-05",
        "dek": "Students conducted the morning assembly and gave each teacher a rose at the Annakshetra.",
        "who": "Students and teachers",
        "photos": [
            (14, 2492, "Students in blue and grey standing in formation on a lawn in front of the school buildings"),
            (14, 2495, "A student in a saffron kurta speaking at a lectern"),
            (14, 2498, "A girl in a pink sari speaking at a lectern"),
        ],
        "blocks": [
            ("p", "5th September was a special day at CIRS as we celebrated Teachers’ Day, commemorating the birth anniversary of Dr. Sarvepalli Radhakrishnan. The occasion provided an opportunity to express our heartfelt gratitude to teachers who guide, encourage and support us every day. Students conducted the morning assembly and presented each teacher with a rose at the Annakshetra. Their warm smiles made the gesture truly meaningful. The celebration concluded with affection, laughter and cherished memories, honouring those who make our school journey meaningful."),
        ],
    },
    # ---------------------------------------------------------- Subject weeks
    {
        "slug": "language-week-2026",
        "title": "Language Week: puzzles, antakshari and the Language Run",
        "section": "Academics",
        "group": "Subject weeks",
        "date": "6–11 July 2026",
        "datetime": "2026-07-06",
        "dek": "Classroom activities, a senior quiz, runs in four languages and a handwriting competition.",
        "who": "Grades I–XII",
        "photos": [
            (16, 2607, "Students in green house shirts gathered around a desk"),
            (16, 2611, "Students in mustard house shirts crowded around a table"),
            (16, 2617, "Students in house shirts standing at a green board"),
            (16, 2620, "A man speaking at a lectern in a hall"),
        ],
        "blocks": [
            ("p", "Language Week was celebrated from 6 to 11 July 2026, offering students a wide range of activities. The week commenced on 6 July with an engaging day of classroom activities. Students explored language through puzzles and crosswords, language quizzes, short videos, spin a story, group discussions, language antakshari and dumb charades."),
            ("p", "The Senior Quiz was conducted on 8 July, followed by the Language Run in Sanskrit and Tamil on 9 July and the Language Run in Hindi and French on 10 July. The week concluded on 11 July with a handwriting competition for the students of Grades I-VIII."),
        ],
    },
    {
        "slug": "mathematics-week-2026",
        "title": "Mathematics Week 2026",
        "section": "Academics",
        "group": "Subject weeks",
        "date": "13–18 July 2026",
        "datetime": "2026-07-13",
        "dek": "Mental Maths, Origami, a Maths Quiz, Coding and Decoding, and sessions on Mathematical Induction.",
        "who": "The Mathematics Department and students",
        "photos": [
            (16, 2652, "Students seated at a table covered in a red cloth, answering questions before an audience"),
            (16, 2630, "Students in blue shirts gathered around a table"),
            (16, 2643, "Students working at desks in a classroom"),
            (16, 2649, "A team of students in maroon shirts standing in a line in a classroom"),
            (16, 2637, "A man in a pink shirt speaking into a microphone while holding up a small white object"),
        ],
        "blocks": [
            ("p", "To make the subject more enjoyable, the Mathematics Department came up with a variety of activities to engage students and help them discover its fun side. Mathematics Week 2026, held from 13 to 18 July, included Mental Maths, Origami, Maths RUN, a Maths Quiz, Coding and Decoding, and “Math Detectives.” Sessions on Mathematical Induction further enriched the week, making learning lively and enjoyable beyond the classroom."),
        ],
    },
    {
        "slug": "english-week-2026",
        "title": "English Week: storytelling, Spell Bee and HAM",
        "section": "Arts",
        "group": "Subject weeks",
        "date": "17–22 August 2026",
        "datetime": "2026-08-17",
        "dek": "Storytelling, handwriting, poetry recitation, Spell Bee, a quiz and HAM, with enrichment activities in the regular lessons.",
        "who": "Students and English teachers",
        "photos": [
            (17, 2731, "Students in school uniform and a swami in saffron standing on a stage before a Half-A-Minute banner"),
            (17, 2741, "Two students at a table with microphones before a backdrop that reads In just 30 seconds"),
            (17, 2734, "Students seated at a table covered in a red cloth"),
            (17, 2738, "Students seated at a red-clothed table with microphones"),
        ],
        "blocks": [
            ("p", "English week was celebrated from 17 to 22 August 2026. The week brought together a lively mix of Storytelling, Handwriting, Poetry Recitation, Spell Bee, Quiz and HAM, giving students varied platforms to explore language, expression and performance. Beyond the competitions, teachers introduced various language-enrichment activities into their regular lessons throughout the week. The celebration highlighted the many dimensions of language learning while nurturing confidence and appreciation for English literature and language."),
        ],
    },
    {
        "slug": "india-week-2026",
        "title": "India Week: Independence Day, Bharat Run and Niti Nirman",
        "section": "Academics",
        "group": "Subject weeks",
        "date": "Independence Day, August 2026",
        "datetime": "2026-08",
        "undated": True,
        "dek": "Essay, photography and poetry contests, a policymaking contest, and a run with stations on freedom, ending in the Nasha Mukt Bharat pledge.",
        "who": "All students",
        "photos": [
            (17, 2724, "Uniformed cadets marching across a parade ground under a flag"),
            (17, 2718, "Students marching in formation behind a house banner"),
            (17, 2715, "Rows of students standing in formation on a parade ground"),
            (17, 2727, "A woman in a white and red sari handing something to small children, one of them holding a flag"),
            (17, 2721, "Students at a table with a laptop and a notebook"),
        ],
        "blocks": [
            ("p", "Independence Day was marked by many events honoring the journey to August 15, 1947. The Crossroads Magazine held essay and photography contests, while the Cultural Department hosted a poetry contest, “Expression of Oppression,” on Partition’s horrors. The Youth Economic Initiative ran “Niti Nirman,” a policymaking contest. KTPI students led Bharat Run, with stations on freedom’s meaning, its modern expressions, and unsung freedom fighters. All students took the “Nasha Mukt Bharat” pledge."),
            ("html", "<p><a href=\"crossroads.html\">The Crossroads, the school’s magazine</a></p>"),
        ],
    },
    {
        "slug": "management-week-2026",
        "title": "Management Week 2026: from Ads-Up to COMQUEST ’26",
        "section": "Academics",
        "group": "Subject weeks",
        "date": "2026, dates not stated",
        "datetime": "2026-10",
        "undated": True,
        "dek": "Junior and senior activities, two film screenings and a business quiz and pitch deck competition with 13 schools.",
        "who": "Grades V–XII",
        "photos": [
            (17, 2693, "Students in mustard kurtas and teachers gathered in a laboratory"),
            (17, 2687, "Students in mustard kurtas crowded around a tall tower of sticks"),
            (17, 2690, "Two women speaking at a lectern"),
            (17, 2696, "Students seated on a wooden floor with coloured pens and paper"),
        ],
        "blocks": [
            ("p", "Management Week 2026, organised by the Department of Management at CIRS, offered students a myriad of experiential activities. Grades V–VII participated in Ads-Up, Product Designing and the Marshmallow Tower Challenge, while senior students engaged in the Management Run, Mystery Box Challenge, Beyond the Storm disaster-management simulation and Decoding the AI Bubble. The week also featured screenings of The Intern and The Big Short, offering insights into leadership, workplace dynamics, and financial decision-making. The celebrations culminated in COMQUEST ’26, featuring the Business Quiz and Pitch Deck Competition, with participation from 13 schools."),
        ],
    },
    {
        "slug": "seva-week-2026",
        "title": "Seva Week: notebooks, saplings and temple cleaning",
        "section": "Community",
        "group": "Subject weeks",
        "date": "2026, dates not stated",
        "datetime": "2026-10",
        "undated": True,
        "dek": "Gratitude cards, reused notebooks, temple cleaning, saplings, paper bags and a special Aarthi at Vraja.",
        "who": "Students",
        "photos": [
            (16, 2640, "Students and staff picking up litter on the ground outside a temple"),
            (16, 2646, "Students in mustard kurtas seated on the floor with sheets of paper"),
            (16, 2627, "Students seated on a tiled floor sorting notebooks and papers"),
            (16, 2634, "Students seated in rows on blue mats in a hall"),
        ],
        "blocks": [
            ("p", "SEVA Week provided students with meaningful opportunities to practise the spirit of selfless service and community engagement. The week featured Gratitude Card Making, Refurbishing Old Notebooks by Reusing Pages, Essay Writing Competition, Campus Temple Cleaning, Rangoli Making, Planting New Saplings, Paper Bag Making, Patteswara Temple Cleaning at Perur, Coimbatore, and a Special Aarthi for students of Grades V–XI at Vraja."),
            ("html", "<p><a href=\"seva-week.html\">Seva Week, April 2025</a></p>"),
        ],
    },
    # ------------------------------------------------- Highlights, competitions
    {
        "slug": "first-time-speakers-forum-2026",
        "title": "The First Time Speakers’ Forum",
        "section": "Arts",
        "group": "Highlights and competitions",
        "date": "20 August 2026",
        "datetime": "2026-08-20",
        "dek": "The English Department gave hesitant speakers a space to recite, narrate and share for the first time.",
        "who": "Selected students",
        "photos": [
            (18, 2780, "A collage of students speaking into microphones at the First Time Speakers’ Forum"),
        ],
        "blocks": [
            ("p", "Not every child who has something to say is ready to step forward and speak. The English Department makes a conscious effort to spot such hesitant speakers and give them a space to find their voice. The First Time Speakers’ Forum is one such initiative. This year, the department held the forum on 20 August 2026, where selected students recited poems, narrated stories, and shared experiences for the first time. Watching their initial hesitation give way to smiles, confidence, and the courage to speak was truly heartening."),
        ],
    },
    {
        "slug": "ncc-best-school-of-the-camp-2026",
        "title": "NCC: Best School of the Camp",
        "section": "Achievements",
        "group": "Highlights and competitions",
        "date": "27 July – 5 August 2026",
        "datetime": "2026-07-27",
        "dek": "CIRS cadets excelled at the Combined Annual Training Camp at SNS College of Technology, Coimbatore.",
        "who": "The NCC cadets",
        "photos": [
            (18, 2777, "NCC cadets marching behind a blue and red flag on a parade ground"),
        ],
        "blocks": [
            ("p", "The NCC at CIRS goes beyond regular training, nurturing team spirit, responsibility, and a spirit of service. During Seva Week, cadets visited Thondamuthur and Alandurai Hospitals to support a plastic-reduction initiative and participated in a cleanliness drive at Dharmalingeshwar Temple. Further, at the Combined Annual Training Camp, held from 27 July to 5 August 2026 at SNS College of Technology, Coimbatore, our students excelled in volleyball, drawing, drill, throwball, and cultural events, earning CIRS the Best School of the Camp award."),
        ],
    },
    {
        "slug": "interschool-competitions-2026",
        "title": "Interschool competitions",
        "section": "Achievements",
        "group": "Highlights and competitions",
        "date": "Reported in the bulletin of October 2026",
        "datetime": "2026-10",
        "undated": True,
        "dek": "First places in a hackathon, quizzes, spell bee, essay writing, group dance and extempore, with second and third prizes at Suguna.",
        "who": "Students of Grades V–XII",
        "photos": [
            (19, 1397, "Girls in purple and orange dance costumes holding a certificate on a stage"),
            (19, 1396, "Students seated at computers in a room"),
            (19, 1389, "Students and adults with certificates before a Coimbatore Sahodaya Inter-School Quiz Competition banner"),
            (19, 1390, "Two women, two men and a student holding a certificate in a room"),
            (19, 1388, "A student in a white kurta and another in a yellow kurta with three adults before a screen"),
            (19, 1395, "Students and adults, several holding certificates, standing beneath a Suguna International School sign"),
        ],
        "blocks": [
            ("p", "The results below are printed in the bulletin under the heading Interschool Competition. They are set out here as the bulletin gives them."),
            ("h", "Mind-Spark ’26, Karunya Institute of Technology and Science"),
            ("fig", 2),
            ("p", "Aryan I G and Adwaith Praveen of Grade XII: Hackathon, First Place."),
            ("h", "“Bewitching Bali”: a young voice in print"),
            ("p", "Aarav Bhartia, IB I Year: Travel Article Publication."),
            ("h", "Hindi Utsav, Hindustan College of Arts and Science"),
            ("ul", [
                "Shrey Kothari: Essay Writing, First Place",
                "Nukkad Natak (Team): First Place",
                "Mime (Team): Second Place",
            ]),
            ("h", "47th Sahodaya Inter-School Spell Bee Competition"),
            ("ul", [
                "Arnav Nair (Grade X) and Jesal Dangaria (Grade X): Category D (Boy), First Place",
                "Rhea Sontakke (Grade XI) and Mahi Mandhana (Grade XI): Category E (Girls), First Place",
            ]),
            ("h", "Quiz results, Devansh Mazumdar and Pradyuth Senthil"),
            ("fig", 4),
            ("ul", [
                "Quiztrack: First Place",
                "Quiz Fest: Second Place",
                "AQMEN: Second Place",
                "Coimbatore Quiz Circle: First Place",
            ]),
            ("h", "Coimbatore Quiz Circle"),
            ("fig", 5),
            ("ul", [
                "Vrishank Mehta and Ishaan Madhusudhan: Second Place",
                "Viraj Lal and Divyam Gupta: recognized for conducting the quiz",
            ]),
            ("h", "47th Sahodaya (73 performances), Benglen Public School"),
            ("fig", 1),
            ("p", "School Team: Group Dance Competition, First Place."),
            ("h", "Suguna International School Competition"),
            ("fig", 6),
            ("ul", [
                "School Team: Group Bhajan, Second Prize",
                "Krishnav Deorah: Extempore, First Prize",
                "Manvi Sah: Storytelling, Second Prize",
                "Sadhana P. M.: Thirukkural Recitation, Second Prize",
                "Munaga Srivathsa: Bhagavad Gita, Second Prize",
                "Darsh Kejriwal: Extempore, Second Prize",
                "Aradhya E. S.: Art, Second Prize",
                "Riya Shri S.: Thirukkural Recitation, Third Prize",
                "Antara Kumari Bhudolia: Storytelling, Third Prize",
            ]),
            ("h", "Bizcollatus 2026"),
            ("p", "Shaurya Bhartia and Viraj Lal (XII): On the Docket, First Place."),
            ("h", "Sahodaya GK, Avatar Public School, Coimbatore"),
            ("fig", 3),
            ("ul", [
                "Devansh Mazumdar and Aryavardhan Agarwal: Quiz Senior Category, First Place",
                "Arnav Anand and Hridith Agarwal: Quiz Junior Category, First Place",
            ]),
        ],
    },
    # ----------------------------------------------------------------- Sports
    {
        "slug": "football-2026",
        "title": "Football: winners at Nathan, runners-up at the Games",
        "section": "Sports",
        "group": "Sports",
        "date": "7 August – 1 September 2026",
        "datetime": "2026-08-07",
        "dek": "The Under-16 team won the 4th Nathan Inter-School Football, the Under-18 IB team was runner-up in the International School Games, and the Under-12 team placed third twice.",
        "who": "Under-12, Under-14, Under-16 and Under-18 teams",
        "photos": [
            (20, 2822, "Boys in blue and yellow kits gathered before a banner for the 4th Nathan Memorial Trophy football tournament"),
            (22, 2858, "A football team in blue and yellow kits wearing medals and holding a trophy, with adults standing beside them"),
            (22, 2855, "A football team holding certificates in front of a Coimbatore Sahodaya football tournament banner"),
            (20, 2813, "A football team in yellow and blue kits kneeling beside a trophy on a pitch"),
        ],
        "blocks": [
            ("h", "4th Nathan Inter-School Football"),
            ("p", "Our Under-12, Under-14 and Under-16 Football teams participated in the 4th Nathan Inter-School Football Tournament organised by Vivekam Sr. Sec. School, Coimbatore on 7th and 8th August 2026. With 48 schools competing, our Under-12 team secured 3rd position, while the Under-16 team emerged as Winners. Yughav (Grade 10) was honoured with the Best Player Award."),
            ("h", "International School Games Football"),
            ("fig", 2),
            ("p", "Our school participated in the International School Games Football Tournament organised by Manchester International School, Coimbatore, on 29th August 2026. Our Under-18 IB students secured the Runner-Up position, while Samarth Nambiar of 2nd IB received the Best Player Award."),
            ("h", "47th Coimbatore Sahodaya Inter-School Football Tournament"),
            ("fig", 3),
            ("p", "Our Under-12 Football Team participated in the 47th Coimbatore Sahodaya Inter-School Football Tournament organised by Chandrakanthi Public School on 31st August and 1st September 2026. With 36 schools participating, our Under-12 team secured the 3rd position."),
            ("h", "Champion Cup 5-on-5 Football Tournament"),
            ("fig", 4),
            ("p", "Our Boys Under-17 Football Team participated in the Champion Cup 5-on-5 Football Tournament held at Emirates Sports Arena, Coimbatore, on 3rd May 2025. With 21 sports academies competing, our team performed strongly and secured the Runner-Up position."),
        ],
    },
    {
        "slug": "tennis-pickleball-and-table-tennis-2026",
        "title": "Tennis, pickleball and table tennis",
        "section": "Sports",
        "group": "Sports",
        "date": "27 July – 19 September 2026",
        "datetime": "2026-07-27",
        "dek": "Bronze at the CBSE South Zone, Gold in pickleball singles, three medals at the Sahodaya tournament and two winners at the UTR event in Bangalore.",
        "who": "Boys and girls, Classes 5 to 12",
        "photos": [
            (20, 2819, "Players and officials standing together after the CBSE South Zone Tennis Tournament"),
            (20, 1409, "Boys holding trophies and certificates before a Coimbatore Sahodaya pickleball tournament banner"),
            (21, 2838, "Boys holding medals and certificates beneath a Perks Public School banner"),
            (21, 2841, "A boy holding a trophy standing beside a man on a clay tennis court, in two photographs side by side"),
        ],
        "blocks": [
            ("h", "CBSE South Zone Tennis Tournament"),
            ("p", "CIRS participated in the CBSE South Zone Tennis Tournament organised by National Academy School, Ramanathapuram, from 27th to 30th July 2026. With schools from five states competing and 64 schools in the Under-19 Boys category, our school secured the Bronze Medal. The team comprised Deepansh Gupta (Grade 12), Laksh Bajaj (Grade 10), Yug Goyal (Grade 9) and Nidhershan (Grade 9)."),
            ("h", "47th Sahodaya Pickleball"),
            ("fig", 2),
            ("p", "Our school participated in the 47th Coimbatore Sahodaya Inter-School Boys Pickleball Tournament organised by Bridgewood International School, Sulur, on 8th August 2026. With 21 schools participating, Deepansh Gupta (Grade 12) won Gold in Singles, while Deepansh Gupta and Vedant (Grade 11) secured Bronze in Doubles."),
            ("h", "47th Sahodaya Tennis"),
            ("fig", 3),
            ("p", "CIRS participated in the Coimbatore Sahodaya Inter-School Tennis Tournament organised by Perks Public School, Coimbatore, on 19th and 20th August 2026. With 42 schools participating, our students secured three medals: Silver in Under-14 Boys Doubles for Shiv Adith and Arnav, and Bronze in Under-16 Boys Doubles for Yug Goyal and Nidhershan, and Under-19 Boys Doubles for Deepansh and Aaryan IG."),
            ("h", "47th Coimbatore Sahodaya Table Tennis Tournament"),
            ("p", "CIRS participated in the CBSE Coimbatore Sahodaya Table Tennis Tournament organised by Perks Public School, Coimbatore, on 2nd September 2026. With 32 schools participating, Aarav Bhartia (Class 5) won Bronze in Under-12 Boys Singles, while Ramdan Sarawgi and Arush Jakkhodia (Class 10) secured Silver in Under-16 Boys Doubles."),
            ("h", "UTR (Universal Tennis Rating) Tennis Tournament"),
            ("fig", 4),
            ("p", "CIRS participated in the UTR Tennis Tournament organised by White Line Tennis Arena, Bangalore, on 19th September 2026. Among 21 UTR-ranked players, our students achieved notable results. In the Junior Category, Nidhershan (Grade 9) emerged Winner and Shiv Adith (Class 7) finished Runner-up. In the Senior Category, Deepansh Gupta (Grade 12) emerged Winner, Yug Goyal (Grade 9) finished Runner-up and Shaurya Gadhyan (Grade 12) reached the Semifinals."),
        ],
    },
    {
        "slug": "swimming-2026",
        "title": "Swimming: relay Gold and third overall",
        "section": "Sports",
        "group": "Sports",
        "date": "11 July – 4 September 2026",
        "datetime": "2026-07-11",
        "dek": "Silver at the Tiruppur District meet, and Sahodaya meets for twenty girls and twenty boys, the boys taking Gold in both Under-19 relays.",
        "who": "Under-12, Under-14, Under-16 and Under-19 swimmers",
        "photos": [
            (21, 2835, "A large group of boys in grey shirts posing before Perks Public School Sahodaya swimming banners"),
            (21, 2832, "A girl on the winners’ podium at the 47th Sahodaya Swimming Competition for girls, with officials standing beside it"),
            (20, 2816, "Boys in orange shirts holding certificates in front of a banner"),
        ],
        "blocks": [
            ("h", "47th Sahodaya Swimming Competition for Boys"),
            ("p", "Twenty boys represented CIRS at the 47th Sahodaya Swimming Competition held at Perks School, Coimbatore, on 4th September 2026, competing across the Under-12, Under-14, Under-16 and Under-19 categories. Our swimmers achieved multiple medals across individual and relay events, including Gold in both the 4×50m Medley Relay and 4×50m Freestyle Relay in the Under-19 category. The school also secured Overall Third Place with 140 points."),
            ("h", "47th Sahodaya Swimming Competition for Girls"),
            ("fig", 2),
            ("p", "Twenty girls represented CIRS at the 47th Sahodaya Swimming Competition held at Navabharath International School, Coimbatore, on 25th August 2026. Competing across the Under-12, Under-14, Under-16 and Under-19 categories, Anagha Mappat of the Under-16 category won Bronze in the 200m Individual Medley and 200m Butterfly."),
            ("h", "Tiruppur District Swimming"),
            ("fig", 3),
            ("p", "Six of our boys participated in the Tiruppur District State Level Swimming Competition held at KBR Swimming Pool, Tiruppur, on 11th July 2026, with 16 schools competing. Our swimmers secured Silver in the 4×50m Freestyle Relay, with Arav Jagadesh, Vidhur Vaibhav, Saket Kalyani and Shrey Kothari forming the relay team. Shrey Kothari also won Bronze in the 100m Breaststroke and 100m Butterfly."),
        ],
    },
    {
        "slug": "marathon-athletics-and-basketball-2026",
        "title": "A marathon, an athletics meet and Under-16 basketball",
        "section": "Sports",
        "group": "Sports",
        "date": "7–16 August 2026",
        "datetime": "2026-08-07",
        "dek": "Fifty-two students and teachers ran at Kangeyam, five students won Bronze at the District-Level Athletic Meet, and the Under-16 boys were basketball runners-up.",
        "who": "Students and teachers",
        "photos": [
            (21, 1416, "A large group of students in matching light-green shirts on a stage after the Kangeyam Marathon"),
        ],
        "blocks": [
            ("h", "Kangeyam Marathon 2026–27"),
            ("p", "A team of 52 students and teachers represented CIRS at the Kangeyam Marathon held on 15th and 16th August 2026. The event attracted around 6,500 participants, with our team comprising 27 boys, 20 girls, 4 male teachers and 1 female teacher. Our participants took part in the 5K, 10K and 21K races, giving their best throughout the event."),
            ("h", "District-Level Athletic Meet"),
            ("p", "CIRS participated in the District-Level Athletic Meet conducted at PPG Institute of Technology, Saravanampatti, Coimbatore, on 7th August 2026, with 780 athletes participating. Our students won five Bronze Medals: Jatan in Shot Put, Krishil in 100 Metres, Hasini in Shot Put, Anushya in Long Jump and Prinnika in 200 Metres."),
            ("h", "Sahodaya Inter-School Basketball Tournament"),
            ("p", "Our school participated in the 47th Coimbatore Sahodaya Basketball Tournament in the Under-16 Boys category, hosted by United Public School on 13th and 14th August 2026. With 24 schools competing, our team finished as Runners-up (II Place)."),
        ],
    },
]

# The group headings the News page's section is arranged under, in order.
GROUP_ORDER = ["Anand Utsav 2026", "#CIRS Celebrations", "Subject weeks",
               "Highlights and competitions", "Sports"]


def photo_path(slug, n, width=None):
    suffix = f"-{width}" if width else ""
    return f"{IMG_DIR}/{slug}-{n}{suffix}.webp"


def _prepare():
    """Give each article the fields news_article_html reads."""
    for art in ARTICLES:
        art["bulletin"] = True
        art["paragraphs"] = []
        figs = []
        for n, (_page, _xref, alt) in enumerate(art["photos"], 1):
            src = photo_path(art["slug"], n)
            w, h = webp_size(src)
            figs.append({"src": src, "alt": alt, "w": w, "h": h})
        inline = {b[1] for b in art["blocks"] if b[0] == "fig"}
        art["inline"] = {n: figs[n - 1] for n in inline}
        if figs:
            art["image"], art["image_alt"] = figs[0]["src"], figs[0]["alt"]
            art["image_size"] = (figs[0]["w"], figs[0]["h"])
            # Photographs the text does not place itself close the article.
            art["figures"] = [f for i, f in enumerate(figs) if i > 0 and (i + 1) not in inline]
        else:
            art["image"] = ""
            art["figures"] = []
        if 1 in inline:
            # The lead photograph is placed in the text; do not also open on it.
            art["image"] = ""
            art["lead_inline"] = True


_prepare()


def _thumb(art, sizes):
    if not art["image"] and not art.get("lead_inline"):
        return ""
    fig = art["inline"][1] if art.get("lead_inline") else {"src": art["image"], "alt": art["image_alt"],
                                                           "w": art["image_size"][0], "h": art["image_size"][1]}
    small = photo_path(art["slug"], 1, 720)
    srcset = (f'{small} 720w, {fig["src"]} {fig["w"]}w'
              if os.path.exists(os.path.join(ROOT, small)) else f'{fig["src"]} {fig["w"]}w')
    return (f'<img src="{fig["src"]}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{fig["w"]}" height="{fig["h"]}" alt="{esc(fig["alt"])}" loading="lazy" decoding="async">')


def _has_photo(art):
    return bool(art["image"]) or bool(art.get("lead_inline"))


def _date(art):
    if art.get("undated"):
        return f'<span>{esc(art["date"])}</span>'
    return f'<time datetime="{art["datetime"]}">{esc(art["date"])}</time>'


def _meta(art):
    return f'<p class="journal-meta"><span>{esc(art["section"])}</span>{_date(art)}</p>'


def _card(art, sizes):
    img = (f'<div class="journal-term__image">{_thumb(art, sizes)}</div>' if _has_photo(art) else "")
    plain = "" if _has_photo(art) else " journal-term__card--plain"
    return (f'        <li class="journal-term__card{plain}"><a href="{art["slug"]}.html">{img}'
            f'<div class="journal-term__copy">{_meta(art)}<h4>{esc(art["title"])}</h4>'
            f'<p>{esc(art["dek"])}</p></div></a></li>')


def group_photo_html(sizes="(max-width: 860px) 100vw, 1200px"):
    """The whole council's photograph, for the Student Life page."""
    big = council_path("council", 1600)
    small = council_path("council", 800)
    w, h = webp_size(big)
    return (f'<figure class="xc__all">\n'
            f'      <img src="{big}" srcset="{small} 800w, {big} 1600w" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{esc(COUNCIL_GROUP["alt"])}" loading="lazy" decoding="async">\n'
            f'      <figcaption>The Student Council {COUNCIL_YEARS}, as the bulletin pictures it. '
            f'The sashes name each office.</figcaption>\n'
            f'    </figure>')


def _rows():
    """(href, group, who, page) for every pledge, in the order the council is listed."""
    rows = [
        ("the-cirs-experience.html#student-council", "School Deans", "Two students", "The CIRS experience"),
        ("spiritual-life.html#cultural-secretaries", "Cultural Secretaries", "Four students", "Spiritual Life"),
        ("sports.html#secretaries", "Sports Secretaries", "Four students", "Our Sports"),
    ]
    for slug in HOUSE_SLUGS:
        g = GROUPS[slug]
        rows.append((f"houses.html#{g['anchor']}", f"{g['short']} House Captains", "Four students", "Our Houses"))
    return rows


def links_html():
    """The Student Life page's list of the pledges printed elsewhere."""
    items = "\n".join(
        f'        <li><a href="{href}">{esc(group)} <small>{esc(page)}</small></a></li>'
        for href, group, _who, page in _rows()[1:])
    return f'''<div class="xc__more">
      <h3 id="xc-more-title">The rest of the council, in its own words</h3>
      <ul aria-labelledby="xc-more-title">
{items}
      </ul>
    </div>'''


def council_hub_html():
    """The News page's way into the Student Council: who, and where each pledge is printed.

    The pledges themselves are not repeated here. Each is printed once, on the
    page of the school where its group's work belongs, and this lists them.
    """
    big = council_path("council", 1600)
    small = council_path("council", 800)
    w, h = webp_size(big)
    rows = _rows()
    items = "\n".join(
        f'        <li><a href="{href}"><span class="journal-council__group">{esc(group)}</span>'
        f'<span class="journal-council__who">{esc(who)} &middot; read their pledge on {esc(page)}</span>'
        f'<span class="journal-council__arrow" aria-hidden="true">&#8599;</span></a></li>'
        for href, group, who, page in rows)
    return f'''    <div class="journal-council" id="council" aria-labelledby="council-title">
      <figure class="journal-council__photo">
        <img src="{big}" srcset="{small} 800w, {big} 1600w" sizes="(max-width: 760px) 100vw, 52vw" width="{w}" height="{h}" alt="{esc(COUNCIL_GROUP["alt"])}" loading="lazy" decoding="async">
        <figcaption>The Student Council {COUNCIL_YEARS}, from the bulletin.</figcaption>
      </figure>
      <div class="journal-council__copy">
        <p class="journal-section-head__label">Student voice</p>
        <h3 id="council-title">The Student Council {COUNCIL_YEARS}, in its own words.</h3>
        <p>Each group of the council wrote a pledge for the bulletin. They are printed in full, and unedited, where each group&rsquo;s work belongs.</p>
        <ul class="journal-council__list">
{items}
        </ul>
        <p class="journal-council__more"><a href="student-council-2026-27.html">Read about the Investiture Ceremony <span aria-hidden="true">&#8599;</span></a></p>
      </div>
    </div>'''


def section_html():
    """The News page's section for the bulletin: three leads, the council, then each group."""
    leads = [a for a in ARTICLES if a.get("lead")]
    out = ['<section class="journal-term journal-sakshi" id="sakshi" aria-labelledby="sakshi-title">',
           '  <div class="journal-wrap">',
           '    <div class="journal-section-head">',
           f'      <p class="journal-section-head__label">{esc(ISSUE)} &middot; {esc(ISSUE_LINE)}</p>',
           '      <h2 id="sakshi-title">From the school&rsquo;s bulletin</h2>',
           f'      <p>{len(ARTICLES)} reports from the October 2026 issue of the school&rsquo;s bulletin: '
           'the festivals and subject weeks of the year, the matches and competitions, the plans for Anand Utsav, '
           'and the pledges of the Student Council.</p>',
           '    </div>',
           '    <div class="journal-new-reports journal-term__leads">']
    for i, a in enumerate(leads):
        lead = " journal-new-report--lead" if i == 0 else ""
        sizes = "(max-width: 760px) 100vw, 56vw" if i == 0 else "(max-width: 760px) 100vw, 36vw"
        out += [f'      <article class="journal-new-report{lead}">',
                f'        <a href="{a["slug"]}.html">',
                f'          <div class="journal-new-report__image">{_thumb(a, sizes)}</div>',
                f'          <div class="journal-new-report__copy">{_meta(a)}<h3>{esc(a["title"])}</h3>'
                f'<p>{esc(a["dek"])}</p><span class="journal-read">Read story</span></div>',
                '        </a>',
                '      </article>']
    out.append('    </div>')
    out.append(council_hub_html())
    for group in GROUP_ORDER:
        arts = [a for a in ARTICLES if a["group"] == group and not a.get("lead")]
        if not arts:
            continue
        sid = "sakshi-" + "".join(c if c.isalnum() else "-" for c in group.lower()).strip("-")
        sid = "-".join(p for p in sid.split("-") if p)
        out += [f'    <div class="journal-term__group" aria-labelledby="{sid}">',
                f'      <h3 class="journal-term__label" id="{sid}">{esc(group)}</h3>',
                '      <ul class="journal-term__grid">']
        for a in arts:
            out.append(_card(a, "(max-width: 760px) 100vw, 30vw"))
        out += ['      </ul>', '    </div>']
    out += ['    <p class="journal-term__credit">Every report above is the school&rsquo;s own account, from Chinmaya Sakshi, '
            'the Anand Utsav Bulletin of October 2026. Photographs are the bulletin&rsquo;s own. Where the bulletin '
            'gives no date, none is shown.</p>',
            '  </div>',
            '</section>']
    return "\n".join(out)


def _short(datetime):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    parts = datetime.split("-")
    return f"{months[int(parts[1]) - 1]} {parts[0]}"


def archive_html():
    """One archive row per story, newest first, in the News archive's own format."""
    rows = []
    for a in sorted(ARTICLES, key=lambda a: a["datetime"], reverse=True):
        words = " ".join([a["title"], a["dek"], a["who"], a["group"]]).lower()
        words = "".join(c if c.isalnum() or c == " " else " " for c in words)
        words = " ".join(words.split())
        when = (f'<span class="journal-archive__undated">{esc(a["date"])}</span>' if a.get("undated")
                else f'<time datetime="{a["datetime"]}">{esc(a["date"])}</time>')
        rows.append(f'        <li data-journal-category="{a["section"]}" data-journal-search="{esc(words)}">'
                    f'<a href="{a["slug"]}.html">{when}'
                    f'<span>{esc(a["title"])}</span><small>{esc(a["section"])}</small></a></li>')
    return "\n".join(rows)


if __name__ == "__main__":
    for a in ARTICLES:
        print(f'{a["datetime"]:<10} {a["section"]:<13} {a["slug"]:<48} {len(a["photos"])} photos')
    print(len(ARTICLES), "articles")
    for k, g in GROUPS.items():
        print(k, g["photo"], len(g["pledge"]), "paragraphs,", len(" ".join(g["pledge"]).split()), "words")
