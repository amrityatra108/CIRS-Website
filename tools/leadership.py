"""The Leadership page, as data: the people, their portraits and their messages.

build-site.py writes the page's three generated parts from here —

    {{LEAD_FEATURED}}   the four portraits that open the directory
    {{LEAD_DIRECTORS}}  the three further Directors, compact
    {{LEAD_READER}}     "In their own words": the index and the six messages

— and tools/make-leadership.py cuts every portrait named in PORTRAITS. Keeping
the crop, the file widths and the markup in one place is what stops a srcset
naming a file the script never cut.

WHERE THE WORDS COME FROM

  Roster, names and roles: the school's own management page
  (cirschool.org/management.html) and School Information, with two
  deliberate differences recorded in HOSTING.md — "Shri Ram Buxani" is on
  the school's older list and not on this site's current one, and the school
  writes "Viju" where this site has "Vijay" Mahtaney. Neither is resolved
  here; both are waiting on the school.

  Messages: word for word as the school publishes them, on
  new.cirschool.org/about-us and cirschool.org (the two agree). Greetings and
  sign-offs are kept. The only changes are typographic — curly quotes, dashes
  — and one misspelling, "unsumountable", set as "insurmountable". Do not
  edit a message here for style: it is the author's text, not the site's.

  Introductions: only what the school has published or the person's own
  organisation states. A person with none has none; there is no stand-in.
"""

# ---------------------------------------------------------------------------
# Portraits. slug -> (source, 4:5 crop box in source pixels).
#
# Every box is 4:5 and placed by measurement so the eyes sit about 36% of the
# way down and the whole head is inside with room above it. The boxes are as
# large as each source allows at a similar scale of face: Smt. Shanti
# Krishnamurthy's photograph is full-length, so her face is small in it and
# her portrait is only 356px wide. That is the honest ceiling of the file;
# it is never enlarged past it (see widths()).
#
# A person appears only with a photograph published under their own name —
# supplied by the school, or from the official page of an organisation they
# belong to (originals in assets/source/leadership/, see make-leadership.py).
# Shri Vijay Mahtaney has none, and is shown without one.
# ---------------------------------------------------------------------------
PORTRAITS = {
    "swaroopananda": ("assets/source/leadership/swaroopananda.jpg", (270, 99, 638, 559)),
    "anukoolananda": ("assets/img/swami-anukoolananda.jpg",        (0, 0, 1000, 1250)),
    "krishnamurthy": ("assets/img/shanti-krishnamurthy.jpg",       (274, 80, 630, 525)),
    "rajeshwari":    ("assets/img/principal.jpg",                  (479, 348, 963, 953)),
    "moorjani":      ("assets/source/leadership/moorjani.png",      (55, 0, 455, 500)),
    # The frame on the wall behind him, at the right, stays out.
    "balachandran":  ("assets/source/leadership/balachandran.jpg",  (127, 0, 767, 800)),
    "tejomayananda": ("assets/source/leadership/tejomayananda.jpg", (112, 0, 912, 1000)),
    "chinmayananda": ("assets/img/founder/archive/p607-portrait.webp", (164, 128, 1064, 1253)),
}

STEPS = (320, 480, 640)
CAP = 1000


def widths(slug):
    """The widths a portrait is cut at: a few steps, then its own full width.

    A step is cut only where it is clearly smaller than the source, and
    nothing is ever cut wider than the crop box — a browser upscaling a
    356px file is the file's limit showing; a 720px file made from it would
    be a lie about it.
    """
    box = PORTRAITS[slug][1]
    native = min(box[2] - box[0], CAP)
    return [w for w in STEPS if w <= native * 0.8] + [native]


def portrait_path(slug, w):
    return f"assets/img/leadership/{slug}-{w}.jpg"


def img(slug, alt, sizes, eager=False, cls=""):
    ws = widths(slug)
    big = ws[-1]
    srcset = ", ".join(f"{portrait_path(slug, w)} {w}w" for w in ws)
    load = ('fetchpriority="high" decoding="async"' if eager
            else 'loading="lazy" decoding="async"')
    klass = f' class="{cls}"' if cls else ""
    return (f'<img{klass} src="{portrait_path(slug, big)}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{big}" height="{big * 5 // 4}" alt="{alt}" {load}>')


# The group photograph of staff and faculty. Supplied by the school
# (tools/media.tsv) at 2000px; cut down by make-leadership.py.
STAFF_SOURCE = "assets/img/staff-and-faculty.jpg"
STAFF_WIDTHS = (800, 1200, 1600)


def staff_path(w):
    return f"assets/img/leadership/staff-{w}.jpg"


def staff_html():
    srcset = ", ".join([f"{staff_path(w)} {w}w" for w in STAFF_WIDTHS] + [f"{STAFF_SOURCE} 2000w"])
    return (f'<img src="{STAFF_SOURCE}" srcset="{srcset}" '
            'sizes="(min-width: 1400px) 1320px, calc(100vw - 32px)" width="2000" height="1333" '
            'alt="About ninety members of staff and faculty, seated and standing in rows on the '
            'steps of a campus building, between two pine trees" loading="lazy" decoding="async">')


# ---------------------------------------------------------------------------
# The people. The four who open the page are the school's current officers,
# each with a message. Order is the school's own.
#   note  one line on what the person does for CIRS, first; anything about
#         their life elsewhere after it. None where nothing is published.
# ---------------------------------------------------------------------------
FEATURED = [
    {
        "slug": "swaroopananda", "msg": "chairman",
        "name": "Swami Swaroopanandaji", "role": "Chairman",
        # School Information publishes this, as does cirschool.org.
        "note": "Heads the committee that manages the school. Head of Chinmaya Mission worldwide.",
    },
    {
        "slug": "anukoolananda", "msg": "director",
        "name": "Swami Anukoolanandaji", "role": "Resident Director",
        "note": None,
    },
    {
        "slug": "krishnamurthy", "msg": "academics",
        "name": "Smt. Shanti Krishnamurthy", "role": "Director &mdash; Academics &amp; Administration",
        "note": "Principal of CIRS from 2009, and Director &mdash; Academics and Administration "
                "since 2018. A Director of the CCMT Education Cell.",
    },
    {
        "slug": "rajeshwari", "msg": "principal",
        "name": "Smt. G. Rajeshwari", "role": "Principal",
        "note": None,
    },
]

DIRECTORS = [
    {
        "slug": None,
        "name": "Shri Vijay Mahtaney", "role": "Director",
        # Park Hyatt Chennai: Wikipedia, "built by entrepreneur Vijay
        # Mahtaney ... diversifying into hotels, IT parks and residential
        # projects". The "twenty-eight directorships" and present ownership
        # are dated, so they are gone until the school confirms them.
        "note": "Closely associated with Chinmaya Mission. An entrepreneur who has diversified "
                "into hotels, IT parks and residential development, among them Chennai&rsquo;s "
                "Park Hyatt hotel.",
    },
    {
        "slug": "moorjani",
        "name": "Shri Jagdish Moorjani", "role": "Director",
        # cvv.ac.in/management/mr-jagdish-moorjani; citiustech.com.
        "note": "A trustee of the Chinmaya Vishwa Vidyapeeth Trust. Co-founder of CitiusTech and "
                "TransWorks, he now works in a personal capacity with not-for-profit initiatives "
                "in school education, higher education and healthcare.",
    },
    {
        "slug": "balachandran",
        "name": "Shri Siddharth Balachandran", "role": "Director",
        # The BSE shareholding and the MRAMM award are left out: the first is
        # a ranking that moves, the second could not be confirmed.
        "note": "Executive Chairman and CEO of Buimerc Corporation, Dubai, and a recipient of the "
                "Government of India&rsquo;s Pravasi Bharatiya Samman.",
    },
]


# ---------------------------------------------------------------------------
# The messages, in the order the school publishes them. "group" separates the
# Founder and Pujya Guruji, whose messages belong to the school's beginning,
# from the four who hold office at CIRS today.
#   title    the author's own heading, where the school publishes one
#   open     greeting lines, before the body
#   body     paragraphs, verbatim
#   close    sign-off lines, verbatim
# ---------------------------------------------------------------------------
MESSAGES = [
    {
        "id": "founder", "slug": "chinmayananda", "group": "origin",
        "name": "Pujya Gurudev Swami Chinmayananda", "short": "Swami Chinmayananda",
        "role": "Founder of CIRS",
        "title": None, "open": [],
        "body": [
            "Never before in our national history did the best minds of India move out in such "
            "spectacular numbers to serve communities in distant foreign lands, living amidst "
            "unusual climates, strange food habits, peculiar social customs and confusing cultural "
            "environments. Everywhere young Indians are scoring success with their performances in "
            "science and technology, commerce and art. We salute them for all their excellence and "
            "wish them even greater success in their professions.",
            "Those who have gone abroad with their families try to contribute their Indian way of "
            "life with the lifestyle of their adopted countries. At times such attempts create "
            "pressures and conflicts over moral values and cultural patterns. The children see one "
            "thing at home and meet contradictory situations outside. Because of this bi-cultural "
            "experience they run the risk of picking up attitudes potentially dangerous and "
            "sometimes suicidal to their future happiness and success.",
            "I am glad my suggestions are now fully accepted both in India and abroad. CIRS will "
            "provide an environment that will help integrate the best of each culture. It will be "
            "a cultural home away from home for our growing children.",
            "Send us your children. Let them have one to six years of cultural adventure during "
            "their 11&ndash;18 years of age. Let us give them a chance to understand and absorb "
            "Indian culture and heritage and return to the countries from where they came, to "
            "continue their studies. Let us build up sufficient knowledge and taste in them to "
            "feel a sense of identity with and a pride in their Indian heritage.",
        ],
        "close": [],
    },
    {
        "id": "guruji", "slug": "tejomayananda", "group": "origin",
        "name": "Pujya Guruji Swami Tejomayananda", "short": "Swami Tejomayananda",
        "role": "Pujya Guruji, Chinmaya Mission",
        "title": None, "open": [],
        "body": [
            "The purpose of education is manifold. Literacy and employment are its primary aims. "
            "Another purpose is to make students capable of living their lives fully at all levels "
            "of their personalities. They should be able to face the numerous challenges of life "
            "and carve out a purposeful future for themselves.",
            "At yet another level, the purpose of education is to groom students in noble cultural "
            "values. In the absence of this culture, knowledge itself and material prosperity can "
            "become a weapon of destruction instead of a means of blessing to humanity. Still "
            "higher than this aim is to create a thirst for greater knowledge in students, so that "
            "they discover the mysteries of Nature and the world around them.",
            "The Chinmaya International Residential School at Coimbatore imparts education to "
            "students from India and abroad. Keeping all the aforesaid in view, children get "
            "modern education in an atmosphere of rich Indian culture.",
            "Pujya Gurudev Swami Chinmayananda had laid the foundation of this school in "
            "Coimbatore, a few years ago. He attained Mahasamadhi in August 1993. To realise His "
            "cherished dream is now the sacred duty of us all &mdash; His disciples, devotees, "
            "followers and admirers. Let us come together and pay our respectful homage to Him in "
            "making the Chinmaya International Residential School a reality. May He shower His "
            "grace and blessings on us to make this project a great success.",
        ],
        "close": [],
    },
    {
        "id": "chairman", "slug": "swaroopananda", "group": "today",
        "name": "Swami Swaroopanandaji", "short": "Swami Swaroopanandaji",
        "role": "Chairman",
        "title": "Transcending Limitations", "open": [],
        "body": [
            "Life can be a stormy affair, full of challenges. But if we choose, our storms can "
            "strengthen our character and bring out the greatness in us.",
            "Life constantly presents us with all kinds of challenges. Often, external problems "
            "mirror internal disturbances, which in turn are due to our internal limitations. Our "
            "capacity to meet them depends largely on the strength or weakness of our inner state. "
            "That is why we need to gather strength inwardly: so that we can fulfil our potential "
            "and attain success regardless of circumstances.",
            "The values we hold dear, the virtues we choose to cultivate, the positive habits we "
            "develop, all benefit us in checking the mental chaos created by negative qualities. "
            "Replace vice with virtue. Actively cultivate noble qualities and virtues to secure "
            "inner strength and peace of mind.",
            "Across history, people have been inspired by their difficulties to generate new and "
            "creative responses, that not only serve as a beacon to others but also become larger "
            "than themselves and benefit others even after they, as individuals, are gone.",
            "I wish you all a wonderful year of transcending limitations.",
        ],
        "close": ["Hari Om!", "Love", "At His feet", "Swami Swaroopananda"],
    },
    {
        "id": "director", "slug": "anukoolananda", "group": "today",
        "name": "Swami Anukoolanandaji", "short": "Swami Anukoolanandaji",
        "role": "Resident Director",
        "title": "Transcending Limitations", "open": [],
        "body": [
            "Gurudev said, &ldquo;Win the Mind; win the world&rdquo;. Mind alone is the cause for "
            "our successes and our failures. To train the mind to reap a heap of successes in our "
            "life is real education. A prominent business tycoon once said, &ldquo;The greatest "
            "opportunities lie in the greatest challenges&rdquo;.",
            "Limitations and obstacles look staggering only for those that are incapable of "
            "handling them. For the capable and the empowered, there are no obstacles or "
            "limitations to their progress. The greatest inventions, the brightest innovations and "
            "the deepest discoveries have happened on the face of seemingly insurmountable "
            "obstacles.",
            "With steely determination and exuberant creativity, let us all march forth zealously "
            "towards our castle of true success, fulfilling us and benefitting the world around us.",
        ],
        "close": ["Hari Om!", "Swami Anukoolananda"],
    },
    {
        "id": "academics", "slug": "krishnamurthy", "group": "today",
        "name": "Smt. Shanti Krishnamurthy", "short": "Smt. Shanti Krishnamurthy",
        "role": "Director &mdash; Academics &amp; Administration",
        "title": None, "open": ["Hari Om!"],
        "body": [
            "The latest and the most recent and serious concern today in Schools is DAS "
            "(Depression, Anxiety and Stress) among growing adolescents all over the world. "
            "Globally the reported rates of these mental disorders range up to an alarming 51%. "
            "The scene in India is slightly better than that of USA and Australia where one in "
            "five teenagers suffer from mental health problems. In a recent survey conducted in "
            "Chandigarh it was found that one out of 10 children are suffering from depression and "
            "it is higher among students of classes 10 and 12.",
            "One would wonder how did these disorders creep into our glorious system of education "
            "we had in the past? This erosion is not the result of recent trends. We are "
            "responsible for slowly injecting the poison of competition over years among children. "
            "Right after independence, though the British left India physically, they left behind "
            "the Industrial mind set. Like an Industry, where the raw materials go through "
            "grinding, cutting and welding, children became the raw materials and had to go "
            "through the pain of memorizing, reproducing and taking periodical examinations. At "
            "the end when the student emerges out of the system, he is tested through an yearend "
            "examination for uniformity and any deviation found in the end product, he gets "
            "rejected and becomes like a scrap in the society. Children get branded with marks "
            "when they emerge out of the Schools. Too much of uniformity has killed creativity "
            "among children. One common examination and one expected answer; all these "
            "successfully took away the joy in learning. Fine skills like art, music and dance are "
            "all neglected and given no importance. The system focused only on scores and "
            "encouraged only cut-throat competition among children. What else can be the outcome "
            "of such an unhealthy system? No wonder we have ended up creating mental disorders in "
            "children.",
            "We are fortunate in CIRS, that we have our Gurudev&rsquo;s vision which focusses on "
            "the holistic development of Children. When children study in a stress-free "
            "environment like ours, blossoming happens naturally. No wonder every child here gets "
            "the opportunity to unleash their own hidden potential.",
        ],
        "close": ["Best wishes,", "Shanti Krishnamurthy"],
    },
    {
        "id": "principal", "slug": "rajeshwari", "group": "today",
        "name": "Smt. G. Rajeshwari", "short": "Smt. G. Rajeshwari",
        "role": "Principal",
        "title": None, "open": ["Dear Parents and Children,", "Hari Om!"],
        "body": [
            "When we look at a storm, with its unstoppable immense power, we can only wonder at its "
            "might and force. Centred around a low pressure &ldquo;eye of the storm&rdquo; is a "
            "high pressure system of massive cloud and fierce wind, moving with great velocity, "
            "having a colossal force and enormous reach.",
            "When one observes this natural phenomena and study the complexity of its nature one "
            "can see that, higher the pressure in the eye of the storm, lower the intensity of the "
            "winds around it and the calmer the eye of the storm is, the more massive the power it "
            "has, in the winds around it.",
            "In the same way, the calmer we are in our mind just like the eye of the storm, the "
            "more power we will have to &ldquo;storm to perform&rdquo; in the world around us. For "
            "our mind to be calm, we must not get excited by the success nor be beaten down by the "
            "failure of life. For, these things are part and parcel of our lives. We must continue "
            "to look within for inner peace, train the mind to become calm and act to create a "
            "massive impact in this world. The eye of the storm, this inner peace, is the goal we "
            "need to seek in our lives.",
            "Let us &ldquo;Storm to Perform&rdquo;.",
        ],
        "close": ["With all wishes,", "Rajeshwari"],
    },
]

GROUPS = {"origin": "Founder &amp; Guruji", "today": "The school today"}


# ---------------------------------------------------------------------------
# Markup
# ---------------------------------------------------------------------------
def featured_html():
    """The four portraits that open the directory. Name, role and the link to
    the message are always shown: nothing waits on a hover."""
    items = []
    for i, p in enumerate(FEATURED):
        note = f'\n        <p class="ld-person__note">{p["note"]}</p>' if p["note"] else ""
        items.append(f'''    <li class="ld-person" style="--i:{i}">
      <figure class="ld-person__frame">
        {img(p["slug"], "", "(min-width: 1100px) 23vw, (min-width: 640px) 45vw, 88vw", eager=True)}
      </figure>
      <div class="ld-person__text">
        <p class="ld-person__role">{p["role"]}</p>
        <h3 class="ld-person__name">{p["name"]}</h3>{note}
        <a class="ld-person__link" href="#msg-{p["msg"]}" data-ld-msg="{p["msg"]}">Read message<span class="sr-only"> from {p["name"]}</span></a>
      </div>
    </li>''')
    return '<ul class="ld-four">\n' + "\n".join(items) + "\n  </ul>"


def directors_html():
    """One ruled row each: who, what, and — at the row's end — a portrait.
    A person with no approved photograph has a row that simply ends after
    the text: not a silhouette, not an empty frame, not somebody else."""
    items = []
    for p in DIRECTORS:
        face = (f'\n      <figure class="ld-dir__face">{img(p["slug"], "", "96px")}</figure>'
                if p["slug"] else "")
        cls = "ld-dir" if p["slug"] else "ld-dir ld-dir--text"
        items.append(f'''    <li class="{cls}">
      <div class="ld-dir__id">
        <p class="ld-person__role">{p["role"]}</p>
        <h3 class="ld-dir__name">{p["name"]}</h3>
      </div>
      <p class="ld-dir__note">{p["note"]}</p>{face}
    </li>''')
    return '<ul class="ld-dirs">\n' + "\n".join(items) + "\n  </ul>"


def _lines(lines, cls):
    return "".join(f'\n            <p class="{cls}">{l}</p>' for l in lines)


def reader_html():
    """The index (a tab list from 900px, a labelled select below it) and
    every message in full. With no script, every message is in the page,
    one after another, and the index is hidden: the anchors still land."""
    tabs, options, panels = [], [], []
    group = None
    for i, m in enumerate(MESSAGES):
        on = i == 0
        if m["group"] != group:
            group = m["group"]
            tabs.append(f'        <span class="ld-idx__group" aria-hidden="true">{GROUPS[group]}</span>')
            if options:
                options.append("          </optgroup>")
            options.append(f'          <optgroup label="{GROUPS[group]}">')
        tabs.append(f'''        <button type="button" class="ld-idx__tab" role="tab" id="msg-tab-{m["id"]}"
                aria-controls="msg-{m["id"]}" aria-selected="{"true" if on else "false"}"{"" if on else ' tabindex="-1"'}>
          <span class="ld-idx__name">{m["short"]}</span>
          <span class="ld-idx__role">{m["role"]}</span>
        </button>''')
        options.append(f'            <option value="{m["id"]}" data-role="{m["role"]}">{m["short"]}</option>')
        title = f'\n            <p class="ld-msg__title">{m["title"]}</p>' if m["title"] else ""
        body = "".join(f"\n            <p>{p}</p>" for p in m["body"])
        kind = ("The Founder&rsquo;s message" if m["id"] == "founder"
                else "Pujya Guruji&rsquo;s message" if m["id"] == "guruji"
                else f'Message from the {m["role"]}')
        panels.append(f'''      <article class="ld-msg" id="msg-{m["id"]}" role="tabpanel" aria-labelledby="msg-name-{m["id"]}" tabindex="-1">
        <header class="ld-msg__head">
          <figure class="ld-msg__face">{img(m["slug"], "", "(min-width: 1100px) 220px, 112px")}</figure>
          <div class="ld-msg__who">
            <p class="ld-msg__kind">{kind}</p>
            <h3 class="ld-msg__name" id="msg-name-{m["id"]}">{m["name"]}</h3>
            <p class="ld-msg__role">{m["role"]}</p>
          </div>
        </header>
        <div class="ld-msg__text">{title}{_lines(m["open"], "ld-msg__greet")}{body}{_lines(m["close"], "ld-msg__sign")}
        </div>
      </article>''')
    options.append("          </optgroup>")
    return f'''<div class="ld-reader" data-ld-reader>
    <div class="ld-idx">
      <div class="ld-idx__tabs" role="tablist" aria-label="Messages" aria-orientation="vertical">
{chr(10).join(tabs)}
      </div>
      <div class="ld-idx__pick">
        <label class="ld-idx__label" for="ld-pick">Choose a message</label>
        <div class="ld-idx__bar">
          <select class="ld-idx__select" id="ld-pick" aria-describedby="ld-pick-role">
{chr(10).join(options)}
          </select>
          <p class="ld-idx__now" id="ld-pick-role">{MESSAGES[0]["role"]}</p>
        </div>
      </div>
    </div>
    <div class="ld-sheet">
{chr(10).join(panels)}
    </div>
  </div>'''


def expand(html):
    return (html.replace("{{LEAD_FEATURED}}", featured_html())
                .replace("{{LEAD_DIRECTORS}}", directors_html())
                .replace("{{LEAD_READER}}", reader_html())
                .replace("{{LEAD_STAFF}}", staff_html()))


def head_script():
    """Before first paint: say which message the URL asks for, so the reader
    opens on it rather than showing all six and then collapsing. The index
    shows only under html.ld-js (leadership.css). Deferred scripts have all
    run by DOMContentLoaded, so if leadership.js has not, the class comes off
    and every message is shown again."""
    ids = ",".join(f'"{m["id"]}"' for m in MESSAGES)
    return ('<script>\n(function(){var ids=[' + ids + '],h=location.hash.replace(/^#msg-/,""),'
            'd=document.documentElement;d.classList.add("ld-js");'
            'd.setAttribute("data-ld-msg",ids.indexOf(h)>-1?h:ids[0]);'
            'document.addEventListener("DOMContentLoaded",function(){'
            'if(!window.__ldBooted)d.classList.remove("ld-js");});})();\n</script>\n')


def head_css():
    """The companion of head_script: only the chosen message shows."""
    # Hides the others rather than showing the one, so the panel keeps the
    # display leadership.css gives it.
    rules = ",".join(f'html.ld-js[data-ld-msg="{m["id"]}"] .ld-msg:not(#msg-{m["id"]})'
                     for m in MESSAGES)
    return f"<style>{rules}{{display:none}}</style>\n"
