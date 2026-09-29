"""Optimise the user-supplied archival photographs without editing content.

Original files are read from the local review folder. Provenance and caption
boundaries are recorded in docs/school-history-cinematic.md and history.py.
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'review/school-history-cinematic'
DEST = ROOT / 'assets/img/history'
FILES = {'supplied-rupee': 'drive-rupee.png',
         'supplied-opening': 'drive-opening.png',
         'supplied-isa': 'drive-award.jpg',
         'supplied-poland': 'drive-poland.png'}
for name, filename in FILES.items():
    im = ImageOps.exif_transpose(Image.open(SOURCE / filename)).convert('RGB')
    for suffix, width in [('sm', 640), ('lg', 1600)]:
        copy = im.copy()
        copy.thumbnail((width, 2200))
        copy.save(DEST / f'{name}-{suffix}.jpg', quality=88, optimize=True)
        print(name, suffix, copy.size)
