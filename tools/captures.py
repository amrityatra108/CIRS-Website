"""CIRS Captures — the photographs below the opening, and the page's ending.

Everything shown here is one of the school's own camera originals from
assets/source. tools/make-captures-gallery.py cuts each one — a tile for the
page and a full-size image for the viewer, and for the four featured
photographs a cut at the size their frame draws them — and records the sizes
it wrote in tools/captures-gallery.json, which is what this module reads, so
the site build itself never needs an image library.

CAPTIONS say what the photograph shows. Where one also names the occasion,
that was verified, not inferred: the file in assets/source is byte for byte
the file in a named event folder in the school's Drive (CIRS Studio), and the
date the camera recorded agrees with it. Only the unresized camera originals
can be matched that way; the rest were resized on the way in, so for them no
occasion is given. No file anywhere records a photographer, so no caption
names one: where the school can supply a name, it goes in CREDITS, and the
viewer shows a credit line for any photograph that has one.

    0C9A4095, 0C9A4097, 0C9A4128  "46. Anand Utsav"; taken 8 October 2025
    0C9A2196                      "9. Khel Mela (Sports DAY)", Day 2;
                                  taken 4 February 2026

FEATURED is the short sequence that follows the opening: the photograph that
opened out of the camera's lens, then three more, each given a composition of
its own — see tools/pages/captures.html and assets/css/captures-featured.css.
They are not repeated in the gallery.

ROWS is the gallery's layout. Each row is laid out at one height across the
full width, so a portrait sits beside a landscape at its own shape rather
than being cropped to match it; a row of one is a full-width photograph. The
order is the reading order, and the viewer's next and previous follow it.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "captures-gallery.json")

ANAND_UTSAV = "at Anand Utsav, October 2025"
KHEL_MELA = "at Khel Mela, the sports day, February 2026"

# (source file in assets/source, output name, caption, width of the cut)
# The lead — the photograph the camera's lens opens onto — is cut by
# tools/make-captures-shot.py, because the opening uses it first.
FEATURED = [
    ("8A5A3313.JPG", "overhead-kick", "An overhead kick on the field, with the hills behind", 1800),
    ("0C9A4095.JPG", "greeting", "A student with her hands folded in greeting, " + ANAND_UTSAV, 1200),
    ("DJI_0856.JPG", "campus-air", "The campus from the air, its courtyards among the trees", 2400),
]
LEAD_CAPTION = "A student dancing on stage in red, one arm raised"

# (source file in assets/source, output name, caption)
ROWS = [
    [("IMG_0550.JPG", "dancers-pink-light", "Dancers in performance under pink stage light"),
     ("0C9A4097.JPG", "hands-folded-him", "A student with his hands folded in greeting, " + ANAND_UTSAV)],
    [("IMG_1790.JPG", "microscope", "A student at the microscope in the laboratory"),
     ("IMG_2474.JPG", "amphitheatre-night", "Students seated in the amphitheatre under floodlights"),
     ("IMG_1828.JPG", "three-dancers", "Three dancers on a stage lit pink")],
    [("IMG_20210514_182259.jpg", "after-rain", "The school after rain, its lights reflected in the paving")],
    [("IMG_9314.JPG", "swimmer", "A swimmer mid-stroke in the pool"),
     ("DSC_0858.JPG", "guitars", "Students playing guitars together"),
     ("IMG_1686.JPG", "meditation", "Students seated in meditation")],
    [("IMG_6061.JPG", "rappelling", "Rappelling down a rock face in helmet and harness"),
     ("0C9A4128.JPG", "seated-together", "Students seated together on the floor, " + ANAND_UTSAV),
     ("IMG_8811.JPG", "stage-production", "A stage production in costume")],
    [("IMG_3051.JPG", "football", "Football on the field"),
     ("IMG_1898.JPG", "robot", "Students at work on a small wheeled robot"),
     ("DSC_8037.JPG", "tabla", "A tabla lesson")],
    [("0C9A2196.JPG", "lectern", "A student speaking at a lectern outdoors, " + KHEL_MELA),
     ("IMG_9879.JPG", "human-pyramid", "A human pyramid reaching for a hanging pot, after dark")],
    [("IMG_2327.JPG", "runners", "Runners in team colours on the track"),
     ("IMG_1630.JPG", "yoga", "Yoga on the lawn"),
     ("2.JPG", "ncc-march", "The NCC contingent marching with its flag")],
    [("drive-student-life-beyond.JPG", "dancing-lawn", "Students dancing on the lawn")],
]

# The ending: one photograph, kept out of the gallery above so that it is
# seen once, at the end.
END = ("IMG_2051.JPG", "end", "The school, with cloud on the hills behind it")

# Photographer credits, by output name, once the school can confirm them.
CREDITS = {}


def items():
    """Every gallery photograph in reading order, as (source, name, caption)."""
    return [item for row in ROWS for item in row]


def count():
    return len(items())


WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
         "fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = {2: "twenty", 3: "thirty", 4: "forty"}


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


def gallery_html():
    """The rows of tiles. Each tile is a link to the full-size image, so
    without JavaScript it simply opens the photograph; with it, the viewer
    in assets/js/captures-gallery.js takes the click instead."""
    sizes = _sizes()
    out, index = [], 0
    for row in ROWS:
        tiles = []
        for _, name, caption in row:
            s = sizes[name]
            ratio = s["tile"][0] / s["tile"][1]
            credit = CREDITS.get(name, "")
            tiles.append(
                f'        <a class="cg__item" href="{s["full_path"]}" data-cg-item '
                f'data-cg-index="{index}" data-cg-w="{s["full"][0]}" data-cg-h="{s["full"][1]}"'
                + (f' data-cg-credit="{_esc(credit)}"' if credit else "") +
                f' style="--ar:{ratio:.4f}">\n'
                f'          <img src="{s["tile_path"]}" width="{s["tile"][0]}" height="{s["tile"][1]}"\n'
                f'               alt="{_esc(caption)}" loading="lazy" decoding="async">\n'
                f'        </a>')
            index += 1
        solo = " cg__row--solo" if len(row) == 1 else ""
        out.append(f'      <div class="cg__row{solo}">\n' + "\n".join(tiles) + "\n      </div>")
    return "\n".join(out)


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
