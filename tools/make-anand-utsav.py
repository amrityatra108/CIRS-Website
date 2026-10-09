#!/usr/bin/env python3
"""Cut the Anand Utsav 2026 report's photographs into assets/img/news/anand-utsav/.

The report's seventeen photographs are published with Chinmaya Mission's
account of the festival. They are large (up to 8192 px wide, about 26 MB in
all) and are not kept in the repository; tools/anandutsav.py records where
each one is, and this fetches them and cuts:

    anand-utsav-2026-1.webp          the lead, 1400 px wide
    anand-utsav-2026-2..17.webp      the rest, 1000 px wide
    anand-utsav-2026-hero-1200.webp  the lead cropped to 1200x620 for the News carousel
    anand-utsav-2026-hero-720.webp   and at 720x372

    python3 tools/make-anand-utsav.py [folder of the seventeen originals]

Given a folder, it reads au-00.webp ... au-16.webp from it instead of
fetching, so a second run need not download again. Needs Pillow.
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
# Where the carousel's crop starts, as a fraction of the lead's height. The
# lead is 3:2 and the crop is wider than that, so it keeps the sign and the
# row of people under it and drops the lamps above and the floor below.
HERO_TOP = 0.10


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
        with open(os.path.join(folder, f"au-{n - 1:02d}.webp"), "rb") as f:
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
    crop_h = round(im.width * h / w)
    top = min(round(im.height * HERO_TOP), im.height - crop_h)
    return im.crop((0, top, im.width, top + crop_h)).resize(size, Image.LANCZOS)


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
