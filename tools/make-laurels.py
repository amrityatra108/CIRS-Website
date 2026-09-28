#!/usr/bin/env python3
"""Cut the Our Laurels competition photographs into assets/img/laurels/.

The photographs are the school's own, from its Google Drive (folders and file
ids are recorded in SEASON_PHOTOS in tools/laurels.py). The originals are not
in the repository. Put them, under their Drive file names, in one folder and
point this tool at it:

    python3 tools/make-laurels.py <folder-of-originals>

Each photograph is cut at two widths, honouring the EXIF rotation, and the
tool prints the sizes to keep in SEASON_PHOTOS. Nothing is retouched.

The Drive connector will not hand over files over 10 MB, so the Science Quiz,
English Quiz, Storytelling, Trinity, HAM and most Spell Bee originals are not
here. When the school exports them at a smaller size, add them to
SEASON_PHOTOS and re-run.
"""

import os
import sys

from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import laurels  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "img", "laurels")
WIDTHS = {"landscape": (1600, 800), "portrait": (900, 450)}


def main(src):
    os.makedirs(OUT, exist_ok=True)
    for key, rec in laurels.SEASON_PHOTOS.items():
        path = os.path.join(src, rec["file"])
        if not os.path.exists(path):
            sys.exit(f"missing original: {rec['file']} (Drive id {rec['id']})")
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        w, h = im.size
        large, small = WIDTHS["portrait" if h > w else "landscape"]
        sizes = []
        for width, suffix in ((large, "1600"), (small, "800")):
            height = round(h * width / w)
            out = im.resize((width, height), Image.LANCZOS)
            dest = os.path.join(OUT, f"{key}-{suffix}.jpg")
            out.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
            sizes.append((width, height, os.path.getsize(dest)))
        print(f"{key:6} large {sizes[0][0]}x{sizes[0][1]} ({sizes[0][2] // 1024} KB)  "
              f"small {sizes[1][0]}x{sizes[1][1]} ({sizes[1][2] // 1024} KB)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
