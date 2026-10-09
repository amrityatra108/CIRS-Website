#!/usr/bin/env python3
"""Anand Utsav 2026: the school's report of its annual celebration and Family Meet.

The text is the school's own, supplied for the News page on 9 October 2026,
and is printed as supplied. Three small corrections are made to it, so that
nothing is changed quietly:

  * "Vidhya Vaibhav" is "Vidya Vaibhav", which is how the school's bulletin and
    this site's own story of the exhibition (vidya-vaibhav-2026) spell it;
  * "Social Studies" is "Social Science", the department's name everywhere
    else on this site;
  * "design, sports and writing etc." loses its "etc.": "such as" already says
    the list is not complete.

The names and the facts are the school's. Where this site already reports the
same days (the schedule and the Vidya Vaibhav projects, from the October 2026
bulletin) the two agree.

The photographs are the seventeen published with Chinmaya Mission's report of
the festival, in the order that page gives them; the first is the report's own
lead. They are not in the repository: tools/make-anand-utsav.py fetches them
from the addresses below and cuts them into assets/img/news/anand-utsav/. The
report gives no captions, so none is written. Each alt text describes only what
the frame shows. Nobody is named from a face, and a frame is not tied to a part
of the programme that nothing in it says.

    PHOTOS    (id of the file on Chinmaya Mission's image server, alt text)
"""
import os

from sakshi import webp_size

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = "assets/img/news/anand-utsav"

SOURCE_URL = "https://www.chinmayamission.com/global/news/anand-utsav-at-cirs-family-values-creativity"
IMAGE_HOST = "https://images.chinmayamission.com/uploads/"

SLUG = "anand-utsav-2026"
TITLE = "Anand Utsav 2026: CIRS Celebrates Family, Values and Creativity"
DEK = ("The school’s annual celebration and CIRS Family Meet, held from 5 to 7 October 2026, "
       "brought students, parents and teachers together.")

PHOTOS = [
    ("dede5f7e-3a69-4293-ac2d-f9952a811884",
     "Ten people standing in a row on a stage under a blue backdrop that reads Award Ceremony, Anand Utsav 2026, "
     "a swami in saffron among them"),
    ("5194a591-bc1e-42fd-87d9-6d1b61e7fb0a",
     "A swami in saffron speaking into a microphone on stage, in front of a backdrop that begins with the word Welcome "
     "and reads Anand Utsav"),
    ("a0a535ef-5310-473d-b451-0e247dead67c",
     "Dancers in blue and purple costumes on a stage lit in violet, with a glowing symbol at the back"),
    ("55ad52ae-350e-4f49-919c-034a8bdd4996",
     "Students in blue skirts and kurtas of many colours on a dark stage, in front of a screen showing a robed figure "
     "in saffron"),
    ("3c711f94-91ea-47ca-955f-6bb1b18cca6c",
     "Dancers in red and gold costumes on stage, some of them stacked in a human pyramid, in front of a screen showing "
     "a street of garlanded doorways"),
    ("b8ff7ac0-914a-41de-8b97-997ab72ee5b0",
     "A large group of dancers in red, green and teal costumes posed together on stage, in front of a screen showing a "
     "village below green hills"),
    ("4490497d-e52d-4353-9a01-d7d07c87dc79",
     "A large group of students in white and coloured clothes on stage, in front of a screen showing a glowing outline "
     "map of India"),
    ("d135b940-b5eb-4bf8-9c10-d9455bb7f3ba",
     "Dancers in red, cream and green costumes on stage, in front of a screen showing a carved stone gateway hung with "
     "marigold garlands"),
    ("098527b4-ec2b-4f46-a740-385078bfc158",
     "Performers in red and orange costumes on stage, in front of a screen showing a spiral galaxy, with a many-armed "
     "figure at the centre"),
    ("8466304e-de90-4073-98e3-659b82c25ac7",
     "Students in colourful clothes filling the stage, with a swami in saffron standing at the front of it, hands "
     "together, and an audience in the foreground"),
    ("52580127-799d-46a8-a2a1-c6b315b4bb28",
     "Two swamis in saffron holding brass lamps in front of a seated audience in a hall, with a tabla player beside them"),
    ("b0af1aad-5a4e-4f7f-86dd-bf173a3b7959",
     "A wide view of a hall filled with parents, students and teachers seated on chairs and on the floor"),
    ("cfdd77f5-7f9e-4897-94b9-cae33e71d0cb",
     "Two members of the audience in the front rows, a woman and a man, applauding, with other people seated behind them"),
    ("88ad0597-e79b-415f-bf69-b01db44eb2d0",
     "A hall packed with people seated on the floor and on chairs, seen from the front under rows of ceiling lights"),
    ("41bf3184-87bf-422f-87eb-7ca67de9886d",
     "Parents seated on chairs in a crowded hall, with children sitting on the floor in front of them and flower petals "
     "scattered around; some parents reach toward their children’s faces"),
    ("fe55dd5c-be11-4c9d-92bc-ba944026d392",
     "A row of students in yellow kurtas holding dark folders, standing on a stage with teachers and swamis, in front of "
     "a screen with the school’s emblem and name"),
    ("e174e0ae-e332-46fa-8eb1-ae371b210b12",
     "A tiered display of carved fruit and flowers lit at night, with two peacocks at its sides, swans, and the words "
     "Chinmaya Amrit Mahotsav and 75 Years"),
]

ARTICLE = {
    "slug": SLUG,
    "title": TITLE,
    "section": "Campus",
    "date": "5–7 October 2026",
    "datetime": "2026-10-05",
    "dek": DEK,
    "festival": True,
    "paragraphs": [],
    "blocks": [
        ("p", "Chinmaya International Residential School (CIRS) came alive with Anand Utsav 2026, the school’s annual "
              "celebration and CIRS Family Meet, held from 5 to 7 October 2026. Held each year, Anand Utsav brings "
              "students, parents and teachers together to celebrate the vibrant spirit and values of the CIRS community."),
        ("p", "In the august presence of Swami Swaroopananda, Global Head of Chinmaya Mission, the celebrations featured "
              "an inspiring showcase of music, dance, theatre and creativity, with students taking centre stage to "
              "present their talents."),
        ("p", "Swamiji invited all parents and guests to the Chinmaya Amrit Mahotsav, to celebrate our shared identity "
              "as one Chinmaya family."),
        ("h", "A Tribute to Parents"),
        ("p", "A particularly moving highlight of the programme was the Matru-Pitru Pooja, in which students expressed "
              "their gratitude, love and reverence towards their parents. The ceremony reflected the spirit of "
              "value-based education at CIRS, where learning goes beyond academics to nurture gratitude, respect and "
              "the right values."),
        ("h", "Releases and Recognition"),
        ("html", "<p>Anand Utsav also saw the special release of three school publications: "
                 "<a href=\"news.html#sakshi\">Chinmaya Sakshi</a>, the newsletter for Anand Utsav, along with the "
                 "<a href=\"crossroads.html\">Crossroads Magazine</a> and The Chinmaya Awareness Magazine.</p>"),
        ("html", "<p>Adding to the occasion, a team guided by Br. Sanatan Chaitanya created and launched a brand-new "
                 "CIRS website, <a href=\"index.html\">www.cirschool.org</a>. The team received special praise from the "
                 "Resident Director, Swami Anukoolananda.</p>"),
        ("p", "Swami Anukoolananda also felicitated the CIRS parents who contributed to the smooth sail of the Chinmaya "
              "Amrit Yatra across India, through both financial contributions and organisational support."),
        ("h", "Chinmaya Gaurav Awards"),
        ("p", "Swami Swaroopananda recognised and honoured students and teachers with the Chinmaya Gaurav Awards. The "
              "awards celebrated exemplary students, students who have shown great leadership, and students with major "
              "achievements in fields such as design, sports and writing."),
        ("h", "Exhibitions Across Disciplines"),
        ("html", "<p>Students of Grades 5 to 8 presented <a href=\"vidya-vaibhav-2026.html\">Vidya Vaibhav</a>, an "
                 "exhibition on the Gita Panchamrit. Grades 5 and 6 together presented the first verse, Grade 7 the "
                 "next two verses, and Grade 8 the last two verses.</p>"),
        ("p", "The academic departments also put up a range of thoughtful exhibitions:"),
        ("ul", [
            "Science: Home as a laboratory",
            "Social Science: How Geography United Bharat",
            "Mathematics: Indian Knowledge Systems and Mathematics",
            "Music: Hour-long musicals on Naam Sankirtan",
        ]),
        ("h", "Learning by Doing"),
        ("p", "The Art and Management departments brought an entrepreneurial energy to the event. Student-made art "
              "pieces, including table light covers, drew brisk sales, while the Management stalls sold food from "
              "outside vendors. Running the stalls gave Management students hands-on experience in handling accounts."),
        ("p", "The CHYK Transformation Circle added to the excitement with its own line of merchandise, including "
              "diaries, pens, water bottles and quarter-zip T-shirts, which proved popular among the students."),
        ("h", "Bharata Bhagya Vidhata"),
        ("p", "The highlight of the celebrations was the evening cultural programme on the second day, titled Bharata "
              "Bhagya Vidhata. The production explored the nuances behind Rabindranath Tagore’s composition of the "
              "national anthem, offering the audience a fresh and moving perspective on a song every Indian knows by "
              "heart."),
        ("h", "A Celebration of Togetherness"),
        ("p", "With a perfect blend of fun, learning and cultural exploration, Anand Utsav 2026 fostered a spirit of "
              "togetherness. It gave students the chance to express themselves, connect with their peers and enjoy a "
              "vibrant, festive atmosphere, while parents witnessed first-hand the holistic education that defines CIRS."),
        ("h", "The festival in pictures"),
    ],
}


def photo_path(n, width=None):
    """Photograph n (1 is the lead), at its full cut or at a given width."""
    suffix = f"-{width}" if width else ""
    return f"{IMG_DIR}/{SLUG}-{n}{suffix}.webp"


def hero_path(width):
    """The lead photograph cropped for the News page's carousel."""
    return f"{IMG_DIR}/{SLUG}-hero-{width}.webp"


def photo_url(n):
    return f"{IMAGE_HOST}{PHOTOS[n - 1][0]}.webp"


def _prepare():
    """Give the article the fields news_article_html reads."""
    figs = []
    for n, (_id, alt) in enumerate(PHOTOS, 1):
        src = photo_path(n)
        w, h = webp_size(src)
        figs.append({"src": src, "alt": alt, "w": w, "h": h})
    ARTICLE["inline"] = {}
    ARTICLE["image"], ARTICLE["image_alt"] = figs[0]["src"], figs[0]["alt"]
    ARTICLE["image_size"] = (figs[0]["w"], figs[0]["h"])
    ARTICLE["figures"] = figs[1:]


ARTICLES = [ARTICLE]

_prepare()
