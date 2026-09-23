#!/usr/bin/env python3
"""Cut the CIRS Captures gallery from the school's camera originals.

    assets/img/captures/<name>.jpg              the tile on the page
    assets/img/captures/full/<name>.jpg         the photograph in the viewer
    assets/img/captures/featured/<name>.jpg     a featured photograph, and a
    assets/img/captures/featured/<name>-lqip.jpg  blurred stand-in for it
    tools/captures-gallery.json                 the sizes written, for build-site.py

Anything else in assets/img/captures is removed: a photograph taken out of
the lists would otherwise stay behind, and tools/check-links.py would rightly
report it as an orphan.

The list of photographs, their captions and their layout live in
tools/captures.py. Nothing here repaints a photograph: every output is the
whole frame, resized, never cropped — the gallery lays each one out at its
own shape, so there is nothing to crop it to.

A tile is cut at the size it is actually drawn, with room for a 1.5x screen:
its share of a row at the page's widest, 1320px. So a photograph that has a
row to itself gets a larger tile than one sharing it with two others, and a
reader who never opens the viewer never downloads a full-size image. The
viewer's images are 2400px on the long side and are only fetched when a
photograph is opened, and then its neighbours, so the next one is ready.

    python3 tools/make-captures-gallery.py
"""

import json
import os
import sys

from PIL import Image, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import captures  # noqa: E402

ROOT = os.path.dirname(HERE)
SOURCE = os.path.join(ROOT, "assets/source")
OUT = "assets/img/captures"
PAGE_WIDTH = 1320          # --maxw in assets/css/cirs.css
DENSITY = 1.5
TILE_MIN, TILE_MAX = 900, 1800
FULL_LONG_EDGE = 2400
END_WIDTHS = (1200, 2400)  # the ending runs the full width of the window; the
                           # smaller cut is what a phone asks for


def fit(im, width):
    width = min(width, im.width)
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def save(im, rel, quality):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    return os.path.getsize(path)


def lqip(im, rel):
    """A stand-in a few hundred bytes long, drawn blurred until the file
    arrives, as the opening's photograph does (tools/make-captures-shot.py)."""
    small = fit(im, 32).filter(ImageFilter.GaussianBlur(1.2))
    return save(small, rel, 60)


def open_source(name):
    path = os.path.join(SOURCE, name)
    if not os.path.exists(path):
        sys.exit(f"make-captures-gallery: {path} is missing")
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def main():
    images, total = {}, 0
    for row in captures.ROWS:
        ratios = []
        opened = []
        for source, name, _ in row:
            im = open_source(source)
            opened.append((im, name))
            ratios.append(im.width / im.height)
        share = sum(ratios)
        for (im, name), ratio in zip(opened, ratios):
            tile_w = round(PAGE_WIDTH * ratio / share * DENSITY)
            tile = fit(im, max(TILE_MIN, min(TILE_MAX, tile_w)))
            long_edge = max(im.width, im.height)
            full = im if long_edge <= FULL_LONG_EDGE else fit(
                im, round(im.width * FULL_LONG_EDGE / long_edge))
            tile_path, full_path = f"{OUT}/{name}.jpg", f"{OUT}/full/{name}.jpg"
            total += save(tile, tile_path, 78) + save(full, full_path, 80)
            images[name] = {"tile": [tile.width, tile.height], "tile_path": tile_path,
                            "full": [full.width, full.height], "full_path": full_path}
            print(f"  write  {name:22s} tile {tile.width}x{tile.height}  full {full.width}x{full.height}")

    for source, name, _, width in captures.FEATURED:
        im = open_source(source)
        cut = fit(im, width)
        path, small = f"{OUT}/featured/{name}.jpg", f"{OUT}/featured/{name}-lqip.jpg"
        total += save(cut, path, 82) + lqip(im, small)
        images["featured/" + name] = {"tile": [cut.width, cut.height], "tile_path": path,
                                      "full": [cut.width, cut.height], "full_path": path,
                                      "lqip": small}
        print(f"  write  featured/{name:13s} {cut.width}x{cut.height}")

    source, name, _ = captures.END
    im = open_source(source)
    small, end = (fit(im, w) for w in END_WIDTHS)
    small_path, path = f"{OUT}/{name}-{small.width}.jpg", f"{OUT}/{name}.jpg"
    total += save(small, small_path, 80) + save(end, path, 80)
    images[name] = {"tile": [small.width, small.height], "tile_path": small_path,
                    "full": [end.width, end.height], "full_path": path}
    print(f"  write  {name:22s} {small.width}x{small.height} and {end.width}x{end.height}")

    written = {os.path.normpath(v[k]) for v in images.values()
               for k in ("tile_path", "full_path", "lqip") if k in v}
    for folder, _, files in os.walk(os.path.join(ROOT, OUT)):
        for f in files:
            rel = os.path.relpath(os.path.join(folder, f), ROOT)
            if rel not in written:
                os.remove(os.path.join(ROOT, rel))
                print(f"  remove {rel}")

    with open(captures.MANIFEST, "w", encoding="utf-8") as f:
        json.dump({"images": images}, f, indent=2)
        f.write("\n")
    print(f"  {len(images)} photographs, {total / 1e6:.1f} MB, sizes in tools/captures-gallery.json")


if __name__ == "__main__":
    main()
