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

The opened CIRS Cultural Gallery photographs remain in the school's shared
Drive and use its 1600px image endpoint. Their 420px tile renditions are kept
locally so the moving wall appears immediately without downloading the large
camera originals.
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

    # CIRS Cultural Gallery — filenames are retained where they carry a title;
    # camera filenames are given neutral labels rather than invented context.
    ("drive-01", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 01"),
    ("drive-02", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 02"),
    ("drive-03", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 03"),
    ("drive-04", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 04"),
    ("drive-05", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 05"),
    ("drive-06", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 06"),
    ("drive-07", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 07"),
    ("drive-08", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 08"),
    ("drive-09", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 09"),
    ("drive-10", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 10"),
    ("drive-11", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 11"),
    ("drive-12", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 12"),
    ("drive-13", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 13"),
    ("drive-14", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 14"),
    ("drive-15", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 15"),
    ("drive-16", "CIRS Cultural Gallery", "Unfold — The Voice of Transformation"),
    ("drive-17", "CIRS Cultural Gallery", "Unfold 2 — artwork 4"),
    ("drive-18", "CIRS Cultural Gallery", "Unfold 2 — artwork 3"),
    ("drive-19", "CIRS Cultural Gallery", "Unfold 2 — artwork 1"),
    ("drive-20", "CIRS Cultural Gallery", "Gurudev Aradhana"),
    ("drive-21", "CIRS Cultural Gallery", "Story 2 — artwork 2"),
    ("drive-22", "CIRS Cultural Gallery", "Story 2 — artwork 1"),
    ("drive-23", "CIRS Cultural Gallery", "Story 2"),
    ("drive-24", "CIRS Cultural Gallery", "AU Program — artwork 2"),
    ("drive-25", "CIRS Cultural Gallery", "AU Program — artwork 1"),
    ("drive-26", "CIRS Cultural Gallery", "AU Program"),
    ("drive-27", "CIRS Cultural Gallery", "Crossroads 20"),
    ("drive-28", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 28"),
    ("drive-29", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 29"),
    ("drive-30", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 30"),
    # drive-31 was the amphitheatre photograph above, a second time.
    ("drive-32", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 32"),
    ("drive-33", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 33"),
    ("drive-34", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 34"),
    ("drive-35", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 35"),
    ("drive-36", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 36"),
    ("drive-37", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 37"),
    ("drive-38", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 38"),
    ("drive-39", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 39"),
    ("drive-40", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 40"),
    ("drive-41", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 41"),
    ("drive-42", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 42"),
    ("drive-43", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 43"),
    ("drive-44", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 44"),
    ("drive-45", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 45"),
    ("drive-46", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 46"),
    ("drive-47", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 47"),
    ("drive-48", "CIRS Cultural Gallery", "CIRS cultural gallery photograph 48"),
]

DIR = "assets/img/arts"

DRIVE_IDS = {
    "drive-01": "1ovsB76NFcBwwwZaMEAT1YkaZoUiO4w1e",
    "drive-02": "1D5yQyB1q4xdDp-Q5iy0u4CfGIY8K-w6w",
    "drive-03": "118WJtsLm84IcTTZni9GJOdH_dvKBztCZ",
    "drive-04": "1yTL186-mADqlAYUTir6o-LzqVamXZLdU",
    "drive-05": "1AewZ5oFZCiQwKAkWWIo7LeyRbunUmVgs",
    "drive-06": "1y_EZLJ4CPVfkbouBxVv5Lg9JAVAE19FQ",
    "drive-07": "10AKDkdvn6KK2MFEmJ_mBr695hEPxNtoB",
    "drive-08": "1pvyRi5EivAfIpdNOYSyeUJDw_UFO7wus",
    "drive-09": "19WgS_f8eAm509uJhe4nkzRda-7I5zgvm",
    "drive-10": "19yQdujoNtjZ1Ii1Z9P0Qq1UPTOGAQU_j",
    "drive-11": "1spjnMA2o99YYegEqVDQOxxDl_7fX-LyW",
    "drive-12": "113544sqwvhCloNJmHS5KFl-vefABYs1h",
    "drive-13": "1y7zb7gQVwpuths0JGEn_mW96QSy8UHL6",
    "drive-14": "17flEEdk_wSrBK2CDrYlTc1q_8DAlQulp",
    "drive-15": "1g6In1aiVsjbuec9joinSkUU-aTqz533O",
    "drive-16": "1x_8CwzIHFlw1AGfoNC9QWnDJEIXXyaAk",
    "drive-17": "143Sr9ktPiQnsmulLmR_qqnMRoIA6xqWs",
    "drive-18": "1L-p_QsE1qqUIBlbE4rT65Wxm62aatqpL",
    "drive-19": "1u1yHQFdpk4L83NJJPvlhTyPj_g3Svz9x",
    "drive-20": "1O0tv8_QfosDCUJcSbr4yTK92L6EUTecO",
    "drive-21": "1Lbrxj6zPQyeMS2gPz1Q4rhiVK-jLdq3r",
    "drive-22": "1jaSXyFPJJ-Sfe3Tx0yCucWWuk4Q25l-O",
    "drive-23": "1DCMAATJMNIoWxTyUuYLZ1xLm3Zl9ft3s",
    "drive-24": "1s_pKN_BHj9D50Q8u830jTf7S6V1LzWUL",
    "drive-25": "10eyNddMkouQFUmE4G4z0Iuw63an0W9o6",
    "drive-26": "1YekJ8Vwi_B6BjVoigDN7jpfcvnz_RW88",
    "drive-27": "1h5-H43f4Bo1ZnRyAj90wDpDtdDc_W-nh",
    "drive-28": "1SjhGvyDNHybNi3OhNeD1vZjo-l0vfm1Q",
    "drive-29": "1r4bn0szqYB_i-mSuldxitsI-N-tkau2S",
    "drive-30": "11HA5xoqGAxewgVzeh3TM3PppvYev3ydI",
    "drive-32": "1WXXFAVYlxKh2oIDuo8KbtnAaMHyHQlqs",
    "drive-33": "15XLVfpC-ku-xLNxBPm6n8y70CPvQwBlq",
    "drive-34": "17eSe_RrLEvuErwJy0Qu2Ew2SPyLZFi1i",
    "drive-35": "1V2qJbbaLi7w7ibC2O4-Y5kMCD49OvILm",
    "drive-36": "1U3a6rktdmKDfB4hQk8ORO_PR6Wau6CLG",
    "drive-37": "1BYcosqP2CUqrB9BcRp3gVdf1yhKO8dBI",
    "drive-38": "1td2J-DBmdQglv7R9ipomguSIF6imqodO",
    "drive-39": "1cccSDakP850BhLJtQ65eacHvXG8iNk_S",
    "drive-40": "1TWlbjArXKJxBrNd2CJpqqyvsvtlWD_rz",
    "drive-41": "1sE29U_XritU9e_1Azx03FHhvK4DtUwxG",
    "drive-42": "1sFKdi5AkEcb8KvcU3TU04I3YnO_CfzHi",
    "drive-43": "1LCavK2TYVWLcsmVNr8Dh9yn7mh8YWDFi",
    "drive-44": "1mtke6DV1TzpBfnahtg8SaaDYTck7u_kw",
    "drive-45": "11ng9M1eVUq1y5ULXu5tLhrHz-LGAz0_g",
    "drive-46": "1qh4LqV0spT3lyQpqYUlCtTF0clJAF_pi",
    "drive-47": "1SApLBkb9H3EiG-SDo9Os_KVrUPheHfiK",
    "drive-48": "1xCuNw9X22rcjeN65qUHBk0UNgL7FvAH9",
}


def drive_image(name, width):
    file_id = DRIVE_IDS[name]
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{width}"


def full(name):
    if name in DRIVE_IDS:
        return drive_image(name, 1600)
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
