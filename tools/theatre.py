"""CIRS Theatre — the media manifest and the markup built from it.

Every photograph on the Theatre page after its opening is listed here, with
where it came from: the school's Google Drive file (by id and by its camera
filename), the folder it sits in, the event, the house, the year and the
production. tools/make-theatre.py cuts the files from this list, and
tools/build-site.py writes the page's three acts from it, so there is one
record of what each picture is and nothing on the page can drift from it.

The season shown is 2025: Anand Utsav 2025 and Masquerade 2025.

What is known and what is not
-----------------------------
  * Anand Utsav 2025. The school's 2025-26 social media timeline gives the
    event's first day as 6 October 2025. Every photograph here is from the
    Drive folder "46. Anand Utsav", taken on the evening of 7 October 2025
    (the camera's own timestamps, 18:23 to 20:50) — the second day, and the
    evening of its cultural programme. The next morning's photographs, and the
    speeches and awards earlier that evening, are left out. The production's
    title is the one the school gave its recording on YouTube.
  * Masquerade 2025. The Drive folder "54. Masquerade" holds one folder per
    house from one photographer (Smaran/Valmiki, /Vasistha, /Vishwamitra) and
    three photographers' folders not sorted by house (Abarna, Adhivika,
    Radha). Each house played on its own evening, and the photographs are
    assigned to a house by the evening they were taken:

        23 November  Valmiki      Smaran/Valmiki is dated 23 Nov
        24 November  Vasistha     Smaran/Vasistha is dated 24 Nov; the
                                  Vantara trailer says "November 24"
        25 November  Vishwamitra  Smaran/Vishwamitra is dated 25 Nov
        26 November  Vyasa        the Ivysherin trailer says "November 26"

    Every set was also checked against the house's own trailer and folder:
    the same sets and costumes appear in both. Never by costume colour.
  * Abarna's camera clock reads a year behind (2024 for November 2025). Its
    photographs sit in the 2025 folder and show the same stage, sets and cast,
    evening by evening, as the correctly dated cameras beside them; the year
    below is the evening's, not the camera's.
  * The production titles are the school's own, from the trailers on its
    channel: Melora (titled "Valmiki 2025 | Masquerade 2025"), Vantara,
    El Diablo and Ivysherin. Melora and Vantara are also written on stage, in
    photographs below. No full recording of a 2025 Masquerade is on the
    channel, so each house links to its trailer, not to a production.
  * Captions describe what is in the frame. No character is named and no
    scene is explained: the school has not published cast lists or synopses.

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
# fit: "contain" for a photograph shown whole rather than cropped to fill


def photo(name, drive, file, folder, src, alt, caption, focus=(0.5, 0.5), size="l", fit="cover"):
    return {"name": name, "drive": drive, "file": file, "folder": folder, "src": src,
            "alt": alt, "caption": caption, "focus": focus, "size": size, "fit": fit}


AU_FOLDER = "46. Anand Utsav"
L = (6000, 4000)       # the Sony cameras
C = (6000, 3368)       # the Canon R100
R5 = (8192, 5464)      # the Canon R5 at Anand Utsav

ANAND_UTSAV = {
    "event": "Anand Utsav 2025",
    "year": 2025,
    "date": "7 October 2025",
    "title": "Maryada Purushottham",
    # The school's own recording of this evening's theatre programme.
    "recording": {"id": "-QrRDoSJ9Ww", "title": "Maryada Purushottham | Anand Utsav 2025 | Theater Show",
                  "length": "67:36"},
    # The frame the act opens on, in near darkness, before the lights come up.
    # Shown whole: the dark around the figure is the photograph's own.
    "dark": photo("au25-alone", "1hiQjsvBRUJL3j6B807V9db9ASlMvangb", "0C9A3355.JPG", AU_FOLDER, (5464, 8192),
                  "A student in a yellow dhoti alone in a pool of light on a dark stage, both arms raised",
                  "One figure, one light", (0.5, 0.4), "xl", "contain"),
    # The image that carries the act: the whole stage, the whole cast.
    "wide": photo("au25-palace", "1hXLl5G9a4JXSrHTKM_GBk0C53aOaOTGo", "0C9A3507.JPG", AU_FOLDER, R5,
                  "A palace hall filling the stage: a king on a carved throne, courtiers in bright costume and guards in black around him",
                  "The palace, across the whole stage", (0.5, 0.62), "xl"),
    # The sequence after it, in the order the page shows them.
    "sequence": [
        photo("au25-court", "1EEsW3XQTAiRV27qfAX1HqIs2RtxG-seN", "0C9A3377.JPG", AU_FOLDER, R5,
              "Two crowned figures on gilded thrones before a painted palace wall, a young actor before them",
              "A court, on gilded thrones", (0.55, 0.55)),
        photo("au25-sunset", "1vOIDfCdt88wlPc30CaIkwRDtq-UdetyQ", "0C9A3556.JPG", AU_FOLDER, R5,
              "An ensemble in bright dhotis dancing before a sunset backdrop",
              "An ensemble at sunset", (0.4, 0.6), "xl"),
        photo("au25-mountain", "1PA5HB15r7P2cKN5HdkdjuwyMRZcyPvcb", "0C9A3461.JPG", AU_FOLDER, R5,
              "Two students in green dhotis grappling before a painted blue mountain",
              "A struggle before the mountain", (0.62, 0.65)),
        photo("au25-tableau", "1XlJjkbgWYBorYFkqVXI2yk5EvwNHPhnq", "0C9A3199.JPG", AU_FOLDER, R5,
              "A dancer in red and gold at the centre of a many-armed tableau",
              "A many-armed tableau", (0.5, 0.5)),
        photo("au25-curtain-call", "1JSouOer072ufxlw6yiX3Ov2QHygzAdlL", "0C9A3703.JPG", AU_FOLDER, R5,
              "The cast crowded together on the stage at the close, petals on the floor",
              "Everyone on the stage at the close", (0.5, 0.5), "xl"),
    ],
    # Other years of the same programme on the school's channel.
    "more": [
        {"id": "93Pnob1zi90", "title": "Anand Utsav 2025", "note": "CIRS Annual Day · highlights", "length": "3:58"},
        {"id": "hWddJ6T9H2c", "title": "Transforming Lives! Transforming Vision!", "note": "Anand Utsav 2024 · Theater show", "length": "68:21"},
        {"id": "XZg-NTpB1zo", "title": "Dharmo Rakshati Rakshitah", "note": "Anand Utsav 2023 · Cultural programme", "length": "66:22"},
        {"id": "g_uTAO3wsO0", "title": "CIRS Anand Utsav – 2019", "note": "Recorded live", "length": "79:17"},
    ],
}


def mq(folder):
    return f"54. Masquerade / {folder}"


# The act's opening frame. From Vishwamitra's evening; it is not repeated in
# that house's gallery.
MASQUERADE_OPENER = photo(
    "mq25-skull-paint", "1tuapc3jdq6YHsqHX6UVvlywPCvi59qco", "DSC05729.JPG", mq("Abarna"), L,
    "An actor in white skull face paint under orange light, hands open",
    "Vishwamitra House, El Diablo, 2025", (0.5, 0.3))

# The four houses, in the order they played. The spelling of the house names
# is the site's; the school's own titles also write Vasishta and Vasishtha.
HOUSES = [
    {
        "id": "valmiki", "name": "Valmiki", "numeral": "I",
        "title": "Melora", "year": 2025, "date": "23 November",
        "drive_folder": "54. Masquerade / Smaran/Valmiki, Adhivika, Abarna (23 November)",
        "recording": None,
        "trailers": [{"id": "EfzbNboA4TE", "length": "1:17", "label": "Trailer",
                      "title": "Melora | Valmiki 2025 | Masquerade 2025"}],
        "card": "valmiki25-red-coat",
        "layout": [
            ("feature", ["valmiki25-candy", "valmiki25-sofa", "valmiki25-bed"]),
            ("full", ["valmiki25-storm"]),
            ("trio", ["valmiki25-neon", "valmiki25-painted", "valmiki25-silhouette"]),
            ("duo", ["valmiki25-factory", "valmiki25-tunnel"]),
            ("full", ["valmiki25-amazing-violet"]),
            ("trio", ["valmiki25-chocolate", "valmiki25-after", "valmiki25-poster"]),
        ],
        "lead": photo("valmiki25-dance", "1eaSNX8Wa3GvlO7968jqH5fT-tniNWPuz", "DSC01333.JPG", mq("Adhivika"), L,
                      "The company dancing across the stage before a candy-land backdrop, a lead in a red coat and top hat among them",
                      "The company, dancing across the candy land", (0.5, 0.5), "xl"),
        "gallery": [
            photo("valmiki25-red-coat", "1ovr9E4cRkDnGX-A8t3aFLlgesEStTaxR", "DSC04895.JPG", mq("Abarna"), L,
                  "An actor in a red coat and top hat before shelves of jars",
                  "Red coat and top hat", (0.45, 0.4)),
            photo("valmiki25-candy", "1VAqElRZ30HqtRgzSIiFSqv4EC-QPa_DV", "DSC04866.JPG", mq("Abarna"), L,
                  "An actor in a red coat and top hat, arm out, before a pink candy-land backdrop",
                  "In the candy land", (0.5, 0.45)),
            photo("valmiki25-neon", "1BrUCc_mt28WYh-eaeA4ZleX8LD1x03Za", "DSC04923.JPG", mq("Abarna"), L,
                  "An actor in a grey suit speaking into a microphone beside a neon sign",
                  "Beside the neon sign", (0.4, 0.4)),
            photo("valmiki25-painted", "1ft0W0SYS_qce9tPePnP9Zf9nKLa9EZSx", "DSC05034.JPG", mq("Abarna"), L,
                  "An actor in red swirling body paint, arms spread, against a dark backdrop",
                  "Red body paint", (0.5, 0.4)),
            photo("valmiki25-storm", "13847kisw6B3I4FjrWciiMWKQUn3MOf5C", "DSC01290.JPG", mq("Adhivika"), L,
                  "An actor in body paint standing before a projected lightning storm and a broken hut",
                  "Before the storm", (0.5, 0.5)),
            photo("valmiki25-silhouette", "1WHyTLvfkOMI2-L-i54_sgRiLU3H9z-8T", "DSC01292.JPG", mq("Adhivika"), L,
                  "A figure crawling in silhouette before a projected desert and a ruined hut",
                  "In silhouette", (0.6, 0.6)),
            photo("valmiki25-sofa", "1UGCC4U37WV5H2z2LFmAFmD66c7yrMPZP", "DSC05069.JPG", mq("Abarna"), L,
                  "Two actors on a sofa before a white-and-peach backdrop, one in a red coat holding a cane",
                  "On the sofa", (0.5, 0.5)),
            photo("valmiki25-bed", "1bH9x9x0prDg6yEMCpCst2piqlU45SstJ", "DSC01270.JPG", mq("Adhivika"), L,
                  "Two actors on a bed in a room set with yellow shelves and soft toys",
                  "A room with yellow shelves", (0.5, 0.55)),
            photo("valmiki25-factory", "1HQwTGDIytXJa-wmCxcknm9fQepHe_OOk", "DSC01343.JPG", mq("Adhivika"), L,
                  "Actors in a factory set, one in a red coat seated with a cane",
                  "In the factory", (0.45, 0.5)),
            photo("valmiki25-tunnel", "1rww1p4CT6j5P2lSlcwChi1PH3wDgmEYg", "DSC01406.JPG", mq("Adhivika"), L,
                  "Actors before a swirling pink tunnel projected behind them",
                  "The pink tunnel", (0.6, 0.55)),
            photo("valmiki25-amazing-violet", "1A7VbBIMFqdljJJr7gVgp9_2cFGBVnt5D", "IMG_7479.JPG", mq("Smaran/Valmiki"), C,
                  "Dancers before a neon sign reading The Amazing Violet",
                  "The Amazing Violet", (0.4, 0.5)),
            photo("valmiki25-chocolate", "1G5aG11O8VPoa4Ju2NBNM2QpR9qYCIe5s", "IMG_7485.JPG", mq("Smaran/Valmiki"), C,
                  "A lone actor in a striped shirt beside a projected landscape of chocolate and candy canes",
                  "The chocolate landscape", (0.6, 0.5)),
            photo("valmiki25-after", "1tlSodgx7w5SMWiya6Tj2zP8THJCnn1Gu", "IMG_7520.JPG", mq("Smaran/Valmiki"), C,
                  "Two actors after the show, one in swirling body paint, one in a red coat and top hat",
                  "After the show", (0.5, 0.4)),
            photo("valmiki25-poster", "1b4ESJmvQK3rk1P2kUCKeyDJV0fYyTvIP", "IMG_7547.JPG", mq("Smaran/Valmiki"), C,
                  "A figure in a red coat and top hat before a painted poster reading Melora",
                  "The Melora poster", (0.5, 0.5)),
        ],
        "more": [
            {"id": "fIMCetOlzCQ", "title": "Maledictus", "note": "Masquerade 2024 · the production", "length": "67:23"},
            {"id": "LDQe07FKQ3c", "title": "Maledictus — Trailer", "note": "Masquerade 2024", "length": "1:43"},
            {"id": "P4GGqjywNhQ", "title": "Inscenare — Trailer", "note": "Masquerade 2022 · with Vyasa House", "length": "1:38"},
            {"id": "YMccsEUTFmo", "title": "Masquerade Trailer", "note": "2018", "length": "2:01"},
            {"id": "Gfq8MvXjejk", "title": "Masquerade Trailer", "note": "2017", "length": "2:03"},
            {"id": "8bFocvpMhVs", "title": "Masquerade Trailer", "note": "2016", "length": "1:53"},
            {"id": "ZRIpcIDuCYg", "title": "The Aladdin — Trailer", "note": "2015", "length": "2:14"},
            {"id": "7boWOTghbtg", "title": "Masquerade Trailer", "note": "2013", "length": "2:02"},
        ],
    },
    {
        "id": "vasistha", "name": "Vasistha", "numeral": "II",
        "title": "Vantara", "year": 2025, "date": "24 November",
        "drive_folder": "54. Masquerade / Smaran/Vasistha, Abarna (24 November)",
        "recording": None,
        "trailers": [{"id": "xXx1UMMRg6k", "length": "1:58", "label": "Trailer",
                      "title": "Vantara | Vasishta Productions | Trailer 1"},
                     {"id": "ahsfpRphrww", "length": "1:05", "label": "Second trailer",
                      "title": "Vantara | Vasishta Productions | Trailer 2"}],
        "card": "vasistha25-tiger",
        "layout": [
            ("feature", ["vasistha25-cradle", "vasistha25-wolves", "vasistha25-roar"]),
            ("full", ["vasistha25-clearing"]),
            ("trio", ["vasistha25-bear", "vasistha25-sunbeams", "vasistha25-torch"]),
            ("duo", ["vasistha25-gathered", "vasistha25-silhouettes"]),
            ("full", ["vasistha25-tree"]),
            ("duo", ["vasistha25-banner", "vasistha25-company"]),
        ],
        "lead": photo("vasistha25-violet", "1TpF5ACdBq2jxfWvZ1t9f-zrrr4OhV8R0", "DSC05189.JPG", mq("Abarna"), L,
                      "A performer in purple with glowing patterns, arms held out under violet light",
                      "Under violet light", (0.5, 0.4), "xl"),
        "gallery": [
            photo("vasistha25-tiger", "1lUh8nIbO2ALZg9FpM89I-SYgFXwQAb2m", "DSC05330.JPG", mq("Abarna"), L,
                  "An actor in tiger body paint under blue light",
                  "The tiger", (0.45, 0.4)),
            photo("vasistha25-cradle", "16a3fYTcSJVigANZHFCLY_MhkXyGx0Xst", "DSC05101.JPG", mq("Abarna"), L,
                  "A figure in dark body paint cradling a bundle in red cloth before a blue forest",
                  "In the blue forest", (0.4, 0.5)),
            photo("vasistha25-wolves", "1ClAn-X1SLn7s19CoQKB-p7VAeWmylYT_", "DSC05136.JPG", mq("Abarna"), L,
                  "Three actors made up as wolves, crouching in green light",
                  "The wolves", (0.5, 0.4)),
            photo("vasistha25-roar", "1PFsd4aGCsifDbjUAIWsG9k5Z7B-lm07g", "DSC05152.JPG", mq("Abarna"), L,
                  "An actor in tiger body paint roaring, head thrown back",
                  "The roar", (0.55, 0.35)),
            photo("vasistha25-bear", "1Pjpm8K-Fr9EXp_aZfsel388txHYRu8yT", "DSC05258.JPG", mq("Abarna"), L,
                  "An actor in a bear costume, arms raised, among painted jungle children before a ruined temple set",
                  "The bear, and the jungle around him", (0.45, 0.4), "xl"),
            photo("vasistha25-sunbeams", "1BvcRJ8gxgu059eSfbRcS-UKeu--ugk5v", "DSC05239.JPG", mq("Abarna"), L,
                  "A boy and the actor in the bear costume talking in shafts of light through a forest",
                  "In the sunbeams", (0.5, 0.45)),
            photo("vasistha25-torch", "1_sllSau0k-GEEOUemXCB4Eq8f0BYPN3r", "DSC05293.JPG", mq("Abarna"), L,
                  "A performer in black holding up a flaming torch prop before the temple set",
                  "The torch", (0.5, 0.45)),
            photo("vasistha25-gathered", "16BREGbEch8hM16APbBDftClOmc2pKi0T", "DSC05374.JPG", mq("Abarna"), L,
                  "The cast gathered around a boy lying on the stage",
                  "Gathered around him", (0.5, 0.55)),
            photo("vasistha25-silhouettes", "1CL4xXBcyqnHeNrzOa1rZGclU9IdiKw2H", "DSC05394.JPG", mq("Abarna"), L,
                  "Three figures in silhouette holding hands before bare trees",
                  "In silhouette", (0.5, 0.5)),
            photo("vasistha25-banner", "1BSt1MXccnJARH7aZRrlrvirrsAmhTfIL", "IMG_7550.JPG", mq("Smaran/Vasistha"), C,
                  "A painted banner of jungle leaves reading Vantara along the front of the stage",
                  "The banner", (0.5, 0.5)),
            photo("vasistha25-clearing", "1R67ZnnGg5xodiGRdmBvK7j-1DglY-sQF", "IMG_7586.JPG", mq("Smaran/Vasistha"), C,
                  "The actor in the bear costume and a boy in a forest clearing lit by shafts of light",
                  "The clearing", (0.5, 0.55)),
            photo("vasistha25-tree", "1RzaMCEg9h_AlNxMTDg11_u036cGSxE2D", "IMG_7612.JPG", mq("Smaran/Vasistha"), C,
                  "Actors in costume and body paint beside a glowing green tree",
                  "The glowing tree", (0.5, 0.45), "xl"),
            photo("vasistha25-company", "1GnkQqeefjTuGMT6SMA4lFitzxu-rGYb5", "IMG_7645.JPG", mq("Smaran/Vasistha"), C,
                  "The company after the show, still in face paint and costume",
                  "The company", (0.5, 0.5)),
        ],
        "more": [
            {"id": "T0EEKg1t92g", "title": "Incursion", "note": "Masquerade 2024 · the production", "length": "63:50"},
            {"id": "mcS44liPzw8", "title": "Incursion — Trailer", "note": "Masquerade 2024", "length": "2:06"},
            {"id": "irgJPObYt6Q", "title": "The Anarchist — Trailer", "note": "Masquerade 2022 · with Vishwamitra House", "length": "1:38"},
            {"id": "hdKRmW4mnIk", "title": "Masquerade Trailer", "note": "2018", "length": "1:19"},
            {"id": "y1Lr7ViWMcE", "title": "Masquerade Trailer", "note": "2017", "length": "1:39"},
            {"id": "fVA42gm00PY", "title": "Masquerade Trailer", "note": "2016", "length": "1:30"},
            {"id": "7Boq4RjnQ30", "title": "Zangoora — Trailer", "note": "2015", "length": "2:17"},
            {"id": "SsI4Tm5PP8Q", "title": "Masquerade Trailer", "note": "2013", "length": "2:47"},
        ],
    },
    {
        "id": "vishwamitra", "name": "Vishwamitra", "numeral": "III",
        "title": "El Diablo", "year": 2025, "date": "25 November",
        "drive_folder": "54. Masquerade / Smaran/Vishwamitra, Abarna (25 November)",
        "recording": None,
        "trailers": [{"id": "G5C-ZwOjFfc", "length": "1:31", "label": "Trailer",
                      "title": "El Diablo | Vishwamitra Productions | Trailer"}],
        "card": "vishwamitra25-green",
        "layout": [
            ("feature", ["vishwamitra25-cobwebs", "vishwamitra25-flowers", "vishwamitra25-stick"]),
            ("full", ["vishwamitra25-courtyard"]),
            ("trio", ["vishwamitra25-leaves", "vishwamitra25-guitar", "vishwamitra25-plates"]),
            ("duo", ["vishwamitra25-held", "vishwamitra25-rope"]),
            ("duo", ["vishwamitra25-dance", "vishwamitra25-orange"]),
            ("duo", ["vishwamitra25-waistcoat", "vishwamitra25-face-to-face"]),
        ],
        "lead": photo("vishwamitra25-skull", "1EMjWvKzB0VwwOQrbFzp-s9WtiqN0vIzt", "DSC05629.JPG", mq("Abarna"), L,
                      "An actor in skull face paint with red-painted hands, arms spread, before a wooden wall hung with shields",
                      "Skull paint, arms spread", (0.45, 0.4), "xl"),
        "gallery": [
            photo("vishwamitra25-green", "1zapIaZ5yqGXGQI3I48WQcgK25VFZrtug", "DSC05454.JPG", mq("Abarna"), L,
                  "A performer lit green beside a painted skeleton figure",
                  "Green light and a painted figure", (0.35, 0.4)),
            photo("vishwamitra25-flowers", "1gFIT20gdQYmBY3kl4XIPpavwj68S8Syp", "DSC05434.JPG", mq("Abarna"), L,
                  "Two performers side by side, one with flowers in her hair",
                  "Flowers in her hair", (0.5, 0.4)),
            photo("vishwamitra25-stick", "15uN4dzQ96znJaBNEZawH2Eks_Mb-9BFQ", "DSC05463.JPG", mq("Abarna"), L,
                  "An actor made up with grey hair, leaning on a stick in the dark",
                  "Grey hair and a walking stick", (0.4, 0.4)),
            photo("vishwamitra25-dance", "1lhP1BwKgswfj6A2fMTSkai9Lt9UV3CqO", "DSC05486.JPG", mq("Abarna"), L,
                  "A performer in a satin dress dancing, one arm raised",
                  "Mid-dance", (0.55, 0.4)),
            photo("vishwamitra25-cobwebs", "1RacD-rV9WRMQGBxR-IyjKTGrPnlQMBb4", "DSC05514.JPG", mq("Abarna"), L,
                  "An actor in skull face paint in a green set strung with cobwebs",
                  "The cobweb set", (0.4, 0.45)),
            photo("vishwamitra25-courtyard", "1_OhtHaL_JlnmusFxmU9gPViUkwlyRrVg", "IMG_7665.JPG", mq("Smaran/Vishwamitra"), C,
                  "The company across a blue courtyard set",
                  "The company in the courtyard", (0.5, 0.6)),
            photo("vishwamitra25-leaves", "1dPr_zn27J5kzkV6Y9qr8ws7k4INpZgYe", "DSC05560.JPG", mq("Abarna"), L,
                  "Two performers among giant painted leaves, one with flowers in her hair",
                  "Among the leaves", (0.4, 0.4)),
            photo("vishwamitra25-guitar", "1irWL1c8Fj36XdOTScQeWj6W-MAqTx_Am", "DSC05568.JPG", mq("Abarna"), L,
                  "A boy playing a guitar at a stall beneath a hand-painted sign",
                  "A guitar at the stall", (0.45, 0.5)),
            photo("vishwamitra25-plates", "1BNZMowkYes3iDDRpqYiwzGYhNCKpeiPK", "DSC05571.JPG", mq("Abarna"), L,
                  "One actor climbing onto another's back beside a wall of hanging plates",
                  "The wall of plates", (0.45, 0.45)),
            photo("vishwamitra25-held", "1EbyatY_X1iLbRP1kaBmQlfIgoxCCDts3", "DSC05636.JPG", mq("Abarna"), L,
                  "An actor holding another, in skull face paint, from behind",
                  "Held from behind", (0.5, 0.45)),
            photo("vishwamitra25-rope", "1loGNUqAQ59fDmPVlpwkCySQGRoBy0mPo", "DSC05667.JPG", mq("Abarna"), L,
                  "An actor tied with pink rope before a blue cavern backdrop",
                  "Tied in the cavern", (0.5, 0.55)),
            photo("vishwamitra25-orange", "1T32puOYYkx0mCkMCIcJlKRL26xuVf5Lh", "DSC05682.JPG", mq("Abarna"), L,
                  "A performer in an orange satin dress, one hand on her hip",
                  "In orange", (0.55, 0.4)),
            photo("vishwamitra25-waistcoat", "1oa1-zBxUsGZuFq9jW3mgLR1SB8kwyKKs", "DSC05693.JPG", mq("Abarna"), L,
                  "An actor in a purple waistcoat with arms spread",
                  "The purple waistcoat", (0.5, 0.4)),
            photo("vishwamitra25-face-to-face", "1YM-RsTDy3KvAnmpuNWvVjtnRA17refnJ", "DSC05707.JPG", mq("Abarna"), L,
                  "Two performers facing each other in warm light",
                  "Face to face", (0.5, 0.45)),
        ],
        "more": [
            {"id": "ZlWd-PLTHaI", "title": "The Imperium", "note": "Masquerade 2024 · the production", "length": "73:59"},
            {"id": "2MzXLwLoszE", "title": "The Imperium — Trailer", "note": "Masquerade 2024", "length": "2:03"},
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
        "title": "Ivysherin", "year": 2025, "date": "26 November",
        "drive_folder": "54. Masquerade / Radha, Abarna (26 November)",
        "recording": None,
        "trailers": [{"id": "khzY2dwtnrE", "length": "2:10", "label": "Trailer",
                      "title": "Ivysherin | Vyasa Productions | Trailer"}],
        "card": "vyasa25-staff",
        "layout": [
            ("feature", ["vyasa25-wanted", "vyasa25-make-up", "vyasa25-violin"]),
            ("full", ["vyasa25-ensemble"]),
            ("trio", ["vyasa25-bunting", "vyasa25-leather", "vyasa25-bass"]),
            ("duo", ["vyasa25-porch", "vyasa25-fence"]),
            ("duo", ["vyasa25-blue", "vyasa25-fallen"]),
            ("duo", ["vyasa25-lifted", "vyasa25-red-coat"]),
        ],
        "lead": photo("vyasa25-circus", "1xBKyqOODP5oJG0UfHDrmIXBAHxKdKKBO", "DSC07298.JPG", mq("Radha"), L,
                      "The company in a line before red-and-white striped curtains, beneath a sign reading Circus",
                      "Under the circus sign", (0.5, 0.55), "xl"),
        "gallery": [
            photo("vyasa25-staff", "1BGDQuWHukC5Jt6DaVvcWTMhLs3mC1rIk", "DSC05764.JPG", mq("Abarna"), L,
                  "A figure in a shaggy cloak holding a skull-topped staff, lit green and gold",
                  "The skull-topped staff", (0.55, 0.4)),
            photo("vyasa25-make-up", "191l46oVN9KQAeBKdIEs-YgfzbYb7mSQ3", "DSC05751.JPG", mq("Abarna"), L,
                  "Backstage: a student painting cracks onto a cast member's face",
                  "Backstage, in make-up", (0.5, 0.4)),
            photo("vyasa25-violin", "10TsjuKjPlrbC8dLQK58qHtY2u7Dnw0_B", "DSC05784.JPG", mq("Abarna"), L,
                  "An actor playing a violin before a giant playing card",
                  "A violin and a playing card", (0.55, 0.45)),
            photo("vyasa25-bunting", "1ZYrjqNPpNGhJbXYFQWzqKfJp7Rfg1R50", "DSC05815.JPG", mq("Abarna"), L,
                  "An actor in a waistcoat with a fist raised beside a younger actor in a bow tie, bunting above",
                  "Beneath the bunting", (0.4, 0.45)),
            photo("vyasa25-fence", "1gAWZaQTzZxZwgUzCW86fzIHTDJnxZ_dB", "DSC05840.JPG", mq("Abarna"), L,
                  "Two boys talking on a lawn before a wooden fence",
                  "By the fence", (0.5, 0.5)),
            photo("vyasa25-wanted", "1pMBnUAWYGCp81xvGNusl1wChOTTpqIJ-", "DSC05855.JPG", mq("Abarna"), L,
                  "An actor in a fringed waistcoat seated before a board reading Wanted",
                  "The Wanted board", (0.4, 0.5)),
            photo("vyasa25-bass", "1qsuROEtXV2bXP2M-56H1MEMvvj6FnUSQ", "DSC05971.JPG", mq("Abarna"), L,
                  "An actor with a bass guitar between two others before striped curtains",
                  "The bass guitar", (0.5, 0.45)),
            photo("vyasa25-porch", "1_kBytpkHdLtk5fcvNpydmJEeizoymkIL", "DSC05993.JPG", mq("Abarna"), L,
                  "An actor holding a violin and a boy on a porch set at night",
                  "On the porch", (0.5, 0.45)),
            photo("vyasa25-lifted", "10N-ICxMdN14MYSjGkrijY-cdLEuGN8mA", "DSC06047.JPG", mq("Abarna"), L,
                  "A performer in clown face paint lifted high by others",
                  "Lifted high", (0.5, 0.4)),
            photo("vyasa25-blue", "1wRqAcmtgn0mMtiT5N6mGhsWeHlufBCWY", "DSC07303.JPG", mq("Radha"), L,
                  "Two actors clasped together under blue light before striped curtains",
                  "Under blue light", (0.45, 0.45)),
            photo("vyasa25-fallen", "19H6OW-i7byaQdkmvylSBaL96oLwRocRx", "DSC07318.JPG", mq("Radha"), L,
                  "An actor kneeling over another who lies on the floor, before striped curtains",
                  "Kneeling over him", (0.5, 0.55)),
            photo("vyasa25-red-coat", "1ZxyZ7eOxI5gMetqeA7lYr3MTc10DKFxX", "DSC07324.JPG", mq("Radha"), L,
                  "An actor in a red coat, arm raised, among dancers under purple light",
                  "The red coat", (0.4, 0.45)),
            photo("vyasa25-ensemble", "1gYYDz1l0cezYfZWEhuIF5chx1Eiu5bes", "DSC07325.JPG", mq("Radha"), L,
                  "The ensemble dancing under blue light around an actor raising a staff",
                  "The ensemble", (0.5, 0.5)),
            photo("vyasa25-leather", "1w9p-14OX0gfCPRRG_UJ_l9aLgWullOjL", "DSC05933.JPG", mq("Abarna"), L,
                  "A performer in a leather jacket, arms spread, before striped curtains",
                  "Arms spread before the curtains", (0.5, 0.4)),
        ],
        "more": [
            {"id": "QB5y9Y4h-k0", "title": "Iridescente", "note": "Masquerade 2024 · the production", "length": "68:00"},
            {"id": "XgO-X6jokU0", "title": "Iridescente — Trailer", "note": "Masquerade 2024", "length": "2:01"},
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
    if p.get("fit") == "contain":
        cls = (cls + " is-whole").strip()
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
    <p class="th-programme__label" id="th-programme-title">Three ways to take the stage</p>
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
      <div><dt>Production</dt><dd><em>{esc(au["title"])}</em></dd></div>
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


# The rows stay side by side down to 761px (assets/css/theatre.css goes to one
# column at 760px), so a tablet draws a third of a row about 40vw wide, not
# the whole window: measured, not assumed, at 768 and 820px.
ROW_SIZES = {
    "feature": ["(min-width: 900px) 64vw, (min-width: 761px) 90vw, 100vw",
                "(min-width: 900px) 32vw, (min-width: 761px) 40vw, 100vw",
                "(min-width: 900px) 32vw, (min-width: 761px) 40vw, 100vw"],
    "full": ["(min-width: 1320px) 1320px, 100vw"],
    "trio": ["(min-width: 900px) 32vw, (min-width: 761px) 40vw, 100vw"] * 3,
    "duo": ["(min-width: 900px) 58vw, (min-width: 761px) 71vw, 100vw",
            "(min-width: 900px) 40vw, (min-width: 761px) 51vw, 100vw"],
}


def _row(kind, photos, group, start):
    figs = []
    for i, p in enumerate(photos):
        portrait = p["src"][1] > p["src"][0]
        cls = f"th-g th-g--{kind}-{i}" + (" is-portrait" if portrait else "")
        sizes = "(min-width: 761px) 30vw, 100vw" if portrait else ROW_SIZES[kind][i]
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


def _watch_bar(h):
    """The production when the school has published it; otherwise its
    trailers, and a plain note that the full recording is not online."""
    rec, trailers = h.get("recording"), h.get("trailers", [])
    parts = []
    if rec:
        parts.append(f'<a class="th-watch__link" href="{watch(rec["id"])}"{EXTERNAL}><span class="th-watch__play" aria-hidden="true"></span>'
                     f'Watch the production <span class="th-watch__len">{rec["length"]}</span>{NEW_TAB}</a>')
    for j, t in enumerate(trailers):
        if not rec and j == 0:
            parts.append(f'<a class="th-watch__link" href="{watch(t["id"])}"{EXTERNAL}><span class="th-watch__play" aria-hidden="true"></span>'
                         f'Watch the trailer <span class="th-watch__len">{t["length"]}</span>{NEW_TAB}</a>')
        else:
            parts.append(f'<a class="th-watch__alt" href="{watch(t["id"])}"{EXTERNAL}>{t["label"]} <span class="th-watch__len">{t["length"]}</span>{NEW_TAB}</a>')
    parts.append(f'<button type="button" class="th-watch__alt th-house__view" data-th-view="{h["id"]}" hidden>Open the photographs</button>')
    note = ("" if rec else
            '\n        <p class="th-house__note">The full recording of this production is not on the school&rsquo;s channel.</p>')
    return '<p class="th-watch th-watch--dark">' + "\n          ".join(parts) + "</p>" + note


def house_html(h, i):
    photos = house_photos(h)
    lead = photos[0]
    watch_bar = _watch_bar(h)
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
            <span class="th-house__kicker">{h["name"]} House &middot; Masquerade {h["year"]} &middot; {h["date"]}</span>
            <h3 class="th-house__play serif" id="{h["id"]}-title" tabindex="-1"><span class="sr-only">{h["name"]} House: </span><em>{esc(h["title"])}</em></h3>
            <span class="th-house__count">{house_count(h)} photographs &middot; {esc(lead["caption"])}</span>
          </div>
        </figcaption>
      </figure>
      <div class="wrap th-house__bar">
        {watch_bar}
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
            <span class="th-bill__meta">{h["date"]} &middot; {house_count(h)} photographs</span>
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
      <p class="th-bill__season">The programme &middot; Masquerade {HOUSES[0]["year"]}, {HOUSES[0]["date"].split()[0]}&ndash;{HOUSES[-1]["date"]}</p>
      <p class="th-bill__note">Four productions and {total_masquerade()} photographs from the school&rsquo;s archive. Choose a house, or step through every photograph in order.</p>
      <button type="button" class="th-bill__all" data-th-view="all" hidden>View all {total_masquerade()} photographs</button>
    </div>
    <ol class="th-bill__list">
{chr(10).join(cards)}
    </ol>
  </div>

  <div class="th-houses">
    <nav class="th-rail" aria-label="Masquerade {HOUSES[0]["year"]} houses">
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
      <p class="lead">Every class of twenty-five gets the opportunity to put up a theatrical presentation in the school assembly once a year. Engaging every student through acting, dance, tech and lighting, theatre here is not limited to drama clubs but brings every pupil into its embrace. This is where prodigies are born.</p>
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
