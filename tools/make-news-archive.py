#!/usr/bin/env python3
"""Cut the photographs that came back from the school's older news pages.

Two of the stories the News page linked out to were galleries on the
school's own earlier site rather than articles: the Vishu and Tamil
Puthandu celebration and the Gayathri Havan. The pages are still up but
they are the only copy of those photographs, so they were fetched down
into assets/source/news-archive/ before the links were repointed.

Seven of the Vishu set are already gone from that server (pic01 and
pic15-20 return 404). What came back is what there is; nothing has been
substituted for the rest.

They arrive as 1200x675 web JPEGs rather than camera originals, so they
are not re-cropped — there is no detail left to crop into. They are put
through the same light grade as every other photograph on the site, so an
archive gallery sits beside the rest of the News page rather than looking
like a window onto a different website.

    python3 tools/make-news-archive.py
"""

import importlib.util
import os

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))

# The grade lives in make-photos.py and is not duplicated here: two copies of
# a grade drift, and then half the site is warmer than the other half. The
# hyphen in that filename is why this is loaded rather than imported.
_spec = importlib.util.spec_from_file_location("make_photos",
                                               os.path.join(HERE, "make-photos.py"))
_mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mp)
grade = _mp.grade

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/source/news-archive")
OUT = os.path.join(ROOT, "assets/img/news-archive")
WIDTH = 1200


def main():
    total = count = 0
    for gallery in sorted(os.listdir(SRC)):
        src = os.path.join(SRC, gallery)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(OUT, gallery)
        os.makedirs(dst, exist_ok=True)
        for name in sorted(os.listdir(src)):
            im = ImageOps.exif_transpose(Image.open(os.path.join(src, name))).convert("RGB")
            if im.width > WIDTH:
                im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
            out = os.path.join(dst, name)
            grade(im).save(out, "JPEG", quality=82, optimize=True, progressive=True)
            total += os.path.getsize(out) // 1024
            count += 1
        print(f"  {gallery}: {len(os.listdir(dst))} photographs")
    print(f"  {count} photographs, {total} KB")


if __name__ == "__main__":
    main()
