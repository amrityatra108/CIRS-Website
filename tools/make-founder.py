#!/usr/bin/env python3
<<<<<<< HEAD
"""Cut the Founder page's photographs from the archival scan.
=======
"""Cut the Founder page's science photograph from its archival scan.
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

assets/source/founder/ holds the archival masters at full resolution — like
the rest of assets/source/, they are never deployed. This derives the web
copies the page actually ships.

<<<<<<< HEAD
The grade is the point. The scan is a colour transparency: the sweater is a
near-fluorescent red that would dominate a page built on parchment and muted
greens, and would make the whole thing read as the "saffron spiritual website"
the design deliberately avoids. Saturation comes down, the highlights warm
toward paper, and a thin ivory wash ties the photograph to the ground it sits
on — so the red settles into brick and the Himalaya into a soft grey-blue.
=======
The main portraits now come from the supplied Gurudev archive and are exported
separately. This script retains the earlier science image used by the
Education as Transformation section.
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

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
<<<<<<< HEAD
# Boxes are in master pixels; the master is 4060x6091.
CUTS = {
    # The hero: the whole frame. Its top half is pale, soft mountain, which is
    # what lets the oversized letters read through the sky while his figure
    # blocks them — the interleave is in the photograph, not a fake cutout.
    "gurudev-hero.jpg":    ("gurudev-sidhbari.jpg", (0, 0, 4060, 6091), 1500),
    # The introduction: close on the face and the raised hand, mid-sentence.
    "gurudev-portrait.jpg": ("gurudev-sidhbari.jpg", (1180, 2180, 3180, 4680), 1100),
    # The closing: he sits small under the mountain he studied beneath.
    "gurudev-himalaya.jpg": ("gurudev-sidhbari.jpg", (0, 500, 4060, 4560), 1700),
=======
# Boxes are in master pixels.
CUTS = {
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
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
