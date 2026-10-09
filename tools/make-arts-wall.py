#!/usr/bin/env python3
"""Cut the photographs for the CIRS Cultural Gallery wall.

    assets/img/arts/<name>.webp          the photograph, opened from a tile
    assets/img/arts/thumbs/<name>.webp   the copy the moving tile carries
    tools/culture-gallery.json           what was written, for tools/artswall.py

The wall holds every photograph at once and moves them, so the tile copies
have to be small: a hundred tiles at full size is a hundred megabytes moving
under a finger. The full copy is only fetched when somebody opens a tile.

Every photograph goes through the one grade in tools/gallerygrade.py, so that
a stage, a festival, a classroom and a child's painting from a dozen sources
read as one wall. The grade is decided photograph by photograph (see that
module), and the paintings and drawings get the correction without the tone.

Three families feed it:

  * The wall's original photographs, listed here: camera originals in
    assets/source/ (cropped and graded), the SPIC MACAY contact sheet (cut
    back into its six), the photographs the designer chose for the archive
    (assets/source/archive/), and the 48 CIRS Cultural Gallery tiles
    (assets/source/cultural-gallery/), which are Drive renditions at most 520px
    on a side. Those 48 have no larger copy in this repository: their opened
    1600px photographs stay on the school's Drive, so only their tiles are cut.
  * Everything else the school's pages show of its arts, music, theatre,
    festivals and students' own making, listed in tools/culturegallery.py:
    each page's own record of its photographs, taken as it stands. Those are
    cut from the best copy in the repository.
  * SPIC MACAY.jpg is a contact sheet of six photographs from the society's
    visiting-artist concerts. They are visiting professional musicians and
    dancers, not students, and the captions say so.

Nothing is upscaled. A photograph that arrived small stays small.

    python3 tools/make-arts-wall.py
"""

import concurrent.futures
import json
import os
import shutil
import sys
import time

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import culturegallery  # noqa: E402
import gallerygrade  # noqa: E402

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "assets/source")
ARCHIVE = os.path.join(ROOT, "assets/source/archive")
CULTURAL = os.path.join(ROOT, "assets/source/cultural-gallery")
OUT = os.path.join(ROOT, "assets/img/arts")
MANIFEST = os.path.join(HERE, "culture-gallery.json")

FULL = 1440           # long edge of the copy a tile opens
THUMB = 480           # long edge of the copy a tile carries
Q_FULL, Q_THUMB = 72, 66

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

# Photographs the designer had already chosen for the archive, at the size
# they arrived: these are the only copies in the repository. The paintings are
# graded as paintings.
CARRIED = [
    ("stage",  "stage.jpg",   "photo"),
    ("dance",  "dancers.jpg", "photo"),
    ("paint1", "paint1.jpg",  "art"),
    ("paint2", "paint2.jpg",  "art"),
    ("paint3", "paint3.jpg",  "art"),
    ("paint4", "paint4.jpg",  "art"),
    ("paint5", "paint5.jpg",  "art"),
]

# drive-31 was the amphitheatre photograph a second time; it has no tile.
CULTURAL_TILES = [f"drive-{index:02d}" for index in range(1, 49) if index != 31]


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


def jobs():
    """Every photograph to cut, in wall order: the originals, then the rest."""
    out = []
    for name, source, focal in CAMERA:
        out.append({"name": name, "src": os.path.join(SRC, source), "focal": focal})
    for row, (top, bottom) in enumerate(SHEET_ROWS):
        for col, (left, right) in enumerate(SHEET_COLS):
            out.append({"name": SHEET_NAMES[row][col], "src": os.path.join(SRC, SHEET),
                        "box": (left, top, right + 1, bottom + 1)})
    for name, source, kind in CARRIED:
        out.append({"name": name, "src": os.path.join(ARCHIVE, source), "kind": kind})
    for name in CULTURAL_TILES:
        out.append({"name": name, "src": os.path.join(CULTURAL, f"{name}.jpg"), "thumb_only": True})
    for item in culturegallery.collect():
        out.append({"name": item["name"], "src": os.path.join(ROOT, item["src"].replace("/", os.sep)),
                    "kind": item["kind"], "new": item})
    return out


def cut(job):
    """Cut one photograph. Runs in a worker process."""
    im = Image.open(job["src"])
    if "box" not in job:
        # A camera original is 8192px; the decoder can hand back a half or a
        # quarter of it for nothing, which is all the grade will see. (Not for
        # the contact sheet, whose panels are measured in its own pixels.)
        im.draft("RGB", (FULL * 2, FULL * 2))
    im = ImageOps.exif_transpose(im).convert("RGB")
    if "box" in job:
        im = im.crop(job["box"])
    if "focal" in job:
        im = trim(im, job["focal"])
    if job.get("thumb_only"):
        # Drive's renditions carry a hairline of white on one or two edges.
        im = im.crop((2, 2, im.width - 2, im.height - 2))
    kind = job.get("kind", "photo")
    name = job["name"]
    graded = gallerygrade.grade(gallerygrade.fit(im, FULL), kind)

    result = {"name": name}
    if not job.get("thumb_only"):
        full = gallerygrade.sharpen(graded, 0.5)
        full.save(os.path.join(OUT, f"{name}.webp"), "WEBP", quality=Q_FULL, method=6)
        result.update(w=full.width, h=full.height,
                      kb=os.path.getsize(os.path.join(OUT, f"{name}.webp")) // 1024)
    tile = gallerygrade.sharpen(gallerygrade.fit(graded, THUMB), 0.6)
    tile.save(os.path.join(OUT, "thumbs", f"{name}.webp"), "WEBP", quality=Q_THUMB, method=6)
    result["tile_kb"] = os.path.getsize(os.path.join(OUT, "thumbs", f"{name}.webp")) // 1024
    return result


def main():
    todo = jobs()
    missing = [j["src"] for j in todo if not os.path.exists(j["src"])]
    if missing:
        sys.exit("make-arts-wall: not found — " + ", ".join(os.path.relpath(m, ROOT) for m in missing))

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "thumbs"))

    started = time.time()
    results = {}
    workers = max(1, min(8, (os.cpu_count() or 2) - 1))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        for n, r in enumerate(pool.map(cut, todo, chunksize=4), 1):
            results[r["name"]] = r
            if n % 40 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)}  {time.time() - started:.0f}s", flush=True)

    full_kb = sum(r.get("kb", 0) for r in results.values())
    tile_kb = sum(r["tile_kb"] for r in results.values())
    print(f"  {len(results)} photographs -> assets/img/arts/  "
          f"{full_kb / 1024:.1f} MB full, {tile_kb / 1024:.1f} MB of tiles")

    # What tools/artswall.py reads: only the photographs this module adds. The
    # original seventy-five are written out by hand in artswall.py, with the
    # captions they have always had.
    record = []
    for j in todo:
        item = j.get("new")
        if not item:
            continue
        r = results[j["name"]]
        record.append({"name": item["name"], "group": item["group"], "cat": item["cat"],
                       "title": item["title"], "desc": item["desc"], "weight": item["weight"],
                       "w": r["w"], "h": r["h"], "src": item["src"]})
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump({"photographs": record}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"  {len(record)} recorded in tools/culture-gallery.json")


if __name__ == "__main__":
    main()
