#!/usr/bin/env python3
"""Extract the Student Life subject without synthesising or repainting pixels.

The source frame has a student performer against a predominantly black stage.
Hand-traced body regions establish the subject, then luminance keys the dark
stage within them. A very small feather only softens the photographic edge.
The face and clothing remain the original school-owned photograph.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/source/drive-student-life-subject.JPG"
OUTPUT = ROOT / "assets/img/life-split-student.webp"

# Points are normalised to the source so the trace survives EXIF correction.
SHAPES = [
    # Head, torso and dress.
    [(0.235,.145),(0.285,.11),(0.345,.14),(0.385,.22),(0.43,.36),
     (0.51,.48),(0.50,1),(0.13,1),(0.19,.62),(0.21,.35)],
    # Raised left arm.
    [(0.18,0),(0.255,0),(0.275,.18),(0.24,.34),(0.19,.25)],
    # Extended right arm.
    [(0.39,.34),(0.58,.43),(0.91,.43),(0.93,.51),(0.60,.55),(0.42,.51)],
]

im = ImageOps.exif_transpose(Image.open(SOURCE)).convert("RGBA")
w, h = im.size
mask = Image.new("L", im.size, 0)
draw = ImageDraw.Draw(mask)
for shape in SHAPES:
    draw.polygon([(round(x*w), round(y*h)) for x, y in shape], fill=255)
# The traced shapes establish identity and exclude the other performer. Inside
# them, key the near-black stage while preserving the subject's red dress,
# natural skin and jewellery. Dark hair is allowed a softer edge; preserving a
# broad head region also preserves the black stage and creates a visible block.
rgb = np.asarray(im.convert("RGB"), dtype=np.int16)
r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
alpha = np.asarray(mask).copy()
light = np.maximum(np.maximum(r,g),b)
subject_colour = (r > g * 1.18) & (r > b * 1.22) & ((r - np.maximum(g, b)) > 20)
# The performer behind the subject wears a mid-grey costume. A higher key is
# intentional here: the warm colour guard preserves the foreground student's
# skin and costume while removing both that costume and the black stage.
stage = ~subject_colour
alpha[stage] = 0
mask = Image.fromarray(alpha, "L").filter(ImageFilter.GaussianBlur(max(1.2, w / 1800)))
im.putalpha(mask)

bbox = mask.getbbox()
if not bbox:
    raise SystemExit("life-split cutout mask is empty")
pad = round(w * .018)
bbox = (max(0,bbox[0]-pad), max(0,bbox[1]-pad), min(w,bbox[2]+pad), min(h,bbox[3]+pad))
cut = im.crop(bbox)
cut.thumbnail((1100, 1400), Image.Resampling.LANCZOS)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
cut.save(OUTPUT, "WEBP", quality=88, method=6)
print(f"  {OUTPUT.relative_to(ROOT)} {cut.width}x{cut.height} {OUTPUT.stat().st_size // 1024} KB <- {SOURCE.name}")
