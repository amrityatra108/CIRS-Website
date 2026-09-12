#!/usr/bin/env python3
"""Derive the Crossroads cover thumbnails the archive page ships.

The school's own cover scans live in assets/source/crossroads/ at print
resolution — 20 MB across the run, and never deployed. The archive shows
each one in a 5:7 card no wider than a few hundred pixels, so this crops
to that ratio and writes a 720x1008 copy into assets/img/crossroads/.

Run it after adding a scan; tools/build-site.py reads the output.
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/source/crossroads"
OUT = ROOT / "assets/img/crossroads"
SIZE = (720, 1008)          # 5:7, the card's aspect-ratio
QUALITY = 82


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for path in sorted(SRC.glob("issue-*.jpg")):
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        # Cover-fit from the top: a magazine cover's masthead is at the
        # head of the page, and that is the part worth keeping when the
        # scan is taller than 5:7.
        im = ImageOps.fit(im, SIZE, Image.LANCZOS, centering=(0.5, 0.32))
        im.save(OUT / path.name, "JPEG", quality=QUALITY, optimize=True,
                progressive=True)
        made += 1
    total = sum(p.stat().st_size for p in OUT.glob("*.jpg"))
    print(f"{made} covers -> {OUT.relative_to(ROOT)}  ({total/1024:.0f} KB)")


if __name__ == "__main__":
    main()
