"""CIRS Theatre — the media manifest and the markup built from it.

Every photograph on the Theatre page after its opening is listed here, with
where it came from: the school's Google Drive file (by id and by its camera
filename), the folder it sits in, the event, the house, the year and the
production. tools/make-theatre.py cuts the files from this list, and
tools/build-site.py writes the page's three acts from it, so there is one
record of what each picture is and nothing on the page can drift from it.

What is known and what is not
-----------------------------
  * House and production are taken from the Drive folder a photograph sits in
    ("Masquerade 2024/Vyasa") and from the school's own YouTube titles for the
    same evening ("Iridescente | CIRS - Vyasa House Masquerade - 2024"). Never
    from the colour of a costume.
  * The Anand Utsav photographs are all from the evening cultural programme of
    Anand Utsav 2024, 15 October — the second day. The Drive folder is
    "Anand utsav 2024 phtoos/day 1 and 2"; only frames the camera dated
    15 October are used, which is the evening the school's Anand Utsav
    Bulletin (October 2024) schedules the Annual Day programme. The title is
    the one the school gave its recording on YouTube.
  * Captions describe what is in the frame. No character is named and no
    scene is explained: the school has not published cast lists or synopses,
    and a plausible guess would read as fact.
  * The exact evening of each 2024 house play is not stated anywhere the
    school has published. Two of the cameras disagree by a day, so the page
    says November 2024 and no more.

Everything with a URL here was checked against the school's channel,
youtube.com/@CIRS-YouTube (channel UCqtdZclBQYN_BfJCyZY7WVg): the video exists,
plays, and was uploaded by that channel. Durations are YouTube's own.
"""

DIR = "assets/img/theatre"
CHANNEL = "https://www.youtube.com/@CIRS-YouTube"
CLASS_PLAYLIST = "https://www.youtube.com/playlist?list=PLjprqkMR0QoY-Wg1DkYqtn5MiPAzVStN3"
DRIVE_FILE = "https://drive.google.com/file/d/{}/view"

# ---------------------------------------------------------------- photographs
#
# name: the file stem in assets/img/theatre
# drive: the Drive file id;  file: its camera filename;  folder: its Drive folder
# src: the original's size (after EXIF rotation);  focus: x, y of the subject,
#      0..1, used where a frame is cropped to fill a space
# alt: what the picture shows;  caption: a short line for the lightbox and grid
# size: "xl" for a full-bleed image, which is cut larger


def photo(name, drive, file, folder, src, alt, caption, focus=(0.5, 0.5), size="l"):
    return {"name": name, "drive": drive, "file": file, "folder": folder, "src": src,
            "alt": alt, "caption": caption, "focus": focus, "size": size}


AU_FOLDER = "Anand Utsav 2024 / Anand utsav 2024 phtoos / day 1 and 2"

ANAND_UTSAV = {
    "event": "Anand Utsav 2024",
    "year": 2024,
    "date": "15 October 2024",
    "title": "Transforming Lives! Transforming Vision!",
    # The school's own recording of this evening's theatre programme.
    "recording": {"id": "hWddJ6T9H2c", "title": "Transforming Lives ! Transforming Vision! | Anand Utsav 2024 | Theater Show",
                  "length": "68:21"},
    # The frame the act opens on, in near darkness, before the lights come up.
    "dark": photo("au-telephone", "1paWhgIFxCQO7dt7HGFTPbgEdFHReNWLl", "0C9A3627.JPG", AU_FOLDER, (8192, 4608),
                  "A student in a red kurta alone on a darkened stage, holding a telephone receiver",
                  "A single light, a single voice", (0.46, 0.4), "xl"),
    # The image that carries the act: the whole stage, the whole cast.
    "wide": photo("au-forest", "1CowC58S9mzt-UaFBrU7IYTrCQhTwFxg3", "0C9A3714.JPG", AU_FOLDER, (8192, 4608),
                  "A forest scene filling the stage: a large cast in costume under red light before a backdrop of trees",
                  "The full stage, under red light", (0.5, 0.62), "xl"),
    # The sequence after it, in the order the page shows them.
    "sequence": [
        photo("au-court", "1IDBUyO00Bn784kNGhg__GXySNFsb6EGQ", "0C9A3579.JPG", AU_FOLDER, (8192, 5464),
              "A royal court scene: seated figures in rich costume, guards with spears and a painted palace behind them",
              "A court, in full costume", (0.5, 0.55)),
        photo("au-soldiers", "1rX0o82KLX4bRbq-473YFz8mYBGIELFtZ", "0C9A3659.JPG", AU_FOLDER, (8192, 4608),
              "A long line of students in army fatigues before a mountain backdrop",
              "An ensemble in uniform, across the whole stage", (0.5, 0.6), "xl"),
        photo("au-dance", "1lPmlRFvvNymSQK2736973e9BqUA3os-x", "0C9A3762.JPG", AU_FOLDER, (8192, 4608),
              "Dancers in violet, white and lilac before a painted palace",
              "Dancers before the palace", (0.5, 0.55)),
        photo("au-sage", "1I9hmEP_ZOCe9rzvOXwuiFjstju9qPvzT", "0C9A3753.JPG", AU_FOLDER, (4608, 8192),
              "A student made up as a white-haired sage in saffron, one arm raised, under violet light",
              "One figure, one light", (0.5, 0.4)),
        photo("au-finale", "1rgsEdQeCCHpCIy3eGfCQgxYFCekd9tZo", "0C9A3819.JPG", AU_FOLDER, (8192, 4608),
              "Hundreds of students crowded together on the stage, under a backdrop reading Transforming Lives",
              "Hundreds on the stage together", (0.5, 0.55), "xl"),
    ],
    # Other years of the same programme on the school's channel.
    "more": [
        {"id": "-QrRDoSJ9Ww", "title": "Maryada Purushottham", "note": "Anand Utsav 2025 · Theater show", "length": "67:36"},
        {"id": "XZg-NTpB1zo", "title": "Dharmo Rakshati Rakshitah", "note": "Anand Utsav 2023 · Cultural programme", "length": "66:22"},
        {"id": "g_uTAO3wsO0", "title": "CIRS Anand Utsav – 2019", "note": "Recorded live", "length": "79:17"},
    ],
}


def mq(house):
    return f"Masquerade 2024 / {house}"


# The act's opening frame. Its folder is Vasistha's; it is not repeated in
# that house's gallery.
MASQUERADE_OPENER = photo(
    "mq-painted-face", "1dE3fugHbeWllfbO2thN5xg-9YcOtGFtD", "DSC00142.JPG", mq("Vasishtha"), (4000, 6000),
    "A student in dark body paint, half lit, looking out from the shadows",
    "Vasistha House, Incursion, 2024", (0.5, 0.3))

# The four houses, in the order the site lists them elsewhere (Student Life,
# Sports). The spelling is the site's; the school's own titles also write
# Vasishta, Vasishtha and Vashistha, which are the same house.
HOUSES = [
    {
        "id": "vasistha", "name": "Vasistha", "numeral": "I",
        "title": "Incursion", "year": 2024,
        "drive_folder": "Masquerade 2024 / Vasishtha",
        "recording": {"id": "T0EEKg1t92g", "length": "63:50",
                      "title": "Incursion | CIRS - Vasishta House Masquerade - 2024"},
        "trailer": {"id": "mcS44liPzw8", "length": "2:06"},
        # The photograph on this house's card in the programme index. It is one
        # of the house's own and is not shown again in the gallery.
        "card": "vasistha-skull-staff",
        # The gallery as rows: feature (one large, two beside it), full (one
        # across the width), trio (three even) and duo (two, offset).
        "layout": [
            ("feature", ["vasistha-elder-violet", "vasistha-forest-dance", "vasistha-green-light"]),
            ("full", ["vasistha-full-stage"]),
            ("trio", ["vasistha-lights", "vasistha-body-paint", "vasistha-blue-light"]),
            ("duo", ["vasistha-foliage", "vasistha-red-cloth"]),
            ("full", ["vasistha-green-costumes"]),
            ("duo", ["vasistha-round-window", "vasistha-off-stage"]),
        ],
        "lead": photo("vasistha-hut", "1mmnwb2b9goe7c-9_ZH5pxfSSmbhTxgIY", "CRS06384.JPG", mq("Vasishtha"), (6000, 3376),
                      "Inside a thatched hut set: an elder in white holding a carved staff, and a younger actor leaning in",
                      "Inside the hut", (0.45, 0.45), "xl"),
        "gallery": [
            photo("vasistha-elder-violet", "1OYpeUmMHTZUMJ7FugALJ5RZZUhE744tm", "CRS06347.JPG", mq("Vasishtha"), (6000, 3376),
                  "Under violet light, an elder in white with a staff, and a figure in purple holding up a shell",
                  "Under violet light", (0.65, 0.4)),
            photo("vasistha-forest-dance", "1aSdHMTK1phcvbsm0vS9AbJCJyS3apPuA", "CRS06422.JPG", mq("Vasishtha"), (6000, 3376),
                  "A dance in the forest set: an actor in braces among dancers in floral dresses",
                  "A dance in the forest", (0.45, 0.45)),
            photo("vasistha-skull-staff", "1yihrCJb8yOmhM_CPYf6Y5SWveb2Q3zfe", "CRS06683.JPG", mq("Vasishtha"), (3376, 6000),
                  "A figure in black holding a staff topped with a skull",
                  "The skull-topped staff", (0.5, 0.35)),
            photo("vasistha-full-stage", "1U2X9Zz3glEuVvnx1d2jW-J7Qx5njkj94", "IMG_9065.JPG", mq("Vasishtha"), (2400, 1344),
                  "The whole stage: a forest set lit violet, dancers in pink and white, and one actor in braces",
                  "The whole stage", (0.5, 0.6)),
            photo("vasistha-green-light", "1zWZl4oqSGWKDRttJDtnLj9XodLYkxMQo", "CRS06603.JPG", mq("Vasishtha"), (6000, 3376),
                  "The cast in green light, several in white face paint",
                  "In green light", (0.5, 0.5)),
            photo("vasistha-lights", "1pvXOKu5Z28uxZGTKNlbuEG6lhay83mxp", "CRS06782.JPG", mq("Vasishtha"), (6000, 3376),
                  "A figure in a pointed hat and cloak in a set strung with fairy lights, a young actor beside",
                  "Among the strings of light", (0.45, 0.5)),
            photo("vasistha-body-paint", "1zy2irwMSEhF2Uh7bQ2t6_ldsdfK51vDC", "CRS06840.JPG", mq("Vasishtha"), (6000, 3376),
                  "An actor with a painted back raises a staff overhead above another",
                  "Body paint and a raised staff", (0.5, 0.4)),
            photo("vasistha-blue-light", "1W9jTumzH-WI2MIofezWXkMk19QC2ZSio", "CRS06954.JPG", mq("Vasishtha"), (6000, 3376),
                  "An actor, arms flung wide, in a single blue light",
                  "Arms wide, in blue light", (0.5, 0.45)),
            photo("vasistha-foliage", "19IUGJi0mNsdEcMPNQrHuy58rdEF6pFAr", "DSC00004.JPG", mq("Vasishtha"), (6000, 4000),
                  "An actor in dark body paint crouches forward in front of green-lit foliage",
                  "In the foliage", (0.55, 0.45)),
            photo("vasistha-red-cloth", "1ZIhhWezewwvkktMZM_Lh-QMSmgSh0y9P", "DSC00009.JPG", mq("Vasishtha"), (6000, 4000),
                  "Two actors in the forest set, one wrapped in red cloth",
                  "Two actors in the forest", (0.55, 0.45)),
            photo("vasistha-round-window", "1sXbmCtJYZ3FciyF_SU_BAwtIRwbegumP", "DSC00129.JPG", mq("Vasishtha"), (6000, 4000),
                  "Three actors in casual clothes in a room set with a round window",
                  "A room with a round window", (0.5, 0.45)),
            photo("vasistha-green-costumes", "1moelEla23JS7pH_CdkAYLt2sFZ4r4V02", "IMG_9107.JPG", mq("Vasishtha"), (2400, 1344),
                  "The cast in green costumes surging across the stage with staffs, the audience close in front",
                  "The cast in green, across the stage", (0.5, 0.55)),
            photo("vasistha-off-stage", "1TR8Lq9GNGa5ngSrnXzaE3O8RvmDVPKqv", "IMG_9274.JPG", mq("Vasishtha"), (2400, 1344),
                  "Off stage: cast members in face paint grinning at the camera",
                  "Off stage, still in paint", (0.5, 0.5)),
        ],
        "more": [
            {"id": "xXx1UMMRg6k", "title": "Vantara — Trailer 1", "note": "Vasishta Productions · uploaded January 2026", "length": "1:58"},
            {"id": "ahsfpRphrww", "title": "Vantara — Trailer 2", "note": "Vasishta Productions · uploaded January 2026", "length": "1:05"},
            {"id": "irgJPObYt6Q", "title": "The Anarchist — Trailer", "note": "Masquerade 2022 · with Vishwamitra House", "length": "1:38"},
            {"id": "hdKRmW4mnIk", "title": "Masquerade Trailer", "note": "2018", "length": "1:19"},
            {"id": "y1Lr7ViWMcE", "title": "Masquerade Trailer", "note": "2017", "length": "1:39"},
            {"id": "fVA42gm00PY", "title": "Masquerade Trailer", "note": "2016", "length": "1:30"},
            {"id": "7Boq4RjnQ30", "title": "Zangoora — Trailer", "note": "2015", "length": "2:17"},
            {"id": "SsI4Tm5PP8Q", "title": "Masquerade Trailer", "note": "2013", "length": "2:47"},
        ],
    },
    {
        "id": "valmiki", "name": "Valmiki", "numeral": "II",
        "title": "Maledictus", "year": 2024,
        "drive_folder": "Masquerade 2024 / Valmiki",
        "recording": {"id": "fIMCetOlzCQ", "length": "67:23",
                      "title": "Maledictus | CIRS - Valmiki House Masquerade - 2024"},
        "trailer": {"id": "LDQe07FKQ3c", "length": "1:43"},
        "card": "valmiki-spotlight",
        "layout": [
            ("feature", ["valmiki-hat-jacket", "valmiki-grey-paint", "valmiki-staff"]),
            ("full", ["valmiki-ribbons"]),
            ("trio", ["valmiki-grip", "valmiki-reach", "valmiki-star"]),
            ("duo", ["valmiki-rope", "valmiki-struggle"]),
            ("full", ["valmiki-smoke"]),
            ("duo", ["valmiki-sound-desk", "valmiki-company"]),
        ],
        "lead": photo("valmiki-song", "1Z9oqKIWqGXNRtYJ3co8SfvYi2X7Asetz", "CRS05946.JPG", mq("Valmiki"), (6000, 3376),
                      "An actor in a wide-brimmed hat and braces sings with arms open, dancers with blue silks behind",
                      "A song, with the whole company behind", (0.5, 0.4), "xl"),
        "gallery": [
            photo("valmiki-hat-jacket", "1dJtxJoTOocerjfrZCWWRyCi7lXGN4Zj4", "CRS06062.JPG", mq("Valmiki"), (6000, 3376),
                  "An actor in a wide-brimmed hat faces another in a leather jacket",
                  "Face to face", (0.45, 0.45)),
            photo("valmiki-spotlight", "1oRNYhmcI3Yh_3DwUP3laTZz1qNAMPXEb", "CRS06091.JPG", mq("Valmiki"), (6000, 3376),
                  "An actor alone under a spotlight, a figure in the dark behind",
                  "Alone in the spotlight", (0.6, 0.45)),
            photo("valmiki-grey-paint", "1qUXv__P7xvFctHDVb2ixNxVNtVOVXiEo", "CRS06078.JPG", mq("Valmiki"), (6000, 3376),
                  "An actor painted grey leans on another in a hat",
                  "Grey paint and a battered hat", (0.55, 0.45)),
            photo("valmiki-ribbons", "1XPRMqNTmfzZsE6z66bKP0UdbjNb_cR2S", "IMG_8845.JPG", mq("Valmiki"), (2400, 1344),
                  "The whole stage: dancers with blue silks above, and the company in front of the audience",
                  "Blue silks across the stage", (0.5, 0.5)),
            photo("valmiki-staff", "1rccisPLB3VfV0SKOf67EIOeHyCnvzg_j", "CRS06028.JPG", mq("Valmiki"), (6000, 3376),
                  "Two actors in dark body paint, one holding a tall staff, with two actors in costume between them",
                  "The staff-bearers", (0.5, 0.45)),
            photo("valmiki-grip", "17nngyE4TmbAU9J8FBh0InN0Xk6ymyZCc", "CRS06102.JPG", mq("Valmiki"), (6000, 3376),
                  "In blue light, a cloaked figure grips another actor from behind while a third, in a green waistcoat, watches",
                  "In blue light", (0.45, 0.5)),
            photo("valmiki-reach", "1ZJwGQH5HSVLxNJyOQDkru5b3Cwe-b_0w", "CRS06168.JPG", mq("Valmiki"), (6000, 3376),
                  "An actor holding a tall staff reaches out an arm, the forest set dark behind",
                  "A staff, and an outstretched arm", (0.65, 0.5)),
            photo("valmiki-star", "17YPhwIHOIGJs5igfcIdC9PLgu6Fd6SLO", "CRS06265.JPG", mq("Valmiki"), (6000, 3376),
                  "Three actors around a glowing star-shaped prop",
                  "The star", (0.4, 0.5)),
            photo("valmiki-rope", "1uihCmaQXF3s5WXEhrhjjomp8SpbZjRxG", "CRS06306.JPG", mq("Valmiki"), (6000, 3376),
                  "An actor swings a coil of rope in blue light, the audience seated close around the stage floor",
                  "Among the audience", (0.5, 0.45)),
            photo("valmiki-struggle", "1MGH0Vk_teMBLujyW_xtK8VgIRVx_Hdng", "CRS06315.JPG", mq("Valmiki"), (6000, 3376),
                  "Two actors locked together in a struggle in blue light",
                  "A struggle in the dark", (0.5, 0.55)),
            photo("valmiki-smoke", "18zEXzvrS0qxoPRYuLmIy9mnYtDDQcehN", "IMG_8878.JPG", mq("Valmiki"), (2400, 1344),
                  "Actors in body paint, and one in white holding a staff that trails smoke",
                  "Smoke from the staff", (0.6, 0.45)),
            photo("valmiki-sound-desk", "10UiLMp2OaneNv6V5U-AZDqqjNJjifF-w", "CRS05942.JPG", mq("Valmiki"), (6000, 3376),
                  "A mixing desk, a laptop and a monitor speaker in the sound booth",
                  "The sound booth", (0.5, 0.5)),
            photo("valmiki-company", "1-GJuGuwU4L-VFMVbGvVMv2ZaI0GRYlSY", "IMG_9028.JPG", mq("Valmiki"), (2400, 1344),
                  "The company gathered together on the hall floor in front of the stage",
                  "The company", (0.5, 0.55)),
        ],
        "more": [
            {"id": "EfzbNboA4TE", "title": "Melora", "note": "Masquerade 2025", "length": "1:17"},
            {"id": "P4GGqjywNhQ", "title": "Inscenare — Trailer", "note": "Masquerade 2022 · with Vyasa House", "length": "1:38"},
            {"id": "YMccsEUTFmo", "title": "Masquerade Trailer", "note": "2018", "length": "2:01"},
            {"id": "Gfq8MvXjejk", "title": "Masquerade Trailer", "note": "2017", "length": "2:03"},
            {"id": "8bFocvpMhVs", "title": "Masquerade Trailer", "note": "2016", "length": "1:53"},
            {"id": "ZRIpcIDuCYg", "title": "The Aladdin — Trailer", "note": "2015", "length": "2:14"},
            {"id": "7boWOTghbtg", "title": "Masquerade Trailer", "note": "2013", "length": "2:02"},
        ],
    },
    {
        "id": "vishwamitra", "name": "Vishwamitra", "numeral": "III",
        "title": "The Imperium", "year": 2024,
        "drive_folder": "Masquerade 2024 / Vishwamitra",
        "recording": {"id": "ZlWd-PLTHaI", "length": "73:59",
                      "title": "The Imperium | CIRS - Vishwamitra House Masquerade - 2024"},
        "trailer": {"id": "2MzXLwLoszE", "length": "2:03"},
        "card": "vishwamitra-gold",
        "layout": [
            ("feature", ["vishwamitra-make-up", "vishwamitra-face-paint", "vishwamitra-backdrop"]),
            ("full", ["vishwamitra-curtain"]),
            ("duo", ["vishwamitra-seated", "vishwamitra-portrait"]),
            ("trio", ["vishwamitra-bed", "vishwamitra-armour", "vishwamitra-aisle"]),
            ("full", ["vishwamitra-beam"]),
            ("duo", ["vishwamitra-close", "vishwamitra-steps"]),
            ("full", ["vishwamitra-banner"]),
        ],
        "lead": photo("vishwamitra-swords", "1Hgo4HDwwkgTzsgsfDlRQRgYscZ5p1csp", "CRS05851.JPG", mq("Vishwamitra"), (6000, 3376),
                      "Two actors with swords among the cast, before a painted backdrop of houses and mountains",
                      "Swords drawn, the village behind", (0.5, 0.4), "xl"),
        "gallery": [
            photo("vishwamitra-make-up", "1akbrCz-DdM2jioCvYKWRTVtep62kFLog", "CRS05380.JPG", mq("Vishwamitra"), (6000, 3376),
                  "Backstage: several students painting one actor's face and chest",
                  "Backstage, in make-up", (0.5, 0.45)),
            photo("vishwamitra-backdrop", "1D2HGcVJGPBPn060OjAcPHeQ-Xx7jmi7h", "IMG_1194.JPG", mq("Vishwamitra") + " / Behind The Scenes", (6000, 4000),
                  "Students kneeling on a large cloth outdoors, painting it in sweeps of turquoise",
                  "Painting a backdrop", (0.45, 0.55)),
            photo("vishwamitra-face-paint", "1LqJLsQpie_EQxjkMxhpU8T0_yYkPnfDB", "CRS05384.JPG", mq("Vishwamitra"), (6000, 3376),
                  "A smiling actor in white and gold face paint",
                  "Face paint, close up", (0.5, 0.4)),
            photo("vishwamitra-portrait", "11Ocy_OMSYExoU1v_DQ4meatBEs9UThXM", "CRS05930.JPG", mq("Vishwamitra") + " / Behind The Scenes", (3376, 6000),
                  "A cast member with white face paint and dark eyeliner, looking to one side",
                  "Before going on", (0.5, 0.35)),
            photo("vishwamitra-curtain", "1LGzNY4sBp5QCdPr5PZmwq438zCb-hBUi", "IMG_8768.JPG", mq("Vishwamitra"), (2400, 1344),
                  "The whole cast in a line, hands raised, before the painted backdrop of houses and mountains",
                  "The whole company, hands raised", (0.5, 0.6)),
            photo("vishwamitra-seated", "1Bw0pJa8vegEPHMLDBsyxAP_C1Lrv2xjM", "CRS05395.JPG", mq("Vishwamitra"), (6000, 3376),
                  "An actor seated on a draped block, arms spread wide in the dark",
                  "Arms spread, in the dark", (0.5, 0.45)),
            photo("vishwamitra-gold", "1BeFS6DBIRQVXQSPgmBDQnVnWkOSIoCRH", "CRS05406.JPG", mq("Vishwamitra"), (6000, 3376),
                  "An actor in gold body paint raises a sword, a figure in black standing behind",
                  "Gold paint, sword raised", (0.6, 0.45)),
            photo("vishwamitra-bed", "124AsQewVSKToFzys39Uiow9VO8ICNAjI", "CRS05482.JPG", mq("Vishwamitra"), (6000, 3376),
                  "Two actors sitting on the edge of a bed in a room set",
                  "A quieter scene", (0.6, 0.5)),
            photo("vishwamitra-armour", "1hZRdwUhMVf2eIoqEPBuqoxAfTip2w_sc", "CRS05541.JPG", mq("Vishwamitra"), (6000, 3376),
                  "A figure in black armour in a doorway lit blue and white, another actor watching",
                  "The armoured figure", (0.6, 0.45)),
            photo("vishwamitra-aisle", "1VJL_tD1oMmDTghj9VX8iRMpxiq430HbF", "CRS05613.JPG", mq("Vishwamitra"), (6000, 3376),
                  "An actor with a sword walks the aisle between rows of seated students",
                  "Down the aisle", (0.45, 0.5)),
            photo("vishwamitra-close", "1EDyRcbcsox--86d4hoOIbODxZAt20ymd", "CRS05682.JPG", mq("Vishwamitra"), (6000, 3376),
                  "An actor in a white shirt, arms held wide, close to the camera",
                  "Close enough to touch", (0.55, 0.4)),
            photo("vishwamitra-steps", "1Kw7H92NgOlShWcmvCdAagoRfldI2WFG8", "CRS05761.JPG", mq("Vishwamitra"), (6000, 3376),
                  "A figure in dark costume crouches on draped steps",
                  "On the steps", (0.55, 0.5)),
            photo("vishwamitra-beam", "1S2_z-gbhHjqAineYBD1mZFCPmMlp6BF0", "IMG_8771.JPG", mq("Vishwamitra"), (2400, 1344),
                  "An actor lit by a single beam of light, students seated in the dark around",
                  "One beam of light", (0.55, 0.5)),
            photo("vishwamitra-banner", "1aSLrr16aAYzm97171AFgpop2JEkcFHjz", "IMG_8834.JPG", mq("Vishwamitra"), (2400, 1344),
                  "The company cheering under a banner reading The Imperium",
                  "Under the banner", (0.5, 0.55)),
        ],
        "more": [
            {"id": "G5C-ZwOjFfc", "title": "El Diablo — Trailer", "note": "Vishwamitra Productions · uploaded January 2026", "length": "1:31"},
            {"id": "irgJPObYt6Q", "title": "The Anarchist — Trailer", "note": "Masquerade 2022 · with Vasistha House", "length": "1:38"},
            {"id": "TBc2QiQpxgE", "title": "Masquerade Trailer", "note": "2018", "length": "2:14"},
            {"id": "YtkRYZAH6mY", "title": "Masquerade Trailer", "note": "2017", "length": "2:26"},
            {"id": "LP_ya4AeLRo", "title": "Masquerade Trailer", "note": "2016", "length": "2:07"},
            {"id": "epJFbrfj85A", "title": "Lincoln", "note": "Masquerade 2015 · the production", "length": "81:33"},
            {"id": "G0dKF5LcYHs", "title": "Lincoln — Trailer", "note": "2015", "length": "2:14"},
            {"id": "x6qiFz3deYo", "title": "Masquerade Trailer", "note": "2013", "length": "1:41"},
        ],
    },
    {
        "id": "vyasa", "name": "Vyasa", "numeral": "IV",
        "title": "Iridescente", "year": 2024,
        "drive_folder": "Masquerade 2024 / Vyasa",
        "recording": {"id": "QB5y9Y4h-k0", "length": "68:00",
                      "title": "Iridescente | CIRS - Vyasa House Masquerade - 2024"},
        "trailer": {"id": "XgO-X6jokU0", "length": "2:01"},
        "card": "vyasa-turn",
        "layout": [
            ("feature", ["vyasa-court", "vyasa-green-mask", "vyasa-gold-gown"]),
            ("full", ["vyasa-tea-table"]),
            ("trio", ["vyasa-lunge", "vyasa-crouch", "vyasa-staff"]),
            ("duo", ["vyasa-kick", "vyasa-sashes"]),
            ("full", ["vyasa-banner"]),
            ("duo", ["vyasa-top-hat", "vyasa-kneel"]),
            ("full", ["vyasa-company"]),
        ],
        "lead": photo("vyasa-throne", "1VbaEz4GPC8CncpssJsko-US2DpwkLZaW", "CRS07138.JPG", mq("Vyasa"), (6000, 3376),
                      "A crowned figure on a throne beneath a lit heart, holding a white orb",
                      "The heart throne", (0.5, 0.45), "xl"),
        "gallery": [
            photo("vyasa-banner", "1Lody4uNEEeaGiqmDagNwPlTOrJvKEac_", "CRS07019.JPG", mq("Vyasa"), (6000, 3376),
                  "A hand-painted banner reading Iridescente above the stage",
                  "The banner", (0.5, 0.35)),
            photo("vyasa-green-mask", "14INMUv2FoN-V2-PsIDnFjJ7NmW2pQD9d", "CRS07014.JPG", mq("Vyasa"), (6000, 3376),
                  "A cast member in green spotted face paint and yellow spectacles",
                  "Green paint, yellow spectacles", (0.4, 0.45)),
            photo("vyasa-gold-gown", "1jN2_yoBQZSjzz6dS98A2wvcQebobXYB0", "CRS07027.JPG", mq("Vyasa"), (6000, 3376),
                  "A figure in a gold gown walks through the seated audience in blue light",
                  "Through the audience", (0.45, 0.45)),
            photo("vyasa-court", "1vBL9eiAttvIYPGfIEBUFjVF09bTixjyK", "CRS07060.JPG", mq("Vyasa"), (6000, 3376),
                  "A figure in a green jacket and a crowned figure with a staff before the heart set",
                  "At the heart set", (0.45, 0.45)),
            photo("vyasa-tea-table", "1-RaX4g915bL7Tz6yFyKnr6Sh5NTImWbL", "CRS07344.JPG", mq("Vyasa"), (6000, 3376),
                  "Actors crowded around a tea table beneath balloons and hanging lights",
                  "Around the tea table", (0.5, 0.5)),
            photo("vyasa-lunge", "1Pvr_6kHU-l-KMm95qSwoUQr_axKuLoJl", "CRS07193.JPG", mq("Vyasa"), (6000, 3376),
                  "A figure in patterned body paint lunges low before the crowned figure holding an orb",
                  "The lunge", (0.4, 0.55)),
            photo("vyasa-kick", "17YdBHLao-FXBxUSRC_0IlEOwR6ARwRyb", "CRS07359.JPG", mq("Vyasa"), (6000, 3376),
                  "A dancer in white kicks forward in front of the ensemble",
                  "The ensemble dances", (0.5, 0.5)),
            photo("vyasa-turn", "1DZNAszxdfrZkncsgeXfHIG-Nqu1KRav9", "DSC00159.JPG", mq("Vyasa"), (6000, 4000),
                  "A performer in a white and gold dress, mid-turn, arms out",
                  "Mid-turn", (0.5, 0.4)),
            photo("vyasa-sashes", "1tHUf2_UjUMzQTDsVreYF5J8DdNfSpPR9", "DSC00172.JPG", mq("Vyasa"), (6000, 4000),
                  "Dancers in black with red sashes, hands raised",
                  "Black and red", (0.45, 0.45)),
            photo("vyasa-top-hat", "18yENMxRARfKyHg3I00s8LEny-6yKYKW5", "DSC00197.JPG", mq("Vyasa"), (6000, 4000),
                  "A figure in a tall hat and polka-dot sleeves beside a figure in an orange fur coat",
                  "A tall hat and an orange coat", (0.5, 0.4)),
            photo("vyasa-crouch", "1qt6R9cl5n9TTxKmqbtBMZ-Wjlr337Xm6", "DSC00293.JPG", mq("Vyasa"), (6000, 4000),
                  "A figure in patterned body paint crouches low against red drapes",
                  "Against the red drapes", (0.5, 0.5)),
            photo("vyasa-kneel", "1w2M197oXvugnowk0_8bqVZDeTDlcOOvx", "DSC00350.JPG", mq("Vyasa"), (6000, 4000),
                  "Three actors kneel close together in pink light",
                  "Three together", (0.5, 0.55)),
            photo("vyasa-staff", "1syL-_ws1PpY5iN6XbnQENpwrzuikHfBV", "DSC00381.JPG", mq("Vyasa"), (6000, 4000),
                  "A figure in dark face paint raises both arms, holding a gilded staff",
                  "Both arms raised", (0.55, 0.4)),
            photo("vyasa-company", "1QtliRjQrRnWIECy89SxbecwsaaUW0l4S", "IMG_9423.JPG", mq("Vyasa"), (2400, 1344),
                  "The company crowded together in front of the heart set",
                  "The company", (0.5, 0.55)),
        ],
        "more": [
            {"id": "khzY2dwtnrE", "title": "Ivysherin — Trailer", "note": "Vyasa Productions · uploaded January 2026", "length": "2:10"},
            {"id": "P4GGqjywNhQ", "title": "Inscenare — Trailer", "note": "Masquerade 2022 · with Valmiki House", "length": "1:38"},
            {"id": "rfNsT_1eSAk", "title": "Masquerade Trailer", "note": "2018", "length": "2:13"},
            {"id": "4V3SA84lv8U", "title": "Imperium — Trailer", "note": "2017", "length": "2:15"},
            {"id": "YyrYMlsxt9g", "title": "Masquerade Trailer", "note": "2016", "length": "1:48"},
            {"id": "4zVnVIRazB0", "title": "Vyasa House Masquerade 2015", "note": "2015 · recording", "length": "34:29"},
            {"id": "7aYY7nQH4mE", "title": "Inside Out — Trailer", "note": "2015", "length": "2:05"},
            {"id": "1YbFJ4XF2tI", "title": "Masquerade Trailer", "note": "2013", "length": "3:05"},
        ],
    },
]

# ---------------------------------------------------------- class presentations
#
# Every video the school's channel titles as a class presentation. The class
# is written as the title writes it; nothing is inferred from who is on
# screen. "uploaded" is YouTube's upload date, which is not necessarily the
# day of the assembly, and the page says so.

CLASS_RECENT = [
    # title: the YouTube title up to its hashtags, exactly as the school wrote it
    {"id": "h0w1Y3murJU", "title": "Dare to Dream | Grade 8", "class": "Grade 8", "uploaded": "April 2026", "length": "5:47"},
    {"id": "M1X5UxpTSdQ", "title": "The Importance of Empathy | 12th Management", "class": "12th Management", "uploaded": "March 2026", "length": "9:19"},
    {"id": "yhlidIk6ufM", "title": "The Battle Within | 9th Grade", "class": "9th Grade", "uploaded": "March 2026", "length": "7:01"},
    {"id": "LUi91hmstMY", "title": "Protect Nature! | 5th Grade", "class": "5th Grade", "uploaded": "March 2026", "length": "5:11"},
    {"id": "PIaI4F8kIC8", "title": "For One More Day | IB 1st Year", "class": "IB 1st Year", "uploaded": "March 2026", "length": "7:34"},
    {"id": "-3n1Ms17jao", "title": "Knowing the Nation | Grade 7", "class": "Grade 7", "uploaded": "March 2025", "length": "5:44"},
]

CLASS_EARLIER = [
    # title: the YouTube title exactly; year: only where the title states one
    {"id": "qh1LZqnmHOE", "title": "CIRS - Class presentation by 7C on Kerala floods.", "class": "7C", "uploaded": "2019", "length": "5:36"},
    {"id": "SxUIJthDw1A", "title": "CIRS - Class presentation by10 C on Kerala floods.", "class": "10 C", "uploaded": "2019", "length": "7:16"},
    {"id": "7GL6BD-PoLo", "title": "CIRS - Class presentation by 10B. Live in the moment.", "class": "10B", "uploaded": "2019", "length": "7:43"},
    {"id": "VzVlBfmg8ek", "title": "Class presentation by Class 11 science. SAY NO TO SUICIDE.", "class": "Class 11 Science", "uploaded": "2019", "length": "5:19"},
    {"id": "PSBkm2KabT8", "title": "Class presentation by 11 Management.", "class": "11 Management", "uploaded": "2019", "length": "4:57"},
    {"id": "hZC0gSYXjH0", "title": "CIRS - Class 10 B Presentation", "class": "10 B", "uploaded": "2018", "length": "7:23"},
    {"id": "jARHAh1WyZE", "title": "CIRS - Class 10 C Presentation", "class": "10 C", "uploaded": "2018", "length": "6:13"},
    {"id": "XhlQL5u9f2s", "title": "CIRS - Class Presentation by 10 D", "class": "10 D", "uploaded": "2018", "length": "5:35"},
    {"id": "ILPM6xFXtXA", "title": "CIRS - Class 11 Management Presentation", "class": "11 Management", "uploaded": "2018", "length": "4:59"},
    {"id": "T0VdRpLM4Jk", "title": "CIRS - CLASS PRESENTATION BY 7 A", "class": "7 A", "uploaded": "2018", "length": "6:38"},
    {"id": "0f14pDWoVVc", "title": "CIRS - CLASS PRESENTATION BY 5 B", "class": "5 B", "uploaded": "2017", "length": "8:16"},
    {"id": "jO9t7gN8v4A", "title": "CIRS - CLASS PRESENTATION BY 11 th SCIENCE", "class": "11th Science", "uploaded": "2017", "length": "5:24"},
    {"id": "CnWj3OTRP3A", "title": "CIRS - CLASS 10 B PRESENTATION", "class": "10 B", "uploaded": "2016", "length": "5:16"},
    {"id": "tLkWgIBgtkQ", "title": "CIRS - CLASS 6 B presentation", "class": "6 B", "uploaded": "2016", "length": "8:57"},
    {"id": "N0o6O4xjKIM", "title": "CIRS - Class 7c Presentation about Mobile Use", "class": "7C", "uploaded": "2015", "length": "1:55"},
    {"id": "IzJvNBZZzw8", "title": "CIRS - CLASS 6B PRESENTATION ABOUT \"AGRICULTURE\"", "class": "6B", "uploaded": "2015", "length": "10:34"},
    {"id": "wgpxdg4__2A", "title": "CIRS - IB Ist Year Class Presentation -\"About IB \"", "class": "IB 1st Year", "uploaded": "2015", "length": "6:10"},
    {"id": "9ltZfFC2lvU", "title": "CIRS - \"I transform, india transforms\" 12th Management Class Presentation 2015", "class": "12th Management", "year": "2015", "uploaded": "2015", "length": "7:12"},
    {"id": "_1YLD_SKHBM", "title": "CIRS 11 mgmt class presentation 2015", "class": "11 Management", "year": "2015", "uploaded": "2015", "length": "7:15"},
]


# ------------------------------------------------------------------- helpers

import html as _html
import json as _json


def esc(text):
    return _html.escape(text, quote=True)


def all_photos():
    """Every photograph the page uses, each once, with where it is shown."""
    out = [("Anand Utsav", ANAND_UTSAV["dark"]), ("Anand Utsav", ANAND_UTSAV["wide"])]
    out += [("Anand Utsav", p) for p in ANAND_UTSAV["sequence"]]
    out.append(("Masquerades", MASQUERADE_OPENER))
    for h in HOUSES:
        out.append((h["name"], h["lead"]))
        out += [(h["name"], p) for p in h["gallery"]]
    return out


def youtube_thumbs():
    """Every video whose thumbnail the page shows."""
    return [v["id"] for v in CLASS_RECENT + CLASS_EARLIER]


def widths(p):
    """The widths a photograph is cut at (tools/make-theatre.py) and offered at."""
    portrait = p["src"][1] > p["src"][0]
    base = [640, 1280] if portrait else [800, 1600]
    if p["size"] == "xl" and not portrait:
        base.append(2400)
    return [w for w in base if w <= p["src"][0]] or [p["src"][0]]


def file(p, w):
    return f"{DIR}/{p['name']}-{w}.webp"


def dims(p):
    """The intrinsic size of the largest file, for width and height."""
    w = widths(p)[-1]
    return w, round(w * p["src"][1] / p["src"][0])


def img(p, sizes, eager=False, cls=""):
    ws = widths(p)
    w, h = dims(p)
    srcset = ", ".join(f"{file(p, x)} {x}w" for x in ws)
    fx, fy = p["focus"]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    klass = f' class="{cls}"' if cls else ""
    return (f'<img{klass} src="{file(p, ws[0])}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{esc(p["alt"])}" {load} decoding="async" '
            f'style="--fx:{fx * 100:g}%;--fy:{fy * 100:g}%;--ar:{w}/{h}">')


def house_photos(h):
    """A house's photographs in the order the viewer steps through them:
    the lead, the programme card, then the gallery as laid out."""
    by = {p["name"]: p for p in h["gallery"]}
    order = [h["lead"], by[h["card"]]]
    for _, names in h["layout"]:
        order += [by[n] for n in names]
    return order


def house_count(h):
    return 1 + len(h["gallery"])


def total_masquerade():
    return sum(house_count(h) for h in HOUSES)


def watch(vid):
    return f"https://www.youtube.com/watch?v={vid}"


def _check():
    """No photograph twice, no name twice, every gallery photograph laid out
    exactly once. Run whenever this module is imported."""
    names, ids = set(), set()
    for _, p in all_photos():
        assert p["name"] not in names, f"theatre.py: {p['name']} is listed twice"
        assert p["drive"] not in ids, f"theatre.py: Drive file {p['file']} is used twice"
        names.add(p["name"])
        ids.add(p["drive"])
    for h in HOUSES:
        placed = [h["card"]] + [n for _, ns in h["layout"] for n in ns]
        gallery = [p["name"] for p in h["gallery"]]
        assert sorted(placed) == sorted(gallery), f"theatre.py: {h['name']} layout does not match its gallery"


_check()


# -------------------------------------------------------------------- markup

EXTERNAL = ' target="_blank" rel="noopener"'
NEW_TAB = '<span class="sr-only"> (opens YouTube in a new tab)</span>'
ARROW = '<span class="th-ext" aria-hidden="true">&#8599;</span>'


def photo_link(p, group, index, sizes, cls="", caption=True):
    """A photograph that opens in the viewer. Without scripting the link
    opens the largest file on its own, so nothing is lost."""
    cap = f'\n  <figcaption class="th-cap">{esc(p["caption"])}</figcaption>' if caption else ""
    klass = f"th-fig {cls}".strip()
    return (f'<figure class="{klass}">\n'
            f'  <a class="th-photo" href="{file(p, widths(p)[-1])}" data-th-open="{group}:{index}">'
            f'{img(p, sizes)}</a>{cap}\n'
            f'</figure>')


def _list_row(v):
    return (f'<li><a href="{watch(v["id"])}"{EXTERNAL}><span class="th-list__title">{esc(v["title"])}</span>'
            f'<span class="th-list__note">{esc(v["note"])}</span><span class="th-list__len">{v["length"]}</span>'
            f'{ARROW}{NEW_TAB}</a></li>')


def programme_html():
    acts = [
        ("I", "anand-utsav", "Anand Utsav", "The whole school"),
        ("II", "masquerades", "Masquerades", "The four houses"),
        ("III", "class-presentations", "Class Presentations", "Every class"),
    ]
    items = "\n".join(
        f'      <li><a class="th-programme__act" href="#{sid}">'
        f'<span class="th-programme__n">{n}</span>'
        f'<span class="th-programme__name serif">{name}</span>'
        f'<span class="th-programme__who">{who}</span></a></li>' for n, sid, name, who in acts)
    return f'''<nav class="th-programme rv" aria-labelledby="th-programme-title">
    <p class="th-programme__label" id="th-programme-title">The year, in three acts</p>
    <p class="th-programme__lead">The whole school, the four houses and every class of twenty-five: each has its own turn in front of an audience.</p>
    <ol class="th-programme__list">
{items}
    </ol>
  </nav>'''


def anand_utsav_html():
    au = ANAND_UTSAV
    court, soldiers, dance, sage, finale = au["sequence"]
    rec = au["recording"]
    more = "\n".join("        " + _list_row(v) for v in au["more"])
    return f'''<section class="th-au" id="anand-utsav" aria-labelledby="au-title" data-jump-label="Act I &middot; Anand Utsav">
  <div class="th-au__track" data-au-track>
    <div class="th-au__stage">
      {img(au["dark"], "100vw", cls="th-au__dark")}
      <div class="th-au__wide">{img(au["wide"], "100vw", cls="th-au__wideimg")}</div>
      <div class="th-au__scrim" aria-hidden="true"></div>
      <header class="th-au__head">
        <p class="th-label"><span class="th-label__act">Act I</span> The whole school &middot; Annual cultural programme</p>
        <h2 class="th-au__title" id="au-title">Anand Utsav</h2>
        <p class="th-au__sub">{au["year"]} &middot; <em>{esc(au["title"])}</em></p>
      </header>
      <p class="th-au__credit">{esc(au["wide"]["caption"])}</p>
    </div>
  </div>

  <div class="wrap th-au__intro">
    <p class="th-au__lede">Anand Utsav is the school&rsquo;s annual celebration, when parents come to campus &mdash; and its evening programme is the theatrical highlight of the year, for guests and students alike. The entire student body joins forces to put up a show to be remembered, with the concepts, the scripts and the acting done almost completely by the students, on the stage and off it.</p>
    <dl class="th-facts">
      <div><dt>Evening</dt><dd>{au["date"]}, the second day</dd></div>
      <div><dt>Stage</dt><dd>The main pandal, Arjuna Athletic Ground</dd></div>
      <div><dt>On stage</dt><dd>The whole school</dd></div>
    </dl>
    <p class="th-watch"><a class="th-watch__link" href="{watch(rec["id"])}"{EXTERNAL}><span class="th-watch__play" aria-hidden="true"></span>Watch the production <span class="th-watch__len">{rec["length"]}</span>{NEW_TAB}</a></p>
  </div>

  <div class="th-au__seq">
    <div class="wrap th-au__row th-au__row--court">
      {photo_link(court, "anand-utsav", 0, "(min-width: 900px) 62vw, 100vw")}
    </div>
    {photo_link(soldiers, "anand-utsav", 1, "100vw", cls="th-bleed")}
    <div class="wrap th-au__row th-au__row--pair">
      {photo_link(dance, "anand-utsav", 2, "(min-width: 900px) 58vw, 100vw", cls="th-au__dance")}
      {photo_link(sage, "anand-utsav", 3, "(min-width: 900px) 30vw, 100vw", cls="th-au__sage")}
    </div>
    <figure class="th-fig th-bleed th-au__finale">
      <a class="th-photo" href="{file(finale, widths(finale)[-1])}" data-th-open="anand-utsav:4">{img(finale, "100vw")}</a>
      <figcaption class="th-au__finalecap">
        <span class="th-au__finaleline serif">One stage. <em>The whole school.</em></span>
        <span class="th-cap">{esc(finale["caption"])}</span>
      </figcaption>
    </figure>
  </div>

  <div class="wrap th-au__more">
    <p class="th-list__head">Other years of Anand Utsav on the school&rsquo;s channel</p>
    <ul class="th-list">
{more}
    </ul>
  </div>
</section>'''


ROW_SIZES = {
    "feature": ["(min-width: 900px) 64vw, 100vw", "(min-width: 900px) 32vw, 100vw", "(min-width: 900px) 32vw, 100vw"],
    "full": ["(min-width: 1320px) 1320px, 100vw"],
    "trio": ["(min-width: 900px) 32vw, 100vw"] * 3,
    "duo": ["(min-width: 900px) 58vw, 100vw", "(min-width: 900px) 40vw, 100vw"],
}


def _row(kind, photos, group, start):
    figs = []
    for i, p in enumerate(photos):
        portrait = p["src"][1] > p["src"][0]
        cls = f"th-g th-g--{kind}-{i}" + (" is-portrait" if portrait else "")
        sizes = "(min-width: 900px) 30vw, 100vw" if portrait else ROW_SIZES[kind][i]
        figs.append(photo_link(p, group, start + i, sizes, cls=cls))
    extra = " has-portrait" if any(p["src"][1] > p["src"][0] for p in photos) else ""
    return f'        <div class="th-grid__row th-grid__row--{kind}{extra}">\n' + "\n".join(figs) + "\n        </div>"


def _more_list(h):
    rows = "\n".join("          " + _list_row(v) for v in h["more"])
    return f'''        <details class="th-more">
          <summary class="th-more__toggle">Earlier {h["name"]} seasons on YouTube <span class="th-more__n">{len(h["more"])}</span></summary>
          <ul class="th-list th-list--dark">
{rows}
          </ul>
        </details>'''


def house_html(h, i):
    photos = house_photos(h)
    lead = photos[0]
    rec, trailer = h["recording"], h["trailer"]
    nxt = HOUSES[i + 1] if i + 1 < len(HOUSES) else None
    rows, index = [], 2   # 0 is the lead, 1 is the programme card
    by = {p["name"]: p for p in h["gallery"]}
    for kind, names in h["layout"]:
        ps = [by[n] for n in names]
        rows.append(_row(kind, ps, h["id"], index))
        index += len(ps)
    if nxt:
        onward = (f'<a class="th-house__next" href="#{nxt["id"]}" data-house-link="{nxt["id"]}">'
                  f'<span class="th-house__nextlabel">Next</span> '
                  f'<span class="th-house__nextname">{nxt["numeral"]}. {nxt["name"]} &middot; <em>{esc(nxt["title"])}</em></span></a>')
    else:
        onward = ('<a class="th-house__next" href="#class-presentations"><span class="th-house__nextlabel">Next</span> '
                  '<span class="th-house__nextname">Act III &middot; Class Presentations</span></a>')
    return f'''    <article class="th-house" id="{h["id"]}" aria-labelledby="{h["id"]}-title" data-house="{h["id"]}">
      <figure class="th-house__lead">
        <a class="th-photo" href="{file(lead, widths(lead)[-1])}" data-th-open="{h["id"]}:0">{img(lead, "100vw", cls="th-house__leadimg")}</a>
        <figcaption class="th-house__label">
          <span class="th-house__numeral" aria-hidden="true">{h["numeral"]}</span>
          <div class="th-house__labeltext">
            <span class="th-house__kicker">{h["name"]} House &middot; Masquerade {h["year"]}</span>
            <h3 class="th-house__play serif" id="{h["id"]}-title" tabindex="-1"><span class="sr-only">{h["name"]} House: </span><em>{esc(h["title"])}</em></h3>
            <span class="th-house__count">{house_count(h)} photographs &middot; {esc(lead["caption"])}</span>
          </div>
        </figcaption>
      </figure>
      <div class="wrap th-house__bar">
        <p class="th-watch th-watch--dark"><a class="th-watch__link" href="{watch(rec["id"])}"{EXTERNAL}><span class="th-watch__play" aria-hidden="true"></span>Watch the production <span class="th-watch__len">{rec["length"]}</span>{NEW_TAB}</a>
          <a class="th-watch__alt" href="{watch(trailer["id"])}"{EXTERNAL}>Trailer <span class="th-watch__len">{trailer["length"]}</span>{NEW_TAB}</a>
          <button type="button" class="th-watch__alt th-house__view" data-th-view="{h["id"]}" hidden>Open the photographs</button></p>
      </div>
      <div class="wrap th-grid">
{chr(10).join(rows)}
      </div>
      <div class="wrap th-house__foot">
{_more_list(h)}
        {onward}
      </div>
    </article>'''


def masquerades_html():
    op = MASQUERADE_OPENER
    cards = []
    for h in HOUSES:
        card = {p["name"]: p for p in h["gallery"]}[h["card"]]
        cards.append(f'''      <li class="th-bill__item">
        <a class="th-bill__link" href="#{h["id"]}" data-house-link="{h["id"]}">
          <span class="th-bill__img">{img(card, "(min-width: 900px) 24vw, (min-width: 560px) 48vw, 100vw")}</span>
          <span class="th-bill__text">
            <span class="th-bill__n">{h["numeral"]}</span>
            <span class="th-bill__house serif">{h["name"]}</span>
            <span class="th-bill__play"><em>{esc(h["title"])}</em></span>
            <span class="th-bill__meta">{h["year"]} &middot; {house_count(h)} photographs</span>
          </span>
        </a>
      </li>''')
    rail = "\n".join(f'        <a href="#{h["id"]}" data-house-link="{h["id"]}"><span class="th-rail__n" aria-hidden="true">{h["numeral"]}</span>{h["name"]}</a>'
                     for h in HOUSES)
    houses = "\n".join(house_html(h, i) for i, h in enumerate(HOUSES))
    return f'''<section class="th-mq" id="masquerades" aria-labelledby="mq-title" data-jump-label="Act II &middot; Masquerades">
  <header class="wrap th-mq__open">
    <figure class="th-mq__face">{img(op, "(min-width: 900px) 34vw, 70vw")}
      <figcaption class="th-cap">{esc(op["caption"])}</figcaption>
    </figure>
    <div class="th-mq__intro">
      <p class="th-label"><span class="th-label__act">Act II</span> The four houses</p>
      <h2 class="th-mq__title" id="mq-title">Masquerades</h2>
      <p class="th-mq__lede">Four evenings. Four houses. Hundreds of students stoking the fire of theatre. Every house comes together to put up an hour-long play &mdash; fantasy or mystery, satire or thriller &mdash; and every eye in CIRS is hooked to the stage for every single second.</p>
      <dl class="th-facts th-facts--dark">
        <div><dt>Houses</dt><dd>Four</dd></div>
        <div><dt>Evenings</dt><dd>One for each house</dd></div>
        <div><dt>Each play</dt><dd>About an hour</dd></div>
      </dl>
    </div>
  </header>

  <div class="wrap th-bill">
    <div class="th-bill__head">
      <p class="th-bill__season">The programme &middot; Masquerade 2024, November</p>
      <p class="th-bill__note">Four productions and {total_masquerade()} photographs from the school&rsquo;s archive. Choose a house, or step through every photograph in order.</p>
      <button type="button" class="th-bill__all" data-th-view="all" hidden>View all {total_masquerade()} photographs</button>
    </div>
    <ol class="th-bill__list">
{chr(10).join(cards)}
    </ol>
  </div>

  <div class="th-houses">
    <nav class="th-rail" aria-label="Masquerade 2024 houses">
      <div class="th-rail__inner">
{rail}
      </div>
    </nav>
{houses}
  </div>
</section>'''


def _video_card(v):
    name = v["title"].split(" | ")[0]
    return f'''      <li class="th-video">
        <a class="th-video__link" href="{watch(v["id"])}"{EXTERNAL}>
          <span class="th-video__thumb"><img src="{DIR}/yt/{v["id"]}.webp" alt="" width="640" height="360" loading="lazy" decoding="async"><span class="th-video__len">{v["length"]}</span></span>
          <span class="th-video__class">{esc(v["class"])}</span>
          <span class="th-video__title serif">{esc(name)}</span>
          <span class="th-video__meta">Uploaded {v["uploaded"]}</span>
          <span class="th-video__cta">Watch on YouTube {ARROW}</span>{NEW_TAB}
        </a>
      </li>'''


def _video_row(v):
    year = f' &middot; {v["year"]}' if v.get("year") else ""
    return f'''        <li class="th-vrow">
          <a class="th-vrow__link" href="{watch(v["id"])}"{EXTERNAL}>
            <img src="{DIR}/yt/{v["id"]}.webp" alt="" width="320" height="180" loading="lazy" decoding="async">
            <span class="th-vrow__title">{esc(v["title"])}</span>
            <span class="th-vrow__meta">{esc(v["class"])}{year} &middot; uploaded {v["uploaded"]} &middot; {v["length"]}</span>
            <span class="th-vrow__cta">Watch on YouTube {ARROW}</span>{NEW_TAB}
          </a>
        </li>'''


def classes_html():
    recent = "\n".join(_video_card(v) for v in CLASS_RECENT)
    earlier = "\n".join(_video_row(v) for v in CLASS_EARLIER)
    return f'''<section class="section th-cp" id="class-presentations" aria-labelledby="cp-title" data-jump-label="Act III &middot; Class Presentations">
  <div class="wrap">
    <div class="th-cp__head">
      <p class="th-label th-label--ink"><span class="th-label__act">Act III</span> Every class</p>
      <h2 class="serif h2" id="cp-title">Class <em>Presentations.</em></h2>
      <p class="lead">Every class of twenty-five puts up a theatrical presentation in the school assembly once a year. Engaging every student through acting, dance, tech and lighting, theatre here is not limited to drama clubs but brings every pupil into its embrace. This is where prodigies are born.</p>
      <p class="th-cp__note">Recorded and published by the school on its YouTube channel. Each class is named as its video names it, and each date is the date the video was uploaded.</p>
    </div>
    <ul class="th-videos">
{recent}
    </ul>
    <details class="th-archive">
      <summary class="th-archive__toggle">Earlier class presentations, 2015&ndash;2019 <span class="th-archive__n">{len(CLASS_EARLIER)}</span></summary>
      <ul class="th-vrows">
{earlier}
      </ul>
    </details>
    <p class="th-cp__links">
      <a class="btn btn--outline" href="{CLASS_PLAYLIST}"{EXTERNAL}>The class presentation playlist{NEW_TAB}</a>
      <a class="th-cp__channel" href="{CHANNEL}"{EXTERNAL}>All videos on the CIRS channel {ARROW}{NEW_TAB}</a>
    </p>
  </div>
</section>'''


def viewer_data():
    """The viewer's sequences, as JSON for assets/js/theatre.js."""
    def item(p):
        ws = widths(p)
        w, h = dims(p)
        return {"src": file(p, ws[-1]), "tile": file(p, ws[0]), "w": w, "h": h,
                "alt": p["alt"], "caption": p["caption"]}
    groups = {"anand-utsav": {"label": f"Anand Utsav {ANAND_UTSAV['year']}",
                              "sub": ANAND_UTSAV["title"],
                              "items": [item(p) for p in ANAND_UTSAV["sequence"]]}}
    for h in HOUSES:
        groups[h["id"]] = {"label": f"{h['name']} House", "sub": f"{h['title']}, Masquerade {h['year']}",
                           "items": [item(p) for p in house_photos(h)]}
    data = _json.dumps({"groups": groups, "all": [h["id"] for h in HOUSES]},
                       ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="th-viewer-data">{data}</script>'
