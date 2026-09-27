"""Current CIRS house identities and dated school records.

Approved current descriptions were supplied by the school. House names and
colours, verified photography and those descriptions are the identity model.
Historical RESULTS and SYMPOSIUMS preserve dated newsletter evidence only.
Stable vasishtha URL fragments retain incoming links; visible name is Vasishta.
The unrelated legacy Sports presentation lives in sports_house_history.py.
"""

HOUSES = [
    dict(slug='vasishtha', name='Vasishta', colour='Red', number='01'),
    dict(slug='valmiki', name='Valmiki', colour='Yellow', number='02'),
    dict(slug='vishwamitra', name='Vishwamitra', colour='Green', number='03'),
    dict(slug='vyasa', name='Vyasa', colour='Blue', number='04'),
]

# ---------------------------------------------------------------------------
# The inter-house record, as the school published it.
#
# Each row is one dated event from the available school material. Where the
# source gives placements or named awards, those are reproduced. Nothing is
# aggregated into a championship table: these sources do not include a
# complete points total, and a total made from selected results would be
# presented as something the school did not publish here.
#
#   when      the date as the source gives it, no more precisely
#   event     the event's own name
#   category  the strip the competition track groups it under
#   order     the four houses, first to fourth, by slug
#   awards    (award, [slugs]) where the event was judged, not ranked
#   source    which file in pdf/ this row is read from
# ---------------------------------------------------------------------------
RESULTS = [
    {
        # The report names it "our 12th Annual Athletic and Aquatic Meet", and
        # describes the aquatic meet running inside Khel Mela on the same day
        # as the track and field events. The preview in the February issue
        # calls the same event the 12th Annual Athletic Meet; the report's
        # fuller name is the one used here.
        "when": "February 2008",
        "event": "Khel Mela &mdash; the 12th Annual Athletic and Aquatic Meet",
        "category": "Sport",
        "order": None,
        "awards": [("Overall championship", ["valmiki"]),
                   ("Best march past", ["valmiki"]),
                   ("Best individual activities", ["vasishtha", "vishwamitra"]),
                   ("Best drill", ["vyasa"])],
        "source": "Sakshi, March 2008",
        # The source disagrees with itself here, and the page says so rather
        # than choosing quietly. Its list of winners reads "Best Drill - Vyasa
        # House"; three paragraphs earlier its own account of the drill
        # competition says the cup went to "these houses (Vasishtha and Vyasa
        # house)". The list is what is reproduced above, because it is the
        # formal list of winners — but a reader is entitled to know the issue
        # printed both.
        "note": "The same issue reports the best drill cup two ways: its list of winners "
                "names Vyasa alone, while its account of the drill competition says the "
                "cup went to Vasishtha and Vyasa together. The list is what is shown here.",
    },
    {
        "when": "30 April 2008",
        "event": "Senior Social Science Quiz",
        "category": "Quizzing",
        "order": ["valmiki", "vasishtha", "vyasa", "vishwamitra"],
        "awards": None,
        "source": "Sakshi, summer special, May 2008",
    },
    {
        "when": "May 2008",
        "event": "The house symposiums",
        "category": "Culture",
        "order": None,
        "awards": None,
        "source": "Sakshi, summer special, May 2008",
        "note": "Four productions, one from each house, and the only house event in "
                "these sources that was staged rather than scored. The titles are "
                "under <a href=\"#culture\">Where each house tells a story</a>.",
    },
    {
        "when": "22 October 2008",
        "event": "English Quiz, junior school",
        "category": "Quizzing",
        "order": ["vishwamitra", "valmiki", "vyasa", "vasishtha"],
        "awards": None,
        "source": "CIRS e-newsletter, October&ndash;November 2008",
        "note": "Vishwamitra and Valmiki tied, and three further rounds were needed "
                "to separate them.",
    },
    {
        "when": "5 November 2008",
        "event": "Mathematics Quiz, junior school",
        "category": "Quizzing",
        "order": ["vasishtha", "vishwamitra", "vyasa", "valmiki"],
        "awards": None,
        "source": "CIRS e-newsletter, October&ndash;November 2008",
    },
    {
        "when": "19 November 2008",
        "event": "Junior Science Quiz",
        "category": "Quizzing",
        "order": ["vyasa", "valmiki", "vishwamitra", "vasishtha"],
        "awards": None,
        "source": "CIRS e-newsletter, October&ndash;November 2008",
    },
    {
        "when": "23&ndash;24 November 2008",
        "event": "Inter-House Aquatic Meet",
        "category": "Sport",
        "order": ["vishwamitra", "valmiki", "vyasa", "vasishtha"],
        "awards": None,
        "source": "CIRS e-newsletter, October&ndash;November 2008",
    },
    {
        "when": "2025&ndash;2026",
        "event": "Khel Mela &mdash; the 29th Annual Aquatic Meet",
        "category": "Sport",
        "order": None,
        "awards": None,
        "source": "the meet&rsquo;s own medal ribbons",
        "note": "A photographed ribbon names this as the 29th Annual Aquatic Meet; "
                "this repository does not contain its house placings.",
    },
]

# The four house productions of May 2008, with their titles as Sakshi printed
# them and the school's own one-line account of each. The culture chapter is
# built from this. No other production is named anywhere in this repository,
# and none is added here.
SYMPOSIUMS = [
    ("valmiki", "The Twilight of the Gods",
     "How past lives and experiences can shape us as individuals."),
    ("vasishtha", "The Butterfly Effect",
     "In life we do not usually get second chances, so we should make the best of "
     "the only opportunity we get."),
    ("vishwamitra", "V for Vendetta",
     "Nothing in life is trivial enough to be underestimated."),
    ("vyasa", "The Breakthrough",
     "When power and money are at stake, people forget more important relationships."),
]

# The competition categories the sources actually support, and nothing beyond
# them. Debates, arts, service and academic contests happen at CIRS and are on
# other pages of this site, but no source here places the four houses in one,
# so they are not offered as filters.
CATEGORIES = ["All", "Sport", "Quizzing", "Culture"]

DIR = "assets/img/houses"


def by_slug():
    return {h["slug"]: h for h in HOUSES}


def name_of(slug):
    return by_slug()[slug]["name"]


def colour_of(slug):
    return by_slug()[slug]["colour"]


def img(name):
    return f"{DIR}/{name}"


# Current identity copy supplied by the school in the redesign brief.
# Current identities have no historical identity fields.
# Stable slugs intentionally preserve existing incoming URLs.
APPROVED_DESCRIPTIONS = {'Vasishta': 'The blazing untamed red of the fire runs through each member of this house. They strive for perfection with every heartbeat. Like fire they engulf fear, doubt, hatred and anger, pushing aside every obstacle in their way. They march forward with red in their veins and the spirit of remaining undaunted. Like the great Sage Vasishta they remain steadfast to their duties and possess wisdom that guides their fierce battles.', 'Valmiki': 'The Valmiki house stands tall, rooted in values and tenacity. With every failure, they gain experience and learning, serving as a stepping stone to success. The colour yellow represents their optimistic approach to every adversity and their journey to emerge victorious. Bound by ideals, they walk the trail of Sage Valmiki, writing their own epic of resilience, valour and growth.', 'Vishwamitra': 'The Vishwamitra house is testimony to the journey of growth and self control. Similar to the green, deep forests they do not fear storms. Their roots extend miles beyond one can see. They charge ahead with the unstoppable force of nature and refuse to wilt. They inherit the spirit of Sage Vishwamitra, shaping their own destiny. They are the commanders of tomorrow.', 'Vyasa': 'The deep, infinite blue shapes the soul of this house. They don’t merely compete, rather they strive for excellence in every breath. The boundless blue sky serves as their reminder to surpass limits and break barriers while carrying energy and enthusiasm in every stride. They are the torch bearers of the timeless legacy of Sage Vyasa, displaying absolute focus and unshakable composure.'}

PAGE_HOUSES = [
    dict(h, name="Vasishta" if h["slug"] == "vasishtha" else h["name"],
         description=APPROVED_DESCRIPTIONS["Vasishta" if h["slug"] == "vasishtha" else h["name"]],
         hero="identity-" + h["slug"] + ".jpg",
         frame="spread-" + h["slug"] + ".jpg")
    for h in HOUSES
]
PAGE_MEDIA = {
    "vasishtha": ("Vasishta basketball players in red shirts bearing the house name", "In red, on the court", "A Vasishta student climbing a wall, the house name visible on the red shirt", "Finding the next foothold"),
    "valmiki": ("Valmiki players gathered in yellow shirts with the house name across their backs", "A moment with the team", "Valmiki players passing a basketball, with the house name visible on yellow shirts", "Moving the ball together"),
    "vishwamitra": ("Vishwamitra students gathered on the basketball court, their house name visible across green shirts", "Together on the basketball court", "Vishwamitra basketball players huddling in green shirts bearing the house name", "Gathering before the game"),
    "vyasa": ("Vyasa players gathered courtside, with the house name on a blue shirt", "The blue of belonging", "Vyasa players in a basketball huddle, their house name visible on blue shirts", "Coming together on court"),
}
for h in PAGE_HOUSES:
    h["hero_alt"], h["hero_cap"], h["frame_alt"], h["frame_cap"] = PAGE_MEDIA[h["slug"]]


def current_name(slug):
    return next(h["name"] for h in PAGE_HOUSES if h["slug"] == slug)

# Page renderers: complete HTML is readable before progressive enhancement.
from html import escape as _escape


def photo_html(path, alt, width=1600, height=1100, eager=False):
    responsive = ''
    if path.startswith('assets/img/houses/') and path.rsplit('/',1)[-1].startswith(('spread-', 'gallery-', 'march-formation', 'march-procession')):
        responsive = f' srcset="{path.replace(".jpg","-800.jpg")} 800w, {path} 1600w" sizes="(max-width: 900px) 100vw, 58vw"'
    return (f'<img src="{path}" width="{width}" height="{height}"{responsive} '
            f'alt="{_escape(alt, quote=True)}" decoding="async" '
            + ('fetchpriority="high"' if eager else 'loading="lazy"') + '>')


def hero_html():
    out = []
    for h in PAGE_HOUSES:
        out.append(f'''<a class="house-zone" href="#house-{h['slug']}" data-house="{h['slug']}" aria-label="Explore {h['name']}, {h['colour']} house">
  <img src="{img(h['hero'])}" srcset="{img(h['hero'].replace('.jpg','-720.jpg'))} 720w, {img(h['hero'])} 1440w, {img(h['hero'].replace('.jpg','-1800.jpg'))} 1800w" sizes="(max-width: 430px) 100vw, (max-width: 900px) 50vw, 44vw" width="1440" height="2016" alt="{_escape(h['hero_alt'])}" decoding="async"{' fetchpriority="high"' if h['number']=='01' else ''}>
  <span class="house-zone__number" aria-hidden="true">{h['number']}</span>
  <span class="house-zone__label"><span class="house-zone__name">{h['name']}</span><span class="house-zone__colour">{h['colour']}<span class="house-zone__explore" aria-hidden="true"><small>Explore</small> ↗</span></span></span>
</a>''')
    return '\n'.join(out)


def chapters_html():
    out = []
    for i, h in enumerate(PAGE_HOUSES):
        path = img(h['frame'])
        alt, cap = h['frame_alt'], h['frame_cap']
        sentences = h['description'].split('. ')
        cut = 2
        blocks = '. '.join(sentences[:cut]) + '. </span><span class="house-copy-block">' + '. '.join(sentences[cut:])
        previous = PAGE_HOUSES[i-1]['slug'] if i else 'vasishtha'
        out.append(f'''<article class="house-spread" id="house-{h['slug']}" data-house="{h['slug']}" aria-labelledby="name-{h['slug']}">
  <div class="house-wipe" aria-hidden="true"><span class="house-wipe__out" data-house="{previous}"></span><span class="house-wipe__in"></span></div>
  <span class="house-spread__ghost" aria-hidden="true">{h['name']}</span>
  <header class="house-spread__heading"><p class="house-spread__index">{h['number']} <span>/ 04</span></p><h2 id="name-{h['slug']}"><span>{h['name']}</span></h2><p class="house-spread__colour">{h['colour']}</p></header>
  <span class="house-signature-line" aria-hidden="true"></span>
  <div class="house-spread__body"><figure>{photo_html(path, alt)}<figcaption>{cap}</figcaption></figure>
  <div class="house-spread__copy"><p><span class="house-copy-block">{blocks}</span></p><a href="#gallery-{h['slug']}">View {h['name']} photographs <span aria-hidden="true">↗</span></a></div></div>
</article>''')
    return '\n'.join(out)


STAGES = [
    dict(id='march', label='March', title='March past.', image='assets/img/houses/march-formation.jpg',
         alt='CIRS cadets standing in formation on the campus grounds', caption='CIRS cadets in formation',
         copy='The march past brings discipline and collective effort into view. Step, rhythm and formation turn individual practice into a shared performance.',
         record='February 2008 · Khel Mela: Valmiki received the best march past award.', archive=0),
    dict(id='sport', label='Sport', title='On the court.', image='assets/img/houses/sport-tennis.jpg',
         alt='Students practising tennis, with Vyasa and Vasishta named on their blue and red shirts', caption='House colours together on the tennis court',
         copy='From the court to the pool, the house gives individual effort a team to belong to. Competition and the everyday work of practice share the same ground.',
         record='2025–26 · Khel Mela: the medal ribbons identify the 29th Annual Aquatic Meet.', archive=7),
    dict(id='quizzing', label='Quizzing', title='At the quiz table.', image='assets/img/houses/comp-quiz.jpg',
         alt='CIRS students discussing a quiz answer at a table, one student holding a microphone', caption='A school quiz in progress',
         copy='A question, a quick exchange, a shared answer. The quiz table gives teamwork another form, with listening and judgement as important as recall.',
         record='30 April 2008 · Valmiki won the Senior Social Science Quiz.', archive=1),
    dict(id='culture', label='Culture', title='On stage.', image='assets/img/theatre/vishwamitra25-courtyard-1600.webp',
         alt='Vishwamitra performers in a courtyard scene from El Diablo', caption='Vishwamitra · El Diablo · Masquerade 2025',
         copy='On stage, a house becomes a company. The 2025 Masquerade photographs record Melora, Vantara, El Diablo and Ivysherin: four productions made by four houses.',
         record='May 2008 · The house symposiums: four earlier productions recorded in Sakshi.', archive=2),
]


def stage_html():
    tabs = '\n'.join(f'<button type="button" id="tab-{s["id"]}" data-stage-tab="{s["id"]}" aria-controls="{s["id"]}">{s["label"]}</button>' for s in STAGES)
    panels = []
    participants = '<ul class="house-participants" aria-label="The four houses">' + ''.join(f'<li data-house="{h["slug"]}"><span aria-hidden="true"></span>{h["name"]}</li>' for h in PAGE_HOUSES) + '</ul>'
    for s in STAGES:
        link = '<a class="house-stage__link" href="sports.html">Explore CIRS sports →</a>' if s['id']=='sport' else ('<a class="house-stage__link" href="theatre.html#masquerades">Explore CIRS Theatre →</a>' if s['id']=='culture' else '')
        media = march_html() if s['id'] == 'march' else f'<figure>{photo_html(s["image"],s["alt"])}<figcaption>{s["caption"]}</figcaption></figure>'
        panels.append(f'''<section class="house-stage" id="{s['id']}" data-stage-panel aria-labelledby="stage-heading-{s['id']}">
<div class="house-stage__media">{media}</div>
<div class="house-stage__copy"><h3 id="stage-heading-{s['id']}">{s['title']}</h3><p>{s['copy']}</p>{participants}
<p class="house-stage__record">{s['record']} <a href="#event-{s['archive']}">Read archive entry</a></p>{link}</div></section>''')
    return '<div class="house-stage-tabs" data-stage-tabs aria-label="Explore house activities" hidden>'+tabs+'</div>\n'+'<div class="house-stage-stack">'+'\n'.join(panels)+'</div>'


SOURCE_LINKS = {
    'Sakshi, March 2008': 'pdf/Sakshi Newleter March 2008.pdf',
    'Sakshi, summer special, May 2008': 'pdf/Sakshi Newleter summer special May 2008.pdf',
    'CIRS e-newsletter, October&ndash;November 2008': 'pdf/E-Newletter Octnov08.pdf',
    'the meet&rsquo;s own medal ribbons': 'assets/img/houses/sport-medals.jpg',
}


def archive_html():
    rows = []
    for i, r in enumerate(RESULTS):
        details = []
        if r['order']:
            details.append('<ol class="house-placings">'+''.join(f'<li>{current_name(s)}</li>' for s in r['order'])+'</ol>')
        if r['awards']:
            details.append('<ul>'+''.join(f'<li>{award}: {", ".join(current_name(s) for s in slugs)}</li>' for award,slugs in r['awards'])+'</ul>')
        if i == 0:
            # Preserve the original spelling when quoting the conflicting source.
            details.append('<p>The winners’ list names Vyasa for best drill. The same issue’s account credits “Vasishtha and Vyasa house”. Both readings are preserved here.</p>')
        if i == 2:
            details.append('<p>2008 archive · House symposiums</p><ul>'+''.join(f'<li>{current_name(slug)} — <cite>{title}</cite></li>' for slug,title,_ in SYMPOSIUMS)+'</ul>')
        if i == 3:
            details.append('<p>Vishwamitra and Valmiki were tied before three further rounds decided the result.</p>')
        if i == 7:
            details.append('<p>The medal ribbons read “XXIX Annual Aquatic Meet” and “Khel Mela 2025–2026”.</p>')
        source = SOURCE_LINKS[r['source']].replace(' ','%20')
        details.append(f'<p class="house-archive__source">Source: <a href="{source}">{r["source"]}</a></p>')
        rows.append(f'''<li><details id="event-{i}"><summary><span class="house-archive__date">{r['when']}</span><span>{r['event']}</span><span class="house-archive__plus" aria-hidden="true">+</span></summary><div class="house-archive__detail">{''.join(details)}</div></details></li>''')
    return '<ol class="house-archive__list">'+''.join(rows)+'</ol>'


GALLERY_THEATRE = {
    'vasishtha': ('vasistha25-company-1600.webp', 'Vasishta performers gathered after Vantara', 'The company after Vantara · 2025'),
    'valmiki': ('valmiki25-after-1600.webp', 'Two Valmiki performers after Melora, one in body paint and one in a red coat', 'After Melora · 2025'),
    'vishwamitra': ('vishwamitra25-guitar-1600.webp', 'Vishwamitra performers at a guitar stall on the El Diablo stage', 'A scene from El Diablo · 2025'),
    'vyasa': ('vyasa25-make-up-1600.webp', 'A Vyasa student applying stage make-up for Ivysherin', 'Backstage at Ivysherin · 2025'),
}


GALLERY_SPORT = {
    'vasishtha': ('Vasishta players gathered on the basketball court in named red shirts', 'Together on court'),
    'valmiki': ('Valmiki players raising their hands together in named yellow shirts', 'Hands together before play'),
    'vishwamitra': ('Vishwamitra students talking beside the court, with house lettering visible on green shirts', 'Beside the court'),
    'vyasa': ('Vyasa players talking courtside in named blue shirts', 'In the team circle'),
}


def gallery_html():
    buttons = '<button type="button" data-house-filter="all" aria-pressed="true">All</button>'
    buttons += ''.join(f'<button type="button" data-house-filter="{h["slug"]}" aria-pressed="false">{h["name"]}</button>' for h in PAGE_HOUSES)
    frames = []
    for h in PAGE_HOUSES:
        name,alt,cap = GALLERY_THEATRE[h['slug']]
        for j,(path,a,c) in enumerate([(img('gallery-'+h['slug']+'.jpg'), *GALLERY_SPORT[h['slug']]), ('assets/img/theatre/'+name,alt,cap)]):
            anchor = f' id="gallery-{h["slug"]}"' if j==0 else ''
            frames.append(f'<li{anchor} data-gallery-house="{h["slug"]}" data-house="{h["slug"]}"><figure>{photo_html(path,a,1600,1100)}<figcaption><b>{h["name"]}</b><span>{c}</span></figcaption></figure></li>')
    return f'<div class="house-gallery__filters" role="group" aria-label="Filter photographs by house" hidden>{buttons}</div><p class="house-gallery__status" role="status" aria-live="polite">8 photographs · Scroll or swipe to explore</p><ul class="house-gallery__strip" tabindex="0" aria-label="House photographs">'+''.join(frames)+'</ul>'


def march_html():
    photos = [
        ('march-formation.jpg', 'CIRS cadets in formation', 'CIRS cadets standing in formation on the campus grounds'),
        ('march-procession.jpg', 'Students walking in formation', 'CIRS students walking in two rows, led by a student wearing a School Dean sash'),
    ]
    frames = ''.join(f'<figure>{photo_html(img(path),alt,1600,1100)}<figcaption>{caption}</figcaption></figure>' for path,caption,alt in photos)
    return '<div class="house-march"><section class="house-march__viewport" tabindex="0" aria-label="March photographs. Swipe or use arrow keys to explore."><div class="house-march__track">'+frames+'</div></section><p class="house-march__cue">Two views of the school parade <span aria-hidden="true">↔</span></p></div>'
