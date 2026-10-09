#!/usr/bin/env python3
"""Cut the Anand Utsav 2026 report's photographs into assets/img/news/anand-utsav/.

The cover is the school's "CIRS News Page Header" design, exported from its
Canva and kept as the master at assets/source/anand-utsav/header.png. The
seventeen after it are published with Chinmaya Mission's account of the
festival. They are large (up to 8192 px wide, about 31 MB in all) and are not
kept in the repository; tools/anandutsav.py records where each one is, and this
fetches them and cuts:

    anand-utsav-2026-1.webp          the cover, whole, 1400 px wide
    anand-utsav-2026-2..18.webp      the rest, 1000 px wide
    anand-utsav-2026-hero-1200.webp  the cover cropped to 1200x1000 for the News carousel
    anand-utsav-2026-hero-720.webp   and at 720x600

    python3 tools/make-anand-utsav.py [--cover] [folder of the originals]

Given a folder, it reads each original from it, named by its id there (the id,
then its extension), instead of fetching, so a second run need not download
again. With --cover it cuts only the cover and its carousel crops, from the
master, and fetches nothing. Needs Pillow.
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
HERO = (1200, 1000)
# The carousel's crop of the cover, as fractions of its size: the span it keeps
# from the left, and where it starts from the top. The cover is a 16:9 design of
# three photographs side by side, but the carousel's frame is close to square (a
# little over 1.2:1 beside the text, and 1:1 on a phone) and the browser fills it
# from the middle. So the crop is 1.2:1 and full height, and its span is chosen
# so that nobody in the frame is cut through: the whole of the stage and of the
# student at prayer, and a part of the walkers at the left.
HERO_X = (0.23, 0.905)
HERO_TOP = 0.0


def load_module():
    # anandutsav reads the finished images' sizes when it is imported, so read
    # its photo list without importing it before the images exist.
    src = open(os.path.join(ROOT, "tools", "anandutsav.py"), encoding="utf-8").read()
    src = src.replace("\n_prepare()\n", "\n")
    ns = {"__file__": os.path.join(ROOT, "tools", "anandutsav.py")}
    exec(compile(src, "anandutsav.py", "exec"), ns)
    return ns


def original(ns, n, folder):
    if ns["PHOTOS"][n - 1][0] == "canva":
        # A design, not a file at an address: its export is kept in the repository.
        with open(os.path.join(ROOT, ns["COVER_MASTER"]), "rb") as f:
            data = f.read()
    elif folder:
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
    args = [a for a in sys.argv[1:] if a != "--cover"]
    cover_only = len(args) != len(sys.argv) - 1
    folder = args[0] if args else None
    ns = load_module()
    count = len(ns["PHOTOS"])
    for n in range(1, (1 if cover_only else count) + 1):
        im = original(ns, n, folder)
        size = save(im, ns["photo_path"](n), LEAD_WIDTH if n == 1 else GALLERY_WIDTH)
        print(f"anand-utsav-2026-{n}  from {im.width}x{im.height}  to {size[0]}x{size[1]}")
        if n == 1:
            for width in (1200, 720):
                target = (width, round(width * HERO[1] / HERO[0]))
                save(hero_crop(im, HERO).resize(target, Image.LANCZOS), ns["hero_path"](width))
                print(f"anand-utsav-2026-hero-{width}  {target[0]}x{target[1]}")
    print(1 if cover_only else count, "photographs")


if __name__ == "__main__":
    main()
