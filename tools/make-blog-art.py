#!/usr/bin/env python3
"""Lead images for the four Blog articles that had none.

Each was chosen for what its article argues. Three are the article's own
artwork, cut from its pages in the issue (the PDFs in
assets/source/crossroads-pdf/, which are never deployed). The fourth is a
campus photograph the site already holds, because that essay is about the
campus:

    sportswashing.webp
        Issue 30, page 8: the illustration of a World Cup stadium rising out of
        the desert under a crane, with a labourer, a footballer and the
        officials behind it. It is cut out in print, so it is laid on that
        page's own paper.
    is-ai-art-really-art.webp
        Issue 31, page 5: the robot at an easel, one panel of the collage the
        article opens on, with the corner of The Starry Night beside it. It is
        cut short of the title and the issue line.
    death-of-detail.webp
        Issue 4, page 10: the plain chair against a bare wall that heads the
        article.
    my-home.webp
        The campus below the hills, from assets/img/hero.jpg: the essay is
        about the school becoming home.

Each is the article's master image, assets/img/blog/<slug>.webp. Run
tools/make-media.py afterwards for its card sizes, and keep image_width and
image_height in tools/blogposts.py in step with the sizes this prints.

    python3 tools/make-blog-art.py
"""

import os

import pymupdf
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "assets/source/crossroads-pdf/crossroads-issue-{:02d}.pdf")
OUT = os.path.join(ROOT, "assets/img/blog")

# An embedded picture, by its xref in that issue's PDF and the xref of its
# transparency mask (0 for none), with the paper it is laid on if it has one.
EMBEDDED = {
    "sportswashing": (30, 444, 442, (250, 247, 250)),
    "death-of-detail": (4, 160, 0, None),
}
# A region of a page as printed: page number, and the box in PDF points.
REGIONS = {
    "is-ai-art-really-art": (31, 5, (78, 32, 292, 216)),
}
SITE = {
    "my-home": "assets/img/hero.jpg",
}


def embedded(issue, xref, smask, paper):
    doc = pymupdf.open(PDF.format(issue))
    pix = pymupdf.Pixmap(doc, xref)
    if pix.colorspace and pix.colorspace.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    if smask:
        pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(doc, smask))
        im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
        ground = Image.new("RGB", im.size, paper)
        ground.paste(im, mask=im.getchannel("A"))
        return ground
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def region(issue, page, box):
    doc = pymupdf.open(PDF.format(issue))
    pix = doc[page - 1].get_pixmap(clip=pymupdf.Rect(*box), dpi=300)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def save(slug, im):
    path = os.path.join(OUT, f"{slug}.webp")
    im.save(path, "WEBP", quality=84, method=6)
    print(f"  {os.path.relpath(path, ROOT)}  {im.width}x{im.height}  {os.path.getsize(path) // 1024} KB")


def main():
    for slug, args in EMBEDDED.items():
        save(slug, embedded(*args))
    for slug, args in REGIONS.items():
        save(slug, region(*args))
    for slug, source in SITE.items():
        save(slug, Image.open(os.path.join(ROOT, source)).convert("RGB"))


if __name__ == "__main__":
    main()
