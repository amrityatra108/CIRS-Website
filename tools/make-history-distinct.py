#!/usr/bin/env python3
"""Build distinct History photographs and the dated 2025 report exhibit.

Original official-source photographs and their URLs are retained in
assets/source/history-distinct/. Only the proportion-preserving JPEG cuts
are staged for the website. Requires Pillow and PyMuPDF.
"""
from pathlib import Path
from PIL import Image, ImageOps
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/source/history-distinct'
OUT = ROOT / 'assets/img/history'
# The lineage and Guruji photographs were retired on 30 September 2026, when
# the school's own photographs for the 1970s and 1994 took their chapters;
# their masters stay in the source folder.
PHOTOS = {
    'samadhi-sthal': 'samadhi-sthal.jpg',
}


def write(name, image):
    for suffix, width in [('sm', 640), ('lg', 1400)]:
        cut = image.copy()
        cut.thumbnail((width, 2200), Image.Resampling.LANCZOS)
        cut.save(OUT / f'{name}-{suffix}.jpg', quality=86, optimize=True, progressive=True)
        print(name, suffix, cut.size)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, filename in PHOTOS.items():
        write(name, ImageOps.exif_transpose(Image.open(SOURCE / filename)).convert('RGB'))
    with pymupdf.open(ROOT / 'assets/documents/school-info/annual-report.pdf') as report:
        page = report[0]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1400 / page.rect.width, 1400 / page.rect.width), alpha=False)
        write('report-2025', Image.frombytes('RGB', (pix.width, pix.height), pix.samples))


if __name__ == '__main__':
    main()
