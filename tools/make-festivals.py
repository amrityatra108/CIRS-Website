#!/usr/bin/env python3
"""Cut the CIRS Festivals photographs for the web.

Reads the originals in assets/source/festivals (2000px on the long edge,
already turned the right way up; see the list and provenance in
tools/festivals.py) and writes WebP cuts to assets/img/festivals:

    <name>-640.webp     tiles, the opening strip and narrow screens
    <name>-1280.webp    chapters and the viewer
    <name>-1920.webp    the few photographs that run the full width

A portrait original is narrower than 1280, so its largest cut is its own
width rather than an enlargement. The sizes written are recorded in
tools/festivals-images.json, which is all tools/festivals.py reads — so the
site build itself never needs Pillow. Metadata is not carried over: no EXIF,
and so no camera serial numbers or locations, reaches the web.

    python3 tools/make-festivals.py
"""

import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import festivals  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "festivals")
OUT = os.path.join(ROOT, "assets", "img", "festivals")
MANIFEST = os.path.join(HERE, "festivals-images.json")

# Photographs laid across the whole window somewhere on the page.
FULL = {"ganesh-lake", "holi-field", "jan-lamps", "jan-lawn", "onam-sadhya",
        "dussehra-torches"}
QUALITY = 74


def main():
    os.makedirs(OUT, exist_ok=True)
    images = {}
    for name in festivals.PHOTOS:
        path = os.path.join(SRC, name + ".jpg")
        if not os.path.exists(path):
            sys.exit(f"missing original: {path}")
        im = Image.open(path).convert("RGB")
        w, h = im.size
        wanted = [640, 1280] + ([1920] if name in FULL else [])
        widths = sorted({min(x, w) for x in wanted})
        for x in widths:
            cut = im if x == w else im.resize((x, round(h * x / w)), Image.LANCZOS)
            cut.save(os.path.join(OUT, f"{name}-{x}.webp"), "WEBP",
                     quality=QUALITY, method=6)
        images[name] = {"w": w, "h": h, "widths": widths}
    # Anything left over from an earlier list is removed, so the orphan check
    # in check-links.py never has to be taught about it.
    keep = {f"{n}-{x}.webp" for n, v in images.items() for x in v["widths"]}
    for f in os.listdir(OUT):
        if f not in keep:
            os.remove(os.path.join(OUT, f))
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump({"images": images}, f, indent=1, sort_keys=True)
        f.write("\n")
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"{len(images)} photographs, {len(keep)} files, {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
