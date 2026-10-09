#!/usr/bin/env python3
"""Derive the Crossroads cover thumbnails the archive page ships.

The school's own cover scans (JPEG, or PNG as some issues arrive) live in
assets/source/crossroads/ at print
resolution — 20 MB across the run, and never deployed. Two smaller copies
are, both cropped to the 5:7 the page draws them in:

    assets/img/crossroads/issue-NN.jpg        720x1008, the archive card
    assets/img/crossroads/wall/issue-NN.jpg   300x420, the hero wall

The wall shows every cover at once behind a heavy scrim, so its tiles are
sized for the column they drift through rather than for looking at — the
whole run has to arrive with the hero, and the archive copies would be
3.6 MB of it.

An issue named in crossroads.WALL_LEAVES_OUT has its card but no wall copy: the
owner left it off the wall, and an unreferenced file would fail the link check.

Run it after adding a scan; tools/build-site.py reads the output.
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crossroads

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/source/crossroads"
OUT = ROOT / "assets/img/crossroads"
WALL = OUT / "wall"
SIZE = (720, 1008)          # 5:7, the card's aspect-ratio
WALL_SIZE = (300, 420)      # the same ratio, at the width a hero column draws
QUALITY = 82
WALL_QUALITY = 68


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    WALL.mkdir(parents=True, exist_ok=True)
    made = 0
    scans = sorted(list(SRC.glob("issue-*.jpg")) + list(SRC.glob("issue-*.png")))
    for path in scans:
        name = path.stem + ".jpg"      # a PNG scan is served as a JPEG all the same
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        # Cover-fit from the top: a magazine cover's masthead is at the
        # head of the page, and that is the part worth keeping when the
        # scan is taller than 5:7.
        card = ImageOps.fit(im, SIZE, Image.LANCZOS, centering=(0.5, 0.32))
        card.save(OUT / name, "JPEG", quality=QUALITY, optimize=True,
                  progressive=True)
        if int(path.stem.split("-")[1]) in crossroads.WALL_LEAVES_OUT:
            (WALL / name).unlink(missing_ok=True)
        else:
            card.resize(WALL_SIZE, Image.LANCZOS).save(
                WALL / name, "JPEG", quality=WALL_QUALITY, optimize=True,
                progressive=True)
        made += 1

    for label, folder in (("cards", OUT), ("wall", WALL)):
        total = sum(p.stat().st_size for p in folder.glob("*.jpg"))
        count = len(list(folder.glob("*.jpg")))
        print(f"{count} {label:5s} -> {folder.relative_to(ROOT)}  ({total/1024:.0f} KB)")


if __name__ == "__main__":
    main()
