#!/usr/bin/env python3
"""Cut the Houses page's photographs from the source library.

    python3 tools/make-houses.py

Same shape as tools/make-photos.py — every crop, size and focal point is
recorded here rather than remembered — but with one deliberate difference,
and it is the whole reason this page has its own cutter.

make-photos grades towards the site's purple at KEEP_COLOUR 0.72. On this
page the colour IS the content: a reader has to be able to tell the red house
from the green one in a photograph, and a wash that pulls every frame towards
one hue is the one thing that must not happen here. So this file keeps 0.92 of
the original colour and lays on almost no wash. The frames still sit in the
same family as the rest of the site — the tonal lift is identical — but a
Vasishtha jersey stays Vasishtha red.

The choices below are also evidence. The source photographs show house names
on garments, establishing the colours recorded in tools/houses.py. Three hero
crops retain readable names. The green source frame shows partial WAMITRA
lettering on another student; its crop instead focuses on the classroom
activity, so the page does not claim that the cropped shirt bears a name.
"""

import os
import sys

from PIL import Image, ImageEnhance, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/source")
OUT = os.path.join(ROOT, "assets/img/houses")

SHADOW = (36, 26, 56)
HIGHLIGHT = (240, 229, 212)
KEEP_COLOUR = 0.92        # see the note above: the house colours are the content
WASH = (32, 23, 44)
WASH_ALPHA = 0.03

# name, source, (w, h), focal point (x, y) in 0..1, region of the original
#
# The fifth column is what make-photos.py does not have and this page needs.
# A focal point can only move a crop along the axis the target shape leaves
# spare, so on a frame already the right shape it does nothing at all: four
# of the photographs below are wanted as a detail of a wide frame — one player
# in a match of eleven, one sash in a line of thirty — and a focal point
# cannot reach them. The region (x0, y0, x1, y1) in 0..1 is taken out of the
# original first, and the focal point then works inside it.
#
# None of the regions upscales by more than about a tenth: these originals
# are 3200px and larger, so a third of one frame is still wider than the
# 1600px it is being cut to.
PHOTOS = [
    # ---- the opening frame -------------------------------------------------
    # Four 4:5 portraits, one per zone. The source frames document their
    # colours; the green portrait crop omits the lettering in its source frame.
    #
    # These four are the only photographs on this page that a visitor waits
    # for — they are the fold, and nothing else on the page loads until it is
    # scrolled to. So they are the only ones cut twice. On a phone the zones
    # stack at 375px and a 900px rendition is two and a half times the size
    # it is drawn at, which on a hundred-acre school's mobile data is half a
    # megabyte of nothing; the 500px pair below carry the phone and cost about
    # a tenth of it. The <img> lists both in a srcset and the browser picks.
    #
    # tools/check-links.py did not read srcset attributes before this page
    # existed, so these four would have been reported as orphans. It reads
    # them now.
    ("hero-vasishtha.jpg",   "IMG_0612.JPG",            (900, 1125), (0.84, 0.56), None),
    ("hero-vasishtha-500.jpg", "IMG_0612.JPG",          (500,  625), (0.84, 0.56), None),
    # The yellow sashes are in the left eighth of a wide frame of the whole
    # line, so the region is that eighth. It is also cropped off the name
    # badges further down the line, which are legible in the original.
    ("hero-valmiki.jpg",     "IMG_8229.JPG",            (900, 1125), (0.32, 0.45),
     (0.00, 0.18, 0.28, 1.00)),
    ("hero-valmiki-500.jpg", "IMG_8229.JPG",            (500,  625), (0.32, 0.45),
     (0.00, 0.18, 0.28, 1.00)),
    ("hero-vishwamitra.jpg", "IMG_20260709_181900.jpg", (900, 1125), (0.62, 0.44), None),
    ("hero-vishwamitra-500.jpg", "IMG_20260709_181900.jpg", (500, 625), (0.62, 0.44), None),
    # The narrowest region here, and the only one that upscales at all: the
    # blue shirt is a fifth of the width of a frame whose right-hand third is
    # the red house. Widening it to avoid the upscale puts Vasishtha in
    # Vyasa's zone, which is the one thing the opening frame must not do.
    ("hero-vyasa.jpg",       "IMG_0851.JPG",            (900, 1125), (0.50, 0.30),
     (0.505, 0.12, 0.745, 0.98)),
    ("hero-vyasa-500.jpg",   "IMG_0851.JPG",            (500,  625), (0.50, 0.30),
     (0.505, 0.12, 0.745, 0.98)),

    # ---- the four chapters -------------------------------------------------
    # 16:9, one per house. Valmiki and Vishwamitra are two crops of one
    # frame, and that is not a repetition dressed up: it is one inter-house
    # football match, and the two regions below are its two halves — the
    # amber house on the ball, and the green house covering across. Two
    # houses, two subjects, two photographs.
    ("ch-vasishtha.jpg",   "IMG_1405.JPG",            (1600, 900), (0.50, 0.46), None),
    ("ch-valmiki.jpg",     "IMG_3051.JPG",            (1600, 900), (0.50, 0.45),
     (0.10, 0.12, 0.66, 0.78)),
    ("ch-vishwamitra.jpg", "IMG_3051.JPG",            (1600, 900), (0.55, 0.42),
     (0.55, 0.08, 1.00, 0.82)),
    ("ch-vyasa.jpg",       "IMG_20260709_181712.jpg", (1600, 900), (0.42, 0.52), None),

    # ---- the march ---------------------------------------------------------
    # The horizontal sequence. 3:2, four frames, in the order they pass: the
    # colour party, the ranks behind it, the dais, and the lap afterwards.
    ("march-01.jpg", "2.JPG",          (1200, 800), (0.50, 0.52), None),
    ("march-02.jpg", "DSC_0059.JPG",   (1200, 800), (0.46, 0.55), None),
    ("march-03.jpg", "0C9A2196.JPG",   (1200, 800), (0.58, 0.48), None),
    ("march-04.jpg", "0C9A0742.JPG",   (1200, 800), (0.52, 0.40), None),

    # ---- the competition ---------------------------------------------------
    # A house quiz with the house cards standing on the tables. The one
    # photograph in the library of the houses competing at a desk rather
    # than on a field.
    ("comp-quiz.jpg", "IMG_9084.JPG",  (1400, 788), (0.55, 0.42),
     (0.18, 0.18, 0.78, 0.95)),

    # ---- sport -------------------------------------------------------------
    # One frame per sport. The first is the page's best single photograph:
    # one tennis session with three of the four houses waiting to return in
    # their own colours, which is the whole argument of this page in one
    # frame.
    ("sport-tennis.jpg",    "IMG_0851.JPG",  (1600, 900), (0.50, 0.32),
     (0.48, 0.10, 1.00, 1.00)),
    ("sport-athletics.jpg", "HARI5531.JPG",  (1000, 1250), (0.50, 0.42), None),
    # The medals themselves, and not the two swimmers beside them: their
    # certificates carry their names at a size this crop does not publish.
    ("sport-medals.jpg",    "0G8A3883.JPG",  (1000, 750), (0.72, 0.50),
     (0.70, 0.40, 1.00, 0.85)),

    # ---- culture -----------------------------------------------------------
    # The evening pyramid, with the school ringed round it in house colours.
    ("culture-night.jpg", "IMG_9879.JPG", (1600, 900), (0.46, 0.50), None),

    # ---- the reunion -------------------------------------------------------
    # The whole school drawn up in ranks on the field, which is the four
    # houses assembled and is the only photograph here that is. It is cut
    # wider and shallower than why-cirs.html's founding.jpg from the same
    # original, because this one is a closing band rather than a panel.
    ("reunion.jpg", "1.JPG", (2000, 900), (0.50, 0.54), None),
]


def grade(im):
    grey = ImageEnhance.Contrast(im.convert("L")).enhance(1.05)
    ramp = []
    for ch in range(3):
        lo, hi = SHADOW[ch], HIGHLIGHT[ch]
        ramp += [int(lo + (hi - lo) * (i / 255)) for i in range(256)]
    toned = Image.blend(grey.convert("RGB").point(ramp), im, KEEP_COLOUR)
    return Image.blend(toned, Image.new("RGB", im.size, WASH), WASH_ALPHA)


def cover(im, w, h, focal):
    """Fill w x h, keeping the focal point in frame rather than the centre."""
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * scale)), max(h, round(im.height * scale))),
                   Image.LANCZOS)
    fx, fy = focal
    x = min(max(round(im.width * fx - w / 2), 0), im.width - w)
    y = min(max(round(im.height * fy - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))


def region(im, box):
    """The part of the original a crop is taken out of, in 0..1 coordinates."""
    if not box:
        return im
    x0, y0, x1, y1 = box
    return im.crop((round(im.width * x0), round(im.height * y0),
                    round(im.width * x1), round(im.height * y1)))


def main():
    missing = [s for _, s, _, _, _ in PHOTOS if not os.path.exists(os.path.join(SRC, s))]
    if missing:
        sys.exit("make-houses: not in assets/source/ — " + ", ".join(sorted(set(missing))))
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for name, source, (w, h), focal, box in PHOTOS:
        im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, source))).convert("RGB")
        cut = grade(cover(region(im, box), w, h, focal))
        out = os.path.join(OUT, name)
        cut.save(out, "JPEG", quality=82, optimize=True, progressive=True)
        kb = os.path.getsize(out) // 1024
        total += kb
        print(f"  {name:<22} {w}x{h:<5} {kb:>4} KB   <- {source}")
    print(f"  {len(PHOTOS)} photographs, {total} KB")


if __name__ == "__main__":
    main()
