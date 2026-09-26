"""CIRS Festivals — the photographs, the year index and the India calendar.

Every photograph on the page is one of the school's own, taken at the
festival its caption names. Nothing here was inferred from a costume or a
colour: each file came out of a named event folder in the school's Drive
(CIRS Studio, or the social-media account's per-year selections), and where
the camera's clock was right its EXIF date agrees with the festival. Where
the clock was wrong the caption gives the year only, and BASIS says why.

The originals, cut to 2000px, are in assets/source/festivals (never
deployed). tools/make-festivals.py cuts the WebP files the page uses into
assets/img/festivals and records their sizes in tools/festivals-images.json,
which is what this module reads — so the site build needs no image library.

Two things are kept apart on purpose, and the page keeps them apart too:

    FESTIVALS  the seven celebrations documented at CIRS, with evidence
    INDIA      a wider calendar of Indian festivals, each with its sources,
               which makes no claim that CIRS held the celebration. Where the
               school does have evidence of one, CIRS_NOTE says what it is.

Drive folders, for the record (owner: cirsstudio@ unless noted):
    Raksha Bandhan   2023 / 60.Raksha bandhan
    Janmashtami      2026 / New Academic Year / 37. Krishna Janmashtami /
                     Mahant, Tanmay  (socialmedia@ subfolders)
    Onam             2023 / 59. Onam / pookolam, lunch;
                     2024 / New Academic year 24-25 / Onam
    Ganesh           2023 / 67. Ganesh Utsav / GANESH VISARJAN
    Dussehra         2025 / New Academic year / 45. Dussehra /
                     Mahant, Abarna  (socialmedia@ subfolders)
    Pongal           2026 / 4. Pongal / Prahalad, Radha  (socialmedia@)
    Holi             2026 / 19. Holi;  Batch of 2026 / 2025 / 10. Holi /
                     Dhuleti  (socialmedia@)
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "festivals-images.json")

# How each photograph's occasion is known.
EXIF = "event folder, and the camera's date agrees"
FOLDER = "event folder and upload date (the camera's clock was wrong)"

# name: (festival, year, when, caption, alt, drive id, original, basis)
PHOTOS = {
    # Raksha Bandhan, 30 August 2023, 07:45-08:18
    "rakhi-knot": ("raksha-bandhan", 2023, "30 August 2023",
        "A rakhi knotted at the wrist", "A student's hands knotting a thread rakhi on a classmate's wrist",
        "194YT-chUBi6WOExoHKFkahOvAsy7vY8X", "IMG_9875.JPG", EXIF),
    "rakhi-thali": ("raksha-bandhan", 2023, "30 August 2023",
        "The thali before the tying: rakhis, roli, rice and chocolate",
        "A leaf plate holding thread rakhis, red roli, yellow rice and chocolates",
        "15F6sRo2avNWcCrNJJ9IdfoWRfNrhbXvQ", "IMG_9870.JPG", EXIF),
    "rakhi-sweets": ("raksha-bandhan", 2023, "30 August 2023",
        "Chocolate, offered from the plate", "Hands reaching for chocolates from a plate held out by a student",
        "1EgXNA8hmxkAtWmNxdCPf-XlU6AL7e4Qi", "IMG_9887.JPG", EXIF),
    "rakhi-courtyard": ("raksha-bandhan", 2023, "30 August 2023",
        "Rakhis tied across the courtyard", "Students in festive clothes tying rakhis on one another in a courtyard",
        "1MEN2qYNBWu_ZCBlTQAHzr2gynka5_Gs1", "IMG_9898.JPG", EXIF),
    "rakhi-pairs": ("raksha-bandhan", 2023, "30 August 2023",
        "Pairs of students across the courtyard", "Students standing in pairs, some tying rakhis and some smiling at the camera",
        "1PHBEhs5xclbn4RfUylH8HQEfatZsEUfR", "IMG_9928.JPG", EXIF),
    "rakhi-teacher": ("raksha-bandhan", 2023, "30 August 2023",
        "A rakhi for a teacher", "A student tying a rakhi on a teacher's wrist in the courtyard",
        "1Ykm2PYHC0H_xSUjU-leNU87vRILAmrl4", "IMG_9936.JPG", EXIF),
    "rakhi-friends": ("raksha-bandhan", 2023, "30 August 2023",
        "Tilak on the forehead, and a smile", "Two girls with tilak on their foreheads smiling at the camera",
        "1INZiqP1cSW6fpiFvhcdRDMxgmzE2syCo", "IMG_9918.JPG", EXIF),

    # Janmashtami, 4-5 September 2026
    "jan-pooja": ("janmashtami", 2026, "4 September 2026",
        "The morning pooja before the Krishna murti", "Teachers seated on either side of a flower-decked altar with a white Krishna murti",
        "1hmvgwYy2STBV92tsFw30PZ78cNHU2ItH", "_MG_1260.JPG", EXIF),
    "jan-aarti": ("janmashtami", 2026, "4 September 2026",
        "Aarti at the garlanded murti", "A teacher waving an aarti lamp before a garlanded murti",
        "1V9K2OV8WY8zVjE-ldF31VaI68jSTJEqA", "_MG_1279.JPG", EXIF),
    "jan-singer": ("janmashtami", 2026, "4 September 2026",
        "A bhajan at the microphone", "A student singing at a microphone before a red and gold projected mandala",
        "14-lumbDZriHRpcb43PLTNipV3H3WeWnb", "_MG_1316.JPG", EXIF),
    "jan-cajon": ("janmashtami", 2026, "4 September 2026",
        "The cajon keeps the bhajan's time", "A student playing a cajon on stage under violet light",
        "1JpvERH4QMD9Rw1i5mCuXyjTcxM2YUjNh", "_MG_1311.JPG", EXIF),
    "jan-dancers": ("janmashtami", 2026, "4 September 2026",
        "Dancers in the hall before midnight", "Girls in mirrored skirts dancing in the hall under warm light",
        "1VrylNUos-8NXpYjq3ueb5O1KY2D5o134", "_MG_1334.JPG", EXIF),
    "jan-dance": ("janmashtami", 2026, "4 September 2026",
        "A dance in red and gold", "Students in red and gold costume and headbands dancing close to the audience",
        "1Mxo9NwtAru_mzf_kttQrc7r9nKQVq52b", "_MG_1346.JPG", EXIF),
    "jan-bhajan": ("janmashtami", 2026, "4 September 2026",
        "Bhajan singers on stage", "A group of students seated on stage singing before a blue projected mandala",
        "1R2tMWFvzaktZJeJbVDbDkHTBdPQhMIiX", "_MG_1353.JPG", EXIF),
    "jan-lamps": ("janmashtami", 2026, "4 September 2026",
        "Just before midnight, the hall dark but for the lamps",
        "A dark hall with a portrait on stage lit only by lamps before it",
        "1h5aKRlF9m04a8LvMyqvyW7gdOE6Bi5HI", "DSC_3231.JPG", EXIF),
    "jan-reach": ("janmashtami", 2026, "5 September 2026",
        "A hand reaches for the matki", "A student on the shoulders of others reaching up for a clay pot hung from a rope, after dark",
        "1MZkqgUasJbNkyVIQ2PxJ1bfYxlSezesc", "DSC_3303.JPG", EXIF),
    "jan-pyramid": ("janmashtami", 2026, "5 September 2026",
        "The pyramid rises under the tree", "Students building a human pyramid under a tree at night, a pot hanging above them",
        "1gS93evaKCtlAZXmEZt6LCzRn5qU2KzYR", "DSC_3316.JPG", EXIF),
    "jan-crowd": ("janmashtami", 2026, "5 September 2026",
        "The school gathers under the rope", "A crowd of students under a tree at night, looking up at a pot on a rope",
        "1PZRbRfDCP_Wa_bMIDTGSCnyghwH4K3Xk", "DSC_3326.JPG", EXIF),
    "jan-break": ("janmashtami", 2026, "5 September 2026",
        "The matki breaks", "A student at the top of a human pyramid strikes the pot, and its contents burst out in the floodlight",
        "14kjSJ_bpx_ag3M-dhN2w8BOkpM5ruQq_", "DSC_3336.JPG", EXIF),
    "jan-tower": ("janmashtami", 2026, "5 September 2026",
        "Another grade, another tower", "A human pyramid climbing towards a pot hung high in the dark",
        "1hptWKmqgdkTMW6Ic0Ucoq9i-bxjVCVqy", "DSC_3345.JPG", EXIF),
    "jan-lawn": ("janmashtami", 2026, "5 September 2026",
        "After the matki, the lawn full of students", "Students crowded on a lawn at night under the trees and lamps",
        "1RufvBieQWSfOpcL_uWiZFxXj74x6Jr4u", "DSC_3354.JPG", EXIF),

    # Onam, 2023 (camera clock wrong) and 15 September 2024
    "onam-petals": ("onam", 2023, "2023",
        "Petals sorted for the pookalam", "Hands sorting marigold and rose petals on the floor beside a half-laid pookalam",
        "1-dfCms0p3GyOTnmCW2UshAY9xs15F1Qt", "CRS09824.JPG", FOLDER),
    "onam-pookalam": ("onam", 2023, "2023",
        "A finished pookalam in the courtyard", "A circular flower pookalam in yellow, orange and purple laid on a courtyard floor",
        "1imgH0O8SSd6VU56n6iBEZQAh6N41jKe5", "CRS09832.JPG", FOLDER),
    "onam-lamps": ("onam", 2023, "2023",
        "The pookalam and its two lamps", "A large flower pookalam on the dining-hall floor between two lit brass lamps",
        "1klk1FdflCjOszRuiP3lemX5qv1YG0018", "CRS09886.JPG", FOLDER),
    "onam-sadhya": ("onam", 2023, "2023",
        "The sadhya, served on banana leaves", "A long row of students seated on the floor eating the sadhya from banana leaves",
        "1CT9wcmT4Xm6dAFjZfAGcjlnzjQcSald2", "CRS09899.JPG", FOLDER),
    "onam-sadhya-row": ("onam", 2023, "2023",
        "The rows run the length of the hall", "Girls seated in a row on the floor with banana leaves before them, the row running into the distance",
        "1XyYMkuZw11b5pTQguYHRhQBQBE-PUVOO", "CRS09916.JPG", FOLDER),
    "onam-leaf": ("onam", 2023, "2023",
        "Rice, and every curry after it", "A student in a white mundu eating rice from a banana leaf",
        "1qiDQ1vI3tLVgt1hobbMmFA9rXpXZr4kk", "CRS09940.JPG", FOLDER),
    "onam-song": ("onam", 2024, "15 September 2024",
        "Teachers sing in kasavu on Thiruvonam evening", "Teachers in cream and gold kasavu singing together on stage",
        "1d7TZqBsHzdOdp_rtosGE-A4LK09YbLbT", "IMG_8484.JPG", EXIF),
    "onam-dance": ("onam", 2024, "15 September 2024",
        "A dance in white mundu", "Students in white mundu and dark tops dancing on a stage hung with painted suns",
        "1hU5loEDAiY00mbaUAxx2m1QIWq8QR929", "IMG_8495.JPG", EXIF),

    # Ganesh Chaturthi immersion, 28 September 2023, 17:11-17:30
    "ganesh-lake": ("ganesh-chaturthi", 2023, "28 September 2023",
        "The murti crosses the school's lake", "A raft carrying the Ganesh murti crossing a lake below cloud-covered hills",
        "1NH1-EPU3Jl37jEbQjND7x_fVwGjJHxcz", "IMG_3019.JPG", EXIF),
    "ganesh-far": ("ganesh-chaturthi", 2023, "28 September 2023",
        "Far out on the lake, under the hills", "A small raft far out on a still lake, forested hills and cloud behind it",
        "12HDG1bZbmusaQ4IMTbfhGHr9ApKgpO9J", "IMG_3047.JPG", EXIF),
    "ganesh-reflection": ("ganesh-chaturthi", 2023, "28 September 2023",
        "The raft and its reflection", "A raft with the murti and a group aboard, reflected in green water",
        "10Zz20KBgyELDtSJBOCVqXM7SR7W2U5C5", "IMG_3022.JPG", EXIF),
    "ganesh-raft": ("ganesh-chaturthi", 2023, "28 September 2023",
        "The murti on the raft, banana stems at its corners",
        "The Ganesh murti on a raft decorated with banana stems, teachers standing around it",
        "17pbesjlAerhJMFlzAHoPl8gRT9a1tYRl", "IMG_3035.JPG", EXIF),
    "ganesh-immersion": ("ganesh-chaturthi", 2023, "28 September 2023",
        "The immersion", "The murti being lowered from the raft into the lake",
        "1XNfSqsOLtNpdJB3uC2Ytzq705aM9a4TR", "IMG_3053.JPG", EXIF),
    "ganesh-bank": ("ganesh-chaturthi", 2023, "28 September 2023",
        "On the bank, in saffron", "Girls in saffron kurtas seated close together on the bank, cheering",
        "107bslZiptQInKPw-bOvcyP2uGkOHxXvY", "IMG_3028.JPG", EXIF),
    "ganesh-cheer": ("ganesh-chaturthi", 2023, "28 September 2023",
        "Voices in unison on the shore", "A group of girls in saffron laughing together by the water",
        "1doob71ZILIZ6Cxt4DQB7DxAiAErQtZ-1", "IMG_3039.JPG", EXIF),
    "ganesh-boys": ("ganesh-chaturthi", 2023, "28 September 2023",
        "The procession gathers", "Boys in saffron kurtas gathered together, smiling at the camera",
        "1lpTSIzROMsVjsBC7Wsk5lYLimJVNbduw", "IMG_3007.JPG", EXIF),

    # Dussehra, Vijayadashami 2 October 2025
    "dussehra-procession": ("dussehra", 2025, "2 October 2025",
        "The procession sets out", "Students in costume as Rama, Lakshmana and Hanuman leaving a building by torchlight",
        "1S-ckAEgPapqgHrzAd_HKtO7qCorg6_XY", "IMG_7947.JPG", EXIF),
    "dussehra-torches": ("dussehra", 2025, "2 October 2025",
        "By torchlight, towards the field", "Students in costume walking in procession by the light of flaming torches",
        "13_PJoiPEaCBkEMZsfVe-LcUd7gN4G5S0", "IMG_7995.JPG", EXIF),
    "dussehra-rama": ("dussehra", 2025, "2 October 2025",
        "Rama, with bow and torch", "A student in costume as Rama holding a bow beside a burning torch",
        "1ejPV3g_DYGqUoh0fPvd93y_ccwjZ5py7", "IMG_8033.JPG", EXIF),
    "dussehra-fire": ("dussehra", 2025, "2 October 2025",
        "Ravan Dahan", "The ten-headed Ravan effigy burning against the night sky",
        "1Xe6BszKk-xFGvQ2SBUtG2ZTsqFdJx0RG", "IMG_8087.JPG", EXIF),
    "dussehra-dance": ("dussehra", 2025, "2 October 2025",
        "Dance on the field under floodlights", "Students in saffron dancing on the field at night under floodlights",
        "1OC1N_0xy5c-95e5tnJ-q1AgtpLWgoONI", "IMG_8137.JPG", EXIF),
    "dussehra-effigy": ("dussehra", 2025, "2025",
        "The effigy waits on the field", "The ten-headed Ravan effigy standing on the dark field before it is lit",
        "1idYHssACfy_dTwD77__IctUMC6n6_3sR", "DSC03997.JPG", FOLDER),
    "dussehra-embers": ("dussehra", 2025, "2025",
        "The last of the fire", "The Ravan effigy burning in the distance against a black sky",
        "1oho-BTz5UuPWU43XsD70nnt-FHTozS8l", "DSC04015.JPG", FOLDER),

    # Pongal, 15 January 2026
    "pongal-altar": ("pongal", 2026, "15 January 2026",
        "An offering at the Pongal altar", "A girl placing an offering on an altar hung with sugarcane, marigold garlands, fruit and a brass lamp",
        "1TTHLnovECNuoYdBUTyUSfWCMocanRLgo", "IMG_0033.JPG", EXIF),
    "pongal-pooja": ("pongal", 2026, "15 January 2026",
        "The Pongal pooja in the courtyard", "A teacher lighting lamps at an altar hung with sugarcane and marigolds in a sunlit courtyard",
        "1fn7EjL0zTyGi-KsoFrW8uNq7Wr3SSAVz", "IMG_0029.JPG", EXIF),
    "pongal-veshti": ("pongal", 2026, "15 January 2026",
        "In white veshti for the harvest", "A group of boys in white shirts and veshti posing together in the sun",
        "1bu9xG9kzuPwimq6cURSkxh_mmvPdBmo0", "IMG_0053.JPG", EXIF),
    "pongal-pot": ("pongal", 2026, "2026",
        "A pongal pot, painted and tied with turmeric", "A painted clay pot tied with turmeric leaves on a wooden board",
        "1PTNX5ORVJr2AQfWj3mJOk1INqfYQu3aU", "CRS09395.JPG", FOLDER),

    # Holi, 4 March 2026 and 2025 (clock wrong)
    "holi-hills": ("holi", 2026, "4 March 2026",
        "Colour on the field, the hills behind", "Students playing with colour on a dry field, rocky hills behind them",
        "1DXMpYZkJZPAVqRQuBcsCJPCq4zDHC9PG", "IMG_20260304_082300.jpg", EXIF),
    "holi-crowd": ("holi", 2026, "4 March 2026",
        "The whole field at once", "A crowd of students in colour-streaked clothes on the field under trees",
        "1761MDAY7z919fZdxdgdJd3ILf6se83qo", "IMG_20260304_082439.jpg", EXIF),
    "holi-field": ("holi", 2026, "4 March 2026",
        "Holi on the field", "Students with colour on their faces and clothes crossing the playing field",
        "1maydxnoUazlDxxtt4mqnxTERjXYrhWwQ", "IMG_20260304_082658.jpg", EXIF),
    "holi-boy": ("holi", 2026, "4 March 2026",
        "Colour finds its owner", "A boy in an orange CIRS shirt covered in colour, grinning, a friend behind him",
        "1fj1znBOxBoe21DQoQCXoWQLZKkBuWLtN", "IMG_20260304_082858.jpg", EXIF),
    "holi-friends": ("holi", 2025, "2025",
        "Two friends, two colours", "Two students standing together, faces streaked with pink and yellow colour",
        "1Udw7nn4qG_hFvi4BjXF_KtvInyxbcqSJ", "IMG_4943.JPG", FOLDER),
    "holi-face": ("holi", 2025, "2025",
        "Every colour at once", "A student's face covered in blue, pink and yellow colour, smiling in low sunlight",
        "1-P-s4bFd_jCU-ussM6cAkPpyuh8DXXuJ", "IMG_4948.JPG", FOLDER),
    "holi-colour": ("holi", 2025, "2025",
        "Colour, pressed to a cheek", "A hand pressing colour onto a student's cheek, both faces already bright with it",
        "1MoHPcb4IluS2wA_z1D4uRkPD8ytTCfh1", "IMG_4950.JPG", FOLDER),
    "holi-portrait": ("holi", 2025, "2025",
        "Green and pink to the hairline", "A student looking into the camera, face coated in green and pink colour",
        "13KlbVqJUCUDyi_qssbUxz8FlmFZScqeq", "IMG_4958.JPG", FOLDER),
}

# The seven celebrations, in the order the school year meets them. The month
# ranges are ranges because the dates move with the lunar calendar; Pongal
# alone is fixed to the solar year.
FESTIVALS = [
    ("raksha-bandhan",   "Raksha Bandhan",   "July&ndash;August",       "rakhi-teacher",  "01"),
    ("janmashtami",      "Janmashtami",      "August&ndash;September",  "jan-tower",      "02"),
    ("onam",             "Onam",             "August&ndash;September",  "onam-pookalam",  "03"),
    ("ganesh-chaturthi", "Ganesh Chaturthi", "August&ndash;September",  "ganesh-reflection", "04"),
    ("dussehra",         "Dussehra",         "September&ndash;October", "dussehra-embers", "05"),
    ("pongal",           "Pongal",           "January",                 "pongal-pot",     "06"),
    ("holi",             "Holi",             "March",                   "holi-face",      "07"),
]
NAMES = {slug: name for slug, name, *_ in FESTIVALS}

# Where the opening strip's narrow crops sit in each landscape photograph, so
# the tile holds the hands, the murti or the face rather than the gap between.
STRIP_POS = {
    "rakhi-teacher": "72% 55%",
    "ganesh-reflection": "46% 50%",
    "holi-face": "52% 40%",
}

# The archive: every photograph not already used in a chapter, the night
# sequence or the opening strip, so nothing on the page is shown twice.
# Grouped by festival, in the year's order.
ARCHIVE = [
    "rakhi-courtyard", "rakhi-pairs", "rakhi-friends",
    "jan-aarti", "jan-cajon", "jan-dancers", "jan-bhajan", "jan-crowd",
    "onam-sadhya-row", "onam-leaf", "onam-song", "onam-dance",
    "ganesh-boys", "ganesh-cheer", "ganesh-far",
    "dussehra-procession", "dussehra-rama", "dussehra-dance",
    "pongal-veshti",
    "holi-hills", "holi-crowd", "holi-friends",
]

# Moments the page's own copy describes and no photograph yet shows. Said
# plainly under the archive rather than papered over with a nearby picture.
GAPS = ("the pongal being cooked in small groups, the Dussehra rangolis, the "
        "students&rsquo; own Ganesh murtis, the Onam skit of Mahabali, the Holika "
        "skit and the Raksha Bandhan evening programme")

# ---------------------------------------------------------------------------
# Festivals across India. Short descriptions in the site's own words; the
# sources are recorded here, not on the page. None of these is a claim about
# CIRS. CIRS_NOTE marks the two for which the school has its own evidence.
BRIT = "https://www.britannica.com/topic/"
INDIA = [
    ("January&ndash;February", "winter", [
        ("Lohri", "Around 13 January",
         "A winter bonfire festival of Punjab and much of north India, with songs, dancing and "
         "offerings of peanuts, rewri and popcorn to the fire.",
         [BRIT.replace("topic/", "question/What-is-Lohri-and-when-is-it-celebrated")]),
        ("Makar Sankranti", "Mid-January",
         "The sun's passage into Makara, kept across India under many names &mdash; kites for "
         "Uttarayan in Gujarat, sesame and jaggery in Maharashtra, new-rice sweets in Bengal.",
         [BRIT + "Makar-Sankranti"]),
        ("Basant Panchami", "January&ndash;February",
         "The fifth day of Magha, welcoming spring. In many homes and schools it is Saraswati's "
         "day, the goddess of learning, and a day for yellow.",
         [BRIT + "Vasant-Panchami"]),
        ("Maha Shivaratri", "February&ndash;March",
         "A night of fasting and vigil for Shiva, kept in temples and homes across the country.",
         [BRIT + "Mahashivaratri"]),
    ]),
    ("March&ndash;May", "spring", [
        ("Ugadi and Gudi Padwa", "March&ndash;April",
         "The lunisolar New Year: Ugadi in Karnataka, Andhra Pradesh and Telangana, with its "
         "chutney of six tastes; Gudi Padwa in Maharashtra and Goa, with a gudi raised at the door.",
         [BRIT + "Ugadi"]),
        ("Ram Navami", "March&ndash;April",
         "The birth of Rama, on the ninth day of Chaitra, marked with readings of the Ramayana, "
         "temple worship and processions.",
         [BRIT + "Rama-Navami"]),
        ("Mahavir Jayanti", "March&ndash;April",
         "The birth of Vardhamana Mahavira, the twenty-fourth Tirthankara of the Jain tradition, "
         "with processions, worship and giving.",
         [BRIT + "Mahavira-Jayanti"]),
        ("Easter", "March&ndash;April",
         "The Christian feast of the Resurrection, closing Holy Week, kept by churches across India.",
         [BRIT + "Easter-holiday"]),
        ("Baisakhi", "13 or 14 April",
         "The spring harvest festival of Punjab, when the wheat is ready. For Sikhs it also "
         "remembers the founding of the Khalsa in 1699.",
         [BRIT + "Baisakhi"]),
        ("The New Year in mid-April", "Around 14 April",
         "The solar New Year, under many names: Tamil Puthandu, Vishu in Kerala, Bohag Bihu in "
         "Assam, Pohela Boishakh in Bengal and Maha Vishuva Sankranti in Odisha.",
         ["https://www.incredibleindia.gov.in/en/festivals-and-events", BRIT + "Bihu"]),
        ("Buddha Purnima", "April&ndash;May",
         "The full moon remembering the Buddha's birth, enlightenment and passing, also called "
         "Buddha Jayanti.",
         [BRIT + "Vesak"]),
    ]),
    ("June&ndash;September", "monsoon", [
        ("Rath Yatra", "June&ndash;July",
         "Jagannath, Balabhadra and Subhadra drawn through the streets of Puri on great wooden "
         "chariots in the month of Ashadha, with processions in many other cities.",
         [BRIT + "Rathayatra"]),
    ]),
    ("October&ndash;December", "autumn", [
        ("Navaratri and Durga Puja", "September&ndash;October",
         "Nine nights of the Goddess: garba and dandiya in Gujarat, golu in the south, and in "
         "Bengal Durga Puja, recognised by UNESCO in 2021 as intangible cultural heritage.",
         [BRIT + "Durga-Puja", "https://ich.unesco.org/en/RL/durga-puja-in-kolkata-01503"]),
        ("Diwali", "October&ndash;November",
         "The festival of lamps. Hindus mark Rama's return and worship Lakshmi, Jains the "
         "nirvana of Mahavira, and Sikhs keep Bandi Chhor Divas on the same day.",
         [BRIT + "Diwali-Hindu-festival"]),
        ("Chhath", "October&ndash;November",
         "Four days of worship of the Sun in Bihar and eastern Uttar Pradesh, with offerings "
         "at the riverbank to both the setting and the rising sun.",
         ["https://www.incredibleindia.gov.in/en/festivals-and-events/chhath-puja"]),
        ("Guru Nanak Gurpurab", "October&ndash;November",
         "The birth of Guru Nanak, founder of the Sikh faith, on the full moon of Kartik: a "
         "continuous reading of the Guru Granth Sahib, processions and langar.",
         ["https://www.britannica.com/science/calendar/The-sacred-calendar"]),
        ("Christmas", "25 December",
         "The birth of Jesus, kept by Christian communities across India with midnight services, "
         "carols and paper stars.",
         [BRIT + "Christmas"]),
    ]),
    ("Through the year", "lunar", [
        ("Eid al-Fitr", "Moves about eleven days earlier each year",
         "The end of Ramadan, the month of fasting, with morning prayers, new clothes and meals "
         "shared with family and neighbours.",
         [BRIT + "Id-al-Fitr"]),
        ("Eid al-Adha", "Moves about eleven days earlier each year",
         "The Feast of Sacrifice at the close of the Hajj, remembering Ibrahim's devotion, with "
         "prayers and meat shared with family, neighbours and those in need.",
         [BRIT + "Id-al-Adha"]),
    ]),
]

# The two index entries the school has its own evidence for, and the evidence.
CIRS_NOTE = {
    "The New Year in mid-April": (
        'Vishu and Tamil Puthandu were kept in the CIRS dorms in April 2025 &mdash; '
        '<a href="news.html#more">see News</a>.'),
    "Navaratri and Durga Puja": (
        "The school's photo archive holds Navaratri evenings at CIRS from 2023 to 2025; "
        "their story is still to be written here."),
}


def _sizes():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)["images"]


def _esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def src(name, width=None):
    """The path of one cut of a photograph: the largest unless asked."""
    info = _sizes()[name]
    w = width or max(info["widths"])
    return f"assets/img/festivals/{name}-{w}.webp"


def img(name, sizes, cls="", eager=False, alt=None, pos=None):
    """One photograph, with every cut in its srcset.

    Below the fold unless eager: lazy-loaded and decoded off the main thread.
    The width and height are the largest cut's, so the box is reserved before
    a byte of the image arrives.
    """
    info = _sizes()[name]
    widths = sorted(info["widths"])
    srcset = ", ".join(f"assets/img/festivals/{name}-{w}.webp {w}w" for w in widths)
    big = widths[-1]
    h = round(info["h"] * big / info["w"])
    load = ('fetchpriority="high" decoding="async"' if eager
            else 'loading="lazy" decoding="async"')
    text = _esc(alt if alt is not None else PHOTOS[name][4])
    style = f' style="object-position:{pos}"' if pos else ""
    klass = f' class="{cls}"' if cls else ""
    return (f'<img{klass} src="assets/img/festivals/{name}-{widths[0] if len(widths) > 1 else big}.webp" '
            f'srcset="{srcset}" sizes="{sizes}" width="{big}" height="{h}" alt="{text}"{style} {load}>')


def caption(name):
    fest, _year, when, cap, *_ = PHOTOS[name]
    return f'{cap} <span class="fx-when">{NAMES[fest]}, {when}</span>'


def expand(html):
    """Fill the page's tokens.

        {{FX_IMG name | sizes | class | eager | object-position}}
        {{FX_CAP name}}       the caption, with festival and verified date
        {{FX_STRIP}}          the opening's seven photographs
        {{FX_INDEX}}          the sticky year index
        {{FX_ARCHIVE}}        the archive grid, its filters and its note
        {{FX_INDIA}}          the India calendar
        {{FX_GAPS}}           the moments no photograph yet shows
    """
    def fimg(m):
        parts = [p.strip() for p in m.group(1).split("|")]
        name, sizes = parts[0], parts[1]
        cls = parts[2] if len(parts) > 2 else ""
        eager = len(parts) > 3 and parts[3] == "eager"
        pos = parts[4] if len(parts) > 4 and parts[4] else None
        return img(name, sizes, cls, eager, pos=pos)
    html = re.sub(r"\{\{FX_IMG ([^}]+)\}\}", fimg, html)
    html = re.sub(r"\{\{FX_CAP ([a-z0-9-]+)\}\}", lambda m: caption(m.group(1)), html)
    return (html.replace("{{FX_STRIP}}", strip_html())
                .replace("{{FX_INDEX}}", index_html())
                .replace("{{FX_ARCHIVE}}", archive_html())
                .replace("{{FX_INDIA}}", india_html())
                .replace("{{FX_GAPS}}", GAPS))


# The width each photograph is actually drawn at, measured at every one of
# assets/css/festivals.css's breakpoints (520, 820, 1100px). The images are
# cover-fitted, so a box taller than the photograph needs more than its own
# width: a one-column tile on a phone draws a 3:2 photograph about 1.2 times
# the window's width. Earlier values described a four-column grid at every
# width, which sent a tablet the 640px cut for a 707px tile.
SIZES_STRIP = "(max-width: 520px) 87vw, (max-width: 820px) 74vw, (max-width: 1100px) 56vw, 23vw"
SIZES_TILE = "(max-width: 520px) 120vw, (max-width: 820px) 123vw, (max-width: 1100px) 61vw, 520px"


def strip_html():
    """Seven photographs across the opening, one to a festival, in the year's
    order. Each is a link to its chapter: the opening is also the year's
    table of contents."""
    items = []
    for i, (slug, name, months, photo, n) in enumerate(FESTIVALS):
        pic = img(photo, SIZES_STRIP, "fx-strip__img",
                  eager=True, alt="", pos=STRIP_POS.get(photo))
        items.append(f'''      <li class="fx-strip__item" style="--i:{i}">
        <a class="fx-strip__link" href="#{slug}">
          {pic}
          <span class="fx-strip__label"><span class="fx-strip__months">{months}</span>
          <span class="fx-strip__name">{name}</span></span>
        </a>
      </li>''')
    return ('<ol class="fx-strip" aria-label="The CIRS festival year, from July to March">\n'
            + "\n".join(items) + "\n    </ol>")


def index_html():
    """The slim index that follows the reader through the seven chapters."""
    links = "\n".join(
        f'      <li><a class="fx-index__link" href="#{slug}" data-fx-index="{slug}">'
        f'<span class="fx-index__n">{n}</span><span class="fx-index__name">{name}</span></a></li>'
        for slug, name, months, photo, n in FESTIVALS)
    return f'''<nav class="fx-index" aria-label="The festival year">
  <div class="fx-index__bar">
    <p class="fx-index__label" aria-hidden="true">The year</p>
    <ol class="fx-index__list">
{links}
    </ol>
    <span class="fx-index__track" aria-hidden="true"><i class="fx-index__fill"></i></span>
  </div>
</nav>'''


def archive_html():
    """The archive: filters, a grid of tiles and the note on what is missing.

    Each tile is a link to its largest cut, so without scripting it simply
    opens the photograph; with it, the viewer opens instead. The filters are
    buttons with aria-pressed, and the count under them is announced.
    """
    years = sorted({PHOTOS[n][1] for n in ARCHIVE})
    fests = [f for f in FESTIVALS if any(PHOTOS[n][0] == f[0] for n in ARCHIVE)]
    fbtns = ['      <button type="button" class="fx-chip" data-fx-filter="festival" data-value="all" aria-pressed="true">All festivals</button>']
    fbtns += [f'      <button type="button" class="fx-chip" data-fx-filter="festival" data-value="{slug}" aria-pressed="false">{name}</button>'
              for slug, name, *_ in fests]
    ybtns = ['      <button type="button" class="fx-chip" data-fx-filter="year" data-value="all" aria-pressed="true">Every year</button>']
    ybtns += [f'      <button type="button" class="fx-chip" data-fx-filter="year" data-value="{y}" aria-pressed="false">{y}</button>'
              for y in years]
    tiles = []
    for i, name in enumerate(ARCHIVE):
        fest, year, when, cap, alt, *_ = PHOTOS[name]
        info = _sizes()[name]
        shape = "tall" if info["h"] > info["w"] else "wide"
        pic = img(name, SIZES_TILE, "fx-tile__img")
        tiles.append(f'''    <li class="fx-tile fx-tile--{shape}" data-festival="{fest}" data-year="{year}">
      <a class="fx-tile__link" href="{src(name)}" data-fx-open="{i}"
         data-caption="{_esc(cap)}" data-when="{_esc(NAMES[fest] + ', ' + when)}">
        {pic}
      </a>
      <p class="fx-tile__cap">{cap}<span class="fx-when">{NAMES[fest]}, {when}</span></p>
    </li>''')
    return f'''<div class="fx-filters" role="group" aria-label="Filter the archive">
  <div class="fx-filters__row" aria-label="By festival" role="group">
{chr(10).join(fbtns)}
  </div>
  <div class="fx-filters__row" aria-label="By year" role="group">
{chr(10).join(ybtns)}
  </div>
  <p class="fx-filters__count" data-fx-count aria-live="polite">{len(ARCHIVE)} photographs</p>
</div>
<ul class="fx-grid" data-fx-grid>
{chr(10).join(tiles)}
</ul>
<p class="fx-grid__empty" data-fx-empty hidden>No photograph in the archive matches both filters yet.</p>'''


def india_html():
    groups = []
    for label, key, items in INDIA:
        rows = []
        for name, when, text, _sources in items:
            note = CIRS_NOTE.get(name)
            note = (f'\n          <p class="fx-cal__cirs"><span class="fx-cal__cirs-label">At CIRS</span>{note}</p>'
                    if note else "")
            rows.append(f'''        <li class="fx-cal__item">
          <h4 class="fx-cal__name">{name}</h4>
          <p class="fx-cal__when">{when}</p>
          <p class="fx-cal__text">{text}</p>{note}
        </li>''')
        groups.append(f'''    <div class="fx-cal__season" id="india-{key}" role="group" aria-labelledby="india-{key}-h">
      <h3 class="fx-cal__season-h" id="india-{key}-h">{label}</h3>
      <ul class="fx-cal__list">
{chr(10).join(rows)}
      </ul>
    </div>''')
    jumps = "\n".join(f'    <a class="fx-cal__jump" href="#india-{key}">{label}</a>'
                      for label, key, _ in INDIA)
    return f'''<nav class="fx-cal__jumps" aria-label="Seasons">
{jumps}
  </nav>
  <div class="fx-cal">
{chr(10).join(groups)}
  </div>'''


def count():
    return len(PHOTOS)
