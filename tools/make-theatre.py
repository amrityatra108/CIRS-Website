#!/usr/bin/env python3
"""Cut the photographs and video stills for the CIRS Theatre page.

    python3 tools/make-theatre.py            everything that is missing
    python3 tools/make-theatre.py --force    everything, again

Reads tools/theatre.py and writes assets/img/theatre/:

    <name>-800.webp  <name>-1600.webp    every photograph (portraits 640/1280)
    <name>-2400.webp                     full-bleed photographs as well
    yt/<video id>.webp                   the class-presentation thumbnails

The camera originals are 24 to 38 megapixels and live on the school's Google
Drive, not in this repository: forty of them would be half a gigabyte, and
assets/source/ is already the size it should be. So the originals are asked
for at the largest size the page uses, through Drive's own image endpoint,
which applies the camera's rotation. The files must stay shared by link for
this to work; a file that has been made private fails loudly here rather
than dropping out of the page.

Nothing is graded. A stage photograph's colour is the lighting designer's,
and it is kept as it was lit. The only change is size, and a light sharpen
to recover what the downscale softens.

YouTube's thumbnails are copied rather than hot-linked, as the fonts and the
motion libraries are: the page then depends on no third party to draw.
"""

import io
import os
import sys
import urllib.request

from PIL import Image, ImageFilter, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theatre

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, theatre.DIR)
UA = {"User-Agent": "Mozilla/5.0"}
FORCE = "--force" in sys.argv
QUALITY = 78


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=120).read()


def drive_image(file_id, width):
    data = fetch(f"https://drive.google.com/thumbnail?id={file_id}&sz=w{width}")
    im = Image.open(io.BytesIO(data))
    return ImageOps.exif_transpose(im).convert("RGB")


widths = theatre.widths


def save(im, width, dest):
    if im.width > width:
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=45, threshold=2))
    im.save(dest, "WEBP", quality=QUALITY, method=6)
    return os.path.getsize(dest)


def photographs():
    total = 0
    for where, p in theatre.all_photos():
        ws = widths(p)
        dests = [os.path.join(OUT, f"{p['name']}-{w}.webp") for w in ws]
        if not FORCE and all(os.path.exists(d) for d in dests):
            continue
        im = drive_image(p["drive"], max(ws))
        got = []
        for w, d in zip(ws, dests):
            total += save(im, w, d)
            got.append(w)
        print(f"  {where:12s} {p['name']:28s} {p['file']:14s} {im.size[0]}x{im.size[1]} -> {got}")
    return total


def thumbnails():
    os.makedirs(os.path.join(OUT, "yt"), exist_ok=True)
    recent = {v["id"] for v in theatre.CLASS_RECENT}
    for vid in theatre.youtube_thumbs():
        dest = os.path.join(OUT, "yt", f"{vid}.webp")
        if not FORCE and os.path.exists(dest):
            continue
        im = None
        for name in ("maxresdefault", "sddefault", "hqdefault"):
            try:
                im = Image.open(io.BytesIO(fetch(f"https://i.ytimg.com/vi/{vid}/{name}.jpg"))).convert("RGB")
                break
            except Exception:
                continue
        if im is None:
            raise SystemExit(f"make-theatre: no thumbnail for {vid}")
        # sd and hq thumbnails are 4:3 with the 16:9 frame letterboxed in them
        w, h = im.size
        th = round(w * 9 / 16)
        if th < h:
            top = (h - th) // 2
            im = im.crop((0, top, w, top + th))
        width = 640 if vid in recent else 320
        im = im.resize((width, round(width * 9 / 16)), Image.LANCZOS)
        im.save(dest, "WEBP", quality=80, method=6)
        print(f"  yt {vid} from {name} {w}x{h}")


def main():
    os.makedirs(OUT, exist_ok=True)
    total = photographs()
    thumbnails()
    # Anything in the folder the manifest no longer names is removed, so the
    # orphan check in tools/check-links.py stays meaningful.
    keep = {f"{p['name']}-{w}.webp" for _, p in theatre.all_photos() for w in widths(p)}
    for f in os.listdir(OUT):
        if f.endswith(".webp") and f not in keep:
            os.remove(os.path.join(OUT, f))
            print(f"  removed {f}")
    for f in os.listdir(os.path.join(OUT, "yt")):
        if f[:-5] not in theatre.youtube_thumbs():
            os.remove(os.path.join(OUT, "yt", f))
            print(f"  removed yt/{f}")
    if total:
        print(f"  wrote {total / 1e6:.1f} MB of photographs")


if __name__ == "__main__":
    main()
