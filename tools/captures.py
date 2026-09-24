"""CIRS Captures — the featured photographs, gallery, and ending.

The sixteen supplied photographs are in assets/source/captures-2026-09-24.
Captions describe only what is visible; photographer, date, and location are
not inferred. tools/make-captures-gallery.py writes the gallery and featured
images and their dimensions to tools/captures-gallery.json, so the site build
does not need an image library. The opening lead is cut separately by
tools/make-captures-shot.py.

ROWS defines the gallery order and its equal-height rows. The viewer follows
the same reading order. The lead, three featured images, and ending appear
once each outside the gallery.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "captures-gallery.json")

# (source file in assets/source, output name, caption, width of the cut)
# The lead — the photograph dissolved over the camera's final frame — is cut
# by tools/make-captures-shot.py, because the opening uses it first.
LEAD_SOURCE = "captures-2026-09-24/img-9821.jpg"
LEAD_CAPTION = "A bee on a vivid yellow flower"
FEATURED = [
    ("captures-2026-09-24/dsc02269.jpg", "companion", "A black and yellow butterfly on pale purple flowers", 1800),
    ("captures-2026-09-24/img-9515.jpg", "portrait", "A hoopoe perched among branches", 1200),
    ("captures-2026-09-24/img-1007.jpg", "wide", "A small dark bird amid pink blossoms", 2400),
]

# (source file in assets/source, output name, caption)
ROWS = [
    [("captures-2026-09-24/dsc00453.jpg", "bird-among-leaves", "A red-crested bird among broad green leaves"),
     ("captures-2026-09-24/img-1396.jpg", "bird-white-blossoms", "A small bird reaching into white blossoms")],
    [("captures-2026-09-24/img-1887.jpg", "squirrel-branch", "A squirrel perched on a branch against blue sky"),
     ("captures-2026-09-24/img-2031.jpg", "green-lizard", "A green lizard partly hidden beneath leaves"),
     ("captures-2026-09-24/img-4426.jpg", "grey-bird", "A small grey bird seen through soft green foliage")],
    [("captures-2026-09-24/kingfisher.jpg", "kingfisher-water", "A kingfisher by the water, framed by tree trunks")],
    [("captures-2026-09-24/img-4491.jpg", "kingfisher-post", "A kingfisher perched on a post with trees behind"),
     ("captures-2026-09-24/img-4562.jpg", "dove-branches", "A dove perched among yellow flowers and branches")],
    [("captures-2026-09-24/img-2030.jpg", "bird-dark", "A small pale-headed bird against a dark background"),
     ("captures-2026-09-24/img-5244.jpg", "bird-in-shade", "A dark green bird on a branch in deep shade"),
     ("captures-2026-09-24/img-5569.jpg", "bird-bare-branches", "A small red-crowned bird among bare branches")],
]

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
