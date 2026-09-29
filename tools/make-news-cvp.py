#!/usr/bin/env python3
"""Cut the News articles' photographs out of the school's CVP report.

The report (October 2025 – March 2026) is a Canva document the school
exported as a 275-page PDF. It is not in the repository. Each photograph is
taken from the PDF as the image object that was placed on the page, so it is
the photograph at the resolution it was supplied, not a render of the page
with its borders and lettering. tools/cvpnews.py names every one by page and
object number.

    python3 tools/make-news-cvp.py "path/to/CVP report.pdf"

The path can also be given as CIRS_CVP_PDF. Needs PyMuPDF and Pillow.
Writes assets/img/news/cvp/<slug>-<n>.webp, 1400px wide at most, and a
720px cut of each lead photograph for the News page's cards.
"""
import io
import os
import sys

import pymupdf
from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pymupdf.TOOLS.mupdf_display_errors(False)


def load_articles():
    # cvpnews reads the finished images' sizes when it is imported, so read
    # its photo list without importing it before the images exist.
    src = open(os.path.join(ROOT, "tools", "cvpnews.py"), encoding="utf-8").read()
    src = src.replace("\n_prepare()\n", "\n")
    ns = {"__file__": os.path.join(ROOT, "tools", "cvpnews.py")}
    exec(compile(src, "cvpnews.py", "exec"), ns)
    return ns["ARTICLES"], ns["photo_path"]


def extract(doc, xref):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)
    if pix.n - pix.alpha >= 4 or pix.colorspace and pix.colorspace.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = Image.open(io.BytesIO(pix.tobytes("png")))
    return ImageOps.exif_transpose(im).convert("RGB")


def save(im, path, width):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    im.save(full, "WEBP", quality=80, method=6)
    return im.size


def main():
    pdf = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CIRS_CVP_PDF")
    if not pdf:
        sys.exit(__doc__)
    doc = pymupdf.open(pdf)
    articles, photo_path = load_articles()
    count = 0
    for art in articles:
        for n, (page, xref, _alt) in enumerate(art["photos"], 1):
            im = extract(doc, xref)
            size = save(im, photo_path(art["slug"], n), 1400)
            if n == 1 and im.width > 720:
                save(im, photo_path(art["slug"], 1, 720), 720)
            count += 1
            print(f'{art["slug"]}-{n}  p{page} x{xref}  {size[0]}x{size[1]}')
    print(count, "photographs")


if __name__ == "__main__":
    main()
