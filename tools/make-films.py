#!/usr/bin/env python3
"""Cut the phone encodes of the opening films, and the Crossroads opening.

The four scrubbed openings — Our Sports, CIRS Captures, CIRS Art Attack and
CIRS Theatre — are 720p files with every frame a keyframe, at 4–12 Mbit/s.
That is what lets assets/js/filmintro.js seek them several times a second
without stuttering, and it is also 3.5–10 MB that a phone had to fetch before
the reader could scrub. This writes a second encode of each for phones:

    assets/video/<film>-m.mp4     960x540, still every frame a keyframe,
                                  still 24fps and the same frames, moov first

build-site.py's film_html offers it to phones with a media-aware <source>;
the desktop file is not touched, so there is no second generation of loss on
a large screen. Only the frame size and the rate change — never the keyframe
interval, which is what would make the scrubbing stutter (see filmintro.js).

The Crossroads opening is not scrubbed but played once, so it is an ordinary
long-GOP film. Its supplied 1080p file ran at 19 Mbit/s; it is re-encoded at
a visually lossless rate (SSIM 0.995 against the supplied file) and cut again
at 720p for phones. The supplied file is kept, never deployed, as the master
in assets/source/video/, and every run encodes from that master — so running
this again cannot compound the loss.

    python3 tools/make-films.py          # everything
    python3 tools/make-films.py sports-field theatre-opening

ffmpeg is taken from PATH, or from the imageio-ffmpeg package when it is not.
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = os.path.join(ROOT, "assets/video")
MASTERS = os.path.join(ROOT, "assets/source/video")

# Scrubbed films: name -> CRF of the phone encode. Chosen per film so each
# lands at or under about 3 MB; the grain in Art Attack costs the most.
SCRUBBED = {
    "sports-field": 23,
    "captures-camera": 22,
    "art-attack-opening": 23,
    "theatre-opening": 25,
}

# Played films: name -> (desktop CRF, phone CRF). Encoded from the master.
PLAYED = {
    "crossroads-opening": (18, 21),
}

ALL_INTRA = ["-g", "1", "-keyint_min", "1", "-sc_threshold", "0", "-bf", "0"]
COMMON = ["-an", "-c:v", "libx264", "-preset", "slow", "-tune", "film",
          "-pix_fmt", "yuv420p", "-profile:v", "high",
          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
          "-movflags", "+faststart", "-map_metadata", "-1"]


def ffmpeg():
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg is not on PATH and imageio-ffmpeg is not installed")


def run(src, out, scale, crf, extra=()):
    tmp = out + ".part.mp4"
    cmd = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", src,
           "-map", "0:v:0", "-vf", f"scale={scale}:flags=lanczos",
           *COMMON, "-crf", str(crf), *extra, tmp]
    subprocess.run(cmd, check=True)
    os.replace(tmp, out)
    print(f"  write  {os.path.relpath(out, ROOT).replace(os.sep, '/')}  "
          f"{os.path.getsize(out) / 1048576:.2f} MB")


def main():
    wanted = set(sys.argv[1:])
    for name, crf in SCRUBBED.items():
        if wanted and name not in wanted:
            continue
        src = os.path.join(VIDEO, f"{name}.mp4")
        run(src, os.path.join(VIDEO, f"{name}-m.mp4"), "960:540", crf, ALL_INTRA)

    for name, (desk, phone) in PLAYED.items():
        if wanted and name not in wanted:
            continue
        os.makedirs(MASTERS, exist_ok=True)
        master = os.path.join(MASTERS, f"{name}.mp4")
        if not os.path.exists(master):
            # First run: the file in assets/video is the supplied one.
            shutil.copy2(os.path.join(VIDEO, f"{name}.mp4"), master)
        run(master, os.path.join(VIDEO, f"{name}.mp4"), "1920:1080", desk)
        run(master, os.path.join(VIDEO, f"{name}-m.mp4"), "1280:720", phone)


if __name__ == "__main__":
    main()
