#!/usr/bin/env python3
"""Cut the supplied photograph that CIRS Captures dissolves to.

    assets/img/captures-shot.jpg               landscape, for windows wider than 6:5
    assets/img/captures-shot-portrait.jpg      portrait, for phones and tablets upright
    assets/img/captures-shot-lqip.jpg          a few hundred bytes of each, blurred,
    assets/img/captures-shot-portrait-lqip.jpg   standing in until the real one arrives
    assets/img/captures-camera-final.jpg       the camera film's last frame, as a still

The opening photograph is a butterfly in grass. Both cuts keep the butterfly
in the frame; the opening's --film-focus in assets/css/filmintro.css and the
featured section's --cf-focus in assets/css/captures-featured.css must agree
so the photo holds its position across the handoff.

Nothing here repaints the photograph. The two cuts only crop and resize it.

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

import captures

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "assets/source", captures.LEAD_SOURCE)
FILM = os.path.join(ROOT, "assets/video/captures-camera.mp4")
IMG = os.path.join(ROOT, "assets/img")

# (name, output size). The butterfly sits left of centre in the source.
CUTS = [
    ("captures-shot", (1425, 1080)),
    ("captures-shot-portrait", (810, 1080)),
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
    for name, size in CUTS:
        full = ImageOps.fit(src, size, method=Image.Resampling.LANCZOS,
                            centering=(0.12, 0.5))
        path = write(full, f"{name}.jpg", 86)
        print(f"  write  assets/img/{name}.jpg  {os.path.getsize(path)//1024} KB  "
              f"{size[0]}x{size[1]}")
        tiny = full.resize((LQIP_WIDTH, round(LQIP_WIDTH * full.height / full.width)),
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
