#!/usr/bin/env python3
"""Derive the site's photographs from the source library.

Every image a page shows is cut here from assets/source/ and written to
assets/img/, so the crop, the size and the grade of each one are recorded
rather than remembered. Re-run it after changing a choice below.

The grade is deliberately light — lighter than the honeycomb's duotone.
These sit at full strength on the page with nothing over them, so they have
to stay photographs; the small shift towards the palette is only there so a
grid of six reads as one set rather than six unrelated snapshots.

    python3 tools/make-photos.py
"""

import os
import sys

from PIL import Image, ImageEnhance, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/source")
OUT = os.path.join(ROOT, "assets/img")

# The grade below is for photographs. One image here is not a photograph but
# a finished piece of the school's own design, with its wordmark set into it:
# the wash flattens the bright blues it is built on and warms the whole thing,
# which reads as a faded picture rather than a campaign banner. It is cut at
# its own colours. Remove a name from here and it is graded like the rest.
UNGRADED = set()

SHADOW = (36, 26, 56)
HIGHLIGHT = (240, 229, 212)
KEEP_COLOUR = 0.72        # most of the original colour survives
WASH = (32, 23, 44)
WASH_ALPHA = 0.07

# name, source, (w, h), focal point across the frame (x, y) in 0..1
PHOTOS = [
    # Feature panels — 4:5, one per page. Arts no longer has one: that page
    # is the wall, and tools/make-arts-wall.py cuts its photographs.
    ("sports.jpg",              "HARI5692.JPG", (1200, 1500), (0.42, 0.55)),
    # The full-bleed band behind "A Campus That Never Really Closes". The
    # campus itself rather than a room in it: the blocks with the cloud coming
    # over the Ghats behind them. Framed low, so the ridge and the sky have
    # the top of the picture and the gradient has the ground.
    ("campus-band.jpg",         "IMG_2051.JPG", (1920, 1080), (0.50, 0.56)),
    ("junior-school.jpg",       "IMG_1898.JPG", (1200, 1500), (0.50, 0.45)),
    ("senior-school.jpg",       "IMG_1894.JPG", (1200, 1500), (0.50, 0.45)),

    # The School History film window, matching the home page's 16:9 still.
    ("history-still.jpg",       "IMG_20210514_182259.jpg", (1600, 900), (0.50, 0.52)),

    # The Admissions grid — six tiles, all 4:3, two rows of three.
    ("adm-arrival.jpg",         "IMG_0195.JPG", (1000,  750), (0.50, 0.45)),
    ("adm-examination.jpg",     "IMG_9069.JPG", (1000,  750), (0.45, 0.52)),
    ("adm-welcome.jpg",         "8A5A0707.JPG", (1000,  750), (0.50, 0.50)),
    ("adm-interview.jpg",       "IMG_9893.JPG", (1000,  750), (0.50, 0.50)),
    ("adm-assembly.jpg",        "IMG_2258.JPG", (1000,  750), (0.50, 0.60)),
    ("adm-houses.jpg",          "CRS01788.JPG", (1000,  750), (0.50, 0.50)),

    # One photograph, one place. entrance.jpg was carrying five pages and
    # aerial-duo.jpg four, which made the site feel smaller than it is; these
    # seven take over the duplicated slots, each chosen for what its section
    # is actually about rather than for being another picture of the campus.
    ("academic-block.jpg",      "academic-block.JPG",     (1400,  325), (0.50, 0.58)),
    ("campus-lawn.jpg",         "CRS01413.JPG",           (1600,  900), (0.50, 0.55)),
    ("film-audience.jpg",       "IMG_3217.JPG",           (1600,  900), (0.50, 0.52)),
    ("vision.jpg",              "IMG_1663.JPG",           (1600,  900), (0.50, 0.50)),
    ("forest-air.jpg",          "CIRS.jpg",               (1600,  900), (0.50, 0.50)),
    ("fields-air.jpg",          "DJI_0856.JPG",           (1400,  640), (0.50, 0.50)),
    ("valley.jpg",              "school-front-view.JPG",  (1400,  640), (0.50, 0.58)),
    ("assembly-front.jpg",      "IMG_20260423_091355.jpg", (1400, 640), (0.50, 0.55)),

    # The second pass on repetition. hero.jpg opened both the home page and
    # News; history-still, student-life and walkway each carried two pages,
    # and student-life three. Each keeps the page its caption was written for
    # and hands the others a photograph of their own subject.
    ("news-hero.jpg",           "IMG_2327.JPG",           (1280,  720), (0.50, 0.55)),

    # The Why CIRS opening frame. It replaces a 1200x1500 portrait of three
    # students that came in with the original redesign and whose own source
    # is not in this library — so when that page lost its banner and the
    # photograph became a full-window hero, object-fit:cover took 450px off
    # the top of a frame that had no room to give and cut their heads. There
    # was nothing to recrop.
    #
    # This one is cut wide, at 1.6, which is about the shape of a laptop
    # window, so on a desktop cover barely crops it at all. The focal point
    # is high in the frame on purpose: every head keeps clear air above it,
    # and what a narrow window crops is the empty court at the bottom.
    ("why-cirs.jpg",            "IMG_1939.JPG",           (2000, 1250), (0.50, 0.38)),
    ("founding.jpg",            "1.JPG",                  (1600,  900), (0.50, 0.55)),
    ("motto.jpg",               "IMG_1686.JPG",           (1600,  900), (0.46, 0.50)),
    ("boarding.jpg",            "20180518_121042.jpg",    (1600,  900), (0.52, 0.50)),
    ("students.jpg",            "IMG_8075.JPG",           (1400,  640), (0.50, 0.48)),

    # The Student Life hero deck. Ten photographs dealt up through the
    # marquee — and deliberately ten different shapes. A deck of identical
    # cards reads as a slideshow in a frame; a pile of a tall one, a wide
    # one and a square one reads as photographs. The sizes below are the
    # shapes, and the widths they are shown at are in pages.css.
    #
    # PROTOTYPE: these are stand-ins cut from the existing library so the
    # motion can be judged. The school is curating ten.
    ("slhero/card-01.jpg", "0C9A4097.JPG",  ( 900, 1200), (0.52, 0.42)),   # 3:4
    ("slhero/card-02.jpg", "IMG_2480.JPG",  (1200,  800), (0.50, 0.45)),   # 3:2
    ("slhero/card-03.jpg", "IMG_1625.JPG",  (1200,  750), (0.50, 0.52)),   # 8:5
    ("slhero/card-04.jpg", "CRS00876.JPG",  ( 800, 1000), (0.50, 0.45)),   # 4:5
    ("slhero/card-05.jpg", "_MG_0139.JPG",  ( 800, 1200), (0.50, 0.45)),   # 2:3
    ("slhero/card-06.jpg", "IMG_9313.JPG",  (1000, 1000), (0.50, 0.50)),   # 1:1
    ("slhero/card-07.jpg", "IMG_6106.JPG",  ( 900, 1200), (0.50, 0.45)),   # 3:4
    ("slhero/card-08.jpg", "0C9A4128.JPG",  (1200,  800), (0.50, 0.42)),   # 3:2
    ("slhero/card-09.jpg", "HARI7500.JPG",  ( 900,  900), (0.50, 0.45)),   # 1:1
    ("slhero/card-10.jpg", "IMG_2449.JPG",  (1200,  675), (0.50, 0.45)),   # 16:9

    # The Blog. Four fragments for the masthead collage, cut so each one reads
    # as a detail rather than a whole photograph. The cards below them carry
    # no photograph at all: every article came out of the magazine, and a
    # stock picture over someone's essay says less than the essay's own first
    # sentences do.
    # The three commented lines above cut the old Blog masthead collage, which
    # the news-stand front page replaced. Their originals are still in
    # assets/source/ and their crops are intact: uncomment to bring them back.
    # ("blog/frag-voice.jpg",     "0C9A4095.JPG",   ( 900, 1200), (0.52, 0.42)),
    # ("blog/frag-lab.jpg",       "IMG_1790.JPG",   ( 800,  800), (0.52, 0.45)),
    # ("blog/frag-together.jpg",  "IMG_0633.JPG",   (1200,  800), (0.50, 0.45)),
    ("blog/frag-desk.jpg",      "IMG_8830.JPG",   (1200,  800), (0.50, 0.52)),

    # Sport — the inter-house basketball fixture, in the same 4:3 tile as the
    # Admissions grid so the two read as one house style. Shot vertically, so
    # the focal point is doing real work here: centred on the ball and the
    # players contesting it, not on the middle of the frame.
    ("sports/basketball-contest.jpg",  "sports/basketball-contest.jpg",  (1000, 750), (0.50, 0.42)),
    ("sports/basketball-shot.jpg",     "sports/basketball-shot.jpg",     (1000, 750), (0.50, 0.33)),
    ("sports/basketball-floodlit.jpg", "sports/basketball-floodlit.jpg", (1000, 750), (0.50, 0.46)),

    # The home page's horizontal run — ten photographs scrubbed sideways
    # between the hero and the film.
    #
    # Six wide and four tall. A row of identical rectangles sliding past
    # reads as a filmstrip; mixed shapes read as photographs that were laid
    # out. The order is a day, and it is the order they pass in: the lawn at
    # first light, a lesson, the drums, the hall, the table, the field, the
    # water, the trail, the stage, and the amphitheatre after dark.
    #
    # None of these ten is used at size anywhere else on the site. That is
    # deliberate and worth keeping: the run is the first thing under the
    # hero, and a photograph the reader meets here and again on Admissions
    # makes the library look smaller than it is.
    ("hrun/01-lawn.jpg",    "IMG_1630.JPG", (1500, 1000), (0.50, 0.50)),
    ("hrun/02-lesson.jpg",  "IMG_1806.JPG", (1000, 1250), (0.34, 0.52)),
    ("hrun/03-drums.jpg",   "DSC_8037.JPG", (1000, 1250), (0.46, 0.66)),
    ("hrun/04-hall.jpg",    "CRS09514.JPG", (1500, 1000), (0.50, 0.46)),
    ("hrun/05-table.jpg",   "IMG_0081.JPG", (1500, 1000), (0.50, 0.50)),
    ("hrun/06-field.jpg",   "8A5A3313.JPG", (1000, 1500), (0.50, 0.46)),
    ("hrun/07-water.jpg",   "IMG_9314.JPG", (1500, 1000), (0.55, 0.50)),
    ("hrun/08-trail.jpg",   "IMG_6061.JPG", (1500, 1000), (0.56, 0.50)),
    ("hrun/09-stage.jpg",   "IMG_1828.JPG", (1000, 1500), (0.50, 0.45)),
    ("hrun/10-night.jpg",   "IMG_2474.JPG", (1500, 1000), (0.50, 0.52)),
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


def main():
    missing = [s for _, s, _, _ in PHOTOS if not os.path.exists(os.path.join(SRC, s))]
    if missing:
        sys.exit("make-photos: not in assets/source/ — " + ", ".join(missing))
    total = 0
    for name, source, (w, h), focal in PHOTOS:
        im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, source))).convert("RGB")
        out = os.path.join(OUT, name)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        cut = cover(im, w, h, focal)
        if name not in UNGRADED:
            cut = grade(cut)
        cut.save(out, "JPEG", quality=84, optimize=True, progressive=True)
        kb = os.path.getsize(out) // 1024
        total += kb
        print(f"  {name:<22} {w}x{h:<5} {kb:>4} KB   <- {source}")
    print(f"  {len(PHOTOS)} photographs, {total} KB")


if __name__ == "__main__":
    main()
