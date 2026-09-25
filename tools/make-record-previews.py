#!/usr/bin/env python3
"""Cut the document previews The CIRS Record opens on.

School Information opens on four of the school's own certificates, laid out
as sheets of paper. They are not illustrations of certificates: each is the
first page of a PDF the page publishes, rendered, trimmed of the scanner's
margin and toned to the paper the page is printed on. Nothing on a sheet is
redrawn, retyped or moved.

    assets/img/records/recognition.jpg   Certificate of Recognition, Directorate
                                         of Private Schools, dated July 2026,
                                         valid up to 08.09.2027
    assets/img/records/noc-1996.jpg      The State NOC, 15 July 1996
    assets/img/records/cbse-2020.jpg     The CBSE extension-of-affiliation letter
                                         of 3 October 2020, which ran to
                                         31.03.2025 and has EXPIRED
    assets/img/records/land-2020.jpg     The Perur Taluk Office land certificate,
                                         24 January 2020

Each sheet on the page carries its real date and status in text beside it,
read from tools/documents.py — the CBSE letter says "Expired" there, because
it has. Choosing a different document means changing SHEETS below AND the
record in tools/pages/school-info.html, and checking the new one for anything
personal before it is set this large: these four carry no student, staff or
family details, only the school's own name, address and reference numbers.

Needs PyMuPDF to render the PDFs (pip install pymupdf) and Pillow. Run it
after replacing one of these PDFs and commit what changes.
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageOps

try:
    import pymupdf
except ImportError:  # older releases only offered the fitz name
    import fitz as pymupdf

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/documents/school-info"
OUT = ROOT / "assets/img/records"

# The warm white a sheet is toned to. Multiplied in, so white paper becomes
# this and the ink, which is near black, stays near black.
PAPER = (248, 244, 234)

# name -> (pdf, width in pixels, crop box as fractions of the page, contrast)
# The crop removes a scanner's blank margin or a browser's print header, never
# any of the document itself.
SHEETS = {
    "recognition": ("state-government-recognition.pdf", 700, (0.035, 0.05, 0.975, 0.975), 1.06),
    "noc-1996":    ("state-noc.pdf",                    560, (0.08, 0.012, 0.93, 0.88), 1.08),
    "cbse-2020":   ("cbse-affiliation-letter.pdf",      560, (0.04, 0.03, 0.96, 0.975), 1.0),
    "land-2020":   ("land-certificate.pdf",             560, (0.06, 0.04, 0.95, 0.97), 1.04),
}


def render(pdf, width):
    doc = pymupdf.open(SRC / pdf)
    page = doc[0]
    zoom = (width * 1.6) / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, (pdf, width, box, contrast) in SHEETS.items():
        im = render(pdf, width)
        w, h = im.size
        im = im.crop((round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)))
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        if contrast != 1:
            im = ImageEnhance.Contrast(im).enhance(contrast)
        im = ImageOps.autocontrast(im, cutoff=(0.2, 0))
        im = ImageChops.multiply(im, Image.new("RGB", im.size, PAPER))
        path = OUT / f"{name}.jpg"
        im.save(path, "JPEG", quality=70, optimize=True, progressive=True)
        total += path.stat().st_size
        print(f"  {path.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}  {path.stat().st_size / 1024:.0f} KB")
    print(f"{len(SHEETS)} sheets, {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
