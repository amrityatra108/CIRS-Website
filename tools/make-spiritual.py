#!/usr/bin/env python3
"""Cut the Spiritual Life photographs for the web.

Reads camera originals in assets/source/ (never deployed) and writes WebP
cuts to assets/img/spiritual/. Every photograph is one of the school's own.
Captions on the page describe only what each frame shows; none of these files
records the occasion it was taken at, so the page does not attribute any of
them to a named practice. The photographs whose occasion *is* recorded —
the Gayathri Havan of 7 April 2025, the festival poojas, Seva Week — are
used from where they already live (assets/img/news-archive, festivals, news)
and are not cut again here.

    name: (original, (w, h) of the crop at its largest, focal point x, y, widths)

Each cut is taken at the crop's aspect ratio around the focal point, then
written at each width. Metadata is not carried over: no EXIF reaches the web.

    python3 tools/make-spiritual.py
"""

import os
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "assets", "source")
OUT = os.path.join(ROOT, "assets", "img", "spiritual")
QUALITY = 74

CUTS = {
    # The opening: students seated in the amphitheatre after dark. A wide cut
    # for landscape windows and a tall one that keeps the rings on a phone.
    "hero":         ("IMG_2474.JPG", (2400, 1350), (0.50, 0.55), (1280, 1920, 2400)),
    "hero-tall":    ("IMG_2474.JPG", (900, 1400), (0.46, 0.60), (600, 900)),
    # Morning prayer in the hall (the frame Why CIRS captions as such).
    "prayer-hall":  ("IMG_1686.JPG", (1600, 1067), (0.46, 0.50), (720, 1280)),
    "prayer-lead":  ("IMG_1691.JPG", (1600, 1067), (0.55, 0.50), (720, 1280)),
    "palms":        ("0C9A4097.JPG", (1000, 1250), (0.52, 0.45), (640, 1000)),
    "palms-girl":   ("0C9A4095.JPG", (1000, 1250), (0.50, 0.42), (640, 1000)),
    "amphi-lead":   ("IMG_2480.JPG", (1600, 1067), (0.50, 0.50), (720, 1280)),
    "amphi-close":  ("IMG_2449.JPG", (1600, 1067), (0.50, 0.50), (720, 1280)),
    "stage-pooja":  ("IMG_4759.JPG", (1600, 1067), (0.50, 0.55), (720, 1280)),
    "fire-hall":    ("CRS00635.JPG", (1600, 1000), (0.45, 0.55), (720, 1280)),
    "procession":   ("IMG_7712.JPG", (1600, 1067), (0.40, 0.50), (720, 1280)),
}


def crop(im, size, focus):
    """The largest box of the wanted aspect, centred as near the focus as fits."""
    w, h = im.size
    tw, th = size
    if w / h > tw / th:
        ch, cw = h, round(h * tw / th)
    else:
        cw, ch = w, round(w * th / tw)
    x = min(max(round(w * focus[0] - cw / 2), 0), w - cw)
    y = min(max(round(h * focus[1] - ch / 2), 0), h - ch)
    return im.crop((x, y, x + cw, y + ch))


def main():
    os.makedirs(OUT, exist_ok=True)
    keep = set()
    for name, (src, size, focus, widths) in CUTS.items():
        path = os.path.join(SRC, src)
        if not os.path.exists(path):
            sys.exit(f"missing original: {path}")
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        box = crop(im, size, focus)
        for x in widths:
            y = round(x * size[1] / size[0])
            out = f"{name}-{x}.webp"
            box.resize((x, y), Image.LANCZOS).save(
                os.path.join(OUT, out), "WEBP", quality=QUALITY, method=6)
            keep.add(out)
            print(f"  write  assets/img/spiritual/{out} ({x}x{y})")
    for f in os.listdir(OUT):
        if f not in keep:
            os.remove(os.path.join(OUT, f))
            print(f"  remove assets/img/spiritual/{f}")


if __name__ == "__main__":
    main()
