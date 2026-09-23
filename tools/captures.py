"""CIRS Captures — the photographs below the opening, and the page's ending.

Everything shown here is one of the school's own camera originals from
assets/source. tools/make-captures-gallery.py cuts each one twice — a tile
for the page and a full-size image for the viewer — and records the sizes
it wrote in tools/captures-gallery.json, which is what this module reads, so
the site build itself never needs an image library.

CAPTIONS say what the photograph shows and nothing more. None of these files
carries a photographer, a date anyone has confirmed, or the name of an event,
and no caption supplies one: a caption that named the occasion or the
student would be a guess presented as a fact. Where the school can supply
those, they go in CREDITS and in the caption, and the viewer shows a credit
line for any photograph that has one. Until then it shows none.

ROWS is the layout. Each row is laid out at one height across the full
width, so a portrait sits beside a landscape at its own shape rather than
being cropped to match it; a row of one is a full-width photograph. The
order is the reading order, and the viewer's next and previous follow it.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "captures-gallery.json")

# (source file in assets/source, output name, caption)
ROWS = [
    [("IMG_0550.JPG", "dancers-pink-light", "Dancers in performance under pink stage light"),
     ("0C9A4095.JPG", "hands-folded-her", "A student with her hands folded in greeting")],
    [("8A5A3313.JPG", "overhead-kick", "An overhead kick on the field, with the hills behind"),
     ("IMG_1790.JPG", "microscope", "A student at the microscope in the laboratory"),
     ("IMG_2474.JPG", "amphitheatre-night", "Students seated in the amphitheatre under floodlights")],
    [("IMG_20210514_182259.jpg", "after-rain", "The school after rain, its lights reflected in the paving")],
    [("IMG_1828.JPG", "three-dancers", "Three dancers on a stage lit pink"),
     ("IMG_9314.JPG", "swimmer", "A swimmer mid-stroke in the pool"),
     ("0C9A4097.JPG", "hands-folded-him", "A student with his hands folded in greeting")],
    [("DSC_0858.JPG", "guitars", "Students playing guitars together"),
     ("IMG_1686.JPG", "meditation", "Students seated in meditation")],
    [("IMG_6061.JPG", "rappelling", "Rappelling down a rock face in helmet and harness"),
     ("0C9A4128.JPG", "seated-together", "Students seated together on the floor"),
     ("IMG_8811.JPG", "stage-production", "A stage production in costume")],
    [("IMG_3051.JPG", "football", "Football on the field"),
     ("IMG_1898.JPG", "robot", "Students at work on a small wheeled robot"),
     ("DSC_8037.JPG", "tabla", "A tabla lesson")],
    [("DJI_0856.JPG", "from-the-air", "The campus from the air")],
    [("0C9A2196.JPG", "lectern", "A student speaking at a lectern outdoors"),
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
