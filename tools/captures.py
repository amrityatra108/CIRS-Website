"""CIRS Captures — an eighty-two-photograph journal from the supplied collections.

The first sixteen photographs are in assets/source/captures-2026-09-24. The
new ZIP has 43 photographs and one blank frame; nine repeat photographs in
the first collection. Its 34 new photographs are in
assets/source/captures-2026-09-24-zip. The later Drive file and folder add
twelve more photographs in assets/source/captures-2026-09-25 and
assets/source/captures-2026-09-25-folder. The attachment's berry bird and a
folder copy of the lizard are shown once. A later folder update adds 21
photographs; repeated copies, a near-identical kingfisher frame and a second
frame of the same kittens are omitted. Every selected photograph appears once: four in the opening,
77 in the journal, and one at the end.

Captions describe what is visible; photographer, date, and exact location are
not inferred. tools/make-captures-gallery.py writes the image sizes used by
the site build. tools/make-captures-shot.py cuts the opening photograph.
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "captures-gallery.json")

OLD = "captures-2026-09-24"
ZIP = "captures-2026-09-24-zip"
ADDITIONS = "captures-2026-09-25"
FOLDER = "captures-2026-09-25-folder"


def old(name):
    return f"{OLD}/{name}.jpg"


def new(number):
    return f"{ZIP}/{number:02d}.jpg"


def added(name):
    return f"{ADDITIONS}/{name}"


def folder(name):
    return f"{FOLDER}/{name}"


# (source file in assets/source, output name, caption, width of the cut)
# The lead is the first frame after the camera's full-screen dissolve.
LEAD_SOURCE = new(1)
LEAD_CAPTION = "A black and white butterfly resting in sunlit grass"
FEATURED = [
    (new(13), "companion", "Silhouetted stems against a vivid orange sunset", 1800),
    (new(14), "portrait", "A quiet path beneath tall trees", 1200),
    (new(6), "wide", "An overhead view of buildings surrounded by trees", 2400),
]

# Each chapter is a set of justified rows. The large first row of every
# chapter sets its pace; the following pairs and trios keep every photograph
# at its own aspect ratio. The viewer uses this same reading order.
CHAPTERS = [
    {
        "slug": "small-worlds", "title": "Small worlds",
        "intro": "Flowers, insects and the creatures that appear when the camera moves closer.",
        "rows": [
            [(added("dsc09358.jpg"), "lizard-tree-trunk", "A golden lizard climbing a tree trunk")],
            [(old("img-9821"), "bee-yellow-flower", "A bee on a vivid yellow flower"),
             (old("dsc02269"), "butterfly-flowers", "A black and yellow butterfly on pale purple flowers"),
             (new(4), "green-insect", "An iridescent green insect on a leafy branch")],
            [(folder("05-crs05364-2-.jpg"), "red-flower-sky", "A red flower silhouetted against the sky"),
             (folder("06-dsc08037.jpg"), "butterfly-white-flowers", "A butterfly on slender white flowers")],
            [(folder("14-dsc05087.jpg"), "yellow-butterfly-orange-flower", "A yellow butterfly on an orange flower"),
             (folder("15-dsc02280.jpg"), "butterfly-red-flowers", "A butterfly approaching red flowers")],
            [(new(5), "grasshopper-stem", "A grasshopper resting along a slender stem"),
             (new(15), "insect-on-stem", "A small insect clinging to a stem against green"),
             (new(26), "grasshopper-leaf", "A grasshopper on a broad green leaf")],
            [(old("img-2031"), "green-lizard", "A green lizard partly hidden beneath leaves"),
             (new(43), "red-dragonfly", "A red dragonfly resting on a thin stem")],
            [(folder("07-img-1447.jpg"), "green-lizard-grass", "A green lizard in the grass"),
             (folder("08-img-1307.jpg"), "insects-in-flight", "Two insects hovering together in warm light")],
            [(new(7), "squirrel-hollow", "A squirrel peeking out from a tree hollow"),
             (new(35), "bird-in-nest", "A dark bird in a nest among bright leaves")],
            [(folder("09--dsc0735.jpg"), "butterflies-leaves", "Several butterflies gathering on a leafy stem"),
             (folder("10--dsc0733.jpg"), "blue-butterfly-flowers", "A blue and black butterfly on small flowers")],
            # Two frames of the same kittens on the same ledge were one
            # photograph twice; the sharper, single-kitten frame closes the
            # chapter alongside the pair it used to follow.
            [(new(30), "blue-bird-flowers", "A blue bird beside pale flowers"),
             (new(42), "yellow-eyed-bird", "A yellow-eyed bird among branches"),
             (folder("03-dsc-0086.jpg"), "kitten-shelter", "A kitten looking out from a sheltered ledge")],
        ],
    },
    {
        "slug": "among-the-trees", "title": "Among the trees",
        "intro": "Perches, branches and the birds glimpsed between leaves.",
        "rows": [
            [(old("img-1007"), "bird-pink-blossoms", "A small dark bird amid pink blossoms")],
            [(folder("11-dsc09803.jpg"), "bird-orange-berries", "A small bird perched among orange berries"),
             (old("img-9515"), "hoopoe-branches", "A hoopoe perched among branches"),
             (new(2), "brown-bird-branch", "A brown bird on a bare branch against the sky")],
            [(folder("16-dsc08899.jpg"), "yellow-bird-branches", "A yellow-bellied bird perched among branches"),
             (folder("20-dsc07082.jpg"), "black-white-bird-branch", "A black and white bird on a bare branch")],
            [(new(3), "bird-in-large-tree", "A bird perched in the limbs of a broad tree"),
             (new(8), "bird-dense-leaves", "A small bird partly hidden in dense foliage")],
            [(old("dsc00453"), "bird-among-leaves", "A red-crested bird among broad green leaves"),
             (old("img-1396"), "bird-white-blossoms", "A small bird reaching into white blossoms")],
            [(folder("21-img-9878.jpg"), "bird-on-post", "A small bird perched on a post against green"),
             (folder("25-copy-of-dsc09801.jpg"), "green-bird-wire", "A small green bird perched on a wire")],
            [(old("img-1887"), "squirrel-branch", "A squirrel perched on a branch against blue sky"),
             (folder("33-copy-of-dsc00202.jpg"), "squirrel-dark-tree", "A squirrel clinging to a tree in shade")],
            [(old("img-4491"), "kingfisher-post", "A kingfisher perched on a post with trees behind"),
             (new(10), "kingfisher-trunk", "A kingfisher against the dark bark of a tree")],
            [(folder("27-copy-of-indian-silverbill.jpg"), "pale-bird-wire", "A small pale bird perched on a wire at dusk"),
             (folder("29-copy-of-copy-of-cb35bf1a-94be-4427-8c9d-9097f40fdfc9-l0-001-1-6-2024-7-08-57-pm.jpg"), "brown-bird-wire", "A small brown bird on a wire among bare branches")],
            [(old("img-4562"), "dove-branches", "A dove perched among yellow flowers and branches"),
             (old("img-2030"), "bird-dark", "A small pale-headed bird against a dark background"),
             (folder("30-copy-of-dsc-0047-1.jpg"), "green-bird-branches", "A small green bird among branches")],
            [(old("img-5244"), "bird-in-shade", "A bird on a branch in deep shade"),
             (old("img-5569"), "bird-bare-branches", "A small red-crowned bird among bare branches")],
        ],
    },
    {
        "slug": "by-the-water", "title": "By the water",
        "intro": "Reeds, reflections and the birds that gather at the edge.",
        "rows": [
            [(folder("12-dsc09967.jpg"), "sunset-water", "The sun setting over water and distant birds")],
            [(folder("13-dsc09853.jpg"), "waterbird-reeds", "A colorful waterbird among tall reeds"),
             (folder("26-copy-of-dsc09849.jpg"), "waterbird-reeds-flight", "A colorful waterbird lifting from the reeds")],
            [(folder("24-copy-of-dsc05149.jpg"), "heron-water", "A long-necked bird perched above green water"),
             (old("kingfisher"), "kingfisher-water", "A kingfisher by the water, framed by tree trunks")],
            [(folder("31-copy-of-dsc00046.jpg"), "birds-on-water", "A flock of birds moving across the water")],
        ],
    },
    {
        "slug": "sky-and-shade", "title": "Sky and shade",
        "intro": "Open perches, distant light and moments just outside the canopy.",
        "rows": [
            [(new(9), "raptor-stump", "A bird of prey perched on a weathered stump")],
            [(folder("01-img-0111.jpg"), "peacock-fan", "A peacock displaying its tail in a grassy clearing"),
             (new(12), "pale-bird-perch", "A pale bird on a thin bare branch")],
            # The kingfisher arrived as a square photograph on a 16:9 black
            # canvas; CROPS below takes the photograph and leaves the canvas.
            [(new(11), "colorful-bird", "A colorful bird perched among sunlit leaves"),
             (folder("02-a-03-2.jpg"), "full-moon", "A bright full moon against a black sky"),
             (folder("28-copy-of-1untitled-design.png"), "kingfisher-blue-study", "A close view of a kingfisher against blue")],
            [(old("img-4426"), "grey-bird", "A small grey bird seen through soft green foliage"),
             (new(28), "bird-on-roof", "A small bird perched on roof tiles")],
            [(new(16), "trees-at-dusk", "Trees framing an open field in evening light"),
             (new(29), "peacock-shade", "A peacock among dark leaves")],
            [(new(31), "brown-bird-branches", "A brown bird perched among crossing branches"),
             (new(32), "black-white-bird", "A black and white bird with a long tail in green foliage")],
            [(folder("34-copy-of-dsc00628.jpg"), "birds-on-wire", "Two birds perched on a wire against blue sky"),
             (folder("35-copy-of-dsc03869.jpg"), "green-birds-branches", "Two green birds on a bare branch against the sky")],
            [(new(36), "grey-blue-bird", "A grey-blue bird perched on a branch"),
             (new(38), "yellow-bird-sky", "A small yellow bird against blue sky"),
             (new(39), "bird-silhouette", "A bird silhouetted against a pale sky")],
        ],
    },
    {
        "slug": "together", "title": "Together",
        "intro": "Performances, gatherings and people in the collection.",
        "rows": [
            [(new(20), "people-seated-together", "People seated together on the floor")],
            [(new(17), "decorated-stage", "Flowers and artwork on a decorated stage"),
             (new(18), "performer-blue-light", "A performer under blue stage lights"),
             (folder("18-dsc02905.jpg"), "two-dancers", "Two performers dancing in colorful dress")],
            [(folder("17-edit-man.jpg"), "man-seated", "A man seated alone in a light corridor"),
             (folder("19-dsc00372.jpg"), "children-window", "Children looking out of a window")],
            [(new(19), "seated-performer", "A performer seated on stage"),
             (new(21), "singer-spotlight", "A singer holding a microphone on a dark stage"),
             (new(22), "group-outdoors", "A group gathered outdoors with flower garlands")],
        ],
    },
]

# The image builder works over the same flattened rows as the page.
ROWS = [row for chapter in CHAPTERS for row in chapter["rows"]]

# Output name -> (left, top, right, bottom) box in source pixels, for a source
# that carries more than the photograph. Only an empty surround is cut away.
CROPS = {
    "kingfisher-blue-study": (0, 0, 1080, 1080),
}

# The ending: one photograph, kept out of the gallery above so that it is
# seen once, at the end.
END = ("captures-2026-09-24/img-1990.jpg", "end", "A long-necked bird on a branch against misty hills")

# Photographer credits, by output name, once the school can confirm them.
CREDITS = {}


def items():
    """Every gallery photograph in reading order, as (source, name, caption)."""
    return [item for row in ROWS for item in row]


def count():
    return len(items())


WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
         "fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy"}


def count_word():
    """The number of photographs, in words, as the site writes numbers in prose."""
    n = count()
    if n < 20:
        return WORDS[n]
    return TENS[n // 10] + ("-" + WORDS[n % 10] if n % 10 else "")


def _sizes():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)["images"]


def _esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def chapter_nav_html():
    """A short index keeps the photo journal easy to browse."""
    links = [
        f'    <a href="#cg-{chapter["slug"]}">{_esc(chapter["title"])}'
        f'<span>{sum(map(len, chapter["rows"]))}</span></a>'
        for chapter in CHAPTERS
    ]
    return '<nav class="cg__contents" aria-label="Photo chapters">\n' + "\n".join(links) + '\n</nav>'


def _tile_srcset(s, frac):
    """The 1x cut and the tile, and the width a tile with this share of its
    row is drawn at: the whole column on a phone (one photograph to a row),
    then its share of a column 92vw wide, 68vw, and at most 882px."""
    if "small_path" not in s:
        return ""
    return (f' srcset="{s["small_path"]} {s["small"][0]}w, {s["tile_path"]} {s["tile"][0]}w"'
            f' sizes="(max-width: 640px) 92vw, (max-width: 900px) {math.ceil(92 * frac)}vw,'
            f' (max-width: 1300px) {math.ceil(68 * frac)}vw, {math.ceil(882 * frac)}px"')


def gallery_html():
    """Every photograph is visible in a chapter and opens at full size.

    The rows preserve image shape; without JavaScript each link opens its
    photograph directly. With it, the viewer follows the same chapter order.
    """
    sizes = _sizes()
    sections, index = [], 0
    for chapter in CHAPTERS:
        rows = []
        for row in chapter["rows"]:
            tiles = []
            share = sum(sizes[n]["tile"][0] / sizes[n]["tile"][1] for _, n, _ in row)
            for _, name, caption in row:
                s = sizes[name]
                ratio = s["tile"][0] / s["tile"][1]
                credit = CREDITS.get(name, "")
                tiles.append(
                    f'          <a class="cg__item" href="{s["full_path"]}" data-cg-item '
                    f'data-cg-index="{index}" data-cg-w="{s["full"][0]}" data-cg-h="{s["full"][1]}"'
                    + (f' data-cg-credit="{_esc(credit)}"' if credit else "") +
                    f' style="--ar:{ratio:.4f}">\n'
                    f'            <img src="{s["tile_path"]}"{_tile_srcset(s, ratio / share)} width="{s["tile"][0]}" height="{s["tile"][1]}"\n'
                    f'                 alt="{_esc(caption)}" loading="lazy" decoding="async">\n'
                    f'            <span class="cg__item-caption" aria-hidden="true">{_esc(caption)}</span>\n'
                    f'          </a>')
                index += 1
            solo = " cg__row--solo" if len(row) == 1 else ""
            rows.append(f'        <div class="cg__row{solo}">\n' + "\n".join(tiles) + '\n        </div>')
        count = sum(map(len, chapter["rows"]))
        slug = chapter["slug"]
        sections.append(
            f'      <section class="cg__chapter" id="cg-{slug}" aria-labelledby="cg-{slug}-title">\n'
            f'        <header class="cg__chapter-head">\n'
            f'          <p class="cg__chapter-count">{count} photographs</p>\n'
            f'          <h3 id="cg-{slug}-title">{_esc(chapter["title"])}</h3>\n'
            f'          <p>{_esc(chapter["intro"])}</p>\n'
            f'        </header>\n'
            f'        <div class="cg__grid">\n' + "\n".join(rows) +
            '\n        </div>\n      </section>')
    return "\n".join(sections)


def end_html():
    """The last photograph, full width: a phone takes the smaller cut. One
    URL to an attribute, as tools/stage-deploy.py reads them."""
    s = _sizes()[END[1]]
    return (f'<picture>\n'
            f'      <source media="(max-width: 800px)" srcset="{s["tile_path"]}"'
            f' width="{s["tile"][0]}" height="{s["tile"][1]}">\n'
            f'      <img src="{s["full_path"]}" width="{s["full"][0]}" height="{s["full"][1]}"\n'
            f'           alt="{_esc(END[2])}" loading="lazy" decoding="async">\n'
            f'    </picture>')


def featured_img(name, extra=""):
    """One featured photograph, at the size its frame draws it."""
    s = _sizes()["featured/" + name]
    caption = next(c for _, n, c, _ in FEATURED if n == name)
    return (f'<img src="{s["tile_path"]}" width="{s["tile"][0]}" height="{s["tile"][1]}"'
            f' alt="{_esc(caption)}" loading="lazy" decoding="async"{extra}>')


def featured_caption(name):
    return _esc(next(c for _, n, c, _ in FEATURED if n == name))


def expand_featured(html):
    """{{CAPTURES_FEATURED:name}} and {{CAPTURES_FEATURED_CAPTION:name}} in
    the page, and {{CAPTURES_LEAD_CAPTION}}."""
    import re
    html = re.sub(r"\{\{CAPTURES_FEATURED:([a-z-]+)\}\}", lambda m: featured_img(m.group(1)), html)
    html = re.sub(r"\{\{CAPTURES_FEATURED_CAPTION:([a-z-]+)\}\}",
                  lambda m: featured_caption(m.group(1)), html)
    return html.replace("{{CAPTURES_LEAD_CAPTION}}", _esc(LEAD_CAPTION))
