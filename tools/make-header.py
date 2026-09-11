#!/usr/bin/env python3
"""Compose the Admissions banner photograph.

The banner has to do two jobs at once: look like the rest of the site, and
keep a large white headline and a paragraph of lead text readable over it.
A raw photograph does neither — campus pictures are bright, busy and green,
and the site is deep purple and gold.

So the source is graded rather than merely darkened:

  1. cropped to the banner's aspect and gently blurred, so detail never
     competes with the type sitting on top of it;
  2. mapped to a duotone between the site's purple-ink and a warm highlight,
     which is what makes it read as part of this site rather than a stock
     photo dropped into it;
  3. given a directional gradient — heaviest at the bottom left where the
     headline and lead sit, lightest at the top right — the same diagonal
     the .band sections already use.

The CSS scrim over .pagehero is deliberately light, because the darkening
lives here. Change one and check the other: tools/check-contrast.py measures
what the headline actually gets.

    python3 tools/make-header.py                      # uses SOURCES below
    python3 tools/make-header.py path/to/photo.jpg    # or your own

Drop replacement photographs into assets/source/ and pass one in. Anything
wider than it is tall works; the crop is centred. The originals live there
rather than in assets/img because they are 150 MB of camera files that must
never reach a web host — see assets/source/README.md.
"""

import os
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default source, and the fallbacks if it is missing. The assembly in front of
# the school was chosen over the close-up portraits in the same set: under a
# heavy grade a face becomes an unreadable shape, whereas a crowd reads as
# texture, and the empty paved foreground is where the headline lands.
SOURCES = ["assets/source/IMG_20260423_091355.jpg",
           "assets/img/aerial-duo.jpg", "assets/img/hero.jpg"]
OUT = "assets/img/admissions-header.jpg"

WIDTH, HEIGHT = 2400, 1200          # 2:1, covers a 1440px-wide banner at 2x

# The duotone ramp. The shadow is a saturated purple rather than the near
# black of --purple-ink: black shadows give a grey, sepia-looking midtone,
# and what makes the picture belong to this site is purple in the middle of
# the range, not only at the bottom of it. The highlight is warmed toward
# the gold accent for the same reason.
SHADOW = (32, 22, 54)
HIGHLIGHT = (232, 206, 158)
KEEP_COLOUR = 0.10                  # a trace of the original hue survives
WASH = (30, 22, 38)                 # --purple-deep, laid over to unify
WASH_ALPHA = 0.26


def cover(im, w, h):
    """Scale and centre-crop to exactly w x h, without distorting."""
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * scale)), max(h, int(im.height * scale))),
                   Image.LANCZOS)
    left = (im.width - w) // 2
    top = (im.height - h) // 2
    return im.crop((left, top, left + w, top + h))


def duotone(im):
    """Map luminance onto a purple-to-warm ramp."""
    grey = im.convert("L")
    grey = ImageEnhance.Contrast(grey).enhance(1.12)
    ramp = []
    for channel in range(3):
        lo, hi = SHADOW[channel], HIGHLIGHT[channel]
        ramp += [int(lo + (hi - lo) * (i / 255)) for i in range(256)]
    toned = grey.convert("RGB").point(ramp)
    toned = Image.blend(toned, im, KEEP_COLOUR)
    wash = Image.new("RGB", toned.size, WASH)
    return Image.blend(toned, wash, WASH_ALPHA)


def gradient(w, h):
    """A diagonal darkening mask: heaviest bottom-left, lightest top-right."""
    mask = Image.new("L", (w, h))
    px = mask.load()
    for y in range(h):
        for x in range(w):
            # 0 at top-right, 1 at bottom-left
            t = (1 - x / w) * 0.62 + (y / h) * 0.52
            px[x, y] = int(255 * min(1.0, max(0.0, t)) ** 1.05)
    return mask


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if src is None:
        for candidate in SOURCES:
            if os.path.exists(os.path.join(ROOT, candidate)):
                src = candidate
                break
    if src is None:
        sys.exit("make-header: no source photograph found; pass one as an argument")

    path = src if os.path.isabs(src) else os.path.join(ROOT, src)
    if not os.path.exists(path):
        sys.exit(f"make-header: {src} not found")

    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im = cover(im, WIDTH, HEIGHT)
    im = im.filter(ImageFilter.GaussianBlur(radius=2.2))
    im = duotone(im)
    im = ImageEnhance.Brightness(im).enhance(0.86)

    dark = Image.new("RGB", (WIDTH, HEIGHT), SHADOW)
    im = Image.composite(dark, im, gradient(WIDTH, HEIGHT).point(
        lambda v: int(v * 0.88)))   # the gradient never reaches full black

    out = os.path.join(ROOT, OUT)
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"  write  {OUT}  {WIDTH}x{HEIGHT}  "
          f"{os.path.getsize(out):,} bytes  (from {src})")


if __name__ == "__main__":
    main()
