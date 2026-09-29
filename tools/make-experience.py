#!/usr/bin/env python3
"""Cut the photographs for The CIRS experience.

    python3 tools/make-experience.py            everything that is missing
    python3 tools/make-experience.py --force    everything, again

Reads PHOTOS in tools/experience.py and writes assets/img/experience/:

    <key>-<crop>-<width>.webp      e.g. hero-wide-1600.webp, night-tall-1080.webp

Most originals are camera files in assets/source/. Two are on the school's
Google Drive and are not in this repository (the dining-hall lunches: nothing
in assets/source/ shows a meal); they are asked for through Drive's own image
endpoint at the largest size the page uses, as tools/make-theatre.py does,
and must stay shared by link for this to work.

Nothing is graded. The page lays its own purple scrim over the timeline
photographs, and the photographs keep the colour they were taken in. The only
change is the crop, the size and a light sharpen after the downscale. A cut
is never enlarged past the pixels its original has.
"""

import io
import os
import sys
import urllib.request

from PIL import Image, ImageFilter, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import experience

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/source")
OUT = os.path.join(ROOT, experience.DIR)
FORCE = "--force" in sys.argv
QUALITY = 80
UA = {"User-Agent": "Mozilla/5.0"}


def original(p):
    if "src" in p:
        im = Image.open(os.path.join(SRC, p["src"]))
    else:
        url = f"https://drive.google.com/thumbnail?id={p['drive']}&sz=w2400"
        data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        im = Image.open(io.BytesIO(data))
    return ImageOps.exif_transpose(im).convert("RGB")


def cut(im, ratio, fx, fy):
    """The largest frame of this ratio the original holds, centred on the focal point."""
    if im.width / im.height > ratio:
        w, h = round(im.height * ratio), im.height
    else:
        w, h = im.width, round(im.width / ratio)
    x = min(max(round(im.width * fx - w / 2), 0), im.width - w)
    y = min(max(round(im.height * fy - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))


def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for key, p in experience.PHOTOS.items():
        wanted = [(crop, spec) for crop, spec in p["crops"].items()
                  if FORCE or not all(os.path.exists(os.path.join(ROOT, f))
                                      for f, _, _ in experience.files(key, crop))]
        if not wanted:
            continue
        im = original(p)
        for crop, (ratio, fx, fy, widths) in wanted:
            frame = cut(im, ratio, fx, fy)
            for path, w, h in experience.files(key, crop):
                if w > frame.width:
                    sys.exit(f"make-experience: {key}-{crop} asks for {w}px; "
                             f"the original holds {frame.width}px")
                out = frame.resize((w, h), Image.LANCZOS)
                out = out.filter(ImageFilter.UnsharpMask(radius=0.8, percent=40, threshold=2))
                out.save(os.path.join(ROOT, path), "WEBP", quality=QUALITY, method=6)
                kb = os.path.getsize(os.path.join(ROOT, path)) // 1024
                total += kb
                print(f"  {path:<52} {w}x{h:<5} {kb:>4} KB")
    print(f"  {total} KB written")


if __name__ == "__main__":
    main()
