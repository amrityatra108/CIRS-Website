#!/usr/bin/env python3
"""Find photographs the CIRS Cultural Gallery would show twice.

The same frame turns up on more than one page: cut for the Art Attack page
and for the wall from one camera original, or published in a report and again
in the Theatre record. A hash of the pixels misses those, because the copies
differ in size and crop. This matches features instead (ORB, with a geometric
check), after a coarse colour-histogram filter, so a frame still matches when
it has been resized, recropped or regraded.

It reports pairs; it decides nothing. A pair is a duplicate only if it is the
same exposure, not the same occasion, so look at each, then add the one to
set aside to DUPLICATES in tools/culturegallery.py.

Needs opencv-python and numpy, which the rest of the tools do not:

    python3 tools/check-gallery-duplicates.py
"""

import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(os.path.dirname(HERE))

import artswall  # noqa: E402
import culturegallery  # noqa: E402

MIN_INLIERS = 14


def load(path):
    im = Image.open(path)
    im.draft("RGB", (400, 400))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((320, 320))
    return im


def main():
    cands = []
    # The wall's own photographs, from what is on disk (so run the cutter first,
    # or this reads the previous cut).
    for name, _cat, _caption in artswall.ORIGINAL:
        for rel in (f"assets/img/arts/{name}.webp", f"assets/img/arts/thumbs/{name}.webp"):
            if os.path.exists(rel):
                cands.append((name, rel))
                break
    cands += [(i["name"], i["src"]) for i in culturegallery.collect()]

    orb = cv2.ORB_create(700)
    names, hists, feats = [], [], []
    for name, path in cands:
        im = load(path)
        hsv = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2HSV)
        h = cv2.calcHist([hsv], [0, 1, 2], None, [12, 4, 4], [0, 180, 0, 256, 0, 256]).flatten()
        hists.append(np.sqrt(h / (h.sum() + 1e-9)))
        feats.append(orb.detectAndCompute(np.asarray(im.convert("L")), None))
        names.append(name)
    sim = np.stack(hists) @ np.stack(hists).T

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    found = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            (ki, di), (kj, dj) = feats[i], feats[j]
            if sim[i, j] < 0.80 or di is None or dj is None or len(di) < 20 or len(dj) < 20:
                continue
            good = [m[0] for m in matcher.knnMatch(di, dj, k=2)
                    if len(m) == 2 and m[0].distance < 0.72 * m[1].distance]
            if len(good) < 12:
                continue
            src = np.float32([ki[g.queryIdx].pt for g in good])
            dst = np.float32([kj[g.trainIdx].pt for g in good])
            _, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4)
            inliers = int(mask.sum()) if mask is not None else 0
            if inliers >= MIN_INLIERS:
                found.append((inliers, names[i], names[j]))
    for inliers, a, b in sorted(found, reverse=True):
        note = "  (already set aside)" if a in culturegallery.DUPLICATES or b in culturegallery.DUPLICATES else ""
        print(f"  {inliers:>4} matching features   {a}  =  {b}{note}")
    print(f"{len(found)} pair(s) across {len(names)} photographs")


if __name__ == "__main__":
    main()
