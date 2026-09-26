#!/usr/bin/env python3
"""Cut the web copies of images that were shipping at their master's weight.

Every job here reads a master that is kept, never deployed, in assets/source/
(or, for the blog, the article's own lead image), and writes the file the
page actually needs. Nothing is enlarged: a derivative is never wider than
its master, so a low-resolution photograph stays as sharp as it was and no
sharper — it only stops costing more than it shows.

    assets/founder-opening/assets/{menon,gurudev}-state-2048.webp
        The Founder opening's two portrait textures. Same 2048 square, so the
        WebGL plane samples exactly the same geometry; lossy colour over a
        lossless alpha channel, so the silhouette's edge is bit-for-bit the
        PNG's. Masters: assets/source/founder-opening/.

    assets/img/founder/amrit-vahini/{side,body-no-wheels}.webp, wheel-complete.webp
        The Amrit Vahini layers. The van is drawn at most 520 CSS px wide and
        each wheel at 12.68% of that, so the body is cut at 1330x665 (the
        master's exact 2:1, which assets/css/founder-journey.css's
        aspect-ratio:1774/887 depends on) and the wheel at 256 square.
        Masters: assets/source/founder/amrit-vahini/.

    assets/img/alumni/<name>.webp
        The four alumni portraits, at their own size — three of them are
        small, and the school owes larger originals (see tools/alumni.py).
        Masters: assets/source/alumni/.

    assets/img/blog/<name>-400.webp, -800.webp, -1000.webp
        Card sizes of each article's lead image, for the Blog front page's
        srcset (tools/blog.py). The article page keeps the full image.

    assets/img/founder/<file>-800.<ext>, tools/founder-images.json
        An 800px cut of every Founder photograph wider than 1100px, for its
        srcset, and the size of every one, so tools/build-site.py can give
        each <img> its width and height without opening the file.

    assets/img/crossroads/opening-final.jpg
        The Crossroads opening's poster, re-saved from its q95 master.
        Master: assets/source/crossroads/opening-final.jpg.

    python3 tools/make-media.py
"""

import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blogposts  # noqa: E402
import founder  # noqa: E402

ROOT = os.path.dirname(HERE)
SOURCE = os.path.join(ROOT, "assets/source")

# (master under assets/source, output, size or None for the master's own, quality)
WEBP = [
    ("founder-opening/menon-state-2048.png",
     "assets/founder-opening/assets/menon-state-2048.webp", None, 92),
    ("founder-opening/gurudev-state-2048.png",
     "assets/founder-opening/assets/gurudev-state-2048.webp", None, 92),
    ("founder/amrit-vahini/side.png",
     "assets/img/founder/amrit-vahini/side.webp", (1330, 665), 92),
    ("founder/amrit-vahini/body-no-wheels.png",
     "assets/img/founder/amrit-vahini/body-no-wheels.webp", (1330, 665), 92),
    ("founder/amrit-vahini/wheel-complete.png",
     "assets/img/founder/amrit-vahini/wheel-complete.webp", (256, 256), 92),
    ("alumni/shashwath-santosh.png", "assets/img/alumni/shashwath-santosh.webp", None, 88),
    ("alumni/soham-desai.png", "assets/img/alumni/soham-desai.webp", None, 92),
    ("alumni/divyaj-dt.png", "assets/img/alumni/divyaj-dt.webp", None, 92),
    ("alumni/hari-om-jani.png", "assets/img/alumni/hari-om-jani.webp", None, 92),
]

BLOG_CARD_WIDTHS = (400, 800, 1000)

JPEG = [
    ("crossroads/opening-final.jpg", "assets/img/crossroads/opening-final.jpg", 86),
]


def report(path):
    print(f"  write  {os.path.relpath(path, ROOT).replace(os.sep, '/')}  "
          f"{os.path.getsize(path) / 1024:.0f} KB")


def webp(master, out, size, quality):
    im = Image.open(os.path.join(SOURCE, master))
    has_alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
    im = im.convert("RGBA" if has_alpha else "RGB")
    if size and size != im.size:
        if size[0] > im.width or size[1] > im.height:
            sys.exit(f"make-media: {master} is smaller than {size}; nothing is enlarged")
        im = im.resize(size, Image.LANCZOS)
    path = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # alpha_quality=100 keeps the alpha channel lossless: a cut-out's edge is
    # exactly the master's. exact=False lets fully transparent pixels take
    # whatever colour compresses best, which nothing ever draws.
    im.save(path, "WEBP", quality=quality, alpha_quality=100, method=6)
    report(path)


def blog_cards():
    for post in blogposts.POSTS:
        name = post.get("image")
        if not name:
            continue
        master = os.path.join(ROOT, "assets/img/blog", name)
        im = Image.open(master).convert("RGB")
        stem = os.path.splitext(name)[0]
        for width in BLOG_CARD_WIDTHS:
            if width >= im.width:
                continue  # the article's own image already serves this width
            cut = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            path = os.path.join(ROOT, "assets/img/blog", f"{stem}-{width}.webp")
            cut.save(path, "WEBP", quality=80, method=6)
            report(path)


def founder_images():
    import json
    sizes = {}
    for slot, (name, *_) in founder.SLOTS.items():
        if not name:
            continue
        path = os.path.join(ROOT, "assets/img/founder", name)
        if not os.path.exists(path):
            continue
        im = Image.open(path)
        entry = {"w": im.width, "h": im.height}
        if im.width > 1100 and slot not in founder.UNCUT:
            stem, ext = os.path.splitext(name)
            cut = im.convert("RGB").resize((800, round(im.height * 800 / im.width)), Image.LANCZOS)
            out = os.path.join(ROOT, "assets/img/founder", f"{stem}-800{ext}")
            if ext.lower() == ".webp":
                cut.save(out, "WEBP", quality=82, method=6)
            else:
                cut.save(out, "JPEG", quality=84, optimize=True, progressive=True)
            report(out)
            entry["small"] = [os.path.relpath(out, ROOT).replace(os.sep, "/"), 800]
        sizes[name] = entry
    with open(founder.IMAGES, "w", encoding="utf-8") as f:
        json.dump(sizes, f, indent=1, sort_keys=True)
        f.write("\n")


def jpeg(master, out, quality):
    im = Image.open(os.path.join(SOURCE, master)).convert("RGB")
    path = os.path.join(ROOT, out)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    report(path)


def main():
    for job in WEBP:
        webp(*job)
    blog_cards()
    founder_images()
    for job in JPEG:
        jpeg(*job)


if __name__ == "__main__":
    main()
