"""The photographs on the Arts, Music & Theatre wall, and their captions.

One list, read by tools/build-site.py, which writes it into the page as an
inert <template>. assets/js/artswall.js reads the wall's photographs back out
of that template, so there is no second copy to keep in step — and because the
paths sit in href and src attributes, tools/check-links.py sees every file the
wall uses and would catch one that went missing.

The files themselves are cut by tools/make-arts-wall.py. Adding a photograph
means adding it there and here.

Captions describe what is in the frame and nothing more. Where a photograph
was already captioned for the archive, that caption is kept as it was. Dates,
names, ensembles and productions are the school's to supply; none are invented
here.
"""

# name (matching assets/img/arts/<name>.jpg), category, caption
PHOTOGRAPHS = [
    # Music
    ("guitars",        "Music",        "Guitars, in the music room"),
    ("tabla",          "Music",        "Tabla and percussion"),
    ("band",           "Music",        "The band, outside the block"),

    # Dance
    ("bharatanatyam",  "Dance",        "Bharatanatyam, under the lights"),
    ("ensemble",       "Dance",        "The ensemble, mid-phrase"),
    ("juniors",        "Dance",        "The junior school on stage"),
    ("dance",          "Dance",        "Bharatanatyam, New Year"),
    ("stage",          "Dance",        "Annual day, on stage"),

    # Theatre
    ("mime",           "Theatre",      "Mime, in white masks"),
    ("tableau",        "Theatre",      "In costume, a tableau"),
    ("masks",          "Theatre",      "Masks, made for the stage"),

    # Visual art
    ("banner",         "Visual Art",   "Painting the banner"),
    ("exhibition",     "Visual Art",   "The exhibition, being read"),
    ("handwork",       "Visual Art",   "Handwork, on display"),
    ("floorwork",      "Visual Art",   "Working on the floor"),

    # Student work — the paintings themselves, captioned as the archive had them
    ("paint1",         "Student Work", "Rain, Grade IV"),
    ("paint2",         "Student Work", "Blossom and lamplight"),
    ("paint3",         "Student Work", "Sun and butterfly, Grade IV"),
    ("paint4",         "Student Work", "At the window, Grade VIII"),
    ("paint5",         "Student Work", "Figure with birds, Grade XII"),

    # The stage itself
    ("amphitheatre",   "The Stage",    "The amphitheatre, after dark"),
    ("festival",       "The Stage",    "The festival stage, set"),

    # SPIC MACAY — visiting professional musicians and dancers, not students.
    # The society's banner is in the frame of the concert photograph.
    ("spic-sarod",     "SPIC MACAY",   "A visiting recital, strings and tabla"),
    ("spic-kathakali", "SPIC MACAY",   "Visiting artists, in full costume"),
    ("spic-dancers",   "SPIC MACAY",   "Visiting dancers, held mid-figure"),
    ("spic-dancer",    "SPIC MACAY",   "A visiting dancer, alone on stage"),
    ("spic-concert",   "SPIC MACAY",   "A SPIC MACAY concert, on stage"),
    ("spic-tabla",     "SPIC MACAY",   "A visiting tabla player"),
]

DIR = "assets/img/arts"


def full(name):
    return f"{DIR}/{name}.jpg"


def thumb(name):
    return f"{DIR}/thumbs/{name}.jpg"


def count():
    return len(PHOTOGRAPHS)


def categories():
    """The categories, in the order they first appear above."""
    seen = []
    for _, cat, _ in PHOTOGRAPHS:
        if cat not in seen:
            seen.append(cat)
    return seen
