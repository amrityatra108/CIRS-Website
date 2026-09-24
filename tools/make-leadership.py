#!/usr/bin/env python3
"""Cut the Leadership page's portraits to one shape each.

The photographs arrive in every shape: full-length on the school lawns at
1000-1400px, a square studio headshot, a portrait from an organisation's own
site. The page used to hand the school's ones to the browser whole: a 587 KB
file for a 64px disc beside the Principal's message, and a card that cropped
two of three at the knees rather than the face. This cuts every portrait to
the same two shapes instead, so they read as one set:

    leadership/<slug>.jpg        4:5, head and shoulders, for the roster
    leadership/<slug>-face.jpg   square, the face alone, for the messages

A person appears here only with a photograph published under their own name,
from one of two places:

  - supplied by the school: the files the owner's design artifact named
    (tools/media.tsv), kept in assets/img because
    tools/artifact-reference.html still shows them;
  - the official page of an organisation the person belongs to, saved to
    assets/source/leadership/ (never deployed) with the owner's approval,
    September 2026. SOURCES below records where each came from.

Nobody is given a photograph that was not published as theirs. Shri. Vijay
Mahtaney has none: no official page carrying his photograph was found.

    python3 tools/make-leadership.py
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/img/leadership"

PROFILE = (400, 500)    # 4:5, twice the widest the roster ever draws it
FACE = 160              # twice the 64-80px disc beside a message

# slug -> (source, 4:5 box, square face box). Boxes are in source pixels,
# placed by eye so that the eyes sit about a third of the way down. A person
# with no message on the page has no face box: nothing would show it.
CUTS = {
    "anukoolananda": ("assets/img/swami-anukoolananda.jpg",
                      (0, 0, 1000, 1250), (130, 30, 870, 770)),
    "krishnamurthy": ("assets/img/shanti-krishnamurthy.jpg",
                      (261, 95, 621, 545), (286, 95, 596, 405)),
    "rajeshwari":    ("assets/img/principal.jpg",
                      (445, 390, 1005, 1090), (500, 370, 950, 820)),
    "swaroopananda": ("assets/source/leadership/swaroopananda.jpg",
                      (282, 140, 650, 600), (326, 150, 606, 430)),
    "moorjani":      ("assets/source/leadership/moorjani.png",
                      (55, 0, 455, 500), None),
    # The frame on the wall behind him, at the right, stays out of both.
    "balachandran":  ("assets/source/leadership/balachandran.jpg",
                      (127, 0, 767, 800), None),
}

# Where each photograph in assets/source/leadership/ was published.
SOURCES = {
    "swaroopananda.jpg": "chinmayamission.com/global/swami-swaroopananda",
    "tejomayananda.jpg": "chinmayamission.com/global/swami-tejomayananda",
    "moorjani.png":      "citiustech.com/about-us/leadership/jagdish-moorjani",
    "balachandran.jpg":  "buimerccorp.com/team-buimerc",
}

# The Founder and Pujya Guruji have no roster entry — neither is on the
# Board — only a face beside their message. The Founder's is from the
# portrait the Founder page already uses.
FACES = {
    "founder":       ("assets/img/founder/archive/p607-portrait.webp", (230, 90, 1070, 930)),
    "tejomayananda": ("assets/source/leadership/tejomayananda.jpg", (172, 50, 832, 710)),
}


def cut(src, box, size, dest):
    im = ImageOps.exif_transpose(Image.open(ROOT / src)).convert("RGB")
    im = im.crop(box).resize(size, Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"{dest.relative_to(ROOT).as_posix()}  {size[0]}x{size[1]}  {dest.stat().st_size // 1024} KB")


def main():
    for slug, (src, profile, face) in CUTS.items():
        cut(src, profile, PROFILE, OUT / f"{slug}.jpg")
        if face:
            cut(src, face, (FACE, FACE), OUT / f"{slug}-face.jpg")
    for slug, (src, face) in FACES.items():
        cut(src, face, (FACE, FACE), OUT / f"{slug}-face.jpg")


if __name__ == "__main__":
    main()
