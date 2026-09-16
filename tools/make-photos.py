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
    ("student-life.jpg",        "IMG_0081.JPG", (1200, 1500), (0.50, 0.50)),
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
    ("amphitheatre.jpg",        "IMG_2449.JPG",           (1600,  900), (0.50, 0.50)),
    ("vision.jpg",              "IMG_1663.JPG",           (1600,  900), (0.50, 0.50)),
    ("forest-air.jpg",          "CIRS.jpg",               (1600,  900), (0.50, 0.50)),
    ("fields-air.jpg",          "DJI_0856.JPG",           (1400,  640), (0.50, 0.50)),
    ("valley.jpg",              "school-front-view.JPG",  (1400,  640), (0.50, 0.58)),
    ("assembly-front.jpg",      "IMG_20260423_091355.jpg", (1400, 640), (0.50, 0.55)),

    # Sport — the inter-house basketball fixture, in the same 4:3 tile as the
    # Admissions grid so the two read as one house style. Shot vertically, so
    # the focal point is doing real work here: centred on the ball and the
    # players contesting it, not on the middle of the frame.
    ("sports/basketball-contest.jpg",  "sports/basketball-contest.jpg",  (1000, 750), (0.50, 0.42)),
    ("sports/basketball-shot.jpg",     "sports/basketball-shot.jpg",     (1000, 750), (0.50, 0.33)),
    ("sports/basketball-floodlit.jpg", "sports/basketball-floodlit.jpg", (1000, 750), (0.50, 0.46)),
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
        grade(cover(im, w, h, focal)).save(
            out, "JPEG", quality=84, optimize=True, progressive=True)
        kb = os.path.getsize(out) // 1024
        total += kb
        print(f"  {name:<22} {w}x{h:<5} {kb:>4} KB   <- {source}")
    print(f"  {len(PHOTOS)} photographs, {total} KB")


if __name__ == "__main__":
    main()
