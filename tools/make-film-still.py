#!/usr/bin/env python3
"""Build the still that fills the film window on the home page.

    assets/img/film-still.jpg

The window already carries a scrim and a play button over this image, so the
grade here is deliberately lighter than the honeycomb's: enough to belong to
the purple palette, not so much that the photograph stops being one. A heavy
duotone behind a gold play button reads as a texture rather than a place.

    python3 tools/make-film-still.py
"""

import os
import sys

from PIL import Image, ImageEnhance, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "assets/source/IMG_2051.JPG")
OUT = os.path.join(ROOT, "assets/img/film-still.jpg")

W, H = 1600, 900          # the window is 16/9 and never wider than 920px
SHADOW = (34, 24, 54)     # the palette's purple, in the shadows
HIGHLIGHT = (238, 226, 206)
KEEP_COLOUR = 0.55        # far more of the original than the honeycomb keeps
WASH = (30, 22, 40)
WASH_ALPHA = 0.12


def cover(im, w, h):
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * scale)), max(h, int(im.height * scale))),
                   Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def grade(im):
    grey = ImageEnhance.Contrast(im.convert("L")).enhance(1.08)
    ramp = []
    for ch in range(3):
        lo, hi = SHADOW[ch], HIGHLIGHT[ch]
        ramp += [int(lo + (hi - lo) * (i / 255)) for i in range(256)]
    toned = Image.blend(grey.convert("RGB").point(ramp), im, KEEP_COLOUR)
    return Image.blend(toned, Image.new("RGB", im.size, WASH), WASH_ALPHA)


def main():
    if not os.path.exists(SOURCE):
        sys.exit(f"make-film-still: {SOURCE} is missing")
    im = ImageOps.exif_transpose(Image.open(SOURCE)).convert("RGB")
    out = grade(cover(im, W, H))
    out.save(OUT, "JPEG", quality=86, optimize=True, progressive=True)
    print(f"  write  assets/img/film-still.jpg  {os.path.getsize(OUT)//1024} KB  {W}x{H}")


if __name__ == "__main__":
    main()
