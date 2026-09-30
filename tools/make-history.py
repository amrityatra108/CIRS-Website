#!/usr/bin/env python3
"""Cut the exhibits the School History archive is built from.

    assets/img/history/<name>-sm.jpg    about 640px wide: the stage and the grid
    assets/img/history/<name>-lg.jpg    up to 1400px wide: the record's own view

Every exhibit is one of the school's own things, reproduced, never redrawn:
a portrait from the school's archive, the first page of a publication or a
letter the school kept, or a photograph of an award from the school's Drive.
Nothing is toned, aged or retouched. A photograph keeps its own colour and a
page keeps its own paper; the only change is the size and, for a page, the
blank margin a scanner or a printer left around it.

Which exhibit belongs to which event, and where each came from, is recorded
in tools/history.py. Change an exhibit there and here together.

The Drive originals are not in the repository — they are fetched at the
largest size the page uses through Drive's own thumbnail endpoint, the way
tools/make-theatre.py fetches its photographs. The PDFs are in pdf/ (the old
site's files) and assets/documents/school-info/ (published on this site).

Needs Pillow and PyMuPDF:  pip install Pillow pymupdf

    python3 tools/make-history.py
"""
import io
import os
import urllib.request

from PIL import Image, ImageChops, ImageOps

try:
    import pymupdf
except ImportError:  # older releases only offered the fitz name
    import fitz as pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets/img/history")
SIZES = {"sm": 640, "lg": 1400}
QUALITY = 82

# name -> source. ("pdf", path, page) renders a page; ("img", path) reads a
# file in the repository; ("drive", file id) fetches a school Drive photograph.
EXHIBITS = {
    # The portrait the Founder page opens its warm close-up on.
    "gurudev":     ("img", "assets/img/founder/archive/p607-portrait.webp"),
    # The State's No Objection Certificate, dated 15 July 1996. Published on
    # School Information; one typed page.
    "noc-1996":    ("pdf", "assets/documents/school-info/state-noc.pdf", 0),
    # The first page of the school's account of the students' meeting with
    # President Kalam on 7 May 2007. It names the Principal, not the students.
    "kalam-2007":  ("pdf", "pdf/President of India.pdf", 0),
    # The cover of the students' e-newsletter, summer special, May 2008.
    "sakshi-2008": ("pdf", "pdf/Sakshi Newleter summer special May 2008.pdf", 0),
    # The cover of Reflections, the IB newsletter, August 2010.
    "reflections-2010": ("pdf", "pdf/CIRS IB Newsletter August 2010.pdf", 0),
    # The Junior School holiday assignment of December 2010, set as part of
    # the British Council's International School Award programme.
    "isa-2010":    ("pdf", "pdf/CIRS Junior School Holiday Assignment - December 2010.pdf", 0),
    # The CCMT Education Cell Vision Award 2012 at its presentation.
    # Drive: "vision award.jpg", file dated 25 July 2012.
    "vision-2012": ("drive", "1IKee8BaB7Lg6FAda-Tg0JvPjq0f6nzK1"),
    # The Brainfeed School Excellence Awards plaque, 12 November 2017.
    # Drive: "award.JPG", file dated 15 November 2017.
    "brainfeed-2017": ("drive", "1Y26E4qz_3Jqq2IDeSUIWVuWphNM6SLfF"),
    # The first page of the Annual Report of 15 October 2019. Published on
    # School Information as annual-report.pdf.
    "report-2019": ("pdf", "assets/documents/school-info/annual-report.pdf", 0),
}


def fetch_drive(file_id):
    url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w{SIZES['lg']}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=120).read()
    return ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")


def render_page(path, page):
    doc = pymupdf.open(os.path.join(ROOT, path))
    p = doc[page]
    zoom = SIZES["lg"] / p.rect.width
    pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return trim(im)


def trim(im, pad=0.035):
    """Take off the blank margin around a page, keeping a little of it.

    Only near-white is trimmed, so nothing printed is ever cut; what is left
    is the page as it was, a little closer."""
    grey = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 24 else 0)
    box = grey.getbbox()
    if not box:
        return im
    l, t, r, b = box
    px, py = int(im.width * pad), int(im.height * pad)
    return im.crop((max(0, l - px), max(0, t - py),
                    min(im.width, r + px), min(im.height, b + py)))


def load(src):
    kind = src[0]
    if kind == "pdf":
        return render_page(src[1], src[2])
    if kind == "drive":
        return fetch_drive(src[1])
    return ImageOps.exif_transpose(Image.open(os.path.join(ROOT, src[1]))).convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, src in EXHIBITS.items():
        im = load(src)
        for size, width in SIZES.items():
            out = im
            if im.width > width:
                out = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            dest = os.path.join(OUT, f"{name}-{size}.jpg")
            out.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            print(f"  write  {os.path.relpath(dest, ROOT)}  {out.width}x{out.height}"
                  f"  {os.path.getsize(dest) // 1024} KB")


if __name__ == "__main__":
    main()
