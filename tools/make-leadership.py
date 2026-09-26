#!/usr/bin/env python3
"""Cut the Leadership page's portraits, and its staff photograph, to size.

The crops live in tools/leadership.py (PORTRAITS), beside the markup that
names the files, so the two cannot drift. Every portrait is one 4:5 crop,
cut at a few widths for srcset and at its own full width — never wider. The
page used to draw 400px files as the four large portraits and 160px discs
beside the messages; these come from the largest originals in the repository
instead, and a small original stays small:

    leadership/<slug>-<width>.jpg      4:5, head and shoulders
    leadership/staff-<width>.jpg       the staff photograph, uncropped

A person appears here only with a photograph published under their own name,
from one of two places:

  - supplied by the school: the files the owner's design artifact named
    (tools/media.tsv), kept in assets/img because
    tools/artifact-reference.html still shows them;
  - the official page of an organisation the person belongs to, saved to
    assets/source/leadership/ (never deployed) with the owner's approval,
    September 2026. SOURCES below records where each came from.

Nobody is given a photograph that was not published as theirs. Shri Vijay
Mahtaney has none: no official page carrying his photograph was found. The
school's own site (new.cirschool.org) was checked in September 2026 for
larger copies of the others; every one it carries is smaller than these.

    python3 tools/make-leadership.py
"""
from pathlib import Path
from PIL import Image, ImageOps

import leadership as L

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/img/leadership"

# Where each photograph in assets/source/leadership/ was published.
SOURCES = {
    "swaroopananda.jpg": "chinmayamission.com/global/swami-swaroopananda",
    "tejomayananda.jpg": "chinmayamission.com/global/swami-tejomayananda",
    "moorjani.png":      "citiustech.com/about-us/leadership/jagdish-moorjani",
    "balachandran.jpg":  "buimerccorp.com/team-buimerc",
}


def save(im, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"{dest.relative_to(ROOT).as_posix()}  {im.width}x{im.height}  "
          f"{dest.stat().st_size // 1024} KB")


def main():
    made = set()
    for slug, (src, box) in L.PORTRAITS.items():
        im = ImageOps.exif_transpose(Image.open(ROOT / src)).convert("RGB").crop(box)
        assert abs(im.width * 5 - im.height * 4) <= 5, f"{slug}: crop is not 4:5"
        for w in L.widths(slug):
            dest = ROOT / L.portrait_path(slug, w)
            save(im.resize((w, w * 5 // 4), Image.LANCZOS), dest)
            made.add(dest.name)
    staff = ImageOps.exif_transpose(Image.open(ROOT / L.STAFF_SOURCE)).convert("RGB")
    for w in L.STAFF_WIDTHS:
        dest = ROOT / L.staff_path(w)
        save(staff.resize((w, round(staff.height * w / staff.width)), Image.LANCZOS), dest)
        made.add(dest.name)
    # Anything else in the folder is a cut this script no longer makes.
    for old in OUT.glob("*.jpg"):
        if old.name not in made:
            old.unlink()
            print(f"removed {old.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
