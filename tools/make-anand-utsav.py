#!/usr/bin/env python3
"""Cut the Anand Utsav 2026 report's photographs into assets/img/news/anand-utsav/.

The cover is a photograph from the school's Drive, and the seventeen after it
are published with Chinmaya Mission's account of the festival. They are large
(up to 8192 px wide, about 31 MB in all) and are not kept in the repository;
tools/anandutsav.py records where each one is, and this fetches them and cuts:

    anand-utsav-2026-1.webp          the cover, whole, 1400 px wide
    anand-utsav-2026-2..18.webp      the rest, 1000 px wide
    anand-utsav-2026-hero-1200.webp  the cover cropped to 1200x620 for the News carousel
    anand-utsav-2026-hero-720.webp   and at 720x372

    python3 tools/make-anand-utsav.py [folder of the originals]

Given a folder, it reads each original from it, named by its id there (the id,
then its extension), instead of fetching, so a second run need not download
again. Needs Pillow.
"""
import io
import os
import sys
import urllib.request

from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEAD_WIDTH = 1400
GALLERY_WIDTH = 1000
HERO = (1200, 620)
# The carousel's crop of the cover, as fractions of its size: the span it keeps
# from the left, and where it starts from the top. The cover is a wide shot of a
# stage with a dark ceiling above it; the crop is wider than 3:2, so it keeps
# the screen, the row of performers and the audience below, and drops the
# ceiling and the edges.
HERO_X = (0.05, 0.95)
HERO_TOP = 0.30


def load_module():
    # anandutsav reads the finished images' sizes when it is imported, so read
    # its photo list without importing it before the images exist.
    src = open(os.path.join(ROOT, "tools", "anandutsav.py"), encoding="utf-8").read()
    src = src.replace("\n_prepare()\n", "\n")
    ns = {"__file__": os.path.join(ROOT, "tools", "anandutsav.py")}
    exec(compile(src, "anandutsav.py", "exec"), ns)
    return ns


def original(ns, n, folder):
    if folder:
        ident = ns["PHOTOS"][n - 1][1]
        names = [name for name in os.listdir(folder) if name.rsplit(".", 1)[0] == ident]
        if not names:
            sys.exit(f"{ident}: not in {folder}")
        with open(os.path.join(folder, names[0]), "rb") as f:
            data = f.read()
    else:
        request = urllib.request.Request(ns["photo_url"](n), headers={"User-Agent": "cirs-site-build"})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
    return ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")


def save(im, path, width=None):
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    im.save(full, "WEBP", quality=80, method=6)
    return im.size


def hero_crop(im, size):
    w, h = size
    left, right = round(im.width * HERO_X[0]), round(im.width * HERO_X[1])
    crop_h = round((right - left) * h / w)
    top = min(round(im.height * HERO_TOP), im.height - crop_h)
    return im.crop((left, top, right, top + crop_h)).resize(size, Image.LANCZOS)


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    ns = load_module()
    count = len(ns["PHOTOS"])
    for n in range(1, count + 1):
        im = original(ns, n, folder)
        size = save(im, ns["photo_path"](n), LEAD_WIDTH if n == 1 else GALLERY_WIDTH)
        print(f"anand-utsav-2026-{n}  from {im.width}x{im.height}  to {size[0]}x{size[1]}")
        if n == 1:
            for width in (1200, 720):
                target = (width, round(width * HERO[1] / HERO[0]))
                save(hero_crop(im, HERO).resize(target, Image.LANCZOS), ns["hero_path"](width))
                print(f"anand-utsav-2026-hero-{width}  {target[0]}x{target[1]}")
    print(count, "photographs")


if __name__ == "__main__":
    main()
