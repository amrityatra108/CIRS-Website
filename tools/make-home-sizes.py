#!/usr/bin/env python3
"""Cut the smaller candidates the home page offers in a srcset.

    assets/img/glimpses/gNN.jpg      -> gNN-256.webp          (the wall's tiles)
    assets/img/hrun/<photo>.jpg      -> <photo>-<w>.webp      ("A day at CIRS")

Both sets were written for the densest screen they are shown on: the wall's
tiles are 440px squares and the run's photographs are 1000 to 1600px wide,
while a tile is never wider than 237 CSS pixels and the widest frame in the
run is 690. On an ordinary 1x or 1.25x desktop screen most of those pixels
are thrown away after being downloaded. The page names both files in a
srcset, and the browser takes the small one wherever it is enough and the
original wherever the screen is dense enough to need it.

Nothing about a photograph changes: the same crop, the same grade, the same
order, from the file already in the folder. This does not renumber or
rename anything and it is safe to run again. tools/make-glimpses.py clears
the glimpses folder, so run this after it.

    python3 tools/make-home-sizes.py
"""

import glob
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TILE = 256
TILE_QUALITY = 82

# The run's photographs the home page shows that are wide enough to be worth
# a second file, with the width of that file. A tall frame is at most 390px
# across and a wide one 690, so 600 and 960 cover them up to 1.5x density.
RUN = {
    "hrun/01-holi.jpg": 600,
    "hrun/03-campus.jpg": 960,
    "hrun/05-lab.jpg": 960,
    "hrun/06-swim.jpg": 960,
    "hrun/07-sparkler.jpg": 960,
    "hrun/08-candlelight.jpg": 960,
    "hrun/09-meditation.jpg": 960,
    "hrun/10-stage.jpg": 960,
}
RUN_QUALITY = 80


def smaller(src, width, quality):
    out = os.path.splitext(src)[0] + f"-{width}.webp"
    im = Image.open(src).convert("RGB")
    height = round(im.height * width / im.width)
    im.resize((width, height), Image.LANCZOS).save(out, "WEBP", quality=quality, method=6)
    return out


def main():
    tiles = sorted(p for p in glob.glob(os.path.join(ROOT, "assets/img/glimpses/g*.jpg"))
                   if re.fullmatch(r"g\d+\.jpg", os.path.basename(p)))
    a = b = 0
    for src in tiles:
        if Image.open(src).size != (440, 440):
            raise SystemExit(f"{os.path.basename(src)} is not the 440px square")
        out = smaller(src, TILE, TILE_QUALITY)
        a += os.path.getsize(src)
        b += os.path.getsize(out)
    print(f"  {len(tiles)} wall tiles -> gNN-{TILE}.webp  {b/1e6:.2f} MB beside {a/1e6:.2f} MB of JPEG")

    a = b = 0
    for rel, width in RUN.items():
        src = os.path.join(ROOT, "assets/img", rel)
        out = smaller(src, width, RUN_QUALITY)
        a += os.path.getsize(src)
        b += os.path.getsize(out)
    print(f"  {len(RUN)} run photographs -> <name>-<w>.webp  {b/1e6:.2f} MB beside {a/1e6:.2f} MB of JPEG")


if __name__ == "__main__":
    main()
