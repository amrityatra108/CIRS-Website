#!/usr/bin/env python3
"""Cut the bulletin's photographs out of Chinmaya Sakshi, October 2026.

The issue is a 26-page Canva design the school exported as a PDF. It is not
in the repository. Each photograph is taken from the PDF as the image object
that was placed on its page, so it is the photograph at the resolution the
school supplied, not a render of the page with its borders and lettering.
tools/sakshi.py names every one by page and object number.

    python3 tools/make-sakshi.py "path/to/Anand Utsav Bulletin.pdf"

The path can also be given as CIRS_SAKSHI_PDF. Needs PyMuPDF and Pillow.

Writes
    assets/img/news/sakshi/<slug>-<n>.webp      1920px wide at most, and a
                                                720px cut of each lead
    assets/img/news/sakshi/hero-<name>-<w>.webp  the two News hero crops
    assets/img/council/<group>-{800,1600}.webp   the Student Council photographs

Nothing is enlarged: an image the school supplied at 768px stays 768px.
"""
import io
import os
import sys

import pymupdf
from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pymupdf.TOOLS.mupdf_display_errors(False)

MAX_WIDTH = 1920

# The News hero shows a 1200x620 frame. These are the parts of two photographs
# that make one: (left, top, right, bottom) as fractions of the whole.
HERO = {
    "cfore": ((2126), (0.0, 0.20, 1.0, 0.975)),
    "council": ((2236), (0.0, 0.16, 1.0, 0.94)),
}


def load_module():
    # sakshi reads the finished images' sizes when it is imported, so read its
    # data without importing it before the images exist.
    src = open(os.path.join(ROOT, "tools", "sakshi.py"), encoding="utf-8").read()
    src = src.replace("\n_prepare()\n", "\n")
    ns = {"__file__": os.path.join(ROOT, "tools", "sakshi.py"), "__name__": "sakshi_data"}
    exec(compile(src, "sakshi.py", "exec"), ns)
    return ns


def extract(doc, xref):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)
    if pix.n - pix.alpha >= 4 or pix.colorspace and pix.colorspace.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = Image.open(io.BytesIO(pix.tobytes("png")))
    return ImageOps.exif_transpose(im).convert("RGB")


def save(im, path, width, quality=82):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    im.save(full, "WEBP", quality=quality, method=6)
    return im.size


def main():
    pdf = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CIRS_SAKSHI_PDF")
    if not pdf:
        sys.exit(__doc__)
    doc = pymupdf.open(pdf)
    ns = load_module()
    articles, groups, council_group = ns["ARTICLES"], ns["GROUPS"], ns["COUNCIL_GROUP"]
    photo_path = ns["photo_path"]
    council_path = ns["council_path"]

    count = 0
    for art in articles:
        for n, (page, xref, _alt) in enumerate(art["photos"], 1):
            im = extract(doc, xref)
            size = save(im, photo_path(art["slug"], n), MAX_WIDTH)
            if n == 1 and im.width > 720:
                save(im, photo_path(art["slug"], 1, 720), 720)
            count += 1
            print(f'{art["slug"]}-{n}  p{page} x{xref}  {im.width}x{im.height} -> {size[0]}x{size[1]}')

    council = [(key, g["photo"][1]) for key, g in groups.items()]
    council.append(("council", council_group["photo"][1]))
    for key, xref in council:
        im = extract(doc, xref)
        for width in (1600, 800):
            size = save(im, council_path(key, width), width)
        count += 1
        print(f'council/{key}  x{xref}  {im.width}x{im.height} -> {size[0]}x{size[1]}')

    for name, (xref, (l, t, r, b)) in HERO.items():
        im = extract(doc, xref)
        w, h = im.size
        crop = im.crop((round(l * w), round(t * h), round(r * w), round(b * h)))
        # 1200x620, the frame the News hero uses.
        crop = ImageOps.fit(crop, (1200, 620), Image.LANCZOS, centering=(0.5, 0.5))
        for width in (1200, 720):
            save(crop, f"assets/img/news/sakshi/hero-{name}-{width}.webp", width)
        print(f"hero-{name}  x{xref}")
        count += 1
    print(count, "photographs")


if __name__ == "__main__":
    main()
