#!/usr/bin/env python3
"""Cut the photograph that CIRS Captures opens out of its camera lens.

    assets/img/captures-shot.jpg               landscape, for windows wider than 6:5
    assets/img/captures-shot-portrait.jpg      portrait, for phones and tablets upright
    assets/img/captures-shot-lqip.jpg          a few hundred bytes of each, blurred,
    assets/img/captures-shot-portrait-lqip.jpg   standing in until the real one arrives
    assets/img/captures-camera-final.jpg       the camera film's last frame, as a still

The photograph is a student dancing on stage, from the school's own camera
originals (Canon EOS 700D). It was chosen because it is the one picture on
file that works at both of the sizes this opening asks of it: it has to read
inside a lens window roughly half as wide as it is tall, and then hold the
whole screen. Her face, raised arm and dress stack vertically, which is what
reads in the lens; and the dark stage behind her carries the camera film's
own palette, so the photograph arriving out of the lens reads as the same
shot continuing rather than a cut to daylight.

Nothing here repaints the photograph. The cuts are crops and a resize: the
landscape cut stops short of the pale wall panel along the right edge of the
frame, and the portrait cut is centred on her.

FOCUS is the point in each cut that the opening treats as its subject. It is
written into assets/css/captures.css as that cut's object-position, which
does two jobs at once: it keeps her in place however the window crops the
picture, and it tells assets/js/captures.js where to centre the photograph
inside the lens. Change a crop here and update the matching focus there.

The camera still is the film's final frame. Without JavaScript, under
reduced motion, and when the film fails to load, the opening is one screen
of that composition rather than a film. Extracting it needs ffmpeg, which is
not a dependency of this site; the step is skipped with a note when neither
$FFMPEG nor ffmpeg on the PATH is available, and the committed still stands.

    python3 tools/make-captures-shot.py
"""

import os
import shutil
import subprocess
import sys

from PIL import Image, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "assets/source/drive-student-life-subject.JPG")
FILM = os.path.join(ROOT, "assets/video/captures-camera.mp4")
IMG = os.path.join(ROOT, "assets/img")

# (name, crop box in source pixels, output size, focus as fractions of the cut)
CUTS = [
    ("captures-shot",          (0,   0, 4560, 3456), (2400, 1819), (0.37, 0.40)),
    ("captures-shot-portrait", (324, 0, 2916, 3456), (1620, 2160), (0.52, 0.40)),
]
LQIP_WIDTH = 32
FILM_LAST_FRAME = 143          # six seconds at 24fps: frames 0 to 143


def write(im, name, quality):
    path = os.path.join(IMG, name)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    return path


def cut_photographs():
    if not os.path.exists(SOURCE):
        sys.exit(f"make-captures-shot: {SOURCE} is missing")
    src = ImageOps.exif_transpose(Image.open(SOURCE)).convert("RGB")
    for name, box, size, focus in CUTS:
        crop = src.crop(box)
        full = crop.resize(size, Image.LANCZOS)
        path = write(full, f"{name}.jpg", 80)
        print(f"  write  assets/img/{name}.jpg  {os.path.getsize(path)//1024} KB  "
              f"{size[0]}x{size[1]}  focus {focus[0]:.2f} {focus[1]:.2f}")
        tiny = crop.resize((LQIP_WIDTH, round(LQIP_WIDTH * crop.height / crop.width)),
                           Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
        path = write(tiny, f"{name}-lqip.jpg", 60)
        print(f"  write  assets/img/{name}-lqip.jpg  {os.path.getsize(path)} B")


def cut_camera_still():
    ffmpeg = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    out = os.path.join(IMG, "captures-camera-final.jpg")
    if not ffmpeg:
        print("  skip   assets/img/captures-camera-final.jpg  (no ffmpeg; set $FFMPEG to rebuild)")
        return
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", FILM,
                    "-vf", f"select=eq(n\\,{FILM_LAST_FRAME})", "-vsync", "0",
                    "-frames:v", "1", "-q:v", "3", out], check=True)
    print(f"  write  assets/img/captures-camera-final.jpg  {os.path.getsize(out)//1024} KB")


if __name__ == "__main__":
    cut_photographs()
    cut_camera_still()
