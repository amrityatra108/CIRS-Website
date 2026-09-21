#!/usr/bin/env python3
"""Cut the photographs for the Arts, Music & Theatre wall.

    assets/img/arts/<name>.jpg          the photograph, opened from a tile
    assets/img/arts/thumbs/<name>.jpg   the copy the moving tile carries

The wall holds every photograph at once and moves them, so the tile copies
have to be small: a hundred tiles at full size is a hundred megabytes moving
under a finger. The full copy is only fetched when somebody opens a tile.

The grade is lighter than tools/make-photos.py uses. Those sit flat on a page;
these sit on the purple ground at a fifth of their opacity until the pointer
finds them, and the thing worth keeping in a photograph of a lit stage is the
light. So most of the colour survives and the wash is a whisper — just enough
that twenty-eight photographs from twenty-eight evenings read as one wall.

Two sources feed it:

  * assets/source/ — the camera originals, cropped and graded here.
  * assets/source/archive/ — the photographs the designer had already chosen
    and sized for the standalone archive, kept when that folder was folded into
    this page. They arrived small and there is no larger copy of them in this
    repository, so they are carried across as they are rather than upscaled
    into softness.
  * assets/source/cultural-gallery/ — the small Drive renditions used only by
    the moving tiles. The opened 1600px copies remain on the school's Drive.

SPIC MACAY.jpg is a contact sheet of six photographs from the society's
visiting-artist concerts, so it is cut back into the six. They are visiting
professional musicians and dancers, not students, and the captions say so.

    python3 tools/make-arts-wall.py
"""

import os
import shutil
import sys

from PIL import Image, ImageEnhance, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/source")
ARCHIVE = os.path.join(ROOT, "assets/source/archive")
CULTURAL = os.path.join(ROOT, "assets/source/cultural-gallery")
OUT = os.path.join(ROOT, "assets/img/arts")

FULL = 1600           # long edge of the copy a tile opens
THUMB = 520           # long edge of the copy a tile carries

SHADOW = (36, 26, 56)
HIGHLIGHT = (240, 229, 212)
KEEP_COLOUR = 0.86    # more than make-photos keeps: the stage light is the photograph
WASH = (32, 23, 44)
WASH_ALPHA = 0.05

# name, source in assets/source/, focal point across the frame (x, y) in 0..1
CAMERA = [
    ("guitars",       "DSC_0858.JPG", (0.50, 0.50)),
    ("tabla",         "DSC_8037.JPG", (0.45, 0.55)),
    ("band",          "IMG_1256.JPG", (0.50, 0.50)),
    ("bharatanatyam", "IMG_1828.JPG", (0.50, 0.45)),
    ("ensemble",      "IMG_0550.JPG", (0.50, 0.45)),
    ("juniors",       "IMG_1737.JPG", (0.50, 0.50)),
    ("mime",          "IMG_0778.JPG", (0.50, 0.50)),
    ("tableau",       "IMG_8811.JPG", (0.50, 0.45)),
    ("masks",         "IMG_9050.JPG", (0.50, 0.45)),
    ("banner",        "IMG_3251.JPG", (0.55, 0.55)),
    ("exhibition",    "IMG_3349.JPG", (0.50, 0.50)),
    ("handwork",      "IMG_3291.JPG", (0.50, 0.55)),
    ("floorwork",     "IMG_1533.JPG", (0.50, 0.50)),
    ("amphitheatre",  "IMG_2474.JPG", (0.50, 0.55)),
    ("festival",      "IMG_9312.JPG", (0.50, 0.42)),
]

# The SPIC MACAY contact sheet, and where its six photographs sit in it.
# The gutters are a flat border colour, so the panel edges were measured off
# the file rather than guessed; re-measure if the sheet is ever replaced.
SHEET = "SPIC MACAY.jpg"
SHEET_COLS = [(23, 1058), (1083, 2116), (2140, 3175)]
SHEET_ROWS = [(23, 887), (912, 1775)]
SHEET_NAMES = [
    ["spic-sarod",  "spic-kathakali", "spic-dancers"],
    ["spic-dancer", "spic-concert",   "spic-tabla"],
]

# Photographs the designer had already chosen for the archive. Copied across
# at the size they arrived: these are the only copies in the repository.
CARRIED = [
    ("stage",  "stage.jpg"),
    ("dance",  "dancers.jpg"),
    ("paint1", "paint1.jpg"),
    ("paint2", "paint2.jpg"),
    ("paint3", "paint3.jpg"),
    ("paint4", "paint4.jpg"),
    ("paint5", "paint5.jpg"),
]

CULTURAL_TILES = [f"drive-{index:02d}" for index in range(1, 49)]


def grade(im):
    grey = ImageEnhance.Contrast(im.convert("L")).enhance(1.05)
    ramp = []
    for ch in range(3):
        lo, hi = SHADOW[ch], HIGHLIGHT[ch]
        ramp += [int(lo + (hi - lo) * (i / 255)) for i in range(256)]
    toned = Image.blend(grey.convert("RGB").point(ramp), im, KEEP_COLOUR)
    return Image.blend(toned, Image.new("RGB", im.size, WASH), WASH_ALPHA)


def fit(im, edge):
    """Longest edge to `edge`, aspect kept. Never upscales."""
    if max(im.size) <= edge:
        return im.copy()
    s = edge / max(im.size)
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def trim(im, focal, ratio=1.34):
    """Ease a very wide or very tall frame towards the tiles' shape.

    Tiles crop with object-fit, so an extreme frame loses its subject to the
    crop rather than to this. Anything already near the shape is left alone.
    """
    w, h = im.size
    if w / h > ratio:
        nw = round(h * ratio)
        x = min(max(round(w * focal[0] - nw / 2), 0), w - nw)
        return im.crop((x, 0, x + nw, h))
    if h / w > ratio:
        nh = round(w * ratio)
        y = min(max(round(h * focal[1] - nh / 2), 0), h - nh)
        return im.crop((0, y, w, y + nh))
    return im


def write(name, im, graded, tally):
    full = fit(im, FULL)
    if graded:
        full = grade(full)
    p = os.path.join(OUT, f"{name}.jpg")
    full.save(p, "JPEG", quality=82, optimize=True, progressive=True)
    t = os.path.join(OUT, "thumbs", f"{name}.jpg")
    fit(full, THUMB).save(t, "JPEG", quality=74, optimize=True, progressive=True)
    kb, tkb = os.path.getsize(p) // 1024, os.path.getsize(t) // 1024
    tally.append((kb, tkb))
    print(f"  {name:<16} {full.width}x{full.height:<5} {kb:>4} KB   tile {tkb:>3} KB")


def main():
    missing = [s for _, s, _ in CAMERA if not os.path.exists(os.path.join(SRC, s))]
    if not os.path.exists(os.path.join(SRC, SHEET)):
        missing.append(SHEET)
    missing += [s for _, s in CARRIED if not os.path.exists(os.path.join(ARCHIVE, s))]
    missing += [f"cultural-gallery/{name}.jpg" for name in CULTURAL_TILES
                if not os.path.exists(os.path.join(CULTURAL, f"{name}.jpg"))]
    if missing:
        sys.exit("make-arts-wall: not found — " + ", ".join(missing))

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "thumbs"))

    tally = []
    for name, source, focal in CAMERA:
        im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, source))).convert("RGB")
        write(name, trim(im, focal), True, tally)

    sheet = ImageOps.exif_transpose(Image.open(os.path.join(SRC, SHEET))).convert("RGB")
    for row, (top, bottom) in enumerate(SHEET_ROWS):
        for col, (left, right) in enumerate(SHEET_COLS):
            panel = sheet.crop((left, top, right + 1, bottom + 1))
            write(SHEET_NAMES[row][col], panel, True, tally)

    # Already cut and graded for the archive, and small. Grading a second time
    # would compound the wash, and there is nothing to gain by resizing them.
    for name, source in CARRIED:
        im = ImageOps.exif_transpose(Image.open(os.path.join(ARCHIVE, source))).convert("RGB")
        write(name, im, False, tally)

    # These are already web-sized tile renditions. Their full copies stay on
    # Drive and are only requested after a visitor opens one, so do not create
    # unreferenced local "full" duplicates here.
    cultural_tile_kb = 0
    for name in CULTURAL_TILES:
        source = os.path.join(CULTURAL, f"{name}.jpg")
        target = os.path.join(OUT, "thumbs", f"{name}.jpg")
        shutil.copyfile(source, target)
        tile_kb = os.path.getsize(target) // 1024
        cultural_tile_kb += tile_kb
        print(f"  {name:<16} Drive full       tile {tile_kb:>3} KB")

    print(f"  {len(tally) + len(CULTURAL_TILES)} photographs -> assets/img/arts/  "
          f"{sum(k for k, _ in tally)/1024:.1f} MB full, "
          f"{sum(t for _, t in tally) + cultural_tile_kb} KB of tiles")


if __name__ == "__main__":
    main()
