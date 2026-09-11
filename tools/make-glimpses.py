#!/usr/bin/env python3
"""Build the thumbnails for the Glimpses of CIRS collage on the home page.

    assets/img/glimpses/g01.jpg ... gNN.jpg

Unlike every other derived image on this site these are NOT graded towards
the purple. The collage exists to be the one loud, colourful thing on the
page — a wall of the school's own photographs — and a duotone would turn it
into wallpaper. They get a small lift in saturation and contrast instead.

Square, because the mosaic crops them to a dozen different shapes with
object-fit and a single source has to survive all of them.

Anything whose subject is a logo, a banner or signage is left out.

    python3 tools/make-glimpses.py
"""

import glob
import os
import shutil

from PIL import Image, ImageEnhance, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/source")
OUT = os.path.join(ROOT, "assets/img/glimpses")

SIZE = 440
QUALITY = 76
SATURATION = 1.12
CONTRAST = 1.04

# Subject is a banner or signage rather than the school, so it reads as a
# logo in a tile that size.
EXCLUDE = {
    "4.JPG",                  # a TEDx backdrop fills the frame
}


def main():
    files = sorted(
        p for p in glob.glob(os.path.join(SRC, "*"))
        if p.lower().endswith((".jpg", ".jpeg", ".png"))
        and os.path.basename(p) not in EXCLUDE
    )
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    total = 0
    for i, p in enumerate(files, 1):
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        s = max(SIZE / im.width, SIZE / im.height)
        im = im.resize((max(SIZE, round(im.width * s)), max(SIZE, round(im.height * s))),
                       Image.LANCZOS)
        x, y = (im.width - SIZE) // 2, (im.height - SIZE) // 2
        im = im.crop((x, y, x + SIZE, y + SIZE))
        im = ImageEnhance.Color(im).enhance(SATURATION)
        im = ImageEnhance.Contrast(im).enhance(CONTRAST)
        out = os.path.join(OUT, f"g{i:02d}.jpg")
        im.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        total += os.path.getsize(out)

    print(f"  {len(files)} tiles -> assets/img/glimpses/  {total/1e6:.2f} MB "
          f"({total/len(files)/1024:.0f} KB each, {SIZE}px)")


if __name__ == "__main__":
    main()
