#!/usr/bin/env python3
"""Cut the browser-tab icons from the school crest.

The favicon used to be assets/img/favicon.jpg — a JPEG, which cannot hold an
alpha channel, so the round crest arrived baked onto a white square. In a dark
browser chrome that square is the only thing the eye sees: a white chip with a
smudge in it, sitting beside tabs whose icons are shapes. The crest itself has
always had a clean circular cutout in assets/img/logo.png; nothing had ever
carried it as far as the tab.

So these are cut from logo.png, keeping its alpha, and written as PNG:

    favicon-32.png    32x32    the tab, and the bookmark bar
    favicon-180.png   180x180  apple-touch-icon
    favicon-192.png   192x192  Android, and any high-DPI surface

Two decisions worth stating, because neither is obvious from the output:

  * The crest is cropped to its own alpha bounding box and re-centred on a
    square canvas with a small margin. logo.png is 320x312 with a few
    transparent rows on one edge, so using it unchanged would have hung the
    circle a pixel or two off centre at every size — which is invisible at
    320px and plainly wrong at 32.

  * The touch icon is NOT transparent. iOS composites a transparent touch
    icon onto black and then applies its own mask, and black is not one of
    this site's colours. It gets --purple-ink #0E0B12 instead, which is the
    ground the site already declares as its theme-color, so the home-screen
    icon matches the browser chrome the site asks for rather than fighting it.
    The tab icons stay transparent, which is what the tab wants.

Needs Pillow, which the ordinary site build does not — run it only when the
crest changes, and commit what it writes:

    python3 tools/make-favicon.py
"""

import os
import sys

try:
    from PIL import Image
except ImportError:                                          # pragma: no cover
    sys.exit("make-favicon: needs Pillow — pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "assets", "img", "logo.png")
OUT = os.path.join(ROOT, "assets", "img")

# The site's --purple-ink, and the <meta name="theme-color"> value in
# tools/partials/head.html. Keep the three in step.
INK = (14, 11, 18, 255)

# size, filename, margin as a fraction of the canvas, background
#
# The touch icon carries the widest margin because iOS draws it at the size of
# an app icon and rounds the corners; a crest run to the edge there looks
# cramped where the same crest in a 32px tab looks merely small.
ICONS = [
    (32,  "favicon-32.png",  0.010, None),
    (180, "favicon-180.png", 0.105, INK),
    (192, "favicon-192.png", 0.030, None),
]


def crest():
    """logo.png cropped to the crest and squared up, still transparent."""
    im = Image.open(SOURCE).convert("RGBA")
    # A few of logo.png's edge pixels carry one or two units of alpha. Trim on
    # a threshold rather than on "not fully transparent", or the bounding box
    # is the whole canvas and the centring below does nothing.
    box = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    im = im.crop(box)
    side = max(im.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    return square


def main():
    source = crest()
    for size, name, margin, ground in ICONS:
        inner = round(size * (1 - 2 * margin))
        art = source.resize((inner, inner), Image.LANCZOS)
        canvas = Image.new("RGBA", (size, size), ground or (0, 0, 0, 0))
        off = (size - inner) // 2
        canvas.alpha_composite(art, (off, off))
        # A favicon is fetched on every cold page load, so it is worth paying
        # attention to. The crest is a gradient and a truecolour PNG of it is
        # 76 KB at 192; a 255-entry palette is 17 KB and, measured against the
        # truecolour render, shows no banding the eye can find at these sizes.
        # FASTOCTREE is the one method here that keeps the alpha channel.
        canvas = canvas.quantize(colors=255, method=Image.FASTOCTREE)
        path = os.path.join(OUT, name)
        canvas.save(path, "PNG", optimize=True)
        print(f"  write  assets/img/{name}  ({size}x{size}, "
              f"{'on ink' if ground else 'transparent'}, "
              f"{os.path.getsize(path):,} bytes)")


if __name__ == "__main__":
    main()
