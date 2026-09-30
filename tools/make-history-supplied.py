"""Optimise the user-supplied archival photographs without editing content.

The first four originals are read from the local review folder. The rest are
the school's "history" folder on Drive, supplied on 30 September 2026 with
each file named for its year; they are kept in assets/source/, which is never
deployed. Provenance and caption boundaries are recorded in
docs/school-history-cinematic.md and history.py. A cut is never enlarged, so
a small original stays small. Prints the sizes for EXHIBITS in history.py.
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review/school-history-cinematic'
DRIVE = ROOT / 'assets/source/history-drive-2026-09-30'
DEST = ROOT / 'assets/img/history'
FILES = {'supplied-rupee': REVIEW / 'drive-rupee.png',
         'supplied-opening': REVIEW / 'drive-opening.png',
         'supplied-isa': REVIEW / 'drive-award.jpg',
         'supplied-poland': REVIEW / 'drive-poland.png',
         # The Drive folder of 30 September 2026. Its 1984, 6 June 1996, 2011
         # and 2014 files are the four above, and its 1993 file is the
         # portrait of Gurudev already cut as "gurudev" by make-history.py.
         'supplied-1970': DRIVE / '1970.tif',
         'supplied-1994': DRIVE / '1994.png',
         'supplied-until-1996': DRIVE / 'until-1996.png',
         'supplied-june-1996': DRIVE / 'june-1996.png',
         'supplied-2005': DRIVE / '2005.png',
         'supplied-2009': DRIVE / '2009.jpg',
         'supplied-2018': DRIVE / '2018.avif',
         'supplied-2019': DRIVE / '2019.jpg'}
for name, source in FILES.items():
    if not source.exists():
        print(name, 'skipped: no', source.relative_to(ROOT))
        continue
    im = ImageOps.exif_transpose(Image.open(source)).convert('RGB')
    for suffix, width in [('sm', 640), ('lg', 1600)]:
        copy = im.copy()
        copy.thumbnail((width, 2200), Image.Resampling.LANCZOS)
        copy.save(DEST / f'{name}-{suffix}.jpg', quality=88, optimize=True)
        print(name, suffix, copy.size)
