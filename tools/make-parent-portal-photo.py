#!/usr/bin/env python3
"""Build the Parent Portal's responsive photograph from its CIRS original.

Source: CIRS MEDIA POOL / 2025 / New Academic year /
3. New parent & student orientation (swagatham) / CRS02042.JPG
https://drive.google.com/file/d/1sMBNCGroazwpb-pjDzo9SWEKO3G5YISA/view

The wide, tablet, and portrait cuts keep the adult, child, and booklet in view
at the three opening-frame shapes. Outputs omit camera metadata.
"""

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "parent-portal" / "CRS02042.JPG"
OUT = ROOT / "assets" / "img" / "parent-portal"

# name, crop box on the EXIF-corrected 6000 x 3376 source, output widths
FRAMES = (
    ("wide", (0, 0, 6000, 2790), (1200, 2000, 2600)),
    ("tablet", (660, 0, 5160, 3376), (960, 1600)),
    ("mobile", (1020, 0, 4140, 3376), (560, 960)),
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
    if image.size != (6000, 3376):
        raise ValueError(f"Unexpected source dimensions: {image.size}")

    for name, box, widths in FRAMES:
        crop = image.crop(box)
        for width in widths:
            height = round(width * crop.height / crop.width)
            rendition = crop.resize((width, height), Image.Resampling.LANCZOS)
            path = OUT / f"reading-{name}-{width}.webp"
            rendition.save(path, "WEBP", quality=82, method=6)
            print(path.relative_to(ROOT), f"{width}x{height}")
        if name in {"wide", "mobile"}:
            width = 2000 if name == "wide" else 960
            height = round(width * crop.height / crop.width)
            path = OUT / f"reading-{name}-{width}.jpg"
            crop.resize((width, height), Image.Resampling.LANCZOS).save(
                path, "JPEG", quality=84, optimize=True, progressive=True
            )
            print(path.relative_to(ROOT), f"{width}x{height}")


if __name__ == "__main__":
    main()
