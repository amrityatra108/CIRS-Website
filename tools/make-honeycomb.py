#!/usr/bin/env python3
"""Build the Admissions hero: a honeycomb of the school's own photographs.

Every cell is one photograph, centre-cropped into a flat-top hexagon and
graded to the site's purple the same way tools/make-header.py grades the
banner — so the wall reads as one surface rather than fifteen snapshots
pinned together.

It writes two things:

    assets/img/admissions-honeycomb.jpg   the still, used as the poster
    assets/video/admissions-hero.mp4      a slow, seamlessly looping drift
    assets/video/admissions-hero.webm     the same, for browsers that prefer it

The loop is built to be seamless rather than to fade out and back: the drift
follows a full sine cycle and every cell that changes photograph goes A to B
and back to A within the loop, so the last frame is the first frame. A hero
that visibly restarts is worse than one that does not move.

Text sits over this, so the same rule as the banner applies — the darkening
is baked in here and the CSS scrim above it is light. Re-measure with
tools/check-contrast.py after changing either.

    python3 tools/make-honeycomb.py            # still + video
    python3 tools/make-honeycomb.py --still    # just the still, much faster
"""

import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "assets/source")

W, H = 1920, 960          # the video's frame, and the still
HEX_W = 460               # flat-top hexagon, corner to corner
GAP = 10                  # the purple ground showing between cells

FPS, SECONDS = 24, 8

SHADOW = (38, 25, 66)
HIGHLIGHT = (232, 206, 158)
KEEP_COLOUR = 0.10
WASH = (34, 24, 52)
WASH_ALPHA = 0.30
GROUND = (14, 11, 18)


# The wall is curated, not swept up. Every photograph in assets/source/ used
# to land in a cell, which meant each new upload silently changed the hero —
# and the weakest frame in the library got the same 460px hexagon as the best.
#
# A cell is a 460px hexagon, graded to near-monochrome, with headings over it.
# That punishes a crowded frame: an overhead crush of students reads as grey
# mush at this size however good it looks full-bleed. What survives is a
# simple subject, a clear tonal range, or a repeating pattern.
#
# The order matters too. Cells are filled in sequence, so the list alternates
# between architecture, a person, a pattern and an activity — neighbouring
# hexagons then differ in character rather than repeating a mood.
CELLS = [
    "school-front-view.JPG",        # the building against the Ghats
    "IMG_1790.JPG",                 # a girl at a microscope
    "CRS09514.JPG",                 # assembly from above, reads as pattern
    "IMG_8075.JPG",                 # two students, uniform
    "IMG_2051.JPG",                 # the campus under mist
    "IMG_1686.JPG",                 # seated, one face in focus
    "IMG_2474.JPG",                 # the amphitheatre full
    "0C9A4095.JPG",                 # eyes closed, close
    "CRS01413.JPG",                 # the block along the hills
    "IMG_1806.JPG",                 # the laboratory
    "IMG_8229.JPG",                 # rows, garlands
    "IMG_2327.JPG",                 # walking, movement
    "0C9A4128.JPG",                 # namaste, sashes
    "IMG_20210514_182259.jpg",      # the building in the water
    "IMG_1689.JPG",                 # a classroom
    "IMG_2449.JPG",                 # the amphitheatre, nearer
    "0C9A4097.JPG",                 # the second close portrait
    "academic-block.JPG",           # the academic block
    "IMG_8830.JPG",                 # a boy writing
    "IMG_1625.JPG",                 # assembly on the lawn
    "IMG_1663.JPG",                 # seated by the water
    "DJI_0856.JPG",                 # the campus from the air
    "CRS09536.JPG",                 # rows of students
    "0C9A4133.JPG",                 # a teacher blessing a student
    "IMG_2480.JPG",                 # the amphitheatre, wide
    "0C9A2196.JPG",                 # a student at the lectern
    "CIRS.jpg",                     # the hundred acres, from above
    "IMG_1691.JPG",                 # the hall
    "IMG_1630.JPG",                 # the lawn again, further off
    "0C9A4081.JPG",                 # a family — this is the Admissions page
]


def sources():
    files = []
    for name in CELLS:
        path = os.path.join(SOURCE_DIR, name)
        if not os.path.exists(path):
            sys.exit(f"make-honeycomb: {name} is listed in CELLS but not in "
                     f"assets/source/ — fix the list, or restore the file.")
        files.append(path)
    return files


def grade(im):
    """The site's duotone, matching tools/make-header.py."""
    grey = ImageEnhance.Contrast(im.convert("L")).enhance(1.12)
    ramp = []
    for ch in range(3):
        lo, hi = SHADOW[ch], HIGHLIGHT[ch]
        ramp += [int(lo + (hi - lo) * (i / 255)) for i in range(256)]
    toned = Image.blend(grey.convert("RGB").point(ramp), im, KEEP_COLOUR)
    return Image.blend(toned, Image.new("RGB", im.size, WASH), WASH_ALPHA)


def cover(im, w, h):
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * scale)), max(h, int(im.height * scale))),
                   Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def hex_mask(w, h):
    """Flat-top hexagon, antialiased by drawing large and shrinking."""
    S = 4
    m = Image.new("L", (w * S, h * S), 0)
    d = ImageDraw.Draw(m)
    q = w * S / 4
    d.polygon([(q, 0), (w * S - q, 0), (w * S, h * S / 2),
               (w * S - q, h * S), (q, h * S), (0, h * S / 2)], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def layout():
    """Flat-top honeycomb covering the frame, with one cell's overhang."""
    hw = HEX_W
    hh = int(hw * math.sqrt(3) / 2)
    dx = int(hw * 3 / 4)
    cells = []
    col = 0
    x = -hw // 2
    while x < W + hw // 2:
        offset = hh // 2 if col % 2 else 0
        y = -hh + offset
        while y < H + hh:
            cells.append((x, y, hw, hh))
            y += hh
        x += dx
        col += 1
    return cells, hw, hh


def build_cells(files):
    """One graded, hex-masked tile per cell, plus the photo it fades to."""
    cells, hw, hh = layout()
    mask = hex_mask(hw - GAP, hh - GAP)
    cache = {}

    def tile(path):
        if path not in cache:
            # Honour EXIF rotation. Four of the camera originals carry
            # orientation 8, and without this they tile on their side —
            # which is what made two of them look like unusable mush.
            im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
            im = grade(cover(im, hw - GAP, hh - GAP))
            cache[path] = im
        return cache[path]

    built = []
    for i, (x, y, _, _) in enumerate(cells):
        a = tile(files[i % len(files)])
        b = tile(files[(i + 5) % len(files)])
        built.append((x + GAP // 2, y + GAP // 2, a, b, i))
    return built, mask


def vignette():
    """The same diagonal as the banner: heaviest bottom-left."""
    m = Image.new("L", (W, H))
    px = m.load()
    for y in range(H):
        for x in range(W):
            t = (1 - x / W) * 0.52 + (y / H) * 0.46
            px[x, y] = int(255 * min(1.0, max(0.0, t)) ** 1.05 * 0.82)
    return m


def compose(built, mask, vig, phase, still=False):
    """One frame. phase in [0,1) drives both the drift and the cross-fades."""
    drift = math.sin(phase * 2 * math.pi)
    ox, oy = int(drift * 14), int(math.cos(phase * 2 * math.pi) * 9)

    frame = Image.new("RGB", (W, H), GROUND)
    for x, y, a, b, i in built:
        if still:
            cell = a           # the poster shows photographs, not cross-fades
        else:
            # Each cell swings A -> B -> A across the loop, staggered by
            # index, so the loop closes exactly where it opened.
            t = 0.5 - 0.5 * math.cos((phase + (i % 7) / 7.0) * 2 * math.pi)
            cell = a if t <= 0.001 else (b if t >= 0.999 else Image.blend(a, b, t))
        frame.paste(cell, (x + ox, y + oy), mask)

    frame = Image.composite(Image.new("RGB", (W, H), GROUND), frame, vig)
    return ImageEnhance.Brightness(frame).enhance(0.94)


def encode(built, mask, vig, out, args):
    """Render straight into ffmpeg's stdin.

    Writing 192 PNG frames first would cost several hundred megabytes of
    scratch for a video that ends up around a megabyte, so the frames are
    piped as raw RGB and never touch the disk.
    """
    exe = __import__("imageio_ffmpeg").get_ffmpeg_exe()
    cmd = [exe, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-framerate", str(FPS), "-i", "-"] + args + [out]
    total = FPS * SECONDS
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(total):
        proc.stdin.write(compose(built, mask, vig, n / total).tobytes())
        if (n + 1) % 48 == 0:
            print(f"    frame {n+1}/{total}")
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("make-honeycomb: ffmpeg failed")
    print(f"  write  {os.path.relpath(out, ROOT)}  "
          f"{os.path.getsize(out)/1024/1024:.2f} MB")


def transcode(src, out, args):
    """Second format from the first, rather than rendering every frame twice."""
    exe = __import__("imageio_ffmpeg").get_ffmpeg_exe()
    subprocess.run([exe, "-y", "-loglevel", "error", "-i", src] + args + [out],
                   check=True)
    print(f"  write  {os.path.relpath(out, ROOT)}  "
          f"{os.path.getsize(out)/1024/1024:.2f} MB")


def main():
    files = sources()
    built, mask = build_cells(files)
    vig = vignette()
    print(f"  {len(built)} cells from {len(files)} photographs")

    still = compose(built, mask, vig, 0.0, still=True)
    still_path = os.path.join(ROOT, "assets/img/admissions-honeycomb.jpg")
    still.save(still_path, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"  write  assets/img/admissions-honeycomb.jpg  "
          f"{os.path.getsize(still_path)/1024:.0f} KB")

    if "--still" in sys.argv[1:]:
        return

    os.makedirs(os.path.join(ROOT, "assets/video"), exist_ok=True)
    mp4 = os.path.join(ROOT, "assets/video/admissions-hero.mp4")
    encode(built, mask, vig, mp4,
           ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "27",
            "-preset", "slow", "-movflags", "+faststart", "-an"])
    transcode(mp4, os.path.join(ROOT, "assets/video/admissions-hero.webm"),
              ["-c:v", "libvpx-vp9", "-crf", "40", "-b:v", "0",
               "-row-mt", "1", "-cpu-used", "5", "-an"])


if __name__ == "__main__":
    main()
