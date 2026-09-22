#!/usr/bin/env python3
"""Cut both founder portraits onto one common head frame.

The opening dissolves a photograph of Balakrishna Menon into one of Swami
Chinmayananda, and tears the one through the other under the cursor. That
only reads if the two faces occupy the same place in the frame: a tear
across the forehead should show the elder man's forehead where the young
man's was, not his eyebrow or his hairline.

As shot and cut, they did not agree. Measured from the detected faces,
Gurudev's head is rolled 7.8 degrees against Menon's and his eyes sit 8%
closer together, with the midpoint 44px lower. An earlier version of this
script aligned the crown of the head and the head's width from the alpha
channel, which cannot see either the roll or the true scale -- a beard
counts as head to an alpha silhouette -- and so left both in place.

The frame is the interocular axis: eye midpoint, eye separation and the
roll of the line between them. Both portraits are mapped onto one
canonical set of those three, so the faces land on each other and the
tears cut between two men who are looking out of the same head.

The canonical values are Menon's own, levelled. Choosing his rather than
some round number keeps the base photograph almost still and spends the
resampling on the one that has to move.

Needs numpy and opencv-python (<5, for the Haar cascades; the 5.x wheels
drop cv2.objdetect). Neither is in the repository and neither is needed to
build the site -- the registered PNGs are committed. Re-run it only after
recutting a state, and commit what changes.
"""
import sys
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError:
    sys.exit("needs numpy and opencv-python-headless<5; see the docstring")

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "assets" / "founder-opening" / "assets"
STATES = ["menon-state-2048.png", "gurudev-state-2048.png"]

# The common head frame: where the eyes sit, how far apart, and level.
EYE_MID = (982.0, 484.0)
EYE_SPAN = 254.0


def eyes(path):
    """The two eye centres, as (left, right) in image coordinates."""
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None or img.shape[2] != 4:
        sys.exit(f"{path.name}: expected a 4-channel PNG")

    grey = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
    # Flatten the cut-away background to white before detecting. Left as
    # whatever colour happened to survive the cut it invents edges, and the
    # cascade finds "faces" in them.
    grey = np.where(img[:, :, 3] > 16, grey, 255).astype(np.uint8)

    faces = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    ).detectMultiScale(grey, 1.05, 5, minSize=(150, 150))
    if len(faces) == 0:
        sys.exit(f"{path.name}: no face found")
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

    found = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_eye.xml"
    ).detectMultiScale(grey[y:y + int(h * .62), x:x + w], 1.05, 6, minSize=(28, 28))
    pts = [(x + ex + ew / 2, y + ey + eh / 2) for ex, ey, ew, eh in found]

    # The cascade also finds ears and the rims of spectacles. The real pair
    # is the one that straddles the face's centre line most evenly, so score
    # every pair by how far its midpoint drifts off that line and take the
    # best. With only two candidates this is a no-op; on Menon it is what
    # rejects the ear.
    centre = x + w / 2
    pairs = [(a, b) for i, a in enumerate(pts) for b in pts[i + 1:]]
    pairs = [p for p in pairs if abs(p[0][0] - p[1][0]) > w * .18]
    if not pairs:
        sys.exit(f"{path.name}: found {len(pts)} eye candidates, no usable pair")
    a, b = min(pairs, key=lambda p: abs((p[0][0] + p[1][0]) / 2 - centre))
    return (a, b) if a[0] < b[0] else (b, a)


def register(path, left, right):
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]

    dx, dy = right[0] - left[0], right[1] - left[1]
    span = float(np.hypot(dx, dy))
    roll = float(np.degrees(np.arctan2(dy, dx)))
    mid = ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2)
    scale = EYE_SPAN / span

    # Rotate about the eye midpoint and scale in one matrix, then slide that
    # midpoint onto the canonical one.
    M = cv2.getRotationMatrix2D(mid, roll, scale)
    M[0, 2] += EYE_MID[0] - mid[0]
    M[1, 2] += EYE_MID[1] - mid[1]

    out = cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0),
    )
    # Lanczos overshoots at a hard alpha edge and leaves a rim of nearly
    # transparent pixels still carrying colour. Those surface as a halo the
    # moment the reveal lifts them, so anything nearly clear is cleared.
    out[:, :, 3] = np.where(out[:, :, 3] < 8, 0, out[:, :, 3])
    cv2.imwrite(str(path), out)
    return span, roll, mid


def main():
    for name in STATES:
        path = ART / name
        left, right = eyes(path)
        span, roll, mid = register(path, left, right)
        print(f"{name:26s} eyes=({left[0]:.0f},{left[1]:.0f}) ({right[0]:.0f},{right[1]:.0f})  "
              f"span={span:6.1f} roll={roll:+6.2f}deg  mid=({mid[0]:.0f},{mid[1]:.0f})")
        print(f"{'':26s}   -> span {EYE_SPAN:.0f}, level, mid ({EYE_MID[0]:.0f},{EYE_MID[1]:.0f})")


if __name__ == "__main__":
    main()
