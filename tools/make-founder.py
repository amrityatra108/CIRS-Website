#!/usr/bin/env python3
"""Cut the Founder page's science photograph from its archival scan.

assets/source/founder/ holds the archival masters at full resolution — like
the rest of assets/source/, they are never deployed. This derives the web
copies the page actually ships.

The main portraits now come from the supplied Gurudev archive and are exported
separately. This script retains the earlier science image used by the
Education as Transformation section.

Run it after adding a scan; tools/build-site.py reads the output.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/source/founder"
OUT = ROOT / "assets/img/founder"

# Saturation is compressed, not scaled. A flat multiplier that tames the
# sweater also drains the Himalaya to grey, and a gamma curve does nothing at
# all to it — the sweater sits at the very top of the range, where any power
# of 1 is still 1. This bends the curve by the square of saturation, so the
# most saturated pixels lose nearly half and the soft mountain blues lose
# almost nothing: s' = s * (1 - SAT_PULL * s^2).
SAT_PULL   = 0.46
CONTRAST   = 1.06
WARMTH     = (1.030, 1.002, 0.958)   # per-channel gain, toward paper
WASH       = ((244, 240, 232), 0.09)  # the page's own parchment, faintly over all

# name -> (master, crop box on the master, output width)
# Boxes are in master pixels.
CUTS = {
    # Enquiry: a Vedanta teacher holding a laboratory vessel up to the light.
    # The scan carries the print's own border down its left edge and along the
    # bottom, so the crop starts inside it.
    "gurudev-enquiry.jpg": ("gurudev-enquiry.jpg", (60, 20, 2470, 2980), 1300),
}


def desaturate(im):
    h, s, v = im.convert("HSV").split()
    lut = [round(i * (1 - SAT_PULL * (i / 255) ** 2)) for i in range(256)]
    return Image.merge("HSV", (h, s.point(lut), v)).convert("RGB")


def grade(im):
    im = desaturate(im)
    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    r, g, b = im.split()
    im = Image.merge("RGB", (
        r.point(lambda v: min(255, int(v * WARMTH[0]))),
        g.point(lambda v: min(255, int(v * WARMTH[1]))),
        b.point(lambda v: min(255, int(v * WARMTH[2]))),
    ))
    tone, alpha = WASH
    return Image.blend(im, Image.new("RGB", im.size, tone), alpha)


def main():
    Image.MAX_IMAGE_PIXELS = None
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (master, box, width) in CUTS.items():
        path = SRC / master
        if not path.exists():
            print(f"  skip {name} — {master} not in assets/source/founder")
            continue
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB").crop(box)
        im = im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)
        grade(im).save(OUT / name, "JPEG", quality=84, optimize=True, progressive=True)
        print(f"  {name:24s} {im.size[0]}x{im.size[1]}"
              f"  {(OUT / name).stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
