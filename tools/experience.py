"""The CIRS experience — the school day, its photographs, and what is unresolved.

Every time The CIRS experience states is written from this file, and nowhere
else. tools/build-site.py calls expand() to write, from the same two lists:

    the parallel day      twelve events, each with the Junior and Senior slots
                          it covers; assets/js/student-life-journey.js reads
                          them back out of the page to drive the pinned stage
                          on a wide screen
    the full timetables   one table per school, under Practical information

so the timeline, the phone sequence, the reduced-motion view and the tables
cannot disagree: there is one timetable, rendered four ways.

tools/make-experience.py cuts the page's photographs from PHOTOS below.

Where the timetable comes from
------------------------------
The school's own timetable, as it reached this repository in September 2026
and was drawn on the old Student Life page as two proportional tracks
(commit 92c1a198, "Rebuild the day scroll from the real timetable, as two
tracks"). The one gap in it — Junior 8:30 to 9:00 pm — was filled when the
school said it is milk time, followed by sleep (commit 8e793da6). Seventeen
Senior slots and eighteen Junior slots, every minute of both days accounted
for, labels as the school gave them.

The narrative copy is the owner's approved text (commit e57070c0, "Update
CIRS site copy from approved document") wherever it says something about the
day. The twelve events and their order are the owner's (27 September 2026).

An older routine exists on the school's Drive: daily_routine.html from the
2012 website ("5.10am to 9.15pm for juniors and from 5.40am to 10.30pm for
seniors"). It is superseded by the timetable above and is not used.

Not published — see UNRESOLVED at the foot of this file.
"""

import html

DIR = "assets/img/experience"

JUNIOR_NAME, JUNIOR_GRADES = "Junior School", "Grades V&ndash;VIII"
SENIOR_NAME, SENIOR_GRADES = "Senior School", "Grades IX&ndash;XII"

# (start, end, activity, kind). Times are 24-hour; kind is only the family an
# hour belongs to, used for the faint key on the day rail, never as the sole
# carrier of meaning.
JUNIOR = [
    ("04:50", "05:30", "Rouser",                    "wake"),
    ("05:30", "06:00", "Jogging",                   "active"),
    ("06:00", "06:50", "Milk and getting ready",    "wake"),
    ("06:50", "07:25", "Spiritual class",           "spirit"),
    ("07:25", "07:50", "Breakfast",                 "meal"),
    ("07:50", "08:10", "Assembly",                  "spirit"),
    ("08:10", "10:55", "Academic classes",          "study"),
    ("10:55", "11:15", "Juice break",               "meal"),
    ("11:15", "12:20", "Academic classes",          "study"),
    ("12:20", "14:00", "Lunch and rest",            "meal"),
    ("14:00", "16:00", "Study time",                "study"),
    ("16:00", "17:15", "Sports",                    "active"),
    ("17:15", "18:30", "Snacks and getting ready",  "wake"),
    ("18:30", "19:10", "Prayer and aarti",          "spirit"),
    ("19:10", "19:40", "Dinner",                    "meal"),
    ("19:40", "20:30", "Self study",                "study"),
    ("20:30", "21:00", "Milk",                      "meal"),
    ("21:00", "21:30", "Lights off",                "rest"),
]

SENIOR = [
    ("05:30", "06:00", "Rouser",                    "wake"),
    ("06:00", "06:30", "Jogging",                   "active"),
    ("06:30", "07:30", "Milk and getting ready",    "wake"),
    ("07:30", "08:10", "Spiritual class",           "spirit"),
    ("08:10", "08:45", "Breakfast",                 "meal"),
    ("08:45", "09:10", "Assembly",                  "spirit"),
    ("09:10", "10:55", "Academic classes",          "study"),
    ("10:55", "11:15", "Juice break",               "meal"),
    ("11:15", "13:30", "Academic classes",          "study"),
    ("13:30", "15:20", "Lunch and rest",            "meal"),
    ("15:20", "17:00", "Study time",                "study"),
    ("17:00", "18:30", "Sports",                    "active"),
    ("18:30", "19:30", "Snacks and getting ready",  "wake"),
    ("19:30", "20:10", "Prayer and aarti",          "spirit"),
    ("20:10", "20:40", "Dinner",                    "meal"),
    ("20:40", "22:00", "Self study and co-curricular work", "study"),
    ("22:00", "22:30", "Milk, lights off",          "rest"),
]

# The day as the owner lists it: twelve events, in order. Each names the slots
# it covers in both timetables, by position in JUNIOR and SENIOR above, so
# every slot belongs to exactly one event and the two schools are compared
# event by event: the event in the middle, each school's own times beside it.
#   title   the event, as the owner named it
#   short   its label on the row of steps under the stage
#   scene   the photograph shown with it (a scene may return later in the day;
#           its figure is written once, with the first event that uses it)
#   line    one sentence; approved copy where the approved document says it
EVENTS = [
    {"slug": "rouser", "title": "Rouser, jogging and milk", "short": "Rouser",
     "scene": "jog", "junior": [0, 1, 2], "senior": [0, 1, 2],
     "line": "Before first light, students get ready and head to the Arjuna athletic "
             "field for a morning jog, then return to the dorms for hot milk and biscuits."},
    {"slug": "spiritual-class", "title": "Spiritual class", "short": "Spiritual class",
     "scene": "spiritual-hall", "junior": [3], "senior": [3],
     "line": "Bhagavad Gita shlokas, stotram and japa."},
    {"slug": "breakfast", "title": "Breakfast", "short": "Breakfast",
     "scene": "onam-lunch", "junior": [4], "senior": [4],
     "line": "Breakfast at the Annakshetra."},
    {"slug": "assembly", "title": "Assembly", "short": "Assembly",
     "scene": "prayer-hall", "junior": [5], "senior": [5],
     "line": "The Principal addresses the school, and students regularly offer talks, "
             "speeches, book reviews and quizzes."},
    {"slug": "classes", "title": "Classes", "short": "Classes",
     "scene": "classroom", "junior": [6], "senior": [6],
     "line": "The academic morning, until the juice break."},
    {"slug": "juice-break", "title": "Juice break", "short": "Juice break",
     "scene": "classroom", "junior": [7], "senior": [7],
     "line": "The one pause both schools take at the same minute."},
    {"slug": "classes-2", "title": "Classes", "short": "Classes",
     "scene": "classroom", "junior": [8], "senior": [8],
     "line": "Lessons resume until lunch."},
    {"slug": "lunch", "title": "Lunch and rest", "short": "Lunch",
     "scene": "onam-lunch", "junior": [9], "senior": [9],
     "line": "Students return to the Annakshetra for lunch, then rest and reset for "
             "the afternoon."},
    {"slug": "study", "title": "Study time", "short": "Study",
     "scene": "laptop", "junior": [10], "senior": [10],
     "line": "A focused study period bridges classroom learning and the playing fields."},
    {"slug": "sports", "title": "Sports", "short": "Sports",
     "scene": "field", "junior": [11], "senior": [11],
     "line": "The day moves outdoors for organised sport and movement."},
    {"slug": "aarti", "title": "Snacks and aarti", "short": "Aarti",
     "scene": "prayer-hall", "junior": [12, 13], "senior": [12, 13],
     "line": "Snacks and time to get ready lead into prayer and aarti."},
    {"slug": "dinner", "title": "Dinner, study and milk", "short": "Dinner",
     "scene": "reading", "junior": [14, 15, 16, 17], "senior": [14, 15, 16],
     "line": "Dinner, then self study, and milk before lights off."},
]

# Every photograph the page shows, with where it came from and what it shows.
# "src" is a camera original in assets/source/; "drive" is a file on the
# school's Google Drive (the owner's account), fetched by
# tools/make-experience.py through Drive's image endpoint, as the Theatre
# originals are. Captions say only what the picture shows: none of these is a
# time-stamped record of one day, and the page says so.
#   crops   name -> (width/height ratio, focal x, focal y, [widths])
PHOTOS = {
    "hero": {
        "src": "IMG_2327.JPG",
        "alt": "CIRS students running together across the athletic field, trees behind them",
        "crops": {"wide": (3 / 2, 0.52, 0.50, [960, 1600, 2400]),
                  "tall": (2 / 3, 0.60, 0.44, [720, 1080])},
    },
    "jog": {
        "src": "drive-hrun-04.jpg",
        "caption": "Jogging on the campus road, past the signpost to the Annakshetra and the residences",
        "crops": {"wide": (3 / 2, 0.50, 0.46, [800, 1280, 1920])},
    },
    # A video still the owner supplied on 27 September 2026 (see the README in
    # its folder); 1683px of it survive the 3:2 cut, so it stops at 1600.
    "spiritual-hall": {
        "src": "experience-2026-09-27/spiritual-hall.webp",
        "caption": "In the hall beneath Pujya Gurudev&rsquo;s portrait",
        "crops": {"wide": (3 / 2, 0.47, 0.50, [800, 1280, 1600])},
    },
    "classroom": {
        "src": "IMG_1933.JPG",
        "caption": "A junior class at work with their teacher",
        "crops": {"wide": (3 / 2, 0.50, 0.50, [800, 1280, 1920])},
    },
    "onam-lunch": {
        "drive": "1ZmtSRendHmJwWV7FLIH5-OeCj5BJjZe4",
        "drive_file": "CRS09901.JPG",
        "drive_folder": "59. Onam / lunch (Onam 2023; see tools/festivals.py)",
        "caption": "Onam lunch in the dining hall",
        "crops": {"wide": (3 / 2, 0.50, 0.50, [800, 1280, 1920])},
    },
    "laptop": {
        "src": "IMG_1900.JPG",
        "caption": "Working together on a circuit and a laptop",
        "crops": {"wide": (3 / 2, 0.52, 0.52, [800, 1280, 1920])},
    },
    "field": {
        "src": "8A5A3313.JPG",
        "caption": "A bicycle kick on the field below the hills",
        "crops": {"wide": (3 / 2, 0.50, 0.46, [800, 1280, 1920])},
    },
    "prayer-hall": {
        "src": "CRS09514.JPG",
        "caption": "Prayer in the hall",
        "crops": {"wide": (3 / 2, 0.50, 0.46, [800, 1280, 1920])},
    },
    "reading": {
        "src": "IMG_8830.JPG",
        "caption": "Studying together, out of uniform",
        "crops": {"wide": (3 / 2, 0.52, 0.50, [800, 1280, 1920])},
    },
    "together": {
        "src": "20180518_121042.jpg",
        "alt": "Senior students sitting together, laughing, on a platform of logs among the trees",
        "caption": "Seniors together, out of uniform",
        "crops": {"tall": (4 / 5, 0.52, 0.50, [640, 960, 1280])},
    },
    "vishu-lunch": {
        "drive": "19jA9ZqJJa0RVQpp8KuDUNbCN8vVl9RgP",
        "drive_file": "IMG_9126.JPG",
        "drive_folder": "tamil new year and vishu / afternoon lunch",
        "alt": "Junior boys at a dining-hall table with steel plates and tumblers, waving at the camera",
        "caption": "Lunch on Vishu and Tamil New Year, in the dining hall",
        "crops": {"wide": (3 / 2, 0.40, 0.55, [640, 1000, 1400])},
    },
    "billiards": {
        "src": "IMG_0862.JPG",
        "alt": "A student lining up a shot at a billiards table while two friends watch",
        "caption": "A game of billiards",
        "crops": {"wide": (3 / 2, 0.55, 0.50, [640, 1000, 1400])},
    },
    "tyre": {
        "src": "drive-hrun-02.jpg",
        "alt": "A junior student laughing as she swings through a hanging tyre, friends walking behind",
        "caption": "The tyre swing",
        "crops": {"tall": (4 / 5, 0.50, 0.55, [640, 960, 1280])},
    },
    # Supplied with the hall above; 900px wide once cut to 4:5, framed on the
    # two girls so the crop does not run through the boys beside them.
    "flute": {
        "src": "experience-2026-09-27/flute.webp",
        "alt": "Two students in school uniform seated on a rug, playing bamboo flutes",
        "caption": "Flute practice",
        "crops": {"tall": (4 / 5, 0.82, 0.50, [640, 900])},
    },
    "puja": {
        "src": "IMG_0081.JPG",
        "alt": "Students in yellow kurtas seated in a long row on the floor, each with a plate of flowers for a puja",
        "caption": "Students seated for a puja",
        "crops": {"tall": (4 / 5, 0.62, 0.55, [640, 960, 1280])},
    },
    "night": {
        "src": "IMG_2480.JPG",
        "alt": "Students in yellow kurtas seated in the lit amphitheatre after dark, a teacher facing them",
        "crops": {"wide": (3 / 2, 0.50, 0.50, [1280, 1920]),
                  "tall": (2 / 3, 0.46, 0.50, [720, 1080])},
    },
}

# What could not be settled from any source this repository has. Nothing here
# is published; the page shows the timetable's own slots instead of choosing.
UNRESOLVED = [
    "Juice break length: the timetable gives 10:55 to 11:15 (twenty minutes) for both "
    "schools; the approved copy of September 2026 calls it 'a fifteen-minute juice "
    "break'. The page shows the timetable's slot and does not state a length.",
    "Lights off: the timetable's last slots are 'Lights off, 9:00-9:30 pm' (Junior) "
    "and 'Milk, lights off, 10:00-10:30 pm' (Senior). Whether lights go off at the "
    "start or the end of each slot is not stated anywhere. The old page's closing "
    "said '10:30 PM - Lights out' and one chapter 'At 10:30, the senior houses rest'. "
    "The page gives both slots as they are and names no single lights-out time.",
    "The Sports page's own routine (tools/pages/sports.html, #routine) gives "
    "'08:10 AM - 13:30' for classes, '18:30 - 20:10' for prayer and aarti, '22:00 PM' "
    "for lights out and 'ninety minutes' of sport; each mixes the two schools' times. "
    "Not changed here: it is another page.",
    "Enrolment: the old page said 'Six hundred students'. No figure is published "
    "anywhere on the site (School Information defers to the enrolment table), so the "
    "page gives none.",
]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def clock(hhmm):
    """'13:30' -> ('1:30', 'pm')."""
    h, m = (int(x) for x in hhmm.split(":"))
    return f"{(h - 1) % 12 + 1}:{m:02d}", ("am" if h < 12 else "pm")


def span(start, end):
    """'4:50–5:30 am', or '11:15 am – 1:30 pm' across noon, each in a <time>."""
    (a, ap), (b, bp) = clock(start), clock(end)
    first = f'<time datetime="{start}">{a}</time>'
    second = f'<time datetime="{end}">{b}&nbsp;{bp}</time>'
    if ap == bp:
        return f"{first}&ndash;{second}"
    return f'<time datetime="{start}">{a}&nbsp;{ap}</time> &ndash; {second}'


def when(hhmm):
    c, p = clock(hhmm)
    return f'<time datetime="{hhmm}">{c}&nbsp;{p}</time>'


def files(key, crop):
    ratio, fx, fy, widths = PHOTOS[key]["crops"][crop]
    return [(f"{DIR}/{key}-{crop}-{w}.webp", w, round(w / ratio)) for w in widths]


def srcset(key, crop, bust):
    return ", ".join(f"{path}?{bust} {w}w" for path, w, _ in files(key, crop))


def img(key, crop, bust, sizes, alt="", cls="", lazy=True, extra=""):
    cut = files(key, crop)
    path, w, h = cut[len(cut) // 2] if len(cut) > 2 else cut[-1]
    load = ' loading="lazy"' if lazy else ""
    klass = f' class="{cls}"' if cls else ""
    return (f'<img{klass} src="{path}?{bust}" srcset="{srcset(key, crop, bust)}" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{alt}"{load} '
            f'decoding="async"{extra}>')


def slots_of(ev, side):
    schedule = JUNIOR if side == "junior" else SENIOR
    return [schedule[i] for i in ev[side]]


def duration(mins):
    h, m = divmod(mins, 60)
    parts = ([f"{h} hour" + ("s" if h > 1 else "")] if h else []) + \
            ([f"{m} minutes"] if m else [])
    return " ".join(parts)


def gap(ev):
    """How the two schools' timings for one event compare, from the slots alone."""
    j, s = slots_of(ev, "junior"), slots_of(ev, "senior")
    js, ss = minutes(j[0][0]), minutes(s[0][0])
    je, se = minutes(j[-1][1]), minutes(s[-1][1])
    if js == ss and je == se:
        return "Both schools, the same time", True
    if js == ss:
        return "Both schools begin together", False
    first, later = ("Senior", ss - js) if ss > js else ("Junior", js - ss)
    return f"{first} School starts {duration(later)} later", False


def _track(side, name, grades, ev):
    rows = slots_of(ev, side)
    items = "\n".join(
        f'              <li data-start="{minutes(a)}" data-end="{minutes(b)}" data-kind="{k}">'
        f'<span class="xp__what">{what}</span> <span class="xp__time">{span(a, b)}</span></li>'
        for a, b, what, k in rows)
    one = " xp__slots--one" if len(rows) == 1 else ""
    return f'''          <div class="xp__track xp__track--{side}" data-track="{side}">
            <h4 class="xp__school">{name} <span>{grades}</span></h4>
            <div class="xp__body" data-body>
              <p class="xp__range">{span(rows[0][0], rows[-1][1])}</p>
              <ul class="xp__slots{one}">
{items}
              </ul>
            </div>
          </div>'''


def event_html(i, ev, bust):
    scene = ev["scene"]
    owner = scene and next(e for e in EVENTS if e["scene"] == scene) is ev
    figure = ""
    if owner:
        figure = f'''      <figure class="xp__photo" data-scene="{scene}">
        {img(scene, "wide", bust, "100vw")}
        <figcaption>{PHOTOS[scene]["caption"]}</figcaption>
      </figure>
'''
    note, same = gap(ev)
    j, s = slots_of(ev, "junior"), slots_of(ev, "senior")
    return f'''    <li class="xp" id="day-{ev["slug"]}" data-event="{i}" data-scene="{scene or ""}" data-short="{ev["short"]}"{' data-same' if same else ''}>
{figure}      <div class="xp__text">
        <p class="xp__when"><span>Junior {when(j[0][0])}</span> <span>Senior {when(s[0][0])}</span></p>
        <h3 class="xp__title">{ev["title"]}</h3>
        <p class="xp__gap">{note}</p>
        <p class="xp__line">{ev["line"]}</p>
        <div class="xp__tracks">
{_track("junior", JUNIOR_NAME, JUNIOR_GRADES, ev)}
{_track("senior", SENIOR_NAME, SENIOR_GRADES, ev)}
        </div>
      </div>
    </li>'''


def day_html(bust):
    events = "\n".join(event_html(i, e, bust) for i, e in enumerate(EVENTS))
    first, last = JUNIOR[0][0], SENIOR[-1][1]
    buttons = "\n".join(
        f'        <li><button type="button" class="xd__jump" data-go="{i}" '
        f'aria-label="{i + 1} of {len(EVENTS)}: {html.unescape(e["title"])}">{e["short"]}</button></li>'
        for i, e in enumerate(EVENTS))
    return f'''<div class="xd__run" data-xd-run data-first="{minutes(first)}" data-last="{minutes(last)}">
  <div class="xd__stage" data-xd-stage>
    <div class="xd__scrim" aria-hidden="true"></div>
    <ol class="xd__phases">
{events}
    </ol>
    <div class="xd__live" aria-hidden="true" data-xd-live>
      <div class="xd__card xd__card--junior" data-card="junior">
        <p class="xd__school">{JUNIOR_NAME}<span>{JUNIOR_GRADES}</span></p>
        <div class="xd__body" data-body></div>
      </div>
      <div class="xd__centre">
        <p class="xd__count"><span data-count>01</span> / {len(EVENTS):02d}</p>
        <p class="xd__title" data-title></p>
        <p class="xd__gap" data-gap></p>
        <p class="xd__line" data-line></p>
      </div>
      <div class="xd__card xd__card--senior" data-card="senior">
        <p class="xd__school">{SENIOR_NAME}<span>{SENIOR_GRADES}</span></p>
        <div class="xd__body" data-body></div>
      </div>
      <p class="xd__caption" data-caption></p>
      <div class="xd__rail">
        <p class="xd__rail-key"><span>Junior</span><span>Senior</span></p>
        <div class="xd__ribbons" data-ribbons></div>
      </div>
    </div>
    <nav class="xd__nav" aria-label="Move through the day" data-xd-nav hidden>
      <button type="button" class="xd__step" data-step="-1" aria-label="Previous event"><span aria-hidden="true">&larr;</span></button>
      <ol class="xd__jumps">
{buttons}
      </ol>
      <button type="button" class="xd__step" data-step="1" aria-label="Next event"><span aria-hidden="true">&rarr;</span></button>
    </nav>
  </div>
</div>
<p class="sr-only" role="status" aria-live="polite" aria-atomic="true" data-xd-status></p>'''


def table_html(side, name, grades, schedule):
    rows = "\n".join(
        f'          <tr><th scope="row">{span(a, b)}</th><td>{what}</td></tr>'
        for a, b, what, _ in schedule)
    return f'''    <details class="xq__table" id="timetable-{side}">
      <summary><span>Full {name} timetable<small>{grades}</small></span></summary>
      <table>
        <caption class="sr-only">{name}, {grades}: the daily timetable</caption>
        <thead><tr><th scope="col">Time</th><th scope="col">Activity</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </details>'''


def tables_html():
    return "\n".join([table_html("junior", JUNIOR_NAME, JUNIOR_GRADES, JUNIOR),
                      table_html("senior", SENIOR_NAME, SENIOR_GRADES, SENIOR)])


def figure(key, crop, bust, sizes, cls="", lazy=True):
    p = PHOTOS[key]
    cap = f'\n    <figcaption>{p["caption"]}</figcaption>' if p.get("caption") else ""
    return (f'<figure class="{cls}">\n    {img(key, crop, bust, sizes, alt=p["alt"], lazy=lazy)}'
            f'{cap}\n  </figure>')


def picture(key, bust, cls, lazy=True, priority=False):
    """A full-bleed photograph: the tall cut on a portrait screen, the wide one otherwise."""
    p = PHOTOS[key]
    wide, tall = files(key, "wide"), files(key, "tall")
    path, w, h = wide[1] if len(wide) > 2 else wide[-1]
    load = ' loading="lazy"' if lazy else ""
    pri = ' fetchpriority="high"' if priority else ""
    return (f'<picture class="{cls}">\n'
            f'    <source media="(max-aspect-ratio: 4/5)" srcset="{srcset(key, "tall", bust)}" sizes="100vw">\n'
            f'    <img src="{path}?{bust}" srcset="{srcset(key, "wide", bust)}" sizes="100vw" '
            f'width="{w}" height="{h}" alt="{p["alt"]}"{load}{pri} decoding="async">\n'
            f'  </picture>')


def house_list():
    import houses
    names = [f'<span class="xl__house xl__house--{h["slug"]}">{h["name"]}</span>'
             for h in houses.HOUSES]
    return ", ".join(names[:-1]) + " and " + names[-1]


def expand(content, bust):
    return (content
            .replace("{{XP_HERO}}", picture("hero", bust, "xh__photo", lazy=False, priority=True))
            .replace("{{XP_DAY}}", day_html(bust))
            .replace("{{XP_TABLES}}", tables_html())
            .replace("{{XP_HOUSES}}", house_list())
            .replace("{{XP_TOGETHER}}", figure("together", "tall", bust,
                     "(min-width: 900px) 44vw, 100vw", "xl__main"))
            .replace("{{XP_VISHU}}", figure("vishu-lunch", "wide", bust,
                     "(min-width: 900px) 26vw, (min-width: 600px) 46vw, 100vw", "xl__detail"))
            .replace("{{XP_BILLIARDS}}", figure("billiards", "wide", bust,
                     "(min-width: 900px) 26vw, (min-width: 600px) 46vw, 100vw", "xl__detail"))
            .replace("{{XP_TYRE}}", figure("tyre", "tall", bust,
                     "(min-width: 900px) 30vw, 100vw", "xb__photo"))
            .replace("{{XP_FLUTE}}", figure("flute", "tall", bust,
                     "(min-width: 900px) 30vw, 100vw", "xb__photo"))
            .replace("{{XP_PUJA}}", figure("puja", "tall", bust,
                     "(min-width: 900px) 30vw, 100vw", "xb__photo"))
            .replace("{{XP_NIGHT}}", picture("night", bust, "xn__photo"))
            .replace("{{XP_JUNIOR_START}}", when(JUNIOR[0][0]))
            .replace("{{XP_SENIOR_END}}", when(SENIOR[-1][1]))
            .replace("{{XP_JUNIOR_LIGHTS}}", span(JUNIOR[-1][0], JUNIOR[-1][1]))
            .replace("{{XP_SENIOR_LIGHTS}}", span(SENIOR[-1][0], SENIOR[-1][1])))


def report():
    """python3 tools/experience.py — the day as data, and what is still open."""
    for name, sched in (("Junior", JUNIOR), ("Senior", SENIOR)):
        total = sum(minutes(b) - minutes(a) for a, b, *_ in sched)
        gaps = [(b, c) for (_, b, *_), (c, *_) in zip(sched, sched[1:]) if b != c]
        print(f"{name}: {len(sched)} slots, {sched[0][0]}-{sched[-1][1]}, "
              f"{total} minutes, gaps: {gaps or 'none'}")
    used = {"junior": [], "senior": []}
    for e in EVENTS:
        for side in used:
            used[side] += e[side]
        j, sn = slots_of(e, "junior"), slots_of(e, "senior")
        print(f"  {e['title']:<26} J {j[0][0]}-{j[-1][1]}  S {sn[0][0]}-{sn[-1][1]}  {gap(e)[0]}")
    print("every slot in exactly one event:",
          sorted(used["junior"]) == list(range(len(JUNIOR))) and
          sorted(used["senior"]) == list(range(len(SENIOR))))
    print("\nUnresolved:")
    for u in UNRESOLVED:
        print("  - " + u)


if __name__ == "__main__":
    report()
